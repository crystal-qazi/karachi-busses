# Phase 5BC — Think Transportation KML permission and data request

**Review date:** 18 November 2026  
**Status:** Permission request prepared; not sent. Public redistribution remains blocked pending written permission.

## 1. Why this request is required

Think Transportation's Karachi route-map material identifies Ref. KHI-MAP-08, dated 01 January 2025. Its published disclaimer says use of the map without permission is prohibited. SMTA's route-map page credits Think Transportation and states that the map was published with permission, but that permission statement applies to SMTA's own publication context. It does not grant this project a separate right to copy, transform, redistribute or display the KML/route geometry.

The user's supplied KML is accepted as the primary R/EV route-line reference for research and reconciliation. User-supplied possession does not, by itself, establish public redistribution permission.

Until written permission is received:
- Keep the KML as a research/reference input only.
- Do not publish the KML, derived GeoJSON, route line coordinates or a public map layer copied from it.
- Do not infer that SMTA's permission extends to this independent application.
- Keep route_shapes empty and do not enable route geometry in the public API.

## 2. Published contact details

Think Transportation's official contact page publishes:
- Email: info@thinktransportation.net
- Phone: +92-343-2845847
- WhatsApp: +92-343-2851396
- Karachi office: Bungalow No. A-23, Block 10-A, Gulshan-e-Iqbal, Karachi, Pakistan

Source: https://thinktransportation.net/contact-us/

## 3. Draft permission request

**To:** info@thinktransportation.net  
**Subject:** Permission request to use Karachi bus route KML geometry in a public transport information application

Dear Think Transportation Team,

I am developing a Karachi public transport information application and have been using your Karachi Red Bus / People's Bus Service route-map material as the primary reference for reconciling R-series and EV bus route alignments.

I understand that the published KHI-MAP-08 material carries a notice that use without permission is prohibited. I therefore request your written permission before publishing or redistributing any route geometry derived from your map/KML.

The supplied KML reference contains route lines for R1, R2, R3, R4, R8, R9, R10, R11, R12, R13 and EV-01 through EV-05. Please confirm whether you can grant permission for the following uses:

1. Store the route-line geometry in the application's private research database and source-controlled project repository.
2. Display the route lines on a publicly accessible web map for passenger information.
3. Convert the supplied KML route lines to GeoJSON or another web-map format, while preserving the original geometry and route identity.
4. Make limited technical transformations required for web display (for example, coordinate-format conversion or geometry simplification), if permitted.
5. Publish derived route-line data in the application's public API or downloadable data export, if permitted.
6. Use the geometry in a non-commercial application, and please advise whether separate permission or fees would apply if the application later becomes commercial or revenue-generating.

Please also advise the exact attribution wording, copyright notice, source link, licence/terms, permitted derivative works, redistribution conditions, and any restrictions on hosting the route geometry in a public GitHub repository.

If available, I would appreciate a current dated source package or confirmation of:
- Route codes and official route names.
- Direction of travel for each route line.
- Current effective date and operational status.
- Whether route geometry is approved for both directions or represents a single corridor.
- Any current stop/station register with stop IDs, official names, coordinates and boarding-side/platform information.
- Any route changes or temporary diversions after the 01 January 2025 KHI-MAP-08 map.

I will not publish the geometry or claim that your company has endorsed the application unless that is expressly included in your written permission. If permission is limited to display only, I will respect that and will not redistribute source coordinates or derivative geometry.

Thank you for considering this request. Please let me know if there is a formal licensing or permission process I should follow.

Regards,  
Karachi public transport data research

## 4. Permission response register

Complete this register only after receiving a written response:

| Permission item | Current state |
|---|---|
| Private research storage | Not confirmed |
| Public web-map display | Not confirmed |
| KML-to-GeoJSON conversion | Not confirmed |
| Geometry simplification / other derivatives | Not confirmed |
| Public API / downloadable data redistribution | Not confirmed |
| GitHub repository hosting | Not confirmed |
| Non-commercial use | Not confirmed |
| Commercial use / monetisation | Not confirmed |
| Attribution wording | Not confirmed |
| Current route update package | Not received |

## 5. Publication gate

Written permission must clearly cover the intended use. A generic acknowledgement, permission to view the website, or SMTA's permission to publish KHI-MAP-08 is not enough to infer that this project may redistribute route coordinates.

If Think Transportation permits display but not redistribution, the application must use an architecture that respects that restriction and must not expose the underlying route coordinates through its API or downloadable files.

No email has been sent, no permission is claimed, and no KML/route geometry has been added to the public application or database in this phase.
