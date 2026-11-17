#!/usr/bin/env python3
"""Acquire a public Geofabrik Pakistan OSM PBF with explicit user consent.

Safe by default: without --download this script only prints the planned request.
It never downloads map tiles, calls Overpass, accesses private services, or modifies
the application database.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

DATA_URL = "https://download.geofabrik.de/asia/pakistan-latest.osm.pbf"
CHECKSUM_URL = DATA_URL + ".md5"
ALLOWED_HOST = "download.geofabrik.de"
USER_AGENT = "KarachiBusesResearch/1.0 (+https://github.com/crystal-qazi/karachi-busses)"


def validate_source(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise ValueError("Only HTTPS downloads from download.geofabrik.de are allowed.")


def parse_md5(text: str) -> str:
    match = re.search(r"\b([0-9a-fA-F]{32})\b", text)
    if not match:
        raise ValueError("The source checksum file did not contain a valid MD5 digest.")
    return match.group(1).lower()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(url: str, destination: Path) -> None:
    validate_source(url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)


def acquire(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    pbf = output_dir / "pakistan-latest.osm.pbf"
    fetch(DATA_URL, pbf)
    # Geofabrik lists MD5 sidecars for some dated extracts; do not assume the
    # moving latest endpoint always publishes one. SHA-256 is always computed.
    expected_md5 = None
    actual_md5 = None
    try:
        checksum_file = output_dir / "pakistan-latest.osm.pbf.md5"
        fetch(CHECKSUM_URL, checksum_file)
        expected_md5 = parse_md5(checksum_file.read_text(encoding="ascii", errors="replace"))
        md5 = hashlib.md5()
        with pbf.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                md5.update(chunk)
        actual_md5 = md5.hexdigest()
        if actual_md5 != expected_md5:
            pbf.unlink(missing_ok=True)
            raise ValueError(f"MD5 mismatch: expected {expected_md5}, received {actual_md5}. PBF deleted.")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            pbf.unlink(missing_ok=True)
            raise
    metadata = {
        "provider": "Geofabrik",
        "source_url": DATA_URL,
        "checksum_url": CHECKSUM_URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_checksum_algorithm": "MD5 (when provider sidecar is available; transport integrity only)",
        "source_md5_expected": expected_md5,
        "source_md5_actual": actual_md5,
        "file_sha256": sha256_file(pbf),
        "file_name": pbf.name,
        "file_size_bytes": pbf.stat().st_size,
        "data_license": "Open Database License 1.0 (ODbL)",
        "attribution": "© OpenStreetMap contributors",
        "scope": "Pakistan regional extract; not yet clipped to Karachi",
        "warning": "Do not publish derived database without reviewing ODbL obligations."
    }
    (output_dir / "source-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/osm_source"))
    parser.add_argument("--download", action="store_true",
                        help="Actually download the public Pakistan PBF and verify its checksum.")
    args = parser.parse_args()
    validate_source(DATA_URL)
    validate_source(CHECKSUM_URL)
    if not args.download:
        print("DRY RUN: no network request or file write performed.")
        print(f"Source: {DATA_URL}")
        print(f"Checksum: {CHECKSUM_URL}")
        print(f"Output: {args.output_dir.resolve()}")
        print("Review the source licence and run again with --download to proceed.")
        return 0
    try:
        metadata = acquire(args.output_dir)
    except (OSError, urllib.error.URLError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
