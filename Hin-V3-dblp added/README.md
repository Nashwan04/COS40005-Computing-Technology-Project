# P88 — Final client/supervisor HIN demonstration pack

**Goal:** Prove how source JSON + an explicitly supplied schema becomes a **heterogeneous information network** with unique nodes, typed edges, two directions of typed adjacency lookup, independent edge verification, CSV/GraphML exports, and an actual-data visual example.

The enhanced `hin_v2.py` preserves the original schema-driven engine and CLI; additions include optional `--data-root`, grouped typed adjacency (`typed_adjacency`), reverse lookup (`reverse_adjacency`), and primary-sample metadata. Everything uses the Python standard library; **no pip install is required**.

> **Do not claim the project fully supports arbitrary datasets, XML, RDF, automatic schema inference, all DBLP variants, or CSR.** Those are not implemented in this pack. The DBLP normalizer specifically handles AMiner V11/V13 JSON objects with nested author/venue IDs. First-N sampling is not representative sampling.

## 1. Folder location — without duplicating your huge Yelp dataset

Extract the ZIP **into its own folder within your P88 folder**, without overwriting the existing files:

```text
P88/
├── yelp_dataset/                             <-- existing, huge, NOT in ZIP
│   ├── yelp_academic_dataset_review.json
│   ├── yelp_academic_dataset_user.json
│   └── yelp_academic_dataset_business.json
└── P88_Final_Demo_Package/                   <-- extracted ZIP contents
    ├── hin_v2.py
    ├── yelp_schema_v2.json
    ├── yelp_tiny_schema.json
    ├── dblp_schema_example.json
    ├── dblp_synthetic_large_schema.json
    ├── dblp_real_schema.json
    ├── p88_client_demo.py
    ├── demo_data/                            <-- only small synthetic data in ZIP
    ├── tools/
    ├── tests/
    ├── docs/
    └── outputs/                             <-- created as you run commands
```

If your ZIP extracts into an extra nested folder, open **the folder containing `hin_v2.py`** in VS Code. On Windows, select **Terminal → New Terminal**, and confirm your path ends with `P88_Final_Demo_Package`.

Run `python --version` (Windows alternative: replace `python` with `py`).

## 2. First run — small SYNTHETIC DBLP-style dataset, no downloads

```powershell
python hin_v2.py --schema dblp_schema_example.json --output outputs/dblp_small.json
python tools/verify_edges.py --schema dblp_schema_example.json --graph outputs/dblp_small.json
python tools/visualize_shared.py --graph outputs/dblp_small.json --relation AUTHORED_BY --target-type Author --output outputs/dblp_small_graph.html
python tools/export_graph.py --graph outputs/dblp_small.json --outdir outputs/dblp_small_exports
```

Expected from supplied example: **8 nodes, 10 edges**: 4 Paper, 2 Author, 2 Venue; 6 AUTHORED_BY and 4 PUBLISHED_IN. The verification should return `passed: true`, `edges_matching_source_references: 10`. Open `outputs/dblp_small_graph.html` in Chrome. This is **synthetic teaching data**, not real DBLP.


## 2A. Optional offline Yelp-format demonstration (no large download)

These three records are **SYNTHETIC** and are only a fallback for machines without the real Yelp dataset. They demonstrate the same source→schema→shared-Business mapping and the source-record checker:

```powershell
python hin_v2.py --schema yelp_tiny_schema.json --data-root demo_data/yelp_tiny --output outputs/yelp_tiny.json
python tools/verify_edges.py --schema yelp_tiny_schema.json --data-root demo_data/yelp_tiny --graph outputs/yelp_tiny.json
python p88_client_demo.py --graph outputs/yelp_tiny.json --raw demo_data/yelp_tiny/yelp_dataset/yelp_academic_dataset_review.json --output outputs/yelp_tiny_proof.json
```

Open `outputs/client_demo_graph.html`. Expected: **7 unique nodes and 6 edges**, with two distinct reviews sharing a single business node and a sample raw-reference PASS. **Do not present these records as authentic Yelp data.**

## 3. Run Yelp with 50 and 5,000 REAL reviews

