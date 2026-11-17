# Phase 5R — Green and Orange Line station-sequence evidence register

**Status:** Source versions separated and transcribed. No final current station sequence or station coordinates are approved by this phase.

## Green Line: two distinct published versions

### A. Government project presentation — 16 August 2016

The Government of Pakistan / PIDCL project presentation identifies a Green Line corridor from KESC Power House, Surjani Town to Municipal Park and reports **25 BRT stations**. Its corridor sequence section names the following 29 points:

1. KESC Power House
2. KDA Chowrangi Surjani Town
3. Karimi Chowrangi
4. Surjani Chowrangi
5. Two Minute Chowrangi
6. Road 4200
7. Power House Chowrangi
8. Road 2400
9. UP Mor Intersection
10. Nagan Chowrangi
11. Erum Shopping Emporium
12. Sakhi Hassan Chowrangi
13. Jummah Bazar
14. Five Star Chowrangi
15. Hydari Market
16. KDA Chowrangi
17. Board Office
18. Public Park
19. Baqai Hospital
20. Model Park
21. No. 1 Chowrangi
22. Lasbela Chowk
23. Gurumandir
24. West of Quaid-e-Azam
25. KGA Ground
26. Taj Medical Complex
27. Garden Square
28. Radio Pakistan
29. Municipal Park

This is preserved as a **historical planning corridor-point list**, not silently represented as 29 current passenger stations. The same presentation's station-count field says 25, while the named-point list contains 29 entries. Some entries may be terminals, interchange/area labels or corridor points rather than distinct station platforms. This discrepancy requires the original station schedule or station-ID drawing to resolve.

Source: [PIDCL / Government of Pakistan Green Line progress presentation, updated 16 Aug 2016](https://pidcl.com.pk/wp-content/uploads/2016/08/Updated-Progress-Presentation-Green-Line-16-8-16.pdf), especially the project brief and station/corridor sequence.

### B. Passenger-facing 22-stop sequence

The 22-stop Abdullah Chowk (Surjani) to Numaish sequence remains a secondary-source candidate:

1. Abdullah Chowk
2. KDA Flats
3. Karimi Chowrangi
4. 4K Chowrangi
5. 2 Minute Chowrangi
6. Road 2400 (Aisha Complex)
7. Power House Chowrangi
8. Road 4200 (Saleem Centre)
9. U.P. More
10. Nagan Chowrangi
11. Erum Shopping
12. Jummah Bazar
13. Five Star Chowrangi
14. Hyderi
15. Board Office
16. Annu Bhai Park
17. Enquiry Office
18. Nazimabad No. 1
19. Sanitary Market (Gulbahar)
20. Lasbela Chowk
21. Patel Para (Guru Mandir)
22. Numaish

Two passenger-facing transport guides publish this general sequence, but the current accessible SMTA route-map directory does not provide a complete station-by-station Green Line schedule. It must remain **provisional** until confirmed against a current TransKarachi / operator station schedule with official station identifiers and operating status.

Sources:
- [BusUpdate Green Line passenger route list](https://busupdate.com/pakistan/karachi/bus-routes/route-green-line/)
- [Explore Pakistan Green Line guide](https://explorepakistan.live/destinations/guides/karachi-green-line)

### Green Line decision

Do not merge the 2016 29-point planning transcription with the 22-stop passenger list or with the historical 22-node coordinate graph. They are different source versions and scopes. The 2016 presentation's 25-station count versus 29 named points is an explicit open reconciliation issue. No Green Line station coordinate or road-following geometry is approved.

## Orange Line: contract station identities

The 2021 Orange Line Facility Management Agreement Exhibit 1 lists four contract station identities in this order:

1. **OL-1 — 5 No. Chowrangi**
2. **OL-2 — Orangi Town Police Station**
3. **OL-3 — Abdullah College**
4. **OL-4 — Dilpasand Sweets**

SMTA's project page independently describes the corridor from TMA Office, Orangi Town to Jinnah University for Women near the Matriculation Board Office and states that the project has four BRT stations and a 3.88 km corridor. It records formal bus operations commencing on 10 September 2022.

The four contract names are station identities in the agreement, while TMA Office and Jinnah University/Board Office are project endpoints/landmarks. Do not add the corridor endpoints as extra stations or infer unlisted intermediate stops. Confirm the current operating station order and IDs with the operator before mapping.

Sources:
- [Orange Line Facility Management Agreement (2021)](https://pidcl.com.pk/wp-content/uploads/2021/02/Orange-Line-Project-Facility-Management-Agreement_compressed.pdf)
- [SMTA — Abdul Sattar Edhi Orange Line project](https://smta.sindh.gov.pk/brt-abdul-sattar-edhi-line-orange-line)

## Machine-readable output

`data/research/PHASE_5R_BRT_STATION_SEQUENCE_EVIDENCE.csv` stores all 29 Green Line historical planning points, all 22 secondary passenger-list stops and the four Orange Line contract station names with source-version and verification labels.

## Next evidence needed

- Green Line: current operator station schedule with station IDs, platform locations, operating status and direction/order; explanation of the 2016 25-station count against the 29 named points.
- Orange Line: current operator confirmation that the four contract station IDs/names and sequence remain the operational set; exact platform/boarding coordinates and whether any extension or interchange service changes the operating path.

All station rows remain non-approved for coordinate matching and route geometry. OSM remains the primary basemap; OSM proximity is not proof of station location.
