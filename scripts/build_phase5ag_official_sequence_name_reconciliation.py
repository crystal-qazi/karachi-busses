#!/usr/bin/env python3
"""Reconcile residual historical stop names against official SMTA entries.

Exact normalized names and explicit user-confirmed spelling aliases only.
No coordinates, geometry, or physical-stop assignments are produced.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESIDUAL = ROOT / "data/research/PHASE_5AA_REMAINING_UNMATCHED_STOP_CANDIDATES.csv"
SEQUENCES = ROOT / "data/research/PHASE_5AF_OFFICIAL_ROUTE_STOP_SEQUENCES.csv"
ALIASES = ROOT / "data/research/PHASE_5Y_USER_CONFIRMED_NAME_ALIASES.csv"
OUTPUT = ROOT / "data/research/PHASE_5AG_OFFICIAL_SEQUENCE_NAME_RECONCILIATION.csv"
REPORT = ROOT / "data/research/PHASE_5AG_OFFICIAL_SEQUENCE_NAME_RECONCILIATION_REPORT.json"

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = " ".join(value.split())
    value = re.sub(r"\bno\s+(\d+)\b", r"\1", value)
    value = re.sub(r"\b0+(\d+)\b", r"\1", value)
    return value

def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build() -> dict:
    residual = read(RESIDUAL)
    sequences = read(SEQUENCES)
    aliases = read(ALIASES)
    if len(residual) != 82:
        raise ValueError(f"Expected 82 residual unmatched rows, found {len(residual)}")
    allowed_types = {"direction_descriptor", "operator_published_named_entry"}
    if any(r.get("entry_type") not in allowed_types for r in sequences):
        raise ValueError("Official sequence register contains an unknown entry type")
    for route in {r["route_code"] for r in sequences}:
        route_rows = [r for r in sequences if r["route_code"] == route]
        if sum(r["entry_type"] == "direction_descriptor" for r in route_rows) != 1:
            raise ValueError(f"{route} must contain exactly one direction descriptor")
        if route_rows[0]["entry_type"] != "direction_descriptor":
            raise ValueError(f"{route} direction descriptor must be sequence 1")

    # Only explicit Phase 5Y user-confirmed equivalences may bridge spellings.
    alias_by_route: dict[str, dict[str, str]] = {}
    for row in aliases:
        if row.get("name_alias_status") != "confirmed_by_user" or row.get("confirmation_basis") != "user_confirmed_in_chat":
            raise ValueError("Unconfirmed alias found in Phase 5Y register")
        source = normalize(row.get("source_stop_name", ""))
        target = normalize((row.get("historical_node_id", "")).replace("_", " "))
        if not source or not target:
            raise ValueError("Blank alias source or target")
        for route in (row.get("route_codes") or "").split(";"):
            route = route.strip()
            if route:
                mapping = alias_by_route.setdefault(route, {})
                for key in (source, target):
                    existing = mapping.get(key)
                    if existing and existing != target:
                        raise ValueError(f"Conflicting confirmed aliases for {route}: {key}")
                    mapping[key] = target

    official_by_route: dict[str, list[dict[str, str]]] = {}
    descriptors_by_route: dict[str, list[dict[str, str]]] = {}
    for row in sequences:
        if row.get("entry_type") == "operator_published_named_entry":
            official_by_route.setdefault(row["route_code"], []).append(row)
        elif row.get("entry_type") == "direction_descriptor":
            descriptors_by_route.setdefault(row["route_code"], []).append(row)

    fields = [
        "route_code", "source_stop_sequence", "source_stop_name",
        "official_sequence_number", "official_entry_name", "official_entry_type", "official_source_url",
        "name_match_type", "match_count_for_source_row",
        "physical_stop_verification", "coordinate_assignment", "route_approval_status",
        "review_note",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    by_route = Counter()
    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for source in residual:
            route = source["route_code"]
            source_name = source["source_stop_name"]
            base = normalize(source_name)
            canonical = alias_by_route.get(route, {}).get(base, base)
            matches = []
            for official in official_by_route.get(route, []):
                official_base = normalize(official["entry_name"])
                official_canonical = alias_by_route.get(route, {}).get(official_base, official_base)
                if canonical and canonical == official_canonical:
                    match_type = "exact_normalized_name" if base == official_base else "user_confirmed_spelling_alias"
                    matches.append((official, match_type))
            if not matches:
                descriptor_matches = []
                for descriptor in descriptors_by_route.get(route, []):
                    descriptor_name = normalize(descriptor["entry_name"])
                    if base and f" {base} " in f" {descriptor_name} ":
                        descriptor_matches.append(descriptor)
                if descriptor_matches:
                    for descriptor in descriptor_matches:
                        writer.writerow({
                            "route_code": route,
                            "source_stop_sequence": source["source_stop_sequence"],
                            "source_stop_name": source_name,
                            "official_sequence_number": descriptor["sequence_number"],
                            "official_entry_name": descriptor["entry_name"],
                            "official_entry_type": "direction_descriptor",
                            "official_source_url": descriptor["official_source_url"],
                            "name_match_type": "direction_descriptor_reference_only",
                            "match_count_for_source_row": str(len(descriptor_matches)),
                            "physical_stop_verification": "unverified",
                            "coordinate_assignment": "not_assigned",
                            "route_approval_status": "not_approved",
                            "review_note": "Name appears only within the route direction descriptor (e.g. terminal/via corridor); not a separately numbered passenger stop",
                        })
                        counts["direction_descriptor_reference_only"] += 1
                        by_route[route] += 1
                    continue
                writer.writerow({
                    "route_code": route,
                    "source_stop_sequence": source["source_stop_sequence"],
                    "source_stop_name": source_name,
                    "official_sequence_number": "",
                    "official_entry_name": "",
                    "official_entry_type": "",
                    "official_source_url": "",
                    "name_match_type": "no_exact_sequence_name_match",
                    "match_count_for_source_row": "0",
                    "physical_stop_verification": "unverified",
                    "coordinate_assignment": "not_assigned",
                    "route_approval_status": "not_approved",
                    "review_note": "No exact normalized name or explicit user-confirmed alias in the same route; no fuzzy candidate accepted",
                })
                counts["unmatched"] += 1
                by_route[route] += 1
            else:
                for official, match_type in matches:
                    writer.writerow({
                        "route_code": route,
                        "source_stop_sequence": source["source_stop_sequence"],
                        "source_stop_name": source_name,
                        "official_sequence_number": official["sequence_number"],
                        "official_entry_name": official["entry_name"],
                        "official_entry_type": official["entry_type"],
                        "official_source_url": official["official_source_url"],
                        "name_match_type": match_type,
                        "match_count_for_source_row": str(len(matches)),
                        "physical_stop_verification": "unverified",
                        "coordinate_assignment": "not_assigned",
                        "route_approval_status": "not_approved",
                        "review_note": "Name/sequence comparison only; does not prove same physical stop, boarding side, or current operation",
                    })
                    counts[match_type] += 1
                    by_route[route] += 1
                if len(matches) > 1:
                    counts["ambiguous_source_rows"] += 1

    output_rows = read(OUTPUT)
    source_keys = {(r["route_code"], r["source_stop_sequence"]) for r in residual}
    output_keys = {(r["route_code"], r["source_stop_sequence"]) for r in output_rows}
    if source_keys != output_keys:
        raise ValueError("Output does not cover every residual source row exactly at least once")
    report = {
        "status": "name_only_reconciliation_not_physical_stop_verification",
        "residual_source_rows": len(residual),
        "output_rows": len(output_rows),
        "counts": dict(sorted(counts.items())),
        "source_rows_by_route": dict(sorted(Counter(r["route_code"] for r in residual).items())),
        "output_rows_by_route": dict(sorted(by_route.items())),
        "inputs": {
            "phase_5aa_residual_csv_sha256": sha256(RESIDUAL),
            "phase_5af_official_sequences_sha256": sha256(SEQUENCES),
            "phase_5y_confirmed_aliases_sha256": sha256(ALIASES),
        },
        "output_sha256": sha256(OUTPUT),
        "limitations": [
            "Only same-route exact normalized names and explicit Phase 5Y user-confirmed aliases are compared.",
            "No fuzzy similarity score is accepted as a match.",
            "A name match does not verify a physical passenger stop, boarding side, route direction, or live operation.",
            "No coordinates, OSM nodes, roads, route geometry, or database values are assigned.",
            "All records remain physically unverified and route approval remains not_approved.",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        parser.error("pass --build")
    print(json.dumps(build(), indent=2))

if __name__ == "__main__":
    main()
