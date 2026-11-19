#!/usr/bin/env python3
"""Compare the published Zenodo edge CSV with the project's cleaned edge CSV.

Downloads only the public source CSV to a temporary directory, performs a
multiset (duplicate-aware) row comparison, and emits a small delta report.
The source CSV is not copied into the repository or uploaded as an artifact.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://zenodo.org/records/13951512/files/karachi_bus_network_edge_list.csv?download=1"
ALLOWED_HOST = "zenodo.org"
USER_AGENT = "KarachiBusesResearch/1.0 (+https://github.com/crystal-qazi/karachi-busses)"
LOCAL_EDGES = ROOT / "data/imports/karachi_bus_network_cleaned_edges.csv"
OUTPUT = ROOT / "data/research/PHASE_5BI_HISTORICAL_EDGE_SOURCE_DELTA.csv"
REPORT = ROOT / "data/research/PHASE_5BI_HISTORICAL_EDGE_SOURCE_DELTA_REPORT.json"
EXPECTED_COLUMNS = {"stop1", "stop2", "bus_name"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_source_url(url: str = SOURCE_URL) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise ValueError("Only HTTPS downloads from zenodo.org are allowed.")


def download_source(destination: Path, attempts: int = 3) -> dict:
    validate_source_url()
    last_error = None
    for attempt in range(attempts):
        request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as output:
                first = response.read(512)
                if first.lstrip().lower().startswith((b"<!doctype html", b"<html")):
                    raise ValueError("Zenodo returned an HTML page instead of the source CSV.")
                output.write(first)
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
            if destination.stat().st_size == 0:
                raise ValueError("Downloaded source CSV is empty.")
            return {
                "source_url": SOURCE_URL,
                "file_size_bytes": destination.stat().st_size,
                "sha256": sha256_file(destination),
                "download_attempt": attempt + 1,
            }
        except (OSError, urllib.error.URLError, ValueError) as exc:
            last_error = exc
            destination.unlink(missing_ok=True)
            if attempt + 1 < attempts:
                time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f"Unable to download canonical Zenodo edge CSV after {attempts} attempts: {last_error}")


def read_edges(path: Path) -> list[tuple[str, str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = set(reader.fieldnames or [])
        missing = EXPECTED_COLUMNS - columns
        if missing:
            raise ValueError(f"{path.name} is missing required columns: {', '.join(sorted(missing))}")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            edge = tuple((row.get(column) or "").strip() for column in ("stop1", "stop2", "bus_name"))
            if not all(edge):
                raise ValueError(f"{path.name} contains a blank edge field on CSV line {line_number}.")
            rows.append(edge)
    return rows


def duplicate_occurrences(rows: list[tuple[str, str, str]]) -> int:
    counts = Counter(rows)
    return sum(count - 1 for count in counts.values() if count > 1)


def compare(source_path: Path, local_path: Path,
            output_path: Path = OUTPUT, report_path: Path = REPORT,
            download_metadata: dict | None = None) -> dict:
    source_rows = read_edges(source_path)
    local_rows = read_edges(local_path)
    source_counts = Counter(source_rows)
    local_counts = Counter(local_rows)

    missing_counts = source_counts - local_counts
    extra_counts = local_counts - source_counts
    missing_rows = sorted(missing_counts.items())
    extra_rows = sorted(extra_counts.items())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["delta_type", "stop1", "stop2", "bus_name", "occurrences"])
        writer.writeheader()
        for edge, count in missing_rows:
            writer.writerow({"delta_type": "present_in_zenodo_missing_from_project", "stop1": edge[0], "stop2": edge[1], "bus_name": edge[2], "occurrences": count})
        for edge, count in extra_rows:
            writer.writerow({"delta_type": "present_in_project_missing_from_zenodo", "stop1": edge[0], "stop2": edge[1], "bus_name": edge[2], "occurrences": count})

    missing_by_route = Counter()
    extra_by_route = Counter()
    for edge, count in missing_rows:
        missing_by_route[edge[2]] += count
    for edge, count in extra_rows:
        extra_by_route[edge[2]] += count

    report = {
        "status": "reconciled" if not missing_counts and not extra_counts else "row_level_delta_found",
        "source": {
            "url": SOURCE_URL,
            "doi": "10.5281/zenodo.13951512",
            "file": source_path.name,
            "sha256": sha256_file(source_path),
            "edge_rows": len(source_rows),
            "distinct_edge_rows": len(source_counts),
            "exact_duplicate_occurrences": duplicate_occurrences(source_rows),
        },
        "project_cleaned_file": {
            "file": local_path.name,
            "sha256": sha256_file(local_path),
            "edge_rows": len(local_rows),
            "distinct_edge_rows": len(local_counts),
            "exact_duplicate_occurrences": duplicate_occurrences(local_rows),
        },
        "comparison": {
            "matched_edge_occurrences": sum((source_counts & local_counts).values()),
            "rows_present_in_zenodo_missing_from_project": sum(missing_counts.values()),
            "distinct_edge_variants_missing_from_project": len(missing_counts),
            "rows_present_in_project_missing_from_zenodo": sum(extra_counts.values()),
            "distinct_edge_variants_extra_in_project": len(extra_counts),
            "missing_rows_by_route": dict(sorted(missing_by_route.items())),
            "extra_rows_by_route": dict(sorted(extra_by_route.items())),
            "normalization": "Surrounding whitespace stripped; case, punctuation, node spelling, direction and route code preserved exactly; multiset counts preserve duplicates.",
        },
        "download": download_metadata or {},
        "outputs": {"delta_csv": str(output_path)},
        "limitations": [
            "A row-level difference does not by itself establish why an edge was changed or omitted.",
            "Do not infer that missing rows are duplicates, errors or inactive service without source evidence.",
            "No source or project CSV is modified, and no database or application data is written.",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download the canonical Zenodo CSV and compare it.")
    args = parser.parse_args()
    if not args.download:
        print("DRY RUN: no network request or files changed.")
        print(f"Source: {SOURCE_URL}")
        print(f"Project file: {LOCAL_EDGES}")
        print(f"Delta output: {OUTPUT}")
        print("Run with --download to retrieve the source and perform a duplicate-aware row comparison.")
        return 0

    try:
        with tempfile.TemporaryDirectory(prefix="karachi-edge-audit-") as temp_dir:
            source_path = Path(temp_dir) / "karachi_bus_network_edge_list.csv"
            metadata = download_source(source_path)
            report = compare(source_path, LOCAL_EDGES, OUTPUT, REPORT, metadata)
        print(json.dumps(report, indent=2))
    except (OSError, ValueError, RuntimeError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
