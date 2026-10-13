"""Equal-mouse/all-seed frozen configuration selection, never final-data selection."""
import numpy as np

SEEDS={11,23,37}


def candidates(rows,sessions,family,region=None):
    values=[]
    configurations={tuple((k,r.get(k)) for k in ('family','kind','size','ridge')) for r in rows if r['family']==family}
    regions=[region] if region else ['CA1','DG']
    for config in sorted(configurations,key=str):
        definition=dict(config)
        selected=[r for r in rows if all(r.get(k)==v for k,v in config) and r['region'] in regions]
        expected={(s,roi,seed) for s in sessions for roi in regions for seed in SEEDS}
        identities={(r['session_id'],r['region'],r['seed']) for r in selected}
        if identities!=expected or len(selected)!=len(expected) or any(r['converged'] is not True for r in selected):continue
        scores=[];parameters=[]
        for session in sessions:
            local=[r for r in selected if r['session_id']==session]
            scores.append(float(np.mean([r['validation_LL_nats_per_unit_bin'] for r in local])))
            parameters.append(float(np.mean([r['parameter_count'] for r in local])))
        values.append(dict(config=definition,mouse_scores=scores,mean=float(np.mean(scores)),
            SE=float(np.std(scores,ddof=1)/np.sqrt(len(scores))),mean_parameters=float(np.mean(parameters))))
    return values


def select(rows,sessions):
    output=dict(mouse_count=len(sessions),configurations={},baselines={},raw_maxima={},selection='Frozen pooled equal-mouse one-SE/all-seed; baseline maximum separately per ROI',
                final_evaluation_used=False,preferred_biological_regime_claim=False)
    for region in ('CA1','DG'):
        options=candidates(rows,sessions,'baseline',region)
        if not options:raise RuntimeError('NO_ELIGIBLE_BASELINE')
        chosen=min(options,key=lambda x:(-x['mean'],x['mean_parameters'],-(x['config']['ridge'] or 0),str(x['config'])))
        output['baselines'][region]=chosen
    for family in ('Discrete','Continuous','Hybrid'):
        options=candidates(rows,sessions,family)
        if not options:raise RuntimeError('FAMILY_HAS_NO_ELIGIBLE_CONFIGURATION:'+family)
        best=min(options,key=lambda x:(-x['mean'],x['mean_parameters'],x['config']['size'],-x['config']['ridge']))
        threshold=best['mean']-best['SE']
        admitted=[x for x in options if x['mean']>=threshold]
        chosen=min(admitted,key=lambda x:(x['mean_parameters'],x['config']['size'],-x['config']['ridge']))
        output['configurations'][family]=chosen;output['raw_maxima'][family]=best
        output.setdefault('eligible_configuration_counts',{})[family]=len(options)
        output.setdefault('one_SE_thresholds',{})[family]=threshold
    return output