These commands assume your large `yelp_dataset/` folder is next to (not inside) this extracted demo folder, as shown above. `--data-root ..` instructs the code to resolve data paths from its parent P88 folder.

```powershell
python hin_v2.py --schema yelp_schema_v2.json --data-root .. --limit 50 --output outputs/yelp_50.json
python hin_v2.py --schema yelp_schema_v2.json --data-root .. --limit 5000 --output outputs/yelp_5000.json
python tools/verify_edges.py --schema yelp_schema_v2.json --data-root .. --graph outputs/yelp_5000.json --output outputs/yelp_5000_verification.json
python p88_client_demo.py --graph outputs/yelp_5000.json --raw ../yelp_dataset/yelp_academic_dataset_review.json --output outputs/yelp_shared_business.json
python tools/export_graph.py --graph outputs/yelp_5000.json --outdir outputs/yelp_exports
python tools/show_neighbors.py --graph outputs/yelp_5000.json --relation ABOUT
python tools/explain_edge.py --graph outputs/yelp_5000.json --schema yelp_schema_v2.json --data-root .. --relation ABOUT
```

From the earlier user's local 5,000-review run, the **recorded results** were 12,506 unique nodes and 10,000 typed edges (Review 5,000; User 4,843; Business 2,663); actual results must be checked on this run. The `p88_client_demo.py` command creates `outputs/client_demo_graph.html` and `outputs/yelp_shared_business.json`. Open `outputs/client_demo_graph.html` in Chrome. The verified example points two distinct reviews at the **one stored Business node**. Its sample proof and the separate all-stored-edge checker have different scopes.

If you extracted the files directly inside your P88 folder (beside `yelp_dataset/`), **omit `--data-root ..`** and change `--raw` to `yelp_dataset/yelp_academic_dataset_review.json`.

## 4. Run a LARGE SYNTHETIC DBLP-style reproducible scalability test

```powershell
python tools/make_synthetic_dblp.py --papers 5000
python hin_v2.py --schema dblp_synthetic_large_schema.json --output outputs/dblp_synthetic_5000.json
python tools/verify_edges.py --schema dblp_synthetic_large_schema.json --graph outputs/dblp_synthetic_5000.json
python tools/visualize_shared.py --graph outputs/dblp_synthetic_5000.json --relation AUTHORED_BY --target-type Author --output outputs/dblp_synthetic_large_graph.html
python tools/export_graph.py --graph outputs/dblp_synthetic_5000.json --outdir outputs/dblp_synthetic_exports
```

Creates thousands of records **artificially** with shared Author/Venue nodes and Paper→Paper citations. Its purpose is to demonstrate scaling and the same engine, **not to claim real DBLP processing**. Generated files are ignored by `.gitignore`.

## 5. Prepare and run a REAL DBLP sample from AMiner (when downloaded)

