"""Prospective scientific, metadata, authority and fail-closed regression oracles.

All numerical arrays are synthetic. Original final metadata is public and read-only.
No fitting function, original neural count loader or REAL key is invoked.
"""
import copy
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from .common import *
from . import study as r
from .authority import fingerprint,inspect_public_key,require_real_authority
from .frozen_math import load
from .scientific_evaluator import verdict,rate_report
from .production_broker import preflight,VerifiedContext

class ScientificTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.math=load()
    def test_original_sources_and_frozen_nesting(self):
        r.verify();g=self.math['glm'];self.assertEqual(g.CONTRASTS['own'],('F','NP'));self.assertEqual(g.CONTRASTS['population'],('F','NH'));self.assertEqual(g.CONTRASTS['stimulus_time'],('F','OHP'));self.assertEqual(g.CONTRASTS['combined'],('F','O'))
        self.assertTrue(set(g.MODELS['NH'])<set(g.MODELS['F']));self.assertTrue(set(g.MODELS['NP'])<set(g.MODELS['F']))
    def test_history_causality_trial_reset_and_other_excludes_self(self):
        g=self.math['glm'];y=np.zeros((8,20,4));y[0,2,0]=4;c=np.arange(8);o=np.arange(8);x=g.raw(y,c,o)
        self.assertEqual(x[0,2,0,29],0);self.assertAlmostEqual(x[0,3,0,29],np.log(5));self.assertEqual(x[1,0,0,29],0)
        self.assertEqual(x[0,3,0,34],0);self.assertAlmostEqual(x[0,3,1,34],np.log(5)/3)
        self.assertTrue(np.all(x[...,:29]==g.raw(np.zeros_like(y),c,o)[...,:29]))
    def test_score_normalization_and_full_poisson_constant(self):
        from scipy.special import gammaln
        g=self.math['glm'];y=np.ones((8,20,4))*2;x=g.raw(y,np.arange(8),np.arange(8));w=np.zeros((4,39));w[:,0]=np.log(2)
        self.assertAlmostEqual(g.score(y,x,w),float((y*np.log(2)-2-gammaln(y+1)).mean()),places=14)
        self.assertEqual(g.gains(dict.fromkeys(g.MODELS,3.))['own'],0)
    def test_original_PG_and_independent_AD_without_fitting(self):
        g=self.math['glm'];rng=np.random.default_rng(1);x=np.c_[np.ones(40),rng.normal(size=(40,4))];y=rng.poisson(.4,40);theta=rng.normal(size=5)*.03
        f,grad=g.obj(theta,x,y);af,ag=g.independent_ad(theta,x,y);self.assertLess(abs(f-af),1e-10);self.assertLess(float(np.max(abs(grad-ag))),1e-5)
        self.assertEqual(g.pg(np.array([8.,-8.]),np.array([-2.,2.])),0);self.assertEqual(g.pg(np.array([8.,-8.]),np.array([2.,-2.])),2)
    def test_score_null_kernel_and_cache_parity(self):
        g=self.math['glm'];n=self.math['nulls'];rng=np.random.default_rng(4);y=rng.poisson(.25,(24,20,4));c=np.arange(24)%8;o=np.arange(24)*20;x=g.raw(y,c,o);ms=g.scale(x);w=np.zeros((6,4,39))
        for i,name in enumerate(n.NAMES):w[i,:,g.MODELS[name]]=0 # All coefficients are deliberately null.
        w[:,:,0]=np.log(.25);original=n.eta(y,c,o,w,ms)
        scores={name:g.score(y,g.transform(x,ms),w[i]) for i,name in enumerate(n.NAMES)};np.testing.assert_allclose(n.get_gains(y,original),[g.gains(scores)[k] for k in PRIMARY],atol=1e-12,rtol=0)
        cache=self.math['null_cache'].Cache(y,c,o,w,ms)
        for suite in ('S','B','O'):
            cc,oo,bb=n.permute_labels(c,o,suite,n.rng('synthetic','CA1',suite,0));np.testing.assert_allclose(cache.predict(cc,oo,bb,suite),n.eta(y,cc,oo,w,ms,bb),atol=1e-12,rtol=0)
        changed=n.temporal(y,original[n.NAMES.index('N')],n.rng('synthetic','CA1','T',0));np.testing.assert_array_equal(changed.sum(1),y.sum(1))
    def test_exact_signs_Holm_and_bootstrap(self):
        s=self.math['mouse_statistics'];v=s.paired(np.ones(13));self.assertEqual(v['signflip_assignments'],8192);self.assertEqual(v['paired_signflip_p'],2/8192);self.assertEqual(v['bootstrap_replicates'],10000);self.assertEqual(v['CI95'],[1,1]);self.assertEqual(s.holm([.01,.04,.02,.7]),[.04,.08,.06,.7])
        with self.assertRaisesRegex(ValueError,'MINIMUM_EIGHT'):s.paired(np.ones(7))
    def fixtures(self):
        stats={v:{'mice':13,'statistics':{k:{'mean_CA1_minus_DG':DEV_SIGN[k],'CI95':[.5,1.5] if DEV_SIGN[k]>0 else [-1.5,-.5],'holm_p':.01,'leave_one_mouse_out_means':[DEV_SIGN[k]]*13} for k in PRIMARY}} for v in MANDATORY}
        nulls={suite+'_'+k:{'pooled_holm_p':.01,'regional_holm_p':.01} for suite in ('T','S','B','O') for k in PRIMARY};return stats,nulls
    def test_all_four_positive_criteria(self):
        a,b=self.fixtures();self.assertTrue(all(v['registered_criteria_satisfied'] for v in verdict(a,b,True).values()))
    def test_each_required_claim_gate_and_negative_retention(self):
        for gate in ('p','ci','direction','sensitivity','lomo','source','coverage','null'):
            a,b=self.fixtures();source=True
            if gate=='p':a['primary']['statistics']['own']['holm_p']=.050001
            if gate=='ci':a['primary']['statistics']['own']['CI95']=[0,2]
            if gate=='direction':a['primary']['statistics']['own']['mean_CA1_minus_DG']=-1
            if gate=='sensitivity':a['boundary40']['statistics']['own']['mean_CA1_minus_DG']=-1
            if gate=='lomo':a['primary']['statistics']['own']['leave_one_mouse_out_means'][0]=0
            if gate=='source':source=False
            if gate=='coverage':a['rate_matched']['mice']=7
            if gate=='null':b['T_own']['regional_holm_p']=.050001
            self.assertFalse(verdict(a,b,source)['own']['registered_criteria_satisfied'],gate)
    def test_same_suite_control_not_cross_suite_or_order_rescue(self):
        a,b=self.fixtures()
        for suite in ('T','S','B'):b[suite+'_stimulus_time']={'pooled_holm_p':.01,'regional_holm_p':1.}
        b['B_stimulus_time']={'pooled_holm_p':1.,'regional_holm_p':.01}
        self.assertFalse(verdict(a,b,True)['stimulus_time']['registered_criteria_satisfied'])
        b['B_stimulus_time']={'pooled_holm_p':.05,'regional_holm_p':.05};self.assertTrue(verdict(a,b,True)['stimulus_time']['registered_criteria_satisfied'])
    def test_saved_roster_rate_limits_and_no_D_selection(self):
        roster=read_json(r.SAVED/'provenance_roster.json');report=rate_report(roster);self.assertEqual(len(report['rows']),13);self.assertTrue(all(v['within_original_log2'] for v in report['rows']));self.assertEqual(report['rate_source'],'C_ONLY')

