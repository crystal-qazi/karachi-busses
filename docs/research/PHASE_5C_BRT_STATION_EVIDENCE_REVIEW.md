# Phase 5C — Green and Orange Line station evidence reconciliation

**Review date:** 19 November 2026  
**Scope:** Reconcile the new station-list comparison with the existing Phase 5AR and Phase 5BA government-source reviews. This is a source register, not operator confirmation, field verification, owner approval, or publication approval.

## Decision summary

- **Green Line:** The 2012 JICA feasibility report's detailed table lists 29 historical design IDs, while its narrative says 18 existing stations plus four additional stations (22). The 2016 PIDCL progress presentation separately states 25 stations and lists 29 corridor points; a 2021 SIDCL response confirms the 25-station project count. Two 2026 passenger-facing secondary lists each claim 22 operating stops and materially disagree. The FY2025–26 Sindh Budget White Paper says Green Line operations transferred to SMTA and reports 60,000 daily riders in May 2025, but supplies no current station-ID register. Keep all source versions distinct; no complete current station sequence is approved.
- **Orange Line:** A 19 May 2026 Provincial Assembly answer reports the service operating between TMA Office Orangi Town and Jinnah University for Women near Matriculation Board Office. The 2021 facility agreement lists four contract station IDs (OL-1 to OL-4); SMTA project text says four BRT stations plus one depot, while a Sindh Transport Department page reports five bus stations. A secondary list of four names also exists but does not map cleanly to the contract IDs. The current passenger station count, names and order still need operator confirmation.
- **No data changes:** No station records, route sequences, stop coordinates, route shapes, activation states, verification statuses or public API data were changed.

## Green Line — source reconciliation

### Government / project evidence

1. **SIDCL response to pre-bid queries, 19 March 2021:** confirms a Green Line project count of 25 bus stations. It confirms the count, not the current passenger station-ID schedule.
   - https://pidcl.com.pk/wp-content/uploads/2021/03/2021-03-19-Response-Document-Final-Version-.pdf

2. **PIDCL Green Line progress presentation, 16 August 2016:** states 25 stations but separately prints 29 named corridor points. The 29 entries must not be treated as 29 passenger stations.
   - https://pidcl.com.pk/wp-content/uploads/2016/08/Updated-Progress-Presentation-Green-Line-16-8-16.pdf

3. **Government of Sindh / PIDCL operational context:** government material describes the approximately 22–22.5 km Surjani-to-central-Karachi corridor; PIDCL records the infrastructure phase as complete in 2022 and a separate 4 km operationalisation/ITS phase as complete in 2024. The FY2025–26 Budget White Paper reports Green Line ridership of about 60,000 passengers/day in May 2025. These support an operating corridor, not the current ordered station list.
   - https://www.sindh.gov.pk/mega-project/the-greenline-brt-government-of-sindh
   - https://pidcl.com.pk/
   - https://www.finance.gos.pk/Home/Download?path=Budget%2FBudgetBooks%2FFY-25-26%2FBUDGET+WHITE+PAPER+2025-26.pdf

4. **SMTA current route-map index:** includes Green Line but does not provide a complete ordered station-ID list in its accessible route-index text.
   - https://smta.gos.pk/route-map

5. **Green Line extension:** Dawn reported on 18 October 2026 that the Numaish-to-Municipal Park extension was expected to complete during FY2026–27. This is a project forecast, not evidence that Municipal Park is already an operating passenger terminal.
   - https://www.dawn.com/news/2037938/karachis-green-line-extension-to-be-completed-in-fy27-assures-governor



### 2012 JICA feasibility design — ordered station IDs (historical, not as-built)

The JICA/Karachi Metropolitan Corporation *Karachi Transportation Improvement Project Final Report, Volume 2 (Feasibility Study)*, December 2012, contains a detailed Green Line design table (Table 3-2-2, pages 3-7/3-8) with 29 ordered design entries. The table begins at Municipal Park and runs north to the KESC Power House terminal:

| Design ID | Location in JICA Table 3-2-2 |
|---|---|
| M1 | Municipal Park |
| M2 | Radio Pakistan |
| M3 | Garden Square |
| M4 | Taj Medical Complex |
| M5 | KGA Ground |
| G01 | West of Quaid-e-Azam |
| G02 | Gurumandir |
| G03 | Lasbela Chowk |
| G03a | Sanitary Market |
| G04 | No. 1 Chowrangi |
| G05 | Model Park |
| G06 | Baqai Hospital |
| G07 | Public Park near Bridge |
| G08 | Board Office |
| G09 | KAD Chowrangi |
| G10 | Hydri Market |
| G11 | Five Star Chowrangi |
| G12 | Jummah Bazaar |
| G13 | Sakhi Hassan Chowrangi |
| G14 | Erum Shopping Emporium |
| G15 | Nagan Chowrangi |
| G16 | U.P. Mohr intersection |
| G17 | Rd 2400 |
| G18 | Power House Chowrangi |
| G19 | Rd 4200 |
| G20 | 2 minutes Chowrangi |
| G21 | Surujani Chowrangi |
| G22 | KDA Chowrangi Surjani Town |
| G23 | KESC Power House (terminal station) |

