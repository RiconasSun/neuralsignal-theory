import copy
import unittest
from cache_binding3 import validate


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.expected={'mouse_id':'fixture','session_id':'session','group':'development',
                       'source':{'file_id':'file','etag':'etag','bytes':10},'index_registration_sha256':'registration'}
        self.audit={k:self.expected[k] for k in ('mouse_id','session_id','group')}
        self.audit.update(raw_index_valid=True,old_cast_equivalence_proved=True)
        self.binding={**self.expected,'audit_sha256':'audit','previous_output_sha256':'previous'}
        self.previous={k:self.expected[k] for k in ('mouse_id','session_id','group')}
        self.previous.update(source_etag='etag',final_values_exposed_to_analysis=False,final_holdout_evaluated=False)
    def test_bound_valid(self):
        self.assertTrue(validate(self.audit,self.binding,self.expected,'audit',self.previous,'previous'))
    def test_false_equivalence(self):
        self.audit['old_cast_equivalence_proved']=False
        with self.assertRaises(ValueError):validate(self.audit,self.binding,self.expected,'audit')
    def test_numeric_true_not_boolean(self):
        self.audit['raw_index_valid']=1
        with self.assertRaises(ValueError):validate(self.audit,self.binding,self.expected,'audit')
    def test_identity(self):
        self.audit['mouse_id']='other'
        with self.assertRaises(ValueError):validate(self.audit,self.binding,self.expected,'audit')
    def test_etag(self):
        self.binding=copy.deepcopy(self.binding);self.binding['source']['etag']='new'
        with self.assertRaises(ValueError):validate(self.audit,self.binding,self.expected,'audit')
    def test_registration(self):
        self.binding['index_registration_sha256']='changed'
        with self.assertRaises(ValueError):validate(self.audit,self.binding,self.expected,'audit')
    def test_audit_hash(self):
        with self.assertRaises(ValueError):validate(self.audit,self.binding,self.expected,'tampered')
    def test_previous_hash(self):
        with self.assertRaises(ValueError):validate(self.audit,self.binding,self.expected,'audit',self.previous,'tampered')
    def test_previous_source(self):
        self.previous['source_etag']='new'
        with self.assertRaises(ValueError):validate(self.audit,self.binding,self.expected,'audit',self.previous,'previous')
    def test_previous_group(self):
        self.previous['group']='final'
        with self.assertRaises(ValueError):validate(self.audit,self.binding,self.expected,'audit',self.previous,'previous')


if __name__=='__main__':unittest.main()
