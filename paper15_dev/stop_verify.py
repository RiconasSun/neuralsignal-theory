"""Saved-only audit of the stopped mission, without certifying scientific PASS."""
import collections
import hashlib
import importlib.metadata
import json
import socket
import unittest
from pathlib import PurePosixPath
import numpy as np
from .source import P,R
from .saved_audit import numerical_record
from .saved_verify import verify_qc_summary
from .training import configurations,sha

E=R/'ops/evidence/2026-10-17/p15-m2-m5-native-qc-development'
POST_FREEZE_EVIDENCE={'STOP_SAVED_REPRODUCTION.json','STOP_SAVED_REPRODUCTION.log',
    'INDEPENDENT_STOP_ARCHIVE_REVIEW_2.md','INDEPENDENT_STOP_ARCHIVE_SYNTHETIC_2.json',
    'review.md','verdict.md','CLOSURE_MANIFEST.json','closure_receipt.json'}

def read(path):return json.loads(path.read_text(encoding='utf8'))

def inventory_check(sealed_keys,actual_keys,expected_keys):
    assert len(set(sealed_keys))==len(sealed_keys) and set(sealed_keys)==set(actual_keys)
    assert set(actual_keys)<=set(expected_keys)
    return len(set(expected_keys)-set(actual_keys))

def safe_relative(rel):
    value=PurePosixPath(rel)
    assert isinstance(rel,str) and rel and '\\' not in rel and not value.is_absolute()
    assert '..' not in value.parts and ':' not in rel and value.as_posix()==rel
    return rel

def paths():
    return {p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file()
        and not any(x in ('work','__pycache__') for x in p.relative_to(P).parts)
        and p.relative_to(P).as_posix()!='STOP_ARCHIVE_FREEZE.json'}

