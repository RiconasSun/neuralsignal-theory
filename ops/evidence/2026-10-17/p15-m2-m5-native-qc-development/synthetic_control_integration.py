"""Full successful 4x999 integration fixture, never real neural data or fitting."""
import datetime
import time
import socket
import numpy as np
from paper15_dev.source import P,R,dump
from paper15_dev.training import build_model,sha
from paper15_dev.features import design,dct_state
from paper15_dev.controls import history_from_microbins,stratum_keys
from paper15_dev.evaluation_support import FrozenPredictors
from paper15_dev.evaluation import run_controls


def main():
    def denied(*a,**kw):raise RuntimeError('Synthetic-only fixture denies network/neural array files')
    np.load=denied;socket.create_connection=denied;socket.socket.connect=denied
    started=time.perf_counter();rng=np.random.Generator(np.random.PCG64(150900))
    y=rng.poisson(.15,(40,20,8));nx=rng.normal(0,.2,(40,20,37))
    x,scales,active=design(nx,history_from_microbins(y),10)
    arrays=dict(x=x,y=y,active=active,trial_ids=np.arange(40));prep=dict(scales=scales,C_scales={})
    for rank in [1,2]:
        for tau in [.1,.25]:
            key=f'C_r{rank}_tau{tau}';q,cs=dct_state(y,rank,tau)
            arrays[key]=q;arrays[key+'_active']=np.asarray(cs['q_scale']['active']);prep['C_scales'][key]=cs
    predictors=FrozenPredictors.__new__(FrozenPredictors);predictors.configs={};predictors.parameters={}
    for family in ['B0','B1','B2','B3','B4','D','C','S']:
        configs=[dict(family=family,ridge=.1,k=2 if family=='D' else 3,rank=1,tau=.1,seed=s)
            for s in ([11,23,37] if family in ('D','S') else [11])]
        predictors.configs[family]=configs;predictors.parameters[family]=[]
        for c in configs:
            model=build_model(arrays,c);theta=model.initialize(c['seed'])
            theta[8:model.nlin]=rng.normal(0,.01,model.nlin-8)
            predictors.parameters[family].append(theta)
    trials=[dict(contrastLeft=.25,contrastRight=None) for _ in range(40)]
    metadata=dict(E_trial_ids=list(range(40)),role_bounds=[0,40],
        keys_N2=stratum_keys(trials,np.arange(40),[0,40],np.zeros(40),0.),
        keys_N3=stratum_keys(trials,np.arange(40),[0,40]),
        coverage={suite:dict(available=True,trial_ids=list(range(40)),epochs=40,total_epochs=40) for suite in ['N1','N2','N3','N4']})
    journal=P/'work/full_synthetic_reference_journals';assert not journal.exists(),'Preserve complete or interrupted synthetic attempt'
    suites=run_controls('SYNTHETIC_ONLY_150900',arrays,predictors,prep,metadata,journal)
    assert set(suites)=={'N1','N2','N3','N4'}
    for panel in suites.values():
        assert panel['status']=='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE' and panel['replicates_completed']==999
        assert len(panel['mapping_sha256'])==len(panel['seeds'])==999
        assert np.isfinite(np.asarray(panel['reference_effects'],float)).all()
    folder=R/'ops/evidence/2026-10-17/p15-m2-m5-native-qc-development'
    result=folder/'M5_FULL_SYNTHETIC_CONTROL_INTEGRATION.json';assert not result.exists()
    dump(result,dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='SYNTHETIC_INTEGRATION_PASS',
        epochs=40,units=8,bins_per_epoch=20,fixture_seed=150900,replicate_bundles=3996,
        suites={k:dict(replicates_completed=v['replicates_completed'],all_statistics_finite=True,
            original=v['observed'],journal_sha256=sha(journal/(k+'.jsonl'))) for k,v in suites.items()},
        source_hashes={n:sha(P/n) for n in ['models.py','training.py','features.py','controls.py','evaluation.py','evaluation_support.py']},
        fixture_source_sha256=sha(__import__('pathlib').Path(__file__)),seconds=time.perf_counter()-started,
        model_family_predictions_per_bundle=7,N3_family_predictions=2,D_S_members_per_ensemble=3,
        interpretation='Full successful synthetic prediction/journaling/iteration integration only, not real Development/Final control evidence',
        network_denied=True,neural_array_file_loading_denied=True,real_fits=0,real_B_E_access=False,Final_access=False))
    print('Full synthetic4x999 integration PASS; no real neural access/fits',flush=True)


if __name__=='__main__':main()
