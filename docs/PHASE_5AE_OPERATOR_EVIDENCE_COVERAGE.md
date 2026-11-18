# Phase 5AE — Official SMTA Route Evidence Coverage

## Purpose

Record accessible official SMTA route-detail pages for the nine historical route codes R1–R4, R8, R11–R14 and five EV routes. This is operator-published route-sequence evidence, not physical stop-coordinate verification.

## Official numbered route pages

SMTA currently publishes individual numbered route pages and labels each target route Active:

| Project code | Official page | Numbered entries | Published direction |
|---|---|---:|---|
| R1 | Route 01 (Pink) | 18 | Khokharapar 04–Dockyard |
| R2 | Route 02 (Pink) | 15 | North Karachi–Korangi Crossing |
| R3 | Route 03 (Pink) | 13 | North Karachi–Nasir Jump |
| R4 | Route 04 | 14 | North Karachi–Kemari |
| R8 | Route 08 | 13 | Yousuf Goth–Tower |
| R11 | Route 11 | 11 | Mera Naka–Ziauddin Hospital |
| R12 | Route 12 | 15 | Memon Goth–Sadar Lucky Star |
| R13 | Route 13 | 10 | Hawksbay–Tower |
| R14 | Route 14 | 16 | Maymar–Tower |

The EV pages publish 18, 8, 16, 10 and 10 numbered entries for EV-01 through EV-05 respectively.

## Material source conflicts retained

- R2 and R3: individual route pages show North Karachi origins, while the route-map index and older historical summary use Powerhouse origins. Keep this as a source-version conflict.
- R11: individual detail page says Mera Naka–Ziauddin Hospital; route-map index says Miran Naka–Shireen Jinnah Colony.
- R12: individual detail page says Memon Goth–Sadar Lucky Star; route-map index says Naddi Kinara–Lucky Star.
- R14: individual detail page and provincial directory list it as Active, but the map's short route-index list omits it.
- The first numbered entry on each route page is a direction/terminal descriptor. The count is the number of published numbered entries, not a claim that every entry is a distinct intermediate passenger stop.

## Limits

The pages establish what SMTA publishes as route identity, direction, sequence, distance, and status. They do not provide geodetic boarding coordinates, exact carriageway side, stop-pole identity, or live dispatch telemetry. Do not snap stops to OSM roads or generate route geometry until physical boarding points and directions are verified. OSM remains the primary geographic source.

## Output

- `data/research/PHASE_5AE_OPERATOR_EVIDENCE_COVERAGE.csv`
