# Historical network QA map

The admin-only, read-only review map is available at `/admin/historical-network`.

## Behaviour
- Reads only the data source named **Karachi Bus Network Research Dataset (user-provided cleaned files)**.
- Shows all source stops, grouped into marker clusters at wider zoom levels.
- Highlights distinct stop records sharing exactly the same stored coordinates. The popup lists every stop name; records are never merged.
- Provides a route-code filter and an optional overlay of the source's directed edge list.
- Draws edge overlays as dashed straight connectors between endpoint coordinates. They are explicitly labelled as source-listed links, **not road-following geometry**.
- Highlights self-loop segments (including route 19-D, segment 25) as review anomalies.
- Makes no database writes and cannot activate routes or verify the source.

## Verified development dataset snapshot
The local development import was checked after application:
- 572 stops, 76 routes, 76 directions
- 1,415 directed segments and 1,281 ordered route-stop rows
- all 76 routes remain `under_review`; source verification remains `pending`
- 10 coordinate-collision groups and one self-loop were identified

These counts describe the checked development database, not a claim that the records are current bus services.

## Dependencies
The map uses Leaflet and Leaflet.markercluster from their public CDN URLs. The underlying stop and segment data are served from authenticated Flask routes and are not embedded in the public map or service-worker cache.
