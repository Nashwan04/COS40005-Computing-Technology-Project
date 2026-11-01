"""Reproducible tests using small SYNTHETIC fixtures only. Run: python -m unittest discover -s tests -v"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'tools'))
from hin_v2 import build
from normalize_dblp import normalize
from verify_dblp_raw import run as verify_dblp_normalization
from verify_edges import verify
from export_graph import export
from visualize_shared import render

class PipelineTests(unittest.TestCase):
    def test_dblp_original_synthetic(self):
        spec=json.loads((ROOT/'dblp_schema_example.json').read_text())
        result=build(spec,ROOT)
        self.assertEqual(result['metadata']['node_count'],8)
        self.assertEqual(result['metadata']['edge_count'],10)
        self.assertTrue(all(result['metadata']['validation'].values()))
        self.assertEqual(len(result['reverse_adjacency']['Author:A1']['AUTHORED_BY']),3)
        self.assertEqual(set(result['typed_adjacency']['Paper:P2']['AUTHORED_BY']),{'Author:A1','Author:A2'})

    def test_yelp_unique_shared_business_and_verified_raw_edges(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); data=root/'yelp_dataset';data.mkdir()
            def save(name, items):
                (data/name).write_text(''.join(json.dumps(i)+'\n' for i in items),encoding='utf-8')
            save('yelp_academic_dataset_review.json',[
                {'review_id':'r1','user_id':'u1','business_id':'b1','stars':5},
                {'review_id':'r2','user_id':'u2','business_id':'b1','stars':4},
                {'review_id':'r3','user_id':'u1','business_id':'b2','stars':2}])
            save('yelp_academic_dataset_user.json',[{'user_id':'u1','name':'User One'},{'user_id':'u2','name':'User Two'}])
            save('yelp_academic_dataset_business.json',[{'business_id':'b1','name':'Business One'},{'business_id':'b2','name':'Business Two'}])
            schema=json.loads((ROOT/'yelp_schema_v2.json').read_text())
            graph=build(schema,root,limit=3)
            self.assertEqual(graph['metadata']['node_count'],7)
            self.assertEqual(graph['metadata']['edge_count'],6)
            self.assertEqual(len(graph['reverse_adjacency']['Business:b1']['ABOUT']),2)
            self.assertTrue(all(graph['metadata']['validation'].values()))
            outfile=root/'graph.json';outfile.write_text(json.dumps(graph),encoding='utf-8')
            (root/'schema.json').write_text(json.dumps(schema),encoding='utf-8')
            self.assertTrue(verify(outfile,root/'schema.json')['passed'])
            export(outfile,root/'export')
            self.assertTrue((root/'export'/'hin.graphml').exists())
            render(outfile,'ABOUT','Business',root/'shared.html')
            self.assertTrue((root/'shared.html').exists())

    def test_normalizes_nested_aminer_ids_without_inventing_names(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            raw=root/'dblp.jsonl'
            raw.write_text('\n'.join(json.dumps(x) for x in [
              {'id':'p1','title':'A','year':2023,'authors':[{'id':'a1','name':'Alex'}, {'name':'No ID'}], 'venue':{'id':'v1','raw':'Conf A'},'references':['p2','unknown']},
              {'id':'p2','title':'B','year':2024,'authors':[{'id':'a1','name':'Alex'}, {'id':'a2','name':'Bea'}],'venue':{'id':'v1','raw':'Conf A'},'references':['p1']},
              {'id':'p3','title':'C','year':2024,'authors':[{'id':'a2','name':'Bea'}],'venue':{'id':'v2','raw':'Conf B'},'references':[]}])+'\n')
            normalize(raw,root/'dblp_normalized',limit=3)
            report=json.loads((root/'dblp_normalized'/'normalization_report.json').read_text())
            self.assertTrue(verify_dblp_normalization(raw,root/'dblp_normalized')['passed'])
            self.assertEqual(report['warnings_and_counts']['authors_missing_stable_id'],1)
            self.assertEqual(report['warnings_and_counts']['citation_references_outside_sample'],1)
            schema=json.loads((ROOT/'dblp_real_schema.json').read_text())
            graph=build(schema,root,3)
            self.assertEqual(graph['metadata']['node_count'],7)
            self.assertEqual(graph['metadata']['relation_types']['CITES'],2)
            self.assertEqual(graph['metadata']['edge_count'],9)
            self.assertTrue(all(graph['metadata']['validation'].values()))
            outfile=root/'graph.json';outfile.write_text(json.dumps(graph),encoding='utf-8')
            (root/'dblp_schema.json').write_text(json.dumps(schema),encoding='utf-8')
            self.assertTrue(verify(outfile,root/'dblp_schema.json')['passed'])

if __name__=='__main__':unittest.main()
