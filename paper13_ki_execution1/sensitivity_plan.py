"""Registered metadata/training-only sensitivity plans; no neural source IO."""
import re
import numpy as np
from .source import ROOT
from .baseline_A import read
from paper13_ki_pl_contract1.audit import saturation,intersects,validate_intervals

MANDATORY=['first4','rate4','quality005','deep_PL5_PL6a','alignment_minus01','alignment_plus01','recent_event']


def unit_panels(bundle):
    units=bundle['units'];qc=bundle['unit_QC']
    if len(units)!=8 or [u['unit_id'] for u in units]!=sorted(u['unit_id'] for u in units):raise ValueError('Original8numeric units required')
    rates=np.array([qc[str(u['unit_id'])]['rate_hz'] for u in units]);median=float(np.median(rates))
    nearest=sorted(range(8),key=lambda j:(abs(rates[j]-median),units[j]['unit_id']))[:4]
    return {'first4':[j<4 for j in range(8)],'rate4':[j in nearest for j in range(8)],
        'quality005':[qc[str(u['unit_id'])]['refractory_fraction']<=.005 for u in units],
        'deep_PL5_PL6a':[u['label'] in ['PL5','PL6a'] for u in units]}


def recent_keep(epochs,onsets,intervals=()):
    onsets=np.asarray(onsets,dtype=float)
    if not np.isfinite(onsets).all():raise ValueError('Nonfinite known stimulus timestamps')
    validate_intervals(list(intervals))
    return [not(any(e['start']-5<=t<e['stop'] for t in onsets) or any(a<e['stop'] and e['start']-5<b for a,b in intervals)) for e in epochs]


def shifted(epochs,shift,support,spike=(),lfp=(),manual=()):
    if shift not in [-.1,.1]:raise ValueError('Registered +/-100ms only')
    out=[]
    for e in epochs:
        z={**e,'start':e['start']+shift,'stop':e['stop']+shift,'original_tone':e['stop']};reasons=[]
        interval=[z['start'],z['stop']]
        if interval[0]<support[0] or interval[1]>support[1]:reasons.append('support')
        if any(intersects(interval,[a-1,b+1]) for a,b in spike):reasons.append('spike_saturation')
        if any(intersects(interval,[a-1,b+1],touch=True) for a,b in lfp):reasons.append('LFP_saturation')
        if any(intersects(interval,row,touch=True) for row in manual):reasons.append('manual')
        if any(f['ordinal']!=e['ordinal'] and intersects(interval,[f['start']+shift,f['stop']+shift]) for f in epochs):reasons.append('shifted_overlap')
        if any(f['partition']!=e['partition'] and intersects(interval,[f['start'],f['stop']],touch=True) for f in epochs):reasons.append('other_partition_original_touch')
        z['retained']=not reasons;z['exclusion_reasons']=reasons
        z['observed_full_bins']=sum(z['start']+(j+1)/10<=e['stop']+1e-10 for j in range(30))
        if z['observed_full_bins'] not in [29,30]:raise ValueError('Unexpected alignment bin identity')
        # End export at last full pre-tone bin. Keep shifted full-window metadata for masks.
        z['export_stop']=z['start']+z['observed_full_bins']/10
        out.append(z)
    return out


def metadata(record):
    header=read(ROOT/record['header_file']);v=header['decoded_values']
    spike,_=saturation(v,'spike');lfp,_=saturation(v,'LFP')
    manual=read(ROOT/'paper13_ki_pl_contract1/metadata/manual_bad_intervals.json')['intervals'] if record['recording_id']=='147463_20191113-probe0' else []
    onsets=[]
    for path,values in v.items():
        if re.fullmatch(r'/stimulus/presentation/[^/]+/timestamps',path):onsets.extend(values)
    # Frozen header supplies onsets only, not stimulus intervals. Do not infer duration.
    recent=recent_keep(record['epochs'],onsets)
    active=read(ROOT/'paper13_ki_feasibility1/metadata/provider_active_intervals.json')['selected_members']
    candidates=[a for a in active if a['attributes'].get('recid')==record['recording_id']]
    candidates_all=[a for a in candidates if a['path'].endswith('STATEactive__all.h5')]
    chosen=candidates_all or [a for a in candidates if a['path'].endswith('STATEactive.h5')]
    if len(chosen)!=1:raise ValueError('Frozen provider-active identity ambiguous')
    intervals=validate_intervals(chosen[0]['tints'])
    return {'recent_event':{str(e['ordinal']):keep for e,keep in zip(record['epochs'],recent)},
        'alignment_minus01':shifted(record['epochs'],-.1,record['original_support'],spike,lfp,manual),
        'alignment_plus01':shifted(record['epochs'],.1,record['original_support'],spike,lfp,manual),
        'provider_active':{str(e['ordinal']):any(max(abs(e['start']-a),abs(e['stop']-b))<=1e-6 for a,b in intervals) for e in record['epochs']},
        'stimulus_interval_durations_supplied':False,'exact_unsuffixed_PL':'STRUCTURALLY_EMPTY_DESCRIPTIVE_NA',
        'genotype_condition':v.get('/general/subject/genotype','NOT_SUPPLIED'),
        'electrode_depth':{str(u['unit_id']):{k:v[k][u['electrode_row']] for k in v if k.startswith('/general/extracellular_ephys/electrodes/') and k.rsplit('/',1)[-1] in ['x','y','z','rel_x','rel_y','depth']} for u in record['PL_units_numeric_order']}}
