# P88 HIN v2 – explainable schema-driven prototype

## Run from the P88 project folder
Extract this archive **into** `D:\Swinburne Last Semester\P88` so that `hin_v2.py`, both schema files, `demo_data/` and the existing `yelp_dataset/` are directly inside P88.

No external Python libraries required.

Demo (small, synthetic DBLP-style data):
`python hin_v2.py --schema dblp_schema_example.json --output demo_graph.json`

Real Yelp sample (5000 reviews):
`python hin_v2.py --schema yelp_schema_v2.json --limit 5000 --output hin_yelp_v2.json`

## How to explain
- `entities` defines which raw record types are nodes, their identifier fields and ordinary attributes.
- `relationships` defines which source field references an instance of another type. This supplies the semantic edge name; JSON alone does not.
- Nodes are stored in a dictionary keyed by `Type:ID`. Repeated references point to one node.
- Edges are explicit `source`, `target`, `relation` records with `evidence` pointing to the source record/field.
- `adjacency` groups all outgoing typed edges by source node.
- Output includes counts, checks and warnings. Warnings must be reviewed: successful structural checks do NOT prove semantic correctness.
- Demo: `Paper:P2` and `Paper:P3` each link to both `Author:A1` and `Author:A2`; paper nodes are not duplicated.

## Honest scope and limitations
- This is a **prototype**, not a completed multi-format or automatic-schema-discovery solution.
- Handles JSONL streaming and JSON arrays (arrays loaded fully). The selected primary sample is kept in memory.
- Non-primary files are scanned for matching referenced IDs; large Yelp files may take time.
- Handles explicit forward references; nested JSON paths and reverse-only references are not supported yet.
- A schema is supplied by a human; the engine does not infer correct semantics from raw JSON.
- Yelp schema intentionally keeps date, stars, city, state and categories as attributes rather than automatically making nodes.
- DBLP files in `demo_data/` are synthetic and NOT the real DBLP dataset; adapt schema to real DBLP before claiming DBLP support.
- Output includes adjacency and edges, but is not CSR and does not automatically draw a network diagram.
- Does not replace the existing `hin_pipeline.py`; compare and review both with the team.
