"""Regression tests for trusted reverse-proxy client IP resolution."""

from app.admin.rate_limit import client_ip


def test_client_ip_uses_rightmost_non_trusted_forwarded_hop(app):
    app.config["TRUSTED_PROXY_IPS"] = ("10.0.0.1", "10.0.0.2")

    with app.test_request_context(
        "/admin/login",
        environ_base={"REMOTE_ADDR": "10.0.0.1"},
        headers={
            "X-Forwarded-For": "198.51.100.99, 203.0.113.42, 10.0.0.2",
        },
    ):
        # The leftmost address may be forged by the client. The trusted
        # proxy appended the real client address before its own proxy hop.
        assert client_ip() == "203.0.113.42"


def test_client_ip_falls_back_to_direct_peer_when_forwarded_chain_is_empty(app):
    app.config["TRUSTED_PROXY_IPS"] = ("10.0.0.1",)

    with app.test_request_context(
        "/admin/login",
        environ_base={"REMOTE_ADDR": "10.0.0.1"},
        headers={"X-Forwarded-For": "10.0.0.1"},
    ):
        assert client_ip() == "10.0.0.1"
