"""Checkpoint reproduction of saved evidence and synthetic code; no new science."""
import json
import socket
import unittest
from unittest.mock import patch
import numpy as np
from .source import P,ROOT,ALLOCATION,sha
from . import baseline_A as b
from . import development_bundle as d
from . import restore_saved_states as restore
from .predictive import evaluate
from .animal_stats import summarize
from . import sensitivity_plan as sens

E=ROOT/'ops/evidence/2026-10-16/p13-ki-pl-science-first-execution'


def main():
    freeze=b.read(P/'SAVED_PROGRESS_FREEZE.json');original=b.read(ROOT/'paper13_ki_pl_contract1/FREEZE_r2.json')
    for manifest in [freeze,original]:
        for name,digest in manifest['hashes'].items():
            if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Frozen identity mismatch: '+name)
    with patch.object(socket.socket,'connect',side_effect=AssertionError('Saved-only reproduction denies source/network')):
        restored=restore.restore(ROOT,b.read(E/'SAVED_DERIVED_STATES_MANIFEST.json'))
        names=['test_preaccess','test_models','test_fit_engine','test_qc_journal','test_baseline_A','test_development_B',
            'test_families','test_animal_stats','test_predictive','test_development_bundle','test_exploratory_E',
            'test_control_core','test_sensitivity_plan','test_restore_saved']
        tests=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(['paper13_ki_execution1.'+n for n in names]))
        if not tests.wasSuccessful():raise RuntimeError('Saved progress regression failed')
        m2,qcs,baselines,m3,families,m4=d.gates();saved=b.read(P/'results/M5_EXPLORATORY_RESULTS.json');scores={}
        numerical_tolerance=2e-12
        for record in ALLOCATION:
            mouse=record['mouse_id']
            if mouse not in m2['eligible_development']:continue
            bundle=d.build(mouse,qcs[mouse],baselines,m3,families,m4)
            original_bundle=b.read(P/'results/development_models'/(mouse+'.json'))
            if b.canonical(bundle)!=b.canonical(original_bundle):raise ValueError('Saved development model bundle differs')
            exported=b.read(P/'results/exploratory_E'/(mouse+'.json'))
            with np.load(ROOT/exported['state_file'],allow_pickle=False) as state:y=state['counts'].copy()
            epochs=[a for a in record['epochs'] if a['partition']=='E']
            q=d.f.nuisance(record,epochs);replayed=evaluate(y,q,bundle)
            for name,value in replayed['scores'].items():
                if abs(value-saved['per_mouse'][mouse]['scores'][name])>numerical_tolerance:raise ValueError('Saved E score reproduction mismatch')
            scores[mouse]={name:replayed['scores'][name] for name in ['B4','D','C','Bstar','S']}
        stats,arrays=summarize(scores,saved['mouse_order'])
        if b.canonical(stats)!=b.canonical(saved['registered_statistics']):raise ValueError('Saved animal statistics mismatch')
        with np.load(P/'results/exploratory_E/mouse_bootstrap.npz',allow_pickle=False) as old:
            for name,array in arrays.items():np.testing.assert_array_equal(array,old[name])
        metadata=b.read(P/'results/M6_SENSITIVITY_METADATA_AUDIT.json')
        for row in metadata['rows']:
            record=next(a for a in ALLOCATION if a['mouse_id']==row['mouse_id']);plan=sens.metadata(record)
            ordinals=[a['ordinal'] for a in record['epochs'] if a['partition']==row['report_partition'] and plan['recent_event'][str(a['ordinal'])]]
            if ordinals!=row['recent_retained_parent_ordinals']:raise ValueError('Recent-event metadata saved reproduction mismatch')
    print(json.dumps({'synthetic_tests':tests.testsRun,'current_hashes':len(freeze['hashes']),'original_hashes':len(original['hashes']),
        'saved_baseline_fits_verified':len(baselines),'saved_dynamic_fits_verified':len(families),'saved_E_mice_reproduced':len(scores),
        'restoration':restored,'mandatory_recent_event_final_contributors':metadata['final_contributors']['recent_event'],
        'required_final_contributors':8,'new_real_fits':0,'new_source_reads':0,'new_real_control_replicates':0,
        'final_D_outcomes_read_or_evaluated':False,'scope':'Saved progress plus synthetic engineering only, not final scientific validation'}))


if __name__=='__main__':main()
