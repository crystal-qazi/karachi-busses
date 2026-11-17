#!/usr/bin/env python3
"""Audit proximity between existing candidate stop coordinates and OSM road segments.

This is a review aid only. It does not snap stops, approve boarding locations,
infer routes, or change application/database data.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

AREA_CRS = "EPSG:32642"
SEARCH_RADIUS_M = 250.0
NEAR_BANDS = ((15, "0-15m"), (50, "15-50m"), (100, "50-100m"), (250, "100-250m"))

def sha256_file(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()

def proximity_band(distance_m):
    if distance_m is None: return "no_road_geometry"
    for upper,label in NEAR_BANDS:
        if distance_m <= upper: return label
    return ">250m"

def audit_stops(crosswalk_path, roads_path, road_report_path, boundary_path, output_dir):
    from pyproj import Transformer
    from shapely.geometry import Point, shape
    from shapely.ops import transform
    from shapely.strtree import STRtree

    crosswalk_path,roads_path,road_report_path,boundary_path,output_dir=map(Path,(crosswalk_path,roads_path,road_report_path,boundary_path,output_dir))
    for path in (crosswalk_path,roads_path,road_report_path,boundary_path):
        if not path.is_file(): raise FileNotFoundError(path)
    boundary_data=json.loads(boundary_path.read_text(encoding="utf-8"))
    parent_features=[f for f in boundary_data.get("features",[]) if f.get("properties",{}).get("@id")==6080948]
    if len(parent_features)!=1: raise ValueError("Expected exactly one validated OSM parent relation 6080948.")
    parent_boundary=shape(parent_features[0]["geometry"])
    if parent_boundary.is_empty or not parent_boundary.is_valid: raise ValueError("OSM parent boundary is invalid.")
    transformer=Transformer.from_crs("EPSG:4326",AREA_CRS,always_xy=True)
    road_data=json.loads(roads_path.read_text(encoding="utf-8"))
    lines=[]; props=[]
    for feature in road_data.get("features",[]):
        try:
            geom=shape(feature["geometry"])
            projected=transform(transformer.transform,geom)
            if not projected.is_empty and projected.is_valid and projected.length>0:
                lines.append(projected); props.append(feature.get("properties",{}))
        except (KeyError,TypeError,ValueError):
            continue
    if not lines: raise ValueError("Road GeoJSON contains no valid line geometries.")
    tree=STRtree(lines)
    output_dir.mkdir(parents=True,exist_ok=True)
    csv_path=output_dir/"stop-road-proximity-audit.csv"
    counts=Counter()
    with crosswalk_path.open("r",encoding="utf-8-sig",newline="") as source, csv_path.open("w",encoding="utf-8",newline="") as target:
        reader=csv.DictReader(source)
        fields=[
          "route_code","route_name","source_stop_sequence","source_stop_name",
          "coordinate_node_id","latitude","longitude","crosswalk_match_method","crosswalk_review_status",
          "nearest_osm_way_id","nearest_road_name","nearest_highway","nearest_oneway",
          "nearest_access","nearest_distance_m","proximity_band","candidate_roads_within_250m",
          "nearby_osm_candidates","audit_status","review_note"
        ]
        writer=csv.DictWriter(target,fieldnames=fields); writer.writeheader()
        for row in reader:
            out={key:row.get(key,"") for key in fields}
            out.update({key:"" for key in fields if key not in out})
            lat,lon=row.get("latitude",""),row.get("longitude","")
            if not lat or not lon:
                out["audit_status"]="no_coordinate_candidate"
                out["review_note"]="No exact-name coordinate candidate in the historical 572-node crosswalk; no geocoding attempted."
                counts["no_coordinate_candidate"]+=1
                writer.writerow(out); continue
            try:
                source_point=Point(float(lon),float(lat))
                if not source_point.is_valid or source_point.is_empty: raise ValueError("invalid point")
            except (ValueError,TypeError):
                out["audit_status"]="invalid_candidate_coordinate"
                out["review_note"]="Coordinate could not be parsed; manual source review required."
                counts["invalid_candidate_coordinate"]+=1
                writer.writerow(out); continue
            if not parent_boundary.covers(source_point):
                out["audit_status"]="candidate_outside_parent_boundary"
                out["review_note"]="Historical coordinate candidate falls outside OSM parent relation 6080948; no road proximity assigned."
                counts["candidate_outside_parent_boundary"]+=1
                writer.writerow(out); continue
            point=transform(transformer.transform,source_point)
            indexes=tree.query(point.buffer(SEARCH_RADIUS_M))
            candidates=[]
            for idx in indexes:
                i=int(idx); distance=float(point.distance(lines[i]))
                if distance<=SEARCH_RADIUS_M:
                    p=props[i]; tags=p.get("tags",{})
                    candidates.append((distance,i,p,tags))
            candidates.sort(key=lambda item:(item[0],int(item[2].get("@id",0))))
            unique=[]; seen=set()
            for candidate in candidates:
                way_id=candidate[2].get("@id")
                if way_id in seen: continue
                seen.add(way_id); unique.append(candidate)
                if len(unique)>=5: break
            if not unique:
                nearest_idx=int(tree.nearest(point))
                nearest_distance=float(point.distance(lines[nearest_idx]))
                p=props[nearest_idx]; tags=p.get("tags",{})
                out.update({
                  "nearest_osm_way_id":p.get("@id",""),"nearest_road_name":tags.get("name",""),
                  "nearest_highway":tags.get("highway",""),"nearest_oneway":tags.get("oneway",""),
                  "nearest_access":tags.get("access",""),"nearest_distance_m":round(nearest_distance,2),
                  "proximity_band":proximity_band(nearest_distance),"candidate_roads_within_250m":0,
                  "nearby_osm_candidates":"[]","audit_status":"nearest_road_over_250m"
                })
                counts["nearest_road_over_250m"]+=1
            else:
                distance,i,p,tags=unique[0]
                nearby=[{"osm_way_id":x[2].get("@id"),"name":x[3].get("name"),"highway":x[3].get("highway"),"oneway":x[3].get("oneway"),"access":x[3].get("access"),"distance_m":round(x[0],2)} for x in unique]
                out.update({
                  "nearest_osm_way_id":p.get("@id",""),"nearest_road_name":tags.get("name",""),
                  "nearest_highway":tags.get("highway",""),"nearest_oneway":tags.get("oneway",""),
                  "nearest_access":tags.get("access",""),"nearest_distance_m":round(distance,2),
                  "proximity_band":proximity_band(distance),"candidate_roads_within_250m":len(candidates),
                  "nearby_osm_candidates":json.dumps(nearby,ensure_ascii=False,separators=(",",":")),
                  "audit_status":"proximity_only_unverified"
                })
                counts["proximity_only_unverified"]+=1
            out["review_note"]="Nearest OSM road is a geometric proximity candidate only; it does not verify the stop, road side, platform, bus access, route use or direction."
            writer.writerow(out)
    road_report=json.loads(road_report_path.read_text(encoding="utf-8"))
    report={
      "status":"stop_road_proximity_audit_complete_not_stop_verification",
      "created_at_utc":datetime.now(timezone.utc).isoformat(),
      "coordinate_source":"data/research/PHASE_5_STOP_NODE_CROSSWALK.csv",
      "coordinate_source_sha256":sha256_file(crosswalk_path),
      "road_source":"OpenStreetMap candidate roads clipped to parent relation 6080948",
      "road_geojson_sha256":sha256_file(roads_path),
      "parent_boundary_source": "OpenStreetMap relation 6080948",
      "parent_boundary_sha256":sha256_file(boundary_path),
      "road_report_input":road_report_path.name,
      "road_source_pbf_sha256":road_report.get("input_pbf_sha256"),
      "search_radius_m":SEARCH_RADIUS_M,
      "road_feature_count":len(lines),
      "crosswalk_rows":sum(counts.values()),
      "counts":dict(sorted(counts.items())),
      "distance_bands_m":{label:[0,upper] for upper,label in NEAR_BANDS},
      "outputs":{"csv":csv_path.name,"csv_sha256":sha256_file(csv_path)},
      "limitations":[
        "Historical coordinate candidates are not verified physical stops.",
        "Nearest road does not prove a bus serves that road or that the boarding point is on the correct side.",
        "No snapping, geocoding, route construction, turn inference or database write is performed.",
        "OSM access, one-way, bus, vehicle and conditional restrictions still require interpretation.",
        "Manual/operator/field review remains mandatory before any candidate can become an approved stop."
      ],
      "attribution":"© OpenStreetMap contributors","license":"Open Database License 1.0 (ODbL)"
    }
    (output_dir/"stop-road-proximity-report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crosswalk",type=Path,default=Path("data/research/PHASE_5_STOP_NODE_CROSSWALK.csv"))
    parser.add_argument("--roads",type=Path,default=Path("data/osm_roads/karachi-osm-bus-roads.geojson"))
    parser.add_argument("--road-report",type=Path,default=Path("data/osm_roads/road-extraction-report.json"))
    parser.add_argument("--boundary",type=Path,default=Path("data/osm_boundary/karachi-division-6080948.geojson"))
    parser.add_argument("--output-dir",type=Path,default=Path("data/osm_roads"))
    parser.add_argument("--build",action="store_true")
    args=parser.parse_args()
    if not args.build:
        print("DRY RUN: no files changed; pass --build to run proximity audit.")
        return 0
    try: print(json.dumps(audit_stops(args.crosswalk,args.roads,args.road_report,args.boundary,args.output_dir),indent=2))
    except (OSError,ValueError,RuntimeError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 1
    return 0
if __name__=="__main__": raise SystemExit(main())
