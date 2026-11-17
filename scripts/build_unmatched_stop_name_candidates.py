#!/usr/bin/env python3
"""Build a conservative name-only candidate list for unmatched historical stops.

This script never assigns coordinates or changes the stop crosswalk. Scores are
triage hints only; every row remains unverified and requires human evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "data/research/PHASE_5_STOP_NODE_CROSSWALK.csv"
NODES = ROOT / "data/research/PHASE_5_NODE_AUDIT.csv"
OUTPUT = ROOT / "data/research/PHASE_5W_UNMATCHED_STOP_NAME_CANDIDATES.csv"
REPORT = ROOT / "data/research/PHASE_5W_UNMATCHED_STOP_NAME_CANDIDATES_REPORT.json"

# Normalization aliases are linguistic hints only, never coordinate mappings.
ALIASES = {
    "khokharapar": "khokrapar",
    "khokharapar 04": "khokrapar 4",
    "khokrapar no 4": "khokrapar 4",
    "suadabad": "saudabad",
    "sorab goth": "sohrab goth",
    "five star chowrangi": "5 star chowrangi",
    "guru mandar": "gurumandir",
    "kemari": "keamari",
    "mera naka": "mira naka",
    "punjabi chowrangi": "punjab chowrangi",
    "qaidabad": "quaidabad",
    "maripur": "mauripur",
    "domba goth": "damba goth",
    "mosamiyat": "mosmayat",
    "millennium mall": "millenium mall",
}

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = " ".join(value.split())
    return ALIASES.get(value, value)

def score_names(stop_name: str, node_id: str) -> float:
    stop = normalize(stop_name)
    node = normalize(node_id.replace("_", " "))
    if not stop or not node:
        return 0.0
    seq = SequenceMatcher(None, stop, node).ratio()
    a, b = set(stop.split()), set(node.split())
    token = (2 * len(a & b) / (len(a) + len(b))) if a or b else 0.0
    # Sequence and token overlap balance spelling variants and word-order changes.
    return round(0.55 * seq + 0.45 * token, 4)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.name

def build() -> tuple[int, int]:
    with CROSSWALK.open(encoding="utf-8-sig", newline="") as f:
        crosswalk = list(csv.DictReader(f))
    with NODES.open(encoding="utf-8-sig", newline="") as f:
        nodes = list(csv.DictReader(f))
    candidates = [{"node_id": n["node_id"]} for n in nodes if n.get("node_id")]
    unmatched = [r for r in crosswalk if r.get("review_status") == "unmatched"]
    fields = [
        "route_code", "route_name", "source_stop_sequence", "source_stop_name",
        "candidate_1_node_id", "candidate_1_score", "candidate_1_band",
        "candidate_2_node_id", "candidate_2_score", "candidate_2_band",
        "candidate_3_node_id", "candidate_3_score", "candidate_3_band",
        "candidate_count_at_or_above_0_45", "review_status", "review_instruction",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in unmatched:
            ranked = sorted(
                ((score_names(row["source_stop_name"], n["node_id"]), n["node_id"]) for n in candidates),
                key=lambda x: (-x[0], x[1]),
            )[:3]
            out = {k: row.get(k, "") for k in fields[:4]}
            strong_count = sum(
                score_names(row["source_stop_name"], n["node_id"]) >= 0.45
                for n in candidates
            )
            for i in range(3):
                score, node_id = ranked[i] if i < len(ranked) else (0.0, "")
                band = "strong_name_similarity" if score >= 0.85 else (
                    "possible_name_similarity" if score >= 0.65 else (
                        "weak_name_similarity" if score >= 0.45 else "low_similarity"
                    )
                )
                out[f"candidate_{i+1}_node_id"] = node_id
                out[f"candidate_{i+1}_score"] = f"{score:.4f}" if node_id else ""
                out[f"candidate_{i+1}_band"] = band if node_id else ""
            out["candidate_count_at_or_above_0_45"] = strong_count
            out["review_status"] = "unverified_name_candidates_only"
            out["review_instruction"] = (
                "Compare against operator/field evidence; do not copy coordinates, "
                "snap, infer route geometry, or approve from this score."
            )
            writer.writerow(out)
    report = {
        "status": "name_candidate_register_built_not_stop_verification",
        "source_crosswalk": display_path(CROSSWALK),
        "source_crosswalk_sha256": sha256(CROSSWALK),
        "source_node_audit": display_path(NODES),
        "source_node_audit_sha256": sha256(NODES),
        "output_csv": display_path(OUTPUT),
        "output_csv_sha256": sha256(OUTPUT),
        "crosswalk_rows": len(crosswalk),
        "unmatched_rows_reviewed": len(unmatched),
        "node_name_candidates": len(candidates),
        "candidate_method": "standard-library SequenceMatcher plus token Dice score",
        "candidate_limit_per_stop": 3,
        "threshold_count": 0.45,
        "coordinates_emitted": False,
        "automatic_assignments": 0,
        "stop_verification_status": "all_unverified",
        "route_approval_status": "all_not_approved",
        "limitations": [
            "Similarity is a text triage aid, not geographic or operational evidence.",
            "Short/common names can produce misleading candidates.",
            "Historical node labels may not represent current SMTA passenger stops.",
            "No coordinates, road matches, route paths, or access permissions are inferred.",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return len(unmatched), len(candidates)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="write CSV and JSON outputs")
    args = parser.parse_args()
    if not args.build:
        parser.error("pass --build to write the review register")
    unmatched, nodes = build()
    print(f"Built name-only candidate review: {unmatched} unmatched stops; {nodes} node names")

if __name__ == "__main__":
    main()
