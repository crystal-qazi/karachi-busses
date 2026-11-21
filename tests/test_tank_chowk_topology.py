"""Topology tests for the Tank Chowk junction against the real OSM extract.

Uses the committed fixture ``tests/fixtures/tank-chowk-roads.geojson`` — the
road parts intersecting the junction area (focus ways + 800 m pad) extracted
from ``data/osm_roads/karachi-osm-bus-roads.geojson``. The fixture pins the
audit findings (scripts/audit_tank_chowk_junction.py) so routing regressions
around the junction are caught without the full-city inventory.
"""

import json
from pathlib import Path

import pytest

from app.road_network import RoadGraph, route_between
from app.snapping import load_roads

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tank-chowk-roads.geojson"

# The five ways that meet at Tank Chowk (stops 514/515 area).
TRUNK_NORTHBOUND = "522535777"   # trunk carriageway through the junction
JINNAH_EAST = "850584014"        # Jinnah Avenue carriageway (secondary)
TRUNK_LINK_RAMP = "545406459"    # trunk_link ramp at the junction
JINNAH_WEST = "883797721"        # opposite Jinnah Avenue carriageway
TRUNK_SOUTHBOUND = "522375908"   # opposite trunk carriageway
FOCUS_WAYS = [
    TRUNK_NORTHBOUND, JINNAH_EAST, TRUNK_LINK_RAMP, JINNAH_WEST, TRUNK_SOUTHBOUND,
]

# Stops from the historical source around the junction (read-only evidence).
STOP_523 = (24.9268502, 67.1615432)  # Malir Cantt Gate 5
STOP_524 = (24.9131060, 67.1985774)  # Malir Cantt Gate 6
STOP_515 = (24.9125582, 67.1859867)  # Tank Chowk


@pytest.fixture(scope="module")
def roads():
    return load_roads(FIXTURE)


@pytest.fixture(scope="module")
def graph(roads):
    return RoadGraph.from_parts(roads.iter_parts())


def _way_nodes(graph, way_id):
    nodes = set()
    for seq in graph.way_parts.get(way_id, []):
        nodes.update(seq)
    return nodes


def test_fixture_contains_all_five_focus_ways(graph):
    for way_id in FOCUS_WAYS:
        assert graph.way_ref_by_id(way_id) is not None, f"way {way_id} missing"


def test_focus_ways_are_oneway(graph):
    for way_id in FOCUS_WAYS:
        way = graph.ways[graph.way_ref_by_id(way_id)]
        assert way.forward_only, f"way {way_id} should be forward_only (oneway)"
        assert not way.backward_only


def test_junction_triangle_shares_nodes(graph):
    """Trunk, Jinnah Avenue and the ramp form the connected junction triangle."""
    triangle = [TRUNK_NORTHBOUND, JINNAH_EAST, TRUNK_LINK_RAMP]
    for i, a in enumerate(triangle):
        for b in triangle[i + 1:]:
            shared = _way_nodes(graph, a) & _way_nodes(graph, b)
            assert shared, f"ways {a} and {b} share no node"


def test_opposite_carriageways_share_no_nodes_with_triangle(graph):
    """The dual-carriageway opposite sides do not touch the junction triangle
    by coordinate equality inside the audit area (they connect elsewhere)."""
    triangle_nodes = (
        _way_nodes(graph, TRUNK_NORTHBOUND)
        | _way_nodes(graph, JINNAH_EAST)
        | _way_nodes(graph, TRUNK_LINK_RAMP))
    assert not (_way_nodes(graph, TRUNK_SOUTHBOUND) & triangle_nodes)
    assert not (_way_nodes(graph, JINNAH_WEST) & triangle_nodes)


def test_junction_triangle_is_reachable_from_east_carriageway(roads, graph):
    """A stop at Tank Chowk reaches the Malir Cantt Gate 6 side over
    connected roads (the corridor path crosses the junction, not empty
    space) with one-way rules respected."""
    lat, lng = STOP_515
    lat2, lng2 = STOP_524
    leg = route_between(graph, roads, lat, lng, lat2, lng2,
                        max_snap_distance_m=150.0)
    assert leg.status == "routed"
    assert "oneway_restrictions_respected" in leg.flags


def test_corridor_approach_routes_through_junction(roads, graph):
    """EV-2 approach legs (523→524→515) route with one-way rules respected."""
    legs = []
    for (lat1, lng1), (lat2, lng2) in [
        (STOP_523, STOP_524), (STOP_524, STOP_515),
    ]:
        legs.append(route_between(graph, roads, lat1, lng1, lat2, lng2,
                                  max_snap_distance_m=150.0))
    assert all(leg.status == "routed" for leg in legs)
    # Tank Chowk sits on Jinnah Avenue / trunk ways flagged one-way.
    way_ids = {way.osm_way_id for leg in legs for way in leg.ways_used}
    assert TRUNK_NORTHBOUND in way_ids or JINNAH_EAST in way_ids
    assert any("oneway_restrictions_respected" in leg.flags for leg in legs)
