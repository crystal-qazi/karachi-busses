#!/usr/bin/env python3
"""Extract one OSM administrative relation from a locally acquired regional PBF.

Dry-run by default. With --extract, runs the local Osmium Tool; no network
requests are made. The script never edits OSM, scrapes raster tiles, or changes
the application database.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

RELATION_ID = 6080948


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
        raise ValueError(f"Extract does not contain expected relation {RELATION_ID}.")

    tags = {item.attrib["k"]: item.attrib["v"] for item in relation.findall("tag")}
    if tags.get("boundary") != "administrative":
        raise ValueError("Selected relation is not tagged boundary=administrative.")
    if tags.get("name") not in {"Karachi Division", "Karachi"}:
        raise ValueError(f"Unexpected relation name: {tags.get('name')!r}")

    members = [
        {"type": m.attrib.get("type"), "ref": m.attrib.get("ref"), "role": m.attrib.get("role", "")}
        for m in relation.findall("member")
    ]
    available = {
        "node": {item.attrib["id"] for item in root.findall("node")},
        "way": {item.attrib["id"] for item in root.findall("way")},
        "relation": {item.attrib["id"] for item in root.findall("relation")},
    }
    missing = [
        member for member in members
        if member["type"] not in available or member["ref"] not in available[member["type"]]
    ]
    if missing:
        raise ValueError(f"Extract is missing {len(missing)} direct relation members.")

    way_node_refs = {
        node.attrib["ref"]
        for way in root.findall("way")
        for node in way.findall("nd")
    }
    available_nodes = available["node"]
    missing_way_nodes = sorted(way_node_refs - available_nodes)
    if missing_way_nodes:
        raise ValueError(f"Extract is missing {len(missing_way_nodes)} nodes referenced by member ways.")

    return {
        "relation_id": RELATION_ID,
        "tags": tags,
        "version": relation.attrib.get("version"),
        "timestamp": relation.attrib.get("timestamp"),
        "changeset": relation.attrib.get("changeset"),
        "member_count": len(members),
        "member_way_count": sum(1 for m in members if m["type"] == "way"),
        "member_relation_count": sum(1 for m in members if m["type"] == "relation"),
        "member_node_count": sum(1 for m in members if m["type"] == "node"),
        "outer_member_count": sum(1 for m in members if m["role"] == "outer"),
        "inner_member_count": sum(1 for m in members if m["role"] == "inner"),
        "other_member_count": sum(1 for m in members if m["role"] not in {"outer", "inner"}),
        "included_nodes": len(available_nodes),
        "included_ways": len(available["way"]),
        "included_relations": len(available["relation"]),
        "missing_direct_members": 0,
        "missing_way_nodes": 0,
        "members": members,
    }


def extract_from_pbf(input_pbf: Path, output_dir: Path) -> dict:
    if not input_pbf.is_file():
        raise FileNotFoundError(
            f"OSM PBF not found: {input_pbf}. First run scripts/acquire_osm_road_data.py --download."
        )
    osmium = shutil.which("osmium")
    if not osmium:
        raise FileNotFoundError("Osmium Tool is not installed or not available on PATH.")

    output_dir.mkdir(parents=True, exist_ok=True)
    xml_path = output_dir / f"osm-relation-{RELATION_ID}-full.osm"
    command = [
        osmium, "getid", "-r", "-f", "osm", "-o", str(xml_path),
        str(input_pbf), f"r{RELATION_ID}",
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)

    inspected = inspect_relation(xml_path)
    metadata = {
        "provider": "Geofabrik Pakistan OSM extract; relation extracted locally with Osmium Tool",
        "input_pbf": str(input_pbf),
        "input_pbf_size_bytes": input_pbf.stat().st_size,
        "input_pbf_sha256": sha256_file(input_pbf),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "extract_command": "osmium getid -r -f osm <input-pbf> r6080948",
        "relation_xml": xml_path.name,
        "relation_xml_size_bytes": xml_path.stat().st_size,
        "relation_xml_sha256": sha256_file(xml_path),
        "license": "Open Database License 1.0 (ODbL)",
        "attribution": "© OpenStreetMap contributors",
        "geometry_status": "complete referenced OSM objects extracted; polygon geometry not yet assembled or validated",
        "inspection": inspected,
    }
    (output_dir / "relation-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-pbf", type=Path, default=Path("data/osm_source/pakistan-latest.osm.pbf"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/osm_boundary"))
    parser.add_argument("--extract", action="store_true",
                        help="Extract relation 6080948 from the local PBF using Osmium Tool.")
    args = parser.parse_args()
    if not args.extract:
        print("DRY RUN: no network request, file write, or extraction performed.")
        print(f"Input PBF: {args.input_pbf.resolve()}")
        print(f"Selected relation: {RELATION_ID}")
        print(f"Output: {args.output_dir.resolve()}")
        print("After the separately approved Geofabrik PBF download and Osmium installation, run with --extract.")
        return 0
    try:
        print(json.dumps(extract_from_pbf(args.input_pbf, args.output_dir), indent=2))
    except (OSError, subprocess.CalledProcessError, ET.ParseError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