class BoundaryTests(unittest.TestCase):
    def test_synthetic_authorization_ID_uuid_property_regression(self):
        from .run_synthetic import synthetic_authorization_id
        values=[synthetic_authorization_id() for _ in range(8)];self.assertEqual(len(set(values)),8)
        self.assertTrue(all(isinstance(v,str) and len(v)==32 and all(x in '0123456789abcdef' for x in v) for v in values))
    def test_original_custody_metadata_catalog_no_neural_opens(self):
        from .real_metadata import materialize
        from .custodian_producer import validate_catalog
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'binding';receipt=materialize(root);self.assertEqual(receipt['mice'],13);self.assertGreater(receipt['distinct_custody_roots'],1);validate_catalog(root,{'realm':'REAL_D'})
            p=read_json(root/'source_catalog.json');mouse=p['cohort'][0];p['sessions'][mouse]['context']['unit_lock_sha256']='0'*64;(root/'source_catalog.json').write_bytes(canonical(p))
            with self.assertRaisesRegex(PermissionError,'ORIGINAL_CUSTODY'):validate_catalog(root,{'realm':'REAL_D'})
    def test_exact_real_13_and_359_C_public_metadata_only(self):
        m=read_json(r.EVIDENCE.parent.parent/'2026-10-14/p12-c-seal-host-import-repair-1/complete_C_state_manifest.json');a=read_json(r.ROOT/'paper12_curated_v1/locks/animals.json');t=read_json(r.ROOT/'paper12_curated_v1/locks/trials.json');p=read_json(r.ROOT/'paper12_controls1/final_D_partition_manifest.json');p=copy.deepcopy(p);p['cohort']=m['cohort'];p['sessions']={};conditions=sorted({v['condition'] for v in t})
        for animal in [v for v in a if v['group']=='final']:
            rows=[v for v in t if v['session_id']==animal['session_id'] and v['partition']=='locked_evaluation' and v['metadata_admitted']];p['sessions'][animal['mouse_id']]={'session_id':animal['session_id'],'trial_ids':[v['trial_id'] for v in rows],'conditions':[conditions.index(v['condition']) for v in rows],'orders':[v['provider_row_index'] for v in rows]}
        self.assertEqual(len(m['cases']),290);self.assertEqual(sorted(set(len(c['trial_ids']) for c in m['cases'])),[359,360]);self.assertEqual(len({c['mouse_id'] for c in m['cases'] if len(c['trial_ids'])==359}),3);self.assertTrue(validate_partition(m,p,a,t));self.assertTrue(all(len(v)==240 for v in p['D_trial_ids'].values()))
        for mode in ('duplicate','extra','missing','overlap','condition','order','cohort'):
            q=copy.deepcopy(p);mouse=m['cohort'][0]
            if mode=='duplicate':q['D_trial_ids'][mouse][1]=q['D_trial_ids'][mouse][0]
            if mode=='extra':q['D_trial_ids'][mouse].append('EXTRA')
            if mode=='missing':q['D_trial_ids'][mouse].pop()
            if mode=='overlap':q['D_trial_ids'][mouse][0]=next(c for c in m['cases'] if c['mouse_id']==mouse)['trial_ids'][0]
            if mode=='condition':q['sessions'][mouse]['conditions'][0]=99
            if mode=='order':q['sessions'][mouse]['orders'][0]=599
            if mode=='cohort':q['cohort']=q['cohort'][::-1]
            with self.assertRaises(PermissionError,msg=mode):validate_partition(m,q,a,t)
    def test_AAD_original_cipher_compatibility_and_tamper(self):
        from paper12_custody1.cipher_core import seal,unseal
        from cryptography.exceptions import InvalidTag
        context={'study':'P12-M2-ISOLATED-CUSTODY-1','mouse':'synthetic','source_etag':'synthetic','trial_lock_sha256':'a'*64,'unit_lock_sha256':'b'*64,'compartment':'D','shape':[2,20,4],'dtype':'<u4'}
        key=bytes(range(32));raw=np.ones((2,20,4),dtype='<u4').tobytes();cipher=seal(key,raw,context);self.assertEqual(unseal(key,cipher,context),raw)
        with self.assertRaises(InvalidTag):unseal(key,cipher,dict(context,trial_lock_sha256='c'*64))
    def test_public_fingerprint_length_and_independent_match(self):
        public='ab'*32;found=fingerprint(public);self.assertEqual(inspect_public_key(public,found,found)['status'],'CANDIDATE_VERIFIED_NOT_ACTIVATED')
        for bad in ('00','zz'):
            with self.assertRaises(PermissionError):fingerprint(bad)
        with self.assertRaises(PermissionError):inspect_public_key(public,found,'0'*64)
    def test_REAL_authority_pending_before_any_file_open(self):
        with patch.object(Path,'read_bytes',side_effect=AssertionError('NO_READ')),patch.object(Path,'read_text',side_effect=AssertionError('NO_READ')):
            with self.assertRaisesRegex(PermissionError,'AUTHORITY_PENDING'):require_real_authority('UNOPENED',None,'UNOPENED')
    def test_plain_caller_configuration_and_context_mutation_denied(self):
        with self.assertRaisesRegex(PermissionError,'REGISTERED_HOST_DEPLOYMENT'):preflight({'realm':'REAL_D'},lambda x:None)
        c=VerifiedContext({'a':[1]});v=c['a'];v.append(2);self.assertEqual(c['a'],[1])
        with self.assertRaises(TypeError):c._encoded=b'FORGE'
    def test_host_dependency_drift_individually_denied(self):
        from .production_broker import host_identity
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);expected={}
            for name in ('common.py','native_host.py','authority.py','production_broker.py'):(root/name).write_bytes(b'PINNED');expected[name]=sha(root/name)
            host_identity(root,expected)
            for name in expected:
                (root/name).write_bytes(b'ALTERED')
                with self.assertRaisesRegex(PermissionError,'HOST_PRODUCTION_CODE_DRIFT'):host_identity(root,expected)
                (root/name).write_bytes(b'PINNED')
    def test_incomplete_code_identity_rejected_before_path_checks(self):
        from .production_broker import complete_code_identity
        for value in ({},{'source_sha256':{}},{'source_sha256':{},'target_code_sha256':{},'controller_code_sha256':{},'new_source_freeze_sha256':sha(r.HERE/'source_freeze.json')}):
            with self.assertRaisesRegex(PermissionError,'EXACT_HOST_CODE_FREEZE_ROSTER'):complete_code_identity(value,r.HERE,'UNOPENED','UNOPENED')
    def test_no_fit_invocations_or_REAL_keygen_in_production(self):
        import ast
        for name in ('scientific_evaluator.py','custodian_producer.py','production_broker.py','authority.py','activation.py'):
            tree=ast.parse((r.HERE/name).read_text())
            calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
            self.assertFalse(any(isinstance(n.func,ast.Attribute) and n.func.attr in ('fit','minimize','generate') for n in calls),name)

if __name__=='__main__':unittest.main()
