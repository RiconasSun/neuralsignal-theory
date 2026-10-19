"""Owned synthetic fourth-source end-to-end: exact suffix then saved-prefix resume."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from paper16_dev_r3 import test_neural as fixture_module
from .core import P,R,load,save_arrays,sha
from .transport import Journal
from .run_sources import process_source
from .test_transport import stage,Response


class FourthSourceIntegration(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=P/'work/private',prefix='synthetic-integration-');self.root=Path(self.temp.name)
        self.reg=load(P/'ACCESS_REGISTRATION.json');fixture_reg=copy.deepcopy(self.reg);fixture_reg['objects']=[self.reg['objects'][3]]
        self.fixture_host=self.root/'fixture';(self.fixture_host/'work').mkdir(parents=True)
        (self.fixture_host/'ACCESS_REGISTRATION.json').write_text(json.dumps(fixture_reg),encoding='utf8')
        self.fixture_patch=patch.object(fixture_module,'P',self.fixture_host);self.fixture_patch.start()
        self.fixture=fixture_module.NativeReaderTests();self.fixture.setUp()
        old=self.fixture.run_reader()['units'];captures=self.fixture.persisted[:2];self.reused=[]
        self.history=self.root/'history';self.item=copy.deepcopy(self.fixture.item)
        data=self.fixture.path.read_bytes();self.item['size']=len(data);self.reg['objects'][3]=self.item
        self.prefix_bytes=len(data)//3;prefix=self.history/'work/private/ranges'/str(self.item['session_id'])/'0.bin'
        prefix.parent.mkdir(parents=True);prefix.write_bytes(data[:self.prefix_bytes]);self.prefix=prefix
        self.reg['recovery'].update({'old_offset':0,'old_length':len(data),'prefix_length':self.prefix_bytes,
            'prefix_path':prefix.relative_to(R).as_posix(),'prefix_sha256':sha(prefix),'suffix_offset':self.prefix_bytes,
            'suffix_length':len(data)-self.prefix_bytes,'historical_completed_candidates':2,'backoff_seconds':0})
        folder=self.history/'results/sources'/str(self.item['session_id']);folder.mkdir(parents=True)
        for prior,(_,arrays,_) in zip(old[:2],captures):
            path=self.history/'work/private/A'/str(self.item['session_id'])/(str(prior['unit_id'])+'.npz');path.parent.mkdir(parents=True,exist_ok=True)
            prior=copy.deepcopy(prior);prior['private_A_capture']={'private_path':path.relative_to(R).as_posix(),**save_arrays(path,arrays)};self.reused.append(prior)
        self.raw=(''.join(json.dumps(x)+'\n' for x in self.reused)).encode()
        (folder/'UNIT_QC.jsonl').write_bytes(self.raw)
        (self.history/'SOURCE_CANDIDATE_CERTIFICATES.json').write_text(json.dumps({'candidates':[{'session_id':sid,'unit_id':uid,**cert} for (sid,uid),cert in self.fixture.certs.items()]}),encoding='utf8')
        self.e=self.root/'evidence';self.e.mkdir();(self.e/'PREACCESS_APPROVAL.json').write_text('OWNED SYNTHETIC ONLY',encoding='utf8')
        (self.root/'ACCESS_REGISTRATION.json').write_text(json.dumps(self.reg),encoding='utf8')
        self.data=data;self.gets=[]
    def tearDown(self):self.fixture.tearDown();self.fixture_patch.stop();self.temp.cleanup()
    def test_HEAD_suffix_reconstruction_then_only_new_candidate_payloads(self):
        def get(url,**kw):
            self.gets.append(kw);start=kw['params']['p16_r4_offset'];length=kw['params']['p16_r4_length']
            return Response(self.data[start:start+length],start,length,self.item)
        head=Response(b'',0,0,self.item,status=200);head.headers={'ETag':self.item['etag'],'Content-Length':str(len(self.data))}
        inputs=(self.fixture.header,self.fixture.flashes,{'missing':np.zeros((150,6),dtype=bool)},{'synthetic':True})
        journal=Journal(self.root/'journal.jsonl',self.reg)
        try:
            with patch('paper16_source_r4.run_sources.P',self.root),patch('paper16_source_r4.run_sources.E',self.e), \
                 patch('paper16_source_r4.run_sources.S',self.history),patch('paper16_source_r4.core.S',self.history), \
                 patch('paper16_source_r4.transport.P',self.root),patch('paper16_source_r4.transport.S',self.history), \
                 patch('paper16_source_r4.core.source_inputs',return_value=inputs),patch('paper16_source_r4.run_sources.source_inputs',return_value=inputs), \
                 patch('requests.Session.get',side_effect=get),patch('requests.Session.head',return_value=head), \
                 patch('socket.socket.connect',side_effect=AssertionError('No actual network')):
                result=process_source(self.item,self.reg,stage(),journal,fourth=True)
        finally:journal.close()
        self.assertEqual(len(self.gets),1);self.assertEqual(self.gets[0]['headers']['Range'],f'bytes={self.prefix_bytes}-{len(self.data)-1}')
        self.assertEqual(result['new_R4_candidate_states'],6);self.assertEqual(result['historical_R3_candidate_states_reused'],2)
        self.assertTrue(result['source_pass']);self.assertTrue(result['selection']['admitted'])
        folder=self.root/'results/sources'/str(self.item['session_id'])
        self.assertTrue((folder/'UNIT_QC.jsonl').read_bytes().startswith(self.raw))
        self.assertEqual(self.prefix.read_bytes(),self.data[:self.prefix_bytes])
        trace=json.loads((folder/'VALUE_READS.json').read_text(encoding='utf8'))
        self.assertEqual(len([x for x in trace if x['path']=='/units/spike_times']),6)
        self.assertFalse(result['B_E_arrays_exported']);self.assertEqual(result['model_fits'],0)


if __name__=='__main__':unittest.main(verbosity=2)
