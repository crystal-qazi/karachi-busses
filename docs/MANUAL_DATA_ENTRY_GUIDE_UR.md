# Karachi Buses — Manual Data Entry Guide (Urdu / Roman Urdu)

Yeh guide admin panel mein manually operator, bus, route, stops, stop sequence aur route geometry enter karne ke liye hai.

## 1. Pehle yeh samjhein: data ke 5 alag hissey

1. **Operator / Bus service:** service chalane wala idara/company.
2. **Route:** route code, naam, category, origin aur destination.
3. **Stops:** har physical boarding/alighting point ka naam aur coordinates.
4. **Route sequence:** har direction mein stops ka sahi order.
5. **Route geometry:** map par road-following line, jo bus ke actual raaste ko dikhati hai.

Bus (vehicle) aur Bus Route alag concepts hain. Agar app mein vehicle/fleet module available nahi, to route ko bus/vehicle record samajh kar enter na karein.

## 2. Data enter karne se pehle tayyari

Har route ke liye yeh evidence ikattha karein:
- Official/operator route name and code.
- Operator and service category.
- Origin and destination.
- Direction (outbound/inbound) and stop order.
- Stop names, latitude, longitude, boarding-side confirmation.
- Route geometry as GeoJSON LineString (WGS84 / EPSG:4326).
- Source name, source URL/document, access date, reviewer and notes.
- Evidence of current service status. Historical route list ko current service na samjhein.

Coordinate format:
- Latitude: 24.xxxxxx
- Longitude: 67.xxxxxx
- GeoJSON coordinate order is **[longitude, latitude]**, not [latitude, longitude].

## 3. Admin panel mein entry ka recommended order

Menu labels app version ke mutabiq thore different ho sakte hain. Sirf woh menu use karein jo aapke admin panel mein waqai maujood ho.

### Step A — Operator / service
1. Admin login karein.
2. Operators ya Service Providers section kholein (agar available ho).
3. Add New par operator ka official naam enter karein.
4. Duplicate operator create na karein; pehle existing list search karein.
5. Save karein.

### Step B — Route create karein
1. Routes section kholein.
2. Add Route select karein.
3. Route code, official name, category, operator, origin, destination aur direction details enter karein.
4. Route status ko default **under_review / draft** par rakhein jab tak evidence approve na ho.
5. Source/provenance fields available hon to fill karein.
6. Save karein aur generated Route ID note karein.

### Step C — Stops create karein
1. Stops section kholein.
2. Har stop ko pehle search karein; same physical stop ko duplicate na banayein.
3. Stop name, latitude, longitude, locality/area, source and verification note enter karein.
4. Coordinates decimal degrees mein enter karein.
5. Map marker ko zoom karke check karein. Marker road ke beech ya wrong side par ho to boarding point confirm kiye baghair approve na karein.
6. Save karein aur Stop ID note karein.

### Step D — Route ke saath stops attach karein
1. Route detail / Route Stops / Direction Stops section kholein.
2. Correct route aur direction select karein.
3. Stops ko actual travel order mein add karein.
4. Har stop ka sequence number 1, 2, 3... set karein.
5. Return direction ka order alag record karein; sirf outbound list reverse copy na karein jab tak actual service same na ho.
6. Duplicate sequence numbers, missing stops aur impossible jumps check karein.
7. Save and preview route.

### Step E — Route geometry add karein
Geometry ek ordered road-following polyline honi chahiye. Sirf origin aur destination ke do points se route shape complete nahi hoti.

Recommended GeoJSON:
```json
{
  "type": "Feature",
  "properties": {
    "route_code": "R1",
    "direction": "outbound",
    "source": "official route map",
    "review_status": "under_review"
  },
  "geometry": {
    "type": "LineString",
    "coordinates": [
      [67.123456, 24.987654],
      [67.124100, 24.988100],
      [67.125000, 24.989000]
    ]
  }
}
```

