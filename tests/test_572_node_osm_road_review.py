import csv
import json
from pathlib import Path

import pytest

pytest.importorskip("shapely")
pytest.importorskip("pyproj")

from scripts.build_572_node_osm_road_review import build_register


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_builds_complete_node_register_without_approving_stops(tmp_path):
    nodes = tmp_path / "nodes.csv"
    crosswalk = tmp_path / "crosswalk.csv"
    roads = tmp_path / "roads.geojson"
    boundary = tmp_path / "boundary.geojson"
    output = tmp_path / "out"

    node_fields = [
        "node_id", "latitude", "longitude", "historical_route_labels",
        "route_label_count", "coordinate_collision_group",
    ]
    node_rows = [
        {"node_id": f"node_{i}", "latitude": "24.86", "longitude": str(67.0 + i * 0.001),
         "historical_route_labels": "R-test", "route_label_count": "1",
         "coordinate_collision_group": "COL-test" if i == 0 else ""}
        for i in range(572)
    ]
    write_csv(nodes, node_fields, node_rows)
    write_csv(crosswalk, ["route_code", "source_stop_sequence", "source_stop_name", "coordinate_node_id"], [
        {"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Candidate", "coordinate_node_id": "node_0"}
    ])

    boundary.write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "geometry": {
            "type": "Polygon", "coordinates": [[[66.9, 24.7], [67.8, 24.7], [67.8, 25.1],
                                                  [66.9, 25.1], [66.9, 24.7]]]},
            "properties": {"@id": 6080948}}]
    }), encoding="utf-8")
    roads.write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "geometry": {
            "type": "LineString", "coordinates": [[66.9, 24.86], [67.8, 24.86]]},
            "properties": {"@id": 12345, "tags": {"name": "Test Road", "highway": "primary"}}}]
    }), encoding="utf-8")

    report = build_register(nodes, crosswalk, roads, boundary, output)
    with (output / "karachi-572-node-osm-road-review.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert report["source_node_count"] == 572
    assert report["output_node_count"] == 572
    assert len(rows) == 572
    assert rows[0]["candidate_smta_ref_count"] == "1"
    assert rows[0]["audit_status"] == "proximity_only_unverified"
    assert rows[0]["coordinate_collision_group"] == "COL-test"
    assert report["database_writes"] is False
