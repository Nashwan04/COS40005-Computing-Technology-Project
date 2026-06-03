# COS40005-Computing-Technology-Project

## Project P88 - Constructing Information Networks from Device Data Sources

This project works with the Yelp Open Dataset and converts raw JSON data into a basic Heterogeneous Information Network (HIN) structure.

## Dataset

Dataset used: Yelp Open Dataset  
Link: https://business.yelp.com/data/resources/open-dataset/

The code uses these three JSON files from the Yelp dataset:

- `yelp_academic_dataset_business.json`
- `yelp_academic_dataset_review.json`
- `yelp_academic_dataset_user.json`

These files are used to create graph nodes and relationships.

## What the Code Does

The file `sprint2_expand_hin.py` reads the Yelp JSON files and creates HIN output files.

It creates node types such as:

- Business
- User
- Review
- Category
- City
- State

It also creates relationship types such as:

- Business → IN_CATEGORY → Category
- Business → LOCATED_IN → City
- City → IN_STATE → State
- User → WROTE → Review
- Review → REVIEWS → Business

## How to Use

1. Download the Yelp Open Dataset from the link above.
2. Extract the dataset folder.
3. Make sure these files are available:

```text
yelp_academic_dataset_business.json
yelp_academic_dataset_review.json
yelp_academic_dataset_user.json