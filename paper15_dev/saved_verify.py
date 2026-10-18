"""Saved-evidence reproduction only: no source download, neural reads or fitting."""
import hashlib
import json
import socket
import unittest
import importlib.metadata
import numpy as np
from .source import P, R


def archive_paths():
    excluded={'ARCHIVE_FREEZE.json'}
    return {p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and
        not any(x in ('work','__pycache__') for x in p.relative_to(P).parts) and p.relative_to(P).as_posix() not in excluded}


def verify_archive(freeze):
    required={'models.py','features.py','training.py','selection.py','sensitivities.py','sensitivity_fits.py',
        'evaluation.py','evaluation_support.py','controls.py','statistics.py','saved_verify.py','saved_audit.py',
        'PRODUCTION_GATE.json','SOURCE_FILE_FREEZE.json','NEURAL_HEADER_FREEZE.json','A_FIT_PLAN.json','SENSITIVITY_FIT_PLAN.json',
        'SENSITIVITY_GATE.json','SELECTION_FREEZE.json','E_EXPLORATORY_GATE.json','E_BATCH_CLAIM.json','REFERENCE_METADATA_FREEZE.json',
        'results/M2_PHYSIOLOGY_GATE.json','results/BASELINE_ATTEMPTS_COMPLETE.json','results/DYNAMIC_ATTEMPTS_COMPLETE.json',
        'results/SENSITIVITY_PREPARATION.json','results/SENSITIVITY_ATTEMPTS_COMPLETE.json',
        'results/E_STATISTICS.json','results/E_SENSITIVITY_SUMMARY.json','results/E_CONTROL_SUMMARY.json',
        'results/DEVELOPMENT_STATUS.json','DEVELOPMENT_REPORT.md','A1_A10_CLAIM_AUDIT.md','requirements.txt','reproduce.ps1',
        'anatomy.py','results/LAYER_PROXY_ASSOCIATIONS.json','tables/ANATOMY_LAYER_PROXY.csv'}
    assert required<=set(freeze['hashes']) and set(freeze['hashes'])==archive_paths()
    for rel,sha in freeze['hashes'].items():assert hashlib.sha256((P/rel).read_bytes()).hexdigest()==sha,rel


def verify_qc_summary(doc):
    assert doc['status']=='COMPLETED'
    qualified=[]
    for m in doc['physiology']:
        e=m['A_exposure_seconds'];n=m['A_spikes'];pairs=m['A_within_epoch_ISI_pairs'];r=m['A_refractory_pairs']
        assert abs(m['A_rate_Hz']-n/e)<1e-12
        frac=r/pairs if pairs else None;assert m['A_refractory_fraction']==frac
        assert sum(m['original_A_quartile_spikes'])==n and sum(m['original_A_quartile_exposures'])==e
        qr=[c/x if x else 0. for c,x in zip(m['original_A_quartile_spikes'],m['original_A_quartile_exposures'])]
        assert qr==m['original_A_quartile_rates']
        ok=(.5<=n/e<=100 and n>=100 and pairs>=99 and frac is not None and frac<=.005
            and min(m['original_A_quartile_exposures'])>=10 and min(qr)>=.1)
        assert m['primary_qualified']==ok
        if ok:qualified.append(m)
    ranked=sorted(qualified,key=lambda x:(x['A_refractory_fraction'],-x['A_rate_Hz'],x['uuid']))
    assert [x['cluster_id'] for x in ranked]==doc['ranking']
    assert doc['qualified_units']==len(ranked)
    assert doc['selected_unit_ids']==([x['cluster_id'] for x in ranked[:8]] if len(ranked)>=8 else [])
    assert doc['admitted']==(len(ranked)>=8)


def main():
    def denied(*a,**kw):raise RuntimeError('Saved-only reproduction denies network/neural array loading')
    socket.create_connection=denied
    socket.socket.connect=denied
    # Synthetic tests pass arrays directly, never load real/cached npy/npz neural data.
    np.load=denied
    freeze=json.loads((P/'ARCHIVE_FREEZE.json').read_text(encoding='utf8'))
    verify_archive(freeze)
    for line in (P/'requirements.txt').read_text(encoding='utf8').splitlines():
        name,version=line.split('==');assert importlib.metadata.version(name)==version,name
    m1=json.loads((R/'paper15_m1/PROTOCOL_FREEZE.json').read_text(encoding='utf8'))
    for rel,sha in m1['hashes'].items():
        assert hashlib.sha256((R/'paper15_m1'/rel).read_bytes()).hexdigest()==sha
    docs=list((P/'results').glob('*_A_QC.json'))
    gate=json.loads((P/'results/M2_PHYSIOLOGY_GATE.json').read_text(encoding='utf8'))
    expected={x['subject'] for x in gate['subjects'] if x['neural_access']}
    assert {p.name.removesuffix('_A_QC.json') for p in docs}==expected
    for path in docs:verify_qc_summary(json.loads(path.read_text(encoding='utf8')))
    suites=unittest.TestSuite()
    for name in ['source','reader','integrity','models','features','worker','selection','controls','sensitivities','statistics','evaluation','saved_audit','anatomy']:
        name='paper15_dev.test_'+name
        suites.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
    result=unittest.TextTestRunner(verbosity=1).run(suites)
    assert result.wasSuccessful()
    from .saved_audit import audit_all
    audit=audit_all()
    print(json.dumps(dict(saved_A_QC_journals_verified=len(docs),synthetic_tests=result.testsRun,
        frozen_files_verified=len(freeze['hashes']),M1_files_verified=len(m1['hashes']),
        network_denied=True,real_neural_arrays_loaded=0,real_fits=0,Final_access=False,
        saved_scientific_audit=audit,
        scope='Saved source/QC/numerical arithmetic, selection and E statistics/reference regeneration; synthetic regressions only; no fresh source or real QC/fits/predictions')))


if __name__=='__main__':main()
