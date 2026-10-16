"""Prospective proposed-contract corrections after preserved independent r1 review."""
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parent

def main():
    c=json.loads((P/'PROPOSED_CONFIG.json').read_text())
    c.update(proposal_version=2,final_fit_cap_per_mouse=22,
             continuous_index='c_t=counts in bin t; z_t=standardize(c_t); h_1=0; h_t=R*h_(t-1)+(I-R)*Q.T*z_(t-1) for t>=2; score c_tthen observe c_t',
             sign_flip_null='Independent fair signs conditional on absolute mouse differences; centered sign symmetry, NOT unrestricted zero mean',
             inference_gate='Without defensible symmetry/independence/sampling assumptions, conditional descriptive p only; withhold confirmatory claim',
             strongest_baseline='B* development Bmean maximum across selected B0-B4, ties1e-12lower parameter count then Bnumber; final Cfrom scratch',
             static_comparator='S existing p=.5grid; development one-SElargest ridge; Aobjective start; final C3starts',
             claim_guard_family=['D-B*','C-B*','D-S'],claim_guard_correction='Holm3; guards only withhold primary interpretation',
             conditional_model_null='Frozen B* sequential Poisson,999replicates, D/C-B*exceedance Holm2',
             sensitivity_unit_operator='Omitted source standardized neural terms=0in B2-B4and Cinput; HMM score/filter only retained units; original scalers/intercepts/nuisance; denominator retained unit-bins',
             sensitivity_anatomy={'mandatory':'retain PL5/PL6a from original8,>=4units','exact_PL':'structurally empty descriptive N/A fixed before neural outcomes','census':{'PL5':1064,'PL6a':754,'PL2/3':68,'PL6b':14,'PL':0}},
             sensitivity_recent_event='Whole original epoch censor: onset in[start-5,stop) or supplied interval overlap; no replacement/bin/covariate ablation',
             sensitivity_minimum={'final_mice':8,'D_epochs_per_mouse':10,'retained_units':4,'missing_required_panel':'INCONCLUSIVE','opposite_sign':'MIXED'},
             sensitivity_alignment='Shift original windows+-100ms; no response bins ending after original tone; masks/support/partitionoverlap rechecked, no replacement')
    (P/'PROPOSED_CONFIG.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
    (P/'PROPOSED_PROTOCOL_FREEZE_r2.json').write_text(json.dumps({'scope':'Proposed r2only; no neural execution authority','prior_snapshot':'PROPOSED_PROTOCOL_FREEZE.json and reviewed_r1_package.zip','hashes':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['PROPOSED_P13_V2.md','PROPOSED_ALLOCATION.json','PROPOSED_CONFIG.json','results/initial/future_qc.json']}},indent=2)+'\n',encoding='utf8',newline='\n')

if __name__=='__main__':main()
