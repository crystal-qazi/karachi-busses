"""Timing probe for the cached snap endpoint (Task 4 cold/warm measurements).

Logs in via Selenium (CSRF-protected form), syncs cookies to a requests
session, then times repeated GETs of /admin/historical-network/snap for stops
514 and 515. Read-only; no data changes.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests
from selenium import webdriver
from selenium.webdriver.edge.options import Options

from verify_snap_preview import BASE_URL, login


def make_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,1000")
    return webdriver.Edge(options=options)


def main():
    driver = make_driver()
    session = requests.Session()
    try:
        login(driver, session)
        for stop_id in (514, 515):
            print(f"--- stop {stop_id} ---")
            for i in range(1, 4):
                t0 = time.perf_counter()
                resp = session.get(
                    f"{BASE_URL}/admin/historical-network/snap?stop_id={stop_id}",
                    timeout=180,
                )
                dt = time.perf_counter() - t0
                payload = resp.json() if resp.headers.get("Content-Type", "").startswith("application/json") else None
                if payload and payload.get("success"):
                    snapped = payload.get("snapped") or {}
                    note = (payload.get("note") or {}).get("code", "")
                    print(
                        f"  req{i}: {dt:8.3f}s  candidates={len(payload.get('candidates', []))}"
                        f"  nearest_way={snapped.get('osm_way_id')}"
                        f"  dist={snapped.get('distance_m')}  note={note}"
                    )
                else:
                    print(f"  req{i}: {dt:8.3f}s  status={resp.status_code}  body={resp.text[:160]}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
