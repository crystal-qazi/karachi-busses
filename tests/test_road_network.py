"""Unit tests for the connected-road routing engine (app.road_network).

The engine must produce connected-road *candidates* that respect OSM one-way
restrictions, never bridge disconnected roads, preserve stop order and flag
legs it cannot route instead of fabricating a path.
"""

import json
import math

import pytest
from shapely.geometry import box

from app.road_network import RoadGraph, route_between, route_stops
from app.snapping import load_roads


def _feature(way_id, coords, tags=None):
    return {
        "type": "Feature",
        "id": f"way/{way_id}/1",
        "properties": {"@id": way_id, "tags": tags or {"highway": "residential"}},
        "geometry": {"type": "LineString", "coordinates": coords},
    }


def _write_roads(tmp_path, features):
    path = tmp_path / "roads.geojson"
    path.write_text(json.dumps({
        "type": "FeatureCollection", "features": features,
    }), encoding="utf-8")
    return path


def _graph_from(roads):
    return RoadGraph.from_parts(roads.iter_parts())


def _stop(stop_id, lng, lat, name="stop", sequence=1, status="under_review"):
    return {"id": stop_id, "name": name, "sequence": sequence,
            "lat": lat, "lng": lng, "status": status}


# ~0.001 degrees of longitude at Karachi's latitude is ~101 m; 0.001 degrees
# of latitude is ~111 m. Coordinates below stay around (67.0 E, 24.9 N).
BASE_ROADS = [
    _feature(1, [[67.000, 24.900], [67.005, 24.900], [67.010, 24.900]],
             {"highway": "primary", "name": "East Road"}),
    _feature(2, [[67.010, 24.900], [67.010, 24.910]],
             {"highway": "primary", "name": "North Road"}),
    _feature(3, [[67.010, 24.910], [67.020, 24.910]],
             {"highway": "primary", "name": "Far Road"}),
    _feature(4, [[67.100, 24.900], [67.110, 24.900]],
             {"highway": "one_way_street", "oneway": "yes", "name": "OneWay"}),
    _feature(5, [[67.200, 24.900], [67.210, 24.900]],
             {"highway": "one_way_street", "oneway": "-1", "name": "Backward"}),
    _feature(6, [[67.300, 24.900], [67.310, 24.900]],
             {"highway": "residential", "junction": "roundabout", "name": "Circle"}),
    _feature(7, [[67.500, 25.500], [67.510, 25.500]],
             {"highway": "residential", "name": "Island"}),
]


@pytest.fixture()
def base_roads(tmp_path):
    return _write_roads(tmp_path, BASE_ROADS)


