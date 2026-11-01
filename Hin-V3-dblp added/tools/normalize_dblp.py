"""Normalize AMiner DBLP V11/V13 JSONL (or JSON array) into schema-driven 3-file input.

Usage: python tools/normalize_dblp.py --input path/to/dblp.v13.json --limit 5000

Important: preserves supplied identifiers; does NOT equate author names with identities.
Citation links are kept only when both papers are in the selected subset (induced graph).
Requires no third-party modules. Do not use on original DBLP XML (different format).
"""
import argparse
import json
from collections import Counter
from pathlib import Path


def read_json_records(path):
    """Stream JSON Lines or a JSON array without loading the whole dataset."""
    decoder = json.JSONDecoder()
    with Path(path).open('r', encoding='utf-8-sig') as f:
        start = f.read(1)
        while start and start.isspace():
            start = f.read(1)
        f.seek(0)
        if start != '[':
            for i, line in enumerate(f, 1):
                if line.strip():
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as e:
                        raise ValueError(f'Invalid JSONL at line {i}: {e}') from e
                    if not isinstance(obj, dict):
                        raise ValueError(f'Expected JSON object at line {i}')
                    yield obj
        else:
            buffer = ''
            ended = False
            while True:
                chunk = f.read(65536)
                if not chunk and not buffer.strip():
                    break
                buffer += chunk
                while True:
                    buffer = buffer.lstrip()
                    if buffer.startswith('['):
                        buffer = buffer[1:]
                        continue
                    if buffer.startswith(','):
                        buffer = buffer[1:]
                        continue
                    if buffer.startswith(']'):
                        ended = True
                        buffer = buffer[1:]
                        break
                    if not buffer:
                        break
                    try:
                        obj, end = decoder.raw_decode(buffer)
                    except json.JSONDecodeError:
                        if not chunk:
                            raise ValueError('Incomplete or malformed JSON array')
                        break
                    if not isinstance(obj, dict):
                        raise ValueError('Expected paper objects in JSON array')
                    yield obj
                    buffer = buffer[end:]
                if ended:
                    break
                if not chunk:
                    if buffer.strip():
                        raise ValueError('Incomplete JSON array')
                    break


def normalize(source, outdir, limit):
    outdir.mkdir(parents=True, exist_ok=True)
    papers, author_map, venue_map = [], {}, {}
    counts = Counter()
    seen_papers = set()
    for entry in read_json_records(source):
        pid = str(entry.get('id') or '').strip()
        if not pid:
            counts['missing_paper_ids'] += 1
            continue
        if pid in seen_papers:
            counts['duplicate_paper_ids'] += 1
            continue
        seen_papers.add(pid)
        aid_list = []
        for item in entry.get('authors') or []:
            if not isinstance(item, dict):
                counts['authors_missing_stable_id'] += 1
                continue
            aid = str(item.get('id') or '').strip()
            if not aid:
                counts['authors_missing_stable_id'] += 1
                continue
            if aid not in aid_list:
                aid_list.append(aid)
            author_map.setdefault(aid, {'author_id':aid, 'name':item.get('name', '')})
        venue = entry.get('venue') or {}
        if isinstance(venue, dict):
            vid = str(venue.get('id') or '').strip()
            raw_name = venue.get('raw') or venue.get('name') or ''
        else:
            vid, raw_name = '', str(venue)
        if vid:
            venue_map.setdefault(vid, {'venue_id':vid, 'name':raw_name})
        elif raw_name:
            counts['venues_missing_stable_id'] += 1
        refs = [str(x) for x in entry.get('references') or [] if x is not None and str(x).strip()]
        papers.append({'paper_id':pid, 'title':entry.get('title',''), 'year':entry.get('year'),
                       'author_ids':aid_list, 'venue_id':vid or None, '_raw_reference_ids':refs})
        if len(papers) >= limit:
            break
    if not papers:
        raise ValueError('No valid DBLP paper IDs in input. Check your source format (expects AMiner DBLP V11/V13).')
    # This is an induced subgraph: a citation edge is represented only when both IDs
    # are present among the selected source papers, not by inventing absent paper records.
    included = {p['paper_id'] for p in papers}
    for paper in papers:
        refs = paper.pop('_raw_reference_ids')
        paper['reference_ids'] = sorted({r for r in refs if r in included and r != paper['paper_id']})
        counts['citation_references_outside_sample'] += sum(r not in included for r in refs)
        counts['citation_edges_within_sample'] += len(paper['reference_ids'])
    def dump(name, data):
        with (outdir / name).open('w', encoding='utf-8') as f:
            for record in data:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
    dump('papers.jsonl', papers)
    dump('authors.jsonl', author_map.values())
    dump('venues.jsonl', venue_map.values())
    metadata = {'source':str(source), 'source_format':'AMiner DBLP V11/V13',
                'selected_paper_count':len(papers), 'author_count':len(author_map),
                'venue_count':len(venue_map), 'notes':'The selected subset is first-N; citations to outside papers excluded, with count reported. Missing author/venue IDs are NOT guessed.',
                'warnings_and_counts':dict(counts)}
    (outdir/'normalization_report.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(json.dumps(metadata, indent=2))
    print('Prepared:', outdir)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',required=True,help='Path to real AMiner DBLP V11/V13 JSONL or JSON array')
    ap.add_argument('--limit',type=int,default=5000,help='Maximum number of selected real paper records')
    ap.add_argument('--outdir',default='dblp_normalized')
    args=ap.parse_args()
    if args.limit < 1: ap.error('--limit must be positive')
    normalize(Path(args.input),Path(args.outdir),args.limit)

if __name__ == '__main__':
    main()
