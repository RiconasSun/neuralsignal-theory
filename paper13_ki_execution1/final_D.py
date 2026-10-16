"""One trusted-local descriptive D bundle; no fitting, tuning or retry path."""
import json
import os
import h5py
import numpy as np
from .source import P,ROOT,ALLOCATION,SourceReader,node,load_unit,cut_windows,sha
from . import baseline_A as b
from . import models as m
from .features import nuisance
from .qc import durable_record
from .fit_engine import ScientificStop
from .predictive import evaluate
from .animal_stats import summarize
from . import control_core as controls
from . import sensitivity_scores
from . import descriptive_groups
from .calibration_state import validate as validate_C_bundle,PARAMETERS

AUTHORIZATION_ID='P13-KI-PL-SCIENCE-FIRST-EXECUTION-DESC-D-001'


def approved():
    path=P/'FINAL_D_APPROVAL.json'
    if not path.is_file():raise PermissionError('Independent complete pre-D review required')
    a=b.read(path)
    if not a.get('accepted') or a['authorization_id']!=AUTHORIZATION_ID:raise PermissionError('Wrong once-only D authority')
    freeze=P/a['freeze_file']
    if sha(freeze.read_bytes())!=a['freeze_sha256'] or sha((ROOT/a['review_path']).read_bytes())!=a['review_sha256']:
        raise PermissionError('D protocol/source/review mismatch')
    for name,digest in b.read(freeze)['hashes'].items():
        if sha((ROOT/name).read_bytes())!=digest:raise PermissionError('Unreviewed pre-D state: '+name)
    return sha(freeze.read_bytes())


