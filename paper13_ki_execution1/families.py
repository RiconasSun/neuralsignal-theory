"""Frozen tractable families: all required A fits, then global B selection."""
import json
import numpy as np
from .source import P,ROOT,ALLOCATION,CONFIG,sha
from . import baseline_A as b
from . import development_B as dev
from . import models as m
from .features import nuisance
from .fit_engine import fit,ScientificStop,digest_arrays
from .selection import ridge_choice
from .qc import durable_record

TAUS=[(.1,.3),(.3,1.),(.1,1.)]
PS=[.5,.9,.98]
RIDGES=[.1,1.,10.]
SEEDS=[11,23,37]


def D_schedule():return [(p,ridge,seed) for p in PS for ridge in RIDGES for seed in SEEDS]
def C_schedule():return [(tau,ridge,seed) for tau in TAUS for ridge in RIDGES for seed in SEEDS]
def D_key(p,ridge,seed):return f'D_p{p:g}_ridge{ridge:g}_seed{seed}'
def C_key(tau,ridge,seed):return f'C_tau{tau[0]:g}-{tau[1]:g}_ridge{ridge:g}_seed{seed}'


def approved():
    path=P/'M4_APPROVAL.json'
    if not path.is_file():raise PermissionError('Independent frozen M4 implementation review required')
    a=b.read(path)
    if not a.get('accepted'):raise PermissionError('M4 implementation not accepted')
    freeze=P/a['freeze_file']
    if sha(freeze.read_bytes())!=a['freeze_sha256'] or sha((ROOT/a['review_path']).read_bytes())!=a['review_sha256']:
        raise PermissionError('M4 source/review mismatch')
    for name,digest in b.read(freeze)['hashes'].items():
        if sha((ROOT/name).read_bytes())!=digest:raise PermissionError('Unreviewed M4 source/artifact: '+name)
    return sha(freeze.read_bytes())


def prior_gates():
    dev.approved();m2,qcs,records=dev.numerical_gate();selection=b.read(P/'results/M3_BASELINE_SELECTION.json')
    if selection.get('M3')!='PASS' or not selection['B_only_selection'] or selection['C_E_D_scores_used']:
        raise ScientificStop('Full M3 frozen baseline selection required')
    if set(selection['mouse_order'])!=set(m2['eligible_development']):raise ScientificStop('M3/M2 mouse roster mismatch')
    return m2,qcs,records,selection


def B4_model(mouse,records,selection):
    ridge=selection['selected_baselines']['B4']['selected_ridge']
    if ridge not in RIDGES:raise ScientificStop('Selected B4 ridge outside frozen grid')
    chosen=b.choose_seed([records[(mouse,'B4',ridge,seed)] for seed in SEEDS])
    identity=selection['score_identities'][mouse][f'B4_ridge{ridge:g}']
    if identity['A_selected_seed']!=chosen['identity']['configuration']['seed'] or identity['A_full_request_sha256']!=chosen['full_request_sha256']:
        raise ScientificStop('Frozen B4 A-seed identity mismatch')
    scaler=b.read(P/'results/m3_A/preprocessing'/(mouse+'_B4.json'))
    if sha(b.canonical(scaler)+b'\n')!=chosen['identity']['scaler_sha256']:raise ScientificStop('Frozen B4 scaler identity mismatch')
    return chosen,scaler


def baseline_offset(y,q,theta,scaler):
    raw,_=m.raw_features(y,q,'B4')
    state={'mean':np.asarray(scaler['mean']),'sd':np.asarray(scaler['sd'])}
    offset=m.glm_predict(theta,m.scale(raw,state))
    if not np.isfinite(offset).all():raise ScientificStop('Nonfinite frozen B4 offset')
    return offset


def continuous_design(y,tau,seed,state=None):
    arrays=None if state is None else {k:np.asarray(v,dtype=float) for k,v in state.items()}
    x,arrays=m.continuous_features(y,tau,seed,arrays)
    return x,{k:v.tolist() for k,v in arrays.items()}


def family_score(kind,theta,y,offset,*,p=None,x=None):
    if kind=='D':
        joint=m.hmm_eval(theta,y,offset,p,0.,gradient=False,return_scores=True)
        value=float(joint[:,5:].sum()/y[:,5:].size)
    elif kind=='C':value=float(m.poisson_scores(y[:,5:],m.glm_predict(theta,x,offset)[:,5:]).mean())
    else:raise ScientificStop('Unknown predictive family')
    if not np.isfinite(value):raise ScientificStop('Nonfinite family score')
    return value


