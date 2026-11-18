#!/usr/bin/env python3
"""Cross-check historical exact-coordinate collision groups against SMTA crosswalk.

This is a diagnostic join only. It does not transfer coordinates or approve stops.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, sys
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

NODES = Path("data/research/PHASE_5_NODE_AUDIT.csv")
CROSSWALK = Path("data/research/PHASE_5_STOP_NODE_CROSSWALK.csv")
OUTPUT = Path("data/research/PHASE_5AC_COLLISION_CROSSWALK_IMPACT.csv")
REPORT = Path("data/research/PHASE_5AC_COLLISION_CROSSWALK_IMPACT_REPORT.json")


def read(path: Path, required: set[str]):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        if required - fields:
            raise ValueError(f"{path} missing columns: {sorted(required-fields)}")
        rows = list(reader)
    return rows


def coord(lat: str, lon: str):
    try:
        pair = (Decimal(lat), Decimal(lon))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"Invalid coordinate: {lat!r}, {lon!r}") from exc
    if not all(v.is_finite() for v in pair):
        raise ValueError(f"Non-finite coordinate: {lat!r}, {lon!r}")
    return pair


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(nodes_path=NODES, crosswalk_path=CROSSWALK, output_path=OUTPUT, report_path=REPORT):
    nodes = read(nodes_path, {"node_id", "latitude", "longitude", "historical_route_labels", "verification_status"})
    stops = read(crosswalk_path, {"route_code", "source_stop_sequence", "source_stop_name", "coordinate_node_id", "latitude", "longitude", "review_status"})
    by_coord = defaultdict(list)
    ids = set()
    for row in nodes:
        nid = row["node_id"].strip()
        if not nid or nid in ids:
            raise ValueError(f"Blank or duplicate node ID: {nid!r}")
        ids.add(nid)
        by_coord[coord(row["latitude"], row["longitude"])].append(row)
    collisions = [(p, sorted(g, key=lambda x: x["node_id"])) for p,g in by_coord.items() if len(g)>1]
    collisions.sort(key=lambda x:(x[0][0],x[0][1]))

    stop_by_id = defaultdict(list)
    stop_by_coord = defaultdict(list)
    for stop in stops:
        if stop["coordinate_node_id"].strip():
            stop_by_id[stop["coordinate_node_id"].strip()].append(stop)
        if stop["latitude"].strip() and stop["longitude"].strip():
            stop_by_coord[coord(stop["latitude"],stop["longitude"])].append(stop)

    fields = ["collision_group_id","node_id","latitude","longitude","cluster_size","historical_route_labels","node_verification_status","exact_node_id_crosswalk_match_count","exact_coordinate_crosswalk_match_count","crosswalk_rows_same_node_id","crosswalk_rows_same_coordinate","impact_status","review_action"]
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_rows=0; id_hits=set(); coord_hits=set(); groups=[]
    with output_path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for i,(point,members) in enumerate(collisions,1):
            group_id=f"CC-{i:02d}"
            node_ids={x["node_id"] for x in members}
            id_rows=[s for nid in node_ids for s in stop_by_id.get(nid,[])]
            coordinate_rows=stop_by_coord.get(point,[])
            id_hits.update((s["route_code"],s["source_stop_sequence"]) for s in id_rows)
            coord_hits.update((s["route_code"],s["source_stop_sequence"]) for s in coordinate_rows)
            for n in members:
                w.writerow({
                    "collision_group_id":group_id,"node_id":n["node_id"],"latitude":n["latitude"],"longitude":n["longitude"],
                    "cluster_size":len(members),"historical_route_labels":n["historical_route_labels"],
                    "node_verification_status":n["verification_status"],
                    "exact_node_id_crosswalk_match_count":len(stop_by_id.get(n["node_id"],[])),
                    "exact_coordinate_crosswalk_match_count":len(coordinate_rows),
                    "crosswalk_rows_same_node_id":";".join(f'{s["route_code"]}:{s["source_stop_sequence"]}' for s in stop_by_id.get(n["node_id"],[])),
                    "crosswalk_rows_same_coordinate":";".join(f'{s["route_code"]}:{s["source_stop_sequence"]}:{s["source_stop_name"]}' for s in coordinate_rows),
                    "impact_status":"no_current_crosswalk_reference_found" if not id_rows and not coordinate_rows else "manual_review_required_crosswalk_overlap",
                    "review_action":"retain historical collision; do not transfer coordinates or merge nodes; inspect independent source evidence",
                })
                output_rows+=1
            groups.append({"collision_group_id":group_id,"node_ids":[x["node_id"] for x in members],"coordinate":[str(point[0]),str(point[1])],"crosswalk_node_id_rows":len(id_rows),"crosswalk_coordinate_rows":len(coordinate_rows)})
    report={
        "status":"collision_to_crosswalk_impact_audit_complete",
        "created_at_utc":datetime.now(timezone.utc).isoformat(),
        "inputs":{"node_audit":{"path":str(nodes_path),"sha256":sha(nodes_path)},"stop_crosswalk":{"path":str(crosswalk_path),"sha256":sha(crosswalk_path)}},
        "counts":{"historical_node_rows":len(nodes),"crosswalk_rows":len(stops),"crosswalk_rows_with_node_id":sum(bool(s["coordinate_node_id"].strip()) for s in stops),"collision_groups":len(collisions),"nodes_in_collision_groups":output_rows,"crosswalk_rows_matching_collision_node_ids":len(id_hits),"crosswalk_rows_matching_collision_coordinates":len(coord_hits)},
        "groups":groups,
        "output":{"csv":str(output_path),"sha256":sha(output_path),"rows":output_rows},
        "limitations":["Exact node-ID and exact-coordinate joins only; no fuzzy or spatial proximity join.","No source names or coordinates are transferred into the SMTA crosswalk.","No physical stop is verified and no route is approved.","No geocoding, snapping, route inference, geometry generation, or database writes."],
    }
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--build",action="store_true");a=p.parse_args()
    if not a.build:p.error("pass --build")
    try: print(json.dumps(build(),indent=2))
    except (OSError,ValueError) as e: print(f"ERROR: {e}",file=sys.stderr);return 1
    return 0
if __name__=="__main__": raise SystemExit(main())
