# Historical Karachi network dataset import

## What this import represents

This import consumes the two cleaned research files supplied for the project:

- `karachi_bus_network_cleaned_nodes.csv`: 572 named nodes and WGS84 coordinates.
- `karachi_bus_network_cleaned_edges.csv`: 1,415 directed stop-to-stop edges across 76 route identifiers.

The dataset's original author, publication date, source URL and redistribution licence have not yet been independently confirmed. The source record is therefore created with `verification_status='pending'`, and the importer deliberately does not identify a transport operator or claim that these routes currently operate.

## Important modelling choice

Some route edge lists form a single directed path; others branch or contain cycles. A branching edge list must not be flattened into a fabricated stop order. The importer therefore:

- creates stop records with `status='under_review'`;
- creates route records with `status='under_review'` and no operator;
- stores every source edge in `route_segments`, preserving its direction and source row order;
- creates `route_stops` only when the graph is exactly one simple directed path;
- does not create road-following geometry or `route_shapes`;
- never activates routes.

The 10 coordinate-collision groups and one self-loop in route 19-D were identified in the QA review. Distinct stop names at the same coordinate are preserved; the self-loop is retained as supplied and should be reviewed.

## Prepare input files

Place the cleaned CSVs at:

```
data/imports/karachi_bus_network_cleaned_nodes.csv
data/imports/karachi_bus_network_cleaned_edges.csv
```

Do not substitute the original uncleaned edge list unless it has been re-reviewed.

## Apply safely (Windows)

1. Back up the development database.
2. Ensure the current branch includes migrations 001–004.
3. Run `python scripts/migrate.py`.
4. Run a dry-run: `python scripts/import_historical_network.py`.
5. Inspect the counts and warnings.
6. Apply only to the intended development database:

```bat
python scripts/import_historical_network.py --apply --confirm-database karachi_buses
```

The importer is idempotent for matching source/route/stop records. It does not update existing records from other sources.

## After import

Verify counts in MySQL and review all source records before publication. This dataset must remain separate from the verified SMTA route catalogue until each route's current operating status, operator, stop names, stop coordinates and direction have been checked against authoritative or field-survey evidence.

A straight line between stops is not a road route. Road-following GeoJSON must be traced or sourced separately before route map publication.