def test_routed_path_follows_road_chain(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    leg = route_between(graph, roads, 24.9000, 67.0000, 24.9100, 67.0100,
                        max_snap_distance_m=150.0)
    assert leg.status == "routed"
    # The path must traverse the *intermediate* node (67.005, 24.900), not
    # jump straight from the snap stub to the far end.
    assert len(leg.geometry) >= 4
    way_ids = [way.osm_way_id for way in leg.ways_used]
    assert way_ids == ["1", "2"]
    assert leg.network_distance_m >= leg.straight_m
    assert leg.geometry[0] == (67.0000, 24.9000)
    assert leg.geometry[-1] == (67.0100, 24.9100)


def test_oneway_yes_blocks_reverse_travel(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    forward = route_between(graph, roads, 24.9000, 67.1000, 24.9000, 67.1100,
                            max_snap_distance_m=150.0)
    assert forward.status == "routed"
    backward = route_between(graph, roads, 24.9000, 67.1100, 24.9000, 67.1000,
                             max_snap_distance_m=150.0)
    assert backward.status == "no_path"
    assert "no_connected_path_within_budget" in backward.flags


def test_oneway_minus_one_blocks_forward_travel(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    forward = route_between(graph, roads, 24.9000, 67.2000, 24.9000, 67.2100,
                            max_snap_distance_m=150.0)
    assert forward.status == "no_path"
    backward = route_between(graph, roads, 24.9000, 67.2100, 24.9000, 67.2000,
                             max_snap_distance_m=150.0)
    assert backward.status == "routed"


def test_roundabout_implies_forward_only(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    forward = route_between(graph, roads, 24.9000, 67.3000, 24.9000, 67.3100,
                            max_snap_distance_m=150.0)
    assert forward.status == "routed"
    backward = route_between(graph, roads, 24.9000, 67.3100, 24.9000, 67.3000,
                             max_snap_distance_m=150.0)
    assert backward.status == "no_path"


def test_disconnected_road_is_never_bridged(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    leg = route_between(graph, roads, 24.9000, 67.0000, 25.5000, 67.5000,
                        max_snap_distance_m=150.0)
    assert leg.status == "no_path"
    # The fallback geometry is the straight line, clearly flagged.
    assert leg.geometry == [(67.0, 24.9), (67.5, 25.5)]


def test_snap_limit_reports_no_snap(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    # Target is ~1.1 km north of any road; the snap limit is 150 m.
    leg = route_between(graph, roads, 24.9000, 67.0000, 24.9110, 67.0050,
                        max_snap_distance_m=150.0)
    assert leg.status == "no_snap"
    assert "to_endpoint_not_snappable" in leg.flags


def test_cost_budget_rejects_oversized_detour(tmp_path):
    roads_file = _write_roads(tmp_path, [
        # Parallel east-west roads ~1.1 km apart (0.01 deg lat), connected
        # only by a long detour far to the east.
        _feature(20, [[67.000, 24.900], [67.010, 24.900]]),
        _feature(21, [[67.000, 24.910], [67.010, 24.910]]),
        _feature(22, [[67.010, 24.900], [67.060, 24.900]]),
        _feature(23, [[67.060, 24.900], [67.060, 24.910]]),
        _feature(24, [[67.060, 24.910], [67.010, 24.910]]),
    ])
    roads = load_roads(roads_file)
    graph = _graph_from(roads)
    # budget = straight * 1.0: any road path is longer than the straight line,
    # so a lawful-but-longer path must be rejected as outside the budget.
    leg = route_between(graph, roads, 24.9000, 67.0000, 24.9100, 67.0000,
                        max_snap_distance_m=150.0,
                        cost_budget_factor=1.0, cost_budget_extra_m=0.0)
    assert leg.status == "no_path"


def test_large_detour_flag_on_lawful_but_long_path(tmp_path):
    roads_file = _write_roads(tmp_path, [
        _feature(30, [[67.000, 24.900], [67.010, 24.900]]),
        _feature(31, [[66.990, 24.905], [67.000, 24.905]]),
        # Only connection runs 505 m east, 555 m north and 1 km back west:
        # the lawful path is ~3.7x the straight line.
        _feature(32, [[67.010, 24.900], [67.015, 24.900], [67.015, 24.905],
                      [67.000, 24.905]]),
    ])
    roads = load_roads(roads_file)
    graph = _graph_from(roads)
    leg = route_between(graph, roads, 24.9000, 67.0000, 24.9050, 67.0000,
                        max_snap_distance_m=150.0)
    assert leg.status == "routed"
    assert "large_detour_vs_straight" in leg.flags


def test_two_stops_on_same_oneway_segment(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    forward = route_between(graph, roads, 24.9000, 67.1000, 24.9000, 67.1050,
                            max_snap_distance_m=150.0)
    assert forward.status == "routed"
    way_ids = [way.osm_way_id for way in forward.ways_used]
    assert way_ids == ["4"]
    backward = route_between(graph, roads, 24.9000, 67.1050, 24.9000, 67.1000,
                             max_snap_distance_m=150.0)
    assert backward.status == "no_path"


def test_identical_stops_are_flagged(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    leg = route_between(graph, roads, 24.9000, 67.0000, 24.9000, 67.0000)
    assert leg.status == "identical_stop"
    assert "zero_length_leg" in leg.flags


def test_route_stops_preserves_stop_order(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    stops = [
        _stop(1, 67.0000, 24.9000, "A", 1),
        _stop(2, 67.0100, 24.9000, "B", 2),
        _stop(3, 67.0100, 24.9100, "C", 3),
        _stop(4, 67.0200, 24.9100, "D", 4),
    ]
    result = route_stops(graph, roads, stops, max_snap_distance_m=150.0)
    assert result["summary"]["status"] == "routed"
    assert result["summary"]["leg_count"] == 3
    assert result["summary"]["problem_legs"] == 0
    legs = result["legs"]
    assert [(leg["from_stop"]["id"], leg["to_stop"]["id"]) for leg in legs] == \
        [(1, 2), (2, 3), (3, 4)]
    # Combined geometry runs A → B → C → D in order; routed legs share their
    # boundary stop coordinate.
    geometry = result["geometry"]
    assert geometry[0] == [67.0000, 24.9000]
    assert geometry[-1] == [67.0200, 24.9100]
    assert [67.0100, 24.9000] in geometry
    assert [67.0100, 24.9100] in geometry


def test_route_stops_summarises_problem_legs(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    stops = [
        _stop(1, 67.0000, 24.9000, "A", 1),
        _stop(2, 67.0100, 24.9000, "B", 2),
        # C sits on the disconnected island road.
        _stop(3, 67.5000, 25.5000, "C", 3),
    ]
    result = route_stops(graph, roads, stops, max_snap_distance_m=150.0)
    assert result["summary"]["status"] == "partial"
    assert result["summary"]["routed_legs"] == 1
    assert result["summary"]["problem_legs"] == 1
    assert result["legs"][1]["status"] == "no_path"
    # Problem legs are never merged into the combined geometry.
    assert result["geometry"][-1] == [67.0100, 24.9000]


def test_snap_proposals_respect_candidate_cap(base_roads):
    roads = load_roads(base_roads)
    graph = _graph_from(roads)
    proposals = graph.snap_proposals(roads, 24.9000, 67.0000,
                                     max_distance_m=150.0, max_candidates=1)
    assert len(proposals) == 1
    assert proposals[0].snap.way_id == "1"


def _distant_pair_length_m(p1, p2):
    lat1, lng1 = p1
    lat2, lng2 = p2
    return math.hypot((lat2 - lat1) * 111_000.0,
                      (lng2 - lng1) * 101_000.0)


def test_routed_connector_geometry_bounds(tmp_path):
    roads_file = _write_roads(tmp_path, [
        _feature(40, [[67.000, 24.900], [67.010, 24.900]]),
    ])
    roads = load_roads(roads_file)
    graph = _graph_from(roads)
    leg = route_between(graph, roads, 24.9002, 67.0005, 24.9001, 67.0095,
                        max_snap_distance_m=150.0)
    assert leg.status == "routed"
    # Connector stubs keep the geometry starting/ending at the stop coords.
    assert leg.geometry[0] == (67.0005, 24.9002)
    assert leg.geometry[-1] == (67.0095, 24.9001)
    # Connector lengths are inside the snap limit.
    assert leg.from_snap.distance_m <= 150.0
    assert leg.to_snap.distance_m <= 150.0
