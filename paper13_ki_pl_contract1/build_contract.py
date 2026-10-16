"""Freeze a proposed allocation/configuration from metadata only; never activates it."""
import hashlib
import json
from pathlib import Path
from audit import future_qc_contract

P=Path(__file__).resolve().parent

def build():
    a=json.loads((P/'results/initial/audit.json').read_text())
    mice=[r['mouse_id'] for r in a['records'] if r['A_potential']]
    ordered=sorted(mice,key=lambda m:hashlib.sha256(('P13v2-PL-A-v1|41|'+m).encode()).hexdigest())
    allocation={'status':'PROPOSED_ONLY_NOT_ACTIVATED','algorithm':'SHA256(P13v2-PL-A-v1|41| + mouse_id), ascending hex','development':ordered[:10],'final':ordered[10:],'minimum_each':8,'replacements':False}
    config={'status':'PROPOSED_ONLY_NOT_ACTIVATED','dataset':'000473','version':'0.230417.1502','anatomy':'provider PL','estimand':'A recording-supported aversive-task pre-tone',
            'units':8,'epochs':120,'epoch_seconds':3,'bin_seconds':.1,'warmup_bins':5,'scored_bins_per_epoch':25,
            'development_epoch_blocks':{'A':60,'B':30,'E':30},'final_epoch_blocks':{'C':60,'D':60},'training_exposure_seconds':180,
            'QC':future_qc_contract(),'ridge_grid':[.1,1,10],'seeds':[11,23,37],
            'baseline_parameter_counts':{'B0':8,'B1':96,'B2':32,'B3':176,'B4':288},'D':{'states':2,'p':[.5,.9,.98],'initial':[.5,.5],'added_free_parameters':16},
            'C':{'dimension':2,'tau_pairs_seconds':[[.1,.3],[.3,1],[.1,1]],'added_free_parameters':16,'projection':'seeded fixed orthonormal QR, not fitted'},
            'solver':{'name':'L-BFGS-B','maxiter':2000,'maxfun':100000,'maxls':40,'maxcor':10,'ftol':1e-12,'gtol':1e-5,'bounds':[-8,8]},
            'numerical':{'PG_max':.001,'independent_gradient_relative_max':1e-5,'fixed_FD_relative_step':1e-4,'FD_scan':[1e-2,1e-3,1e-4,1e-5,1e-6]},
            'primary_contrasts':['D-B4','C-B4','D-C'],'bootstrap_replicates':10000,'bootstrap_seed':130041,'primary_correction':'Holm3','alpha':.05,'control_replicates_each':999,'control_seeds':[130101,130102,130103,130104],
            'development_fit_cap_per_mouse':93,'final_fit_cap_per_mouse':19,'neural_reads_authorized':False,'M1_M7_activated':False,'one_final_assessment':True}
    for name,v in [('PROPOSED_ALLOCATION.json',allocation),('PROPOSED_CONFIG.json',config)]:
        p=P/name
        with p.open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(v,indent=2)+'\n')
    (P/'PROPOSED_PROTOCOL_FREEZE.json').write_text(json.dumps({'scope':'Proposed protocol only; no neural execution authority','hashes':{name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in ['PROPOSED_P13_V2.md','PROPOSED_ALLOCATION.json','PROPOSED_CONFIG.json','results/initial/future_qc.json']}},indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(allocation))

if __name__=='__main__':build()
