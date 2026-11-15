-- Phase 5: preserve provenance and who verified each source record.
ALTER TABLE bus_stops
    ADD COLUMN source_id BIGINT UNSIGNED NULL AFTER address,
    ADD KEY idx_bus_stops_source (source_id),
    ADD CONSTRAINT fk_bus_stops_source
        FOREIGN KEY (source_id) REFERENCES data_sources(id)
        ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE data_sources
    ADD COLUMN verified_by BIGINT UNSIGNED NULL AFTER verification_status,
    ADD COLUMN verified_at DATETIME NULL AFTER verified_by,
    ADD CONSTRAINT fk_data_sources_verified_by
        FOREIGN KEY (verified_by) REFERENCES admin_users(id)
        ON DELETE SET NULL ON UPDATE CASCADE;
