"""Explainable HIN queries: outgoing and incoming neighbors grouped by edge type."""
import argparse
import json
from collections import Counter
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--graph',required=True)
    p.add_argument('--node',default='',help='Type:ID, e.g. Business:abc')
    p.add_argument('--relation',default='',help='Optional relation filter')
    a=p.parse_args()
    g=json.loads(Path(a.graph).read_text(encoding='utf-8'))
    inc=g.get('reverse_adjacency',{})
    if not inc:
        inc={}
        for e in g['edges']:
            inc.setdefault(e['target'],{}).setdefault(e['relation'],[]).append(e['source'])
    outgoing=g.get('typed_adjacency',{})
    if not outgoing:
        outgoing={}
        for e in g['edges']:
            outgoing.setdefault(e['source'],{}).setdefault(e['relation'],[]).append(e['target'])
    if not a.node:
        options=sorted(inc, key=lambda k:sum(len(v) for v in inc[k].values()),reverse=True)
        if not options:
            print('No edges available'); return
        node=options[0]
        print('Automatically selected a shared/highly connected node:',node)
    else:node=a.node
    if not any(n['id']==node for n in g['nodes']):
        raise SystemExit(f'Node not found: {node}')
    print('NODE',node)
    print('INCOMING:')
    for rel,ids in sorted(inc.get(node,{}).items()):
        if not a.relation or rel==a.relation:
            print(f'  {rel}: {len(ids)} source nodes; example:',ids[:5])
    print('OUTGOING:')
    for rel,ids in sorted(outgoing.get(node,{}).items()):
        if not a.relation or rel==a.relation:
            print(f'  {rel}: {len(ids)} target nodes; example:',ids[:5])

if __name__=='__main__':main()