def prior_gates():
    c=b.read(P/'results/FINAL_C_GATE.json');e=b.read(P/'results/M6_E_CONTROLS_GATE.json');sealed=b.read(P/'results/FINAL_C_FULL_STATE_MANIFEST.json')
    if c.get('FINAL_C_NUMERICS')!='PASS' or e.get('M6_E_CONTROLS')!='PASS' or sealed.get('COMPLETE_C_STATE')!='PASS':
        raise ScientificStop('All C/E-control/full-state prerequisites required before D')
    if c['required']!=198 or c['completed']!=198 or len(c['fits'])!=198 or len(c['models'])!=9:raise ScientificStop('Exact frozen nine-mouse198fit C state required')
    if c['mouse_order']!=sealed['mouse_order'] or c['mouse_order']!=sorted(a['mouse_id'] for a in ALLOCATION if a['role']=='final'):
        raise ScientificStop('Original final mouse identities changed')
    seen=set();requests={};configurations={mouse:set() for mouse in c['mouse_order']}
    for item in c['fits']:
        path=ROOT/item['path']
        if item['path'] in seen:raise ScientificStop('Duplicate required C fit artifact')
        seen.add(item['path'])
        if sha(path.read_bytes())!=item['sha256']:raise ScientificStop('C fit artifact changed')
        r=b.read(path)
        if r['status']!='PASS' or not r['real_data'] or r['source_hash']!=c['source_freeze'] or r['identity']['partition']!='C' or r['identity']['mouse_id']!=item['mouse_id']:
            raise ScientificStop('C source/fit identity failure')
        if r['full_request_sha256'] in requests:raise ScientificStop('Duplicate C full fit request')
        requests[r['full_request_sha256']]=r;configurations[item['mouse_id']].add(b.canonical(r['identity']['configuration']))
        config=r['identity']['configuration'];n=PARAMETERS[config['baseline']] if 'baseline' in config else 16
        if np.shape(r['theta'])!=(n,):raise ScientificStop('Original C fit coefficient count mismatch')
        if not np.isfinite(r['objective']) or r['PG']>.001:raise ScientificStop('Required C numerical gate failure')
        if not 0<=r['iterations']<=2000 or not 0<r['calls']<=100000:raise ScientificStop('Original C solver/total-call budget exceeded')
        for checkpoint in ['initial','intermediate_first_callback','endpoint']:
            cert=r['derivatives'][checkpoint]
            if not cert['pass'] or cert['numerical_gate_step']!=1e-4 or cert['AD_error']['max_relative']>1e-5 or cert['fixed_FD_error']['max_relative']>1e-5:
                raise ScientificStop('Required original C independent certificate failure')
            if any(np.shape(cert[key])!=(n,) or not np.isfinite(cert[key]).all() for key in ['theta','analytical_gradient','independent_AD_gradient','fixed_FD_gradient']):raise ScientificStop('Incomplete C all-coordinate certificate')
            analytic=np.asarray(cert['analytical_gradient']);automatic=np.asarray(cert['independent_AD_gradient']);fd=np.asarray(cert['fixed_FD_gradient'])
            if m.gradient_errors(analytic,automatic)!=cert['AD_error'] or m.gradient_errors(analytic,fd)!=cert['fixed_FD_error']:
                raise ScientificStop('C reported independent error differs from saved coordinates')
        endpoint=r['derivatives']['endpoint']
        if endpoint['theta']!=r['theta'] or m.pg(r['theta'],endpoint['analytical_gradient'])>.001:raise ScientificStop('C endpoint theta/PG mismatch')
    m3=b.read(P/'results/M3_BASELINE_SELECTION.json');m4=b.read(P/'results/M4_MODEL_SELECTION.json')
    expected={b.canonical({'baseline':name,'ridge':m3['selected_baselines'][name]['selected_ridge'],'seed':seed}) for name in ['B0','B1','B2','B3','B4'] for seed in [11,23,37]}
    for name,configuration in [('D',m4['D_selection']['selected_configuration']),('S',{'p':.5,'ridge':m4['S_selection']['selected_ridge']})]:
        expected|={b.canonical({'family':name,'p':configuration['p'],'ridge':configuration['ridge'],'seed':seed}) for seed in [11,23,37]}
    expected.add(b.canonical({'family':'C',**m4['C_selection']['selected_configuration']}))
    if len(expected)!=22 or any(values!=expected for values in configurations.values()):raise ScientificStop('Exact original22Cconfiguration roster required')
    models={}
    for mouse,entry in c['models'].items():
        path=ROOT/entry['path']
        if sha(path.read_bytes())!=entry['sha256'] or entry['sha256']!=sealed['models'][mouse]['sha256']:raise ScientificStop('Complete C model seal mismatch')
        model=b.read(path)
        validate_C_bundle(model)
        if model['Bstar']!=m3['strongest_baseline']['B_star']:raise ScientificStop('Frozen strongest comparator changed')
        if model['training_partition']!='C' or model['mouse_id']!=mouse or len(model['all_C_fit_requests'])!=22 or set(model['source_fit_requests'])!={'B0','B1','B2','B3','B4','D','C','S'}:
            raise ScientificStop('Incomplete mandatory calibrated model state')
        if set(model['all_C_fit_requests'].values())!={key for key,r in requests.items() if r['identity']['mouse_id']==mouse}:raise ScientificStop('C model does not account for every required request')
        for name,key in model['source_fit_requests'].items():
            fit=requests[key];config=fit['identity']['configuration']
            if fit['identity']['mouse_id']!=mouse or config.get('baseline',config.get('family'))!=name or fit['theta']!=(model['baseline_thetas'][name] if name in PARAMETERS else model[name]['theta']):raise ScientificStop('Selected C coefficient/request/model identity mismatch')
            if name in ['D','S'] and any(config[k]!=model[name][k] for k in ['p','ridge']):raise ScientificStop('C emission model policy differs from its fitted objective')
            if name=='C' and any(config[k]!=model[name][k] for k in ['tau','seed','ridge']):raise ScientificStop('C leaky policy differs from its fitted objective')
            if name!='C':
                candidates=[r for r in requests.values() if r['identity']['mouse_id']==mouse and r['identity']['configuration'].get('baseline',r['identity']['configuration'].get('family'))==name]
                if b.choose_seed(candidates)['full_request_sha256']!=key:raise ScientificStop('Original C-objective/lower-seed selection changed')
        models[mouse]=model
    amendment=b.read(P/'PRE_D_STOPPING_RULE_AMENDMENT.json')
    if amendment['known_failed_gate']['immutable_associated_claim_verdict']!='INCONCLUSIVE' or amendment['final_D_outcome_access_before_amendment']:
        raise PermissionError('Original pre-D owner amendment/claim lock absent')
    return c,sealed,models


