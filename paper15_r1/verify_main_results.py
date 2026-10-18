"""Saved endpoint verification after every fresh main start has terminated."""
import datetime
from .source import P,dump
from .saved_audit import audit_fits
from .ledger import snapshot

def run():
    ledger=snapshot();assert ledger['NEW_MAIN_ATTEMPTS']==ledger['main_cap']==610 and not ledger['new_interrupted_or_active']
    rows=audit_fits();assert len(rows)==610
    passed=[r for r in rows if r['status']=='NUMERICAL_PASS']
    failed=[dict(subject=r['subject'],configuration=r['configuration'],termination=r.get('termination',r.get('error'))) for r in rows if r['status']!='NUMERICAL_PASS']
    target=P/'results/MAIN_SAVED_VERIFICATION.json';assert not target.exists()
    result=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),all610_attempts_and_saved_gradients_verified=True,
        attempted=len(rows),completed=len(rows),numerical_pass=len(passed),failures=failed,
        max_PG_passed=max(r['PG'] for r in passed),max_AD_scaled_passed=max(r['independent']['AD_max_scaled'] for r in passed),
        max_FD_scaled_passed=max(f['max_scaled'] for r in passed for f in r['independent']['FD']),
        ledger=ledger,real_fits=0,neural_arrays_loaded=0,B_E_access=False,Final_access=False,
        scope='Saved endpoint arithmetic/hash/plan verification; no new independent AD evaluation or scientific refit')
    dump(target,result);print('Verified610 saved main attempts; passed',len(passed),'failed',len(failed))

if __name__=='__main__':run()
