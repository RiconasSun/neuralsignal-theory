"""Synthetic interruption retention; no source/network or neural data access."""
import json
import uuid
import unittest
from unittest.mock import patch
import numpy as np
from .source import P
from . import qc


class JournalTests(unittest.TestCase):
    def fixture(self):
        root=P/'work'/('qc_journal_'+uuid.uuid4().hex);root.mkdir(parents=True)
        record={'mouse_id':'synthetic','QC_partition':'C'}
        units=[{'unit_id':i,'row':i,'label':'PL5'} for i in range(3)]
        return root,record,units

    def test_mid_mouse_source_stop_preserves_earlier_failed_QC(self):
        root,record,units=self.fixture();path=qc.begin_mouse(root,record,'frozen')
        with patch.object(qc,'node',return_value=np.arange(3)),patch.object(qc,'unit_window_export',
                side_effect=[[np.array([])]*60,ValueError('SOURCE_INTEGRITY_STOP: nonfinite/unassignable source timestamp')]) as export:
            _,first=qc.examine_unit(None,units[0],record,'C',path)
            self.assertFalse(first['pass'])
            with self.assertRaisesRegex(ValueError,'SOURCE_INTEGRITY_STOP'):
                for unit in units[1:]:qc.examine_unit(None,unit,record,'C',path)
            self.assertEqual(export.call_count,2)
        rows=[json.loads(x) for x in path.read_text().splitlines()]
        self.assertEqual([x['event'] for x in rows],['MOUSE_START','UNIT_START','UNIT_COMPLETE','UNIT_START','UNIT_ERROR'])
        self.assertEqual(rows[2]['QC'],first);self.assertEqual(rows[-1]['unit_id'],1)
        self.assertNotIn('nonfinite',path.read_text());self.assertFalse((root/'synthetic.json').exists())

    def test_interrupted_or_repeated_start_refused_without_overwrite(self):
        root,record,_=self.fixture();path=qc.begin_mouse(root,record,'original')
        before=path.read_bytes()
        with self.assertRaises(FileExistsError):qc.begin_mouse(root,record,'new')
        self.assertEqual(path.read_bytes(),before)

    def test_passing_unit_record_and_fsync(self):
        root,record,units=self.fixture();path=qc.begin_mouse(root,record,'frozen')
        windows=[np.array([.1,1.1,2.1]) for _ in range(60)]
        with patch.object(qc,'node',return_value=np.arange(3)),patch.object(qc,'unit_window_export',return_value=windows),patch.object(qc.os,'fsync',wraps=qc.os.fsync) as sync:
            times,result=qc.examine_unit(None,units[0],record,'C',path)
            self.assertTrue(result['pass']);self.assertIs(times,windows);self.assertEqual(sync.call_count,2)
        row=json.loads(path.read_text().splitlines()[-1])
        self.assertEqual(row['event'],'UNIT_COMPLETE');self.assertEqual(row['QC']['training_spikes'],180)

    def test_completed_reuse_requires_intact_completion_and_state(self):
        root,record,_=self.fixture();journal=qc.begin_mouse(root,record,'frozen')
        state=root/'training.npz';state.write_bytes(b'synthetic-state')
        result={'source_freeze':'frozen','training_state_file':str(state),'training_state_sha256':qc.sha(state.read_bytes())}
        path=root/'synthetic.json';path.write_text(json.dumps(result))
        with self.assertRaisesRegex(ValueError,'Incomplete QC'):qc.completed_result(path,'frozen')
        qc.durable_record(journal,'MOUSE_COMPLETE',result_sha256=qc.sha(path.read_bytes()),training_state_sha256=result['training_state_sha256'])
        self.assertEqual(qc.completed_result(path,'frozen'),result)
        with self.assertRaisesRegex(ValueError,'changed extraction'):qc.completed_result(path,'other')
        state.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'QC state receipt'):qc.completed_result(path,'frozen')
        state.write_bytes(b'synthetic-state');path.write_text(json.dumps({**result,'extra':'tamper'}))
        with self.assertRaisesRegex(ValueError,'QC result receipt'):qc.completed_result(path,'frozen')


if __name__=='__main__':unittest.main(verbosity=2)
