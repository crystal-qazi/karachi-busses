-- Karachi Buses initial schema (MySQL 8+).
-- The database itself must be created before running this migration.

CREATE TABLE IF NOT EXISTS data_sources (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    source_name VARCHAR(180) NOT NULL,
    source_url VARCHAR(1000) NULL,
    notes TEXT NULL,
    verification_status ENUM('unverified', 'pending', 'verified', 'rejected') NOT NULL DEFAULT 'unverified',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_data_sources_status (verification_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS bus_operators (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(180) NOT NULL,
    contact VARCHAR(120) NULL,
    website VARCHAR(500) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_bus_operators_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS route_categories (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_route_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS bus_routes (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    operator_id BIGINT UNSIGNED NULL,
    source_id BIGINT UNSIGNED NULL,
    route_code VARCHAR(60) NOT NULL,
    route_name VARCHAR(180) NOT NULL,
    description TEXT NULL,
    status ENUM('draft', 'active', 'inactive', 'under_review') NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_bus_routes_operator_code (operator_id, route_code),
    KEY idx_bus_routes_status (status),
    KEY idx_bus_routes_name (route_name),
    CONSTRAINT fk_bus_routes_operator FOREIGN KEY (operator_id) REFERENCES bus_operators(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_bus_routes_source FOREIGN KEY (source_id) REFERENCES data_sources(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS route_category_map (
    route_id BIGINT UNSIGNED NOT NULL,
    category_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (route_id, category_id),
    CONSTRAINT fk_route_category_route FOREIGN KEY (route_id) REFERENCES bus_routes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_route_category_category FOREIGN KEY (category_id) REFERENCES route_categories(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS route_directions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    route_id BIGINT UNSIGNED NOT NULL,
    direction_name VARCHAR(100) NOT NULL,
    start_label VARCHAR(180) NULL,
    end_label VARCHAR(180) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_route_direction_name (route_id, direction_name),
    CONSTRAINT fk_route_directions_route FOREIGN KEY (route_id) REFERENCES bus_routes(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS bus_stops (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    stop_name VARCHAR(180) NOT NULL,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    address VARCHAR(500) NULL,
    status ENUM('active', 'inactive', 'under_review') NOT NULL DEFAULT 'under_review',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_bus_stops_lat_lng (latitude, longitude),
    KEY idx_bus_stops_name (stop_name),
    CONSTRAINT chk_bus_stops_latitude CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT chk_bus_stops_longitude CHECK (longitude BETWEEN -180 AND 180)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS route_stops (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    direction_id BIGINT UNSIGNED NOT NULL,
    stop_id BIGINT UNSIGNED NOT NULL,
    stop_sequence INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_direction_stop_sequence (direction_id, stop_sequence),
    UNIQUE KEY uq_direction_stop (direction_id, stop_id),
    KEY idx_route_stops_stop (stop_id),
    CONSTRAINT fk_route_stops_direction FOREIGN KEY (direction_id) REFERENCES route_directions(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_route_stops_stop FOREIGN KEY (stop_id) REFERENCES bus_stops(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS route_shapes (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    direction_id BIGINT UNSIGNED NOT NULL,
    geojson JSON NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_route_shapes_direction (direction_id),
    CONSTRAINT fk_route_shapes_direction FOREIGN KEY (direction_id) REFERENCES route_directions(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS admin_users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    username VARCHAR(80) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('super_admin', 'route_manager', 'data_reviewer') NOT NULL DEFAULT 'route_manager',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_admin_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    admin_user_id BIGINT UNSIGNED NULL,
    action VARCHAR(80) NOT NULL,
    entity_type VARCHAR(80) NOT NULL,
    entity_id BIGINT UNSIGNED NULL,
    details JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_audit_logs_entity (entity_type, entity_id),
    KEY idx_audit_logs_created (created_at),
    CONSTRAINT fk_audit_logs_admin FOREIGN KEY (admin_user_id) REFERENCES admin_users(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
