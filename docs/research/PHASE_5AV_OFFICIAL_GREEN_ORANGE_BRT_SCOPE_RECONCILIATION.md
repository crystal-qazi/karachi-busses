# Phase 5AV — Official Green/Orange BRT source-scope reconciliation

**Review date:** 2026-11-18  
**Status:** Official source claims compared; no station sequence or station coordinate approved.

## Orange Line — official station-count discrepancy

Three government-level sources do not state the same station scope:

1. The Sindh Transport Department project page reports a **3.88 km** Orange Line corridor and **five bus stations**: [Sindh Transport Department — Orange Line](https://transport.sindh.gov.pk/orange-line).
2. The SMTA project page describes the project alignment and **four BRT stations plus one bus depot**: [SMTA — Abdul Sattar Edhi Line](https://smta.sindh.gov.pk/brt-abdul-sattar-edhi-line-orange-line).
3. The Provincial Assembly answer for 19 May 2026 states the **4 km line is in operation** from TMA Office Orangi Town to Jinnah University for Women near Matriculation Board Office, serving approximately 2,500 passengers daily: [Provincial Assembly of Sindh, Question 520](https://pas.gov.pk/business/questios-details/33/2019).

The 2021 Facility Management Agreement Exhibit 1 names four contract station IDs: OL-1 5 No. Chowrangi; OL-2 Orangi Town Police Station; OL-3 Abdullah College; OL-4 Dilpasand Sweets. This schedule is contractual evidence, not confirmation that the current operating system still uses exactly those four passenger platforms.

### Orange Line decision

- Accept current operation and the government-reported corridor endpoints from the 19 May 2026 Assembly answer.
- Retain the official 5-bus-station and 4-BRT-station claims separately. The count difference may reflect different scopes, but no source presently proves that explanation.
- Retain OL-1 to OL-4 as contract station IDs only.
- Do not create a fifth station name or infer which contract station is omitted/added.
- Do not assign coordinates, station order or geometry until the operator provides a current station register or platform schedule.

## Green Line — current operator sequence remains unresolved

The 2016 Government/PIDCL presentation reports 25 stations but names 29 corridor points. The 2021 SIDCL/PIDCL pre-bid response confirms 25 bus stations but does not provide station names or IDs. PIDCL's operationalization project page marks the Green Line operationalization/ITS project 100% complete in 2024, but it does not publish a current passenger station register.

Two 2026 passenger-facing lists each claim 22 stations but differ in material names and order:
- [BusUpdate list](https://busupdate.com/pakistan/karachi/bus-routes/route-green-line/)
- [CMTA list](https://cmta.com.pk/karachi-green-line-brt-route/)

Neither is an operator-issued station-ID schedule. The 22-stop lists therefore remain independent secondary-source variants, not a resolved operating register. Municipal Park remains an extension endpoint reported for FY 2026–27, not an approved currently operating stop.

The Green and Orange Line operational control handover to the Sindh government was reported on 11 March 2025: [Dawn — operational control transfer](https://www.dawn.com/news/1897123/sindh-takes-over-operational-control-of-brt-green-orange-lines). This supports the current government operator context but does not settle the station list.

### Green Line decision

- Preserve the 25-station government project count and 29 historical corridor points.
- Preserve both 22-stop secondary lists separately.
- Do not select, merge or geocode either 22-stop list.
- Require a current SIDCL/SMTA station-ID schedule or official operational drawing before accepting passenger stop sequence and coordinates.

## Publication gates

No BRT stop was approved, no station coordinate or route geometry was added, and no MySQL/public API data was changed. Existing Phase 5AR findings remain in force; this phase only clarifies the official source-scope discrepancy and the remaining evidence needed.
