"""
Browser-based visual verification of the OSM road snap preview.

Logs in as admin, opens the historical network map, runs snap previews for
stops 514 and 515, inspects all five candidates for each stop, collects
console errors and network failures, tests edge cases (invalid stop ID,
repeated candidate re-selection), and confirms the preview is read-only.

All screenshots are written to artifacts/snap-verification/.
"""
import json
import os
import sys
import time
import urllib.parse
from pathlib import Path

import requests
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts" / "snap-verification"
ART.mkdir(parents=True, exist_ok=True)

BASE_URL = "http://127.0.0.1:5000"
ADMIN_USER = "admin"
ADMIN_PASS = "Karachi@1234567"

from mysql.connector import connect as db_connect
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "database": os.environ.get("DB_NAME", "karachi_buses"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "root"),
}


def snapshot_db():
    conn = db_connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, stop_name, latitude, longitude, status, source_id "
        "FROM bus_stops WHERE id IN (514, 515)"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def snapshot_audit_logs(count=20):
    conn = db_connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT %s", (count,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def install_js_monitors(driver):
    monitor = """
    (() => {
        window.__consoleErrors = [];
        window.__failedRequests = [];

        const origError = console.error;
        console.error = function(...args) {
            window.__consoleErrors.push(args.map(a =>
                typeof a === 'object' ? JSON.stringify(a).substring(0, 200) : String(a)
            ).join(' '));
            origError.apply(console, args);
        };

        const origWarn = console.warn;
        console.warn = function(...args) {
            window.__consoleErrors.push('[WARN] ' + args.map(a =>
                typeof a === 'object' ? JSON.stringify(a).substring(0, 200) : String(a)
            ).join(' '));
            origWarn.apply(console, args);
        };

        const origFetch = window.fetch;
        window.fetch = function(...args) {
            const url = typeof args[0] === 'string' ? args[0] : args[0].url;
            const method = (args[1] && args[1].method) || 'GET';
            return origFetch.apply(window, args).then(
                response => {
                    if (response.status >= 400) {
                        window.__failedRequests.push({ url: url, method: method, status: response.status });
                    }
                    return response;
                },
                error => {
                    window.__failedRequests.push({ url: url, method: method, status: 'network_error', detail: String(error) });
                    throw error;
                }
            );
        };

        const origOpen = XMLHttpRequest.prototype.open;
        const origSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.open = function(method, url, ...rest) {
            this._track = { method, url };
            return origOpen.call(this, method, url, ...rest);
        };
        XMLHttpRequest.prototype.send = function(...args) {
            const xhr = this;
            xhr.addEventListener('error', function() {
                window.__failedRequests.push({
                    url: xhr._track.url, method: xhr._track.method,
                    status: 'xhr_error', detail: xhr.statusText
                });
            });
            xhr.addEventListener('load', function() {
                if (xhr.status >= 400) {
                    window.__failedRequests.push({
                        url: xhr._track.url, method: xhr._track.method,
                        status: xhr.status, detail: xhr.statusText
                    });
                }
            });
            return origSend.apply(xhr, args);
        };
    })();
    """
    driver.execute_script(monitor)


def wait_for_condition(driver, condition_fn, timeout=15, desc="condition"):
    start = time.time()
    while time.time() - start < timeout:
        try:
            if condition_fn():
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def screenshot(driver, filename):
    path = ART / filename
    driver.save_screenshot(str(path))
    print(f"  Screenshot: {filename}")
    return str(path)


def login(driver, session):
    print("[login] Navigating to /admin/login ...")
    driver.get(f"{BASE_URL}/admin/login?next={urllib.parse.quote('/admin/', safe='')}")
    time.sleep(2)

    if "login" not in driver.current_url.lower():
        print(f"[login] Already logged in: {driver.current_url}")
        for cookie in driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain", "127.0.0.1"))
        return True

    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    username_field.clear()
    username_field.send_keys(ADMIN_USER)
    password_field.clear()
    password_field.send_keys(ADMIN_PASS)

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button.btn-success, button[type=submit]")
    submit_btn.click()

    success = wait_for_condition(
        driver,
        lambda: (
            "/admin/" in driver.current_url
            and "login" not in driver.current_url.lower()
        ),
        timeout=20,
        desc="redirect away from login"
    )
    if not success:
        print(f"[login] FAILED - still at: {driver.current_url}")
        screenshot(driver, "login_failed.png")
        return False

    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain", "127.0.0.1"))

    print(f"[login] Success. Now at: {driver.current_url}")
    time.sleep(1)
    screenshot(driver, "01_login_success.png")
    return True


