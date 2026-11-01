"""Generate reproducible LARGE SYNTHETIC DBLP-style test data (NOT real DBLP)."""
import argparse
import json
from pathlib import Path


def generate(outdir, num_papers=5000):
    if num_papers < 3:
        raise ValueError('Expected at least 3 papers')
    outdir.mkdir(parents=True, exist_ok=True)
    n_authors = max(3, num_papers // 12)
    n_venues = max(2, num_papers // 100)
    def write(name, data):
        with (outdir/name).open('w',encoding='utf-8') as f:
            for row in data: f.write(json.dumps(row,ensure_ascii=False)+'\n')
    write('authors.jsonl', ({'author_id':f'A{i:05d}','name':f'SYNTHETIC Author {i}'} for i in range(n_authors)))
    write('venues.jsonl', ({'venue_id':f'V{i:04d}','name':f'SYNTHETIC Venue {i}'} for i in range(n_venues)))
    def papers():
        for i in range(num_papers):
            # deliberately reuse authors, venue and cite earlier papers (shared entities)
            aids=sorted({f'A{(i*3)%n_authors:05d}',f'A{(i*3+1)%n_authors:05d}'})
            yield {'paper_id':f'P{i:07d}', 'title':f'SYNTHETIC Paper {i}',
                   'year':2020 + i%7,'author_ids':aids,
                   'venue_id':f'V{i%n_venues:04d}',
                   'reference_ids':[f'P{i-1:07d}'] if i else []}
    write('papers.jsonl',papers())
    print(f'Generated SYNTHETIC data: {num_papers} papers, {n_authors} authors, {n_venues} venues in {outdir}')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--papers',type=int,default=5000)
    p.add_argument('--outdir',default='demo_data/dblp_large')
    a=p.parse_args()
    generate(Path(a.outdir),a.papers)
