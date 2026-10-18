"""Audit saved numerical/statistical evidence only; forbid source arrays/network."""
import argparse
import json
import socket
import unittest
import importlib.metadata
import numpy as np
from .source import R,P,read,sha,frozen_definitions
from .saved_audit import verify_archive,audit_fits,audit_D


def denied(*args,**kwargs):raise PermissionError('Saved-only reproduction denies source-array/network access')


def run():
    socket.socket.connect=denied;socket.create_connection=denied;np.load=denied
    frozen_definitions()
    archive=read(P/'ARCHIVE_FREEZE.json')
    verify_archive(archive)
    for line in (P/'requirements.txt').read_text(encoding='utf8').splitlines():
        name,version=line.split('==');assert importlib.metadata.version(name)==version,name
    # These tests use generated arrays and workspace-local scratch only.
    loader=unittest.TestLoader();suite=unittest.TestSuite()
    for name in ['test_models','test_features','test_controls','test_calibration','test_D_boundary_statistics','test_saved_audit','test_reader','test_metadata_boundary']:
        suite.addTests(loader.loadTestsFromName('paper15_final1.'+name))
    tests=unittest.TextTestRunner(verbosity=1).run(suite);assert tests.wasSuccessful()
    fits=audit_fits()
    claim=read(P/'D_BATCH_CLAIM.json') if (P/'D_BATCH_CLAIM.json').exists() else None
    stats_checked=False
    if claim and claim['status']=='COMPLETE_REGISTERED_DESCRIPTIVE_D_BATCH':
        audit_D()
        stats_checked=True
    result=dict(saved_only=True,tests=tests.testsRun,frozen_files_verified=len(archive['hashes']),
        external_files_verified=len(archive['external_hashes']),**fits,saved_statistics_exact=stats_checked,
        source_arrays_loaded=0,new_real_fits=0,new_real_likelihood_or_AD_FD_evaluations=0,D_reassessment=False,network_denied=True,
        final_scientific_delivery=read(P/'results/FINAL_DELIVERY.json'))
    # Keep routine terminal output compact; the complete delivery is already a saved artifact.
    print(json.dumps({k:v for k,v in result.items() if k!='final_scientific_delivery'},sort_keys=True))


if __name__=='__main__':run()
