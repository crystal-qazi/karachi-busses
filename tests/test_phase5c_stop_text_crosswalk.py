import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_phase5c_text_crosswalk_is_name_only_and_keeps_conflicts(tmp_path):
    out = tmp_path / "stop_text_crosswalk.csv"
    run = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_phase5c_stop_text_crosswalk.py"),
         "--output", str(out)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    with out.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 191
    assert all(r["coordinate_approval"] == "not_approved" for r in rows)
    assert any(r["route_code"] == "R11" and r["text_evidence_status"] == "route_identity_conflict"
               for r in rows)
    assert any(r["source_stop_name"] == "Baldia" and
               r["text_evidence_status"] == "route_identity_conflict" for r in rows)
    assert all(r["text_source_url"] == "https://smta.gos.pk/route-map" for r in rows)