def open_historical_network(driver):
    print("[historical-network] Navigating to /admin/historical-network ...")
    driver.get(f"{BASE_URL}/admin/historical-network")
    time.sleep(1)
    install_js_monitors(driver)

    wait_for_condition(
        driver,
        lambda: driver.execute_script(
            "return document.getElementById('historical-map') && "
            "document.getElementById('map-message') && "
            "!document.getElementById('map-message').classList.contains('text-danger')"
        ),
        timeout=30,
        desc="historical network data loaded"
    )
    time.sleep(2)
    screenshot(driver, "02_historical_network_loaded.png")


def fetch_snap_api(session, stop_id):
    try:
        resp = session.get(f"{BASE_URL}/admin/historical-network/snap", params={"stop_id": stop_id}, timeout=30)
        return resp.json()
    except Exception as e:
        print(f"  API fetch error for stop {stop_id}: {e}")
        return {"success": False, "error": {"message": str(e)}}


def run_snap_preview(driver, session, stop_id, tag="", reload=False):
    print(f"[snap:{stop_id}] Starting snap preview ...")
    result = {
        "stop_id": stop_id,
        "success": False,
        "candidates": [],
        "snapped": None,
        "status_message": "",
        "error_message": "",
        "screenshots": [],
        "console_errors": [],
        "failed_requests": [],
    }

    if reload:
        # Reload to reset closure state (snapPreviewInFlight, etc.)
        print(f"  Reloading page to reset UI state ...")
        driver.get(f"{BASE_URL}/admin/historical-network")
        time.sleep(2)
        install_js_monitors(driver)
        wait_for_condition(
            driver,
            lambda: driver.execute_script(
                "return document.getElementById('historical-map') && "
                "document.getElementById('map-message') && "
                "!document.getElementById('map-message').classList.contains('text-danger')"
            ),
            timeout=30,
            desc="map data reloaded"
        )
        time.sleep(1)

    # Clear stop ID field and enter new ID
    stop_input = driver.find_element(By.ID, "snap-stop-id")
    stop_input.clear()
    stop_input.send_keys(str(stop_id))
    time.sleep(0.3)

    # Click preview button
    driver.find_element(By.ID, "snap-preview-btn").click()

    # Wait for candidate selector to populate
    success = wait_for_condition(
        driver,
        lambda: driver.execute_script(
            "return document.getElementById('snap-candidate').options.length > 1;"
        ),
        timeout=30,
        desc=f"candidates loaded for stop {stop_id}"
    )
    time.sleep(1)

    msg_el = driver.find_element(By.ID, "map-message")
    result["status_message"] = msg_el.text

    candidate_select = driver.find_element(By.ID, "snap-candidate")
    options = candidate_select.find_elements(By.TAG_NAME, "option")
    n_candidates = len(options) - 1
    result["candidate_count"] = n_candidates
    print(f"  Candidate selector: {n_candidates} candidates")
    for i, opt in enumerate(options):
        opt_text = opt.text.encode('ascii', 'replace').decode('ascii')
        print(f"    option[{i}]: '{opt_text}'")

    payload = fetch_snap_api(session, stop_id)
    if payload.get("success"):
        result["success"] = True
        result["candidates"] = payload.get("candidates", [])
        result["snapped"] = payload.get("snapped")
        result["note"] = payload.get("note")
        print(f"  API: {len(result['candidates'])} candidates, note={result.get('note', {}).get('code', '')}")
    else:
        result["api_error"] = payload.get("error", payload.get("note"))
        print(f"  API error: {result['api_error']}")

    result["console_errors"] = driver.execute_script("return window.__consoleErrors || [];")
    result["failed_requests"] = driver.execute_script("return window.__failedRequests || [];")

    result["screenshots"].append(screenshot(driver, f"{tag}_stop_{stop_id}_cand_0.png"))

    for idx in range(1, n_candidates):
        driver.execute_script("""
            const sel = document.getElementById('snap-candidate');
            sel.value = arguments[0];
            sel.dispatchEvent(new Event('change', { bubbles: true }));
        """, str(idx))
        time.sleep(0.8)
        result["screenshots"].append(screenshot(driver, f"{tag}_stop_{stop_id}_cand_{idx}.png"))

    driver.execute_script("""
        const sel = document.getElementById('snap-candidate');
        sel.value = '0';
        sel.dispatchEvent(new Event('change', { bubbles: true }));
    """)
    time.sleep(0.5)
    result["screenshots"].append(screenshot(driver, f"{tag}_stop_{stop_id}_reselect.png"))

    if result["candidates"]:
        print(f"  Candidates for stop {stop_id}:")
        for i, c in enumerate(result["candidates"]):
            road_name = c.get('road_name') or '(unnamed)'
            print(f"    #{i+1} way={c.get('osm_way_id')} road={road_name} "
                  f"dist={c.get('distance_m')}m highway={c.get('highway')}")

    return result


