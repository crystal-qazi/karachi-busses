"""Road-network topology and routing over the extracted OSM road inventory.

Builds a directed node/edge graph from the same candidate-road GeoJSON that
:mod:`app.snapping` indexes, then finds connected paths between stop
coordinates while respecting OSM one-way restrictions.

Strict interpretation
---------------------
A routed path is a *connected-road candidate*, not proof of the historical bus
alignment. Stops are attached to the network through short geometric connector
stubs (reported separately); a leg that cannot be connected — because the
roads are genuinely disconnected, a connector exceeds the snap limit, or the
cheapest path would violate a one-way — is reported as a problem and never
replaced by a fabricated road path. Nothing in this module writes to the
database; callers decide what to do with the preview.

Graph construction
------------------
Nodes are unique rounded WGS84 coordinates (OSM shared junction nodes appear
at identical coordinates in every way that references them, so coordinate
equality is a reliable shared-node signal for the exported GeoJSON). Each
consecutive coordinate pair of a way becomes an edge measured in the planar
CRS (EPSG:32642, metres). Direction follows the OSM tagging: ``oneway=yes``,
``oneway=1``/``true`` and roundabout/circular junctions are forward-only
along the way's coordinate order; ``oneway=-1`` is backward-only; everything
else is bidirectional.

Stop attachment
---------------
A stop is snapped to the nearest road parts via the shared RoadIndex. Each
snap position splits its containing segment into a temporary node for the
duration of one leg search, with edges that obey the way's direction rules —
so a connector never travels against a one-way and a path can leave or enter
the road exactly at the stop's snapped position.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Any, Iterable

from app.snapping import RoadIndex, SnapResult, project_wgs84

FORWARD_ONLY_ONEWAY = {"yes", "1", "true"}
IMPLICIT_ONEWAY_JUNCTION = {"roundabout", "circular"}


@dataclass(frozen=True)
class WayInfo:
    """Identity and direction rules of one OSM way inside the graph."""

    osm_way_id: str
    name: str
    highway: str
    forward_only: bool
    backward_only: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "osm_way_id": self.osm_way_id,
            "name": self.name,
            "highway": self.highway,
            "forward_only": self.forward_only,
            "backward_only": self.backward_only,
        }


@dataclass
class LegResult:
    """Outcome of routing one ordered stop pair.

    ``status`` is one of ``routed`` (connected road path found),
    ``no_snap`` (at least one endpoint has no road within the snap limit),
    ``no_path`` (both endpoints snapped but the network offers no connected
    path within the cost budget), ``identical_stop`` (zero-length leg) or
    ``missing_coordinates`` (a stop coordinate is absent or invalid).

    ``geometry`` is a ``[(lng, lat), ...]`` polyline. For ``routed`` legs it
    runs stop → snapped point → road nodes → snapped point → stop; for
    problem legs it is the straight stop-to-stop line so a map can show the
    problematic connection visibly.
    """

    status: str
    geometry: list[tuple[float, float]] = field(default_factory=list)
    network_distance_m: float | None = None
    straight_m: float | None = None
    from_snap: SnapResult | None = None
    to_snap: SnapResult | None = None
    ways_used: list[WayInfo] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    from_stop: dict[str, Any] | None = None
    to_stop: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "geometry": [[lng, lat] for lng, lat in self.geometry],
            "network_distance_m": (
                round(self.network_distance_m, 2)
                if self.network_distance_m is not None else None),
            "straight_m": (
                round(self.straight_m, 2) if self.straight_m is not None else None),
            "from_snap": (
                self.from_snap.as_dict(include_geometry=False)
                if self.from_snap else None),
            "to_snap": (
                self.to_snap.as_dict(include_geometry=False)
                if self.to_snap else None),
            "ways_used": [way.as_dict() for way in self.ways_used],
            "flags": list(self.flags),
            "from_stop": dict(self.from_stop) if self.from_stop else None,
            "to_stop": dict(self.to_stop) if self.to_stop else None,
        }


@dataclass(frozen=True)
class SnapProposal:
    """One candidate place where a stop could join the road graph.

    The snap position lies on the graph segment ``(node_a, node_b)`` of the
    OSM way; ``offset_a``/``offset_b`` are the along-segment distances from
    the snap position to each bracketing node.
    """

    snap: SnapResult
    way: WayInfo
    way_ref: int
    node_a: int
    node_b: int
    offset_a: float
    offset_b: float

    @property
    def connector_m(self) -> float:
        """Distance from the stop coordinate to the snapped road position."""
        return self.snap.distance_m


class RoadGraph:
    """Directed graph over OSM road parts (nodes = shared coordinates).

    Build one with :meth:`from_parts` — typically feeding it
    :meth:`app.snapping.RoadIndex.parts_intersecting` results restricted to
    the area of interest — and route with :func:`route_between`.
    """

    def __init__(self) -> None:
        self.node_coords: list[tuple[float, float]] = []   # node -> (lng, lat)
        self.node_proj: list[tuple[float, float]] = []     # node -> (x, y) planar
        self.node_index: dict[tuple[float, float], int] = {}
        self.adjacency: dict[int, list[tuple[int, float, int]]] = {}
        self.ways: list[WayInfo] = []
        self._way_refs: dict[tuple, int] = {}
        self._way_refs_by_id: dict[str, int] = {}
        # OSM way id -> node-id sequences, one per geometry part of that way.
        self.way_parts: dict[str, list[list[int]]] = {}
        self.edge_count = 0

    # -- construction ----------------------------------------------------

    @classmethod
    def from_parts(cls, parts: Iterable[tuple]) -> "RoadGraph":
        """Build a graph from ``(wgs84_line, projected_line, props)`` parts.

        Parts come from ``RoadIndex.parts_intersecting`` /
        ``RoadIndex.iter_parts``. Parts with fewer than two coordinates or
        mismatched coordinate arrays are skipped.
        """
        graph = cls()
        for wgs84_line, projected_line, props in parts:
            coords = list(wgs84_line.coords)
            pcoords = list(projected_line.coords)
            if len(coords) < 2 or len(coords) != len(pcoords):
                continue
            tags = props.get("tags", {}) if isinstance(props, dict) else {}
            way = graph._way_info(props, tags)
            node_ids: list[int] = []
            for (lng, lat), (x, y) in zip(coords, pcoords):
                node_ids.append(graph._node(lng, lat, x, y))
            graph.way_parts.setdefault(way.osm_way_id, []).append(node_ids)
            for a, b, (x1, y1), (x2, y2) in zip(
                node_ids, node_ids[1:], pcoords, pcoords[1:]
            ):
                length = math.dist((x1, y1), (x2, y2))
                if length <= 0:
                    continue
                way_ref = graph._way_ref(way)
                if not way.backward_only:
                    graph.adjacency[a].append((b, length, way_ref))
                if not way.forward_only:
                    graph.adjacency[b].append((a, length, way_ref))
                graph.edge_count += 1
        return graph

    def _node(self, lng: float, lat: float, x: float, y: float) -> int:
        key = (round(lat, 8), round(lng, 8))
        node = self.node_index.get(key)
        if node is None:
            node = len(self.node_coords)
            self.node_index[key] = node
            self.node_coords.append((lng, lat))
            self.node_proj.append((x, y))
            self.adjacency[node] = []
        return node

    def _way_info(self, props: dict, tags: dict) -> WayInfo:
        oneway = str(tags.get("oneway", "") or "").strip().lower()
        junction = str(tags.get("junction", "") or "").strip().lower()
        forward_only = (
            oneway in FORWARD_ONLY_ONEWAY or junction in IMPLICIT_ONEWAY_JUNCTION)
        return WayInfo(
            osm_way_id=str(props.get("@id", "") or "") or "unknown",
            name=str(tags.get("name", "") or ""),
            highway=str(tags.get("highway", "") or ""),
            forward_only=forward_only,
            backward_only=(oneway == "-1"),
        )

    def _way_ref(self, way: WayInfo) -> int:
        key = (way.osm_way_id, way.name, way.highway,
               way.forward_only, way.backward_only)
        ref = self._way_refs.get(key)
        if ref is None:
            ref = len(self.ways)
            self._way_refs[key] = ref
            self.ways.append(way)
            self._way_refs_by_id.setdefault(way.osm_way_id, ref)
        return ref

    def way_ref_by_id(self, osm_way_id: str) -> int | None:
        """Return the graph way reference for an OSM way id, if present."""
        return self._way_refs_by_id.get(osm_way_id)

    # -- stop attachment -------------------------------------------------

    def snap_proposals(
        self,
        roads: RoadIndex,
        lat: float,
        lng: float,
        max_distance_m: float,
        max_candidates: int = 5,
    ) -> list[SnapProposal]:
        """Find candidate places where a stop coordinate joins this graph.

        Uses the shared :class:`~app.snapping.RoadIndex` to find nearby road
        parts (capped by ``max_candidates`` ways), then locates the containing
        segment of this graph for each snapped position. Proposals are sorted
        by total connector distance (stop → road → nearest bracketing node).
        """
        proposals: list[SnapProposal] = []
        seen_segments: set[tuple[str, int, int]] = set()
        for candidate in roads.snap_candidates(
            lat, lng, max_distance_m=max_distance_m, max_candidates=max_candidates
        ):
            located = self._locate_on_way(candidate)
            if located is None:
                continue
            proposal = located
            key = (candidate.way_id, proposal.node_a, proposal.node_b)
            if key in seen_segments:
                continue
            seen_segments.add(key)
            proposals.append(proposal)
        proposals.sort(key=lambda p: p.connector_m + min(p.offset_a, p.offset_b))
        return proposals

    def _locate_on_way(self, candidate: SnapResult) -> SnapProposal | None:
        """Build a :class:`SnapProposal` for a snap position on one OSM way."""
        parts = self.way_parts.get(candidate.way_id)
        if not parts:
            return None
        way_ref = self.way_ref_by_id(candidate.way_id)
        if way_ref is None:
            return None
        way = self.ways[way_ref]
        snap_x, snap_y = project_wgs84(candidate.lng, candidate.lat)
        best: tuple[float, int, int] | None = None
        for node_ids in parts:
            for a, b in zip(node_ids, node_ids[1:]):
                ax, ay = self.node_proj[a]
                bx, by = self.node_proj[b]
                distance = _point_segment_distance(snap_x, snap_y, ax, ay, bx, by)
                if best is None or distance < best[0]:
                    best = (distance, a, b)
        if best is None:
            return None
        _, node_a, node_b = best
        ax, ay = self.node_proj[node_a]
        bx, by = self.node_proj[node_b]
        return SnapProposal(
            snap=candidate,
            way=way,
            way_ref=way_ref,
            node_a=node_a,
            node_b=node_b,
            offset_a=math.hypot(snap_x - ax, snap_y - ay),
            offset_b=math.hypot(snap_x - bx, snap_y - by),
        )


def _point_segment_distance(px, py, ax, ay, bx, by) -> float:
    """Planar distance from point P to segment AB."""
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab_len_sq = abx * abx + aby * aby
    if ab_len_sq <= 0:
        return math.hypot(apx, apy)
    t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab_len_sq))
    cx, cy = ax + t * abx, ay + t * aby
    return math.hypot(px - cx, py - cy)


# -- leg search ----------------------------------------------------------

@dataclass
class _LegOverlay:
    """Per-leg edge overlay that splits snapped segments at stop positions.

    Temporary nodes (negative ids) sit at each snap position. Edges honour
    the way's one-way rules: on a forward-only way the temp node only
    receives from upstream and only departs downstream. Several snaps on the
    same segment additionally get temp-to-temp edges covering the
    sub-segment between them, so two stops on one one-way street can follow
    the road in its permitted direction.
    """

    graph: RoadGraph
    adjacency: dict[int, list[tuple[int, float, int]]] = field(default_factory=dict)
    temp_positions: dict[int, tuple[float, float]] = field(default_factory=dict)

    def edges(self, node: int) -> list[tuple[int, float, int]]:
        edges = self.adjacency.get(node)
        if edges is None:
            edges = list(self.graph.adjacency.get(node, ()))
            self.adjacency[node] = edges
        return edges

    def add_edge(self, u: int, v: int, cost: float, way_ref: int) -> None:
        self.edges(u).append((v, cost, way_ref))

    def node_position(self, node: int) -> tuple[float, float]:
        if node < 0:
            return self.temp_positions[node]
        return self.graph.node_coords[node]


def _build_overlay(
    graph: RoadGraph,
    from_proposals: list[SnapProposal],
    to_proposals: list[SnapProposal],
) -> tuple[_LegOverlay, list[tuple[int, float]], dict[int, float], dict[int, SnapProposal], dict[int, SnapProposal]]:
    """Create the leg overlay: temp split nodes, stub costs and edges."""
    overlay = _LegOverlay(graph)
    sources: list[tuple[int, float]] = []
    targets: dict[int, float] = {}
    from_meta: dict[int, SnapProposal] = {}
    to_meta: dict[int, SnapProposal] = {}
    created: dict[tuple[str, int, int], int] = {}
    segment_temps: dict[tuple[int, int], list[tuple[float, int, SnapProposal]]] = {}

    def temp_for(proposal: SnapProposal) -> int:
        # Snap positions on the same segment stay distinct: merging them
        # would invent a free zero-length move that ignores one-way rules.
        key = (proposal.snap.way_id, proposal.node_a, proposal.node_b,
               round(proposal.snap.lng, 6), round(proposal.snap.lat, 6))
        temp = created.get(key)
        if temp is None:
            temp = -len(created) - 1
            created[key] = temp
            overlay.temp_positions[temp] = (proposal.snap.lng, proposal.snap.lat)
            way = proposal.way
            way_ref = proposal.way_ref
            oa, ob = proposal.offset_a, proposal.offset_b
            # Edges between the temp node and the segment ends follow the
            # way's direction rules.
            if not way.backward_only:
                overlay.add_edge(proposal.node_a, temp, oa, way_ref)
                overlay.add_edge(temp, proposal.node_b, ob, way_ref)
            if not way.forward_only:
                overlay.add_edge(proposal.node_b, temp, ob, way_ref)
                overlay.add_edge(temp, proposal.node_a, oa, way_ref)
            segment_temps.setdefault(
                (proposal.node_a, proposal.node_b), []).append(
                (oa, temp, proposal))
        return temp

    for proposal in from_proposals:
        temp = temp_for(proposal)
        sources.append((temp, proposal.connector_m))
        from_meta[temp] = proposal
    for proposal in to_proposals:
        temp = temp_for(proposal)
        targets[temp] = proposal.connector_m
        to_meta[temp] = proposal

    # Sub-segment edges between multiple snaps of one segment.
    for (node_a, node_b), temps in segment_temps.items():
        if len(temps) < 2:
            continue
        temps.sort(key=lambda item: item[0])
        way = temps[0][2].way
        way_ref = temps[0][2].way_ref
        for (oa_i, temp_i, _), (oa_j, temp_j, _) in zip(temps, temps[1:]):
            sub_length = oa_j - oa_i
            if sub_length <= 0:
                continue
            if not way.backward_only:
                overlay.add_edge(temp_i, temp_j, sub_length, way_ref)
            if not way.forward_only:
                overlay.add_edge(temp_j, temp_i, sub_length, way_ref)
    return overlay, sources, targets, from_meta, to_meta


def _dijkstra(
    overlay: _LegOverlay,
    sources: list[tuple[int, float]],
    targets: dict[int, float],
    budget_m: float,
) -> tuple[float, list[int], list[int], int, int] | None:
    """Cheapest path from any source node to any target node.

    Node lookups go through ``overlay.edges`` so the base graph's adjacency
    is lazily materialised as the search reaches it — the overlay dict alone
    only contains nodes touched by temp-edge construction, and routing must
    traverse the whole subgraph.

    ``sources`` carries ``(node, initial_cost)`` entries (the stop stub);
    ``targets`` maps ``node -> final_cost`` (the other stop stub). Search
    abandons nodes beyond ``budget_m``. Returns ``(total_cost, node_path,
    way_refs, source_node, target_node)`` or None when no target is
    reachable within the budget.
    """
    best_start: dict[int, float] = {}
    heap: list[tuple[float, int]] = []
    for node, cost in sources:
        if cost > budget_m:
            continue
        if cost < best_start.get(node, math.inf):
            best_start[node] = cost
            heapq.heappush(heap, (cost, node))
    dist: dict[int, float] = dict(best_start)
    parent: dict[int, tuple[int, int]] = {}  # node -> (prev_node, way_ref)
    best_total: float | None = None
    best_target: int | None = None
    while heap:
        cost, node = heapq.heappop(heap)
        if cost > dist.get(node, math.inf):
            continue
        if node in targets:
            total = cost + targets[node]
            if best_total is None or total < best_total:
                best_total = total
                best_target = node
        if best_total is not None and cost >= best_total:
            break
        for nbr, length, way_ref in overlay.edges(node):
            ncost = cost + length
            if ncost > budget_m:
                continue
            if ncost < dist.get(nbr, math.inf):
                dist[nbr] = ncost
                parent[nbr] = (node, way_ref)
                heapq.heappush(heap, (ncost, nbr))
    if best_target is None:
        return None
    nodes = [best_target]
    way_refs: list[int] = []
    while nodes[-1] not in best_start:
        prev_node, way_ref = parent[nodes[-1]]
        nodes.append(prev_node)
        way_refs.append(way_ref)
    nodes.reverse()
    way_refs.reverse()
    source_node = nodes[0]
    return best_total, nodes, way_refs, source_node, best_target


def _straight_distance_m(lat1, lng1, lat2, lng2) -> float:
    x1, y1 = project_wgs84(lng1, lat1)
    x2, y2 = project_wgs84(lng2, lat2)
    return math.hypot(x2 - x1, y2 - y1)


def route_between(
    graph: RoadGraph,
    roads: RoadIndex,
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float,
    max_snap_distance_m: float = 150.0,
    cost_budget_factor: float = 3.0,
    cost_budget_extra_m: float = 2500.0,
) -> LegResult:
    """Find a connected road path between two stop coordinates.

    Both endpoints are snapped to the network (within ``max_snap_distance_m``);
    the cheapest path that respects one-way restrictions is searched within a
    cost budget derived from the straight-line distance. Returns a
    :class:`LegResult`; problem legs carry the straight stop-to-stop geometry
    so callers can display the problematic connection without implying that a
    road path exists.
    """
    straight = _straight_distance_m(lat1, lng1, lat2, lng2)
    if straight < 0.5:
        return LegResult(
            status="identical_stop",
            geometry=[(lng1, lat1)],
            network_distance_m=0.0,
            straight_m=straight,
            flags=["zero_length_leg"],
        )
    budget = straight * cost_budget_factor + cost_budget_extra_m
    from_proposals = graph.snap_proposals(
        roads, lat1, lng1, max_distance_m=max_snap_distance_m)
    to_proposals = graph.snap_proposals(
        roads, lat2, lng2, max_distance_m=max_snap_distance_m)
    if not from_proposals or not to_proposals:
        missing = "from" if not from_proposals else "to"
        return LegResult(
            status="no_snap",
            geometry=[(lng1, lat1), (lng2, lat2)],
            straight_m=straight,
            from_snap=from_proposals[0].snap if from_proposals else None,
            to_snap=to_proposals[0].snap if to_proposals else None,
            flags=[f"{missing}_endpoint_not_snappable"],
        )

    overlay, sources, targets, from_meta, to_meta = _build_overlay(
        graph, from_proposals, to_proposals)
    found = _dijkstra(overlay, sources, targets, budget_m=budget)
    if found is None:
        return LegResult(
            status="no_path",
            geometry=[(lng1, lat1), (lng2, lat2)],
            straight_m=straight,
            from_snap=from_proposals[0].snap,
            to_snap=to_proposals[0].snap,
            flags=["no_connected_path_within_budget"],
        )

    total, nodes, way_refs, source_node, target_node = found
    first_snap = from_meta[source_node].snap
    last_snap = to_meta[target_node].snap

    # Geometry: stop 1 → snapped point 1 → road nodes → snapped point 2 → stop 2.
    geometry: list[tuple[float, float]] = [(lng1, lat1)]
    for node in nodes:
        geometry.append(overlay.node_position(node))
    geometry.append((lng2, lat2))
    geometry = _dedupe_consecutive(geometry)

    ways_used: list[WayInfo] = []
    seen_ways: set[int] = set()
    for ref in way_refs:
        if ref in seen_ways:
            continue
        seen_ways.add(ref)
        ways_used.append(graph.ways[ref])
    # Attachment ways complete the picture when the path stays inside
    # connector stubs (both stops snapped onto the same road segment).
    for proposal in (from_meta[source_node], to_meta[target_node]):
        ref = proposal.way_ref
        if ref in seen_ways:
            continue
        seen_ways.add(ref)
        ways_used.append(graph.ways[ref])

    flags: list[str] = []
    if any(way.forward_only or way.backward_only for way in ways_used):
        flags.append("oneway_restrictions_respected")
    if not way_refs and first_snap.way_id == last_snap.way_id:
        flags.append("same_segment")
    # A lawful path can still be a review signal: when the connected path is
    # many times longer than the straight line, either the stop coordinates
    # or the assumed alignment deserve QA attention.
    if straight >= 500.0 and total >= 3.0 * straight:
        flags.append("large_detour_vs_straight")
    return LegResult(
        status="routed",
        geometry=geometry,
        network_distance_m=total,
        straight_m=straight,
        from_snap=first_snap,
        to_snap=last_snap,
        ways_used=ways_used,
        flags=flags,
    )


def _dedupe_consecutive(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    result: list[tuple[float, float]] = []
    for point in points:
        if not result or (round(point[0], 8), round(point[1], 8)) != (
            round(result[-1][0], 8), round(result[-1][1], 8)
        ):
            result.append(point)
    return result


def route_stops(
    graph: RoadGraph,
    roads: RoadIndex,
    stops: list[dict[str, Any]],
    max_snap_distance_m: float = 150.0,
    cost_budget_factor: float = 3.0,
    cost_budget_extra_m: float = 2500.0,
) -> dict[str, Any]:
    """Route an ordered stop sequence, preserving order and flagging gaps.

    ``stops`` is a list of ``{"id", "name", "sequence", "lat", "lng", "status"}``
    dicts in travel order. Consecutive pairs become legs routed with
    :func:`route_between`. Returns ``{"legs": [...], "summary": {...},
    "geometry": [...]}`` where the summary status is ``routed`` (all legs
    connected), ``partial`` (some legs) or ``no_path`` (no leg connected).
    The combined polyline of routed legs is ``geometry`` — problem legs are
    never bridged into it.
    """
    legs: list[dict[str, Any]] = []
    combined: list[tuple[float, float]] = []
    problem_legs = 0
    routed_legs = 0
    for index, stop in enumerate(stops[:-1]):
        nxt = stops[index + 1]
        leg = route_between(
            graph, roads,
            stop["lat"], stop["lng"], nxt["lat"], nxt["lng"],
            max_snap_distance_m=max_snap_distance_m,
            cost_budget_factor=cost_budget_factor,
            cost_budget_extra_m=cost_budget_extra_m,
        )
        leg.from_stop = {"id": stop["id"], "name": stop["name"],
                         "sequence": stop["sequence"]}
        leg.to_stop = {"id": nxt["id"], "name": nxt["name"],
                       "sequence": nxt["sequence"]}
        legs.append(leg.as_dict())
        if leg.status == "routed":
            routed_legs += 1
            segment = leg.geometry
            if combined and combined[-1] == segment[0]:
                combined.extend(segment[1:])
            else:
                combined.extend(segment)
        else:
            problem_legs += 1
    if not legs:
        summary_status = "no_stops"
    elif problem_legs == 0:
        summary_status = "routed"
    elif routed_legs == 0:
        summary_status = "no_path"
    else:
        summary_status = "partial"
    return {
        "legs": legs,
        "summary": {
            "status": summary_status,
            "leg_count": len(legs),
            "routed_legs": routed_legs,
            "problem_legs": problem_legs,
        },
        "geometry": [[lng, lat] for lng, lat in combined],
    }
