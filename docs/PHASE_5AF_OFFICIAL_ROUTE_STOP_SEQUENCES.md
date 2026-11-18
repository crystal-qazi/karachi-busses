# Phase 5AF — Official SMTA Numbered Route Entries

## Purpose

Store numbered entries displayed on individual Sindh Mass Transit Authority (SMTA) route-detail pages. Source pages were accessed on 2026-11-18. This register now includes active and inactive R-series routes, EV routes, and the Double Decker route.

## Register

- `data/research/PHASE_5AF_OFFICIAL_ROUTE_STOP_SEQUENCES.csv`
- **268 numbered entries across 20 route pages**.
- Each route's first numbered item is typed `direction_descriptor`. It is the page's terminal/direction summary (often followed by “via …”), not a separately inferred passenger stop.
- Remaining items are typed `operator_published_named_entry` and preserve SMTA's displayed sequence and spelling.
- Sequence numbers are the numbers printed on each page; they are not coordinates, stop-pole IDs, or proof of physical boarding locations.
- Published inactive status is retained as `Inactive`; these sequences must not be presented as currently operating services.

## Source pages

- R1–R7: `https://smta.gos.pk/routes/1` through `/7` (R5–R7 currently marked inactive)
- R8–R14: `https://smta.gos.pk/routes/8` through `/14`
- EV-01–EV-05: `https://smta.gos.pk/routes/15` through `/19`
- DD01: `https://smta.gos.pk/routes/27`

## Known source-version conflicts retained

- R1: SMTA detail page uses Khokharapar 04 / Kokharpar 04, while the supplied Think Transportation KML label uses Khokrapar No. 1.
- R2 and R3 individual detail pages show North Karachi origins, while the route-map index and supplied KML labels use Powerhouse origins.
- R4 individual detail page describes North Karachi to Kemari, while the route-map index and KML label use Powerhouse to Keamari.
- R9 and R10 are now included from their individual SMTA pages; their published stop lists are not treated as coordinate evidence.
- R11 detail page shows Mera Naka–Ziauddin Hospital; the route-map index lists Miran Naka–Shireen Jinnah Colony.
- R12 detail page shows Memon Goth–Sadar Lucky Star; the route-map index lists Naddi Kinara–Lucky Star.
- R14 appears in the provincial directory and its individual page, while it is absent from the supplied KML route inventory.
- R5–R7 are listed by SMTA but marked inactive. DD01 is listed as active and is absent from the supplied KML route inventory.
- The SMTA route-map page credits Think Transportation for map data and disclaims authentication of third-party service data. Individual SMTA detail pages are used for the published numbered sequences; route-index differences remain separately recorded.

## Limits and next step

This is a transcription of operator-published page content, not field verification. It does not assert that each named area has a current passenger stop, that a bus boards at a specific pole or carriageway side, or that a service is currently dispatched. It assigns no coordinates, OSM nodes, roads, or route geometry. Physical stop identity and boarding location require independent evidence.

**Geometry source policy:** the supplied Think Transportation KML is the primary route-line geometry reference where it contains a route. SMTA is authoritative for its published route status, names and numbered sequences. OSM is supporting geographic/road context only; it does not replace or rewrite KML geometry.

No historical stop rows are overwritten, no fuzzy matches are accepted, no coordinates are assigned, and no route is approved by this register.
