# Phase 5 — Karachi Data Collection and Verification

## Provenance model
- Every route must reference a data source.
- Every bus stop may reference a data source; active stops require a verified source.
- Sources record name, URL, notes, verification status, reviewer and verification timestamp.
- Administrative actions are written to audit_logs.
- Public APIs and journey search expose only active routes and active stops whose sources are verified.

## Admin workflow
1. Open Admin → Data sources & review.
2. Record the source, publication URL and evidence/field-survey notes.
3. A super administrator or data reviewer verifies the source.
4. Create route records and assign their source.
5. Create stops or import stops with the source assigned. Keep them under review until checked.
6. Review stop coordinates and names; only activate stops with a verified source.
7. Add each direction's ordered stops and draw/import its GeoJSON LineString.
8. A super administrator or data reviewer uses Verify & publish.
9. Publication requires a verified route source, at least one direction, two or more active verified-source stops per direction and a saved route shape for every direction.

## Duplicate checks
- Stop CSV imports reject repeated same-name coordinates within a small tolerance inside the upload.
- Imports also reject an existing same-name stop within the configured coordinate tolerance.
- Route codes have a database uniqueness constraint.
- Reviewers should still inspect aliases, spelling variants and route variants; near-duplicate text matching cannot establish that two physical stops are identical.

## CSV stop import
UTF-8 CSV columns:
- Required: stop_name, latitude, longitude
- Optional: address

The import form requires a source record. Imported stops are always created as under_review; no import automatically activates or publishes records.

## Karachi coverage quality checklist
- Source is authoritative or independently corroborated.
- Source date and survey date are recorded in notes.
- Route code and operator spelling are normalized.
- Forward and reverse directions are separate records.
- Stop coordinates are checked against the road/boarding side, not merely a broad neighbourhood centroid.
- Stop order is verified end-to-end.
- Route shape follows the actual road path and uses GeoJSON [longitude, latitude].
- Duplicate stops and alternate names are reviewed before publication.
- Uncertain services remain under_review and are not exposed publicly.

## Important data limitation
The repository does not include a verified comprehensive Karachi bus-route dataset. Do not create fictional route entries or mark unverified crowdsourced information as verified. Route coverage becomes complete only after a trusted dataset and field validation are obtained.
