"""Complete frozen development model state for scoring; no neural source IO."""
import numpy as np
from .source import P,ROOT,sha
from . import baseline_A as b
from . import families as f
from .fit_engine import ScientificStop


def gates():
    model_source=f.approved();m2,qcs,baselines,m3=f.prior_gates()
    numerical=b.read(P/'results/M4_A_GATE.json');selected=b.read(P/'results/M4_MODEL_SELECTION.json')
    if numerical.get('M4_A_NUMERICS')!='PASS' or selected.get('M4')!='PASS':raise ScientificStop('Complete M4 required before E')
    if numerical['required']!=540 or numerical['completed']!=540 or len(numerical['fits'])!=540:raise ScientificStop('All540D/C fits required')
    if selected['required_new_fits']!=540 or selected['cumulative_development_fits']!=930:raise ScientificStop('M4 fit budget/denominator mismatch')
    rows={}
    for item in numerical['fits']:
        path=ROOT/item['path']
        if sha(path.read_bytes())!=item['sha256']:raise ScientificStop('M4 numerical artifact mismatch')
        record=b.read(path)
        if record['status']!='PASS' or record['PG']>.001 or record['source_hash']!=model_source:raise ScientificStop('Required family numerical/source failure')
        if record['identity']['mouse_id']!=item['mouse_id'] or record['identity']['partition']!='A' or not record['real_data'] or len(record['theta'])!=16:
            raise ScientificStop('Family parameter/training identity mismatch')
        for checkpoint in ['initial','intermediate_first_callback','endpoint']:
            certificate=record['derivatives'][checkpoint]
            if not certificate['pass'] or certificate['numerical_gate_step']!=1e-4 or certificate['AD_error']['max_relative']>1e-5 or certificate['fixed_FD_error']['max_relative']>1e-5:
                raise ScientificStop('Required family independent certificate failure')
        endpoint=record['derivatives']['endpoint']
        if record['theta']!=endpoint['theta'] or f.m.pg(record['theta'],endpoint['analytical_gradient'])>.001:
            raise ScientificStop('Family endpoint identity/PG mismatch')
        key=path.stem
        if (item['mouse_id'],key) in rows:raise ScientificStop('Duplicate family fit identity')
        rows[(item['mouse_id'],key)]=record
    expected={(mouse,f.D_key(p,ridge,seed)) for mouse in m2['eligible_development'] for p,ridge,seed in f.D_schedule()}
    expected|={(mouse,f.C_key(tau,ridge,seed)) for mouse in m2['eligible_development'] for tau,ridge,seed in f.C_schedule()}
    if set(rows)!=expected:raise ScientificStop('D/C full candidate roster mismatch')
    return m2,qcs,baselines,m3,rows,selected


def build(mouse,qc,baselines,m3,family_records,m4):
    if qc['mouse_id']!=mouse or qc['role']!='development' or qc['partition']!='A':raise PermissionError('Only original A-fitted models in development bundle')
    bundle={'mouse_id':mouse,'training_partition':'A','training_state_sha256':qc['training_state_sha256'],
        'units':qc['selected_units'],'unit_QC':{str(a['unit_id']):a for a in qc['attempts'] if a['pass']},
        'baseline_thetas':{},'baseline_scalers':{},'source_fit_requests':{},'Bstar':m3['strongest_baseline']['B_star']}
    for name in ['B0','B1','B2','B3','B4']:
        ridge=m3['selected_baselines'][name]['selected_ridge'];chosen=b.choose_seed([baselines[(mouse,name,ridge,seed)] for seed in f.SEEDS])
        path=P/'results/m3_A/preprocessing'/(mouse+'_'+name+'.json')
        if sha(path.read_bytes())!=chosen['identity']['scaler_sha256']:raise ScientificStop('Selected baseline scaler mismatch')
        bundle['baseline_thetas'][name]=chosen['theta'];bundle['baseline_scalers'][name]=b.read(path)
        bundle['source_fit_requests'][name]=chosen['full_request_sha256']
    for name,configuration in [('D',m4['D_selection']['selected_configuration']),('S',{'p':.5,'ridge':m4['S_selection']['selected_ridge']})]:
        p=configuration['p'];ridge=configuration['ridge']
        chosen=b.choose_seed([family_records[(mouse,f.D_key(p,ridge,seed))] for seed in f.SEEDS])
        bundle[name]={'theta':chosen['theta'],'p':p,'ridge':ridge,'A_selected_seed':chosen['identity']['configuration']['seed'],
            'reporting_state_order':np.argsort(np.asarray(chosen['theta']).reshape(2,8).sum(axis=1),kind='stable').tolist()}
        bundle['source_fit_requests'][name]=chosen['full_request_sha256']
    configuration=m4['C_selection']['selected_configuration'];tau=configuration['tau'];seed=configuration['seed'];ridge=configuration['ridge']
    chosen=family_records[(mouse,f.C_key(tau,ridge,seed))]
    path=P/'results/m4/preprocessing'/mouse/f'C_tau{tau[0]:g}-{tau[1]:g}_seed{seed}.json'
    if sha(path.read_bytes())!=chosen['identity']['scaler_sha256']:raise ScientificStop('Selected C A-state mismatch')
    bundle['C']={'theta':chosen['theta'],'tau':tau,'seed':seed,'ridge':ridge,'state':b.read(path)}
    bundle['source_fit_requests']['C']=chosen['full_request_sha256']
    return bundle
