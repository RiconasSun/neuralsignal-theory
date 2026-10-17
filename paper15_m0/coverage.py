"""Saved metadata screening only; no neural array access or fitting."""
import hashlib, json, re
from pathlib import Path
import numpy as np
import pandas as pd

R = Path(__file__).resolve().parent.parent
P = R / 'paper15_m0'

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8')

def region_of(acronym, regions):
    return next((r for r in regions if re.fullmatch(re.escape(r)+r'(?:1|2/3|4|5|6a|6b)?', str(acronym))), None)

def trial_mask(t):
    fields=['intervals_0','stimOn_times','goCue_times','feedback_times','intervals_1']
    a,s,g,f,z=[t[x].to_numpy(float) for x in fields]
    return (np.isfinite(t[fields]).all(axis=1).to_numpy() & (a<=s) & (s<=f) & (f<=z)
            & (a<=g) & (g<=f) & (s+.5<=z) & t.bwm_include.to_numpy(bool)
            & ~t.saturation_stim_plus06.to_numpy(bool))

def allocate(rows, mission):
    bylab={lab: sorted(g.to_dict('records'), key=lambda x:hashlib.sha256((mission+x['subject']).encode()).hexdigest())
           for lab,g in rows.groupby('lab', sort=True)}
    ordered=[]
    while any(bylab.values()):
        for lab in sorted(bylab):
            if bylab[lab]: ordered.append(bylab[lab].pop(0))
    n=len(ordered); nf=max(6,int(.4*n)) if n>=12 else 0
    for i,r in enumerate(ordered):
        r['allocation']='FINAL_RESERVED' if ((i+1)*nf//n>i*nf//n) else 'DEVELOPMENT'
    return ordered

def build(out):
    policy=json.loads((P/'M0_REGISTRATION.json').read_text(encoding='utf8'))
    for rel,sha in json.loads((P/'INPUT_PINS.json').read_text(encoding='utf8'))['hashes'].items():
        assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==sha, rel
    fixture=pd.read_csv(R/'paper13/metadata/fixture.csv',index_col=0)
    units=pd.read_csv(R/'paper13/metadata/clusters_metadata.csv.gz')
    trials=pd.read_csv(R/'paper13/metadata/trials_metadata.csv.gz')
    atlas=json.loads((R/'paper13/metadata/atlas.json').read_text(encoding='utf8'))['msg']
    # Allen structure IDs in the aggregate are unsigned; reject contradictory duplicate mappings.
    atlasmap={}
    for a in atlas:
        k=int(a['id']);v=a['acronym']
        assert k not in atlasmap or atlasmap[k]==v
        atlasmap[k]=v
    assert fixture.pid.is_unique and not units.duplicated(['pid','cluster_id']).any()
    assert units.merge(fixture[['pid','eid']],on=['pid','eid'],how='left',indicator=True)._merge.eq('both').all()
    units['acronym']=units.atlas_id.map(atlasmap)
    units['region']=units.acronym.map(lambda a:region_of(a,policy['regions']))
    unknown=sorted(str(a) for a in units.acronym.dropna().unique()
                   if any(str(a).startswith(r) for r in policy['regions']) and region_of(a,policy['regions']) is None)
    summaries=[]
    for eid,t in trials.groupby('eid',sort=True):
        m=trial_mask(t);n=len(t);cut=n//2
        summaries.append(dict(eid=eid,original_trials=n,usable_trials=int(m.sum()),half1=int(m[:cut].sum()),half2=int(m[cut:].sum()),
            usable_seconds=float(.5*m.sum()),first_movement_finite=int(np.isfinite(t.firstMovement_times).sum()),
            response_finite=int(np.isfinite(t.response_times).sum()),saturation_excluded=int(t.saturation_stim_plus06.sum()),
            bwm_excluded=int((~t.bwm_include).sum()),trial_pass=bool(m.sum()>=100 and min(m[:cut].sum(),m[cut:].sum())>=40)))
    ts=pd.DataFrame(summaries)
    allrows=[]
    for region in policy['regions']:
        u=units[units.region.eq(region)]
        count=u.groupby('pid').agg(labeled_units=('cluster_id','size'),good_units=('label',lambda x:int(x.eq(1).sum())))
        d=fixture.merge(count,on='pid',how='left').fillna({'labeled_units':0,'good_units':0}).merge(ts,on='eid',validate='many_to_one')
        d['region']=region;d[['labeled_units','good_units']]=d[['labeled_units','good_units']].astype(int)
        allrows.append(d)
    coverage=pd.concat(allrows,ignore_index=True)
    tiers=[];chosen={}
    for region in policy['regions']:
        d=coverage[coverage.region.eq(region)]
        for tier in policy['unit_tiers']:
            q=d[d.good_units.ge(tier)&d.trial_pass].copy()
            q['min_half']=q[['half1','half2']].min(axis=1)
            one=q.sort_values(['good_units','min_half','eid','pid'],ascending=[False,False,True,True]).drop_duplicates('subject')
            tiers.append(dict(region=region,tier=tier,anatomical_mice=int(d[d.labeled_units.gt(0)].subject.nunique()),
                anatomical_probes=int(d.labeled_units.gt(0).sum()),good_unit_probes=int(d.good_units.ge(tier).sum()),
                qualified_probes=len(q),independent_mice=len(one),sessions=int(q.eid.nunique())))
            if tier==8:chosen[region]=one
    selected=next((r for minimum in (12,6,1) for r in policy['regions'] if len(chosen[r])>=minimum),None)
    allocation=allocate(chosen[selected],policy['mission']) if selected else []
    dev=[r for r in allocation if r['allocation']=='DEVELOPMENT']
    # Highest attainable registered tier, then usable trials, then lexical session/probe.
    dev.sort(key=lambda x:(-max(t for t in policy['unit_tiers'] if x['good_units']>=t),-x['usable_trials'],x['eid'],x['pid']))
    pilot=dev[:2]
    out.mkdir(parents=True,exist_ok=True)
    coverage.to_csv(out/'COVERAGE.csv',index=False,lineterminator='\n')
    ts.to_csv(out/'TRIAL_COVERAGE.csv',index=False,lineterminator='\n')
    pd.DataFrame(tiers).to_csv(out/'REGION_TIERS.csv',index=False,lineterminator='\n')
    pd.DataFrame(allocation).to_csv(out/'ALLOCATION.csv',index=False,lineterminator='\n')
    summary=dict(original_mice=int(fixture.subject.nunique()),original_sessions=int(fixture.eid.nunique()),original_probes=len(fixture),
        original_labeled_units=len(units),original_good_units=int(units.label.eq(1).sum()),
        original_trials=len(trials),selected_region=selected,candidate_independent_mice=len(allocation),
        design='INDEPENDENT_HOLDOUT' if len(allocation)>=12 else 'TEMPORAL_EXPLORATORY' if len(allocation)>=6 else 'LIMITED_PILOT',
        development_mice=len(dev),reserved_final_mice=len(allocation)-len(dev),
        labs={str(k):int(v) for k,v in fixture.drop_duplicates('subject').lab.value_counts().items()},
        repeated_session_mice=int(fixture.groupby('subject').eid.nunique().gt(1).sum()),
        selected_labs={str(k):int(v) for k,v in pd.DataFrame(allocation).lab.value_counts().items()} if allocation else {},
        unrecognized_target_labels=unknown,unknown_atlas_units=int(units.acronym.isna().sum()),
        metadata_source='Paired 2024_Q2_IBL_et_al_BWM aggregates; native pilot equivalence not assumed',physiologically_admitted_mice=0,
        pilot=[{k:v for k,v in r.items() if k in ['subject','eid','pid','probe_name','lab','region','good_units','usable_trials','allocation','date','session_number']} for r in pilot])
    dump(out/'COVERAGE_SUMMARY.json',summary)
    return summary

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=P/'results');args=ap.parse_args()
    print(json.dumps(build(args.out),indent=2))
