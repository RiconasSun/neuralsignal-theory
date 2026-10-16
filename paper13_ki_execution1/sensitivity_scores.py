"""Pure fixed-state sensitivity scoring and equal-mouse descriptive summaries."""
import numpy as np
from .predictive import evaluate
from .control_core import LABELS,effects
from .sensitivity_plan import MANDATORY


def cell(y,q,bundle,*,epochs=None,units=None):
    mask=np.ones(len(y),dtype=bool) if epochs is None else np.asarray(epochs,dtype=bool)
    umask=np.ones(8,dtype=bool) if units is None else np.asarray(units,dtype=bool)
    if mask.shape!=(len(y),) or umask.shape!=(8,):raise ValueError('Exact original parent/unit mask required')
    n_epochs=int(mask.sum());n_units=int(umask.sum());denominator=n_epochs*(y.shape[1]-5)*n_units
    result={'retained_epochs':n_epochs,'retained_units':n_units,'nominal_unit_bins':denominator,
        'coverage_eligible':n_epochs>=10 and n_units>=4,'scores':None}
    if n_epochs and n_units:result['scores']=evaluate(y[mask],q[mask],bundle,units=umask)['scores']
    return result


def score_mouse(y,q,bundle,record,descriptor,aligned):
    partition='D' if record['role']=='final' else 'E'
    if bundle['training_partition']!=('C' if partition=='D' else 'A'):raise PermissionError('Sensitivity role/training-state mismatch')
    epochs=[e for e in record['epochs'] if e['partition']==partition]
    if len(epochs)!=len(y):raise ValueError('Sensitivity original epoch identity mismatch')
    metadata=bundle['sensitivity_metadata'];out={};aligned_plans={}
    original={e['ordinal']:e for e in epochs}
    for name,shift,T in [('alignment_minus01',-.1,30),('alignment_plus01',.1,29)]:
        planned=[e for e in metadata[name] if e['partition']==partition and e['retained']]
        supplied=aligned[name];N=len(planned)
        if [e['ordinal'] for e in planned]!=supplied['parent_ordinals'] or len({e['ordinal'] for e in planned})!=N:
            raise ValueError('Alignment parent ordinal identity/order mismatch')
        if supplied['unit_ids']!=[u['unit_id'] for u in bundle['units']]:raise ValueError('Original aligned unit identity/order mismatch')
        if np.shape(supplied['counts'])!=(N,T,8) or np.shape(supplied['q'])!=(N,T,11):
            raise ValueError('Exact aligned pre-tone bin/epoch/unit/nuisance dimensions required; no truncation')
        for e in planned:
            parent=original[e['ordinal']]
            required=['start','stop','original_tone','export_stop','observed_full_bins']
            if any(k not in e for k in required) or not np.isfinite([e[k] for k in required]).all():raise ValueError('Missing/nonfinite aligned plan bounds')
            if e['observed_full_bins']!=T or abs(e['start']-(parent['start']+shift))>1e-10 or abs(e['stop']-(parent['stop']+shift))>1e-10:
                raise ValueError('Aligned shift/full-bin plan inconsistent with original parent')
            if abs(e['original_tone']-parent['stop'])>1e-10 or abs(e['export_stop']-(e['start']+T/10))>1e-10 or e['export_stop']>e['original_tone']+1e-10:
                raise ValueError('Aligned export bound includes forbidden response or mismatches full bins')
        aligned_plans[name]=planned
    for name,units in bundle['sensitivity_unit_masks'].items():out[name]=cell(y,q,bundle,units=units)
    for name in ['recent_event','provider_active']:
        keep=[metadata[name][str(e['ordinal'])] for e in epochs];out[name]=cell(y,q,bundle,epochs=keep)
        out[name]['retained_parent_ordinals']=[e['ordinal'] for e,keep_e in zip(epochs,keep) if keep_e]
    for name in ['alignment_minus01','alignment_plus01']:
        planned=aligned_plans[name]
        supplied=aligned[name]
        if [e['ordinal'] for e in planned]!=supplied['parent_ordinals']:raise ValueError('Alignment parent ordinal mismatch')
        if planned:
            out[name]=cell(supplied['counts'],supplied['q'],bundle)
        else:out[name]={'retained_epochs':0,'retained_units':8,'nominal_unit_bins':0,'coverage_eligible':False,'scores':None}
        out[name]['retained_parent_ordinals']=supplied['parent_ordinals'];out[name]['shifted_full_window_metadata']=planned
    for quartile in range(4):out['session_order_quartile'+str(quartile+1)]=cell(y,q,bundle,epochs=[(e['ordinal']-1)//30==quartile for e in epochs])
    for label in ['PL','PL1','PL2/3','PL4','PL5','PL6a','PL6b']:
        out['label_'+label]=cell(y,q,bundle,units=[u['label']==label for u in bundle['units']])
        if label=='PL':out['label_'+label]['structural_status']='STRUCTURALLY_EMPTY_DESCRIPTIVE_NA_FROZEN_BEFORE_NEURAL_ACCESS'
    for name,mask in descriptor['depth_rank_masks'].items():out[name]=cell(y,q,bundle,units=mask)
    out['descriptive_metadata']=descriptor
    return out


def aggregate(per_mouse,mouse_order):
    if set(per_mouse)!=set(mouse_order):raise ValueError('All original sensitivity mice required')
    names=sorted(set().union(*(set(v)-{'descriptive_metadata'} for v in per_mouse.values())))
    panels={}
    for name in names:
        cells={m:per_mouse[m].get(name) for m in mouse_order}
        contributing=[m for m in mouse_order if cells[m] and cells[m]['scores'] is not None and cells[m]['coverage_eligible']]
        computed=[m for m in mouse_order if cells[m] and cells[m]['scores'] is not None]
        if contributing:
            matrix=effects(np.array([[cells[m]['scores'][label] for label in LABELS] for m in contributing]))
            mean=matrix.mean(axis=0);lomo=np.array([np.delete(matrix,j,axis=0).mean(axis=0) for j in range(len(matrix))]) if len(matrix)>1 else None
        else:mean=None;lomo=None
        panels[name]={'mandatory':name in MANDATORY,'contributing_mice':contributing,'computed_mice_including_subthreshold':computed,
            'unavailable_mice':[m for m in mouse_order if m not in computed],
            'required_coverage_pass':len(contributing)>=8 if name in MANDATORY else None,
            'minimum_epochs':10,'minimum_units':4,'equal_mouse_effect_means':None if mean is None else mean.tolist(),
            'leave_one_contributing_mouse_out_means':None if lomo is None else lomo.tolist(),
            'interpretation':'Mandatory failed coverage stays INCONCLUSIVE; computed nonpositive/opposite signs stay mixed; no favorable optional substitute' if name in MANDATORY else 'Descriptive cell; not independent confirmation or a new hypothesis test'}
    if any(name not in panels for name in MANDATORY):raise ValueError('Required sensitivity panel missing; do not silently omit')
    return {'mouse_order':mouse_order,'panels':panels,'all_mandatory_panel_names_preserved':True,
        'associated_broad_primary_verdict':'INCONCLUSIVE_LOCKED_PRE_D_COVERAGE_AMENDMENT','optional_panels_can_rescue':False,
        'probe_dependence':'One probe/mouse: leave-probe-out duplicates leave-one-mouse-out; not independent probe/lab replication'}