def audit():
    freeze=read(P/'STOP_ARCHIVE_FREEZE.json')
    mandatory={'STOP_REPORT.md','STOP_CLAIM_AUDIT.md','README.md','stop_verify.py','test_time_serialization.py','reproduce_stop.ps1',
        'metadata_qc.py','features.py','models.py','training.py','independent_ad.py','A_FIT_PLAN.json','PRODUCTION_GATE.json',
        'SOURCE_FILE_FREEZE.json','NEURAL_HEADER_FREEZE.json','results/DEVELOPMENT_STATUS.json','results/M2_PHYSIOLOGY_GATE.json',
        'results/BASELINE_ATTEMPTS_COMPLETE.json','requirements.txt'}
    mandatory_evidence={'baseline.json','BASELINE_CLOSURE.json','HISTORICAL_HASHES.json','INTERRUPTION_SEAL.json',
        'TIME_SERIALIZATION_AUDIT_1.json','TIME_PRECISION_REVIEW_1.md','TIME_PRECISION_REVIEW_2.md','TIME_INDEX_AUDIT_1.json',
        'INDEPENDENT_INTERRUPTION_REVIEW_1.md','M5_COMPONENT_SYNTHETIC_RECEIPT_2.json','M5_FULL_SYNTHETIC_CONTROL_INTEGRATION.json',
        'FULL_SYNTHETIC_CONTROL_REVIEW.md','DAILY_PREPEND_RECEIPT.json'}
    assert mandatory<=set(freeze['package_hashes']) and mandatory_evidence<=set(freeze['evidence_hashes'])
    assert freeze['postfreeze_evidence_exclusions']==sorted(POST_FREEZE_EVIDENCE)
    actual_evidence={p.relative_to(E).as_posix() for p in E.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    assert actual_evidence-POST_FREEZE_EVIDENCE==set(freeze['evidence_hashes'])
    assert paths()==set(freeze['package_hashes'])
    for rel,h in freeze['package_hashes'].items():assert sha(P/safe_relative(rel))==h,rel
    for rel,h in freeze['evidence_hashes'].items():assert sha(E/safe_relative(rel))==h,rel
    old=read(E/'HISTORICAL_HASHES.json')
    for rel,h in old.items():assert sha(R/rel)==h,rel
    m1=read(R/'paper15_m1/PROTOCOL_FREEZE.json')
    for rel,h in m1['hashes'].items():assert sha(R/'paper15_m1'/rel)==h,rel
    sealed=read(E/'INTERRUPTION_SEAL.json');plan=read(P/'A_FIT_PLAN.json')
    assert plan['configurations']==configurations() and len(plan['subjects'])==len(set(plan['subjects']))==10
    assert plan['total_main']==610 and plan['max_retries']==0
    expected={(s,c['id']):c for s in plan['subjects'] for c in plan['configurations']}
    files=list((P/'fits').glob('*/*.json'))
    assert len(files)==len(sealed['attempt_rows'])==359
    actual_keys={(p.parent.name,p.stem) for p in files}
    sealed_keys=[(r['subject'],r['configuration']) for r in sealed['attempt_rows']]
    assert inventory_check(sealed_keys,actual_keys,expected)==sealed['unattempted']==251
    counts=collections.Counter();per_mouse=collections.defaultdict(collections.Counter)
    for row in sealed['attempt_rows']:
        key=(row['subject'],row['configuration']);assert key in expected
        path=P/'fits'/key[0]/(key[1]+'.json');assert sha(path)==row['sha256']
        fit=read(path);assert fit['configuration']==expected[key] and fit['subject']==key[0] and fit['attempt']==1
        assert fit['production_gate_sha256']==sha(P/'PRODUCTION_GATE.json')
        assert fit['A_preprocessing_sha256']==sha(P/'states'/(key[0]+'_A_PREPROCESSING.json'))
        if fit['status']=='STARTED':assert 'coefficients' not in fit and fit['optimizer_history']==[]
        else:numerical_record(fit)
        counts[fit['status']]+=1;per_mouse[key[0]][fit['status']]+=1
    assert dict(counts)=={'NUMERICAL_PASS':358,'STARTED':1}
    assert (sealed['completed'],sealed['interrupted'],sealed['unattempted'])==(358,1,251)
    base=read(P/'results/BASELINE_ATTEMPTS_COMPLETE.json')
    assert base['attempted']==base['completed']==base['numerical_pass']==130
    assert set(base['attempt_hashes'])=={s+'/'+cid for (s,cid),c in expected.items() if c['family'].startswith('B')}
    for key,h in base['attempt_hashes'].items():assert sha(P/'fits'/(key+'.json'))==h
    for rel,record in sealed['preserved_artifacts'].items():
        if record['git_archive']:assert sha(P/rel)==record['sha256'],rel
    status=read(P/'results/DEVELOPMENT_STATUS.json')
    assert not any(status[k] for k in ('M2_SOURCE_QC_PASS','PRODUCTION_NUMERICAL_PASS','M3_BASELINE_PASS','M4_DYNAMIC_PASS','M5_DEVELOPMENT_COMPLETE','FINAL_C_ACCESS','FINAL_D_ACCESS','PROMPT_4_READY'))
    assert status['BUG_COUNT']==1 and status['WARN_COUNT']==1
    for name in ('SELECTION_FREEZE.json','E_BATCH_CLAIM.json','E_EXPLORATORY_GATE.json','SENSITIVITY_FIT_PLAN.json'):
        assert not (P/name).exists(),name
    assert not (P/'results/DYNAMIC_ATTEMPTS_COMPLETE.json').exists()
    assert not list((P/'work').glob('B_exports/*')) and not list((P/'work').glob('E_exports/*'))
    qc_files=list((P/'results').glob('*_A_QC.json'))
    old_gate=read(P/'results/M2_PHYSIOLOGY_GATE.json')
    assert {p.name.removesuffix('_A_QC.json') for p in qc_files}=={r['subject'] for r in old_gate['subjects'] if r['neural_access']}
    for path in qc_files:
        qc=read(path);assert qc['subject']==path.name.removesuffix('_A_QC.json')
        verify_qc_summary(qc)
    precision=read(E/'TIME_SERIALIZATION_AUDIT_1.json')
    assert len(precision['rows'])==10 and not precision['B_E_neural_access'] and not precision['Final_access']
    assert all(x['A_target_count_cells_changed']==x['A_history_cells_changed']==0 for x in precision['rows'])
    # Nonzero source membership is established by exact index witnesses, not a new scientific tolerance.
    indices=read(E/'TIME_INDEX_AUDIT_1.json')
    assert indices['changed_mice']==5 and indices['total_changed_indices']>0
    daily=(R/'ops/daily-operations.md').read_bytes();prior=read(E/'DAILY_PREPEND_RECEIPT.json')
    assert len(daily)>=prior['original_bytes'] and hashlib.sha256(daily[-prior['original_bytes']:]).hexdigest()==prior['original_sha256']
    return dict(attempted=359,completed=358,numerical_pass_on_rounded_inputs=358,interrupted=1,unattempted=251,
        per_mouse=dict(per_mouse),historical_files_verified=len(old),package_files_verified=len(freeze['package_hashes']),
        source_gate_pass=False,scientific_completion=False,real_fits=0,real_neural_arrays_loaded=0,Final_access=False)

def main():
    def deny(*a,**kw):raise RuntimeError('STOP saved-only audit denies network/neural arrays')
    socket.create_connection=deny;socket.socket.connect=deny;np.load=deny
    for line in (P/'requirements.txt').read_text().splitlines():
        name,version=line.split('==');assert importlib.metadata.version(name)==version
    result=audit()
    names=['source','reader','integrity','models','features','worker','selection','controls','sensitivities','statistics','evaluation','saved_audit','anatomy','time_serialization','stop_verify']
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName('paper15_dev.test_'+n) for n in names)
    tests=unittest.TextTestRunner(verbosity=1).run(suite);assert tests.wasSuccessful()
    print(json.dumps(dict(result,synthetic_tests=tests.testsRun,network_denied=True,
        scope='Stopped-evidence integrity and saved arithmetic only; current source defect remains unresolved')))

if __name__=='__main__':main()
