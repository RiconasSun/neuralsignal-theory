import io
import json
import uuid
import unittest
from unittest.mock import patch
import h5py
import numpy as np
from . import final_D as d
from paper13_ki_execution1.sensitivity_plan import shifted


class FinalDTests(unittest.TestCase):
    def fixture(self,nonfinite_unit=None):
        root=d.P/'work'/('D_tests_'+uuid.uuid4().hex);root.mkdir(parents=True)
        epochs=[{'ordinal':i+1,'start':10.+5*i,'stop':13.+5*i,'partition':'C' if i<60 else 'D'} for i in range(120)]
        record={'mouse_id':'synthetic','role':'final','epochs':epochs}
        bundle={'mouse_id':'synthetic','training_partition':'C','units':[{'unit_id':j,'row':j} for j in range(8)],
            'sensitivity_metadata':{name:shifted(epochs,shift,[0,1000]) for name,shift in [('alignment_minus01',-.1),('alignment_plus01',.1)]}}
        model=root/'model.json';model.write_bytes(d.b.canonical(bundle)+b'\n')
        c={'models':{'synthetic':{'path':'model.json','sha256':d.sha(model.read_bytes())}}};sealed={'test':'C state'}
        raw=io.BytesIO()
        with h5py.File(raw,'w') as h:
            h['/units/id']=np.arange(8);times=[];ends=[]
            for unit in range(8):
                values=np.array([e['start']+v+unit*.001 for e in epochs for v in [-.05,.05,.15,2.95,3.05]])
                if unit==nonfinite_unit:values[0]=np.nan
                times.extend(values);ends.append(len(times))
            h['/units/spike_times']=np.array(times);h['/units/spike_times_index']=np.array(ends)
        folder=root/'results/final_D';folder.mkdir(parents=True)
        return root,record,bundle,c,sealed,raw.getvalue(),folder

    def prepare(self,root,c,sealed,folder):
        (root/'PRE_D_STOPPING_RULE_AMENDMENT.json').write_text('{}',encoding='utf8')
        return d.consume(folder,'reviewed-D-source',c,sealed)

    def patches(self,root,c,sealed,raw):
        from contextlib import ExitStack
        stack=ExitStack();stack.enter_context(patch.object(d,'P',root));stack.enter_context(patch.object(d,'ROOT',root))
        stack.enter_context(patch.object(d,'approved',return_value='reviewed-D-source'))
        original_read=d.b.read
        def read(path):
            path=str(path).replace('\\','/')
            if path.endswith('/results/FINAL_C_GATE.json'):return c
            if path.endswith('/results/FINAL_C_FULL_STATE_MANIFEST.json'):return sealed
            return original_read(path)
        stack.enter_context(patch.object(d.b,'read',side_effect=read))
        reader=stack.enter_context(patch.object(d,'SourceReader',side_effect=lambda record:io.BytesIO(raw)))
        return stack,reader

    def test_missing_approval_or_failed_prior_gate_never_consumes_or_reads_D(self):
        root,*_=self.fixture()
        with patch.object(d,'P',root),patch.object(d,'prior_gates',side_effect=AssertionError('prior before approval')),patch.object(d,'SourceReader',side_effect=AssertionError('Daccess')):
            with self.assertRaises(PermissionError):d.run()
        with patch.object(d,'approved',return_value='source'),patch.object(d,'prior_gates',side_effect=d.ScientificStop('Cfailed')),patch.object(d,'consume',side_effect=AssertionError('consumption before priorPASS')):
            with self.assertRaises(d.ScientificStop):d.run()

    def test_consumption_is_exclusive_even_before_export_or_after_crash(self):
        root,_,_,c,sealed,_,folder=self.fixture()
        with patch.object(d,'P',root):
            record=self.prepare(root,c,sealed,folder)
            with self.assertRaises(FileExistsError):d.consume(folder,'reviewed-D-source',c,sealed)
        self.assertTrue(record['no_automatic_retry_even_after_crash'])

    def test_synthetic_primary_and_alignment_exports_exclude_response_and_repeat(self):
        root,record,bundle,c,sealed,raw,folder=self.fixture();stack,reader=self.patches(root,c,sealed,raw)
        with stack:
            self.prepare(root,c,sealed,folder);receipt,sets,arrays=d.export(record,bundle,folder,folder/'actions.jsonl')
            self.assertEqual(reader.call_count,1);self.assertEqual(arrays['primary_counts'].shape,(60,30,8))
            self.assertEqual(arrays['alignment_plus01_counts'].shape,(60,29,8));self.assertEqual(arrays['alignment_minus01_counts'].shape,(60,30,8))
            self.assertEqual(int(arrays['primary_counts'].sum()),60*8*3)
            self.assertEqual(int(arrays['alignment_plus01_counts'].sum()),60*8*2)
            self.assertTrue(all(e['stop']<=e['original_tone']+1e-10 for e in sets['alignment_plus01']['epochs']))
            self.assertEqual(receipt['parent_ordinals']['primary'],list(range(61,121)))
            with self.assertRaises(FileExistsError):d.export(record,bundle,folder,folder/'actions.jsonl')
            self.assertEqual(reader.call_count,1)

    def test_tampered_model_or_consumption_denied_before_decoder(self):
        root,record,bundle,c,sealed,raw,folder=self.fixture();stack,reader=self.patches(root,c,sealed,raw)
        with stack:
            self.prepare(root,c,sealed,folder)
            changed={**bundle,'units':list(reversed(bundle['units']))}
            with self.assertRaises(PermissionError):d.export(record,changed,folder,folder/'actions.jsonl')
            marker=folder/'ONCE_EXECUTION.json';v=d.b.read(marker);v['source_freeze']='tampered';marker.write_text(json.dumps(v),encoding='utf8')
            with self.assertRaises(PermissionError):d.export(record,bundle,folder,folder/'actions.jsonl')
            self.assertEqual(reader.call_count,0)

    def test_nonfinite_source_failure_keeps_completed_unit_and_denies_second_export(self):
        root,record,bundle,c,sealed,raw,folder=self.fixture(nonfinite_unit=1);stack,reader=self.patches(root,c,sealed,raw)
        with stack:
            self.prepare(root,c,sealed,folder)
            with self.assertRaisesRegex(ValueError,'SOURCE_INTEGRITY_STOP'):d.export(record,bundle,folder,folder/'actions.jsonl')
            self.assertTrue((folder/'partial_unit_exports/synthetic/0.npz').is_file());self.assertFalse((folder/'partial_unit_exports/synthetic/1.npz').exists())
            rows=[json.loads(s) for s in (folder/'actions.jsonl').read_text().splitlines()]
            self.assertEqual(rows[-1]['event'],'D_EXPORT_ERROR');self.assertEqual(rows[-1]['unit_id'],1)
            self.assertEqual(sum(r['event']=='D_UNIT_EXPORT_COMPLETE' for r in rows),1)
            with self.assertRaises(FileExistsError):d.export(record,bundle,folder,folder/'actions.jsonl')
            self.assertEqual(reader.call_count,1)

    def test_missing_consumption_and_wrong_role_deny_before_decoder(self):
        root,record,bundle,c,sealed,raw,folder=self.fixture();stack,reader=self.patches(root,c,sealed,raw)
        with stack:
            with self.assertRaises(PermissionError):d.export(record,bundle,folder,folder/'actions.jsonl')
            with self.assertRaises(PermissionError):d.window_sets({**record,'role':'development'},bundle)
            self.assertEqual(reader.call_count,0)