Important internal source conflicts:
- The JICA narrative immediately before Table 3-2-2 says the earlier study proposed 18 stations and JICA added four (22 total), but the detailed table contains 29 design entries.
- The same report's later detailed Table 6-3-1 also lists 29 entries, but calls G17 and G19 only "Street Name" rather than "Rd 2400" and "Rd 4200".
- G23 is explicitly described as a terminal station/depot. M2 is a proposed transfer terminal. G01 is shared with the Red Line. These are design-role notes, not proof of current passenger service.
- The JICA table is a 2012 feasibility design, not an as-built or current operator register. Do not import its 29 IDs into the current passenger sequence or assume all entries remain open.

Source: [JICA/KMC Karachi Transportation Improvement Project Final Report, Volume 2 (December 2012), Table 3-2-2 and Table 6-3-1](https://openjicareport.jica.go.jp/pdf/12086393_01.pdf).

### Current operating authority

The Sindh Government FY2025–26 Budget White Paper states that Green Line operations have transferred to SMTA and reports average ridership of 60,000 passengers/day in May 2025, up from 52,000 before transfer. The 2023–24 Ministry Year Book had described a planned handover from SIDCL by December 2024. Treat SMTA as the current operating authority for the requested station register; SIDCL/PIDCL remain important sources for historical project/design records. Neither source provides a current ordered station-ID list in the reviewed material.

- Budget White Paper FY2025–26: https://www.finance.gos.pk/Home/Download?path=Budget%2FBudgetBooks%2FFY-25-26%2FBUDGET+WHITE+PAPER+2025-26.pdf
- Ministry of Planning Year Book 2023–24: https://pc.gov.pk/uploads/pub/YB-2023-24-%20NEW-07-05-2025.pdf

### Competing 2026 passenger-facing lists — secondary evidence only

Both lists claim 22 stops between Numaish and Abdullah Chowk / Surjani, but their named entries differ materially. They are preserved as separate variants, not reconciled or merged.

- **BusUpdate list:** https://busupdate.com/pakistan/karachi/bus-routes/route-green-line/
- **CMTA list:** https://cmta.com.pk/karachi-green-line-brt-route/

The earlier candidate transcriptions are recorded in Phase 5AR. Differences include the Board Office / Orange Line interchange area, the Gulbahar-to-Hyderi section, and the Nagan-to-Surjani section.

### Green Line decision

- Retain **25** as the 2021 government project-count evidence and 2016 PIDCL progress-presentation count.
- Retain the JICA 2012 **29 design IDs** and PIDCL 2016 **29 named corridor points** as separate historical planning evidence sets; the JICA report itself has a 22-versus-29 internal count conflict.
- Retain the **22-stop** 2026 passenger-facing lists as separate current secondary candidate variants.
- Retain both **22-stop** 2026 secondary lists as separate candidate variants.
- Do not choose one list, delete four entries by inference, assign station coordinates, or create route geometry.
- Obtain a current dated operator station register or diagram with station IDs and ordered stops in both directions.

## Orange Line — source reconciliation

### Current operation and corridor endpoints

The Provincial Assembly of Sindh answer for **19 May 2026** reports that Orange Line (4 km) is operating from Town Municipal Administration Office, Orangi Town to Jinnah University for Women near Matriculation Board Office, serving approximately 2,500 passengers daily. An earlier Assembly answer dated 29 January 2026 reports the same endpoints and approximately 5,000 passengers/day. The ridership figures differ; neither answer provides the complete station sequence.

- 19 May 2026: https://www.pas.gov.pk/business/questios-details/33/2019
- 29 January 2026: https://pas.gov.pk/business/questios-details/33/1989

### Contract station IDs — four named entries

The 2021 Orange Line Facility Management Agreement Exhibit 1 lists:

1. **OL-1** — 5 No. Chowrangi
2. **OL-2** — Orangi Town Police Station
3. **OL-3** — Abdullah College
4. **OL-4** — Dilpasand Sweets

Source: https://pidcl.com.pk/wp-content/uploads/2021/02/Orange-Line-Project-Facility-Management-Agreement_compressed.pdf

These are contract station identities. The 2026 Assembly answer confirms the operating corridor endpoints but does not re-confirm the current names, order, station IDs or boarding platforms.

### Four-versus-five count discrepancy

- **SMTA Orange Line project page:** states four BRT stations plus one depot and describes the TMA Office–Jinnah University for Women alignment.
  - https://smta.sindh.gov.pk/brt-abdul-sattar-edhi-line-orange-line
- **Sindh Transport Department page:** reports five bus stations, but the reviewed page does not provide a station-by-station list that reconciles the count with OL-1 to OL-4.
  - https://transport.sindh.gov.pk/orange-line
- **BusUpdate secondary candidate list:** AO Chowk, Abdul Sattar Chowrangi, Poney Panch Chowrangi, TMO Office.
  - https://busupdate.com/pakistan/karachi/stations/tmo-office-station/

Do not treat the depot as a passenger station, infer a fifth stop, or map the BusUpdate labels to OL-1 through OL-4 without evidence. The contract also describes mixed-traffic continuation beyond the dedicated corridor; those mixed-traffic points must not be mistaken for additional Orange Line BRT stations.

### Orange Line decision

- Accept TMA Office Orangi Town to Jinnah University for Women near Matriculation Board Office as the latest government-reported operating corridor endpoints.
- Retain OL-1 to OL-4 as contract station identities, not as newly operator-confirmed current passenger stops.
- Preserve the four-versus-five count conflict and the ridership discrepancy.
- Do not create a complete current station sequence or passenger-facing geometry until the operator confirms station IDs, names, order, terminal equivalence and boarding platforms.

## Evidence required to close the BRT blocker

Request from SMTA as the current operating authority (and use SIDCL/PIDCL for historical project-record clarification):

- Current dated Green Line station register with unique station IDs, official names, sequence in both directions, operational status and WGS84 coordinates.
- Clarification of the 25-station project count versus 29 historical corridor points and the two conflicting 22-stop passenger lists.
- Confirmation of Green Line extension status, including whether Municipal Park is an operating passenger terminal.
- Current dated Orange Line station register mapping OL-1 to OL-4 to current station names and order.
- Written resolution of the Orange Line four-versus-five passenger-station count and the relationship between TMA Office, Board Office and Jinnah University for Women terminal labels.
- Confirmation of which portions are dedicated BRT and which are mixed-traffic continuation.

Until this evidence is received, keep BRT station sequences provisional and do not create verified coordinates or passenger-facing route geometry from the secondary lists.

## Relationship to prior research

This document reconciles and supplements:
- [Phase 5AR — Current Green and Orange Line source reconciliation](PHASE_5AR_CURRENT_GREEN_ORANGE_LINE_RECONCILIATION.md)
- [Phase 5BA — Current BRT status and operator evidence request](PHASE_5BA_CURRENT_BRT_STATUS_AND_OPERATOR_EVIDENCE_REQUEST.md)

The existing government-source findings remain controlling where they provide stronger dated evidence. This document does not replace their source records.

## Next safe action

Obtain written or published operator evidence for Green and Orange station names/order. In parallel, continue the 572-node historical coordinate audit and candidate crosswalk as separate research-only workstreams. Do not promote any candidate coordinate or route geometry based on name matching alone.


## Cross-corridor guard — TransKarachi's 22-station count is Red Line evidence (19 November 2026)

A fresh check of the official TransKarachi website found a separate **Red Line** station count that must not be attributed to the Green Line:

- TransKarachi's home page labels the project as **Karachi BRT Red Line** and says 22 K-BRT stations are planned on a dedicated corridor from Malir Halt to Numaish.
- Its official [Routes page](https://transkarachi.pk/routes/) explicitly identifies the Red Line, describes the 26.6 km Malir Halt–Tower corridor (24.2 km main corridor to Numaish plus 2.4 km common corridor to Tower), and lists Red Line locations including Model Colony, Safoora Goth, Met Office, Safari Park, Federal Urdu University, Civic Centre, Dawood University, Numaish, King Cottages, NED University, NIPA, Masjid Baitul Mukarram, Askari Park, Society Office and Tower.
- The Government of Sindh's [Karachi BRT page](https://transport.sindh.gov.pk/karachi-bus-rapid-transit-brt) likewise identifies TransKarachi as the implementation agency for the Red Line.

Therefore, TransKarachi's **22-station Red Line count is not evidence for the Green Line's station count or ordered sequence**. Keep the Green Line's 25-station government project-count evidence, 29 historical planning corridor points and two separate 22-stop secondary passenger-facing lists in their existing evidence classes. Do not merge the Red Line count or station names into the Green Line register.

This also reinforces the need to keep the corridor identities separate:
- Green Line: existing north–central corridor Surjani/Abdullah Chowk–Numaish, with the Numaish–Municipal Park extension separately under development.
- Red Line: separate TransKarachi/ADB corridor Malir Halt–Numaish, with a shared/common corridor continuing toward Tower.
- Orange Line: separate Orangi Town corridor, with its own four-versus-five station evidence conflict.

Sources:
- TransKarachi official routes page: https://transkarachi.pk/routes/
- TransKarachi official home page: https://transkarachi.pk/
- Government of Sindh BRT page: https://transport.sindh.gov.pk/karachi-bus-rapid-transit-brt

No Green Line or Red Line station sequence is changed or approved by this clarification.
