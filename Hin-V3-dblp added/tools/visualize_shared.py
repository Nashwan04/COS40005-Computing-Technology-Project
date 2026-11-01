"""Create a simple actual-data HTML proof of 2 sources sharing 1 typed target node."""
import argparse
from collections import defaultdict
from html import escape
import json
from pathlib import Path


def render(graph_path,relation,target_type,outfile):
    graph=json.loads(Path(graph_path).read_text(encoding='utf-8'))
    nodes={n['id']:n for n in graph['nodes']}
    by_target=defaultdict(list)
    for edge in graph['edges']:
        if edge['relation']==relation and nodes[edge['target']]['type']==target_type:
            if not any(x['source']==edge['source'] for x in by_target[edge['target']]):
                by_target[edge['target']].append(edge)
    candidates=[(t,arr) for t,arr in by_target.items() if len(arr)>=2]
    if not candidates:
        raise ValueError(f'No target {target_type} node with two incoming {relation} edges in this sample; try a bigger sample')
    target, connections=sorted(candidates,key=lambda x:(-len(x[1]),x[0]))[0]
    selected=connections[:2]
    ids={target,*(e['source'] for e in selected)}
    proof={'shared_target':target,'relationship':relation,'target_type':target_type,
           'total_incoming_edges_to_shared_target':len(connections),'nodes':[nodes[x] for x in sorted(ids)],'edges':selected,
           'note':'Actual graph data; source-reference correctness can be tested with tools/verify_edges.py'}
    outfile.parent.mkdir(parents=True,exist_ok=True)
    outfile.with_suffix('.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False),encoding='utf-8')
    def label(node):
        obj=nodes[node]
        title=obj.get('attributes',{}).get('title') or obj.get('attributes',{}).get('name') or obj['source_id']
        short=str(title)
        if len(short)>35:short=short[:32]+'...'
        return escape(f"{obj['type']}: {short}")
    def tooltip(node):return escape(node)
    e1,e2=selected
    html=f'''<!doctype html><html><head><meta charset="utf-8"><title>P88 typed HIN proof</title>
<style>body{{font-family:system-ui,Arial;background:#f4f7fb;color:#142235;padding:30px}}main{{max-width:1030px;margin:auto;background:white;border-radius:16px;padding:32px;box-shadow:0 2px 14px #b7c8d866}}svg{{width:100%;height:auto}}p{{line-height:1.6}}code{{background:#e8eff6;padding:2px 6px;border-radius:4px}}</style>
</head><body><main><h1>P88: Two nodes share one {escape(target_type)} entity</h1><p>This diagram comes from the actual generated graph file. Two distinct {escape(nodes[e1['source']]['type'])} nodes have <code>{escape(relation)}</code> edges to the same {escape(target_type)} node. Hover over boxes to inspect IDs.</p>
<svg viewBox="0 0 1020 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Two typed source nodes share one target node">
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0 0L9 3L0 6" fill="#657c91"/></marker></defs>
<g fill="none" stroke="#657c91" stroke-width="3" marker-end="url(#arrow)"><path d="M360 83L610 144"/><path d="M360 213L610 167"/></g>
<g font-size="16" fill="#294f69"><text x="415" y="93">{escape(relation)}</text><text x="415" y="223">{escape(relation)}</text></g>
<rect x="20" y="43" width="340" height="78" rx="13" fill="#15749e"/><text x="190" y="88" font-size="17" fill="white" text-anchor="middle">{label(e1['source'])}</text><title>{tooltip(e1['source'])}</title>
<rect x="20" y="173" width="340" height="78" rx="13" fill="#15749e"/><text x="190" y="218" font-size="17" fill="white" text-anchor="middle">{label(e2['source'])}</text><title>{tooltip(e2['source'])}</title>
<rect x="610" y="112" width="390" height="78" rx="13" fill="#2a8368"/><text x="805" y="156" font-size="17" fill="white" text-anchor="middle">{label(target)}</text><title>{tooltip(target)}</title></svg>
<p><strong>Proof:</strong> {len(connections)} {escape(relation)} edges point to one stored node <code>{escape(target)}</code>. Its original source ID is <code>{escape(nodes[target]['source_id'])}</code>.</p>
<p><strong>Important:</strong> This is a structural demonstration. Independently run <code>tools/verify_edges.py</code> to compare all stored edge references with source records.</p></main></body></html>'''
    outfile.write_text(html,encoding='utf-8')
    print('Shared target:',target,' incoming edges:',len(connections))
    print('HTML:',outfile)
    print('Proof JSON:',outfile.with_suffix('.json'))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--graph',required=True)
    p.add_argument('--relation',required=True)
    p.add_argument('--target-type',required=True)
    p.add_argument('--output',default='outputs/shared_graph.html')
    a=p.parse_args()
    render(a.graph,a.relation,a.target_type,Path(a.output))
