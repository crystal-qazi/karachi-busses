# Phase 5AD — Remaining Unmatched Stop Triage

## Purpose

Prioritize the residual Phase 5AA unmatched stop-name queue for manual research without assigning any historical node or coordinate.

## Reproducible workflow

The GitHub Actions workflow rebuilds Phase 5W name candidates, rebuilds the Phase 5AA residual queue from the current crosswalk and the 13 user-confirmed alias pairs, then builds this triage register. It does not rely on stale downloaded artifacts.

## Triage rules

- Strong: top text score >= 0.85
- Possible: 0.65 <= top text score < 0.85
- Weak: 0.45 <= top text score < 0.65
- Low: top text score < 0.45
- Multiple close candidates: at least two candidates score >= 0.45 and the top-two score gap is <= 0.05
- A leading candidate remains a text candidate only; independent operator or field evidence is required.

## Outputs

- `data/research/PHASE_5AD_UNMATCHED_STOP_TRIAGE.csv`
- `data/research/PHASE_5AD_UNMATCHED_STOP_TRIAGE_REPORT.json`

The workflow uploads these as a 30-day GitHub Actions artifact.

## Safety and limitations

No node is selected or assigned. No coordinates are copied. All physical stops remain `unverified`, coordinate assignments remain `not_assigned`, and routes remain `not_approved`. No geocoding, road snapping, route geometry, or production database writes are performed. OSM remains the primary geographic source when later geographic verification is warranted.
