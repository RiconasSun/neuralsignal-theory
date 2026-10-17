"""Bounded identity/anatomy/task metadata oracles; no neural model fitting."""
import json
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from . import audit,retrieve
from paper14_m0.audit import session_blocks

def task():
    rows=[]
    for block in range(8):
        for trial in range(70):
            t=float(10*(block*70+trial))
            rows.append(dict(probabilityLeft=.2 if block%2==0 else .8,stimOn_times=t+1,goCue_times=t+1.1,feedback_times=t+2,intervals_0=t,intervals_1=t+3,bwm_include=True,saturation_stim_plus06=False))
    f=pd.DataFrame(rows)
    for col in ['bwm_include','saturation_stim_plus06']:f[col]=f[col].astype(object)
    return f

class PivotTests(unittest.TestCase):
    def test_history_preserved(self):self.assertEqual(audit.verify(),673)

    def test_region_exact_medial_frontal_not_single_PFC(self):
        for s in ['MOs','MOs2/3','ACAd6a','ACAv','PL1','ILA6b']:self.assertIsNotNone(audit.region(s))
        for s in ['MOp','MOs-extra','ORBvl','ACA','PLx','unknown']:self.assertIsNone(audit.region(s))

    def test_primary_context_semantics_registered(self):
        r=retrieve.read(retrieve.P/'REGISTRATION.json')
        self.assertEqual(r['expanded_target'],['MOs','ACAd','ACAv','PL','ILA'])
        self.assertEqual((r['contexts']['low_priorLeft'],r['contexts']['high_priorLeft']),(.2,.8))
        self.assertIn('not directly measured belief',r['contexts']['meaning'])
        self.assertEqual(r['observations']['min_final'],8)

    def test_release_license_and_complete_metadata_pages(self):
        assets=audit.asset_metadata();self.assertEqual(len(assets),2048);self.assertEqual(len({a['asset_id'] for a in assets}),2048)

    def test_null_page_totals_supported_not_missing_pages(self):
        self.assertIsNone(retrieve.read(retrieve.P/'sources/assets_page2.json')['count'])
        original=audit.read
        def missing(path):
            obj=original(path)
            if str(path).endswith('assets_page3.json'):obj['results']=[]
            return obj
        with patch.object(audit,'read',side_effect=missing):
            with self.assertRaises(ValueError):audit.asset_metadata()

    def test_wrong_release_or_license_fail_closed(self):
        original=audit.read
        def bad(path):
            obj=original(path)
            if str(path).endswith('release.json'):obj['license']=['ALL_RIGHTS_RESERVED']
            return obj
        with patch.object(audit,'read',side_effect=bad):
            with self.assertRaises(ValueError):audit.asset_metadata()

    def test_uuid_bound_name_bijection(self):
        fixture=pd.DataFrame([dict(subject='A_B',eid='eid1',lab='lab'),dict(subject='A_B',eid='eid2',lab='lab')])
        assets=[dict(subject='A-B',eid='eid1',asset_id='a1'),dict(subject='A-B',eid='eid2',asset_id='a2')]
        rows,names=audit.subject_crosswalk(fixture,assets)
        self.assertEqual(len(rows),2);self.assertEqual(len(names),1);self.assertFalse(rows[0]['literal_subject_match'])

    def test_name_collision_never_merges_animals(self):
        fixture=pd.DataFrame([dict(subject='A_B',eid='eid1',lab='lab'),dict(subject='A-B',eid='eid2',lab='lab')])
        assets=[dict(subject='A-B',eid='eid1',asset_id='a1'),dict(subject='A-B',eid='eid2',asset_id='a2')]
        with self.assertRaisesRegex(ValueError,'collision'):audit.subject_crosswalk(fixture,assets)

    def test_missing_or_duplicate_session_denied(self):
        fixture=pd.DataFrame([dict(subject='A',eid='eid1',lab='lab')]);a=dict(subject='A',eid='eid1',asset_id='a1')
        for assets in [[],[a,a],[dict(a,eid='wrong')]]:
            with self.assertRaises(ValueError):audit.subject_crosswalk(fixture,assets)

    def test_balanced_context_whole_original_halves(self):
        s,runs,mask=session_blocks(task());self.assertTrue(s['eligible']);self.assertEqual(len(runs),8)
        self.assertEqual([r['half'] for r in runs],['calibration']*4+['scoring']*4)
        for c in [.2,.8]:self.assertEqual(s['counts'][c]['calibration_trials'],140);self.assertEqual(s['counts'][c]['scoring_trials'],140)
        self.assertTrue(mask.all())

    def test_neutral_breaks_runs_before_filtering(self):
        f=task();f.loc[30,'probabilityLeft']=.5;s,runs,mask=session_blocks(f)
        self.assertEqual(len(runs),9);self.assertFalse(mask[30]);self.assertEqual(s['neutral_trials'],1)
        self.assertEqual([r['half'] for r in runs],['calibration']*4+['scoring']*5)

    def test_small_run_not_bridged_or_used(self):
        f=task();f.loc[10:69,'bwm_include']=False;s,runs,mask=session_blocks(f)
        self.assertFalse(runs[0]['qualifying']);self.assertFalse(mask[:70].any());self.assertEqual(len(runs),8)

    def test_unknown_saturation_or_provider_mask_excluded(self):
        f=task();f.loc[10,'saturation_stim_plus06']=None;f.loc[11,'bwm_include']=None
        _,_,mask=session_blocks(f);self.assertFalse(mask[10]);self.assertFalse(mask[11])

    def test_invalid_event_window_or_order_excluded(self):
        f=task();f.loc[10,'goCue_times']=f.loc[10,'stimOn_times']-.1;f.loc[11,'intervals_1']=f.loc[11,'stimOn_times']+.2;f.loc[12,'feedback_times']=np.nan
        _,_,m=session_blocks(f);self.assertFalse(m[10:13].any())

    def test_nonmonotone_stimulus_fails_eligibility(self):
        f=task();f.loc[20,'stimOn_times']=f.loc[19,'stimOn_times'];s,_,_=session_blocks(f);self.assertFalse(s['chronological']);self.assertFalse(s['eligible'])

    def test_required_metadata_absence_fail_closed(self):
        for col in ['probabilityLeft','goCue_times','saturation_stim_plus06','bwm_include']:
            with self.assertRaises(ValueError):session_blocks(task().drop(columns=col))

    def test_pseudoreplication_and_composition_real_saved_oracle(self):
        p=pd.read_csv(retrieve.P/'results/ALL_PROBE_COMPOSITION.csv');s=pd.read_csv(retrieve.P/'results/EXPANDED_METADATA_CANDIDATES.csv')
        self.assertEqual(p.pid.nunique(),699);self.assertEqual(s.mouse.nunique(),13);self.assertEqual(len(s),13)
        np.testing.assert_array_equal(s[list(audit.LEAVES)].sum(axis=1),s.expanded_good_units)
        self.assertEqual(int((s.MOs_fraction>.5).sum()),9);self.assertEqual(int((s.strict_good_units>=10).sum()),7)
        self.assertEqual(p.loc[p.expanded_metadata_eligible,'mouse'].nunique(),13)

    def test_historical_strict8_not_reclassified(self):
        old=retrieve.read(audit.R/'paper14_m0/results/IBL_AUDIT.json')['regions']['mPFC_composite']
        now=retrieve.read(retrieve.P/'results/PIVOT_DECISION.json');self.assertEqual(now['strict_historical_mouse_ids'],old['selected_eligible_mice']);self.assertEqual(old['metadata_eligible_mice'],8)

    def test_failed_floor_does_not_allocate_or_activate(self):
        d=retrieve.read(retrieve.P/'results/PIVOT_DECISION.json');self.assertLess(d['expanded_context_metadata_candidates'],d['minimum_total']);self.assertEqual(d['scientific_decision'],'DATA_INSUFFICIENT')
        self.assertFalse(d['full_M1_protocol_frozen']);self.assertFalse(d['Prompt3_eligible']);self.assertIsNone(d['actual_development_final_allocation']);self.assertTrue(d['archive_recommendation'])
        self.assertFalse(d['source_unit_QC_version_equivalence'])

    def test_content_neural_and_wrong_dataset_endpoints_denied(self):
        for u in ['https://api.dandiarchive.org/api/assets/123/download/','https://api.dandiarchive.org/api/dandisets/000473/','https://api.dandiarchive.org/api/dandisets/000409/versions/draft/','https://dandiarchive.s3.amazonaws.com/spike_times.npy','https://example.com/metadata.json']:
            with self.assertRaises(PermissionError):retrieve.validate(u)

    def test_actual_access_budget_and_no_asset_payloads(self):
        rows=[json.loads(l) for l in (retrieve.P/'sources/access.jsonl').read_text().splitlines()];lim=retrieve.read(retrieve.P/'REGISTRATION.json')['access']
        self.assertLessEqual(len(rows),lim['http_attempts']);self.assertLessEqual(sum(r['bytes'] for r in rows),lim['total_bytes'])
        for row in rows:self.assertEqual(row['method'],'GET');retrieve.validate(row['url']);self.assertNotIn('/download/',row['url'])

if __name__=='__main__':unittest.main()
