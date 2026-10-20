"""Saved-only R3 closeout checks. No scientific worker, objective or transport."""
import json,socket,sys,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from . import reproduce as saved
R=saved.R;P=saved.P
E=R/'ops/evidence/2026-10-19/p16-m3-m5-metadata-compat-and-development-r3'

def identities(manifest):
    for row in manifest['files']:
        path=R/row['path']
        saved.require(path.is_file() and saved.sha(path)==row['sha256'],'Missing/corrupt archive payload: '+row['path'])
        if 'bytes' in row:saved.require(path.stat().st_size==row['bytes'],'Archive bytes: '+row['path'])

def original_gate(state,pg,checks):
    saved.require(state['projected_gradient_inf']==pg,'Saved PG summary')
    passed=bool(pg<=1e-5 and checks)
    saved.require(state['numerical_pass']==passed,'Original numerical conjunction')
    return passed

def failure_evidence():
    summary=saved.load(P/'NUMERICAL_FAILURE_SUMMARY.json');folder=R/summary['folder']
    result=saved.fit(folder);x,g,checks=saved.certificate(folder)
    with np.load(folder/'initial.npz',allow_pickle=False) as a:lo=a['lo'];hi=a['hi']
    pg=g.copy();pg[(x<=lo+1e-12)&(g>0)]=0;pg[(x>=hi-1e-12)&(g<0)]=0
    norm=float(np.abs(pg).max())
    saved.require(not original_gate(result,norm,checks),'Required failure must remain rejected')
    saved.require(result['success'] and checks and norm>1e-5,'Optimizer success and gradient checks do not clear PG')
    saved.require(summary['PG']==norm and summary['task']==result['task'],'Failure summary binding')
    return result,norm,checks

class StopRegressions(unittest.TestCase):
    def test_saved_success_and_good_derivatives_do_not_clear_failed_PG(self):
        result,pg,checks=failure_evidence();self.assertFalse(original_gate(result,pg,checks))
    def test_false_pass_and_altered_PG_summary_are_rejected(self):
        result,pg,checks=failure_evidence()
        with self.assertRaises(RuntimeError):original_gate({**result,'numerical_pass':True},pg,checks)
        with self.assertRaises(RuntimeError):original_gate({**result,'projected_gradient_inf':0.},pg,checks)
    def test_missing_and_corrupt_payload_fail_closed(self):
        row=saved.load(P/'PREFIT_FREEZE_MANIFEST.json')['files'][0]
        with patch.object(saved,'sha',return_value='0'*64):
            with self.assertRaises(RuntimeError):identities({'files':[row]})
        with self.assertRaises(RuntimeError):identities({'files':[{'path':'paper16_development_r3/DOES_NOT_EXIST','sha256':'0'*64}]})
    def test_outward_bound_rule_retains_inward_gradients(self):
        x=np.array([-1.,1.,-1.,1.]);g=np.array([2.,-3.,-4.,5.]);p=g.copy()
        p[(x<=-1+1e-12)&(g>0)]=0;p[(x>=1-1e-12)&(g<0)]=0
        np.testing.assert_array_equal(p,[0.,0.,-4.,5.])

def verify():
    identities(saved.load(P/'ARCHIVE_MANIFEST.json'))
    identities(saved.load(P/'PREFIT_FREEZE_MANIFEST.json'))
    identities(saved.load(P/'PROTECTED_STATE_MANIFEST.json'))
    for path,digest in saved.load(P/'SOURCE_PINS.json')['files'].items():saved.require(saved.sha(R/path)==digest,'Inherited identity: '+path)
    snapshot=E/'PHASE_A_ATTEMPT_1'
    old=saved.load(snapshot/'PRESERVATION.json')
    for row in old['files']:saved.require(saved.sha(snapshot/'payload'/row['path'])==row['sha256'],'Original failed candidate preservation')
    phase_a=saved.load(E/'PHASE_A_APPROVAL.json');identities(phase_a)
    saved.require(saved.sha(R/phase_a['review_path'])==phase_a['review_sha256'],'Independent compatibility review')
    phase_b=saved.load(E/'PREFIT_APPROVAL.json')
    saved.require(saved.sha(R/phase_b['review_path'])==phase_b['review_sha256'] and saved.sha(P/'PREFIT_FREEZE_MANIFEST.json')==phase_b['manifest_sha256'],'Independent prefit review')
    f=saved.facts();saved.require(f==saved.load(P/'EXECUTION_FACTS.json'),'Saved execution facts')
    saved.require((f['optimizer_attempts'],f['completed_optimizer_tasks'],f['numerically_failed_optimizer_tasks'],f['incomplete_optimizer_tasks'])==(953,953,1,0),'Exact attempt reconciliation')
    saved.require((f['analytic_B0_certificates'],f['B_access_sessions'],f['E_access_sessions'],len(f['unattempted_optimizer_tasks']))==(216,27,0,5518),'Coverage and stopped tasks')
    allowed={x['session_id'] for x in saved.load(P/'ACCESS_REGISTRATION.json')['objects']}
    access=saved.rows(P/'results/ACCESS.jsonl')
    saved.require(all(r['role'] in ['A','B'] and r['session_id'] in allowed for r in access),'No E/Final neural export')
    for name in ['E_BATCH_CLAIM.json','M4_SELECTION_FREEZE.json','WORKER_COMPLETE.json','E_DEVELOPMENT_RESULTS.json']:
        saved.require(not (P/'results'/name).exists(),'No retrospective M4/E completion: '+name)
    stop=saved.load(P/'results/SCIENTIFIC_STOP.json')
    saved.require(stop['scientific_status']=='STOP_NUMERICAL_REQUIRED_GATE' and stop['no_retry'],'Original STOP retained')
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(StopRegressions)
    result=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite)
    saved.require(result.wasSuccessful() and result.testsRun==4 and not result.skipped,'Saved-only regressions')
    print(json.dumps({'saved_only_reproduction':'PASS','archive_files':len(saved.load(P/'ARCHIVE_MANIFEST.json')['files']),'protected_files':len(saved.load(P/'PROTECTED_STATE_MANIFEST.json')['files']),'optimizer_attempts':953,'numerical_passes':952,'required_failure':1,'unattempted':5518,'analytic_B0_certificates':216,'B_sessions':27,'E_sessions':0,'new_fits':0,'new_derivative_experiments':0,'new_source_requests':0,'Final_C_D_access':False}))

if __name__=='__main__':
    with patch.object(socket.socket,'connect',side_effect=RuntimeError('Saved-only reproduction forbids network')):verify()
