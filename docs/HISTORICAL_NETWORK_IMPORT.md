# Historical Karachi network dataset import

## What this import represents

This import consumes the two cleaned research files supplied for the project:

- `karachi_bus_network_cleaned_nodes.csv`: 572 named nodes and WGS84 coordinates.
- `karachi_bus_network_cleaned_edges.csv`: 1,415 directed stop-to-stop edges across 76 route identifiers.

The source provenance has now been identified: Data Research Lab Pakistan's *Karachi Bus Network* dataset, published 18 October 2024, DOI `10.5281/zenodo.13951512`, with creators Muhammad Qasim Pasta, Moid Raza Khan and Fatima Aslam (Habib University affiliation). The Lab's project page states a Creative Commons Attribution 4.0 International licence. The Zenodo record's own Rights/License fields are blank, so the project page is retained as the explicit licence evidence. The dataset description says route text was compiled from Travel Culture and HamariWeb and coordinates were extracted using Google Maps. This establishes dataset attribution/licence, not current operator accuracy or boarding-point accuracy. The source record should retain pending verification until the project reviewer completes source review; the importer still does not identify a transport operator or claim that these routes currently operate.

## Canonical source and file reconciliation

- Canonical dataset: [Zenodo 13951512 — Karachi Bus Network](https://doi.org/10.5281/zenodo.13951512), published 18 October 2024 by Data Research Lab Pakistan.
- Creators: Muhammad Qasim Pasta (data curator), Moid Raza Khan and Fatima Aslam (data collectors); Habib University affiliation.
- The Lab's project page states **CC BY 4.0**: https://darlab-pakistan.github.io/karachi-bus-network/
- Methodology disclosed by the Lab: route descriptions were sourced from Travel Culture and HamariWeb; stop coordinates were extracted using Google Maps.
- The previously cited Zenodo ID `13932672` is unrelated: it identifies the `xIndices` climate-variability software package, not the Karachi dataset. Do not cite it for this import.
- The canonical Zenodo download contains 572 node rows and 1,490 directed edge rows. The project's cleaned files contain 572 node rows and 1,415 directed edge rows. The 75-edge difference has not yet been reconciled to a documented cleaning log. Keep the cleaned import file unchanged until a row-level difference report explains every removed or altered edge.
- The source node file uses the same `node,latit,long` schema as the project's cleaned node file. Do not assume this proves every coordinate has been independently verified.

The source attribution and licence discovery do not change the dataset's historical/secondary-source status. It remains unsuitable as current operator truth or passenger-facing verified route data.

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