def consume(root,source,c,sealed):
    root.mkdir(parents=True,exist_ok=True)
    record={'authorization_id':AUTHORIZATION_ID,'source_freeze':source,
        'C_gate_sha256':sha(b.canonical(c)),'complete_C_state_sha256':sha(b.canonical(sealed)),
        'D_partition_manifest_sha256':sha(b.canonical({r['mouse_id']:[e for e in r['epochs'] if e['partition']=='D'] for r in ALLOCATION if r['role']=='final'})),
        'owner_amendment_sha256':sha((P/'PRE_D_STOPPING_RULE_AMENDMENT.json').read_bytes()),
        'meaning':'Ordinary trusted-local once-only execution log; not independently enforced custody or protection against administrator',
        'no_automatic_retry_even_after_crash':True}
    # Consumption precedes decoder, D array access and scoring. Existing marker is terminal for this execution path.
    with (root/'ONCE_EXECUTION.json').open('xb') as f:
        f.write(b.canonical(record)+b'\n');f.flush();os.fsync(f.fileno())
    return record


def window_sets(record,bundle):
    if record['role']!='final' or bundle['training_partition']!='C' or bundle['mouse_id']!=record['mouse_id']:
        raise PermissionError('D export requires exact final mouse C model')
    primary=[e for e in record['epochs'] if e['partition']=='D']
    if len(primary)!=60 or len(bundle['units'])!=8:raise ScientificStop('Original60D/eightCselected units required')
    result={'primary':{'epochs':primary,'full_bins':30}}
    for name in ['alignment_minus01','alignment_plus01']:
        plan=[e for e in bundle['sensitivity_metadata'][name] if e['partition']=='D' and e['retained']]
        bins=30 if name=='alignment_minus01' else 29
        if any(e['observed_full_bins']!=bins or e['export_stop']>e['original_tone']+1e-10 for e in plan):raise ScientificStop('Alignment response/full-bin boundary failure')
        result[name]={'epochs':[{**e,'stop':e['export_stop']} for e in plan],'full_bins':bins}
    return result


