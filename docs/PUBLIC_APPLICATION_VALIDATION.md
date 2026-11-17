# Public Application Validation

- **Test date:** 2026-11-17 (local time 2026-11-17 17:45 WAST)
- **Branch:** `fix/radius-refresh-utc-timestamp`
- **Commits tested:**
  - `d74fca2` — *fix(map): refresh nearby results when radius changes*
  - `5d3f567` — *fix(api): generate timezone-aware UTC timestamps*
  - `6772ba4` — *test(api): assert mobile timestamps are timezone-aware*
- **Latest code commit tested:** `6772ba43028e5bf2a160a9abf4d18887ef71fc10`
- **Initial validation report commit:** `87396f1dec8f091a359d18afcb2deaea59edf470`
- **Environment:**
  - Windows 11 / Git Bash / Python 3.11.0
  - Flask 3.0.3, PyMySQL, Leaflet 1.9.4 (CDN), Bootstrap 5.3.3 (CDN)
  - MySQL 8.4.3 @ 127.0.0.1:3306, database `karachi_buses`
  - Browser: Qoder in-app browser (CDP), via `browser-use` and `chrome-devtools` MCP tools
- **Browser:** Headless Chrome via CDP (`visibilityState=hidden`, `window.innerWidth` reported 0 by `browser-use`; true viewport measurements taken via `chrome-devtools.resize_page` and `chrome-devtools.emulate` viewport).

## Automated Test Results

```
$ python -m pytest -q
.........................................................                [100%]
57 passed in 9.27s
```

- **Test count:** 57 passed, 0 failed, 0 skipped.
- **DB check before/after:** identical row counts (bus_routes=98, bus_stops=572, route_directions=98, route_shapes=0, data_sources=4, route_stops=1281). No test modified production or historical records.
- **Import errors:** none.
- **Database migrations:** schema already present in local DB; no migration required during test run.

## GitHub Actions

- Run: `44075124970` — commit `6772ba43028e5bf2a160a9abf4d18887ef71fc10` (HEAD of branch).
- URL: https://github.com/crystal-qazi/karachi-busses/actions/runs/44075124970
- Jobs:
  - `test (Python 3.11)` — success
  - `test (Python 3.12)` — success
  - `container-build` — success

## Browser Testing Results

### A. Initial Page — **PASS**

| Check | Result |
|---|---|
| App loads | 200 OK, title "Karachi Buses — Find your route" |
| Console errors on load | None |
| Leaflet JS + CSS loaded | 200 via unpkg, Leaflet 1.9.4 |
| OSM tiles load | 2 tiles loaded (zoom 11, 256×256), © OSM contributors attribution visible |
| Bootstrap 5.3.3 | 200 via jsdelivr |
| App.css | loaded |

### B. Search — **PASS**

All searches returned gracefully because the local DB contains no `verified` data sources (see "Known Limitations"). Server behaviour confirmed at the API level:

| Query | Expected | Observed |
|---|---|---|
| "Saddar" | 0 routes, 0 stops | 200, success=true, 0/0 |
| "Gulshan" | 0 routes, 0 stops | 200, 0/0 |
| "Clifton" | 0 routes, 0 stops | 200, 0/0 |
| "Korangi" | 0 routes, 0 stops | 200, 0/0 |
| Known route (e.g. "571") | 0/0 | 200, 0/0 |
| "zzzznonexistent" | 0/0 | 200, 0/0 |
| 1-char ("A") | 400 with error message | 400, "Search text must contain at least 2 characters." |
| Empty / whitespace | 400 with error message | 400, same message |

UI behaviour (via DOM dispatch on the real input):

- "Saddar" → status "Search complete. Select a direction to see its mapped path and stops." / results "No matching active routes or stops. Try another search."
- "S" (1-char) → status "Enter at least 2 characters to search." (client-side guard, no API call).
- "" → status "Enter at least 2 characters to search."
- No JS console errors from the UI-driven searches.

### C. Nearby Stops and Radius — **PASS** (with data limitation noted)

