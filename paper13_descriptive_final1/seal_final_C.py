"""Audit and seal completed original C states without fitting or D neural access."""
import json
import numpy as np
from paper13_ki_execution1.source import ROOT,ALLOCATION,sha
from .common import P,OLD
from paper13_ki_execution1 import baseline_A as b
from . import final_C
from paper13_ki_execution1 import models as m
from paper13_ki_execution1.features import nuisance
from paper13_ki_execution1.fit_engine import ScientificStop,digest_arrays
from paper13_ki_execution1.descriptive_metadata import describe
from paper13_ki_execution1 import sensitivity_plan
from paper13_ki_execution1.calibration_state import validate as validate_C_bundle


def run():
    source=final_C.approved();gate=b.read(P/'results/FINAL_C_GATE.json')
    if gate.get('FINAL_C_NUMERICS')!='PASS' or gate['source_freeze']!=source or gate['required']!=198 or gate['completed']!=198 or len(gate['fits'])!=198:
        raise ScientificStop('Complete original198C fit gate required before saved sealing')
    by_id={r['mouse_id']:r for r in ALLOCATION if r['role']=='final'}
    if gate['mouse_order']!=sorted(by_id) or set(gate['models'])!=set(by_id):raise ScientificStop('Original nine final mice required')
    artifacts={};records={};certificates=[];descriptors={};models={}
    def bind(path):
        path=path.resolve();name=str(path.relative_to(ROOT)).replace('\\','/');digest=sha(path.read_bytes());artifacts[name]=digest;return digest
    for item in gate['fits']:
        path=ROOT/item['path']
        if bind(path)!=item['sha256']:raise ScientificStop('C fit checksum mismatch')
        r=b.read(path);identity=r['identity'];mouse=identity['mouse_id']
        if mouse not in by_id or identity['partition']!='C' or not r['real_data'] or r['status']!='PASS' or r['source_hash']!=source:
            raise ScientificStop('C fitted source/partition/role failure')
        if r['full_request_sha256'] in records or not np.isfinite(r['objective']) or r['PG']>.001:raise ScientificStop('C duplicate/finite/PG failure')
        for name in ['initial','intermediate_first_callback','endpoint']:
            cert=r['derivatives'][name]
            if not cert['pass'] or cert['numerical_gate_step']!=1e-4 or cert['AD_error']['max_relative']>1e-5 or cert['fixed_FD_error']['max_relative']>1e-5:
                raise ScientificStop('Original C independent derivative gate failed')
            analytic=np.asarray(cert['analytical_gradient']);automatic=np.asarray(cert['independent_AD_gradient']);fd=np.asarray(cert['fixed_FD_gradient'])
            if m.gradient_errors(analytic,automatic)!=cert['AD_error'] or m.gradient_errors(analytic,fd)!=cert['fixed_FD_error']:
                raise ScientificStop('C coordinate certificate error reconstruction mismatch')
            certificates.append(cert)
        endpoint=r['derivatives']['endpoint']
        if r['theta']!=endpoint['theta'] or m.pg(r['theta'],endpoint['analytical_gradient'])>.001:raise ScientificStop('C endpoint identity mismatch')
        trajectory=path.with_suffix('.trajectory.jsonl');bind(trajectory)
        lines=[json.loads(line) for line in trajectory.read_text(encoding='utf8').splitlines()]
        if lines!=r['trajectory']:raise ScientificStop('External C trajectory differs from embedded history')
        records[r['full_request_sha256']]=r
    m3=b.read(OLD/'results/M3_BASELINE_SELECTION.json');m4=b.read(OLD/'results/M4_MODEL_SELECTION.json')
    for mouse in gate['mouse_order']:
        record=by_id[mouse];entry=gate['models'][mouse];path=ROOT/entry['path']
        if bind(path)!=entry['sha256']:raise ScientificStop('C model checksum mismatch')
        model=b.read(path);validate_C_bundle(model);qc_path=OLD/'results/qc'/(mouse+'.json');qc=b.read(qc_path);bind(qc_path);bind(qc_path.with_suffix('.attempts.jsonl'))
        if model['training_partition']!='C' or model['mouse_id']!=mouse or model['units']!=qc['selected_units'] or len(model['all_C_fit_requests'])!=22:
            raise ScientificStop('Incomplete C model identity/units/requests')
        if model['Bstar']!=m3['strongest_baseline']['B_star'] or model['original_epochs']!=record['epochs'] or model['sensitivity_unit_masks']!=sensitivity_plan.unit_panels(model) or model['sensitivity_metadata']!=sensitivity_plan.metadata(record):
            raise ScientificStop('Frozen C comparator/unit/epoch/sensitivity configuration mismatch')
        if {r['full_request_sha256'] for r in records.values() if r['identity']['mouse_id']==mouse}!=set(model['all_C_fit_requests'].values()):
            raise ScientificStop('C model full-request accounting mismatch')
        bind(ROOT/qc['training_state_file']);y,ids,epochs=final_C.load_C(record,qc);q=nuisance(record,epochs)
        for name in ['B0','B1','B2','B3','B4']:
            scaler_path=P/'results/final_C/preprocessing'/mouse/(name+'.json');bind(scaler_path)
            _,expected=final_C.design(y,q,name)
            if expected!=model['baseline_scalers'][name] or expected!=b.read(scaler_path):raise ScientificStop('C-only baseline preprocessing mismatch')
            candidates=[r for r in records.values() if r['identity']['mouse_id']==mouse and r['identity']['configuration'].get('baseline')==name]
            selected=b.choose_seed(candidates)
            if selected['theta']!=model['baseline_thetas'][name] or selected['full_request_sha256']!=model['source_fit_requests'][name]:raise ScientificStop('Original C-objective seed selection mismatch')
            if selected['identity']['configuration']['ridge']!=m3['selected_baselines'][name]['selected_ridge']:raise ScientificStop('C baseline ridge differs from frozen B policy')
        raw,_=m.raw_features(y,q,'B4');scaler=model['baseline_scalers']['B4']
        offset=m.glm_predict(model['baseline_thetas']['B4'],m.scale(raw,{k:np.asarray(scaler[k]) for k in ['mean','sd']}));offset_hash=digest_arrays(offset)
        for name in ['D','S','C']:
            selected=records[model['source_fit_requests'][name]]
            if selected['identity']['B4_C_offset_sha256']!=offset_hash:raise ScientificStop('C shared B4 offset mismatch')
            if selected['theta']!=model[name]['theta']:raise ScientificStop('C selected family coefficients mismatch')
            if name in ['D','S']:
                frozen=m4['D_selection']['selected_configuration'] if name=='D' else {'p':.5,'ridge':m4['S_selection']['selected_ridge']}
                if model[name]['p']!=frozen['p'] or model[name]['ridge']!=frozen['ridge']:raise ScientificStop('C family differs from globally frozen development policy')
                candidates=[r for r in records.values() if r['identity']['mouse_id']==mouse and r['identity']['configuration'].get('family')==name]
                if b.choose_seed(candidates)['full_request_sha256']!=model['source_fit_requests'][name]:raise ScientificStop('C family minimum-objective/lower-seed mismatch')
        config=model['C'];_,state=m.continuous_features(y,config['tau'],config['seed']);expected={k:v.tolist() for k,v in state.items()}
        state_path=P/'results/final_C/preprocessing'/mouse/'C_state.json';bind(state_path)
        if expected!=config['state'] or expected!=b.read(state_path) or any(config[k]!=m4['C_selection']['selected_configuration'][k] for k in ['tau','seed','ridge']):
            raise ScientificStop('C-only continuous preprocessing/projection mismatch')
        descriptors[mouse]=describe(record,model['units']);models[mouse]=entry
    for path in [P/'results/FINAL_C_GATE.json',P/'results/RETAINED_E_CONTROLS_GATE.json',P/'results/final_C/actions.jsonl',P/'PRE_D_STOPPING_RULE_AMENDMENT.json']:
        bind(path)
    result={'COMPLETE_C_STATE':'PASS','source_freeze':source,'mouse_order':gate['mouse_order'],'models':models,'descriptive_metadata':descriptors,
        'required_fits':198,'verified_fits':len(records),'initial_intermediate_endpoint_certificates':len(certificates),
        'max_PG':max(r['PG'] for r in records.values()),'max_AD_relative':max(c['AD_error']['max_relative'] for c in certificates),
        'max_fixed_FD_relative':max(c['fixed_FD_error']['max_relative'] for c in certificates),'artifacts':artifacts,
        'selected_policies_and_sensitivity_state':'Complete frozen C model bundle per mouse; no development coefficients transferred',
        'strict_recent_event_coverage':'FAIL6vs8_RETAINED','all_three_associated_broad_claims':'INCONCLUSIVE_LOCKED_PRE_D',
        'new_model_fits_in_sealing':0,'D_neural_arrays_read':False,'original_failures_preserved':True}
    path=P/'results/FINAL_C_FULL_STATE_MANIFEST.json';digest=b.save_matching(path,result)
    receipt={'manifest_path':str(path.relative_to(ROOT)).replace('\\','/'),'manifest_sha256':digest,'all_source_model_QC_preprocessing_artifacts':len(artifacts),
        'models':9,'fits':198,'numerical_certificates':len(certificates),'saved_state_only':True,'D_neural_arrays_read':False,'scientific_broad_confirmation':'INCONCLUSIVE_LOCKED'}
    b.save_matching(P/'results/FINAL_C_SEAL_RECEIPT.json',receipt);print(receipt)


if __name__=='__main__':run()
