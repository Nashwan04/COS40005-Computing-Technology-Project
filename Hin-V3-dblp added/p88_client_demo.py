"""P88: demonstrate a shared Business node and verify two Yelp relationships.

Run: python p88_client_demo.py --graph hin_yelp_v2.json
Prints a compact, real example and saves client_demo_subgraph.json.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from html import escape


def main():
    parser = argparse.ArgumentParser(description="Trace two Yelp reviews to one shared Business node")
    parser.add_argument("--graph", default="hin_yelp_v2.json")
    parser.add_argument("--raw", default="yelp_dataset/yelp_academic_dataset_review.json")
    parser.add_argument("--output", default="client_demo_subgraph.json")
    args = parser.parse_args()

    graph = json.loads(Path(args.graph).read_text(encoding="utf-8-sig"))
    nodes = {node["id"]: node for node in graph["nodes"]}
    by_business = defaultdict(list)
    author = {}
    for edge in graph["edges"]:
        if edge["relation"] == "ABOUT" and edge["source"].startswith("Review:"):
            by_business[edge["target"]].append(edge)
        elif edge["relation"] == "AUTHORED_BY" and edge["source"].startswith("Review:"):
            author[edge["source"]] = edge

    candidates = sorted(
        ((business, edges) for business, edges in by_business.items() if len(edges) >= 2),
        key=lambda pair: (-len(pair[1]), pair[0]),
    )
    if not candidates:
        raise SystemExit("No business with 2+ reviews found. Run the 5000-review graph, not the 50-review sample.")

    business, about_edges = candidates[0]
    selected_about = about_edges[:2]
    review_nodes = [e["source"] for e in selected_about]
    raw_ids = {review.split(":", 1)[1] for review in review_nodes}
    raw = {}
    with Path(args.raw).open(encoding="utf-8-sig") as source:
        for line in source:
            if not line.strip():
                continue
            item = json.loads(line)
            if str(item.get("review_id")) in raw_ids:
                raw[str(item["review_id"])] = item
                if len(raw) == len(raw_ids):
                    break

    selected_edges = []
    selected_node_ids = {business, *review_nodes}
    checks = []
    print("\n=== P88 CLIENT DEMO: SHARED BUSINESS NODE ===")
    print("Business:", business)
    print("Number of ABOUT edges pointing at this single Business node:", len(about_edges))
    print("Unique Business node in graph:", business in nodes)
    for e in selected_about:
        review = e["source"]
        identifier = review.split(":", 1)[1]
        raw_review = raw.get(identifier)
        a = author.get(review)
        if not raw_review or not a:
            checks.append(False)
            print("ERROR: Missing raw review or AUTHOR edge for", review)
            continue
        expected_user = "User:" + str(raw_review["user_id"])
        expected_business = "Business:" + str(raw_review["business_id"])
        ok = (a["target"] == expected_user and e["target"] == expected_business)
        checks.append(ok)
        selected_edges.extend((a, e))
        selected_node_ids.add(a["target"])
        print("\nRAW REVIEW:", identifier)
        print("  raw user_id:", raw_review["user_id"])
        print("  raw business_id:", raw_review["business_id"])
        print("CONSTRUCTED RELATIONSHIPS:")
        print(" ", review, "--AUTHORED_BY-->", a["target"])
        print(" ", review, "--ABOUT-->", e["target"])
        print("RAW-TO-GRAPH CHECK:", "PASS" if ok else "FAIL")

    result = {
        "description": "Two reviews pointing to the same business; their raw Yelp references checked.",
        "shared_business": business,
        "total_reviews_for_shared_business": len(about_edges),
        "raw_reference_checks_pass": len(checks) == 2 and all(checks),
        "nodes": [nodes[i] for i in sorted(selected_node_ids) if i in nodes],
        "edges": selected_edges,
    }
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    # Optional human-readable diagram: saved beside the compact JSON proof.
    if result["raw_reference_checks_pass"]:
        a1, b1, a2, b2 = selected_edges
        def short(s):
            kind, _, val = s.partition(":")
            return escape(kind + ":" + (val[:13] + "..." if len(val) > 13 else val))
        def box(node_id, x, y, color):
            return (f'<rect x="{x}" y="{y}" width="240" height="62" rx="12" fill="{color}"/>'
                    f'<text x="{x + 120}" y="{y + 36}" text-anchor="middle" font-size="17" fill="white">{short(node_id)}</text>'
                    f'<title>{escape(node_id)}</title>')
        diagram = f'''<!doctype html><html><head><meta charset="utf-8"><title>P88 HIN proof</title>
<style>body{{font:16px system-ui;margin:24px;background:#f8fafc;color:#0f172a}}
section{{max-width:980px;margin:auto;background:white;border:1px solid #cbd5e1;border-radius:16px;padding:26px}}
svg{{width:100%;height:auto}}p{{line-height:1.5}}</style></head><body><section>
<h1>P88 HIN: Two reviews share one Business</h1>
<p>Each Review is stored once. Both reviews point to the same Business node. Hover a node to see its full ID.</p>
<svg viewBox="0 0 900 340" role="img" aria-label="Two different Reviews each link to a User, and both link to the same Business">
<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 Z" fill="#64748b"/></marker></defs>
<g stroke="#64748b" stroke-width="2.2" fill="none" marker-end="url(#arr)">
<path d="M330 86 L260 86"/><path d="M330 240 L260 240"/>
<path d="M570 86 L650 158"/><path d="M570 240 L650 190"/>
</g>
{box(a1['target'], 20, 55, '#2563eb')}
{box(a2['target'], 20, 209, '#2563eb')}
{box(a1['source'], 330, 55, '#0d9488')}
{box(a2['source'], 330, 209, '#0d9488')}
{box(business, 650, 143, '#7c3aed')}
<g font-size="12" fill="#334155"><text x="278" y="74">AUTHORED_BY</text><text x="278" y="228">AUTHORED_BY</text><text x="583" y="105">ABOUT</text><text x="583" y="231">ABOUT</text></g>
</svg>
<h2>Raw JSON verification: PASS</h2>
<p>Both Review → User and Review → Business edges were compared against actual <code>user_id</code> and <code>business_id</code> values in the raw Yelp review records.</p>
<p><strong>Note:</strong> This verifies two example edges, not every relationship in the complete dataset.</p>
</section></body></html>'''
        html_path = Path(args.output).with_name("client_demo_graph.html")
        html_path.write_text(diagram, encoding="utf-8")
        print("Saved visual diagram:", html_path)
    print("\nSaved small proof:", args.output)
    print("FINAL RESULT:", "PASS" if result["raw_reference_checks_pass"] else "FAIL")
    if not result["raw_reference_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
