# HIN Pipeline Redesign - Semester 2

## Current Limitation

The Sprint 3 implementation successfully creates a graph-based HIN, but the current code is still closely tied to Yelp-specific fields such as:

- user_id
- review_id
- business_id
- stars
- date

The next stage is to make the pipeline more reusable so the same methodology can be applied to other semi-structured datasets.

## General Input

JSON, XML, RDF or another semi-structured dataset.

## General Output

A Heterogeneous Information Network containing:

- node types
- unique node IDs
- relationship types
- typed edges
- graph validation results

## Proposed General Pipeline

1. Load the raw dataset.
2. Inspect available fields.
3. Define node types using a schema/configuration.
4. Map source fields to node IDs and attributes.
5. Create unique nodes.
6. Create typed relationships between nodes.
7. Remove or reuse duplicate entities.
8. Validate the graph structure.
9. Export the HIN.

## Planned Code Improvements

- Move dataset-specific settings into a configuration file.
- Create a generic `create_node()` function.
- Create a generic `create_edge()` function.
- Separate schema definitions from graph-building logic.
- Improve validation.
- Test the same methodology against another dataset such as DBLP.

## Example Mapping

| General Role | Yelp | DBLP |
|---|---|---|
| Actor | User | Author |
| Main entity | Review | Paper |
| Target/context | Business | Venue |
| Attributes | Rating, Date | Year, Topic |

This mapping will help demonstrate that the HIN construction methodology is not limited to Yelp.