def choose_configuration(matrix,configurations,family):
    # ridge_choice uses its second argument only as a tie-priority ordering.
    # Paired mean losses and SEs depend exclusively on the score matrix.
    if family=='D':priorities=[(c['ridge'],-c['p']) for c in configurations]
    elif family=='C':priorities=[(c['ridge'],-max(c['tau']),-sum(c['tau']),-c['seed']) for c in configurations]
    else:raise ScientificStop('Unknown selection family')
    result=ridge_choice(matrix,priorities);result['tie_priority']=result.pop('selected_ridge')
    result['selected_configuration']=configurations[result['selected_index']]
    result['all_configurations']=configurations
    return result


def run():
    source_hash=approved();m2,qcs,baselines,selection=prior_gates()
    root=P/'results/m4';root.mkdir(parents=True,exist_ok=True);journal=root/'actions.jsonl'
    fits={};preprocessors={};offset_ids={};all_rows=[]
    for record in ALLOCATION:
        mouse=record['mouse_id']
        if mouse not in m2['eligible_development']:continue
        qc=qcs[mouse];y,ids,epochs=b.training_state(record,qc)
        chosen,scaler=B4_model(mouse,baselines,selection)
        offset=baseline_offset(y,nuisance(record,epochs),chosen['theta'],scaler)
        offset_ids[mouse]=digest_arrays(offset);fits[mouse]={};preprocessors[mouse]={}
        common={'real_data':True,'mouse_id':mouse,'partition':'A','unit_ids_sha256':digest_arrays(ids),
            'epochs_sha256':sha(b.canonical(epochs)),'protocol_sha256':CONFIG['protocol_sha256'],
            'A_state_sha256':qc['training_state_sha256'],'B4_A_full_request_sha256':chosen['full_request_sha256'],
            'B4_A_offset_sha256':offset_ids[mouse],'B4_scaler_sha256':chosen['identity']['scaler_sha256']}
        for p,ridge,seed in D_schedule():
            key=D_key(p,ridge,seed);configuration={'family':'D','p':p,'ridge':ridge,'seed':seed}
            identity={**common,'configuration':configuration,'scaler_sha256':chosen['identity']['scaler_sha256']}
            path=root/'fits'/mouse/(key+'.json')
            durable_record(journal,'FIT_START',mouse_id=mouse,configuration=configuration,offset_sha256=offset_ids[mouse])
            result=fit(path,'HMM',{'y':y},ridge,np.random.default_rng(seed).normal(0,.05,16),p=p,offset=offset,identity=identity,source_hash=source_hash)
            fits[mouse][key]=result
            report_order=np.argsort(np.asarray(result['theta']).reshape(2,8).sum(axis=1),kind='stable').tolist()
            all_rows.append({'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path.read_bytes()),'mouse_id':mouse,'configuration':configuration,'PG':result['PG'],'objective':result['objective'],'calls':result['calls'],'reporting_state_order_by_training_shift_sum':report_order})
            durable_record(journal,'FIT_COMPLETE',mouse_id=mouse,configuration=configuration,PG=result['PG'])
            print(json.dumps({'M4_A':mouse,**configuration,'status':result['status'],'PG':result['PG']}),flush=True)
        designs={}
        for tau,ridge,seed in C_schedule():
            feature_key=(tau,seed)
            if feature_key not in designs:
                x,state=continuous_design(y,tau,seed)
                path=root/'preprocessing'/mouse/f'C_tau{tau[0]:g}-{tau[1]:g}_seed{seed}.json'
                scaler_hash=b.save_matching(path,state)
                designs[feature_key]=(x,state,scaler_hash)
            x,state,scaler_hash=designs[feature_key]
            key=C_key(tau,ridge,seed);configuration={'family':'C','tau':list(tau),'ridge':ridge,'seed':seed}
            identity={**common,'configuration':configuration,'scaler_sha256':scaler_hash,
                'fixed_Q_sha256':digest_arrays(np.asarray(state['Q']))}
            path=root/'fits'/mouse/(key+'.json')
            durable_record(journal,'FIT_START',mouse_id=mouse,configuration=configuration,offset_sha256=offset_ids[mouse])
            result=fit(path,'C',{'y':y,'x':x},ridge,np.zeros(16),offset=offset,identity=identity,source_hash=source_hash)
            fits[mouse][key]=result;preprocessors[mouse][f'{tau[0]:g}-{tau[1]:g}_seed{seed}']=state
            all_rows.append({'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path.read_bytes()),'mouse_id':mouse,'configuration':configuration,'PG':result['PG'],'objective':result['objective'],'calls':result['calls']})
            durable_record(journal,'FIT_COMPLETE',mouse_id=mouse,configuration=configuration,PG=result['PG'])
            print(json.dumps({'M4_A':mouse,**configuration,'status':result['status'],'PG':result['PG']}),flush=True)
    required=54*len(m2['eligible_development'])
    if len(all_rows)!=required or required>540:raise ScientificStop('D/C required-fit accounting mismatch')
    b.save_matching(P/'results/M4_A_GATE.json',{'M4_A_NUMERICS':'PASS','required':required,'completed':len(all_rows),
        'fits':all_rows,'source_freeze':source_hash,'shared_B4_A_offset_sha256':offset_ids,'dynamic_B_scores_not_yet_evaluated':True})
    # No dynamic Bscore occurs until every required real D/C numerical gate passes.
    mice=sorted(m2['eligible_development']);D_scores={};C_scores={};A_seeds={}
    for record in ALLOCATION:
        mouse=record['mouse_id']
        if mouse not in mice:continue
        export=b.read(P/'results/development_B'/(mouse+'.json'));path=ROOT/export['state_file']
        if export['partition']!='B' or export['mouse_id']!=mouse or sha(path.read_bytes())!=export['state_sha256']:raise ScientificStop('B state identity mismatch')
        with np.load(path,allow_pickle=False) as state:
            y=state['counts'].copy();ids=state['unit_ids'].copy()
        if y.shape!=(30,30,8) or ids.tolist()!=[u['unit_id'] for u in qcs[mouse]['selected_units']]:raise ScientificStop('B count/selected-unit mismatch')
        chosen,scaler=B4_model(mouse,baselines,selection)
        offset=baseline_offset(y,nuisance(record,dev.B_windows(record)),chosen['theta'],scaler)
        B4score=float(m.poisson_scores(y[:,5:],offset[:,5:]).mean())
        ridge=selection['selected_baselines']['B4']['selected_ridge']
        if abs(B4score-selection['all_candidate_scores'][mouse][f'B4_ridge{ridge:g}'])>1e-12:raise ScientificStop('Original B4 Bscore not reproduced')
        D_scores[mouse]={};C_scores[mouse]={};A_seeds[mouse]={}
        for p in PS:
            for ridge in RIDGES:
                candidates=[fits[mouse][D_key(p,ridge,seed)] for seed in SEEDS];chosen=b.choose_seed(candidates)
                key=f'p{p:g}_ridge{ridge:g}';A_seeds[mouse][key]=chosen['identity']['configuration']['seed']
                value=family_score('D',chosen['theta'],y,offset,p=p)
                D_scores[mouse][key]={'score':value,'gain_over_B4':value-B4score}
                durable_record(journal,'D_B_SCORE',mouse_id=mouse,configuration=key,score=value,gain_over_B4=value-B4score)
        for tau,ridge,seed in C_schedule():
            feature_key=f'{tau[0]:g}-{tau[1]:g}_seed{seed}';x,_=continuous_design(y,tau,seed,preprocessors[mouse][feature_key])
            key=C_key(tau,ridge,seed);chosen=fits[mouse][key]
            value=family_score('C',chosen['theta'],y,offset,x=x)
            C_scores[mouse][key]={'score':value,'gain_over_B4':value-B4score}
            durable_record(journal,'C_B_SCORE',mouse_id=mouse,configuration=key,score=value,gain_over_B4=value-B4score)
    D_config=[{'p':p,'ridge':ridge} for p in PS for ridge in RIDGES]
    C_config=[{'tau':list(tau),'ridge':ridge,'seed':seed} for tau,ridge,seed in C_schedule()]
    DM=np.array([[D_scores[mouse][f"p{c['p']:g}_ridge{c['ridge']:g}"]['gain_over_B4'] for c in D_config] for mouse in mice])
    CM=np.array([[C_scores[mouse][C_key(c['tau'],c['ridge'],c['seed'])]['gain_over_B4'] for c in C_config] for mouse in mice])
    SM=np.array([[D_scores[mouse][f'p0.5_ridge{ridge:g}']['gain_over_B4'] for ridge in RIDGES] for mouse in mice])
    result={'M4':'PASS','source_freeze':source_hash,'mouse_order':mice,'D_selection':choose_configuration(DM,D_config,'D'),
        'C_selection':choose_configuration(CM,C_config,'C'),'S_selection':ridge_choice(SM,RIDGES),'D_A_selected_starts':A_seeds,
        'all_D_B_scores':D_scores,'all_C_B_scores':C_scores,'required_new_fits':required,'cumulative_development_fits':390+required,
        'static_S_additional_fits':0,'E_D_outcomes_accessed':False,'same_B4_offsets_both_families':True,
        'interpretation':'Development model selection only; temporal/beyond-Bstar/final claims require all registered guards and future gates'}
    b.save_matching(P/'results/M4_MODEL_SELECTION.json',result)
    print(json.dumps({'M4':'PASS','D':result['D_selection']['selected_configuration'],'C':result['C_selection']['selected_configuration'],
        'S_ridge':result['S_selection']['selected_ridge'],'E_D_outcomes_accessed':False}),flush=True)


if __name__=='__main__':run()
