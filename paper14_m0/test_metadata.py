"""Synthetic metadata regressions and independent saved-table crosschecks.

No neural simulation, source retrieval, optimizer, or predictive score is used.
"""
import csv
import gzip
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from .audit import P, ROOT, read, region, session_blocks, sha, verify_inputs, workdir
from .context_audit import dr_blocks, flag, supported, signed_contrast, overlap
from . import range_metadata as ranges


def ibl_fixture(lengths=(60,60,60,60), contexts=(.2,.8,.2,.8)):
    ctx=np.repeat(contexts,lengths); t=np.arange(len(ctx))*2.
    return pd.DataFrame(dict(probabilityLeft=ctx,intervals_0=t,stimOn_times=t+.1,
        goCue_times=t+.2,feedback_times=t+.7,intervals_1=t+1.,
        bwm_include=True,saturation_stim_plus06=False))


def dr_fixture(lengths=(65,65,65,65), contexts=('aud','vis','aud','vis')):
    blocks=np.repeat(np.arange(len(lengths)),lengths); t=np.arange(len(blocks))*2.
    return pd.DataFrame(dict(trial_index=np.arange(len(t)),start_time=t,
        stim_start_time=t+.1,stim_stop_time=t+.6,stop_time=t+1.,
        block_index=blocks,rewarded_modality=np.repeat(contexts,lengths),
        is_opto=False,is_instruction=False))


def rows(path):
    with (gzip.open(path,'rt',newline='') if str(path).endswith('.gz') else Path(path).open(newline='',encoding='utf8')) as f:
        return list(csv.DictReader(f))


def setUpModule():
    workdir()


