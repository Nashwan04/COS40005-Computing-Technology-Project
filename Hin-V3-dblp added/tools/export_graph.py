"""Export a typed HIN JSON store as standard GraphML and easy-to-inspect CSVs."""
import argparse
import csv
import json
from pathlib import Path
from xml.etree import ElementTree as ET

NS='http://graphml.graphdrawing.org/xmlns'
ET.register_namespace('',NS)
def t(tag):return '{'+NS+'}'+tag

def export(graphfile,outdir):
    graph=json.loads(Path(graphfile).read_text(encoding='utf-8'))
    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir/'nodes.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['id','type','source_id','attributes_json'])
        for n in graph['nodes']:
            w.writerow([n['id'],n['type'],n['source_id'],json.dumps(n.get('attributes',{}),ensure_ascii=False)])
    with (outdir/'edges.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['source','target','relation','evidence_json'])
        for e in graph['edges']:
            w.writerow([e['source'],e['target'],e['relation'],json.dumps(e.get('evidence',{}),ensure_ascii=False)])
    root=ET.Element(t('graphml'))
    for kid,who,name in [('nt','node','type'),('ni','node','source_id'),('er','edge','relation')]:
        ET.SubElement(root,t('key'),id=kid,attrib={'for':who,'attr.name':name,'attr.type':'string'})
    g=ET.SubElement(root,t('graph'),id='P88_HIN',edgedefault='directed')
    for node in graph['nodes']:
        el=ET.SubElement(g,t('node'),id=node['id'])
        ET.SubElement(el,t('data'),key='nt').text=str(node['type'])
        ET.SubElement(el,t('data'),key='ni').text=str(node['source_id'])
    for idx,e in enumerate(graph['edges']):
        el=ET.SubElement(g,t('edge'),id=f'e{idx}',source=e['source'],target=e['target'])
        ET.SubElement(el,t('data'),key='er').text=e['relation']
    ET.ElementTree(root).write(outdir/'hin.graphml',encoding='utf-8',xml_declaration=True)
    print(f"Exported {len(graph['nodes'])} nodes and {len(graph['edges'])} directed typed edges to {outdir}")
    for name in ['hin.graphml','nodes.csv','edges.csv']:
        print(' -',outdir/name)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--graph',required=True)
    p.add_argument('--outdir',default='exports')
    a=p.parse_args()
    export(a.graph,Path(a.outdir))
