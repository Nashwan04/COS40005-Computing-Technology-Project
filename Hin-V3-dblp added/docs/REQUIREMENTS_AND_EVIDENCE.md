# Supervisor/client requirements → concrete evidence and current status

| Asked for | Where to demonstrate | Status in this package | Qualification |
|---|---|---|---|
| Source files and references | Raw Yelp review `review_id/user_id/business_id`; original AMiner paper `id/authors[].id/venue.id/references` | Supported | Real DBLP requires separate download |
| Schema showing nodes vs attributes | `yelp_schema_v2.json`, `dblp_real_schema.json` | Working | Supplied manually, not discovered |
| Show pseudocode | `docs/PSEUDOCODE.md` and matching `hin_v2.py` sections | Complete | Pseudocode reflects this prototype, not full original course requirements |
| Generate HIN from raw+schema | `hin_v2.py`, `tools/normalize_dblp.py` for nested DBLP | Working on tested fixtures | Yelp earlier local test should be rerun live |
| Genuine graph structures, not JSON reformat | `nodes`, `edges`, `typed_adjacency`, `reverse_adjacency` | Complete | JSON is output serialization; GraphML also exported |
| Unique shared nodes | Two reviews share Business or two papers share Author | Demonstrated on synthetic fixtures and earlier local Yelp | Verify actual Yelp sample HTML before claiming |
| Small and large examples | DBLP 4 papers / 5000 synthetic papers, Yelp 50 / 5000 real reviews | DBLP synthetic tests verified | Real DBLP 50/5000 requires raw dataset |
| Verify DBLP normalization against original nested raw IDs | `tools/verify_dblp_raw.py` | Passing on shipped nested-format fixture | Needs a rerun against downloaded real DBLP |
| Verify relations against source IDs | `tools/verify_edges.py` | Passing on shipped tests | Checks stored edges against normalized source records, not semantics of undeclared relationships |
| Graph export | `tools/export_graph.py` | Verified GraphML + CSV | No database/CSR export |
| Source-independent design | Same `hin_v2.py` engine across schemas | Tested for Yelp-style and normalized DBLP-style fixtures | Source preparation remains format-specific |
| Fully automatic schema from JSON | Not implemented | Missing | Professor said supplied schema acceptable at current stage |
| XML/RDF import | Not implemented | Missing | Do not claim completion |
| Original complete DBLP dataset | Official AMiner source link in README | Not bundled | Download/execute/verify before presentation |

## Verified here (synthetic only unless noted)

- Yelp-format 3-review **synthetic** fixture: **7 nodes, 6 edges**, all 6 independently verified, two reviews share one Business node.
- Original four-paper synthetic DBLP-style sample: **8 nodes, 10 edges**, all 10 stored relationships independently verified.
- Nested AMiner-V13-structured synthetic example: **9 nodes, 16 edges** including 4 CITES edges; all 16 verified.
- Generated 5,000-paper synthetic DBLP-scale sample: **5,466 nodes, 19,999 edges**; all 19,999 stored relationships verified.
- Yelp prior run reported **12,506 nodes, 10,000 edges** from 5,000 real reviews. **Not rerun in this package** because raw Yelp dataset is large and not present here.

## What you should bring to the meeting

1. The correct source data on your own machine (do not push raw Yelp or DBLP files).
2. Screenshots of commands and metadata results, with actual date and dataset provenance.
3. Visual shared-node HTML and source-backed verification output.
4. Pseudocode and a real source record + external schema.
5. Clear explanation of limitations and which parts were contributed by which teammates.
