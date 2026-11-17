# Phase 5O — Stop-to-OSM Road Proximity Audit

## Purpose

Compare existing historical coordinate candidates in `PHASE_5_STOP_NODE_CROSSWALK.csv` with the OSM candidate-road inventory from Phase 5N. This creates a review queue showing the nearest road way, its name/class/direction/access tags, and geometric distance.

## Strict interpretation

A proximity result is not a verified stop. The coordinate crosswalk is based on exact normalized name candidates against a historical 572-node dataset. It does not establish a current physical boarding point, platform, road side, or operator-approved route. No automatic geocoding, snapping, route construction, stop relocation, or database write is performed.

Unmatched source stops remain unmatched. Rows with no coordinate candidate are explicitly retained with `no_coordinate_candidate`.

## Distance bands

- 0–15 m
- 15–50 m
- 50–100 m
- 100–250 m
- over 250 m

These are triage bands only, not pass/fail acceptance thresholds. The report includes up to five nearby distinct OSM way candidates within 250 m where available. The nearest candidate is selected geometrically, not by bus suitability.

## Python-only workflow

```powershell
python -m pip install -r requirements-gis.txt
python scripts/audit_stop_road_proximity.py --build
```

No additional executable, external routing service, geocoder, or production database is used. GitHub Actions downloads the Geofabrik regional PBF and runs the same pip-only process in an ephemeral runner.

## Outputs

- `data/osm_roads/stop-road-proximity-audit.csv`
- `data/osm_roads/stop-road-proximity-report.json`

The report records source hashes, row counts, distance bands, and explicit limitations. OSM attribution and ODbL terms are retained.

## Next review gate

Use this audit to prioritize operator/field checks. Confirm physical stop location, boarding side/platform, bus-specific access, one-way restrictions, route identity, and direction before any stop is approved or any route geometry is created.
