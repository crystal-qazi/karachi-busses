from scripts.audit_phase5bb_pakbus_greenline_to_572_nodes import (
    build_crosswalk,
    haversine_m,
)


def test_pakbus_greenline_crosswalk_has_22_candidate_stops():
    rows = build_crosswalk()
    assert len(rows) == 22
    assert rows[0]["nearest_historical_node"] == "kda_stop"
    assert rows[-1]["nearest_historical_node"] == "numaish"


def test_pakbus_greenline_crosswalk_is_candidate_only():
    rows = build_crosswalk()
    assert all(
        row["decision"] == "candidate_only_no_alias_or_coordinate_change"
        for row in rows
    )


def test_haversine_distance_is_in_metres():
    distance = haversine_m(0.0, 0.0, 0.0, 1.0)
    assert 111_000 < distance < 112_000
