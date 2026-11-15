# Karachi route data collection template

Use this worksheet to collect and validate data before entering it in Admin.

## Route register

| Field | Required | Guidance |
|---|---|---|
| route_code | Yes | Official/public route identifier |
| route_name | Yes | Commonly used route name |
| operator | If known | Link to operator record |
| source | Yes | Source record with publication or survey evidence |
| direction_name | Yes | E.g. Northbound / Southbound |
| start_label | Recommended | Origin terminal |
| end_label | Recommended | Destination terminal |
| source_date | Yes | Date the source was published or surveyed |
| verification_notes | Yes | How the route and direction were checked |

## Stop register

| Field | Required | Guidance |
|---|---|---|
| stop_name | Yes | Recognizable boarding/alighting stop |
| latitude | Yes | WGS84 decimal degrees |
| longitude | Yes | WGS84 decimal degrees |
| address | Recommended | Road, landmark or neighbourhood |
| source | Yes | Source record / survey |
| direction_sequence | Yes | Order within each direction |
| verification_notes | Yes | Coordinate and sequence checks |

## Collection rules
- Record forward and reverse directions separately.
- Use one shared stop record when two routes genuinely use the same boarding location.
- Do not merge stops on opposite sides of a road unless they are the same boarding point.
- Record source URL, source date, survey date and reviewer notes.
- Use under_review until the source and coordinates are checked.
- Draw route shapes along actual road geometry. GeoJSON coordinate order is longitude then latitude.
- Do not mark a route verified solely because it appears in an unverified crowd-sourced list.
- Publish only after the route and every stop have passed review.