def export(record,bundle,root,journal):
    if not (root/'ONCE_EXECUTION.json').is_file():raise PermissionError('Once-only consumption record required before D decoder')
    source=approved();consumed=b.read(root/'ONCE_EXECUTION.json')
    if consumed['authorization_id']!=AUTHORIZATION_ID or consumed['source_freeze']!=source:raise PermissionError('D consumption/source identity mismatch')
    c=b.read(P/'results/FINAL_C_GATE.json');sealed=b.read(P/'results/FINAL_C_FULL_STATE_MANIFEST.json')
    if sha(b.canonical(c))!=consumed['C_gate_sha256'] or sha(b.canonical(sealed))!=consumed['complete_C_state_sha256']:
        raise PermissionError('C state changed after once-only consumption')
    model=c['models'][record['mouse_id']]
    if sha((ROOT/model['path']).read_bytes())!=model['sha256'] or bundle!=b.read(ROOT/model['path']):raise PermissionError('Only exact sealed C model/units in D export')
    sets=window_sets(record,bundle);mouse=record['mouse_id'];arrays={};counts={name:[] for name in sets};active=None
    attempt=root/'export_attempts'/(mouse+'.json');attempt.parent.mkdir(parents=True,exist_ok=True)
    with attempt.open('xb') as f:
        f.write(b.canonical({'mouse_id':mouse,'source_freeze':source,'C_model_sha256':model['sha256']})+b'\n');f.flush();os.fsync(f.fileno())
    durable_record(journal,'D_EXPORT_START',mouse_id=mouse,unit_ids=[u['unit_id'] for u in bundle['units']])
    try:
        reader=SourceReader(record)
        with h5py.File(reader,'r') as h:
            for j,unit in enumerate(bundle['units']):
                active=unit['unit_id'];durable_record(journal,'D_UNIT_EXPORT_START',mouse_id=mouse,unit_id=active)
                if int(node(h,'/units/id')[unit['row']])!=active:raise ScientificStop('Original C-selected D unit identity changed')
                raw=load_unit(h,unit['row']);unit_payload={}
                for name,configuration in sets.items():
                    epochs=configuration['epochs'];T=configuration['full_bins'];times=cut_windows(raw,epochs)
                    values=np.stack([np.histogram(ts,bins=np.arange(T+1)/10)[0] for ts in times]) if epochs else np.zeros((0,T),dtype=np.int64)
                    counts[name].append(values);arrays[f'{name}_unit{j}_times']=np.concatenate(times) if times else np.empty(0)
                    arrays[f'{name}_unit{j}_ends']=np.cumsum([len(ts) for ts in times],dtype=np.int64)
                    unit_payload[name+'_counts']=values;unit_payload[name+'_times']=arrays[f'{name}_unit{j}_times'];unit_payload[name+'_ends']=arrays[f'{name}_unit{j}_ends']
                del raw
                unit_path=root/'partial_unit_exports'/mouse/(str(active)+'.npz');unit_path.parent.mkdir(parents=True,exist_ok=True)
                with unit_path.open('xb') as f:np.savez_compressed(f,**unit_payload)
                durable_record(journal,'D_UNIT_EXPORT_COMPLETE',mouse_id=mouse,unit_id=active,
                    saved_unit_artifact=str(unit_path.relative_to(ROOT)).replace('\\','/'),saved_unit_artifact_sha256=sha(unit_path.read_bytes()));active=None
        for name in sets:arrays[name+'_counts']=np.stack(counts[name],axis=-1).astype(np.int64)
        arrays['unit_ids']=np.array([u['unit_id'] for u in bundle['units']],dtype=np.int64)
        path=root/'states'/(mouse+'.npz');path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as f:np.savez_compressed(f,**arrays)
        receipt={'mouse_id':mouse,'partition':'D_WITH_FROZEN_ALIGNMENT_SENSITIVITIES','state_file':str(path.relative_to(ROOT)).replace('\\','/'),
            'state_sha256':sha(path.read_bytes()),'unit_ids':arrays['unit_ids'].tolist(),
            'parent_ordinals':{name:[e['ordinal'] for e in config['epochs']] for name,config in sets.items()},
            'window_metadata_sha256':sha(b.canonical(sets)),'no_D_QC_scaling_selection_fitting':True}
        b.save_matching(root/'states'/(mouse+'.json'),receipt)
        durable_record(journal,'D_EXPORT_COMPLETE',mouse_id=mouse,state_sha256=receipt['state_sha256'])
        return receipt,sets,arrays
    except Exception as exc:
        durable_record(journal,'D_EXPORT_ERROR',mouse_id=mouse,unit_id=active,error_type=type(exc).__name__,error=str(exc));raise