def test_invalid_stop_id(driver, session):
    print("[invalid-id] Testing invalid stop IDs ...")
    results = {}

    # Reload to ensure clean state
    driver.get(f"{BASE_URL}/admin/historical-network")
    time.sleep(2)
    install_js_monitors(driver)
    wait_for_condition(
        driver,
        lambda: driver.execute_script(
            "return document.getElementById('historical-map') && "
            "document.getElementById('map-message')"
        ),
        timeout=30,
        desc="map reloaded for edge case tests"
    )
    time.sleep(1)

    # Non-numeric stop ID via DOM manipulation (input type=number rejects text)
    driver.execute_script("""
        const input = document.getElementById('snap-stop-id');
        input.type = 'text';
        input.value = 'abc';
        input.dispatchEvent(new Event('input', { bubbles: true }));
        document.getElementById('snap-preview-btn').click();
    """)
    time.sleep(1.5)
    msg = driver.find_element(By.ID, "map-message").text
    print(f"  'abc' -> '{msg}'")
    results["abc"] = msg
    screenshot(driver, "invalid_abc.png")

    # Restore input type
    driver.execute_script("document.getElementById('snap-stop-id').type = 'number';")

    # Non-existent stop ID
    stop_input = driver.find_element(By.ID, "snap-stop-id")
    stop_input.clear()
    stop_input.send_keys("99999")
    time.sleep(0.3)
    driver.find_element(By.ID, "snap-preview-btn").click()
    time.sleep(3)
    msg2 = driver.find_element(By.ID, "map-message").text
    print(f"  '99999' -> '{msg2}'")
    results["99999"] = msg2
    screenshot(driver, "invalid_99999.png")

    payload = fetch_snap_api(session, 99999)
    print(f"  API stop 99999: success={payload.get('success')} error={payload.get('error')}")
    results["99999_api"] = payload

    payload0 = fetch_snap_api(session, 0)
    print(f"  API stop 0: success={payload0.get('success')} error={payload0.get('error')}")
    results["0_api"] = payload0

    return results


def test_no_coordinate_stop(driver, session):
    print("[no-coords] Testing a stop without usable coordinates ...")
    conn = db_connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, stop_name, latitude, longitude, status
        FROM bus_stops WHERE source_id=4
        AND (latitude IS NULL OR longitude IS NULL OR latitude=0 OR longitude=0)
        LIMIT 1
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        print("  No stop found with NULL/zero coordinates in historical source.")
        return {"found": False, "message": "No NULL/zero-coord stop found in source"}

    print(f"  Found stop {row['id']} ({row['stop_name']}). Testing ...")
    # Reload for clean state
    driver.get(f"{BASE_URL}/admin/historical-network")
    time.sleep(2)
    install_js_monitors(driver)
    wait_for_condition(
        driver,
        lambda: driver.execute_script(
            "return document.getElementById('historical-map') && "
            "document.getElementById('map-message')"
        ),
        timeout=30,
        desc="map reloaded for no-coords test"
    )
    time.sleep(1)

    stop_input = driver.find_element(By.ID, "snap-stop-id")
    stop_input.clear()
    stop_input.send_keys(str(row["id"]))
    time.sleep(0.3)
    driver.find_element(By.ID, "snap-preview-btn").click()
    time.sleep(3)
    msg = driver.find_element(By.ID, "map-message").text
    print(f"  Message: '{msg}'")
    screenshot(driver, f"stop_{row['id']}_no_coords.png")

    payload = fetch_snap_api(session, row["id"])
    print(f"  API: success={payload.get('success')} error={payload.get('error')}")
    return {"found": True, "stop_id": row["id"], "message": msg, "api": payload}


