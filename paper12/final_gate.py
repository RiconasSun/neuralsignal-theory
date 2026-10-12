"""Evidence-bounded stopped admission gate; independent from engineering tests."""
import json
from pathlib import Path
from audit import HERE
from register import sha, verify

def main():
    verify()
    primary = json.loads((HERE/'results/allen_gate_result.json').read_text())
    original_ibl = json.loads((HERE/'results/ibl_gate_result.json').read_text())
    ibl = json.loads((HERE/'results/ibl_coverage_code1.json').read_text())
    registration = json.loads((HERE/'ibl_registration.json').read_text())
    if sha(HERE/'results/allen_gate_result.json') != registration['primary_failed_gate_sha256']:
        raise RuntimeError('Original primary admission gate changed')
    if sha(HERE/'IBL_POLICY.json') != registration['policy_sha256']:
        raise RuntimeError('Alternative policy changed')
    links = [json.loads(p.read_text()) for p in (HERE/'metadata/link_audit').glob('*.json')]
    if len(links) != 58 or not all(r['pass'] for r in links): raise RuntimeError('Unresolved metadata access defect')
    if primary['pass'] or original_ibl['pass']: raise RuntimeError('Do not amend scientific gates')
    warnings = [
        {'id':'W01','condition':'Native probe-specific origin/end/gaps and clock support unresolved'},
        {'id':'W02','condition':'Independent subfield localization and anatomical uncertainty not verified'},
        {'id':'W03','condition':'Matched repeat identities and trial support not frozen or admitted'},
        {'id':'W04','condition':'Per-session causal behavior availability and missingness unverified'},
        {'id':'W05','condition':'Full physiological release/checksum and cross-release processing provenance not verified'}]
    gate = {'mission':'P12-HIPPOCAMPAL-SUBFIELD-DYNAMICS','phase':'M0',
            'verdict':'INCONCLUSIVE','pass':False,'mission_status':'WAIT_FOR_HUMAN_INPUT',
            'bug_count':0,'warn_count':len(warnings),'warnings':warnings,
            'allen_potential_paired_mice':primary['potential_paired_mice'],
            'ibl_potential_paired_mice':ibl['potential_paired_mice'],
            'admitted_mice':0,'next_phase_executed':False,
            'scientific_validation_pass':False,'manuscript_complete':False,
            'original_gate_sha256':{'allen':sha(HERE/'results/allen_gate_result.json'),
                                     'ibl':sha(HERE/'results/ibl_gate_result.json')},
            'stop_reason':'Both allowed admissions remain unpassed; no automatic rescue or further candidate search authorized.',
            'next_required_action':'Separate explicit decision to commission a prospectively registered native-clock/anatomy/support audit using existing public sources or provide authoritative witnesses; otherwise retain stopped M0. This is not routine approval to enter M1.'}
    (HERE/'results/gate_result.json').write_text(json.dumps(gate,indent=2,sort_keys=True))
    print(json.dumps(gate,indent=2))

if __name__=='__main__': main()
