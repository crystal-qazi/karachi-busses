-- Route codes are globally unique, including routes without an operator.
ALTER TABLE bus_routes ADD UNIQUE KEY uq_bus_routes_route_code (route_code);
