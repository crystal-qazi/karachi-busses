"""Snap a WGS84 coordinate to the nearest OSM road segment (public data only).

This is a pure shapely + pyproj module. It consumes the same candidate-road
GeoJSON inventory produced by ``scripts/extract_osm_karachi_roads.py``, where
each Feature is a ``LineString`` in WGS84 (lon, lat) with ``properties``
carrying ``@id`` and a ``tags`` dict (``highway``, ``name``, ...).

Strict interpretation
---------------------
A snap is a *geometric proximity* result only. It does NOT verify that a bus
serves the road, that the boarding point is on the correct side, or that the
snap coordinate is an operator-approved stop. No database writes and no
network requests are made by this module; the caller is responsible for any
further validation before a snap coordinate is used.

Road lines are loaded in WGS84 and projected to EPSG:32642 (UTM zone 42N) for
planar distance measurement, matching the rest of the research pipeline; snap
coordinates are returned back in WGS84. Data source is © OpenStreetMap
contributors, licensed under the Open Database License 1.0 (ODbL); see docs/
for attribution policy.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform
from shapely.strtree import STRtree

WGS84 = "EPSG:4326"
# UTM zone 42N covers Karachi; the whole research pipeline measures planar
# distance in this CRS to avoid degrees-based distortion.
AREA_CRS = "EPSG:32642"

_transformer_4326_to_32642 = Transformer.from_crs(
    WGS84, AREA_CRS, always_xy=True
)
_transformer_32642_to_4326 = Transformer.from_crs(
    AREA_CRS, WGS84, always_xy=True
)


@dataclass(frozen=True)
class SnapResult:
    """A geometric road-snap candidate.

    ``lat``/``lng`` are the point on the nearest road in WGS84. ``way_id`` is
    the OSM way id (a string, because the source GeoJSON may carry it as an
    int or an ``@id`` that is not purely numeric). ``road_name`` and
    ``highway`` are read from the OSM tags and may be empty when the road is
    unnamed or the tag is absent.

    ``way_geometry`` is the WGS84 ``((lng, lat), ...)`` coordinates of the road
    segment the candidate snapped to — used to highlight the exact road on the
    map. ``way_tags`` carries the relevant OSM tags of that road so the caller
    can display classification and routing details.
    """

    lat: float
    lng: float
    distance_m: float
    road_name: str
    highway: str
    way_id: str
    way_geometry: tuple  # ((lng, lat), ...) in WGS84
    way_tags: dict

    def as_dict(self, include_geometry: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "latitude": self.lat,
            "longitude": self.lng,
            "distance_m": round(self.distance_m, 3),
            "road_name": self.road_name,
            "highway": self.highway,
            "osm_way_id": self.way_id,
            "tags": dict(self.way_tags),
        }
        if include_geometry:
            result["way_geometry"] = [list(c) for c in self.way_geometry]
        return result


class RoadIndex:
    """A spatial index over OSM candidate road segments.

    Build once with :func:`load_roads`, then reuse for many point queries.
    """

    def __init__(self, lines: list, wgs84_lines: list, props: list, feature_count: int) -> None:
        self._lines = lines
        self._wgs84_lines = wgs84_lines
        self._props = props
        self._tree = STRtree(lines)
        self.feature_count = feature_count

    @property
    def is_empty(self) -> bool:
        return self.feature_count == 0

    def _candidate_hits(self, lat: float, lng: float, max_distance_m: float) -> list[tuple[float, int]]:
        """Return ``(distance_m, line_index)`` hits within ``max_distance_m``.

        Both the buffer query and the distance measurement are done in the
        planar CRS (metres). A ``distance <= max_distance_m`` filter is applied
        so the buffer edge does not admit slightly-out-of-range segments.
        """
        source_point = Point(float(lng), float(lat))
        if source_point.is_empty or not source_point.is_valid:
            return []
        point = transform(_transformer_4326_to_32642.transform, source_point)
        candidate_indexes = self._tree.query(point.buffer(max_distance_m))
        hits: list[tuple[float, int]] = []
        for idx in candidate_indexes:
            i = int(idx)
            distance = float(point.distance(self._lines[i]))
            if distance <= max_distance_m:
                hits.append((distance, i))
        return hits

    def _build_result(self, distance: float, i: int, point) -> SnapResult:
        line = self._lines[i]
        p = self._props[i]
        tags = p.get("tags", {}) if isinstance(p, dict) else {}

        # Closest point on the road segment to the projected query point.
        snap_projected = line.interpolate(line.project(point))
        snap_wgs84 = transform(
            _transformer_32642_to_4326.transform, snap_projected
        )
        snap_lng, snap_lat = snap_wgs84.x, snap_wgs84.y

        wgs84_line = self._wgs84_lines[i]
        geometry = tuple((float(round(c[0], 8)), float(round(c[1], 8))) for c in wgs84_line.coords)

        return SnapResult(
            lat=round(float(snap_lat), 8),
            lng=round(float(snap_lng), 8),
            distance_m=distance,
            road_name=str(tags.get("name", "") or ""),
            highway=str(tags.get("highway", "") or ""),
            way_id=str(p.get("@id", "") or ""),
            way_geometry=geometry,
            way_tags=dict(tags),
        )

    def snap(self, lat: float, lng: float, max_distance_m: float) -> SnapResult | None:
        """Return the nearest road segment within ``max_distance_m`` or None."""
        hits = self._candidate_hits(lat, lng, max_distance_m)
        if not hits:
            return None
        source_point = Point(float(lng), float(lat))
        point = transform(_transformer_4326_to_32642.transform, source_point)
        distance, i = min(hits, key=lambda item: item[0])
        return self._build_result(distance, i, point)

    def snap_candidates(
        self,
        lat: float,
        lng: float,
        max_distance_m: float,
        max_candidates: int = 5,
    ) -> list[SnapResult]:
        """Return nearby road segments ordered by distance (nearest first).

        Segments from the same OSM ``way_id`` are collapsed to a single result
        (the closest segment of that way) so that a way split into many
        segments — or overlapping/duplicate copies of the same way — does not
        flood the candidate list. Two *distinct* roads that overlap or cross
        near the point each still appear. Results are capped at
        ``max_candidates``.
        """
        hits = self._candidate_hits(lat, lng, max_distance_m)
        if not hits:
            return []
        source_point = Point(float(lng), float(lat))
        point = transform(_transformer_4326_to_32642.transform, source_point)

        # Deduplicate by OSM way id, keeping the closest segment per way.
        best_per_way: dict[str, tuple[float, int]] = {}
        order: list[str] = []
        for distance, i in sorted(hits, key=lambda item: item[0]):
            way_id = str(self._props[i].get("@id", "") or "")
            if way_id not in best_per_way:
                best_per_way[way_id] = (distance, i)
                order.append(way_id)

        results: list[SnapResult] = []
        for way_id in order[:max_candidates]:
            distance, i = best_per_way[way_id]
            results.append(self._build_result(distance, i, point))
        return results


def _parse_geojson(geojson: str | bytes | dict | Path) -> dict:
    """Return a parsed FeatureCollection dict from path, raw text or dict."""
    if isinstance(geojson, Path):
        geojson = str(geojson)
    if isinstance(geojson, str) and (
        geojson.lstrip().startswith(("{", "[")) or "\n" in geojson
    ):
        # Looks like embedded JSON text.
        return json.loads(geojson)
    if isinstance(geojson, str):
        return json.loads(Path(geojson).read_text(encoding="utf-8"))
    if isinstance(geojson, (bytes, bytearray)):
        return json.loads(bytes(geojson).decode("utf-8"))
    if isinstance(geojson, dict):
        return geojson
    raise TypeError("geojson must be a path, JSON string, bytes, or dict")


def load_roads(geojson: str | bytes | dict | Path) -> RoadIndex:
    """Build a :class:`RoadIndex` from the OSM candidate-road GeoJSON.

    ``geojson`` may be a file path, a raw JSON string, ``bytes``, or an already
    parsed FeatureCollection ``dict``. Invalid / non-line features are skipped;
    if no valid road line remains, an empty :class:`RoadIndex` is returned
    (its ``snap`` always yields ``None``).
    """
    data = _parse_geojson(geojson)
    lines: list = []
    wgs84_lines: list = []
    props: list = []
    for feature in data.get("features", []):
        try:
            geometry = shape(feature.get("geometry"))
        except (KeyError, TypeError, ValueError):
            continue
        feature_props = feature.get("properties", {})
        for part in _line_parts(geometry):
            # Work in the planar CRS (matching the proximity audit) so that
            # planar distance and buffer queries are in metres. Keep the
            # original WGS84 line for reporting the road geometry.
            projected = transform(
                _transformer_4326_to_32642.transform, part
            )
            if projected.is_empty or not projected.is_valid or projected.length <= 0:
                continue
            lines.append(projected)
            wgs84_lines.append(part)
            props.append(feature_props)
    return RoadIndex(lines, wgs84_lines, props, len(lines))


def _line_parts(geometry) -> list:
    """Return the non-empty line sub-geometries of a geometry."""
    if geometry.is_empty:
        return []
    geom_type = geometry.geom_type
    if geom_type == "LineString":
        return [geometry] if geometry.length > 0 else []
    if geom_type == "MultiLineString":
        return [g for g in geometry.geoms if not g.is_empty and g.length > 0]
    if geom_type == "GeometryCollection":
        return [part for child in geometry.geoms for part in _line_parts(child)]
    return []


def nearest_road_snap(
    lat: float,
    lng: float,
    roads: RoadIndex,
    max_distance_m: float,
) -> SnapResult | None:
    """Convenience wrapper: snap ``(lat, lng)`` to the nearest road.

    ``roads`` is a :class:`RoadIndex` from :func:`load_roads`. Returns a
    :class:`SnapResult` when a segment is within ``max_distance_m``, else None.
    """
    return roads.snap(lat, lng, max_distance_m)


def road_snap_candidates(
    lat: float,
    lng: float,
    roads: RoadIndex,
    max_distance_m: float,
    max_candidates: int = 5,
) -> list[SnapResult]:
    """Convenience wrapper: propose several nearby road candidates.

    Delegates to :meth:`RoadIndex.snap_candidates`, returning the candidates
    ordered by distance (nearest first), deduplicated by OSM way id and capped
    at ``max_candidates``.
    """
    return roads.snap_candidates(
        lat, lng, max_distance_m, max_candidates=max_candidates
    )
