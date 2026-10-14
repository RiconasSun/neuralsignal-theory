"""Regression and completeness tests over immutable public artifacts."""
import json
from pathlib import Path
import unittest
import numpy as np
import study as r
from glm import raw,scale,transform
class SavedTests(unittest.TestCase):
    def test_reuse_covariates_identical_after_subsetting(self):
        y=np.random.default_rng(2).poisson(.4,(8,20,5));c=np.arange(8);o=np.arange(8);a=raw(y,c,o);a=transform(a,scale(a));b=raw(y[:,:,[0,2,4]],c,o);b=transform(b,scale(b))
        np.testing.assert_allclose(a[:,:,[0,2,4],:34],b[:,:,:,:34],atol=1e-12,rtol=0)
    def test_no_protocol_change(self):self.assertEqual(r.sha(r.HERE/'PROTOCOL.md'),r.load(r.HERE/'protocol_registration.json')['protocol_sha256'])
    def test_preregistration_source_bindings(self):
        for phase in ('science','original_pg_certificate'):
            for n,d in r.load(r.HERE/(phase+'_execution_registration.json'))['source_sha256'].items():self.assertEqual(r.sha(r.HERE/n),d,n)
    def test_model_roster_and_every_endpoint(self):
        gate=r.load(r.HERE/'results/science/native/gate_result.json');files=list((r.HERE/'results/science/native').glob('*_fit.json'));self.assertEqual(len(files),gate['new_model_cases']);attempts=0
        for p in files:
            z=r.load(p);self.assertTrue(z['passed']);self.assertTrue(z['records'])
            for v in z['records']:
                attempts+=1;self.assertTrue(v['passed']);self.assertTrue(v['optimizer_success']);self.assertLessEqual(v['PG'],.001);self.assertLessEqual(v['AD_PG'],.001);self.assertLessEqual(v['AD_scaled_error'],1e-5);self.assertTrue(v['finite'] and v['bounds']);self.assertLessEqual(v['iterations'],100);self.assertLessEqual(v['objective_calls'],4000)
        self.assertEqual(attempts,gate['new_unit_fit_attempts'])
    def test_exact_sources_and_old_fit_hashes(self):
        registration=r.load(r.HERE/'preflight_execution_registration.json')
        for n,d in registration['M3_fit_sha256'].items():self.assertEqual(r.sha(r.ROOT/'paper12_m3num1/results/full'/n),d)
    def test_native_receipts_and_probes(self):
        for phase in ('preflight_corrected','science','original_pg_certificate'):
            receipt=r.load(r.HERE/f'results/{phase}_launch_receipt.json');proof=r.load(r.HERE/f'results/{phase}/native/role_proof.json')
            self.assertEqual(receipt['exit_code'],0);self.assertFalse(receipt['timed_out']);self.assertTrue(receipt['role_proof_pass']);self.assertEqual(receipt['profile_cleanup_hresult'],'0x00000000');self.assertTrue(proof['pass']);self.assertEqual(proof['capability_count'],0);self.assertFalse(receipt['final_holdout_evaluated'] or receipt['final_values_exposed_to_analysis'])
    def test_sensitivity_minima_and_fixed_mice(self):
        cov=r.load(r.HERE/'results/preflight_corrected/native/coverage.json');self.assertEqual(len(cov['mice']),13)
        for n in ('primary','matched16','rate_matched','boundary20','boundary40'):self.assertGreaterEqual(cov['paired_counts'][n],8)
        rows=r.load(r.HERE/'results/science/native/scientific_scores.json')['rows'];self.assertEqual(len({z['mouse_id'] for z in rows}),13)
        for z in rows:self.assertEqual(z['B_unit_bins'],z['B_trials']*20*z['units'])
    def test_complete_nulls_no_refits(self):
        gate=r.load(r.HERE/'results/nulls_complete/native/gate_result.json');self.assertEqual(gate['cases'],104);self.assertEqual(gate['null_evaluations'],104*999);self.assertEqual(gate['count_preservation_checks'],26*999);self.assertEqual(gate['new_fits'],0)
        files=[p for p in (r.HERE/'results/nulls_complete/native').glob('*.json') if p.stem[-2:] in ('_T','_S','_B','_O')];self.assertEqual(len(files),104)
        for p in files:
            z=r.load(p);self.assertEqual(len(z['gains']),999);self.assertFalse(z['trial_assignment_changed']);self.assertEqual(z['null_refits'],0);self.assertTrue(np.isfinite(z['gains']).all())
            primary=next(q for q in r.load(r.HERE/'results/science/native/scientific_scores.json')['rows'] if q['session_id']==z['session_id'] and q['region']==z['region'] and q['view']=='primary')
            np.testing.assert_allclose(z['observed'],[primary['gains'][k] for k in ('own','population','stimulus_time','combined')],atol=1e-10,rtol=0)
    def test_primary_all_four_unselected(self):
        s=r.load(r.HERE/'results/primary_statistics.json')['primary'];self.assertEqual(len(s['statistics']),4);self.assertEqual(len(s['mouse_ids']),13)
        for v in s['statistics'].values():self.assertEqual(v['mice'],13);self.assertEqual(v['bootstrap_replicates'],10000);self.assertEqual(len(v['leave_one_mouse_out_means']),13);self.assertGreaterEqual(v['holm_p'],v['paired_signflip_p'])
    def test_original_failed_preflights_retained(self):
        for phase in ('preflight','preflight_observed'):self.assertEqual(r.load(r.HERE/f'results/{phase}_launch_receipt.json')['exit_code'],1)
        self.assertEqual(r.load(r.HERE/'results/preflight_observed/native/failure.json')['message'],'FROZEN_COUNT_SHAPE')
    def test_failed_null_role_and_complete_isolated_jobs(self):
        self.assertEqual(r.load(r.HERE/'results/nulls_launch_receipt.json')['exit_code'],1);self.assertEqual(r.load(r.HERE/'results/nulls/native/failure.json')['type'],'PermissionError')
        reg=r.load(r.HERE/'null_resume_registration.json')
        for p,d in reg['completed_case_sha256'].items():self.assertEqual(r.sha(r.HERE/'results/nulls_complete/native'/p),d)
        for job in reg['jobs']:
            here=r.HERE/'jobs'/job['job'];receipt=r.load(here/'results/nulls_launch_receipt.json');proof=r.load(here/'results/nulls/native/role_proof.json');self.assertEqual(receipt['exit_code'],0);self.assertFalse(receipt['timed_out']);self.assertTrue(proof['pass']);self.assertEqual(proof['capability_count'],0);self.assertEqual(receipt['profile_cleanup_hresult'],'0x00000000')
if __name__=='__main__':unittest.main()
