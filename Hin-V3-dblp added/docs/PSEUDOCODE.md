# P88 HIN construction — displayable pseudocode (matches the Python implementation)

## A. Whole-system overview

```text
INPUT:
    Source JSON/JSONL files
    External schema (node types, unique identifier fields, source files,
                     attribute fields and reference-to-relation rules)
    Maximum number of primary records (optional)

OUTPUT:
    HIN containing:
        nodes: dictionary keyed by "Type:SourceID" (unique typed entities)
        edges: list of (source, target, relation, source_evidence)
        adjacency: outgoing list for each source
        typed_adjacency: outgoing targets grouped by relation type
        reverse_adjacency: incoming sources grouped by relation type
        validation metadata

PROCEDURE BuildHIN(schema, source_directory, limit):
    validate that schema names a primary entity type
    sample first LIMIT records of the primary entity, if limit specified
    find referenced IDs of non-primary entity types from the sample

    for each selected primary source record:
        id = primary_record[primary_entity.id_field]
        add NODE only if (type, id) does not exist
        attach scalar attributes specified by the schema

    for each non-primary entity type:
        scan its source JSON file
        keep only source records whose IDs are referenced by the sample
        add NODE only if (type, id) does not already exist

    for each relationship rule in schema:
        examine selected source records of its source entity type
        obtain referenced target ID(s) from rule.reference_field
        for each target ID:
            if source and target nodes exist:
                add typed EDGE(source, target, rule.relation_type)
                record evidence of original source type, record ID,
                field name and referenced ID
                skip identical duplicate edges
            else:
                increment unresolved_reference warning

    for each constructed edge:
        adjacency[source].append((target, relation))
        typed_adjacency[source][relation].append(target)
        reverse_adjacency[target][relation].append(source)

    check node ID uniqueness, endpoint existence, valid node types,
    and declared relationship types
    return HIN (nodes, edges, 3 adjacency views, counts, checks, warnings)
```

## B. DBLP normalization before the same builder (AMiner V11/V13 only)

```text
PROCEDURE Normalize_AMiner_DBLP(raw_paper_json, max_papers):
    stream the raw paper JSON records (JSON Lines or JSON array)
    for each paper until max_papers have valid distinct paper IDs:
        store Paper(paper.id, title, year)
        for each author object in paper.authors:
            if author.id is present:
                store unique Author(author.id, author.name)
                add author.id to paper.author_ids
            else:
                record a missing-ID warning (do NOT guess identity from name)
        if paper.venue.id exists:
            store unique Venue(venue.id, venue.raw)
            set paper.venue_id
        store raw paper.references for later filtering

    let sampled_paper_ids be the set of selected paper IDs
    for each selected Paper:
        retain citation IDs only when the referenced paper is also selected
        count references outside the sampled subset as excluded

    write normalized papers.jsonl, authors.jsonl, venues.jsonl
    write normalization report with any missing/excluded-reference counts
    apply the SAME BuildHIN procedure with dblp_real_schema.json
```

## C. Check every stored edge against the source file

```text
PROCEDURE VerifyEdges(output_hin, schema):
    for each stored edge:
        assert source and target node IDs exist
        assert edge direction, type and reference field match schema
        assert edge's target ID equals its source-reference value
    fetch each source record referred to by an edge from input JSON
    for each edge:
        assert the evidence reference_field value in the raw source record
               contains the expected evidence reference_value
    report checked edges, first failures and PASS/FAIL
```

Verification of all **stored** edges is stronger than only validating a couple of examples, but it does **not** establish that the schema itself captures every meaningful relationship or that the selected input sample is representative.

## D. Worked Yelp trace (illustrative IDs)

```text
INPUT REVIEW: {review_id: "r1", user_id: "u1", business_id: "b1", stars: 5}
SCHEMA: Review(review_id), User(user_id), Business(business_id)
RULES: Review.user_id --AUTHORED_BY--> User
       Review.business_id --ABOUT--> Business

NODES: Review:r1, User:u1, Business:b1
EDGES: Review:r1 --AUTHORED_BY--> User:u1
       Review:r1 --ABOUT-------> Business:b1
```

If another source review references `business_id=b1`, it points to **the same stored** Business:b1 node. Stars/date remain ordinary attributes rather than automatically becoming extra node types.

## E. Worked DBLP trace (illustrative IDs)

```text
RAW PAPER (V13-style):
  id: "p2"
  authors: [{id:"a1",name:"Alex"}, {id:"a2",name:"Bea"}]
  venue: {id:"v1",raw:"Example Venue"}
  references: ["p1"]

NORMALIZED PAPER: paper_id:"p2", author_ids:["a1","a2"],
                  venue_id:"v1", reference_ids:["p1"]

NODES: Paper:p2, Author:a1, Author:a2, Venue:v1, Paper:p1
EDGES: Paper:p2 --AUTHORED_BY--> Author:a1
       Paper:p2 --AUTHORED_BY--> Author:a2
       Paper:p2 --PUBLISHED_IN--> Venue:v1
       Paper:p2 --CITES--------> Paper:p1
```

**Key professor question:** The nested author `id`, venue `id` and paper `references` provide explicit referential evidence for graph edges. A paper's `year` is an attribute unless a task requires treating years as entities.

## F. Actual source code location

- `hin_v2.py` → `records()` and `build()` — core source→graph transformation.
- `hin_v2.py` → `add_node()` — unique typed node insertion.
- `hin_v2.py` → `edges.append(...)` — typed source–target–relation construction with evidence.
- `hin_v2.py` → `typed_adjacency` and `reverse_adjacency` — queryable connections.
- `tools/normalize_dblp.py` → `normalize()` — nested DBLP normalization.
- `tools/verify_dblp_raw.py` → `run()` — independent original DBLP raw→normalized ID/reference check.
- `tools/verify_edges.py` → `verify()` — independent provenance/reference check against the prepared source files.
- `tools/export_graph.py` → `export()` — GraphML and CSV graph representations.

## G. Honest algorithm boundaries

- Only declared reference fields create edges. Undeclared field names do **not** automatically imply relationships.
- The schema is human supplied; automatic schema discovery is not part of the current engine.
- `limit` selects the **first N** primary entities; it is not random or stratified sampling.
- `source_record -> field -> target` is required for constructing an edge. It is not safe to assume a relationship merely because two names look alike.
- The current `nodes` dict, `edges` list and adjacencies are Python objects; exported JSON/GraphML represent the constructed graph on disk. No NetworkX or CSR is used in this version.
