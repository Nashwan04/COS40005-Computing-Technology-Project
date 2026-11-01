"""Print a trace from a raw JSON record to one typed HIN edge.
Usage: python tools/explain_edge.py --graph outputs/yelp_5000.json --schema yelp_schema_v2.json --relation ABOUT --data-root ..
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hin_v2 import records

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--graph',required=True)
p.add_argument('--schema',required=True)
p.add_argument('--data-root',default=None)
p.add_argument('--relation',default='')
p.add_argument('--source',default='')
a=p.parse_args()
graph=json.loads(Path(a.graph).read_text(encoding='utf-8'))
schema_path=Path(a.schema).resolve();schema=json.loads(schema_path.read_text(encoding='utf-8'))
selected=[e for e in graph['edges'] if (not a.relation or e['relation']==a.relation) and (not a.source or e['source']==a.source)]
if not selected:
    raise SystemExit('No edge matching --source / --relation in graph')
edge=selected[0]; ev=edge['evidence']; source_type=ev['source_type'];s_id=str(ev['source_id'])
spec=schema['entities'][source_type]
base=Path(a.data_root).resolve() if a.data_root else schema_path.parent
source_record=None
for row in records(base/spec['file']):
    if str(row.get(spec['id']))==s_id:
        source_record=row
        break
if source_record is None:
    raise SystemExit(f'Source record missing: {source_type}:{s_id}')
print('\n=== P88 RAW → SCHEMA → HIN TRACE ===')
print('Source file:',base/spec['file'])
print('Source entity:',source_type,'; primary key:',spec['id'])
print('Source record ID:',s_id)
print('Raw reference field:',ev['reference_field'])
print('Raw reference value:',source_record.get(ev['reference_field']))
print('Declared relation:',edge['relation'])
print('Constructed edge:',edge['source'],'--'+edge['relation']+'-->',edge['target'])
print('Edge provenance:',json.dumps(ev,ensure_ascii=False))
