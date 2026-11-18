-- Phase 5AX: metadata-only provenance correction for the historical network source.
-- Review the SELECT output before executing the UPDATE.
-- This script does not insert/delete rows and does not alter verification_status.
-- It does not modify bus_routes, bus_stops, route_stops, route_segments or route_shapes.

START TRANSACTION;

SELECT
    id,
    source_name,
    source_url,
    verification_status,
    notes
FROM data_sources
WHERE source_name = 'Karachi Bus Network Research Dataset (user-provided cleaned files)'
FOR UPDATE;

UPDATE data_sources
SET
    source_url = 'https://zenodo.org/records/13951512',
    notes = CONCAT(
        'Historical 2024 research dataset, Version v1, published 2024-10-18 by Data Research Lab Pakistan; ',
        'creators: Muhammad Qasim Pasta (curator), Moid Raza Khan and Fatima Aslam (collectors), Habib University. ',
        'The Zenodo description says 76 Karachi public bus routes (BRT and minibuses) were compiled from ',
        'Travel Culture and HamariWeb, with stop coordinates extracted using Google Maps. ',
        'The node/edge files are historical secondary research, not current operator GPS or proof of current service. ',
        'No per-stop source pins or capture dates are supplied. The publisher companion project page declares CC BY 4.0; ',
        'the Zenodo record visible Rights section has no displayed value, so preserve this distinction in attribution notes. ',
        'Keep verification_status pending because this is historical secondary data, not current operator evidence.'
    )
WHERE source_name = 'Karachi Bus Network Research Dataset (user-provided cleaned files)';

SELECT ROW_COUNT() AS affected_rows;

SELECT
    id,
    source_name,
    source_url,
    verification_status,
    notes
FROM data_sources
WHERE source_name = 'Karachi Bus Network Research Dataset (user-provided cleaned files)';

COMMIT;