def run_controls(data,observed,mice,root,journal):
    folder=root/'controls';folder.mkdir(parents=True,exist_ok=True);arrays={}
    for suite in controls.SUITES:
        path=folder/(suite+'.npy')
        with path.open('xb'):pass
        array=np.lib.format.open_memmap(path,mode='w+',dtype=np.float64,shape=(999,len(mice),len(controls.LABELS)));array[:]=np.nan;array.flush();arrays[suite]=array
        rng=np.random.default_rng(controls.SEEDS[suite])
        for replicate in range(999):
            durable_record(journal,'D_CONTROL_REPLICATE_START',suite=suite,replicate=replicate)
            for index,mouse in enumerate(mice):
                y,q,bundle,ordinals=data[mouse]
                try:
                    with np.errstate(over='raise',invalid='raise',divide='raise'):result=controls.replicate(suite,y,q,bundle,ordinals,rng)
                except Exception as exc:
                    array.flush();durable_record(journal,'D_CONTROL_ERROR',suite=suite,replicate=replicate,mouse_id=mouse,error_type=type(exc).__name__,error=str(exc))
                    exc.final_control_context={'stage':'null_control','suite':suite,'replicate':replicate,'mouse_id':mouse}
                    raise
                array[replicate,index]=[result['scores'][name] for name in controls.LABELS];array.flush()
                durable_record(journal,'D_MOUSE_CONTROL_COMPLETE',suite=suite,replicate=replicate,mouse_id=mouse,nominal_unit_bins=result['nominal_unit_bins'])
            durable_record(journal,'D_CONTROL_REPLICATE_COMPLETE',suite=suite,replicate=replicate)
            if (replicate+1)%100==0:print(json.dumps({'final_D_control':suite,'completed_replicates':replicate+1}),flush=True)
        durable_record(journal,'D_CONTROL_SUITE_COMPLETE',suite=suite,replicates=999,artifact_sha256=sha(path.read_bytes()))
    report,means=controls.summarize(arrays,observed,mice)
    path=folder/'equal_mouse_distributions.npz'
    with path.open('xb') as f:np.savez_compressed(f,**means)
    report['artifacts']={name:{'path':str((folder/(name+'.npy')).relative_to(ROOT)).replace('\\','/'),'sha256':sha((folder/(name+'.npy')).read_bytes())} for name in controls.SUITES}
    report['equal_mouse_distributions_sha256']=sha(path.read_bytes())
    return report


