import unittest
import uuid
import json
import numpy as np
from unittest.mock import patch
from . import controls_E as e


class EControlTests(unittest.TestCase):
    def test_injected_failure_retains_partial_array_and_refuses_repeat(self):
        root=e.P/'work'/('E_control_tests_'+uuid.uuid4().hex);root.mkdir(parents=True)
        mice=[str(i) for i in range(10)];data={m:(None,None,None,None) for m in mice}
        result={'scores':{name:float(j) for j,name in enumerate(e.core.LABELS)},'nominal_unit_bins':6000}
        with patch.object(e,'P',root),patch.object(e,'approved',return_value='synthetic-freeze'),patch.object(e,'inputs',return_value=({'mouse_order':mice},data)),patch.object(e.core,'replicate',side_effect=[result,ValueError('injected numerical failure')]) as call:
            with self.assertRaises(ValueError):e.run()
            gate=json.loads((root/'results/M6_E_CONTROLS_GATE.json').read_text())
            self.assertEqual(gate['attempt'],{'suite':'temporal','replicate':0,'mouse_id':'1'})
            self.assertFalse(gate['retry_or_new_random_draw_authorized'])
            array=np.load(root/'results/m6_controls_E/temporal.npy',allow_pickle=False)
            np.testing.assert_array_equal(array[0,0],np.arange(9));self.assertTrue(np.isnan(array[0,1:]).all())
            rows=[json.loads(line) for line in (root/'results/m6_controls_E/actions.jsonl').read_text().splitlines()]
            self.assertEqual(rows[-1]['event'],'CONTROL_EXECUTION_ERROR')
            self.assertEqual(sum(r['event']=='MOUSE_CONTROL_COMPLETE' for r in rows),1)
            with self.assertRaises(FileExistsError):e.run()
            self.assertEqual(call.call_count,2)

    def test_missing_approval_denies_before_neural_saved_inputs(self):
        with patch.object(e,'approved',side_effect=PermissionError('unapproved')),patch.object(e,'inputs',side_effect=AssertionError('input before approval')):
            with self.assertRaises(PermissionError):e.run()

    def test_failed_M5_denies_before_any_saved_E_arrays(self):
        with patch.object(e.b,'read',return_value={'M5':'FAIL'}),patch.object(e.np,'load',side_effect=AssertionError('values before M5')):
            with self.assertRaises(e.ScientificStop):e.inputs()

    def test_final_role_denied_before_state_loading(self):
        with patch.object(e.b,'read',return_value={'M5':'PASS','scientific_scope':'EXPLORATORY_DEVELOPMENT_ONLY_NOT_FINAL_VALIDATION','mouse_order':['final']}),patch.object(e,'ALLOCATION',[{'mouse_id':'final','role':'final'}]),patch.object(e.np,'load',side_effect=AssertionError('final values')):
            with self.assertRaises(PermissionError):e.inputs()