def main():
    print("=" * 60)
    print("Starting snap preview browser verification")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)

    print("\n[db] Taking pre-test DB snapshot ...")
    db_before = snapshot_db()
    for row in db_before:
        print(f"  stop {row['id']}: {row['stop_name']} lat={row['latitude']} "
              f"lng={row['longitude']} status={row['status']}")
    audit_before = snapshot_audit_logs(10)
    print(f"  audit_logs latest: {len(audit_before)} rows")

    print("\n[browser] Launching Edge WebDriver ...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Edge(options=options)
    driver.set_page_load_timeout(45)
    session = requests.Session()

    try:
        if not login(driver, session):
            print("\n[FAIL] Could not log in. Aborting.")
            sys.exit(1)

        open_historical_network(driver)

        print("\n" + "=" * 60)
        results = {}

        print("\n[stop 514] C.M.H. Malir Cantt")
        results["514"] = run_snap_preview(driver, session, 514, tag="514")

        print("\n[stop 515] Tank Chowk")
        results["515"] = run_snap_preview(driver, session, 515, tag="515", reload=True)

        print("\n[edge cases] Testing invalid and special cases ...")
        results["invalid"] = test_invalid_stop_id(driver, session)
        results["no_coords"] = test_no_coordinate_stop(driver, session)

        all_console = driver.execute_script("return window.__consoleErrors || [];")
        all_failed = driver.execute_script("return window.__failedRequests || [];")
        results["all_console_errors"] = all_console
        results["all_failed_requests"] = all_failed
        print(f"\n[console] {len(all_console)} console errors, {len(all_failed)} failed requests")
        if all_console:
            for e in all_console[:10]:
                print(f"  CONSOLE: {e[:120]}")
        if all_failed:
            for r in all_failed[:10]:
                print(f"  FAILED: {r}")

        print("\n[db] Taking post-test DB snapshot ...")
        db_after = snapshot_db()
        audit_after = snapshot_audit_logs(10)

        print("\n[read-only check]")
        changed = []
        for before, after in zip(db_before, db_after):
            for key in ("stop_name", "latitude", "longitude", "status"):
                if before[key] != after[key]:
                    changed.append(f"stop {before['id']}.{key}: {before[key]!r} -> {after[key]!r}")
        if changed:
            print("  WARNING: DB records changed during test!")
            for c in changed:
                print(f"    {c}")
        else:
            print("  OK: No DB records for stops 514/515 were modified.")

        new_audits = [a for a in audit_after if a not in audit_before]
        if new_audits:
            print(f"  audit_logs new entries: {len(new_audits)}")
            for a in new_audits[:5]:
                print(f"    action={a.get('action')} entity={a.get('entity_type')}:{a.get('entity_id')}")
        else:
            print("  No new audit_logs entries (as expected for read-only snap).")

        summary_path = ART / "verification_summary.json"
        summary = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "stops_tested": [514, 515],
            "results": {str(k): v for k, v in results.items()},
            "db_before": db_before,
            "db_after": db_after,
            "db_changed": changed,
            "read_only_confirmed": len(changed) == 0,
            "new_audit_entries": new_audits,
        }
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\n[output] Summary written to: {summary_path}")

        print("\n" + "=" * 60)
        print("VERIFICATION REPORT")
        print("=" * 60)
        for stop_id in ["514", "515"]:
            r = results.get(stop_id, {})
            print(f"\nStop {stop_id}: api_success={r.get('success')}, "
                  f"candidates={r.get('candidate_count', 0)}, "
                  f"ui_msg='{r.get('status_message', '')[:80]}'")
            if r.get("candidates"):
                for i, c in enumerate(r["candidates"]):
                    print(f"  #{i+1} way={c.get('osm_way_id')} "
                          f"road={c.get('road_name') or '(unnamed)'} "
                          f"dist={c.get('distance_m')}m "
                          f"highway={c.get('highway')}")
            if r.get("console_errors"):
                print(f"  Console errors: {r['console_errors'][:3]}")
            if r.get("failed_requests"):
                print(f"  Failed requests: {r['failed_requests'][:3]}")

        inv = results.get("invalid", {})
        print(f"\nInvalid ID tests:")
        for k, v in inv.items():
            print(f"  {k}: {json.dumps(v, default=str)[:200]}")

        print(f"\nRead-only: DB unchanged={not changed}")
        print("=" * 60)

    finally:
        driver.quit()
        print("\n[browser] WebDriver session closed.")


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    main()
