# Phase 5AZ — Zenodo DOI conflict and licence statement reconciliation

**Review date:** 2026-11-18  
**Status:** DOI conflict resolved; publisher licence statement found; no database or route/stop status changes.

## Finding 1 — canonical Karachi Bus Network dataset

The matching dataset is [Karachi Bus Network, Zenodo DOI 10.5281/zenodo.13951512](https://zenodo.org/records/13951512), Version v1, published 18 October 2024 by Data Research Lab Pakistan. The record identifies Muhammad Qasim Pasta (data curator), Moid Raza Khan and Fatima Aslam (data collectors), affiliated with Habib University. Its description covers 76 Karachi public bus routes (BRT and minibuses), with route information compiled from Travel Culture and HamariWeb and stop coordinates extracted using Google Maps. It provides the node CSV, edge CSV, GraphML and R generation script. The node CSV has 572 node rows.

## Finding 2 — the conflicting DOI is unrelated

The other DOI cited in repository issue #13, [10.5281/zenodo.13932672](https://zenodo.org/records/13932672), resolves to **xIndices: Version 1.2.1**, a software record published 15 October 2024 by Jivesh Dixit, affiliated with IIT Delhi and the National Centre for Medium Range Weather Forecasting. Its description is a Python library for climate variability indices. It is not a Karachi transport dataset, not another version of the Karachi Bus Network dataset, and not a record by Data Research Lab Pakistan.

**Decision:** Use `10.5281/zenodo.13951512` as the sole canonical dataset DOI. Treat `13932672` in issue #13 and any associated repository notes as a mistaken cross-reference, not as a second candidate dataset.

## Finding 3 — licence evidence

The [Data Research Lab Pakistan companion project page](https://darlab-pakistan.github.io/karachi-bus-network/) explicitly states that the Karachi Bus Network dataset is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**. This publisher-controlled project page describes the same dataset and cites DOI `10.5281/zenodo.13951512`.

The [Zenodo dataset record](https://zenodo.org/records/13951512) currently displays a Rights heading and a License subheading but no readable licence value beneath it. Preserve this distinction:
- Publisher's companion page: explicit CC BY 4.0 declaration.
- Zenodo record's visible Rights section: no displayed value.
- Do not claim that the Zenodo record exposes a populated machine-readable `cc-by-4.0` field.
- Use attribution consistent with CC BY 4.0 as stated by the publisher, while retaining the metadata discrepancy in the provenance register.

The unrelated xIndices record displays licenses for that software record; those licenses have no bearing on the Karachi bus dataset.

## Data and publication implications

1. Update the canonical citation to DOI `10.5281/zenodo.13951512` only.
2. Remove the unresolved second-DOI conflict from the project checklist by identifying `13932672` as unrelated software.
3. Record the publisher's CC BY 4.0 statement and the blank Zenodo Rights display separately.
4. Retain attribution to Data Research Lab Pakistan and the listed creators.
5. Keep the dataset classified as 2024 historical secondary research, not current operator service evidence.
6. Keep all 572 historical node coordinates and 1,415 directed edge records unchanged.
7. Keep imported source `pending`, stops/routes `under_review`, and route shapes empty until independently verified.
8. Do not execute the local MySQL importer or metadata SQL as part of this research change.

## Sources

- [Zenodo — Karachi Bus Network, DOI 10.5281/zenodo.13951512](https://zenodo.org/records/13951512)
- [Data Research Lab Pakistan — Karachi Bus Network project page (CC BY 4.0 statement)](https://darlab-pakistan.github.io/karachi-bus-network/)
- [Zenodo — xIndices, DOI 10.5281/zenodo.13932672](https://zenodo.org/records/13932672)
- [Zenodo guidance — licence and rights metadata](https://help.zenodo.org/docs/deposit/describe-records/licenses/)
