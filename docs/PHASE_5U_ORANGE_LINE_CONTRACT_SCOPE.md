# Phase 5U — Orange Line contract route scope and station identities

**Status:** The 2021 Facility Management Agreement provides four station IDs and distinguishes the dedicated Orange Line corridor from the wider bus journey. This is historical contract evidence, not current operator certification.

## Contract station identities

| Sequence | Station ID | Contract station name |
|---:|---|---|
| 1 | OL-1 | 5 No. Chowrangi |
| 2 | OL-2 | Orangi Town Police Station |
| 3 | OL-3 | Abdullah College |
| 4 | OL-4 | Dilpasand Sweets |

Source: [Orange Line Facility Management Agreement, Exhibit 1](https://pidcl.com.pk/wp-content/uploads/2021/02/Orange-Line-Project-Facility-Management-Agreement_compressed.pdf), station list.

## Contracted operating path is wider than the dedicated corridor

Schedule A, clauses 1.1–1.3, distinguishes:

1. **Dedicated Orange Line BRT corridor:** TMA Office Orangi to Board Office, described as 4 km with approximately four stations.
2. **Mixed-traffic extension:** Board Office to Hydri Station (Green Line).
3. **Shared Green Line BRT corridor:** Hydri to Nagan Station, then exit and U-turn in mixed traffic beneath the start of the Green Line elevated section.

The agreement says the total Orange Line project journey is 10 km. The same document's definition section describes an 8 km project from TMA Office Orangi to Board Office, while Schedule A describes 4 km for the dedicated BRT corridor. These are different scopes/length descriptions in one contract and must not be collapsed into a single geometry length.

## Published status and scope conflict

- SMTA's [Orange Line project page](https://smta.sindh.gov.pk/brt-abdul-sattar-edhi-line-orange-line) describes a 3.88 km corridor, four BRT stations, TMA Office Orangi to Jinnah University for Women near the Board Office, and states formal operations commenced on 10 September 2022.
- PIDCL's [project status page](https://pidcl.com.pk/) lists 4 km Orange Line operationalization/IITS and 1 km Green Line integration as 100% in 2025. This is project-completion reporting, not proof of current bus operation.
- SMTA's [current homepage](https://smta.gos.pk/) describes Orange Line as a planned addition. This conflicts with the project's historical commencement statement and PIDCL completion reporting.

The 2021 agreement's first page has an undated agreement placeholder and an operator placeholder. Treat it as contract-form scope evidence, not proof that the exact path remains in current service.

## Mapping decision

- Keep OL-1 through OL-4 as the four contract station identities.
- Do not add TMA Office, Board Office, Hydri or Nagan as additional Orange Line stations; they are corridor endpoints/interchange references in the wider operating path.
- Preserve the dedicated corridor, mixed-traffic segment and Green Line shared-corridor segment as separate path classes.
- Do not build or publish route geometry until the current operator confirms which of these segments are actually operated, current direction, stop/station sequence and physical boarding points.
- OSM remains the primary geographic source for later mapping; no coordinates are inferred in this phase.

## Output

`data/research/PHASE_5U_ORANGE_LINE_CONTRACT_SCOPE.csv` records the four station identities, three path segments, contract length-scope discrepancy, and conflicting published status statements.
