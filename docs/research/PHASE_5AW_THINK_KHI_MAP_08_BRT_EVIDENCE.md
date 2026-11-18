# Phase 5AW — Think Transportation KHI-MAP-08 Green/Orange BRT map evidence

**Review date:** 2026-11-18  
**Source map date:** 1 January 2025  
**Map reference:** KHI-MAP-08  
**Access path:** [SMTA-hosted Karachi Bus Route Map PDF](https://smta.gos.pk/downloads/karachi-bus-route-map.pdf)

## Source identity and scope

The one-page PDF is branded Think Transportation, bears reference KHI-MAP-08 and date 01/01/2025, and contains a schematic map of Karachi bus services including Green Line and Orange Line. SMTA's route-map page says the map data is courtesy of Think Transportation and published with permission, while disclaiming responsibility for authentication of third-party service data. The PDF itself also disclaims authentication and states that use without permission is prohibited.

This is a dated third-party schematic, not an operator-issued station register. It can corroborate corridor depiction and published map labels, but it is not a surveyed route centerline, GPS station schedule, or proof of current passenger boarding platforms. This phase does not extend the user's Think Transportation primary-source decision for R/EV into an unapproved blanket source policy for BRT.

## Green Line observations

The map visually depicts the Green Line corridor between the Power House/Surjani side and central Karachi. Readable named map labels include Power House Chowrangi, Abdullah Chowk, Surjani KDA, Karimi Chowrangi, 4K Chowrangi, 2 Mint Chowrangi, Aisha Complex, UP Mor, Nagan Chowrangi, Erum Shopping, Sakhi Hasan Chowrangi, Five Star Chowrangi, Hyderi Bus/Market, KDA Chowrangi, Board Office, Annu Bhai Park, Model Park, Nazimabad No. 1, Lasbela and Guru Mandir.

These labels are recorded as map annotations, not approved station IDs. The diagram does not establish which labels correspond to currently operating passenger platforms, nor does it resolve the discrepancy between the historical 25-station project count and conflicting 22-stop secondary lists. The image is schematic and should not be converted into road-following geometry or stop coordinates.

## Orange Line observations

The map depicts the Orange Line corridor and the connection toward the Green Line at Board Office. It includes visible nearby labels such as Police Station and Abdullah College, but does not provide a machine-readable operator station-ID schedule or an unambiguous current physical platform sequence. It therefore does not resolve the official four-BRT-station versus five-bus-station discrepancy documented in Phase 5AV.

## Decisions

1. Add KHI-MAP-08 as a dated, attributed schematic evidence source for Green/Orange corridor depiction.
2. Preserve visible labels as map annotations only; do not promote them to verified stops or station IDs.
3. Do not derive coordinates, road-following geometry, station order, or current operating status from this schematic.
4. Keep Green Line 25-station project count, 29 historical corridor points, and two different 22-stop secondary lists separate.
5. Keep Orange Line official 4-vs-5 station-count claims and contract station IDs separate pending current operator confirmation.
6. No MySQL writes, stop approvals, route activation, geometry edits, or public API changes were made.

## Licensing and attribution

Attribute the map to Think Transportation, KHI-MAP-08, dated 1 January 2025, and retain the source's permission restriction. SMTA hosting/publishing the map with permission does not by itself grant a general licence for redistribution of the original map or extracted geometry.
