import io
import json
import uuid
import unittest
from unittest.mock import patch
import h5py
import numpy as np
from . import exploratory_E as e


class ETests(unittest.TestCase):
    def fixture(self):
        root=e.P/'work'/('E_tests_'+uuid.uuid4().hex);root.mkdir(parents=True)
        record={'mouse_id':'synthetic','role':'development','epochs':[{'ordinal':91+i,'start':100.+5*i,'stop':103.+5*i,'partition':'E'} for i in range(30)]}
        units=[{'unit_id':i,'row':i,'electrode_row':i,'label':'PL5'} for i in range(8)]
        qc={'mouse_id':'synthetic','partition':'A','selected_units':units}
        return root,record,qc

    def test_no_E_review_denies_before_models_or_source(self):
        root,_,_=self.fixture()
        with patch.object(e,'P',root),patch.object(e.bundles,'gates',side_effect=AssertionError('models before E approval')):
            with self.assertRaises(PermissionError):e.run()

    def test_final_role_and_wrong_epoch_count_denied(self):
        _,record,_=self.fixture()
        with self.assertRaises(PermissionError):e.windows({**record,'role':'final'})
        with self.assertRaises(e.ScientificStop):e.windows({**record,'epochs':record['epochs'][:29]})

    def test_M4failure_or_unit_tamper_denies_before_source(self):
        _,record,qc=self.fixture()
        with patch.object(e,'approved',return_value='E-code'),patch.object(e,'SourceReader',side_effect=AssertionError('source before gate')):
            with patch.object(e.b,'read',side_effect=[{'M4':'PENDING'},{'M4_A_NUMERICS':'PASS','completed':540}]):
                with self.assertRaises(e.ScientificStop):e.export(record,qc,'E-code')
            with patch.object(e.b,'read',side_effect=[{'M4':'PASS'},{'M4_A_NUMERICS':'PASS','completed':540},{**qc,'selected_units':[]}]):
                with self.assertRaises(PermissionError):e.export(record,qc,'E-code')

    def hdf(self,record,nonfinite_second=False):
        stream=io.BytesIO();values=[];ends=[]
        for unit in range(8):
            values.extend(e['start']+t for e in record['epochs'] for t in [.2,1.2,2.2])
            values.append(float('nan') if nonfinite_second and unit==1 else 10000.)
            ends.append(len(values))
        with h5py.File(stream,'w') as h:
            h['units/id']=np.arange(8);h['units/spike_times']=values;h['units/spike_times_index']=ends
        return stream.getvalue()

    def export_fixture(self,nonfinite_second=False):
        root,record,qc=self.fixture();raw=self.hdf(record,nonfinite_second);original=e.b.read
        def metadata(path):
            name=str(path).replace('\\','/')
            if name.endswith('/M4_MODEL_SELECTION.json'):return {'M4':'PASS'}
            if name.endswith('/M4_A_GATE.json'):return {'M4_A_NUMERICS':'PASS','completed':540}
            if name.endswith('/qc/synthetic.json'):return qc
            return original(path)
        return root,record,qc,raw,metadata

    def test_synthetic_E_exports_only_E_noQC_or_scaling(self):
        root,record,qc,raw,metadata=self.export_fixture()
        with patch.object(e,'P',root),patch.object(e,'approved',return_value='E-code'),patch.object(e.b,'read',side_effect=metadata),patch.object(e,'SourceReader',side_effect=lambda _:io.BytesIO(raw)),patch('paper13_ki_execution1.qc.screen',side_effect=AssertionError('E QC forbidden')),patch('paper13_ki_execution1.models.fit_scale',side_effect=AssertionError('E scaling forbidden')):
            result=e.export(record,qc,'E-code')
        with np.load(e.ROOT/result['state_file'],allow_pickle=False) as state:
            self.assertEqual(state['counts'].shape,(30,30,8));self.assertEqual(int(state['counts'].sum()),720)
            self.assertTrue(np.all(state['unit0_times']<3))
        self.assertFalse(result['QC_scaling_selection_or_fitting_on_E']);self.assertFalse(result['final_D_exported'])

    def test_source_stop_keeps_first_complete_and_second_error(self):
        root,record,qc,raw,metadata=self.export_fixture(True)
        with patch.object(e,'P',root),patch.object(e,'approved',return_value='E-code'),patch.object(e.b,'read',side_effect=metadata),patch.object(e,'SourceReader',side_effect=lambda _:io.BytesIO(raw)):
            with self.assertRaisesRegex(ValueError,'SOURCE_INTEGRITY_STOP'):e.export(record,qc,'E-code')
        rows=[json.loads(line) for line in (root/'results/exploratory_E/synthetic.attempts.jsonl').read_text().splitlines()]
        self.assertEqual([r['event'] for r in rows],['E_EXPORT_START','E_UNIT_START','E_UNIT_COMPLETE','E_UNIT_START','E_UNIT_ERROR','E_EXPORT_ERROR'])
        self.assertFalse((root/'results/exploratory_E/synthetic.json').exists())
