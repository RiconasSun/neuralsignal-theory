"""Offline protocol audit and synthetic oracles, never a neural-data reader."""
import csv,hashlib,json,math,socket
from pathlib import Path
import numpy as np
from scipy.stats import norm
from . import synthetic,test_contract
P=Path(__file__).resolve().parent;R=P.parent
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
def generate(out):
    out.mkdir(parents=True,exist_ok=True)
    pins=json.loads((P/'M0_INPUTS.json').read_text(encoding='utf8'))
    for rel,sha in pins['hashes'].items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==sha,rel
    assert (P/'COHORT.csv').read_bytes()==(R/'paper15_m0/results/ALLOCATION.csv').read_bytes()
    with (P/'COHORT.csv').open(encoding='utf8',newline='') as f:rows=list(csv.DictReader(f))
    summary=dict(candidate_mice=len(rows),development=sum(r['allocation']=='DEVELOPMENT' for r in rows),final=sum(r['allocation']=='FINAL_RESERVED' for r in rows),
        original_source_mice=139,original_source_sessions=459,original_source_probes=699,
        native_resolved_pilots=2,native_remaining_equivalence_unknown=18,physiological_admission_measured=False,
        partition_rule='Original native trial ordinals, not historical aggregate row count; native IDs pending future authorized metadata/QC stage',
        selected_region='MOp',primary_estimand='B4-B1 nats per actual scored nominal curated-release unit-bin')
    dump(out/'DESIGN_SUMMARY.json',summary)
    counts=[]
    for u in [5,8,12,20]:
        for k in [2,3]:
            for r in [1,2]:counts.append(dict(units=u,D_K=k,C_rank=r,**synthetic.parameter_counts(u,k,r)))
    dump(out/'PARAMETER_COUNTS.json',counts)
    curve=[dict(n=n,assumed_mean=mu,assumed_SD=sd,optimistic_known_SD_Gaussian_power=float(norm.cdf(math.sqrt(n)*mu/sd-1.6448536269514722)))
        for n in [6,7,8] for mu in [.001,.005,.01] for sd in [.002,.005,.01]]
    dump(out/'HYPOTHETICAL_DESIGN_CURVE.json',dict(not_empirical_power=True,not_exact_signflip_power=True,not_used_to_change_cohort=True,scenarios=curve))
    return ['DESIGN_SUMMARY.json','PARAMETER_COUNTS.json','HYPOTHETICAL_DESIGN_CURVE.json']
def main():
    def denied(*a,**k):raise RuntimeError('M1 saved-only verifier denies networking')
    socket.create_connection=denied;socket.socket.connect=denied
    out=P/'work/reproduced';names=generate(out)
    for name in names:assert (out/name).read_bytes()==(P/'results'/name).read_bytes(),name
    frozen=P/'PROTOCOL_FREEZE.json'
    if frozen.exists():
        for rel,sha in json.loads(frozen.read_text(encoding='utf8'))['hashes'].items():assert hashlib.sha256((P/rel).read_bytes()).hexdigest()==sha,rel
    tests=test_contract.run()
    rec=dict(network_denied=True,large_neural_cache_read=False,new_real_neural_access=False,real_model_fits=0,real_model_scores=0,
        protocol_results_reproduced=names,cohort_byte_identical=True,historical_input_pins=len(json.loads((P/'M0_INPUTS.json').read_text(encoding='utf8'))['hashes']),
        synthetic_tests=tests['tests'],production_worker_certified=False,protocol_freeze_verified=frozen.exists())
    dump(P/'work/SAVED_REPRODUCTION_RECEIPT.json',rec);print(json.dumps(rec,indent=2))
if __name__=='__main__':main()
