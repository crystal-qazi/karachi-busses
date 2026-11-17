import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_coordinate_review_builder_creates_read_only_outputs(tmp_path):
    output = tmp_path / "phase5b"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_coordinate_review.py"),
            "--output-dir",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((output / "coordinate_qa_report.json").read_text(encoding="utf-8"))
    geojson = json.loads((output / "coordinate_nodes.geojson").read_text(encoding="utf-8"))

    assert report["node_count"] == 572
    assert report["crosswalk_row_count"] == 191
    assert report["exact_name_candidate_row_count"] == 89
    assert report["unmatched_source_stop_row_count"] == 102
    assert report["coordinate_collision_group_count"] == 10
    assert report["coordinate_collision_node_count"] == 24
    assert report["historical_edge_count"] == 1415
    assert report["historical_route_label_count"] == 76
    assert report["dangling_edge_node_ids"] == []
    assert report["database_writes"] is False
    assert report["external_geocoding_or_routing_calls"] is False
    assert report["geometry_generation"].startswith("blocked_")

    assert len(geojson["features"]) == 572
    assert all(feature["geometry"]["type"] == "Point" for feature in geojson["features"])
    assert all(len(feature["geometry"]["coordinates"]) == 2 for feature in geojson["features"])

    with (output / "stop_review_queue.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 191
    assert all(row["review_decision"] == "" for row in rows)
    assert (output / "coordinate_review_map.html").is_file()