class TemporalMetadataTests(unittest.TestCase):
    def test_ibl_exact_floor(self):
        s,r,m=session_blocks(ibl_fixture());self.assertTrue(s['eligible']);self.assertEqual(m.sum(),240)
        self.assertEqual([x['half'] for x in r],['calibration']*2+['scoring']*2)
        for n in [59,14,0]:
            with self.subTest(n=n):self.assertFalse(session_blocks(ibl_fixture((n,60,60,60)))[0]['eligible'])

    def test_ibl_mask_and_unknown_fail_closed(self):
        for field,value in [('bwm_include',False),('bwm_include',None),('saturation_stim_plus06',True),('saturation_stim_plus06',None),('goCue_times',np.nan),('intervals_1',0.)]:
            x=ibl_fixture()
            if value is None:x[field]=x[field].astype(object)
            x.loc[0,field]=value
            with self.subTest(field=field,value=value):
                s,_,m=session_blocks(x);self.assertFalse(s['eligible']);self.assertFalse(m[0])

    def test_ibl_missing_schema(self):
        for col in ibl_fixture().columns:
            with self.subTest(col=col),self.assertRaises(ValueError):session_blocks(ibl_fixture().drop(columns=col))

    def test_neutral_and_unknown_break_runs_before_filter(self):
        for c in [.5,np.nan,.7]:
            x=ibl_fixture((20,1,20),(.2,c,.2));x.loc[20,'bwm_include']=False
            s,r,_=session_blocks(x);self.assertEqual(len(r),2);self.assertEqual([q['raw_trials'] for q in r],[20,20]);self.assertFalse(s['eligible'])

    def test_small_runs_do_not_move_temporal_cut(self):
        s,r,m=session_blocks(ibl_fixture((60,1,60,60,60),(.2,.8,.8,.2,.8)))
        # Adjacent same labels are one original run. A distinct tiny run remains in cut.
        self.assertEqual(s['run_count'],4)
        x=ibl_fixture((60,1,60,60,60),(.2,.8,.2,.8,.2))
        _,r,m=session_blocks(x);self.assertEqual([v['half'] for v in r],['calibration']*2+['scoring']*3)
        self.assertFalse(r[1]['qualifying']);self.assertFalse(m[60])

    def test_chronological_not_sorted_to_pass(self):
        for maker,check,key in [(ibl_fixture,session_blocks,'stimOn_times'),(dr_fixture,dr_blocks,'trial_index'),(dr_fixture,dr_blocks,'stim_start_time')]:
            x=maker();x.loc[10,key]=x.loc[9,key]
            with self.subTest(key=key):self.assertFalse(check(x)[0]['eligible'])

    def test_dr_exact_floor_and_scheduled_first5(self):
        s,r,m=dr_blocks(dr_fixture());self.assertTrue(s['eligible']);self.assertEqual(m.sum(),240)
        self.assertEqual(s['exclusion_counts_nonexclusive']['scheduled_first5'],20)
        self.assertFalse(any(m[:5]));self.assertEqual(s['counts']['aud']['calibration_trials'],60)
        self.assertFalse(dr_blocks(dr_fixture((64,65,65,65)))[0]['eligible'])

    def test_dr_first5_not_outcome_selected(self):
        a=dr_fixture();b=a.copy();b['is_response']=True;b['is_rewarded']=True;b['is_instruction']=True
        sa,ra,ma=dr_blocks(a);sb,rb,mb=dr_blocks(b)
        np.testing.assert_array_equal(ma,mb);self.assertEqual(ra,rb);self.assertEqual(sa['counts'],sb['counts'])
        self.assertGreater(sb['instruction_flags_outside_first5'],0)

    def test_dr_opto_timing_and_unknown(self):
        for field,value in [('is_opto',True),('is_opto',None),('stim_start_time',np.nan),('stim_stop_time',0.),('stop_time',.2)]:
            x=dr_fixture()
            if value is None:x[field]=x[field].astype(object)
            x.loc[5,field]=value
            with self.subTest(field=field):self.assertFalse(dr_blocks(x)[0]['eligible']);self.assertFalse(dr_blocks(x)[2][5])

    def test_dr_schema(self):
        for col in ['trial_index','start_time','stim_start_time','stim_stop_time','stop_time','block_index','rewarded_modality','is_opto']:
            with self.subTest(col=col),self.assertRaises(ValueError):dr_blocks(dr_fixture().drop(columns=col))

    def test_dr_context_and_block_identity(self):
        for col,value in [('block_index',None),('rewarded_modality','unknown'),('block_index',.5)]:
            x=dr_fixture();x[col]=x[col].astype(object);x.loc[70,col]=value
            with self.subTest(col=col,value=value):self.assertFalse(dr_blocks(x)[0]['eligible'])
        x=dr_fixture();x.loc[x.block_index==2,'block_index']=0
        self.assertFalse(dr_blocks(x)[0]['eligible'])

    def test_flags_never_truthiness(self):
        x=pd.Series([True,False,'true','False',None,'nan',1,0])
        self.assertEqual(flag(x).tolist(),[True,False,True,False,False,False,False,False])


