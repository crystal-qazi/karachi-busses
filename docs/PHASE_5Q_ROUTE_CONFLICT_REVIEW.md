# Phase 5Q — Route conflict review and evidence request register

**Status:** Evidence reconciliation complete for the currently available published source records. No operator confirmation has been received in this phase, so no route identity conflict is declared resolved and no route geometry is approved.

## Why this phase is needed

The SMTA-hosted route directory (accessed 17 November 2026) contains route-index termini and detailed route descriptions that disagree for several routes. The source itself attributes map data to Think Transportation and disclaims authentication of third-party service data. The 1 January 2025 SMTA-hosted map is a useful cross-check but is not proof of the current operating stop sequence.

The machine-readable companion file `data/research/PHASE_5Q_ROUTE_CONFLICT_REVIEW.csv` records, for R1–R4, R8, R11–R14, EV-01–EV-05, Green Line and Orange Line:
- both published endpoint representations;
- the precise sequence or identity issue;
- the conservative decision supported by existing records;
- the unresolved operator question;
- the exact evidence needed next; and
- a route geometry gate.

## Findings

### SMTA routes

- **R1:** Repeated Malir Halt and Kokharpar/Khokharapar 04 references are retained literally. There is insufficient evidence to decide whether this is a loop, repeated boarding point, or text duplication.
- **R2:** The route index says Powerhouse–Indus Hospital, while the detailed description says North Karachi–Korangi Crossing and places Indus Hospital before Korangi Crossing. Keep both representations.
- **R3:** Destination Nasir Jump agrees, but Powerhouse versus North Karachi origin remains unresolved.
- **R4:** Powerhouse versus North Karachi origin remains unresolved. Keamari/Kemari is a spelling variant candidate, not proof of an identical terminal record.
- **R8:** The index and detailed description use opposite directions. The via text also repeats Yousuf Goth. A reverse geometry must not be inferred.
- **R11:** Major identity conflict: Miran Naka–Shireen Jinnah Colony versus Mera Naka–Ziauddin Hospital. The 2025 map's Miran Nakka/Lyari/PIDC labels reinforce the need to keep variants separate.
- **R12:** Naddi Kinara–Lucky Star versus Memon Goth–Sadar Lucky Star may represent a changed route or variant. No automatic replacement.
- **R13:** Gulbai appears before Hawksbay and again later in the published sequence. Preserve the source order until the operator confirms the intended sequence.
- **R14:** Endpoints are textually consistent. This does not verify intermediate stops, exact terminal approach or physical boarding points.

### EV routes

EV-01 through EV-05 have consistent endpoint pairs in the route-index and detailed-description fields in the existing source register. EV-01's “Dolmen Mall” versus “Dolmen Mall Clifton” is retained as a naming variant candidate. Endpoint consistency is not proof that all intermediate stops remain current or that their order is correct.

### Green Line

The 22-station Abdullah Chowk (Surjani)–Numaish sequence remains a secondary-source candidate. Do not replace it with the older 22-node historical graph chain, which contains a materially different sequence. Require a current operator station list/map and station identifiers.

### Orange Line

Keep the four contract station identities (5 No. Chowrangi, Orangi Town Police Station, Abdullah College, Dilpasand Sweets) separate from the broader TMA Orangi–Jinnah University/Board Office corridor and mixed-traffic operating extension. A contract station list is not by itself a complete current operational stop sequence.

## Evidence request protocol

For each route variant, request:
1. route code and official route/service name;
2. effective-from date and superseded version, if any;
3. outbound and return direction separately;
4. ordered stop IDs and published stop names;
5. terminal/turnaround and boarding-side information;
6. whether the route is active, suspended, seasonal or changed;
7. operator-approved route map or trace.

Do not use a map screenshot without date/source metadata as sole proof of current operation. Preserve superseded variants rather than overwriting them.

## Geometry and publication gate

All rows remain `blocked` for route geometry. Geometry requires a confirmed route identity, direction-specific ordered stop list, verified physical boarding points and bus-accessible road path. OSM remains the primary geographic base; its one-way/access/bus restrictions must be checked. No arbitrary straight-line joins, snapping, inferred reverse routes, or database writes are permitted.

## Inputs

- `data/research/PHASE_5C_ROUTE_IDENTITY_CONFLICTS.csv`
- `data/research/PHASE_5C_OFFICIAL_ROUTE_REFERENCE_REGISTER.md`
- `data/research/PHASE_5C_PUBLISHED_ROUTE_STOPS.csv`
- `data/research/karachi-stop-review-register.csv`
- OpenStreetMap relation 6080948 and the Phase 5N/5O road candidate outputs.

OSM data attribution: © OpenStreetMap contributors. ODbL 1.0.
