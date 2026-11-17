# Phase 5X — Spelling Alias Candidate Shortlist

## Purpose

Make the most obvious name-normalization candidates easier to inspect without treating them as verified stops. This shortlist is a filtered subset of the Phase 5W name-only register.

## Summary

- 20 route-stop occurrences.
- 13 distinct source-name to historical-node-name pairs.
- Each score is 1.0000 after the Phase 5W normalization and explicit spelling-alias rules.
- Every row remains `unverified`.

## Candidate pairs

| Published/crosswalk stop name | Historical node candidate |
|---|---|
| Khokharapar 04 | `khokrapar_no_4` |
| Suadabad | `saudabad` |
| Sorab Goth | `sohrab_goth` |
| Five Star Chowrangi | `5_star_chowrangi` |
| Guru Mandar | `gurumandir` |
| Kemari | `keamari` |
| Mera Naka | `mira_naka` |
| Punjabi Chowrangi | `punjab_chowrangi` |
| Qaidabad | `quaidabad` |
| Maripur | `mauripur` |
| Domba Goth | `damba_goth` |
| Mosamiyat | `mosmayat` |
| Millennium Mall | `millenium_mall` |

## Important limitation

A score of 1.0000 means only that the strings become identical under the documented text normalization/alias rules. It does **not** prove that the historical coordinate represents the current passenger stop, that the boarding side is correct, or that the route still serves that point. No coordinates are included or assigned. Do not modify the source crosswalk or approve routes from this shortlist alone.

Before accepting a candidate, compare the route-specific stop with operator evidence and confirm its physical boarding point/side. OSM road proximity is a separate supporting check, not proof of a passenger stop.
