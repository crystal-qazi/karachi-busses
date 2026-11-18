import csv,tempfile,unittest
from pathlib import Path
from scripts.audit_phase5ac_collision_crosswalk_impact import build

class CollisionCrosswalkImpactTests(unittest.TestCase):
 def write(self,p,fields,rows):
  with p.open("w",encoding="utf-8",newline="") as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 def test_detects_node_id_and_coordinate_overlaps(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);n=d/"nodes.csv";c=d/"crosswalk.csv"
   self.write(n,["node_id","latitude","longitude","historical_route_labels","verification_status"],[
    {"node_id":"a","latitude":"24.1000","longitude":"67.2","historical_route_labels":"R1","verification_status":"unverified"},
    {"node_id":"b","latitude":"24.1","longitude":"67.200","historical_route_labels":"R2","verification_status":"unverified"},
    {"node_id":"c","latitude":"24.2","longitude":"67.3","historical_route_labels":"R3","verification_status":"unverified"}])
   self.write(c,["route_code","source_stop_sequence","source_stop_name","coordinate_node_id","latitude","longitude","review_status"],[
    {"route_code":"S1","source_stop_sequence":"1","source_stop_name":"Stop A","coordinate_node_id":"a","latitude":"24.1","longitude":"67.2","review_status":"candidate_name_match"},
    {"route_code":"S2","source_stop_sequence":"1","source_stop_name":"Stop B","coordinate_node_id":"other","latitude":"24.10000","longitude":"67.2000","review_status":"candidate_name_match"}])
   out=d/"out.csv";rep=d/"rep.json";r=build(n,c,out,rep)
   self.assertEqual(r["counts"]["collision_groups"],1)
   self.assertEqual(r["counts"]["crosswalk_rows_matching_collision_node_ids"],1)
   self.assertEqual(r["counts"]["crosswalk_rows_matching_collision_coordinates"],2)
 def test_rejects_duplicate_node_ids(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);n=d/"n.csv";c=d/"c.csv"
   self.write(n,["node_id","latitude","longitude","historical_route_labels","verification_status"],[
    {"node_id":"a","latitude":"24.1","longitude":"67.2","historical_route_labels":"","verification_status":"x"},
    {"node_id":"a","latitude":"24.2","longitude":"67.3","historical_route_labels":"","verification_status":"x"}])
   self.write(c,["route_code","source_stop_sequence","source_stop_name","coordinate_node_id","latitude","longitude","review_status"],[])
   with self.assertRaisesRegex(ValueError,"duplicate node ID"):build(n,c,d/"o.csv",d/"r.json")
if __name__=="__main__":unittest.main()
