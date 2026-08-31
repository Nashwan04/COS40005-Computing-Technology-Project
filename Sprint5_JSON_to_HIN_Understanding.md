# Sprint 5 – Understanding the JSON to HIN Pipeline

## Purpose

This document records our current understanding of the Sprint 4 client feedback
and proposes a clearer direction for the next version of the HIN construction pipeline.

We do not need to restart the whole project from zero.

The main part that needs to be improved is how the system understands the source
JSON before building the HIN.

---

## Main Problem

Previously, dataset-specific information was moved from the Python code into a
configuration file.

For example:

- user_id -> Actor
- review_id -> Primary
- business_id -> Entity

This removes some hard-coding from the program, but the mapping is still manually
defined.

For a completely different dataset there may be no User, Review, Business,
Author or Paper.

Therefore, the program should not assume those concepts.

---

## New Direction

The pipeline should begin by understanding the source structure.

JSON Source
    ↓
Inspect JSON structure
    ↓
Identify object types
    ↓
Identify possible IDs
    ↓
Identify references between objects
    ↓
Determine node types
    ↓
Determine relationship types
    ↓
Create node instances
    ↓
Create edges
    ↓
Construct HIN

The important transformation is:

Hierarchical JSON -> Graph-based HIN

---

## JSON Structure

JSON stores data using key-value pairs.

Example:

{
    "review_id": "R1",
    "user_id": "U1",
    "business_id": "B1",
    "stars": 5
}

Possible JSON value types include:

- string
- number
- boolean
- null
- array
- object

`review_id` is a key.

`R1` is its value.

JSON itself does not define SQL-style primary keys.

A field may be treated as an identifier if its values uniquely identify objects.

---

## Node Type and Node Instance

Node Type = category of object.

Examples:

User
Review
Business
Author
Paper

Node Instance = one actual object belonging to that type.

Examples:

User:U1
Review:R1
Business:B1

Therefore:

Node Type     = Review
Node Instance = Review:R1
Identifier    = R1

---

## Finding Relationships

Example source objects:

User:

{
    "user_id": "U1",
    "name": "John"
}

Review:

{
    "review_id": "R1",
    "user_id": "U1",
    "business_id": "B1"
}

Business:

{
    "business_id": "B1",
    "name": "Cafe One"
}

The Review contains:

user_id = U1

The User object has:

user_id = U1

Therefore the values create a reference between the two objects.

Possible HIN edge:

User:U1 -> Review:R1

Similarly:

Review.business_id = B1

matches:

Business.business_id = B1

Therefore:

Review:R1 -> Business:B1

Once the semantic relationship is known:

User:U1 --WROTE--> Review:R1
Review:R1 --ABOUT--> Business:B1

---

# Proposed Pipeline

## Step 1 – Read the Source

For large JSON files, stream the data instead of loading everything into memory.

FOR each JSON record:
    read record
    inspect record structure

---

## Step 2 – Inspect Objects

For every object:

    collect its keys
    identify value datatypes
    identify arrays
    identify nested objects
    record field frequency
    record field uniqueness
    record sample values

Example:

review_id   string
user_id     string
business_id string
stars       number

---

## Step 3 – Find Candidate Object Types

Objects with similar structures can be grouped.

Example:

Objects containing:

review_id
user_id
business_id
stars

may belong to the same object type.

The program does not initially need to call it "Review".

It could internally represent it as:

Type_1

until the schema gives it a meaningful name.

---

## Step 4 – Find Candidate Identifiers

For each object type:

IF a field appears in most objects
AND its values are mostly unique
THEN mark it as a candidate identifier.

Example:

review_id -> possible identifier
user_id   -> possible identifier

---

## Step 5 – Find References

Compare fields from one object type with identifier values from another.

Example:

Type_1.user_id values

match

Type_2.user_id identifier values

Therefore:

Type_1 references Type_2

This becomes a candidate graph relationship.

---

## Step 6 – Build Schema Information

Example:

Node Type: Type_1
ID Field: review_id

Node Type: Type_2
ID Field: user_id

Node Type: Type_3
ID Field: business_id

Relationships:

Type_1.user_id -> Type_2.user_id
Type_1.business_id -> Type_3.business_id

---

# Schema Fallback

If automatic schema discovery is too difficult initially, we can assume that
each JSON source is supplied with a matching schema.

The important point is that the program reads the schema dynamically.

It should NOT contain code such as:

if dataset == "Yelp":
    create_user()
    create_review()
    create_business()

Instead:

schema = load_schema()

FOR each node type defined in schema:
    create nodes

FOR each relationship defined in schema:
    create edges

This means another dataset can use a different schema without changing the program.

---

# Generic HIN Construction Pseudocode

FUNCTION construct_HIN(json_sources, schema):

    graph = empty graph

    FOR each node_type in schema.node_types:

        source = node_type.source
        id_field = node_type.id_field

        FOR each object in stream(source):

            object_id = object[id_field]

            IF object_id is missing:
                CONTINUE

            node_id = node_type.name + ":" + object_id

            IF node does not already exist:
                CREATE node

    FOR each relationship in schema.relationships:

        FOR each source object:

            reference_value =
                source_object[relationship.reference_field]

            target =
                find target object whose ID equals reference_value

            IF target exists:

                CREATE typed edge
                between source node and target node

    RETURN graph

---

# Optional Schema Discovery

FUNCTION discover_schema(json_sources):

    FOR each JSON source:

        sample objects

        FOR each object:

            record keys
            record datatypes
            record uniqueness
            record frequencies

    group objects with similar structures

    FOR each object group:

        identify candidate ID field

        CREATE candidate node type

    FOR each pair of node types:

        compare fields of first type
        with IDs of second type

        IF values strongly overlap:

            CREATE candidate relationship

    RETURN discovered schema

---

# Small Yelp Example

Input:

User:
{"user_id":"U1","name":"John"}

Review:
{"review_id":"R1","user_id":"U1","business_id":"B1"}

Business:
{"business_id":"B1","name":"Cafe One"}

Schema:

Node Types:
User
Review
Business

IDs:

User.user_id
Review.review_id
Business.business_id

References:

Review.user_id -> User.user_id
Review.business_id -> Business.business_id

HIN:

User:U1
   |
 WROTE
   |
   v
Review:R1
   |
 ABOUT
   |
   v
Business:B1

---

# What We Can Reuse

We do not need to restart Sprint 3 and Sprint 4 completely.

We can still reuse:

- NetworkX graph construction
- unique node handling
- edge creation
- JSON streaming
- graph export
- validation
- later projection work

The main redesign is at the beginning of the pipeline.

OLD:

Manual Actor / Primary / Entity mapping
        ↓
Build HIN

NEW:

Understand source/schema
        ↓
Determine node types
        ↓
Determine IDs
        ↓
Determine references
        ↓
Build HIN

---

# Next Practical Tasks

1. Extract a very small Yelp sample.

2. Write a JSON structure inspection function.

3. Print:
   - field name
   - datatype
   - occurrence count
   - uniqueness
   - sample values

4. Detect candidate ID fields.

5. Compare fields between JSON object types.

6. Detect possible references.

7. Generate a simple schema.

8. Build a small HIN using that schema.

---

# Current Understanding

The biggest issue is not the size of the Yelp dataset.

The important problem is understanding the source structure and demonstrating
how hierarchical JSON information is transformed into nodes and relationships
in a Heterogeneous Information Network.

JSON structure
    ↓
Schema
    ↓
Node Types
    ↓
Node Instances
    ↓
Relationships
    ↓
HIN