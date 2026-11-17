#!/usr/bin/env python3
"""Acquire one complete OpenStreetMap relation through the public OSM API.

Dry-run by default. With --download, fetches only the explicitly selected
relation's /full XML from api.openstreetmap.org, validates its identity, and
records provenance. It does not call Overpass, scrape tiles, edit OSM, create
a polygon, or modify the application database.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

RELATION_ID = 6080948
API_URL = f"https://api.openstreetmap.org/api/0.6/relation/{RELATION_ID}/full"
ALLOWED_HOST = "api.openstreetmap.org"
USER_AGENT = "KarachiBusesResearch/1.0 (+https://github.com/crystal-qazi/karachi-busses)"


def validate_source(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise ValueError("Only HTTPS requests to api.openstreetmap.org are allowed.")
    if parsed.path != f"/api/0.6/relation/{RELATION_ID}/full":
        raise ValueError("Only the explicitly selected Karachi Division relation /full endpoint is allowed.")


class SameHostRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_source(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_relation(xml_path: Path) -> dict:
    root = ET.parse(xml_path).getroot()
    relation = root.find(f"./relation[@id='{RELATION_ID}']")
    if relation is None:
        raise ValueError(f"Response does not contain expected relation {RELATION_ID}.")

    tags = {item.attrib["k"]: item.attrib["v"] for item in relation.findall("tag")}
    if tags.get("boundary") != "administrative":
        raise ValueError("Selected relation is not tagged boundary=administrative.")
    if tags.get("name") not in {"Karachi Division", "Karachi"}:
        raise ValueError(f"Unexpected relation name: {tags.get('name')!r}")

    members = [
        {"type": m.attrib.get("type"), "ref": m.attrib.get("ref"), "role": m.attrib.get("role", "")}
        for m in relation.findall("member")
    ]
    way_ids = {m["ref"] for m in members if m["type"] == "way"}
    node_ids = {
        n.attrib["id"]
        for way in root.findall("way")
        for n in way.findall("nd")
    }
    return {
        "relation_id": RELATION_ID,
        "tags": tags,
        "version": relation.attrib.get("version"),
        "timestamp": relation.attrib.get("timestamp"),
        "changeset": relation.attrib.get("changeset"),
        "member_count": len(members),
        "member_way_count": len(way_ids),
        "member_node_reference_count": len(node_ids),
        "outer_member_count": sum(1 for m in members if m["role"] == "outer"),
        "inner_member_count": sum(1 for m in members if m["role"] == "inner"),
        "other_member_count": sum(1 for m in members if m["role"] not in {"outer", "inner"}),
        "members": members,
    }


def acquire(output_dir: Path) -> dict:
    validate_source(API_URL)
    output_dir.mkdir(parents=True, exist_ok=True)
    xml_path = output_dir / f"osm-relation-{RELATION_ID}-full.osm"
    request = urllib.request.Request(API_URL, headers={"User-Agent": USER_AGENT})
    opener = urllib.request.build_opener(SameHostRedirectHandler)
    with opener.open(request, timeout=60) as response, xml_path.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)

    inspected = inspect_relation(xml_path)
    metadata = {
        "provider": "OpenStreetMap API",
        "source_url": API_URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_name": xml_path.name,
        "file_size_bytes": xml_path.stat().st_size,
        "file_sha256": sha256_file(xml_path),
        "license": "Open Database License 1.0 (ODbL)",
        "attribution": "© OpenStreetMap contributors",
        "geometry_status": "raw relation XML acquired; polygon geometry not yet assembled or validated",
        "inspection": inspected,
    }
    (output_dir / "relation-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/osm_boundary"))
    parser.add_argument("--download", action="store_true",
                        help="Fetch the selected OSM relation /full XML and write a provenance manifest.")
    args = parser.parse_args()
    validate_source(API_URL)
    if not args.download:
        print("DRY RUN: no network request or file write performed.")
        print(f"Relation: {RELATION_ID}")
        print(f"Source: {API_URL}")
        print(f"Output: {args.output_dir.resolve()}")
        print("Review OSM attribution/ODbL terms and run with --download to acquire.")
        return 0
    try:
        print(json.dumps(acquire(args.output_dir), indent=2))
    except (OSError, urllib.error.URLError, ET.ParseError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
