# Phase 5F — Pakistan OSM Extract Acquisition

**Status:** Preparation only. The repository workflow does not download data automatically. Run the script locally only after reviewing the source and available disk space.

## Selected source

Geofabrik's Pakistan regional OpenStreetMap extract:
- Landing page: https://download.geofabrik.de/asia/pakistan.html
- PBF: https://download.geofabrik.de/asia/pakistan-latest.osm.pbf
- Format: OSM PBF, suitable for Osmium and other OSM processing tools.
- Scope: all Pakistan, not Karachi-only.
- Licence: ODbL 1.0; attribution: © OpenStreetMap contributors.

Geofabrik's landing page identifies the PBF and its data timestamp/size, and links the ODbL licence. The exact current timestamp and file size must be recorded from the landing page at acquisition time; do not rely on a cached number in this document.

## Acquisition procedure

From the repository root:

```bash
python scripts/acquire_osm_road_data.py
```

This is a dry run: it makes no network request and writes no files.

After reviewing the source landing page and confirming disk capacity, explicitly authorize the download:

```bash
python scripts/acquire_osm_road_data.py --download
```

The script:
- Allows HTTPS downloads only from `download.geofabrik.de`.
- Uses an application-identifying User-Agent.
- Downloads the regional PBF to `data/osm_source/`.
- Checks a provider MD5 sidecar if one is published; absence of a sidecar is not treated as a failed checksum.
- Always computes SHA-256 and records file size, retrieval time, source, licence and attribution in `source-metadata.json`.
- Does not download tiles, query private services, write to MySQL, or publish route geometry.

MD5 is used only as an optional transport-integrity comparison, not as a security signature. SHA-256 is recorded for project provenance.

## Karachi extraction is a separate step

Do not treat the Pakistan PBF as a Karachi road network. Before clipping:
1. Obtain a Karachi administrative boundary from an openly licensed and clearly identified source, or derive it from the same OSM extract using documented administrative relation IDs and tags.
2. Review boundary geometry and administrative level; Karachi district/division/city boundaries are not interchangeable.
3. Record boundary source, OSM relation ID or source feature ID, retrieval timestamp, licence and SHA-256.
4. Require reviewer approval of the boundary map.
5. Only then use Osmium or another documented OSM tool to extract roads within the approved boundary.

Do not invent a bounding polygon from rough coordinates. Do not use the OSM standard tile service to create an offline map.

## Road filtering and routing

After the Karachi extract is approved, build a separate routable graph. Preserve source OSM IDs and relevant tags. Do not assume all `highway=*` ways are bus-accessible. Review one-way, access, bus, motor_vehicle, vehicle, service, construction, private, toll, bridge, tunnel and turn-restriction tags. Keep uncertain access cases flagged.

The routing profile must be selected and tested for bus routing; car routing is not automatically equivalent to a bus route. No bus profile or geometry is approved merely because a path can be computed.

## Output and review gates

Expected research-only outputs after future approved processing:
- Source PBF and `source-metadata.json` (keep large source data out of Git).
- Approved Karachi boundary with provenance.
- Karachi road extract and processing manifest.
- Road graph QA report.
- Candidate route geometries for each direction, each with source lineage and independent review.

No output from this phase may be imported into the passenger application until the Phase 5D physical-stop and operator-evidence gates are satisfied.

## Legal references

- Geofabrik Pakistan extract: https://download.geofabrik.de/asia/pakistan.html
- OSM copyright and licence: https://www.openstreetmap.org/copyright
- OSM tile usage policy: https://operations.osmfoundation.org/policies/tiles/
- OSM Foundation attribution guidance: https://osmfoundation.org/wiki/Attribution_Guidelines

This is an engineering compliance checklist, not legal advice. Confirm current licence and intended redistribution obligations before publishing any OSM-derived database.
