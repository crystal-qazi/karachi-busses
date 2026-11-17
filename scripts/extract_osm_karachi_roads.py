#!/usr/bin/env python3
"""Extract bus-relevant OSM roads clipped to validated Karachi Division geometry."""
from __future__ import annotations
import argparse, gzip, hashlib, json, shutil, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PARENT_RELATION_ID = 6080948
AREA_CRS = "EPSG:32642"
BUS_ROAD_CLASSES = {"motorway","motorway_link","trunk","trunk_link","primary","primary_link","secondary","secondary_link","tertiary","tertiary_link","unclassified","residential","living_street","service","road"}
EXCLUDED_ACCESS = {"no","private"}
PRESERVED_TAGS = {"highway","name","name:en","ref","oneway","access","vehicle","motor_vehicle","bus","psv","surface","maxspeed","lanes","bridge","tunnel","junction","service","lit","width","layer","destination","destination:ref","turn:lanes","bus:lanes","motorcar","hgv"}

def sha256_file(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()

def is_bus_road(tags):
    if tags.get("highway","") not in BUS_ROAD_CLASSES: return False
    return not any(tags.get(key) in EXCLUDED_ACCESS for key in ("access","motor_vehicle","vehicle"))

def line_parts(geometry):
    if geometry.is_empty: return []
    if geometry.geom_type=="LineString": return [geometry] if geometry.length>0 else []
    if geometry.geom_type=="MultiLineString": return [p for p in geometry.geoms if not p.is_empty and p.length>0]
    if geometry.geom_type=="GeometryCollection": return [p for child in geometry.geoms for p in line_parts(child)]
    return []

def clipped_line_parts(geometry,boundary):
    if geometry.is_empty or not geometry.is_valid: return []
    return line_parts(geometry.intersection(boundary))

def extract_roads(input_pbf,boundary_path,output_dir):
    import osmium
    from pyproj import Transformer
    from shapely.geometry import LineString,shape
    from shapely.ops import transform
    input_pbf,boundary_path,output_dir=Path(input_pbf),Path(boundary_path),Path(output_dir)
    if not input_pbf.is_file(): raise FileNotFoundError(f"OSM PBF not found: {input_pbf}")
    if not boundary_path.is_file(): raise FileNotFoundError(f"Validated parent boundary not found: {boundary_path}")
    data=json.loads(boundary_path.read_text(encoding="utf-8"))
    parents=[f for f in data.get("features",[]) if f.get("properties",{}).get("@id")==PARENT_RELATION_ID]
    if len(parents)!=1: raise ValueError(f"Expected exactly one parent relation {PARENT_RELATION_ID}.")
    boundary=shape(parents[0]["geometry"])
    if boundary.is_empty or not boundary.is_valid: raise ValueError("Parent boundary is empty or invalid.")
    output_dir.mkdir(parents=True,exist_ok=True)
    geojson_path=output_dir/"karachi-osm-bus-roads.geojson"
    compressed_path=output_dir/"karachi-osm-bus-roads.geojson.gz"
    transformer=Transformer.from_crs("EPSG:4326",AREA_CRS,always_xy=True)
    counts,lengths=Counter(),Counter()
    total_length=0.0
    feature_count=0
    with geojson_path.open("w",encoding="utf-8",newline="\n") as stream:
        stream.write('{"type":"FeatureCollection","name":"Karachi OSM candidate roads clipped to relation 6080948","features":[\n')
        class RoadHandler(osmium.SimpleHandler):
            def way(self,way):
                nonlocal feature_count,total_length
                tags={t.k:t.v for t in way.tags}
                if not is_bus_road(tags):
                    counts["excluded_non_bus_road"]+=1; return
                try:
                    coords=[(n.lon,n.lat) for n in way.nodes if n.location.valid()]
                except (osmium.InvalidLocationError,RuntimeError):
                    counts["invalid_location"]+=1; return
                if len(coords)<2 or len(coords)!=len(way.nodes):
                    counts["incomplete_geometry"]+=1; return
                try:
                    line=LineString(coords)
                    if line.is_empty or not line.is_valid or line.length==0:
                        counts["invalid_geometry"]+=1; return
                    parts=clipped_line_parts(line,boundary)
                except Exception:
                    counts["geometry_error"]+=1; return
                if not parts:
                    counts["outside_parent_boundary"]+=1; return
                counts["ways_intersecting_parent"]+=1
                for index,part in enumerate(parts,1):
                    if len(part.coords)<2: continue
                    length=float(transform(transformer.transform,part).length)
                    if length<=0: continue
                    props={"@type":"way","@id":int(way.id),"version":int(way.version),"timestamp":str(way.timestamp),"segment":index,"source_highway":tags.get("highway"),"tags":{k:v for k,v in tags.items() if k in PRESERVED_TAGS or k.startswith("access:")},"length_m_epsg_32642":round(length,2)}
                    feature={"type":"Feature","id":f"way/{way.id}/{index}","properties":props,"geometry":{"type":"LineString","coordinates":[[round(x,8),round(y,8)] for x,y in part.coords]}}
                    if feature_count: stream.write(",\n")
                    stream.write(json.dumps(feature,ensure_ascii=False,separators=(",",":")))
                    feature_count+=1
                    counts[f"highway:{tags.get('highway','unknown')}"]+=1
                    lengths[tags.get("highway","unknown")]+=length
                    total_length+=length
        handler=RoadHandler()
        handler.apply_file(str(input_pbf),locations=True)
        stream.write("\n]}\n")
    with geojson_path.open("rb") as source,gzip.open(compressed_path,"wb",compresslevel=6) as target:
        shutil.copyfileobj(source,target)
    report={
      "status":"research_extract_complete_not_route_validation",
      "created_at_utc":datetime.now(timezone.utc).isoformat(),
      "source_provider":"Geofabrik Pakistan regional OSM PBF","input_pbf":input_pbf.name,"input_pbf_sha256":sha256_file(input_pbf),
      "boundary_source":f"OpenStreetMap relation {PARENT_RELATION_ID} (Karachi Division)","boundary_file":boundary_path.name,"boundary_sha256":sha256_file(boundary_path),
      "clip_boundary":"validated parent relation only; OSM child district identities remain unresolved",
      "feature_count":feature_count,"total_length_km_epsg_32642":round(total_length/1000,3),
      "length_by_highway_class_km":{k:round(v/1000,3) for k,v in sorted(lengths.items())},
      "counts":dict(sorted(counts.items())),
      "outputs":{"geojson":geojson_path.name,"geojson_sha256":sha256_file(geojson_path),"compressed_geojson":compressed_path.name,"compressed_size_bytes":compressed_path.stat().st_size},
      "road_filter":{"included_highway_values":sorted(BUS_ROAD_CLASSES),"excluded_access_values":sorted(EXCLUDED_ACCESS),"note":"Candidate-road inventory only; conditional access, bus-specific permissions, vehicle dimensions, turn restrictions and temporal rules require routing review."},
      "preserved_attributes":["OSM way ID, version and timestamp","highway, name, ref, oneway, access, vehicle, motor_vehicle, bus, psv","surface, maxspeed, lanes, bridge, tunnel, junction, service, lit, width, layer","destination and turn-lane tags when present"],
      "attribution":"© OpenStreetMap contributors","license":"Open Database License 1.0 (ODbL)",
      "limitations":["OSM operational boundary, not government legal certification.","Roads clipped to parent relation 6080948 only; no district identity or aggregation inferred.","OSM road geometry is not a verified bus route or turn-by-turn path.","Access, bus, vehicle, turn and time restrictions are preserved but not fully evaluated.","Stops have not yet been snapped or matched to this network.","Review ODbL obligations before redistributing derived databases."]
    }
    (output_dir/"road-extraction-report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-pbf",type=Path,default=Path("data/osm_source/pakistan-latest.osm.pbf"))
    parser.add_argument("--boundary",type=Path,default=Path("data/osm_boundary/karachi-division-6080948.geojson"))
    parser.add_argument("--output-dir",type=Path,default=Path("data/osm_roads"))
    parser.add_argument("--build",action="store_true")
    args=parser.parse_args()
    if not args.build:
        print("DRY RUN: no PBF parsing or files changed.")
        print(f"Input PBF: {args.input_pbf.resolve()}"); print(f"Boundary: {args.boundary.resolve()}"); print(f"Output: {args.output_dir.resolve()}")
        return 0
    try: print(json.dumps(extract_roads(args.input_pbf,args.boundary,args.output_dir),indent=2))
    except (OSError,ValueError,RuntimeError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 1
    return 0

if __name__=="__main__": raise SystemExit(main())
