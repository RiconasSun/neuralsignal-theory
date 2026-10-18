"""Source-only Final adapters and exact timing regressions before payload use."""
import unittest
import numpy as np
from .source import frozen_definitions,source_rows,read,R,P
from .metadata_access import permit
from .metadata_qc import partition,annotation_audit
from .features import held


class MetadataBoundary(unittest.TestCase):
    def test_original_source_and_selection(self):
        frozen_definitions()
        self.assertEqual(len(source_rows()),8)

    def test_metadata_never_neural(self):
        for row in source_rows():
            for f in row['files']:
                if f['role'] in ('times','clusters'):
                    with self.assertRaises(PermissionError):permit(row,f)
                else:permit(row,f)
            other=dict(row,allocation='DEVELOPMENT')
            with self.assertRaises(PermissionError):permit(other,row['files'][0])
            annotation_audit(row)

    def test_original_final_partitions_and_guards(self):
        roles,guard,cuts=partition(101,False)
        self.assertEqual(cuts,{'C':(0,60),'D':(60,101)})
        self.assertEqual(np.flatnonzero(~guard).tolist(),[59,60])
        self.assertTrue(np.all(roles[:60]=='C'))

    def test_pl033_native_equal_boundary(self):
        state=read(R/'paper15_r1/metadata/PL033_task.json')
        b=state['trials'][224]['stimOn_times']
        # Exact native equality must exclude that encoder sample; rounding changes the query.
        wt=np.array([b-.1,b,b+.1]);wp=np.array([1.,999.,3.])
        values,indices=held(wt,wp,np.array([b]))
        self.assertEqual(indices.tolist(),[0]);self.assertEqual(values.tolist(),[1.])


if __name__=='__main__':unittest.main()