| Scenario | Observed |
|---|---|
| GPS granted (simulated `getCurrentPosition` code 0) | status "No nearby active routes found." (discover ran, empty DB) |
| GPS permission denied (code 1) | "Location permission denied. Tap the map to choose your location manually." |
| GPS unavailable (code 2) | "Your location is unavailable. Tap the map to choose your location manually." |
| GPS timeout (code 3) | "Location request timed out. Please try again or tap the map." |
| Manual map-point selection (via a DOM click on `#map`) | user marker added, "No nearby active routes found." |
| Radius change with **no** origin selected | no `discover` call, status unchanged, no JS error |
| Radius change **after** GPS origin | new `/api/v1/discover/nearby?...&radius=<new>` request fired (network capture: radius=3000 → 10000 → 500) |
| Radius change **after** manual map-click origin | new `/api/v1/discover/nearby?...&radius=3000` request fired |
| Empty results | "No active bus stops with published routes were found within this radius. Try a larger radius or search a route." |
| All six radius options (500/1000/1500/3000/5000/10000) | each produces a discover request; results empty (data limitation), no errors |
| No JS console errors | confirmed via `list_console_messages` (only the 400s from my direct probe fetches appeared) |

**Specifically for the radius-refresh feature (commit `d74fca2`):** the listener on `radiusSelect` (app.js:169-172) correctly re-invokes `discover(currentOrigin.lat, currentOrigin.lng)` only when `currentOrigin` is set. Verified with both GPS and manual origins — each radius change produces a fresh `discover/nearby` request at the updated radius.

### D. Route Details — **PASS** (with data limitation noted)

- `showDirection` is called from search / nearby / journey buttons.
- The API endpoint `/api/v1/directions/<id>` returns **404** for ids 1-3 ("Active route direction not found.") because no verified, active directions exist in this DB.
- `showDirection`'s catch block (`setStatus(error.message)`) renders the 404 message gracefully — no uncaught exception.
- The polyline / stop-rendering branch in `showDirection` (app.js:86-106) was verified by **code review** against the shape/stop schema. No browser-level test was possible because no verified active route exists to produce a successful response in this environment.

**Note:** This is an environmental limitation, not a code defect. The route-rendering code path is exercised by unit tests in `tests/test_public_discovery.py` (mocking the DB layer).

### E. Journey Planner — **PASS** (with data limitation noted)

| Scenario | Observed |
|---|---|
| Direct journey (origin=Saddar, destination=Saddar) | 200, `journey_count=0`, message "No active bus stop matches this destination." |
| One-transfer journey (no data to produce it) | same as direct: 0 journeys |
| No matching destination ("zzzznonexistent") | 200, `journey_count=0`, same "No active bus stop matches" message |
| Missing origin (fresh page load) | status "First use GPS or tap the map to select your starting location." |
| Invalid destination (1-char "A") | 400, "Destination must contain 2–100 characters." |
| Empty destination | status "Enter at least 2 characters for the destination stop or area." |
| GPS origin | discover ran, journey returns 0 (data limitation), no errors |
| Manually selected origin | same as GPS |

### F. Responsive Layout — **PASS**

| Device | Resolution | Layout | Horizontal Overflow | Map | Notes |
|---|---|---|---|---|---|
| Desktop | 1366×768 | side-by-side (aside 336px, map 989×587px) | none (scrollWidth=clientWidth=1351) | 587px tall | Map is the right column, full height. |
| Tablet | 768×1024 | stacked (aside 745px above, section 745px below) | none (scrollWidth=clientWidth=753) | 400px tall | Below the 992px breakpoint the `<aside>` stacks above `<section>`. `.map-frame` height rule kicks in: `58vh` (400px of 1024). |
| Mobile | 390×844 | stacked (aside 382px above, section 382px below) | none (scrollWidth=clientWidth=390) | 488px tall | `.map-frame` 58vh = 489px. GPS button 332px wide, search input 260px wide — no clipping. |

No horizontal overflow, no clipping of buttons or inputs, all navigation and search controls remain usable at all three viewports.

## Bugs Discovered

**None.** The three commits being validated contain no reproducible defects:

1. **Radius refresh** (`d74fca2`): the listener correctly guards on `currentOrigin` and re-invokes `discover`. Verified with both GPS and manual origins. No edge-case error when radius is changed without an origin.
2. **UTC timestamp** (`5d3f567`): `datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")` produces a timezone-aware UTC ISO-8601 string. Output observed: `2026-11-17T12:17:00Z`. `datetime.fromisoformat(s.replace("Z", "+00:00")).utcoffset()` returns `0:00:00` on Python 3.11, confirming the "timezone-aware" claim. No other `datetime.utcnow()` usages remain in the codebase.
3. **Timestamp regression test** (`6772ba4`): `assert generated_at.utcoffset() is not None` correctly validates that the parsed timestamp carries UTC offset info. Test passes.

No code changes were required. No regression tests needed to be added beyond the one already committed.

## Files Changed / Fixes Applied

No files modified. No fixes applied. The three commits in scope are correct and verified.

## Known Limitations

1. **No verified data in local DB.** All 4 `data_sources` rows are `verification_status='pending'`, all 572 stops are `under_review`, and `route_shapes` has 0 rows. The route counts reconcile against the committed import documentation: 76 historical-network route identifiers plus 22 SMTA catalogue route identities equals 98 total route rows. The SMTA catalogue marks R5, R6 and R7 inactive; the remaining 19 SMTA routes plus 76 historical routes account for 95 `under_review` routes, alongside 3 inactive routes. The database row count and status summary therefore describe different status groups, not missing routes. This count reconciliation does not verify that any service currently operates. As a result:
   - Search returns 0 routes / 0 stops for every query.
   - Nearby discovery returns 0 stops at every radius.
   - Journey planner returns 0 journeys for every destination.
   - `/api/v1/directions/<id>` returns 404 for every id.
   - Mobile manifest's `dataset_version` is computed on an empty snapshot.

   These are **environmental** constraints (the DB has not yet been verified/published), not code defects. The fix branches do not touch data records (and the task rules forbid activating unverified data).

2. **Screenshots unavailable in this session.** The in-app browser reports `window.innerWidth=0` and `visibilityState=hidden`, so `take_screenshot` and the browser tool's pointer-based `click` returned `NATIVE_BROWSER_VIEWPORT_UNAVAILABLE`. All structural / functional / responsive testing was done via CDP JS evaluation (`evaluate_script`), DOM dispatch, and `chrome-devtools.resize_page` / `emulate`. No visual screenshots were captured.

3. **Route-detail rendering (polyline + ordered stops) was not exercised in a live browser** because no verified route exists to trigger a successful `showDirection` response. The code path was verified by inspection.

## PASS / FAIL / BLOCKED Summary

| Category | Status | Notes |
|---|---|---|
| A. Initial page | PASS | Loads, map/tiles/Bootstrap OK, no errors |
| B. Search | PASS | All cases render gracefully (0 results due to data) |
| C. Nearby stops & radius | PASS | Radius-refresh feature verified with GPS + manual origins |
| D. Route details | PASS* | 404 path handled gracefully; polyline render verified by code inspection only |
| E. Journey planner | PASS* | All error paths verified; positive journey not testable (no data) |
| F. Responsive | PASS | No horizontal overflow at 1366×768, 768×1024, 390×844 |
| Automated tests | PASS | 57/57 pass |
| GitHub Actions | PASS | 3 jobs green on commit 6772ba4 |

\* PASS for "graceful handling / no crashes"; BLOCKED from exercising the positive path due to the DB data limitation described above. The branch code is correct.

## Branch Readiness

The branch is **ready for review and merge** with respect to the code it introduced. The three commits are focused, minimal, and correct:

- The radius-refresh feature (5 lines in `static/js/app.js`) is a clear, guarded addition.
- The timestamp fix (2 lines in `app/api/mobile.py`) is a drop-in replacement of `utcnow()` with `now(timezone.utc)`.
- The regression test (3 lines in `tests/test_mobile_api.py`) pins the behaviour.

No code changes were needed to fix defects. The only thing preventing a "fully green" browser test of the *positive* search/journey/route-detail flows is that the local database has no verified data; that is out of scope for this fix branch and is documented as a known limitation.
