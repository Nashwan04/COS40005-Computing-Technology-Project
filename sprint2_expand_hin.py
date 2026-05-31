import json
import csv
import os

# ── CONFIG ────────────────────────────────────────────────────────────────────
BUSINESS_FILE = r"C:\Users\jacob\Downloads\p88\Yelp JSON\yelp_dataset\yelp_academic_dataset_business.json"
REVIEW_FILE   = r"C:\Users\jacob\Downloads\p88\Yelp JSON\yelp_dataset\yelp_academic_dataset_review.json"
USER_FILE     = r"C:\Users\jacob\Downloads\p88\Yelp JSON\yelp_dataset\yelp_academic_dataset_user.json"
OUTPUT_DIR    = r"C:\Users\jacob\Downloads\p88\Yelp JSON\output"
LIMIT         = 1000
# ─────────────────────────────────────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_jsonl(filepath, limit=1000):
    """Read first `limit` lines from a JSON-lines file."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            line = line.strip()
            if line:
                records.append(json.loads(line))
    print(f"  Loaded {len(records)} records from {os.path.basename(filepath)}")
    return records

def write_csv(filepath, fieldnames, rows):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved {len(rows)} rows → {os.path.basename(filepath)}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Load data
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1] Loading datasets...")
businesses = load_jsonl(BUSINESS_FILE, LIMIT)
reviews    = load_jsonl(REVIEW_FILE,   LIMIT)
users      = load_jsonl(USER_FILE,     LIMIT)

# Build quick lookup sets so we only keep reviews/users that link to
# businesses we actually loaded.
business_ids = {b["business_id"] for b in businesses}
user_ids_in_reviews = {r["user_id"] for r in reviews if r["business_id"] in business_ids}


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Build nodes
# ══════════════════════════════════════════════════════════════════════════════
print("\n[2] Building nodes...")

# ── Business nodes (carry over from Sprint 1) ────────────────────────────────
business_nodes = []
for b in businesses:
    business_nodes.append({
        "node_id":   b["business_id"],
        "node_type": "Business",
        "name":      b.get("name", ""),
        "city":      b.get("city", ""),
        "state":     b.get("state", ""),
        "stars":     b.get("stars", ""),
    })

# ── User nodes ───────────────────────────────────────────────────────────────
user_nodes = []
seen_users = set()
for u in users:
    if u["user_id"] in user_ids_in_reviews and u["user_id"] not in seen_users:
        user_nodes.append({
            "node_id":        u["user_id"],
            "node_type":      "User",
            "name":           u.get("name", ""),
            "review_count":   u.get("review_count", 0),
            "average_stars":  u.get("average_stars", 0),
        })
        seen_users.add(u["user_id"])

# ── Review nodes ─────────────────────────────────────────────────────────────
review_nodes = []
for r in reviews:
    if r["business_id"] not in business_ids:
        continue
    review_nodes.append({
        "node_id":     r["review_id"],
        "node_type":   "Review",
        "stars":       r.get("stars", ""),
        "useful":      r.get("useful", 0),
        "date":        r.get("date", ""),
    })


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Build edges
# ══════════════════════════════════════════════════════════════════════════════
print("\n[3] Building edges...")

# ── From Sprint 1: Business → Category, City, State ─────────────────────────
category_nodes = {}
city_nodes     = {}
state_nodes    = {}

biz_cat_edges   = []
biz_city_edges  = []
city_state_edges = []

for b in businesses:
    bid = b["business_id"]

    # categories
    cats = b.get("categories") or ""
    for cat in [c.strip() for c in cats.split(",") if c.strip()]:
        cid = f"cat_{cat.lower().replace(' ', '_')}"
        category_nodes[cid] = cat
        biz_cat_edges.append({"src": bid, "dst": cid, "relation": "IN_CATEGORY"})

    # city
    city  = b.get("city", "").strip()
    state = b.get("state", "").strip()
    if city:
        cid = f"city_{city.lower().replace(' ', '_')}"
        city_nodes[cid] = city
        biz_city_edges.append({"src": bid, "dst": cid, "relation": "LOCATED_IN"})
        if state:
            sid = f"state_{state.lower()}"
            state_nodes[sid] = state
            city_state_edges.append({"src": cid, "dst": sid, "relation": "IN_STATE"})

# ── NEW Sprint 2: User → WROTE → Review → REVIEWS → Business ────────────────
user_wrote_review   = []
review_reviews_biz  = []

for r in reviews:
    if r["business_id"] not in business_ids:
        continue
    user_wrote_review.append({
        "src": r["user_id"], "dst": r["review_id"], "relation": "WROTE"
    })
    review_reviews_biz.append({
        "src": r["review_id"], "dst": r["business_id"], "relation": "REVIEWS"
    })


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Save everything to CSV
# ══════════════════════════════════════════════════════════════════════════════
print("\n[4] Saving output files...")

# nodes
write_csv(f"{OUTPUT_DIR}/nodes_business.csv",
          ["node_id","node_type","name","city","state","stars"], business_nodes)

write_csv(f"{OUTPUT_DIR}/nodes_user.csv",
          ["node_id","node_type","name","review_count","average_stars"], user_nodes)

write_csv(f"{OUTPUT_DIR}/nodes_review.csv",
          ["node_id","node_type","stars","useful","date"], review_nodes)

write_csv(f"{OUTPUT_DIR}/nodes_category.csv",
          ["node_id","node_type","name"],
          [{"node_id": k, "node_type": "Category", "name": v} for k,v in category_nodes.items()])

write_csv(f"{OUTPUT_DIR}/nodes_city.csv",
          ["node_id","node_type","name"],
          [{"node_id": k, "node_type": "City", "name": v} for k,v in city_nodes.items()])

write_csv(f"{OUTPUT_DIR}/nodes_state.csv",
          ["node_id","node_type","name"],
          [{"node_id": k, "node_type": "State", "name": v} for k,v in state_nodes.items()])

# edges
all_edges = (biz_cat_edges + biz_city_edges + city_state_edges +
             user_wrote_review + review_reviews_biz)

write_csv(f"{OUTPUT_DIR}/edges_all.csv",
          ["src","dst","relation"], all_edges)

# also save new Sprint 2 edges separately (useful for report evidence)
write_csv(f"{OUTPUT_DIR}/edges_user_wrote_review.csv",
          ["src","dst","relation"], user_wrote_review)

write_csv(f"{OUTPUT_DIR}/edges_review_reviews_business.csv",
          ["src","dst","relation"], review_reviews_biz)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Basic analysis / queries (new in Sprint 2)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[5] Running basic analysis...")

# Top 5 highest rated businesses (avg stars from reviews)
from collections import defaultdict

biz_stars = defaultdict(list)
for r in reviews:
    if r["business_id"] in business_ids:
        biz_stars[r["business_id"]].append(r.get("stars", 0))

biz_avg = {bid: sum(s)/len(s) for bid, s in biz_stars.items()}
top5 = sorted(biz_avg.items(), key=lambda x: x[1], reverse=True)[:5]

biz_name_map = {b["business_id"]: b.get("name","?") for b in businesses}

print("\n  Top 5 businesses by average review stars:")
for bid, avg in top5:
    print(f"    {biz_name_map.get(bid,'?'):<40}  avg stars: {avg:.2f}")

# Most active users (by review count in subset)
user_review_count = defaultdict(int)
for r in reviews:
    if r["business_id"] in business_ids:
        user_review_count[r["user_id"]] += 1

top_users = sorted(user_review_count.items(), key=lambda x: x[1], reverse=True)[:5]
user_name_map = {u["user_id"]: u.get("name","?") for u in users}

print("\n  Top 5 most active users in subset:")
for uid, count in top_users:
    print(f"    {user_name_map.get(uid, uid[:8]+'...'):<30}  reviews: {count}")


# ══════════════════════════════════════════════════════════════════════════════
print("\n✅ Sprint 2 complete.")
print(f"   Business nodes : {len(business_nodes)}")
print(f"   User nodes     : {len(user_nodes)}")
print(f"   Review nodes   : {len(review_nodes)}")
print(f"   Total edges    : {len(all_edges)}")
print(f"\n   All files saved to: {OUTPUT_DIR}/")
