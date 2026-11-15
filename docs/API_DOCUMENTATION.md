# API Documentation

Base path: `/api/v1`.

## Implemented
### GET /health
Checks application and database connectivity.

Optional query:
- `check_db=false`: skip database connectivity check.

Healthy response:
```json
{
  "success": true,
  "data": {
    "application": "healthy",
    "database": "healthy"
  }
}
```

Database failure returns HTTP 503 and `error.code = DATABASE_UNAVAILABLE`.

## Planned public endpoints
- `GET /routes`
- `GET /routes/{id}`
- `GET /routes/{id}/directions`
- `GET /directions/{id}/stops`
- `GET /directions/{id}/shape`
- `GET /stops`
- `GET /stops/{id}`
- `GET /stops/{id}/routes`
- `GET /discover/nearby?lat={lat}&lng={lng}&radius={metres}`
- `GET /discover/journey?origin_lat={lat}&origin_lng={lng}&destination_lat={lat}&destination_lng={lng}`
- `GET /search?q={query}`

## Planned admin endpoints
Admin route, stop, direction, geometry and import endpoints will be added with authentication, role checks, input validation and audit logging in the route-management phase. Do not expose write endpoints before those controls exist.
