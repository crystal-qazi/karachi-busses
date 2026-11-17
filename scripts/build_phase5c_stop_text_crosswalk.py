"""Cross-check historical route-stop rows against published SMTA route text.

This records name evidence only. It never assigns coordinates or approves stops.
"""
from __future__ import annotations
import argparse, csv, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/research/PHASE_5_STOP_NODE_CROSSWALK.csv"
PUBLISHED = ROOT / "data/research/PHASE_5C_PUBLISHED_ROUTE_STOPS.csv"
OUTPUT = ROOT / "reports/phase5c/stop_text_crosswalk.csv"
CONFLICTS = {"R2", "R3", "R4", "R8", "R11", "R12", "R1", "R13"}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    crosswalk, published = read(INPUT), read(PUBLISHED)
    by_route: dict[str, dict[str, list[dict[str, str]]]] = {}
    for row in published:
        by_route.setdefault(row["route_code"], {}).setdefault(norm(row["published_stop_name"]), []).append(row)

    result = []
    counts = {"published_name_confirmed": 0, "route_identity_conflict": 0, "not_found_in_published_text": 0}
    for row in crosswalk:
        matches = by_route.get(row["route_code"], {}).get(norm(row["source_stop_name"]), [])
        matched_names = "; ".join(dict.fromkeys(x["published_stop_name"] for x in matches))
        matched_orders = "; ".join(x["published_sequence"] for x in matches)
        if matches and row["route_code"] in CONFLICTS:
            status = "route_identity_conflict"
            note = "Name occurs in published detailed route text, but route identity/direction/order conflict remains unresolved"
        elif matches:
            status = "published_name_confirmed"
            note = "Name occurs in published detailed route text; coordinate and boarding point remain unverified"
        else:
            status = "not_found_in_published_text"
            note = "No exact normalized name in transcribed route description; alias/source review still required"
        counts[status] += 1
        result.append({
            **row,
            "published_name_match": matched_names,
            "published_sequence_match": matched_orders,
            "text_evidence_status": status,
            "text_evidence_note": note,
            "text_source_url": "https://smta.gos.pk/route-map",
            "coordinate_approval": "not_approved",
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(result[0]) if result else []
    with args.output.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(result)
    print({"input_rows": len(crosswalk), "published_source_rows": len(published),
           "statuses": counts, "output": str(args.output), "coordinate_approval": "none"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
