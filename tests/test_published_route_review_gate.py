"""Regression tests for withdrawing edited published routes from public discovery."""

from app.admin import routes as admin_routes


class FakeCursor:
    def __init__(self, rowcount):
        self.rowcount = rowcount
        self.calls = []

    def execute(self, query, params=None):
        self.calls.append((query, params))


def test_structural_edit_demotes_active_route_and_records_audit(monkeypatch):
    cursor = FakeCursor(rowcount=1)
    audits = []
    monkeypatch.setattr(
        admin_routes,
        "_audit",
        lambda cursor_arg, action, entity_type, entity_id, details=None:
            audits.append((action, entity_type, entity_id, details)),
    )

    admin_routes._mark_route_under_review(cursor, 42, "route_geometry_changed")

    assert cursor.calls == [(
        "UPDATE bus_routes SET status='under_review' WHERE id=%s AND status='active'",
        (42,),
    )]
    assert audits == [(
        "unpublish_for_review",
        "bus_route",
        42,
        {"reason": "route_geometry_changed"},
    )]


def test_structural_edit_does_not_change_route_that_is_not_active(monkeypatch):
    cursor = FakeCursor(rowcount=0)
    audits = []
    monkeypatch.setattr(
        admin_routes,
        "_audit",
        lambda *args, **kwargs: audits.append((args, kwargs)),
    )

    admin_routes._mark_route_under_review(cursor, 42, "direction_stop_added")

    assert len(cursor.calls) == 1
    assert audits == []