Source: [AMiner DBLP Citation Network datasets and V11/V13 schema](https://www.aminer.cn/aboutus/en-US/articles/655db2202ab17a072284bc0c). Download a V11/V13 **JSON or JSONL** paper dataset through the source's download links. The ZIP does **not** contain the giant DBLP dataset. If the available dataset uses a different version/schema (e.g., XML, V8 block text, or another provider), you must adjust the preparation step; don't assume compatibility.

Put the raw JSONL in any **local** folder, preferably `P88/dblp_raw/`. For example:

```powershell
python tools/normalize_dblp.py --input ../dblp_raw/dblp.v13.json --limit 5000 --outdir dblp_normalized
python tools/verify_dblp_raw.py --input ../dblp_raw/dblp.v13.json --normalized dblp_normalized
python hin_v2.py --schema dblp_real_schema.json --limit 50 --output outputs/dblp_real_50.json
python hin_v2.py --schema dblp_real_schema.json --limit 5000 --output outputs/dblp_real_5000.json
python tools/verify_edges.py --schema dblp_real_schema.json --graph outputs/dblp_real_5000.json --output outputs/dblp_real_verification.json
python tools/visualize_shared.py --graph outputs/dblp_real_5000.json --relation AUTHORED_BY --target-type Author --output outputs/dblp_real_shared_author.html
python tools/export_graph.py --graph outputs/dblp_real_5000.json --outdir outputs/dblp_real_exports
```

The normalization creates `dblp_normalized/papers.jsonl`, `authors.jsonl`, `venues.jsonl`, and a report. Paper IDs, author IDs, venue IDs and citation IDs are **read from real records, not generated from names**. The normalizer excludes citations whose target paper is not in the selected subset; it counts those exclusions. Some DBLP records may have no author or venue ID; the normalizer counts these cases rather than inventing identity. DBLP has multiple incompatible formats: **check the original file before running**.

### No real DBLP file available today? Test the normalization itself offline

```powershell
python tools/normalize_dblp.py --input demo_data/aminer_v13_format_SYNTHETIC_example.jsonl --limit 4 --outdir dblp_normalized
python tools/verify_dblp_raw.py --input demo_data/aminer_v13_format_SYNTHETIC_example.jsonl --normalized dblp_normalized
python hin_v2.py --schema dblp_real_schema.json --output outputs/dblp_nested_example.json
python tools/verify_edges.py --schema dblp_real_schema.json --graph outputs/dblp_nested_example.json
```

The four raw-style records in this fallback are explicitly **synthetic examples** of nested author/venue structures, not real publications. Run the **real DBLP normalization again** when you have the actual downloaded dataset before demonstrating claims about real data.

## 6. Where to look in the outputs

- `outputs/*.json` — metadata, unique typed node records, typed edge records with evidence, `adjacency`, `typed_adjacency`, `reverse_adjacency`.
- `outputs/client_demo_graph.html` — Yelp-specific two reviews sharing a Business, with sample raw verification.
- `outputs/dblp_*_graph.html` — two paper nodes sharing one Author, sourced from the actual **generated graph**.
- `outputs/*_exports/hin.graphml` — standard directed **GraphML graph format**, can open in Gephi.
- `outputs/*_exports/nodes.csv` and `edges.csv` — independently inspectable node/edge tables.
- `tools/show_neighbors.py` — typed incoming/outgoing graph lookup.
- `tools/verify_dblp_raw.py` — check normalization against the **original nested AMiner raw records**.
- `tools/verify_edges.py` — comparison of **every stored edge** against its schema-normalized source record reference. Checks provenance but cannot prove the chosen schema is semantically ideal.

## 7. Test suite

```powershell
python -m unittest discover -s tests -v
```

Tests use synthetic fixtures, including (i) shared Business deduplication, (ii) source-reference verification, (iii) GraphML export, (iv) nested AMiner-style author/venue normalization, and (v) DBLP-style paper-author edges. They do not replace testing on the downloaded real datasets.

## 8. Source → schema → HIN, in one minute

Input review `review_id=r1`, `user_id=u1`, `business_id=b1`. Schema says Review node ID=`review_id`, User ID=`user_id`, Business ID=`business_id` and Review.user_id has relation AUTHORED_BY to User, Review.business_id has ABOUT to Business. The builder uses unique dictionary keys `Review:r1`, `User:u1`, `Business:b1`; adds the two directed typed edges, and indexes neighbours. Another review with `business_id=b1` points at the existing Business node. `stars` and `date` are scalar attributes on Review, **not necessarily graph nodes**.

**Important accuracy:** Graphs with 2 node/edge types are heterogeneous due to their *different types*. JSON is merely the serialization of the graph; the typed edges and adjacency (and optional GraphML export) demonstrate the HIN. Every stored edge has evidence of its source record/field.

## 9. What is NOT finished and what team should decide

This is a credible final **proof of concept**, not a full original multi-source production system. It handles schema-driven JSON/JSONL, but **not** raw DBLP XML, RDF, automatic schema discovery, CSR, graph database integration, large-scale random sampling, or exhaustive schema correctness verification. A GraphML export is included, but this is not an in-memory NetworkX graph. The team should coordinate on the actual DBLP download/version, demo roles, client-meeting booking, presentation and these honest limitations.

See `docs/FINAL_DEMO_PLAN.md` and `docs/PSEUDOCODE.md` for a suggested final presentation.
