"""Saved numerical identity/bundle audit plus synthetic tests; no E/D access."""
import json
import socket
import unittest
from unittest.mock import patch
from .source import P,ROOT,sha
from . import baseline_A as b
from . import development_bundle as d


def main():
    frozen=b.read(P/'M5_E_IMPLEMENTATION_FREEZE.json')
    for manifest in [frozen,b.read(ROOT/'paper13_ki_pl_contract1/FREEZE_r2.json')]:
        for name,digest in manifest['hashes'].items():
            if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Frozen identity mismatch: '+name)
    names=['test_preaccess','test_models','test_fit_engine','test_qc_journal','test_baseline_A',
        'test_development_B','test_families','test_animal_stats','test_predictive','test_development_bundle','test_exploratory_E']
    with patch.object(socket.socket,'connect',side_effect=AssertionError('No network in saved/synthetic reproduction')):
        tests=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(['paper13_ki_execution1.'+n for n in names]))
        if not tests.wasSuccessful():raise RuntimeError('E synthetic regression failed')
        m2,qcs,baselines,m3,families,m4=d.gates()
        bundles={mouse:d.build(mouse,qcs[mouse],baselines,m3,families,m4) for mouse in sorted(m2['eligible_development'])}
    records=list(families.values());certs=[r['derivatives'][k] for r in records for k in ['initial','intermediate_first_callback','endpoint']]
    print(json.dumps({'tests':tests.testsRun,'frozen_hashes':len(frozen['hashes']),'M3_A_PASS':len(baselines),
        'M4_A_PASS':len(records),'M4_certificates':len(certs),'max_PG':max(r['PG'] for r in records),
        'max_AD_relative':max(c['AD_error']['max_relative'] for c in certs),
        'max_fixed_FD_relative':max(c['fixed_FD_error']['max_relative'] for c in certs),
        'complete_model_bundles':len(bundles),'bundle_hashes':{mouse:sha(b.canonical(v)) for mouse,v in bundles.items()},
        'E_D_values_read':False,'new_real_fits':0,'scientific_outcome':'No new scientific evaluation; saved M4 artifacts and synthetic E path only'}))


if __name__=='__main__':main()
