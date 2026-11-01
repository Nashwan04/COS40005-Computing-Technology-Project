"""Verify AMiner V11/V13 original nested records -> normalized DBLP references.

Run AFTER tools/normalize_dblp.py:
  python tools/verify_dblp_raw.py --input ../dblp_raw/dblp.v13.json

This checks every NORMALIZED paper against source nested author IDs, venue IDs,
within-sample citation IDs, title and year. It does not establish that the source
metadata is accurate or that missing IDs can be inferred.
"""
import argparse
import json
import sys
from pathlib import Path
from normalize_dblp import read_json_records


def run(rawpath, normalized_dir):
    normalized_dir=Path(normalized_dir)
    normalized={}
    with (normalized_dir/'papers.jsonl').open(encoding='utf-8') as f:
        for line in f:
            if line.strip():
                p=json.loads(line)
                normalized[str(p['paper_id'])]=p
    if not normalized:
        raise ValueError('No normalized papers found')
    seen=set()
    errors=[]
    paper_ids=set(normalized)
    for raw in read_json_records(rawpath):
        pid=str(raw.get('id') or '').strip()
        if pid not in paper_ids or pid in seen:continue
        seen.add(pid)
        norm=normalized[pid]
        expected_authors=sorted(set(str(a['id']).strip() for a in (raw.get('authors') or [])
                                    if isinstance(a,dict) and a.get('id')))
        venue=raw.get('venue') or {}
        expected_venue=str(venue.get('id')).strip() if isinstance(venue,dict) and venue.get('id') else None
        expected_refs=sorted(set(str(r) for r in (raw.get('references') or [])
                                 if str(r) in paper_ids and str(r)!=pid))
        for field,expected,actual in [
            ('author_ids',expected_authors,sorted(set(norm.get('author_ids') or []))),
            ('venue_id',expected_venue,norm.get('venue_id')),
            ('reference_ids',expected_refs,sorted(set(norm.get('reference_ids') or []))),
            ('title',raw.get('title',''),norm.get('title','')),
            ('year',raw.get('year'),norm.get('year'))]:
            if expected!=actual:
                errors.append({'paper':pid,'field':field,'expected':expected,'actual':actual})
        if len(seen)==len(normalized):break
    missing=sorted(paper_ids-seen)
    report={'raw_source':str(rawpath),'normalized_directory':str(normalized_dir),
            'normalized_papers':len(normalized),'papers_found_in_original_raw':len(seen),
            'papers_not_found':len(missing),'field_mismatches':len(errors),
            'first_missing_papers':missing[:5],'first_mismatches':errors[:5],
            'passed':not errors and not missing,
            'scope':'Matches normalized paper IDs, author IDs, venue IDs and within-sample citation IDs against original AMiner nested JSON records.'}
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True)
    p.add_argument('--normalized',default='dblp_normalized')
    p.add_argument('--output',default='')
    a=p.parse_args()
    result=run(Path(a.input),Path(a.normalized))
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if a.output:
        out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    if not result['passed']:sys.exit(1)
