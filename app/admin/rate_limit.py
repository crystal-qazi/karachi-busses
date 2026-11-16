"""IP-based rate limiting for admin logins.

Design notes
------------
- File-backed (JSON, one file per client IP) so it works in single- and
  multi-worker deployments without an external dependency (Redis, Memcached).
  Each state file lives under ``LOGIN_RATE_LIMIT_STATE_DIR`` and is keyed
  on the sanitized client IP.
- Client IP resolution honours ``X-Forwarded-For`` **only** when the direct
  peer address is listed in ``TRUSTED_PROXY_IPS``. Otherwise the IP is taken
  from ``REMOTE_ADDR``. This prevents untrusted proxies from spoofing the
  lockout state.
- On success the counter for that IP is cleared.
- On failure the timestamp is recorded; once the number of failures in the
  trailing window reaches ``LOGIN_RATE_LIMIT_MAX_ATTEMPTS`` the IP is
  locked out for ``LOGIN_RATE_LIMIT_LOCKOUT_SECONDS``.
- Lockout expiry is enforced lazily: a request after the lockout has expired
  starts a fresh sliding window.
"""

import json
import os
import time
from collections import deque
from pathlib import Path
from typing import Deque, Optional

from flask import current_app, request


def _state_dir() -> Path:
    cfg = current_app.config.get("LOGIN_RATE_LIMIT_STATE_DIR")
    if not cfg:
        cfg = "data/rate_limits"
    path = Path(cfg)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _trusted_proxy_ips() -> tuple:
    return tuple(current_app.config.get("TRUSTED_PROXY_IPS") or ())


def _sanitize_ip(ip: str) -> str:
    """Return a filesystem-safe key for the given IP. IPv6-mapped IPv4 is
    normalized; anything non-IP-like is hashed to a stable 16-char digest.
    """
    import hashlib

    ip = (ip or "").strip()
    # Only allow alnum, dots, colons and hyphens. Anything else → hash.
    if ip and all(ch.isalnum() or ch in {".", ":", "-"} for ch in ip):
        return ip.replace(":", "_")
    return hashlib.sha256(ip.encode("utf-8", "replace")).hexdigest()[:16]


def client_ip() -> str:
    """Resolve the client IP, honouring X-Forwarded-For only from trusted proxies."""
    peer = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    direct = request.remote_addr or "0.0.0.0"
    trusted = _trusted_proxy_ips()
    if direct in trusted and peer:
        return peer
    return direct


def _state_file(ip: str) -> Path:
    return _state_dir() / f"{_sanitize_ip(ip)}.json"


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {"failures": deque(), "locked_until": 0.0}
    try:
        raw = json.loads(path.read_text("utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"failures": deque(), "locked_until": 0.0}
    failures = deque()
    # Rebuild the deque from a JSON list; keep only the trailing window.
    window = int(current_app.config.get("LOGIN_RATE_LIMIT_WINDOW_SECONDS", 300))
    cutoff = time.time() - window
    for ts in raw.get("failures", []):
        if ts >= cutoff:
            failures.append(float(ts))
    return {"failures": failures, "locked_until": float(raw.get("locked_until", 0.0))}


def _save_state(path: Path, state: dict) -> None:
    payload = {"failures": list(state["failures"]), "locked_until": state["locked_until"]}
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload), "utf-8")
    tmp.replace(path)


def is_locked(ip: Optional[str] = None) -> bool:
    """Return True when the given IP (or the current request's IP) is locked out.

    A lockout expires when ``locked_until`` is in the past. On expiry the
    state file is pruned so the next failure starts a fresh window.
    """
    if ip is None:
        ip = client_ip()
    path = _state_file(ip)
    state = _load_state(path)
    now = time.time()
    if state["locked_until"] > now:
        return True
    # Expired: drop the lockout and stale failure timestamps.
    state["locked_until"] = 0.0
    window = int(current_app.config.get("LOGIN_RATE_LIMIT_WINDOW_SECONDS", 300))
    cutoff = now - window
    state["failures"] = deque(ts for ts in state["failures"] if ts >= cutoff)
    _save_state(path, state)
    return False


def record_failure(ip: Optional[str] = None) -> bool:
    """Record one failed attempt. Returns True when the IP has just reached
    the lockout threshold.
    """
    if ip is None:
        ip = client_ip()
    path = _state_file(ip)
    state = _load_state(path)
    state["failures"].append(time.time())
    max_attempts = int(current_app.config.get("LOGIN_RATE_LIMIT_MAX_ATTEMPTS", 5))
    lockout = int(current_app.config.get("LOGIN_RATE_LIMIT_LOCKOUT_SECONDS", 300))
    if len(state["failures"]) >= max_attempts:
        state["locked_until"] = time.time() + lockout
        state["failures"].clear()
        _save_state(path, state)
        return True
    _save_state(path, state)
    return False


def record_success(ip: Optional[str] = None) -> None:
    """Clear the failure counter for the given IP."""
    if ip is None:
        ip = client_ip()
    path = _state_file(ip)
    state = _load_state(path)
    state["failures"].clear()
    state["locked_until"] = 0.0
    _save_state(path, state)


def reset_state(ip: str) -> None:
    """Remove the on-disk state file for the given IP. Used by tests."""
    path = _state_file(ip)
    if path.exists():
        path.unlink()
