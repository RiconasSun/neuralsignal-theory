"""Saved evidence only. Blocks network; never opens real NWB/spike arrays."""
import csv,datetime,hashlib,json,subprocess,sys,unittest
from pathlib import Path
import numpy as np
from .core import *
P=Path(__file__).resolve().parents[1];R=P.parent;E=R/'ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0'
BASE='bf0e948f57dc49d7c315170c67b9911f72d92530'

def no_network(event,args):
    if event in ['socket.connect','socket.getaddrinfo']:raise RuntimeError('Saved-only reproduction denies network')

def run():
    sys.addaudithook(no_network);checks=[]
    from .evidence_checks import check_saved
    checks.extend(check_saved())
    receipt=read_json(E/'REGISTRATION_RECEIPT_2.json');assert receipt['registration_sha256']==sha256(P/'FEASIBILITY_REGISTRATION.json')
    assert receipt['neural_arrays_opened']==receipt['candidate_eligibility_counts_computed']==0
    assert (P/'code/FEASIBILITY_REGISTRATION.json').read_bytes()==(P/'FEASIBILITY_REGISTRATION.json').read_bytes()
    from .access_gate import REQUIRED
    review=read_json(E/'PILOT_ACCESS_REVIEW_RECEIPT.json')
    assert review['decision']=='ACCEPTED_BOUNDED_PILOT_ACCESS' and review['approved_spike_GET_or_decode'] is True
    assert type(review['open_P0']) is int and type(review['open_P1']) is int and review['open_P0']==review['open_P1']==0
    assert review['report_sha256']==sha256(E/'PILOT_ACCESS_REVIEW.md')
    assert REQUIRED<=review['reviewed_hashes'].keys()
    for name in REQUIRED: assert sha256(R/name)==review['reviewed_hashes'][name]
    checks.append('Saved prospective registration/report and all mandatory access-code/object identities;this reproduction does not grant source access or require ignored full web-page bodies')
    source={n:read_json(P/'metadata'/f'{n}.body')['msg'] for n in ['sessions','probes','channels','source_unit_qc']}
    population=metadata_populations(source['sessions'],source['probes'],source['channels'],source['source_unit_qc'])
    assert population==read_json(P/'results/POPULATION_INVENTORY.json')
    roster=list(csv.DictReader((R/'paper12_curated_v1/replay/mouse_evidence.csv').open(encoding='utf-8-sig')))
    roles=allocate_roles(population['selected'],[x['mouse_id'] for x in roster],[x['mouse_id'] for x in roster if x['group']=='final'])
    assert roles==read_json(P/'results/ROLE_ALLOCATION.json')
    assert not any(x['historical_source_overlap'] and x['group']=='Final_candidate' for x in roles)
    pilots=read_json(P/'results/PILOT_METADATA_SELECTION.json');assert len(pilots)<=2
    assert not any(x['mouse_id'] in {r['mouse_id'] for r in roster if r['group']=='final'} for x in pilots)
    checks.append('Exact all-source probe capacities and deterministic whole-mouse role/pilot boundaries')
    summary=read_json(P/'results/FINAL_M0_STATUS.json')
    for p in pilots:
        sid=p['session_id'];attempt=read_json(P/'results'/f'PILOT_ATTEMPT_{sid}.json')
        if attempt['status']!='COMPLETE':
            assert not summary['PROMPT_2_READY'];checks.append(f'Preserved failed pilot {sid}');continue
        result=read_json(P/'results'/f'PILOT_{sid}.json');assert result['no_fits'] and result['no_Final_access']
        assert all(c['nonfinite']==c['decreases']==0 and c['binary64_roundtrip_pass'] for c in result['unit_certificates'])
        assert result['selected_unit_ids']==p['qualified_unit_ids'][:8]
        event_path=P/'results'/f'NATIVE_EVENTS_{sid}.npz';assert sha256(event_path)==result['events_sha256']
        with np.load(event_path,allow_pickle=False) as events:
            for family in result['families']:
                name=family['family'];start=events[name+'_start'];stop=events[name+'_stop']
                assert start.dtype==stop.dtype==np.dtype('float64')
                assert hashlib.sha256(start.astype('<f8').tobytes()).hexdigest()==family['start_stop_sha256'][0]
                assert hashlib.sha256(stop.astype('<f8').tobytes()).hexdigest()==family['start_stop_sha256'][1]
                for values in [start,stop]:
                    restored=np.frombuffer(values.tobytes(),dtype=values.dtype)
                    assert np.array_equal(values.view('u8'),restored.view('u8'))
        examples=read_json(P/'results'/f'COUNT_EXAMPLES_{sid}.json')
        assert len(examples)==result['count_example_rows']
        for key in ['true_zero_bins','missing_bins']:assert sum(x[key] for x in examples)==result[key]
        checks.append(f'Saved pilot {sid}:finite/order certificates,native events,zeros/missing,count aggregates')
    ledger=read_json(P/'results/PAYLOAD_LEDGER.json');assert ledger['bytes']==sum(x['bytes'] for x in ledger['events'])<=6_000_000_000
    assert sum(p['declared_bytes'] for p in pilots)<=ledger['bytes']
    checks.append('Conservative durable payload ceiling;failures never refund reservation')
    # Local Git object metadata only;do not open old consumed scientific outcomes.
    current=subprocess.check_output(['git','ls-tree','-rz','--full-tree','HEAD'],cwd=R)
    old=(E/'PRECHANGE_GIT_TREE.bin').read_bytes()
    def entries(raw):return {part.split(b'\t',1)[1]:part.split(b'\t',1)[0] for part in raw.split(b'\0') if part}
    cm,om=entries(current),entries(old)
    for name,identity in om.items():
        if name!=b'ops/daily-operations.md':assert cm.get(name)==identity,name
    daily_base=subprocess.check_output(['git','show',BASE+':ops/daily-operations.md'],cwd=R)
    daily=(R/'ops/daily-operations.md').read_bytes();assert daily.endswith(daily_base)
    checks.append('All pre-mission tracked Git blob identities and exact original daily suffix preserved')
    suite=unittest.defaultTestLoader.loadTestsFromNames(['paper16_m0.code.test_core','paper16_m0.code.test_reader','paper16_m0.code.test_integration','paper16_m0.code.test_saved_integrity'])
    outcome=unittest.TextTestRunner(verbosity=1).run(suite);assert outcome.wasSuccessful()
    checks.append(f'{outcome.testsRun} synthetic numerical/time/role/entrypoint/NWB integration regressions')
    result={'mission':MISSION,'status':'PASS','time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'synthetic_tests':outcome.testsRun,'scientific_verdict':summary['SCIENTIFIC_FEASIBILITY_VERDICT'],'real_NWB_opened':0,'real_spike_arrays_opened':0,'Final_outcomes_accessed':0,'model_fits':0,'network_access':0,'saved_manifest_sha256':sha256(P/'SAVED_EVIDENCE_MANIFEST.json')}
    dump_json(P/'work/SAVED_REPRODUCTION_LATEST.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':run()
