"""Independently verify exported graph edges against source JSON records and schema.

Validates every STORED edge's provenance, relation direction and raw reference.
Does not validate that the supplied schema correctly models the real-world semantics.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hin_v2 import records


def verify(graph_path, schema_path, data_root=None):
    graph = json.loads(Path(graph_path).read_text(encoding='utf-8'))
    schema_file=Path(schema_path).resolve()
    schema=json.loads(schema_file.read_text(encoding='utf-8'))
    base=Path(data_root).resolve() if data_root else schema_file.parent
    declared={(r['from'],r['type'],r['field'],r['to']) for r in schema['relationships']}
    nodes={n['id']:n for n in graph['nodes']}
    edges=graph['edges']
    needed=defaultdict(set)
    invalid=[]
    for i,e in enumerate(edges):
        source=e['source']; target=e['target']; ev=e.get('evidence') or {}
        src_kind=ev.get('source_type'); record_id=str(ev.get('source_id'))
        ref_field=ev.get('reference_field'); ref_value=ev.get('reference_value')
        target_kind=nodes[target]['type'] if target in nodes else '<missing>'
        relation=e.get('relation')
        if source not in nodes or target not in nodes:
            invalid.append((i,'missing node'))
        elif (src_kind,relation,ref_field,target_kind) not in declared:
            invalid.append((i,'undeclared or wrongly directed relation'))
        elif source != f'{src_kind}:{record_id}' or target != f'{target_kind}:{ref_value}':
            invalid.append((i,'ID mismatch with edge provenance'))
        if src_kind in schema['entities']:
            needed[src_kind].add(record_id)
    # Also inspect selected source nodes that generated NO edges, so missing
    # expected edges are detectable (not just wrong edges that were stored).
    source_kinds={r['from'] for r in schema['relationships']}
    for node in nodes.values():
        if node['type'] in source_kinds:
            needed[node['type']].add(str(node['source_id']))
    rowmaps={}
    for kind,ids in needed.items():
        spec=schema['entities'][kind]
        found={}
        for row in records(base / spec['file']):
            rid=str(row.get(spec['id']))
            if rid in ids:
                found[rid]=row
                if len(found) == len(ids):break
        rowmaps[kind]=found
    verified=0
    for i,e in enumerate(edges):
        ev=e.get('evidence') or {}
        kind=ev.get('source_type'); record_id=str(ev.get('source_id'))
        record=rowmaps.get(kind,{}).get(record_id)
        if record is None:
            invalid.append((i,'source record not found'))
            continue
        actual=record.get(ev.get('reference_field'))
        possible=actual if isinstance(actual,list) else [actual]
        if not any(str(v)==str(ev.get('reference_value')) for v in possible):
            invalid.append((i,'reference is not present in source record'))
            continue
        verified+=1
    actual={(e['source'],e['target'],e['relation']) for e in edges}
    expected=set()
    for rel in schema['relationships']:
        sk,dk=rel['from'],rel['to']
        for record_id,row in rowmaps.get(sk,{}).items():
            values=row.get(rel['field'])
            if values is None:continue
            for val in (values if isinstance(values,list) else [values]):
                target=f'{dk}:{val}'
                if target in nodes:
                    expected.add((f'{sk}:{record_id}',target,rel['type']))
    missing_expected=sorted(expected-actual)
    unexpected=sorted(actual-expected)
    out={'graph':str(graph_path),'source_schema':str(schema_path),
         'stored_edges':len(edges),'edges_matching_source_references':verified,
         'invalid_findings':len(invalid),'first_invalid_findings':invalid[:10],
         'expected_edges_with_endpoints_in_graph':len(expected),
         'missing_declared_edges':len(missing_expected),
         'unexpected_stored_edges':len(unexpected),
         'sample_missing_declared_edges':missing_expected[:5],
         'passed':len(invalid)==0 and verified==len(edges) and not missing_expected and not unexpected,
         'scope':'Every stored edge and every resolvable declared reference within selected nodes checked; schema meaning and completeness outside the sampled graph are not proven.'}
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--graph',required=True)
    ap.add_argument('--schema',required=True)
    ap.add_argument('--output',default='')
    ap.add_argument('--data-root',default=None)
    a=ap.parse_args()
    r=verify(a.graph,a.schema,a.data_root)
    print(json.dumps(r,indent=2))
    if a.output:Path(a.output).write_text(json.dumps(r,indent=2),encoding='utf-8')
    if not r['passed']:sys.exit(1)
