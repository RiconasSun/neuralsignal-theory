"""Closure-proof regressions with isolated fake Git/receipts; no real D read."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from paper15_final1.source import P,E,read


def module(name):
    spec=importlib.util.spec_from_file_location('p15_closeout_'+name,E/(name+'.py'))
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


class CloseoutGuards(unittest.TestCase):
    def test_dirty_checkout_never_creates_tracked_or_ignored_readback_receipt(self):
        mod=module('verify_git_readback');revision='1'*40
        def git(*args,**kwargs):
            if args[:2]==('rev-parse','HEAD') or args[:2]==('rev-parse','origin/test'):return (revision+'\n').encode()
            if args[:2]==('branch','--show-current'):return b'test\n'
            if args[:2]==('ls-remote','origin'):return (revision+'\trefs/heads/test\n').encode()
            if args[0]=='status':return b' M dirty-file\0'
            raise AssertionError('Must refuse dirty tree before diff/blob queries: '+str(args))
        for destination in [E/'FAKE_NO_WRITE.json',P/'work/FAKE_NO_WRITE.json']:
            with patch.object(mod,'git',side_effect=git),patch.object(mod,'dump') as writer:
                with self.assertRaises(AssertionError):mod.verify(revision,destination)
                writer.assert_not_called()

    def test_rename_is_examined_as_deletion_and_cannot_escape_scope(self):
        mod=module('verify_git_readback');revision='1'*40;seen=[]
        def git(*args,**kwargs):
            if args[:2]==('rev-parse','HEAD') or args[:2]==('rev-parse','origin/test'):return (revision+'\n').encode()
            if args[:2]==('branch','--show-current'):return b'test\n'
            if args[:2]==('ls-remote','origin'):return (revision+'\trefs/heads/test\n').encode()
            if args[0]=='status':return b''
            if args[0]=='diff':
                seen.append(args);self.assertIn('--no-renames',args)
                return b'historical/file.py\n' if '--diff-filter=D' in args else b'historical/file.py\0paper15_final1/new.py\0'
            raise AssertionError('Deleted history must fail before blob queries')
        with patch.object(mod,'git',side_effect=git),patch.object(mod,'dump') as writer:
            with self.assertRaises(AssertionError):mod.verify(revision,E/'FAKE_NO_WRITE.json')
            writer.assert_not_called()
        self.assertEqual(len(seen),2)

    def test_rejected_bool_or_stale_final_review_cannot_close_rows(self):
        mod=module('build_requirement_matrix')
        receipt=dict(decision='ACCEPTED_FINAL_DESCRIPTIVE_HANDOFF',open_P0=0,open_P1=0,
                     archive_sha256='hash',baseline_sha256='hash',D_claim_sha256='hash',report_path='report.md',report_sha256='hash')
        with patch.object(mod,'read',return_value=receipt),patch.object(mod,'sha',return_value='hash'):
            self.assertTrue(mod.valid_review(Path('receipt.json')))
            for change in [dict(decision='CHANGES_REQUIRED'),dict(open_P0=False),dict(open_P1=1),dict(archive_sha256='stale'),dict(report_sha256='stale')]:
                with patch.object(mod,'read',return_value=dict(receipt,**change)):
                    self.assertFalse(mod.valid_review(Path('receipt.json')))

    def test_native_reproduction_needs_actual_typed_fresh_success(self):
        mod=module('build_requirement_matrix')
        receipt=dict(status='PASS_NATIVE_POWERSHELL_SAVED_ONLY',exit_code=0,archive_sha256='hash',D_claim_sha256='hash',
                     log_path='log.txt',log_sha256='hash',command=['powershell'],
                     result=dict(saved_statistics_exact=True,tests=68,source_arrays_loaded=0,new_real_fits=0,D_reassessment=False))
        with patch.object(mod,'read',return_value=receipt),patch.object(mod,'sha',return_value='hash'):
            self.assertTrue(mod.valid_reproduction(Path('receipt.json')))
            for change in [dict(exit_code=False),dict(exit_code=1),dict(archive_sha256='old'),dict(log_sha256='old'),dict(command=['python'])]:
                with patch.object(mod,'read',return_value=dict(receipt,**change)):
                    self.assertFalse(mod.valid_reproduction(Path('receipt.json')))

    def test_H1_is_not_accepted_as_current_H2_or_with_dirty_worktree(self):
        mod=module('build_requirement_matrix')
        receipt=dict(remote_readback_verified=True,changed_blob_hashes_verified=True,working_tree_clean_before_receipt=True,commit='H2')
        with patch.object(mod,'read',return_value=receipt),patch.object(mod.subprocess,'check_output',side_effect=[b'H2\n',b'']):
            self.assertTrue(mod.valid_transport(Path('receipt.json')))
        with patch.object(mod,'read',return_value=dict(receipt,commit='H1')),patch.object(mod.subprocess,'check_output',return_value=b'H2\n'):
            self.assertFalse(mod.valid_transport(Path('receipt.json')))
        with patch.object(mod,'read',return_value=receipt),patch.object(mod.subprocess,'check_output',side_effect=[b'H2\n',b' M dirty\0']):
            self.assertFalse(mod.valid_transport(Path('receipt.json')))

    def test_311_rows_never_close_from_existing_files_or_future_H2(self):
        mod=module('build_requirement_matrix');baseline=read(E/'baseline.json')
        def fake_read(path):
            return baseline if Path(path).name=='baseline.json' else dict(D_BATCH_COMPLETE=True,ONE_SHOT_D_EXECUTED=True)
        def fake_sha(path):return baseline['source_sha256'] if Path(path).name=='OWNER_REQUEST.txt' else 'hash'
        for proofs,terminal,expected in [(False,False,0),(True,False,308),(True,True,311)]:
            with patch.object(mod,'read',side_effect=fake_read),patch.object(mod,'sha',side_effect=fake_sha),\
                 patch.object(Path,'exists',return_value=True),patch.object(mod,'valid_review',return_value=proofs),\
                 patch.object(mod,'valid_reproduction',return_value=proofs),patch.object(mod,'valid_transport',return_value=terminal),\
                 patch.object(mod,'dump') as writer:
                mod.build(terminal=terminal,output=P/'work/FAKE_NO_WRITE.json' if terminal else None)
                value=writer.call_args.args[1]
                self.assertEqual(value['verified_baseline_count'],expected)
                self.assertEqual([(r['id'],r['requirement']) for r in value['requirements']],[(r['id'],r['requirement']) for r in baseline['requirements']])
                if not terminal:
                    self.assertFalse(value['final_transport_verified']);self.assertEqual(value['status'],'CONTINUE_EXECUTION')

    def test_saved_interpretation_covers_every_contrast_and_unavailable_without_predictions(self):
        mod=module('scientific_interpretation');fixture=read(P/'results/FULL_D_SYNTHETIC_REHEARSAL.json')
        root=P/'work/interpretation_tests';root.mkdir(parents=True,exist_ok=True)
        for unavailable in [False,True]:
            stats=copy.deepcopy(fixture['statistics'])
            if unavailable:
                for c in stats:
                    if c!='B4-B1':stats[c].pop('equal_mouse_mean',None)
            delivery=dict(DEVELOPMENT_FINAL_CONSISTENCY={c:dict(Development_mean=.1,Final_mean=r.get('equal_mouse_mean')) for c,r in stats.items()})
            documents={'D_BATCH_CLAIM.json':dict(status='COMPLETE_REGISTERED_DESCRIPTIVE_D_BATCH'),
                       'D_STATISTICS.json':stats,'D_SENSITIVITY_SUMMARY.json':fixture['sensitivity_summaries'],
                       'D_CONTROL_SUMMARY.json':fixture['control_summaries'],'D_SCIENTIFIC_VERDICTS.json':fixture['claim_verdicts'],
                       'FINAL_DELIVERY.json':delivery}
            with tempfile.TemporaryDirectory(dir=root) as folder:
                target=Path(folder);(target/'FINAL_SCIENTIFIC_REPORT.md').write_text('Synthetic report fixture\n')
                with patch.object(mod,'P',target),patch.object(mod,'read',side_effect=lambda p:documents[Path(p).name]),patch.object(mod,'write_csv') as table:
                    mod.append_interpretation();text=(target/'FINAL_SCIENTIFIC_REPORT.md').read_text()
                    for contrast in fixture['statistics']:self.assertIn(contrast,text)
                    self.assertIn('DESCRIPTIVE ONLY',text);self.assertIn('Aggregate N4 has only three',text)
                    self.assertIn('S01 five-unit,S02 twelve-unit and S03 twenty-unit',text)
                    self.assertIn('S10 higher-order trial/session drift covariates',text)
                    self.assertEqual(len(table.call_args.args[1]),1 if unavailable else 6)
                    with self.assertRaises(AssertionError):mod.append_interpretation()

    def test_freeze_stdout_is_retained_but_never_self_hashed(self):
        mod=module('archive_package');root=P/'work/archive_guard_tests';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as folder:
            target=Path(folder);evidence=target/'evidence';evidence.mkdir()
            active=evidence/'ARCHIVE_FREEZE_42.log';active.write_text('')
            stable=evidence/'FAILED_SAVED_REPRODUCTION.log';stable.write_text('Preserved failed test')
            with patch.object(mod,'R',target),patch.object(mod,'E',evidence):
                paths=mod.external_evidence_paths();active.write_text('Output written after snapshot')
                self.assertNotIn('evidence/ARCHIVE_FREEZE_42.log',paths)
                self.assertIn('evidence/FAILED_SAVED_REPRODUCTION.log',paths)
                self.assertEqual(mod.external_evidence_paths(),paths)


if __name__=='__main__':unittest.main()