class SupportAndAnatomyTests(unittest.TestCase):
    def test_signed_zero_is_one_stimulus_level_and_missing_is_not_zero(self):
        a=signed_contrast([0.,np.nan,.25,np.nan,np.nan],[np.nan,0.,np.nan,.25,np.nan])
        self.assertEqual(a[:4].tolist(),[0.,0.,-.25,.25]);self.assertTrue(np.isnan(a[4]))
        self.assertFalse(np.signbit(a[0]));self.assertFalse(np.signbit(a[1]))
        x=pd.DataFrame({'context':['a','a','b','b'],'contrast':a[[0,1,0,1]]})
        rr,common=overlap(x,['a','b'],'context','contrast',source='synthetic',mouse='m',session='s')
        self.assertEqual(common,['0.0']);self.assertEqual([r['count'] for r in rr],[2,2])

    def test_support_exact_boundaries_and_holes(self):
        self.assertTrue(supported('[[0,1],[2,3]]',[(0,1),(2,3)]))
        self.assertFalse(supported('[[0,1],[2,3]]',[(.5,2.5)]))
        self.assertFalse(supported('[[0,1],[2,3]]',[(.5,.8),(1.5,1.8)]))

    def test_invalid_support_fail_closed(self):
        for text in ['garbage','[]','[0,1]','[[1,0]]','[[0,2],[1,3]]','[[2,3],[0,1]]','[[0,NaN]]','null']:
            with self.subTest(text=text):self.assertFalse(supported(text,[(0,.5)]))
        for windows in [[],[(1,0)],[(np.nan,1)],[(0,np.inf)],[0,1]]:
            with self.subTest(windows=windows):self.assertFalse(supported('[[0,10]]',windows))

    def test_vectorized_support_independent_loop(self):
        # Metadata intervals only; no random neural outcomes or fitted quantities.
        rng=np.random.default_rng(912)
        for _ in range(200):
            intervals=np.column_stack((np.arange(8)*2.,np.arange(8)*2.+1.))
            starts=rng.uniform(-1,17,20);windows=np.column_stack((starts,starts+rng.uniform(.01,.6,20)))
            oracle=all(any(a<=s and e<=b for a,b in intervals) for s,e in windows)
            self.assertEqual(supported(json.dumps(intervals.tolist()),windows),oracle)

    def test_anatomical_boundary(self):
        for base in ['ACAd','ACAv','PL','ILA']:
            for layer in ['', '1','2/3','4','5','6a','6b']:self.assertEqual(region(base+layer),base)
        for a in ['MOs','ORB','PLISH','PL6','ACA','ILAextra',None,np.nan]:self.assertIsNone(region(a))


class AccessBoundaryTests(unittest.TestCase):
    def test_fresh_checkout_without_retrieval_scratch(self):
        with tempfile.TemporaryDirectory(dir=P/'work') as directory:
            fresh=Path(directory)/'new_checkout'
            self.assertFalse(fresh.exists())
            target=workdir(fresh)
            self.assertTrue(target.is_dir());self.assertEqual(target,workdir(fresh))
            with tempfile.TemporaryDirectory(dir=target) as output:
                self.assertEqual(Path(output).parent,target)

    def test_deny_neural_url_and_unbounded_get_before_network(self):
        with patch.object(ranges.requests,'request',side_effect=AssertionError('network called')):
            for url in [ranges.PREFIX+'spike_times.parquet',ranges.PREFIX+'session.nwb','https://example.com/units.parquet']:
                with self.subTest(url=url),self.assertRaises(PermissionError):ranges.request(url,headers={'Range':'bytes=0-1'})
            for headers in [None,{}, {'Range':'bytes=0-'},{'Range':'bytes=-20'},{'Range':'bytes=0-1,3-4'}]:
                with self.subTest(headers=headers),self.assertRaises(PermissionError):ranges.request(ranges.IBL,headers=headers)

    def test_reader_deny_bulk_and_invalid_seek(self):
        with tempfile.TemporaryDirectory(dir=P/'work') as directory,patch.object(ranges,'P',Path(directory)),patch.object(ranges,'request',return_value=(b'',{'Content-Length':'10','ETag':'fixed'})):
            f=ranges.MetadataRanges(ranges.IBL)
            for n in [-1,4000001]:
                with self.assertRaises(PermissionError):f.read(n)
            for n in [-1,11]:
                with self.assertRaises(ValueError):f.seek(n)

    def test_range_identity_and_cache_tamper(self):
        for changed in ['ETag','Content-Range','length']:
            with tempfile.TemporaryDirectory(dir=P/'work') as directory,patch.object(ranges,'P',Path(directory)):
                headers={'ETag':'fixed','Content-Range':'bytes 0-1/10'};raw=b'ab'
                if changed=='ETag':headers['ETag']='changed'
                if changed=='Content-Range':headers['Content-Range']='bytes 1-2/10'
                if changed=='length':raw=b'a'
                with patch.object(ranges,'request',side_effect=[(b'',{'Content-Length':'10','ETag':'fixed'}),(raw,headers)]):
                    f=ranges.MetadataRanges(ranges.IBL)
                    with self.assertRaises(ValueError):f.read(2)
        with tempfile.TemporaryDirectory(dir=P/'work') as directory,patch.object(ranges,'P',Path(directory)):
            with patch.object(ranges,'request',side_effect=[(b'',{'Content-Length':'10','ETag':'fixed'}),(b'ab',{'ETag':'fixed','Content-Range':'bytes 0-1/10'})]):
                f=ranges.MetadataRanges(ranges.IBL);self.assertEqual(f.read(2),b'ab')
            (f.root/'0_2.bin').write_bytes(b'xx')
            with patch.object(ranges,'request',return_value=(b'',{'Content-Length':'10','ETag':'fixed'})):
                g=ranges.MetadataRanges(ranges.IBL)
                with self.assertRaises(ValueError):g.read(2)

    def test_no_forbidden_column_whitelist(self):
        policy=read(P/'COLUMN_REGISTRATION.json')
        for name in ['DR_session','DR_trials','DR_units','IBL_trials']:
            self.assertFalse(set(policy[name])&set(policy['explicitly_forbidden_columns']))
        for field in ['spike_times','amplitudes','waveforms','num_spikes','firing_rate','decoder_label','decoder_probability']:
            self.assertFalse(any(field in policy[k] for k in ['DR_session','DR_trials','DR_units','IBL_trials']))