def run():
    source=approved();c,sealed,models=prior_gates();mice=c['mouse_order'];root=P/'results/final_D'
    consumed=consume(root,source,c,sealed);journal=root/'actions.jsonl'
    durable_record(journal,'FINAL_D_EXECUTION_START',authorization_id=AUTHORIZATION_ID,source_freeze=source)
    scores={};primary={};sensitivities={};identities={};data={};active=None
    try:
        for record in ALLOCATION:
            mouse=record['mouse_id']
            if mouse not in mice:continue
            active=mouse;bundle=models[mouse];receipt,sets,arrays=export(record,bundle,root,journal)
            y=arrays['primary_counts'];epochs=sets['primary']['epochs'];q=nuisance(record,epochs)
            if y.shape!=(60,30,8):raise ScientificStop('Exact primary D denominator required')
            durable_record(journal,'D_PRIMARY_SCORE_START',mouse_id=mouse,model_roles=8)
            with np.errstate(over='raise',invalid='raise',divide='raise'):result=evaluate(y,q,bundle,return_sequences=True)
            bin_path=root/(mouse+'_bin_scores.npz')
            with bin_path.open('xb') as f:np.savez_compressed(f,**result.pop('joint_bin_log_scores'))
            primary[mouse]=result;scores[mouse]={k:result['scores'][k] for k in ['B4','D','C','Bstar','S']}
            aligned={}
            for name in ['alignment_minus01','alignment_plus01']:
                config=sets[name];q_shift=nuisance(record,config['epochs'])[:,:config['full_bins']] if config['epochs'] else np.empty((0,config['full_bins'],11))
                aligned[name]={'counts':arrays[name+'_counts'],'q':q_shift,'parent_ordinals':receipt['parent_ordinals'][name],'unit_ids':receipt['unit_ids']}
            with np.errstate(over='raise',invalid='raise',divide='raise'):
                sensitivities[mouse]=sensitivity_scores.score_mouse(y,q,bundle,record,sealed['descriptive_metadata'][mouse],aligned)
            b.save_matching(root/'sensitivities'/(mouse+'.json'),sensitivities[mouse])
            data[mouse]=(y,q,bundle,[e['ordinal'] for e in epochs]);identities[mouse]={'D_state_sha256':receipt['state_sha256'],'C_model_sha256':c['models'][mouse]['sha256'],'bin_scores_sha256':sha(bin_path.read_bytes())}
            b.save_matching(root/'primary_mouse'/(mouse+'.json'),{'mouse_id':mouse,'result':result,'state_identity':identities[mouse],
                'interpretation':'Descriptive partial final bundle only; required controls and sensitivities remain; broadclaim INCONCLUSIVE lock cannot be rescued'})
            durable_record(journal,'D_MOUSE_PRIMARY_SENSITIVITY_COMPLETE',mouse_id=mouse,nominal_unit_bins=result['nominal_unit_bins'],scores=result['scores'])
            print(json.dumps({'final_D_mouse_scored':mouse,'nominal_unit_bins':result['nominal_unit_bins'],'no_fitting_or_selection':True}),flush=True)
        stats,bootstrap=summarize(scores,mice)
        boot_path=root/'mouse_bootstrap.npz'
        with boot_path.open('xb') as f:np.savez_compressed(f,**bootstrap)
        for name in ['D_minus_B4','C_minus_B4','D_minus_C']:
            stats['contrasts'][name]['final_claim_status']='INCONCLUSIVE_DUE_TO_FAILED_MANDATORY_RECENT_EVENT_COVERAGE; PRE_D_OWNER_AMENDMENT_LOCK'
        stats['owner_locked_broad_primary_verdicts_applied']=True
        group_report=descriptive_groups.summarize({mouse:primary[mouse]['scores'] for mouse in mice},sealed['descriptive_metadata'],mice)
        b.save_matching(root/'primary_results.json',{'execution_component':'PRIMARY_DESCRIPTION_COMPLETE_FULL_BUNDLE_PENDING','mouse_order':mice,
            'per_mouse':primary,'statistics':stats,'descriptive_group_dependence':group_report,'bootstrap_sha256':sha(boot_path.read_bytes()),'no_second_evaluation_authorized':True})
        nulls=run_controls(data,{mouse:primary[mouse]['scores'] for mouse in mice},mice,root,journal)
        sensitivity_report=sensitivity_scores.aggregate(sensitivities,mice)
        result={'FINAL_D_EXECUTION':'VALIDLY_COMPLETED_ONCE_DESCRIPTIVE','source_freeze':source,'authorization_id':AUTHORIZATION_ID,
            'owner_stopping_amendment':'PRE_D_COVERAGE_INFORMED_EXCEPTION; original6vs8failure not cleared','mouse_order':mice,
            'per_mouse':primary,'state_identities':identities,'statistics':stats,'null_controls':nulls,'sensitivity_report':sensitivity_report,
            'descriptive_group_dependence':group_report,
            'bootstrap_sha256':sha(boot_path.read_bytes()),'fits_or_model_selection_on_D':0,'D_reassessment_authorized':False,
            'affected_broad_confirmatory_primary_verdicts':'ALL_THREE_INCONCLUSIVE_LOCKED; no VALIDATED or temporal-mechanism claim',
            'scientific_limits':'Selected curated PL units, aversive pre-tone, single lab/probe per mouse; unknown movement/arousal, anatomy/sorting/source/event carryover; conditional sign/exchangeability/plugin-null assumptions'}
        b.save_matching(P/'results/FINAL_D_RESULTS.json',result)
        durable_record(journal,'FINAL_D_EXECUTION_COMPLETE',mouse_count=len(mice),one_assessment=True)
        print(json.dumps({'FINAL_D_EXECUTION':'VALIDLY_COMPLETED_ONCE_DESCRIPTIVE','all_three_broad_primary_verdicts':'INCONCLUSIVE'}),flush=True)
    except Exception as exc:
        failed_context=getattr(exc,'final_control_context',{'stage':'primary_or_sensitivity','mouse_id':active})
        durable_record(journal,'FINAL_D_EXECUTION_ERROR',context=failed_context,error_type=type(exc).__name__,error=str(exc))
        b.save_matching(P/'results/FINAL_D_FAILURE.json',{'FINAL_D_EXECUTION':'INCOMPLETE_REQUIRED_GATE_FAILED','source_freeze':source,
            'context':failed_context,'error_type':type(exc).__name__,'error':str(exc),'one_shot_marker_consumed':True,'retry_or_post_D_repair_authorized':False})
        raise


if __name__=='__main__':run()
