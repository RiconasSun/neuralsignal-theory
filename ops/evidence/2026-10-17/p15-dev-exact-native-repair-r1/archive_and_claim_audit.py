"""Saved-output claim audit and complete artifact seal. No neural IO/prediction."""
import datetime
from pathlib import Path
from paper15_r1.source import P,R,load_json,dump
from paper15_r1.training import sha
from paper15_r1.saved_verify import archive_paths,verify_archive

E=Path(__file__).parent

def read(path):return load_json(path.read_text())

def run():
    claim=read(P/'E_BATCH_CLAIM.json')
    assert claim['status']=='COMPLETE_EXPLORATORY_E_BATCH' and claim['attempt']==claim['E_batches']==1
    status=read(P/'results/DEVELOPMENT_STATUS.json')
    assert status['NEW_MAIN_ATTEMPTS']==610 and status['NEW_SENSITIVITY_ATTEMPTS']==525
    assert status['TOTAL_CUMULATIVE_ATTEMPTS']==1494 and status['FINAL_C_ACCESS'] is status['FINAL_D_ACCESS'] is False
    stats=read(P/'results/E_STATISTICS.json')
    expected=['B4-B1','B4-B3','B4-B2','D-B4','C-B4','D-S']
    assert set(stats)==set(expected)
    control=read(P/'results/E_CONTROL_SUMMARY.json')
    sensitivities=read(P/'results/E_SENSITIVITY_SUMMARY.json')
    source_hashes={name:sha(P/'results'/name) for name in ['E_STATISTICS.json','E_CONTROL_SUMMARY.json','E_SENSITIVITY_SUMMARY.json']}
    rows=[]
    for key in expected:
        row=stats[key]
        assert row['n_mice']==10 and row['validated'] is False
        rows.append(dict(contrast=key,equal_mouse_mean=row['equal_mouse_mean'],CI95=row['CI95'],
            raw_p=row['paired_sign_flip_p'],Holm5_p=row.get('Holm5_adjusted_p'),
            source=f'results/E_STATISTICS.json#{key}',claim='EXPLORATORY_ONLY',validated=False))
    mice=[read(p) for p in sorted((P/'results/E_mice').glob('*.json'))]
    unit_bins=sum(r['models']['B4']['unit_bins'] for r in mice)
    assert len(mice)==10 and unit_bins==98320
    complete_suites=unavailable_suites=replicates=0
    for path in sorted((P/'results/E_control_journals').glob('*/*.jsonl')):
        events=[load_json(line) for line in path.read_text().splitlines()]
        completed=sum(event['event']=='REPLICATE_COMPLETE' for event in events)
        if events[-1]['event']=='SUITE_COMPLETE':
            assert completed==999;complete_suites+=1;replicates+=completed
        else:
            assert events[-1]['event']=='UNAVAILABLE_REGISTERED_COVERAGE' and completed==0
            unavailable_suites+=1
    assert (complete_suites,unavailable_suites,replicates)==(35,5,34965)
    primary=control['B4-B1']
    assert primary['N1']['mice_above_reference_median']==7 and primary['N1']['descriptive_disruption_gate'] is False
    assert primary['N2']['descriptive_disruption_gate'] is True
    assert all(control[key]['N4']['n_mice']==5 and control[key]['N4']['p_reference']==1 for key in expected)
    assert all(stats[key]['Holm5_adjusted_p']>.05 for key in expected[1:])
    dump(P/'results/CLAIM_TO_EVIDENCE_AUDIT.json',dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',source_hashes=source_hashes,contrasts=rows,
        independent_mice=10,labs=8,scored_nominal_curated_release_unit_bins=unit_bins,
        valid_reference_suites=complete_suites,unavailable_reference_suites=unavailable_suites,
        reference_replicate_bundles=replicates,reference_fits=0,
        primary_N1=dict(above_median=7,required=8,gate=False,Holm4_reference_p=primary['N1']['Holm4_reference_p']),
        primary_N2_gate=True,N4_aggregate_available=False,all_secondary_Holm5_nonsignificant=True,
        mandatory_sensitivity_coverage={key:sensitivities[key]['B4-B1']['n_mice'] for key in sensitivities if key not in ('S02','S03')},
        robust_positive_primary_claim=False,heldout_validation=False,persistent_state_claim=False,
        causal_mechanism=False,all_movement_independence=False,completed_paper=False,
        old_rounded_input_failure_preserved=True,Final_C_access=False,Final_D_access=False,
        scope='Saved-result claim and completeness audit; no actual predictions or raw-source revalidation'))
    paths=archive_paths()
    external={E/n for n in ['seal_sensitivity_gate.py','test_sensitivity_seal_guard.py','seal_E_gate.py',
        'test_E_seal_guard.py','seal_sensitivity_gate_ATTEMPT1.py','PRE_E_COVERAGE_LIMITATIONS.md',
        'OWNER_MISSION.txt','baseline.json','PRESERVATION_REGISTRATION.json']}
    external.update(p for p in E.iterdir() if p.is_file() and 'REVIEW' in p.name and p.suffix in ('.md','.json'))
    freeze=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',base='b0b692bd9b7e42f767117a51d0119644327a97f0',
        hashes={rel:sha(P/rel) for rel in sorted(paths)},
        external_hashes={p.relative_to(R).as_posix():sha(p) for p in sorted(external)},
        scope='Complete saved Development artifacts and load-bearing review/guard evidence; work/raw neural arrays excluded')
    target=P/'ARCHIVE_FREEZE.json';assert not target.exists()
    dump(target,freeze);verify_archive(freeze)
    print('Sealed',len(paths),'package files and',len(external),'external review/guard files;34965referencebundles;N1mixed,N4unavailable')

if __name__=='__main__':run()
