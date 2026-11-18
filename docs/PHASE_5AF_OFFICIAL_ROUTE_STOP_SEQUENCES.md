# Phase 5AF — Official SMTA Numbered Route Entries

## Purpose

Store every numbered entry displayed on the individual Sindh Mass Transit Authority (SMTA) route-detail pages for R1–R4, R8, R11–R14 and EV-01–EV-05. Source pages were accessed on 2026-11-18.

## Register

- `data/research/PHASE_5AF_OFFICIAL_ROUTE_STOP_SEQUENCES.csv`
- 187 numbered entries across 14 route pages.
- Each route's first numbered item is typed `direction_descriptor`. It is the page's terminal/direction summary (often followed by “via …”), not a separately inferred passenger stop.
- Remaining items are typed `operator_published_named_entry` and preserve SMTA's displayed sequence and spelling.
- Sequence numbers are the numbers printed on each page; they are not coordinates, stop-pole IDs, or proof of physical boarding locations.

## Source pages

- R1 (Route 01; Pink Bus; 18 numbered entries): https://smta.gos.pk/routes/1
- R2 (Route 02; Pink Bus; 15 numbered entries): https://smta.gos.pk/routes/2
- R3 (Route 03; Pink Bus; 13 numbered entries): https://smta.gos.pk/routes/3
- R4 (Route 04; People's Bus Service; 14 numbered entries): https://smta.gos.pk/routes/4
- R8 (Route 08; People's Bus Service; 13 numbered entries): https://smta.gos.pk/routes/8
- R11 (Route 11; People's Bus Service; 11 numbered entries): https://smta.gos.pk/routes/11
- R12 (Route 12; People's Bus Service; 15 numbered entries): https://smta.gos.pk/routes/12
- R13 (Route 13; People's Bus Service; 10 numbered entries): https://smta.gos.pk/routes/13
- R14 (Route 14; People's Bus Service; 16 numbered entries): https://smta.gos.pk/routes/14
- EV-01 (EV-01; Electric Bus; 18 numbered entries): https://smta.gos.pk/routes/15
- EV-02 (EV-02; Electric Bus; 8 numbered entries): https://smta.gos.pk/routes/16
- EV-03 (EV-03; Electric Bus; 16 numbered entries): https://smta.gos.pk/routes/17
- EV-04 (EV-04; Electric Bus; 10 numbered entries): https://smta.gos.pk/routes/18
- EV-05 (EV-05; Electric Bus; 10 numbered entries): https://smta.gos.pk/routes/19

## Known source-version conflicts retained

- R2 and R3 individual detail pages show North Karachi origins, while the route-map index lists Powerhouse origins.
- R11 detail page shows Mera Naka–Ziauddin Hospital; the route-map index lists Miran Naka–Shireen Jinnah Colony.
- R12 detail page shows Memon Goth–Sadar Lucky Star; the route-map index lists Naddi Kinara–Lucky Star.
- R14 appears in the provincial directory and its individual page, while the map's short route-index list omits it.
- The route-map page disclaims authentication of third-party map service data. This register uses the individual SMTA detail pages as the sequence source and keeps index conflicts separate.

## Limits and next step

This is a transcription of operator-published page content, not field verification. It does not assert that each named area has a current passenger stop, that a bus boards at a specific pole or carriageway side, or that the service is currently dispatched. It assigns no coordinates, OSM nodes, roads, or route geometry. OSM remains the primary geographic reference, but physical stop identity must be verified independently before matching coordinates or creating road-following geometry.

No historical stop rows are overwritten, no fuzzy matches are accepted, and no route is approved by this register.
