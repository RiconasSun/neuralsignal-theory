import unittest
import numpy as np
from .reader import project_C,authorize,check_reader_gate,verify_external_dependencies
from .source import source_rows,P,read


class TrustedReader(unittest.TestCase):
    def test_C_half_open_and_outside_epoch_ordinals_preserved(self):
        t=np.array([0.,1.,1.,2.,3.,4.]);l=np.array([0,1,0,1,0,1])
        ct,cl=project_C(t,l,0.,3.,2,[0.,4.],1000.)
        self.assertEqual(ct.tolist(),[0.,1.,1.,2.]);self.assertEqual(cl.tolist(),[0,1,0,1])

    def test_hidden_D_corruption_not_C_QC(self):
        t=np.array([0.,1.,2.,5.,4.,9.]);l=np.array([0,1,0,999,-3,999])
        ct,cl=project_C(t,l,0.,3.,2,[0.,3.],1000.)
        self.assertEqual(ct.tolist(),[0.,1.,2.]);self.assertEqual(cl.tolist(),[0,1,0])

    def test_unassignable_source_timestamp_generic(self):
        with self.assertRaisesRegex(ValueError,'^UNASSIGNABLE_SOURCE_TIMESTAMP$'):
            project_C(np.array([0.,np.nan]),np.array([0,999]),0.,1.,2,[0.,1.],1000.)

    def test_C_order_and_labels_fail(self):
        for t,l in [(np.array([1.,0.]),np.array([0,0])),(np.array([0.,1.]),np.array([0,999]))]:
            with self.assertRaisesRegex(ValueError,'C_ONLY_SOURCE_ORDER_OR_CLUSTER_ERROR'):
                project_C(t,l,0.,2.,2,[0.,2.],1000.)

    def test_D_export_denied(self):
        row=source_rows()[0]
        with self.assertRaises(PermissionError):authorize(row['subject'],'D',row,{'result':{'prephysiology_possible':True}})

    def test_empty_or_self_declared_gate_denied(self):
        for gate in [{},{'approved_C_only':True,'hashes':{}}]:
            with self.assertRaises(PermissionError):check_reader_gate(gate)

    def test_missing_or_tampered_external_mapping_denied(self):
        with self.assertRaises(PermissionError):verify_external_dependencies({})
        hashes=read(P/'METADATA_SOURCE_EXTERNAL_FREEZE.json')['hashes']
        verify_external_dependencies(hashes)
        hashes=dict(hashes);hashes['paper13/metadata/atlas.json']='0'*64
        with self.assertRaises(PermissionError):verify_external_dependencies(hashes)


if __name__=='__main__':unittest.main()
