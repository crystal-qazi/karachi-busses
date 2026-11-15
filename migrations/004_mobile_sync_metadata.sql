-- Metadata for the published mobile dataset.
-- The initial mobile API uses content-addressed full snapshots. Do not add
-- incremental cursors until admin publication mutations write durable events.
CREATE TABLE IF NOT EXISTS mobile_dataset_metadata (
    id TINYINT UNSIGNED NOT NULL,
    schema_version INT UNSIGNED NOT NULL DEFAULT 1,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT chk_mobile_dataset_singleton CHECK (id = 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO mobile_dataset_metadata (id, schema_version)
VALUES (1, 1)
ON DUPLICATE KEY UPDATE schema_version = VALUES(schema_version);
