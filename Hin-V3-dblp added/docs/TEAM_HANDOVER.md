# P88 team handover / GitHub branch checklist

## Recommended plan for Friday's final client interaction

- Confirm the actual client meeting time and who can speak. Someone should ensure Dr. Lu Chen receives the meeting link/time.
- Assign a reviewer to confirm DBLP source dataset format. The team must choose **AMiner JSON V11/V13** if using the included DBLP normalizer; a DBLP XML file or AMiner V8 blocks will not work unchanged.
- One person reviews `hin_v2.py`/schema/pseudocode; one tests Yelp; one handles DBLP (raw sample, converter, 50 and 5000 tests); one handles documentation/QA.
- Publish **source code and small synthetic fixture data only**, ideally to a reviewable feature branch.
- At least two people independently run the demo commands and verify that all screenshots reflect the actual output.
- Keep a short test log: date, commit SHA, dataset version, `--limit`, node/edge breakdown, warnings, validation result.

## Uploading to GitHub Desktop

1. Open the team's existing GitHub repository and select/create your new branch.
2. Copy this folder into the repo (e.g., `HIN_Final_Demo/`).
3. Its `.gitignore` protects local large data and `outputs/` underneath this folder. If the repo contains raw datasets outside this folder, separately ignore those in the repo root.
4. Review GitHub Desktop's Changes list. **Only stage** scripts, schemas, `demo_data/*.jsonl` small examples, `tests`, `docs`, README, and optionally final `.pptx`.
5. Do **not** commit large generated DBLP sample, Yelp raw JSON, ZIP archives or generated output JSON.
6. Commit and push/publish your branch; share the link in Discord. Do not merge without the team's review.

## Suggested Discord summary

> Hi team, I prepared a final HIN demonstration package based on the recent professor/client feedback. It includes the source→schema→graph pseudocode, an updated schema-driven pipeline with typed adjacency, graph verification against source references, GraphML/CSV exports and two small DBLP-style demonstrations. I also added a normalizer for **AMiner DBLP V11/V13 JSON** and a 5,000-paper **synthetic** large-scale test. To demonstrate **real DBLP** we still need the actual downloaded dataset and must run the 50- and 5,000-paper tests with it. Please check the README and run the commands on your machines, review the code, and confirm the Friday meeting time and presenters. We need to show small and large results clearly and be honest about what's still incomplete.
