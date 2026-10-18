"""Audit saved numerical/statistical evidence only; forbid source arrays/network."""
import argparse
import json
import socket
import unittest
import numpy as np
from .source import R,P,read,sha,frozen_definitions


def denied(*args,**kwargs):raise PermissionError('Saved-only reproduction denies source-array/network access')


def run():
    socket.socket.connect=denied;socket.create_connection=denied;np.load=denied
    frozen_definitions()
    archive=read(P/'ARCHIVE_FREEZE.json')
    for rel,h in archive['hashes'].items():assert sha(P/rel)==h,rel
    for rel,h in archive['external_hashes'].items():assert sha(R/rel)==h,rel
    # These tests use generated arrays and workspace-local scratch only.
    loader=unittest.TestLoader();suite=unittest.TestSuite()
    for name in ['test_models','test_features','test_controls','test_calibration','test_D_boundary_statistics','test_reader','test_metadata_boundary']:
        suite.addTests(loader.loadTestsFromName('paper15_final1.'+name))
    tests=unittest.TextTestRunner(verbosity=1).run(suite);assert tests.wasSuccessful()
    from .seal_C import verify_endpoint
    configs=read(P/'C_FIT_PLAN.json')['configurations'];plan=read(P/'C_FIT_PLAN.json');splan=read(P/'SENSITIVITY_FIT_PLAN.json')
    numerical=[];preserved_failures=0
    for path in sorted((P/'fits').rglob('*.json')):
        subject=path.parent.name;record=read(path);config=next(c for c in configs if c['id']==path.stem)
        assert subject in plan['subjects'] and record['configuration']==config
        if record['status']=='NUMERICAL_PASS':numerical.append(verify_endpoint(record,config,plan['state_hashes'][subject]))
        else:
            assert record['status'] in ('NUMERICAL_FAIL','STARTED');preserved_failures+=1
    indexed={(r['subject'],r['case'],r['family']):r for r in splan['attempts']}
    for path in sorted((P/'sensitivity_fits').rglob('*.json')):
        item=indexed[(path.parent.parent.name,path.parent.name,path.stem)]
        config=dict(id=item['family'],family=item['family'],ridge=item['ridge'],seed=11);record=read(path)
        assert record['configuration']==config
        if record['status']=='NUMERICAL_PASS':numerical.append(verify_endpoint(record,config,item['state_sha256']))
        else:
            assert record['status'] in ('NUMERICAL_FAIL','STARTED');preserved_failures+=1
    claim=read(P/'D_BATCH_CLAIM.json') if (P/'D_BATCH_CLAIM.json').exists() else None
    stats_checked=False
    if claim and claim['status']=='COMPLETE_REGISTERED_DESCRIPTIVE_D_BATCH':
        from .d_batch import complete_saved_statistics
        spec=read(P/'ONE_SHOT_D_SPECIFICATION.json');subjects=spec['primary_subjects']
        mouse=[read(P/'results/D_mice'/(s+'.json')) for s in subjects]
        cases=[read(P/'results/D_sensitivities'/s/(f'S{i:02}.json')) for s in subjects for i in range(1,12)]
        controls=[read(P/'results/D_controls'/(s+'.json')) for s in subjects]
        rebuilt=complete_saved_statistics(mouse,cases,controls,spec)
        for name,value in zip(['D_STATISTICS.json','D_SENSITIVITY_SUMMARY.json','D_CONTROL_SUMMARY.json','D_SCIENTIFIC_VERDICTS.json'],rebuilt):
            assert value==read(P/'results'/name),name
        stats_checked=True
    result=dict(saved_only=True,tests=tests.testsRun,frozen_files_verified=len(archive['hashes']),
        external_files_verified=len(archive['external_hashes']),numerical_endpoint_certificates=len(numerical),
        passing_endpoint_certificates=sum(numerical),saved_statistics_exact=stats_checked,
        preserved_failed_or_interrupted_certificates=preserved_failures,
        source_arrays_loaded=0,new_real_fits=0,new_real_likelihood_or_AD_FD_evaluations=0,D_reassessment=False,network_denied=True,
        final_scientific_delivery=read(P/'results/FINAL_DELIVERY.json'))
    # Keep routine terminal output compact; the complete delivery is already a saved artifact.
    print(json.dumps({k:v for k,v in result.items() if k!='final_scientific_delivery'},sort_keys=True))


if __name__=='__main__':run()
