"""Verify terminated fixed-case saved endpoints; never read neural arrays/refit."""
import datetime
from .source import P,load_json,dump
from .training import sha
from .saved_audit import numerical_record
from .ledger import snapshot

def read(path):
    return load_json(path.read_text())

def run():
    plan=read(P/'SENSITIVITY_FIT_PLAN.json')
    complete=read(P/'results/SENSITIVITY_ATTEMPTS_COMPLETE.json')
    assert complete['attempted']==complete['completed']==plan['expected_attempts']<=550
    assert len(complete['records'])==len(plan['attempts'])
    records=[]
    for item,marker in zip(plan['attempts'],complete['records']):
        assert marker['item']==item
        path=P/'sensitivity_fits'/item['subject']/item['case']/(item['family']+'.json')
        assert sha(path)==marker['sha256']
        record=read(path)
        assert record['plan_item']==item and record['attempt']==1 and record['status']==marker['status']
        assert record['sensitivity_gate_sha256']==sha(P/'SENSITIVITY_GATE.json')
        state_path=P/'sensitivity_states'/item['subject']/(item['case']+'.json')
        assert sha(state_path)==item['state_sha256']
        state=read(state_path)
        numerical_record(record,sensitivity=True,state=state)
        if 'coefficients' in record:
            epochs=state['trial_counts']['A']
            assert record['actual_population_bins']==epochs*int(round(.5/state['delta']))
            assert record['actual_unit_bins']==record['actual_population_bins']*len(state['units'])
        records.append(record)
    passed=[r for r in records if r['status']=='NUMERICAL_PASS']
    assert complete['numerical_pass']==len(passed)
    ledger=snapshot()
    assert ledger['NEW_SENSITIVITY_ATTEMPTS']==plan['expected_attempts'] and not ledger['new_interrupted_or_active']
    target=P/'results/SENSITIVITY_SAVED_VERIFICATION.json'
    assert not target.exists()
    dump(target,dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        attempted=len(records),completed=len(records),numerical_pass=len(passed),
        failures=[dict(plan_item=r['plan_item'],error=r.get('error',r.get('termination'))) for r in records if r['status']!='NUMERICAL_PASS'],
        max_PG_passed=max((r['PG'] for r in passed),default=None),
        max_AD_scaled_passed=max((r['independent']['AD_max_scaled'] for r in passed),default=None),
        max_FD_scaled_passed=max((f['max_scaled'] for r in passed for f in r['independent']['FD']),default=None),
        ledger=ledger,real_fits=0,neural_arrays_loaded=0,E_neural_access=False,Final_access=False,
        scope='Saved endpoint/coordinate/hash/plan/exposure arithmetic, not a new real-data derivative evaluation'))
    print('Verified saved sensitivity endpoints:',len(records),'passed:',len(passed))

if __name__=='__main__':
    run()
