-- Preserve source edge lists without forcing branching networks into a false linear stop order.
CREATE TABLE IF NOT EXISTS route_segments (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    direction_id BIGINT UNSIGNED NOT NULL,
    from_stop_id BIGINT UNSIGNED NOT NULL,
    to_stop_id BIGINT UNSIGNED NOT NULL,
    segment_sequence INT UNSIGNED NOT NULL,
    source_id BIGINT UNSIGNED NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_route_segment_sequence (direction_id, segment_sequence),
    KEY idx_route_segments_from_stop (from_stop_id),
    KEY idx_route_segments_to_stop (to_stop_id),
    CONSTRAINT fk_route_segments_direction FOREIGN KEY (direction_id) REFERENCES route_directions(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_route_segments_from_stop FOREIGN KEY (from_stop_id) REFERENCES bus_stops(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_route_segments_to_stop FOREIGN KEY (to_stop_id) REFERENCES bus_stops(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_route_segments_source FOREIGN KEY (source_id) REFERENCES data_sources(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
