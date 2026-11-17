"""Build a read-only coordinate QA package for the Karachi bus research dataset.

No database access, geocoding, routing API calls, or source-data mutation occurs.
Run from the repository root:
    python scripts/build_coordinate_review.py

Outputs are written to reports/phase5b/:
    coordinate_review_map.html
    coordinate_nodes.geojson
    stop_review_queue.csv
    coordinate_qa_report.json
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODES = ROOT / "data/research/PHASE_5_NODE_AUDIT.csv"
CROSSWALK = ROOT / "data/research/PHASE_5_STOP_NODE_CROSSWALK.csv"
EDGES = ROOT / "data/imports/karachi_bus_network_cleaned_edges.csv"
KARACHI_BOUNDS = {"south": 24.65, "north": 25.15, "west": 66.65, "east": 67.50}


def read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing input file: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path.name} missing columns: {', '.join(sorted(missing))}")
        return list(reader)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/phase5b")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    nodes = read_csv(NODES, {"node_id", "latitude", "longitude", "historical_route_labels",
                             "route_label_count", "coordinate_collision_group"})
    crosswalk = read_csv(CROSSWALK, {"route_code", "source_stop_sequence", "source_stop_name",
                                     "coordinate_node_id", "latitude", "longitude", "review_status"})
    edges = read_csv(EDGES, {"stop1", "stop2", "bus_name"})

    node_by_id: dict[str, dict[str, str]] = {}
    collision_groups: dict[str, list[str]] = defaultdict(list)
    for row in nodes:
        node_id = row["node_id"].strip()
        if not node_id or node_id in node_by_id:
            raise ValueError(f"Blank or duplicate node_id: {node_id!r}")
        lat, lon = float(row["latitude"]), float(row["longitude"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f"Invalid coordinate for {node_id}: {lat}, {lon}")
        node_by_id[node_id] = row
        if row["coordinate_collision_group"]:
            collision_groups[row["coordinate_collision_group"]].append(node_id)

    candidate_refs: dict[str, list[str]] = defaultdict(list)
    unmatched = []
    review_rows = []
    for row in crosswalk:
        node_id = row["coordinate_node_id"].strip()
        if node_id:
            if node_id not in node_by_id:
                raise ValueError(f"Crosswalk points to unknown coordinate node: {node_id}")
            candidate_refs[node_id].append(f'{row["route_code"]} #{row["source_stop_sequence"]}')
        else:
            unmatched.append(row)
        review_rows.append({
            **row,
            "review_decision": "",
            "reviewer": "",
            "reviewed_at": "",
            "evidence_url_or_reference": "",
            "review_notes": "",
        })

    edge_node_ids = {r[k].strip() for r in edges for k in ("stop1", "stop2")}
    dangling = sorted(edge_node_ids - set(node_by_id))
    if dangling:
        raise ValueError(f"Historical edges reference missing nodes: {dangling[:10]}")

    outside = []
    geo_features = []
    map_points = []
    for node_id, row in node_by_id.items():
        lat, lon = float(row["latitude"]), float(row["longitude"])
        in_bounds = (KARACHI_BOUNDS["south"] <= lat <= KARACHI_BOUNDS["north"]
                     and KARACHI_BOUNDS["west"] <= lon <= KARACHI_BOUNDS["east"])
        if not in_bounds:
            outside.append(node_id)
        props = {
            "node_id": node_id,
            "historical_route_labels": row["historical_route_labels"],
            "route_label_count": int(row["route_label_count"] or 0),
            "coordinate_collision_group": row["coordinate_collision_group"],
            "candidate_smta_refs": candidate_refs.get(node_id, []),
            "review_status": "source_unreviewed",
        }
        geo_features.append({"type": "Feature", "geometry": {
            "type": "Point", "coordinates": [lon, lat]}, "properties": props})
        map_points.append({"id": node_id, "lat": lat, "lon": lon, **props})

    review_fields = list(crosswalk[0]) + [
        "review_decision", "reviewer", "reviewed_at",
        "evidence_url_or_reference", "review_notes",
    ]
    write_csv(output / "stop_review_queue.csv", review_rows, review_fields)

    geojson = {"type": "FeatureCollection", "name": "Karachi historical coordinate candidates",
               "source": "Habib University / Data Research Lab Pakistan candidate dataset, CC BY 4.0",
               "features": geo_features}
    (output / "coordinate_nodes.geojson").write_text(
        json.dumps(geojson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "status": "research_only_not_verified",
        "node_count": len(nodes),
        "valid_coordinate_count": len(nodes),
        "outside_karachi_bounds": outside,
        "karachi_plausibility_bounds": KARACHI_BOUNDS,
        "coordinate_collision_group_count": len(collision_groups),
        "coordinate_collision_node_count": sum(map(len, collision_groups.values())),
        "coordinate_collision_groups": dict(collision_groups),
        "crosswalk_row_count": len(crosswalk),
        "exact_name_candidate_row_count": len(crosswalk) - len(unmatched),
        "unmatched_source_stop_row_count": len(unmatched),
        "distinct_candidate_node_count": len(candidate_refs),
        "candidate_nodes_reused_by_multiple_source_stops": {
            k: v for k, v in candidate_refs.items() if len(v) > 1
        },
        "historical_edge_count": len(edges),
        "historical_route_label_count": len({r["bus_name"] for r in edges}),
        "dangling_edge_node_ids": dangling,
        "geometry_generation": "blocked_until_stop_coordinates_and_order_are_reviewed",
        "database_writes": False,
        "external_geocoding_or_routing_calls": False,
        "review_queue_decisions_allowed": [
            "accept_candidate", "reject_candidate", "needs_field_check", "needs_better_source"
        ],
    }
    (output / "coordinate_qa_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    points_json = json.dumps(map_points, ensure_ascii=False).replace("</", "<\\/")
    map_html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Karachi Bus Coordinate Review — Research Only</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
html,body{height:100%;margin:0;font:14px system-ui,sans-serif}#top{padding:10px 14px;background:#172554;color:white}
#top strong{font-size:16px}#top small{display:block;color:#dbeafe;margin-top:3px}
#bar{padding:8px 14px;background:#f1f5f9;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
#map{height:calc(100% - 112px)}.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px}
button{padding:6px 10px} .leaflet-popup-content{line-height:1.5}
</style></head><body>
<div id="top"><strong>Karachi Bus Coordinate Review</strong>
<small>572 historical coordinate nodes · Research candidates only · Not approved bus stops or route geometry</small></div>
<div id="bar"><span class="legend"><i style="background:#2563eb"></i>Historical node</span>
<span class="legend"><i style="background:#dc2626"></i>SMTA name-match candidate</span>
<span class="legend"><i style="background:#d97706"></i>Coordinate collision</span>
<label><input id="candidateOnly" type="checkbox"> Candidate matches only</label>
<label><input id="collisionOnly" type="checkbox"> Collisions only</label></div>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const points = __POINTS__;
const map=L.map('map').setView([24.86,67.05],11);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
 maxZoom:19,attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
const layer=L.layerGroup().addTo(map);let visible=[];
function render(){
 layer.clearLayers();visible=[];
 const cand=document.getElementById('candidateOnly').checked;
 const coll=document.getElementById('collisionOnly').checked;
 for(const p of points){
  const isCandidate=p.candidate_smta_refs.length>0;
  const isCollision=Boolean(p.coordinate_collision_group);
  if(cand&&!isCandidate)continue;if(coll&&!isCollision)continue;
  const color=isCollision?'#d97706':(isCandidate?'#dc2626':'#2563eb');
  const marker=L.circleMarker([p.lat,p.lon],{radius:isCandidate?7:5,color,fillColor:color,fillOpacity:.8,weight:1});
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  marker.bindPopup('<b>'+esc(p.id)+'</b><br>'+p.lat+', '+p.lon+
   '<br>Historical labels: '+esc(p.historical_route_labels||'none')+
   '<br>SMTA candidate refs: '+esc(p.candidate_smta_refs.join('; ')||'none')+
   '<br>Collision group: '+esc(p.coordinate_collision_group||'none')+
   '<br><b>Review status:</b> source_unreviewed');
  marker.addTo(layer);visible.push([p.lat,p.lon]);
 }
}
document.getElementById('candidateOnly').addEventListener('change',render);
document.getElementById('collisionOnly').addEventListener('change',render);
render();
</script></body></html>""".replace("__POINTS__", points_json)
    (output / "coordinate_review_map.html").write_text(map_html, encoding="utf-8")

    print(json.dumps({
        "output_dir": str(output),
        "nodes": len(nodes),
        "candidate_matches": len(crosswalk) - len(unmatched),
        "unmatched": len(unmatched),
        "collision_groups": len(collision_groups),
        "collision_nodes": sum(map(len, collision_groups.values())),
        "historical_edges": len(edges),
        "files": ["coordinate_review_map.html", "coordinate_nodes.geojson",
                  "stop_review_queue.csv", "coordinate_qa_report.json"],
        "database_writes": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
