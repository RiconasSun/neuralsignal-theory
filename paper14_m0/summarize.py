"""Deterministic descriptive accounting of saved non-neural metadata."""
import json
import numpy as np
import pandas as pd
from .audit import P, read, write, table, REGIONS
from .context_audit import flag


def run(out=None):
    out=P/'results' if out is None else out
    selected=pd.read_csv(out/'DR_selected_populations.csv',dtype={'mouse':str})
    selected=selected[(selected.region=='mPFC_composite')&selected.metadata_eligible]
    d=read(out/'DR_AUDIT.json');pop=pd.read_csv(out/'DR_populations.csv');blocks=pd.read_csv(out/'DR_blocks.csv')
    trials=pd.read_csv(P/'metadata/trials_metadata.csv.gz',dtype={'session_id':str},float_precision='round_trip')
    sessions=pd.read_csv(P/'metadata/session_metadata.csv.gz',dtype={'session_id':str})
    units=pd.read_csv(out/'DR_target_unit_metadata.csv.gz',dtype={'session_id':str,'electrode_group_name':str,'target_region':str})
    composition=[];contextrows=[];missing=[]
    for e in selected.itertuples():
        u=units[(units.session_id==e.session)&(units.electrode_group_name==e.probe)]
        q=u[flag(u.good)&flag(u.anatomy_coordinates_valid)&flag(u.all_primary_windows_supported)]
        for region in REGIONS[:-1]:composition.append({'mouse':e.mouse,'session':e.session,'probe':e.probe,'leaf':region,'qualified_metadata_units':int(q.target_region.eq(region).sum())})
        for ctx,z in d['session_summaries'][e.session]['counts'].items():contextrows.append({'source':'DR','mouse':e.mouse,'session':e.session,'probe':e.probe,'region':e.region,'context':ctx,'qualified_units':e.qualified_metadata_units,**z})
        x=trials[trials.session_id==e.session]
        for c in x.columns:missing.append({'mouse':e.mouse,'session':e.session,'field':c,'missing':int(x[c].isna().sum()),'rows':len(x)})
    table(out/'DR_selected_composition.csv',pd.DataFrame(composition))
    table(out/'DR_selected_context_coverage.csv',pd.DataFrame(contextrows))
    table(out/'DR_selected_trial_missingness.csv',pd.DataFrame(missing))
    table(out/'DR_session_metadata_missingness.csv',pd.DataFrame([{'field':c,'missing':int(sessions[c].isna().sum()),'rows':len(sessions)} for c in sessions]))
    exclusions=[]
    for source,fn in [('DR','DR_populations.csv'),('IBL','IBL_populations.csv')]:
        z=pd.read_csv(out/fn)
        for r in REGIONS:
            a=z[z.region==r]
            for why in sorted({w for s in a.exclusion_reasons.dropna() for w in s.split(';')}):
                bad=a[a.exclusion_reasons.fillna('').str.split(';').map(lambda x:why in x)]
                exclusions.append({'source':source,'region':r,'reason_nonexclusive':why,'probe_session_rows':len(bad),'mice_with_some_failed_population':int(bad.mouse.nunique()),'total_probe_session_rows':len(a)})
    table(out/'EXCLUSIONS_NONEXCLUSIVE.csv',pd.DataFrame(exclusions))
    merged=[]
    for source,fn in [('IBL','Context_Mouse_Region_Coverage.csv'),('DR','DR_Mouse_Region_Context.csv'),('KI','KI_Mouse_Region_Context.csv')]:
        x=pd.read_csv(out/fn);x.insert(0,'source',source);merged.append(x)
    table(out/'ALL_Context_Mouse_Region.csv',pd.concat(merged,ignore_index=True,sort=False))
    logs=[json.loads(l) for l in (P/'metadata/access.jsonl').read_text().splitlines()]
    report={'registered_metadata_eligible_mice':len(selected),'selected_single_probe_units_min':int(selected.qualified_metadata_units.min()),
        'selected_single_probe_units_max':int(selected.qualified_metadata_units.max()),'selected_context_half_trials_min':int(selected.minimum_context_half_trials.min()),
        'selected_context_half_trials_max_of_mouse_minima':int(selected.minimum_context_half_trials.max()),
        'selected_run_counts':sorted({d['session_summaries'][s]['run_count'] for s in selected.session}),
        'selected_instruction_flags_outside_first5':sum(d['session_summaries'][s]['instruction_flags_outside_first5'] for s in selected.session),
        'selected_drift_false_among_good':int(selected.source_drift_flag_false_among_good.sum()),
        'selected_primary_session_labs':sorted(sessions[sessions.session_id.isin(selected.session)].lab.dropna().unique().tolist()),
        'scripted_http_attempts':len(logs),'scripted_response_bytes':sum(x.get('bytes',0) for x in logs),
        'scripted_failed_attempts':sum('error' in x for x in logs),'browser_discovery_transport_bytes':'UNOBSERVABLE_NOT_INCLUDED',
        'neural_arrays_fits_scores':0,'physiologically_admitted_mice':None}
    write(out/'DESCRIPTIVE_SUMMARY.json',report);return report


if __name__=='__main__':print(json.dumps(run()))
