"""Close an externally triggered critical STOP without fitting or data acquisition."""
import argparse
import json
from datetime import datetime, timezone

import run_r2 as run

OUT = run.base.STUDY/'results/R2_stop'
SUPPORT = run.base.STUDY/'results/R2_external_support_code2'


def register():
    run.verify()
    support = run.load(SUPPORT/'gate_result.json')
    if support['gate_verdict']!='FAIL' or support['scientific_verdict']!='DATA_INSUFFICIENT':
        raise RuntimeError('No actual failed external observation-support gate')
    if (OUT/'registration.json').exists():
        verify(); return
    run.base.save(OUT/'registration.json',{
        'registered_utc':datetime.now(timezone.utc).isoformat(),
        'source_sha256':{run.relative(__file_path()):run.base.digest(__file__)},
        'support_artifact_lock_sha256':run.base.digest(SUPPORT/'artifact_lock.json'),
        'support_gate_sha256':run.base.digest(SUPPORT/'gate_result.json'),
        'R2_registration_sha256':run.base.digest(run.OUT/'registration.json'),
        'scope':'Saved evidence closure only; no new fits, acquisition, model selection or inference',
        'stop_receipt':'Own exec session17582 received CTRL_C after support FAIL; tool returned exit1. No scientific evaluation resumed.',
        'no_threshold_or_roster_or_split_change':True},immutable=True)


def __file_path():
    from pathlib import Path
    return Path(__file__).resolve()


def verify():
    run.verify()
    reg = run.load(OUT/'registration.json')
    for rel,sha in reg['source_sha256'].items():
        if run.base.digest(run.base.ROOT/rel)!=sha:
            raise RuntimeError('STOP finalizer changed')
    if run.base.digest(SUPPORT/'artifact_lock.json')!=reg['support_artifact_lock_sha256']:
        raise RuntimeError('Support lock changed')
    for rel,sha in run.load(SUPPORT/'artifact_lock.json')['sha256'].items():
        if run.base.digest(run.base.ROOT/rel)!=sha:
            raise RuntimeError('Support failure evidence changed: '+rel)


def finalize():
    verify()
    if (run.OUT/'gate_result.json').exists():
        for rel,sha in run.load(run.OUT/'artifact_lock.json')['sha256'].items():
            if run.base.digest(run.base.ROOT/rel)!=sha:
                raise RuntimeError('Closed R2 evidence changed: '+rel)
        print('Critical STOP already closed; unchanged.'); return
    fits = [run.load(p) for p in (run.OUT/'fits').rglob('*.json')]
    actual = {(r['session'],run.configuration_id(r['config']),r['seed']) for r in fits}
    expected = {(key,run.configuration_id(c),seed) for key in run.roster()
                for c in run.baseline_configs()+run.family_configs()
                for seed in ([None] if c['family']=='stationary' else run.SEEDS)}
    a_complete = len(fits)==len(actual)==len(expected) and actual==expected and all(r['converged'] for r in fits)
    null_rows,incomplete = [],[]
    for path in sorted((run.OUT/'nulls').rglob('*_seed*.json')):
        try:
            row = run.load(path)
            null_rows.append({'path':run.relative(path),**row})
        except (json.JSONDecodeError,UnicodeDecodeError):
            incomplete.append({'path':run.relative(path),'sha256':run.base.digest(path),
                               'state':'INTERRUPTED_INCOMPLETE_OUTPUT','not_reclassified_as_nonconvergence':True})
    completed_nulls = [run.relative(p.parent) for p in (run.OUT/'nulls').rglob('subject_results.json')]
    support = run.load(SUPPORT/'gate_result.json')
    ledger = {'completed_primary_fits':len(fits),'primary_converged':sum(r['converged'] for r in fits),
              'completed_null_fit_records':len(null_rows),'null_converged':sum(r['converged'] for r in null_rows),
              'null_failed_records':sum(not r['converged'] for r in null_rows),
              'complete_null_cohort_replicates':completed_nulls,
              'incomplete_files_preserved':incomplete,
              'interrupted_in_flight_candidate':'No result fabricated; work may have been interrupted between saved records.',
              'no_null_completion_claim':True,'no_null_p_values_from_partial_replicates':True}
    run.base.save(OUT/'stop_ledger.json',ledger,immutable=True)
    gate = {'study':'P11-v2','milestone':'R2','gate_verdict':'FAIL','scientific_verdict':'DATA_INSUFFICIENT',
            'regime_verdict':'INCONCLUSIVE','R2_A':'PASS' if a_complete else 'INCOMPLETE',
            'R2_B':'INCOMPLETE_STOPPED','R2_C':'FAIL_OBSERVATION_SUPPORT','R3':'NOT_EXECUTED',
            'failures':['Mandatory external observation support unresolved for5of52frozen candidate sessions; stop without pruning or relaxed boundary criterion.'],
            'source_gate_path':run.relative(SUPPORT/'gate_result.json'),
            'source_gate_sha256':run.base.digest(SUPPORT/'gate_result.json'),
            'scope_of_failure':'Current registered metadata-boundary audit cannot certify complete external support; not evidence that neural recordings or hippocampal regimes are absent.',
            'support_sessions':47,'unsupported_or_unknown_sessions':5,
            'external_training_unit_QC_executed':False,'eligible_external_subjects_physiologically_verified':None,
            'attempted_development_fits':len(fits),'converged_development_fits':sum(r['converged'] for r in fits),
            'mandatory_development_fits':23*169,'unexecuted_development_fits':23*169-len(fits),
            'completed_null_fit_records':len(null_rows),'completed_null_cohort_replicates':len(completed_nulls),
            'registered_null_replicates_per_type':200,'registered_null_types':3,
            'tests_exit_code':0,'initial_R2_tests':34,
            'numerical_oracle':run.load(run.OUT/'numerical_oracle.json'),
            'independent_subjects':9,'sessions':23,'statistics_scope':'Previously exposed exploratory development only; exact512subject sign flips and10000paired subject bootstraps, Holm6.',
            'oldtest_accessed':False,'external_spikes_accessed':False,'final_holdout_locked':True,
            'external_60_40_split_sha256':run.base.digest(run.base.STUDY/'results/R0_schema1/final_validation_lock.json'),
            'source_hashes_unchanged':True,'fit_seconds':sum(r.get('elapsed_seconds',0.) for r in fits),
            'stop_mechanism':'CTRL_C own execution after independent metadata gate FAIL, exit1. No numerical failure invented.',
            'scientific_success_not_claimed':True}
    run.base.save(run.OUT/'QC.json',gate,immutable=True)
    run.base.save(run.OUT/'gate_result.json',gate,immutable=True)
    run.artifact_lock()
    run.base.save(OUT/'artifact_lock.json',{'sha256':{run.relative(p):run.base.digest(p) for p in OUT.iterdir() if p.is_file()}},immutable=True)
    print(json.dumps(gate,indent=2)); print(json.dumps(ledger,indent=2))


if __name__=='__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action',choices=['register','finalize'])
    action = parser.parse_args().action
    register() if action=='register' else finalize()