1. Geometry import/editor section available ho to GeoJSON upload karein.
2. Coordinate system WGS84 / EPSG:4326 confirm karein.
3. GeoJSON coordinates **longitude first, latitude second** hoti hain.
4. Geometry direction ke travel order mein honi chahiye.
5. Map preview mein line roads par follow karti hai ya nahi zoom karke dekhein.
6. Stops geometry ke qareeb hon, lekin road ke doosri side ke stop ko automatically same boarding point na samjhein.
7. Source and review status preserve karein.
8. Save as under_review; reviewer approval ke baad hi publish/active karein.

Agar admin panel mein geometry upload ka option nazar nahi aata, to random JSON database mein paste na karein. Neeche diya gaya Qoder prompt use karke app mein safe geometry editor/import workflow add karwayen.

## 4. GeoJSON geometry kahan se banayein?

Possible workflows:
- QGIS mein road network load karke route ke roads par line digitize karein, phir GeoJSON (EPSG:4326) export karein.
- Operator ki official route polyline/map se source data hasil karein.
- Field survey / GPS trace ko clean karke road-following line banayein.
- OSM roads routing ko supporting reference ke taur par use karein; OSM par nearest road hona bus route ka proof nahi.

Har geometry ke saath source, date, direction, reviewer aur confidence note rakhein.

## 5. Save karne ke baad QA checklist

- [ ] Route code duplicate nahi.
- [ ] Operator/category sahi.
- [ ] Origin/destination official source se match.
- [ ] Stops duplicate nahi.
- [ ] Har stop ka lat/lon correct.
- [ ] Stop order verified.
- [ ] Outbound/return directions separately checked.
- [ ] Geometry LineString valid and ordered.
- [ ] GeoJSON uses [longitude, latitude].
- [ ] Geometry route ke roads par follow karti hai.
- [ ] Stops geometry ke qareeb hain; large offsets investigated.
- [ ] Source and evidence attached.
- [ ] Status under_review until reviewer approval.
- [ ] Public map par sirf approved records visible.

## 6. Existing Karachi Buses data ke hawale se important caution

Current reviewed export (2026-11-21) mein 98 routes, 572 stops, 1,281 route-stop associations, 1,415 historical segments aur 2 saved route shapes the. 95 routes aur 566 stops under_review thay. Is liye existing historical data ko current verified service assume na karein. Naye records add karte waqt pehle search karein taake duplicates na banen.

## 7. Agar admin panel mein exact button/menu na mile

App ke current UI ka screenshot ya page URL dekh kar usi screen ke mutabiq steps follow karein. Menu labels/version guess na karein. Existing records par bulk changes karne se pehle database backup aur staging test zaroor karein.

## 8. Qoder prompt — missing geometry workflow implement karne ke liye

Agar current app mein route geometry create/import/edit ka complete admin UI nahi hai, yeh prompt Qoder mein paste karein:

> Inspect the existing Karachi Buses Flask/MySQL repository and implement a production-safe Route Geometry management workflow using the existing architecture and Bootstrap UI. Do not invent table or column names: inspect schema, models, migrations, authorization and existing route/stop CRUD first. Add admin-only GeoJSON Feature/LineString import, validation (WGS84 EPSG:4326, longitude-latitude order, finite coordinate bounds, minimum two distinct points), map preview/editing if compatible with the current Leaflet setup, route + direction association, source/provenance metadata, review status, duplicate detection, and audit logging. Preserve existing geometries and IDs. Never auto-activate imported data. Add CSRF protection, role checks, size/vertex limits, clear validation errors, transaction-safe saves, tests and documentation. Provide a dry-run preview before database writes. Do not change existing production records or mark any unverified route/stop active. Run the existing test suite and report changed files, migration steps, backup/rollback procedure and test results.

## 9. Golden rule

**Pehle source → phir route → phir stops → phir sequence → phir geometry → phir QA → phir approval/publish.**

Is order ko follow karne se incomplete ya wrong data public map par show nahi hoga.
