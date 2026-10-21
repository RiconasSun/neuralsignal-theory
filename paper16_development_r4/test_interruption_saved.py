"""Metadata-only interruption regressions; no fitting or neural arrays."""
import contextlib
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from . import reproduce_saved as saved


@contextlib.contextmanager
def fixture():
    temp_root=saved.R/'.r4t'
    temp_root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temp_root) as directory:
        root=Path(directory);p=root/'paper16_development_r4';results=p/'results';results.mkdir(parents=True)
        e=root/'ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4';e.mkdir(parents=True)
        def write(path,value):path.write_text(json.dumps(value),encoding='utf8')
        def reference(path):return {'path':path.relative_to(root).as_posix(),'sha256':saved.sha(path)}
        task={'id':'synthetic-saved-prefix'}
        write(results/'STAGE_CLAIM.json',{'synthetic_metadata':True})
        write(results/'SUPERVISOR.json',{'supervisor_pid':1,'job_name':'fixture-job'})
        (results/'FIT_JOURNAL.jsonl').write_text(json.dumps({'event':'ATTEMPTED','task':task})+'\n')
        folder=p/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest();folder.mkdir(parents=True)
        write(folder/'ATTEMPT.json',{'task':task})
        write(p/'PARTIAL_ATTEMPT_MANIFEST.json',{'task':task,'files':[reference(folder/'ATTEMPT.json')]})
        write(e/'probe.json',{'native_supervisor_pid':1,'job_name':'fixture-job','supervisor_present':False,
            'matching_processes':[],'job_open_succeeded':False,'job_last_error':2,'no_scientific_actions':True})
        write(e/'owner.json',{'owner_reported_cause':'COMPUTER_SHUTDOWN','scientific_restart_authorized_by_this_message':False})
        receipt={'schema':'R4_EXTERNAL_INTERRUPTION_V1','scientific_verdict':'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE',
            'native_returncode':None,'termination_time':None,'cause':None,'native_supervision_available':False,
            'scientific_resumption_authorized':False,'no_retry':True,'attempts':1,'completed':0,
            'stage_claim_sha256':saved.sha(results/'STAGE_CLAIM.json'),
            'supervisor_sha256':saved.sha(results/'SUPERVISOR.json'),
            'fit_journal_sha256':saved.sha(results/'FIT_JOURNAL.jsonl'),
            'partial_manifest_sha256':saved.sha(p/'PARTIAL_ATTEMPT_MANIFEST.json'),
            'independent_native_probe':reference(e/'probe.json'),'owner_reported_cause':'COMPUTER_SHUTDOWN',
            'owner_cause_evidence':reference(e/'owner.json')}
        write(results/'EXTERNAL_INTERRUPTION_CLOSEOUT.json',receipt)
        with patch.object(saved,'R',root),patch.object(saved,'P',p):
            yield receipt,p,e,write