class IndependentSavedChecks(unittest.TestCase):
    def test_original_input_hashes(self):verify_inputs()

    def test_pinned_catalog_denominators(self):
        rr=rows(P/'metadata/dr_assets__datacube_sessions.csv')
        self.assertEqual(len(rr),263);self.assertEqual(len({r['subject_id'] for r in rr}),85)
        primary=[r for r in rr if r['session_type']=='brainwide' and r['is_behavior_pass'].lower()=='true']
        self.assertEqual(len(primary),82);self.assertEqual(len({r['subject_id'] for r in primary}),34)
        self.assertEqual(sum(not r['session_type'] for r in rr),83)

    def test_independent_probe_selection_and_animal_counts(self):
        for source,fn,expected,unitfield in [('DR','DR_populations.csv',18,'qualified_metadata_units'),('IBL','IBL_populations.csv',8,'provider_good_units')]:
            rr=[r for r in rows(P/'results'/fn) if r['region']=='mPFC_composite']
            admitted=[r for r in rr if r['metadata_eligible']=='True']
            self.assertEqual(len({r['mouse'] for r in admitted}),expected)
            self.assertTrue(all(int(r[unitfield])>=10 and int(r['minimum_context_half_trials'])>=60 for r in admitted))
            chosen=[r for r in rows(P/'results'/(source+'_selected_populations.csv')) if r['region']=='mPFC_composite' and r['metadata_eligible']=='True']
            self.assertEqual(len(chosen),expected);self.assertEqual(len({r['mouse'] for r in chosen}),expected)
            sid='session' if source=='DR' else 'eid';probe='probe' if source=='DR' else 'pid'
            for r in chosen:
                options=[z for z in admitted if z['mouse']==r['mouse']]
                oracle=min(options,key=lambda z:(-int(z[unitfield]),-int(z['minimum_context_half_trials']),z[sid],z[probe]))
                self.assertEqual((r[sid],r[probe]),(oracle[sid],oracle[probe]))

    def test_ki_canonical_independent_animals(self):
        rr=[r for r in rows(ROOT/'paper13_ki_feasibility1/results/review1/all_recording_identities.csv') if r['dandiset'].zfill(6)=='001260']
        self.assertEqual(len(rr),74);self.assertEqual(len({r['mouse_id'] for r in rr}),41)
        self.assertEqual(len({r['raw_subject_id'] for r in rr}),43)
        self.assertEqual(len({r['mouse_id'] for r in rr if r['task']=='Context'}),8)

    def test_final_verdict_not_neural_activation(self):
        x=read(P/'results/M0_DECISION.json');self.assertEqual(x['scientific_feasibility_verdict'],'INCONCLUSIVE_METADATA')
        self.assertEqual(x['metadata_mouse_upper_bound'],18);self.assertFalse(x['M1_activated']);self.assertFalse(x['primary_recommended_for_neural_activation'])


if __name__=='__main__':unittest.main(verbosity=2)
