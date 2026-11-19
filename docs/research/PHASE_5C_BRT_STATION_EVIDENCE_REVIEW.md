# Phase 5C — BRT station-sequence evidence review

**Research date:** 19 November 2026  
**Scope:** Green Line and Orange Line station-order evidence only. This is a source audit, not operator verification, field verification, owner approval, or publication approval.

## Decision summary

- **Green Line:** Do not approve a station sequence yet. The current SMTA route-map page identifies the Green Line but does not publish an ordered station list in its text. Two 2026 secondary references publish different 22-station sequences. Preserve them as competing candidate transcriptions; neither is an operator-confirmed station register.
- **Orange Line:** The current SMTA project page describes the alignment as TMA Orangi to Jinnah University for Women and says four BRT stations. A Sindh Transport Department page reports five stations. The Provincial Assembly's 30 January 2026 answer confirms the service is operating between TMA Office, Orangi Town and Jinnah University for Women near Matriculation Board Office, but does not name or count stations. A 2026 secondary station directory lists four names. Do not silently resolve the four-versus-five discrepancy or adopt the secondary names as authoritative.
- **No database changes:** No station records, stop coordinates, route sequences, route shapes, activation states, or public API data were changed.

## Green Line — source comparison

### Official-source evidence

1. **SMTA Karachi Bus Route Map** identifies BRT Green Line as a BRT system but its accessible route index does not enumerate the station names or their order. It is useful for confirming the system's inclusion in the official route map, not for reconstructing a complete station sequence.
   - https://smta.gos.pk/route-map
   - Accessed 19 November 2026.

2. **JICA Karachi Transportation Improvement Project final report** contains a historical planning-stage Green Line station-location table. It is not a current as-built or operator station list and must not be used as proof of today's station names/order.
   - https://openjicareport.jica.go.jp/pdf/12086393_01.pdf
   - Published approximately 2013.

### Competing secondary transcriptions — retain separately

**Candidate A — CMTA.com.pk, Numaish to Surjani (22 entries), published 16 November 2026:**

1. Numaish Chowrangi
2. Guru Mandir (Patel Para)
3. Lasbela Chowk
4. Gul Bahar (Sanitary Market)
5. Urdu Bazaar
6. Eid Gah Bagh
7. North Nazimabad
8. Orange Line Interchange
9. Shahrah-e-Humayun
10. Hyderi
11. Shahrah-e-Jehangir
12. Sakhi Hassan
13. Nagan Chowrangi
14. UP Morr
15. North Karachi
16. 4K Chowrangi (Surjani Chowrangi)
17. Power House Chowrangi
18. Road 2400 (Aisha Complex)
19. Road 4200 (Saleem Centre)
20. KDA Flats
21. Karimi Chowrangi
22. Abdullah Chowk (Surjani Terminal)

Source: https://cmta.com.pk/karachi-green-line-brt-route/

**Candidate B — BusUpdate.com station dataset, October 2026, reversed here only to show the same south-to-north direction (22 entries):**

1. Numaish
2. Patel Para (Guru Mandir)
3. Lasbela Chowk
4. Sanitary Market (Gulbahar)
5. Nazimabad No.1
6. Enquiry Office
7. Annu Bhai Park
8. Board Office
9. Hyderi
10. Five Star Chowrangi
11. Jummah Bazar
12. Erum Shopping
13. Nagan Chowrangi
14. U.P. More
15. Road 4200 (Saleem Centre)
16. Power House Chowrangi
17. Road 2400 (Aisha Complex)
18. 2 Minute Chowrangi
19. 4K Chowrangi
20. Karimi Chowrangi
21. KDA Flats
22. Abdullah Chowk

Source: https://busupdate.com/pakistan/karachi/stations/u-p-more-station/ (appendix described as compiled October 2026).

**Comparison finding:** Both sources claim 22 stations and share some names, but the station names and order differ materially. Examples include the Board Office / Orange Line interchange area, the Gulbahar-to-Hyderi section, and the Nagan-to-Surjani section. Do not combine the two lists, choose one by majority, or use either to create verified stop records. Obtain the operator's current station list or a dated official station diagram.

## Orange Line — source comparison

### Official-source evidence

1. **SMTA project page — BRT Abdul Sattar Edhi Line (Orange Line):**
   - Describes the route from Town Municipal Administration Office, Orangi Town to Jinnah University for Women near Matriculation Board Office.
   - States four BRT stations and one depot.
   - States formal bus operations commenced on 10 September 2022 and names Daewoo Pakistan Express Bus Service Ltd. as operator.
   - https://smta.sindh.gov.pk/brt-abdul-sattar-edhi-line-orange-line
   - Accessed 19 November 2026.

2. **Sindh Transport Department Orange Line page:**
   - Reports five bus stations, conflicting with the SMTA project page's four.
   - https://transport.sindh.gov.pk/orange-line
   - Search result accessed 19 November 2026; page retrieval timed out during this review. Treat the count as an official-source discrepancy requiring direct confirmation.

3. **Provincial Assembly of Sindh, answer dated 30 January 2026:**
   - Confirms Orange Line was in operation from TMA Office, Orangi Town to Jinnah University for Women near Matriculation Board Office.
   - Does not enumerate the station names or resolve the four-versus-five count.
   - https://www.pas.gov.pk/business/questios-details/33/1989

### Secondary candidate station list — not approved

BusUpdate's October 2026 station dataset lists four entries in this order:

1. AO Chowk
2. Abdul Sattar Chowrangi
3. Poney Panch Chowrangi
4. TMO Office

Source: https://busupdate.com/pakistan/karachi/stations/tmo-office-station/

The list is consistent with SMTA's stated count of four, but not with the Sindh Transport Department page's count of five. It also needs the operator to confirm whether AO Chowk / Board Office and Jinnah University for Women / Matriculation Board Office are the same official terminal/station label or distinct places in the operational station sequence. Do not use this secondary list as a verified sequence.

## Required evidence to close the BRT sequence blocker

Request from SMTA / SIDCL / the Orange Line operator:

- Current dated station register or route/station diagram for Green Line, including official names and terminal labels in both directions.
- Current dated station register for Orange Line, explicitly resolving four versus five stations and naming each station in order.
- Confirmation of interchange naming and whether interchange labels represent one physical station or separate facilities.
- Any current service suspension, extension, or station-closure notices affecting the station list.

Until that evidence is received, keep both BRT station sequences provisional and do not create verified station coordinates or passenger-facing route geometry from these lists.

## Relationship to the route-owner review register

Owner confirmations for R-series and EV-series routes record agreement with the displayed source stop names/order only. They do not satisfy operator confirmation, physical boarding-platform verification, coordinate verification, reverse-direction verification, or geometry rights. The unresolved route identity variants in Phase 5C remain open for the same reason.

## Next safe action

Obtain written or published operator evidence for Green and Orange station names/order. In parallel, continue the 572-node historical coordinate audit as a separate research-only workstream; do not match coordinate collisions or ambiguous nodes to physical boarding stops without independent evidence.
