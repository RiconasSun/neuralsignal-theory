"""Different implementation of saved-metadata counts (pandas joins/groupby).

Internal reproducibility cross-check, not a second-person scientific review.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

P=Path(__file__).resolve().parent


def run(output):
    fixture=pd.read_csv(P/'metadata/fixture.csv',dtype=str)
    clusters=pd.read_csv(P/'metadata/clusters_metadata.csv.gz',dtype={'pid':str,'eid':str})
    trials=pd.read_csv(P/'metadata/trials_metadata.csv.gz')
    atlas=json.loads((P/'metadata/atlas.json').read_text())['msg']
    expected=json.loads((P/'results/M0/M0_audit.json').read_text())
    policy=json.loads((P/'M0_REGISTRATION.json').read_text())
    assert not fixture.pid.duplicated().any()
    assert not clusters[['pid','cluster_id']].duplicated().any()
    assert not clusters.uuids.duplicated().any()
    joined=clusters.merge(fixture[['pid','eid','subject','lab']],on='pid',validate='many_to_one',suffixes=('','_fixture'),indicator=True)
    assert (joined['_merge']=='both').all()
    assert (joined.eid==joined.eid_fixture).all()
    joined['mouse']=joined.lab+'/'+joined.subject
    trialok=(trials.bwm_include.eq(True) & trials.intervals_0.le(trials.stimOn_times)
             & trials.stimOn_times.le(trials.feedback_times) & trials.feedback_times.le(trials.intervals_1)
             & trials.intervals_0.le(trials.goCue_times) & trials.goCue_times.le(trials.feedback_times)
             & (trials.intervals_1-trials.intervals_0).ge(.1))
    for column in ['intervals_0','intervals_1','stimOn_times','goCue_times','feedback_times']:
        trialok &= trials[column].notna() & trials[column].abs().lt(float('inf'))
    valid_trials=trials.loc[trialok].groupby('eid').size()
    answers={}
    for name in policy['region_priority']:
        # Explicit set, independent of audit regex.
        acronyms={name+s for s in ['','1','2/3','4','5','6a','6b']}
        ids={int(row['id']) for row in atlas if row['acronym'] in acronyms}
        candidates=joined.loc[joined.atlas_id.abs().isin(ids)]
        good=candidates.loc[candidates.label.eq(1)]
        n=good.groupby('pid').size()
        valid_pids=set(n.loc[n.ge(policy['minimum_good_units_single_probe'])].index)
        upper=good.loc[good.pid.isin(valid_pids) & good.eid.map(valid_trials).ge(policy['minimum_usable_trials'])]
        ans={'all_labeled_units':len(candidates),'provider_good_units':len(good),
             'anatomical_mice':candidates.mouse.nunique(),'anatomical_sessions':candidates.eid.nunique(),
             'anatomical_probes':candidates.pid.nunique(),
             'unit_threshold_mice':good.loc[good.pid.isin(valid_pids)].mouse.nunique(),
             'unit_threshold_sessions':good.loc[good.pid.isin(valid_pids)].eid.nunique(),
             'unit_threshold_probes':len(valid_pids),
             'count_upper_bound_mice':upper.mouse.nunique(),
             'count_upper_bound_sessions':upper.eid.nunique(),'count_upper_bound_probes':upper.pid.nunique()}
        ans={k:int(v) for k,v in ans.items()}
        assert all(expected['regions'][name][k]==v for k,v in ans.items()),(name,ans)
        answers[name]=ans
    d=expected['denominator']
    assert len(clusters)==d['aggregate_clusters']==621733
    assert int(clusters.label.eq(1).sum())==d['aggregate_good_in_fixture']==75708
    assert len(fixture)==d['fixture_probes']==699
    assert fixture.eid.nunique()==d['fixture_sessions']==459
    assert len(set(zip(fixture.lab,fixture.subject)))==d['fixture_mice']==139
    assert len(trials)==d['trial_rows']==295920
    assert set(trials.eid)==set(fixture.eid)
    assert all(x['unit_threshold_mice']<16 for x in answers.values())
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf8') as f:
        f.write(json.dumps({'pass':True,'implementation':'pandas independent joins/groupby; no production-audit import',
                            'regions':answers,'pandas_version':pd.__version__,
                            'neural_arrays_or_scores_accessed':False},indent=2)+'\n')
    print('Independent implementation: all saved denominators and regional counts agree')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