class InterruptionTests(unittest.TestCase):
    def test_seal_writes_create_only_manifest_and_prints_valid_receipt(self):
        import io
        from . import closeout_saved as archive
        with tempfile.TemporaryDirectory(dir=saved.R/'.r4t') as directory:
            root=Path(directory);p=root/'paper16_development_r4';(p/'work').mkdir(parents=True);(p/'results').mkdir()
            (p/'work/synthetic.json').write_text('{}');(p/'results/synthetic.json').write_text('{}')
            output=io.StringIO()
            with patch.object(archive,'R',root),patch.object(archive,'P',p),contextlib.redirect_stdout(output):
                archive.seal()
                original=(p/'PROTECTED_STATE_MANIFEST.json').read_bytes()
                with self.assertRaises(FileExistsError):archive.seal()
                self.assertEqual(original,(p/'PROTECTED_STATE_MANIFEST.json').read_bytes())
            result=json.loads(output.getvalue());self.assertEqual(result['files'],2)
            self.assertEqual(result['protected_manifest']['sha256'],saved.sha(p/'PROTECTED_STATE_MANIFEST.json'))

    def test_valid_metadata_does_not_supply_native_exit_or_scientific_pass(self):
        with fixture() as (receipt,p,e,write):
            self.assertTrue(saved.external_interruption(receipt))
            with self.assertRaises(FileNotFoundError):saved.closure_status()

    def test_unknown_native_values_cannot_be_invented(self):
        for key,value in [('native_returncode',0),('termination_time','guessed'),('cause','inferred'),
                          ('native_supervision_available',True),('no_retry',False),('scientific_resumption_authorized',True)]:
            with fixture() as (receipt,p,e,write),self.subTest(key=key),self.assertRaises(RuntimeError):
                saved.external_interruption({**receipt,key:value})
        for key in ['native_returncode','termination_time','cause']:
            with fixture() as (receipt,p,e,write),self.subTest(missing=key),self.assertRaises(RuntimeError):
                del receipt[key];saved.external_interruption(receipt)

    def test_access_denied_or_live_job_is_not_process_loss(self):
        for change in [{'job_last_error':5},{'job_open_succeeded':True},{'supervisor_present':True},
                       {'matching_processes':[{'pid':2}]},{'job_name':'other-job'},{'native_supervisor_pid':2}]:
            with fixture() as (receipt,p,e,write),self.subTest(change=change):
                path=e/'probe.json';probe=saved.load(path);probe.update(change);write(path,probe)
                receipt['independent_native_probe']['sha256']=saved.sha(path)
                with self.assertRaises(RuntimeError):saved.external_interruption(receipt)

    def test_interruption_cannot_replace_any_scientific_terminal_receipt(self):
        for name in ['SUPERVISION.json','SCIENTIFIC_STOP.json','M4_SELECTION_FREEZE.json',
                     'M4_READY_FOR_INDEPENDENT_REVIEW.json','E_BATCH_CLAIM.json','E_DEVELOPMENT_RESULTS.json','WORKER_COMPLETE.json']:
            with fixture() as (receipt,p,e,write),self.subTest(name=name):
                write(p/'results'/name,{})
                with self.assertRaises(RuntimeError):saved.external_interruption(receipt)

    def test_hash_tampering_and_unlisted_partial_files_fail_closed(self):
        for target in ['results/FIT_JOURNAL.jsonl','results/STAGE_CLAIM.json','PARTIAL_ATTEMPT_MANIFEST.json']:
            with fixture() as (receipt,p,e,write),self.subTest(target=target):
                (p/target).write_text('{}')
                with self.assertRaises(RuntimeError):saved.external_interruption(receipt)
        with fixture() as (receipt,p,e,write):
            folder=next((p/'work/fits').iterdir());write(folder/'EXTRA.json',{})
            with self.assertRaises(RuntimeError):saved.external_interruption(receipt)

    def test_complete_or_failed_endpoint_cannot_be_hidden_as_partial(self):
        for name in ['RESULT.json','DIAGNOSTICS.json','coordinate_certificates.npz','endpoint.npz','FAILURE.json']:
            with fixture() as (receipt,p,e,write),self.subTest(name=name):
                folder=next((p/'work/fits').iterdir());write(folder/name,{})
                with self.assertRaises(RuntimeError):saved.external_interruption(receipt)

    def test_missing_or_forged_independent_approval_is_rejected(self):
        with fixture() as (receipt,p,e,write):
            review=e/'review.md';review.write_text('fixture review')
            approval={'decision':'ACCEPTED_EXTERNAL_INTERRUPTION_EVIDENCE_ONLY','open_P0':0,'open_P1':0,
                'receipt_sha256':saved.sha(p/'results/EXTERNAL_INTERRUPTION_CLOSEOUT.json'),
                'reproducer_sha256':saved.sha(Path(saved.__file__)),
                'review_path':review.relative_to(saved.R).as_posix(),'review_sha256':saved.sha(review)}
            write(e/'EXTERNAL_INTERRUPTION_APPROVAL.json',approval)
            self.assertEqual(saved.closure_status(),(True,'EXTERNAL_INTERRUPTION_NATIVE_RETURN_UNKNOWN'))
            for change in [{'receipt_sha256':'0'*64},{'reproducer_sha256':'0'*64},{'review_sha256':'0'*64},
                           {'open_P1':1},{'decision':'PASS'}]:
                write(e/'EXTERNAL_INTERRUPTION_APPROVAL.json',{**approval,**change})
                with self.subTest(change=change),self.assertRaises(RuntimeError):saved.closure_status()

    def test_owner_shutdown_explanation_is_bound_and_cannot_authorize_restart(self):
        with fixture() as (receipt,p,e,write):
            owner=saved.load(e/'owner.json');owner['scientific_restart_authorized_by_this_message']=True
            write(e/'owner.json',owner);receipt['owner_cause_evidence']['sha256']=saved.sha(e/'owner.json')
            with self.assertRaises(RuntimeError):saved.external_interruption(receipt)


if __name__=='__main__':unittest.main()
