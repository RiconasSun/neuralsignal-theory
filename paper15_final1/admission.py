"""Complete pre-D scientific/numerical admission; no neural source opens."""
import os
from .source import P,R,read,sha,frozen_definitions
from .reader import verify_external_dependencies


def verify_pre_D_gate():
    gate=read(P/'PRE_D_GATE.json')
    required={'d_batch.py','d_support.py','admission.py','reference_evaluation.py','final_statistics.py',
              'report.py','saved_verify.py','models.py','features.py','independent_ad.py','controls.py','statistics.py',
              'sensitivities.py','calibration.py','sensitivity_calibration.py','source.py','reader.py',
              'C_PRODUCTION_GATE.json','C_FIT_PLAN.json','SENSITIVITY_FIT_PLAN.json',
              'results/C_MAIN_ATTEMPTS_COMPLETE.json','results/C_SENSITIVITY_ATTEMPTS_COMPLETE.json',
              'results/FINAL_C_QC_GATE.json','FINAL_C_STATE_SEAL.json','REFERENCE_METADATA_FREEZE.json',
              'ONE_SHOT_D_SPECIFICATION.json','results/FULL_D_SYNTHETIC_REHEARSAL.json'}
    required|={p.name for p in P.glob('*.py')}
    if gate.get('approved_one_D_batch') is not True or not required<=set(gate.get('hashes',{})):
        raise PermissionError('Complete reviewed pre-D freeze required')
    for rel,h in gate['hashes'].items():
        if sha(P/rel)!=h:raise PermissionError('Pre-D input mismatch: '+rel)
    if gate['D_batches']!=1:raise PermissionError('Exactly one batch required')
    if set(gate['independent_reviews'])!={'scientific','numerical'}:raise PermissionError('Both independent pre-D reviews required')
    for item in gate['independent_reviews'].values():
        path=R/item['path'];receipt=read(path)
        if (sha(path)!=item['sha256'] or receipt['decision']!='ACCEPTED_FROZEN_ONE_SHOT_D'
            or receipt['approved_one_D_batch'] is not True or type(receipt['open_P0']) is not int or receipt['open_P0']!=0
            or type(receipt['open_P1']) is not int or receipt['open_P1']!=0 or receipt['hashes']!=gate['hashes']):
            raise PermissionError('Pre-D review rejected/stale/incomplete')
        if sha(R/receipt['report_path'])!=receipt['report_sha256']:raise PermissionError('Pre-D review report changed')
    frozen_definitions();verify_external_dependencies(read(P/'METADATA_SOURCE_EXTERNAL_FREEZE.json')['hashes'])
    seal=read(P/'FINAL_C_STATE_SEAL.json')
    assert gate['subjects']==seal['primary_subjects'] and len(gate['subjects'])>=6
    for item in seal['artifacts']:
        assert item['path'] in gate['hashes'] and sha(P/item['path'])==item['sha256']
    return gate
