"""Schema-driven JSONL/JSON -> typed HIN. No dataset-specific field names in engine."""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def records(path, limit=None):
    with open(path, encoding='utf-8-sig') as f:
        first = f.read(1)
        f.seek(0)
        if first == '[':
            # Array JSON requires loading the array; JSONL is streamed below.
            data = json.load(f)
            for i, row in enumerate(data):
                if limit is not None and i >= limit: break
                yield row
        else:
            for i, line in enumerate(f):
                if limit is not None and i >= limit: break
                if line.strip(): yield json.loads(line)


def build(schema, base, limit=None):
    nodes, edges, seen_edges = {}, [], set()
    indexes = defaultdict(dict)
    stats = Counter()
    # First collect records for every declared entity type. For Yelp, sample Reviews
    # and select referenced Users/Businesses without loading whole large files.
    specs = schema['entities']
    primary = schema.get('primary')
    if primary not in specs: raise ValueError('schema.primary must name an entity type')
    sampled = list(records(base / specs[primary]['file'], limit))
    needed = defaultdict(set)
    for row in sampled:
        for rel in schema['relationships']:
            if rel['from'] == primary and rel['to'] != primary:
                val = row.get(rel['field'])
                if val is not None:
                    for item in (val if isinstance(val, list) else [val]):
                        needed[rel['to']].add(str(item))
    def add_node(kind, row):
        spec = specs[kind]
        value = row.get(spec['id'])
        if value is None or value == '':
            stats['missing_ids'] += 1
            return
        key = str(value)
        nid = f'{kind}:{key}'
        if nid in nodes:
            stats['duplicate_source_ids'] += 1
            return
        attrs = {field:row.get(field) for field in spec.get('attributes', []) if field in row}
        nodes[nid] = {'id':nid,'type':kind,'source_id':key,'attributes':attrs}
        indexes[kind][key] = nid
    for row in sampled: add_node(primary, row)
    for kind, spec in specs.items():
        if kind == primary: continue
        target_ids = needed[kind]
        for row in records(base / spec['file']):
            if not target_ids or str(row.get(spec['id'])) not in target_ids: continue
            add_node(kind, row)
            if len(indexes[kind]) >= len(target_ids): break
    # Build edges from explicit schema references; no invented links.
    # Allow refs from either source kind, not only the primary kind.
    for rel in schema['relationships']:
        src_kind, dst_kind = rel['from'], rel['to']
        src_spec = specs[src_kind]
        if src_kind == primary:
            source_rows = sampled
        else:
            source_rows = records(base / src_spec['file'])
        for row in source_rows:
            src_id = indexes[src_kind].get(str(row.get(src_spec['id'])))
            if not src_id: continue
            values = row.get(rel['field'])
            if values is None: continue
            if not isinstance(values, list): values = [values]
            for v in values:
                dst_id = indexes[dst_kind].get(str(v))
                if not dst_id:
                    stats['unresolved_references'] += 1
                    continue
                edge_key = (src_id, dst_id, rel['type'])
                if edge_key in seen_edges: continue
                seen_edges.add(edge_key)
                edges.append({'source':src_id,'target':dst_id,'relation':rel['type'],
                              'evidence':{'source_type':src_kind,'source_id':row[src_spec['id']],
                                          'reference_field':rel['field'],'reference_value':v}})
    adjacency = defaultdict(list)
    for e in edges:
        adjacency[e['source']].append({'target':e['target'],'relation':e['relation']})
    checks = {'no_dangling_edges':all(e['source'] in nodes and e['target'] in nodes for e in edges),
              'unique_node_ids':len(nodes)==len(set(nodes)),
              'typed_nodes':all(n['type'] in specs for n in nodes.values()),
              'declared_relations':all(e['relation'] in {r['type'] for r in schema['relationships']} for e in edges)}
    return {'metadata':{'dataset':schema['name'],'node_count':len(nodes),'edge_count':len(edges),
                        'node_types':dict(Counter(n['type'] for n in nodes.values())),
                        'relation_types':dict(Counter(e['relation'] for e in edges)),
                        'validation':checks,'warnings':dict(stats)},
            'nodes':list(nodes.values()),'edges':edges,'adjacency':dict(adjacency)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--schema',required=True)
    p.add_argument('--output',default='hin_v2_output.json')
    p.add_argument('--limit',type=int,default=None,help='Number of primary records to sample')
    a=p.parse_args()
    path=Path(a.schema).resolve()
    schema=json.loads(path.read_text(encoding='utf-8-sig'))
    result=build(schema,path.parent,a.limit)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(result['metadata'],indent=2))
    print('Saved:',a.output)

if __name__=='__main__': main()
