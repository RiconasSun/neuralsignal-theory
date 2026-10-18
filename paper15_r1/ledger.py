"""Distinct historical and corrective attempt accounting; no fitting or data loading."""
import datetime
from .source import P,R,dump,load_json

def snapshot():
    plan=load_json((P/'A_FIT_PLAN.json').read_text());subjects=plan['subjects']
    assert plan['per_mouse']==61 and plan['total_main']==61*len(subjects)<=732
    main=list((P/'fits').glob('*/*.json'));sensitivity=list((P/'sensitivity_fits').glob('*/*/*.json'))
    expected={(s,c['id']) for s in subjects for c in plan['configurations']}
    assert len(main)==len({(p.parent.name,p.stem) for p in main})<=61*len(subjects)
    assert {(p.parent.name,p.stem) for p in main}<=expected
    assert len(sensitivity)<=55*len(subjects)<=660
    records=[load_json(p.read_text()) for p in main+sensitivity]
    assert all(r['attempt']==1 and r['status'] in ('STARTED','NUMERICAL_PASS','NUMERICAL_FAIL') for r in records)
    return dict(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        historical_started=359,historical_completed=358,historical_interrupted=1,historical_unattempted=251,
        NEW_MAIN_ATTEMPTS=len(main),NEW_SENSITIVITY_ATTEMPTS=len(sensitivity),TOTAL_CUMULATIVE_ATTEMPTS=359+len(main)+len(sensitivity),
        completed=sum(r['status']!='STARTED' for r in records),numerical_pass=sum(r['status']=='NUMERICAL_PASS' for r in records),
        new_interrupted_or_active=sum(r['status']=='STARTED' for r in records),main_cap=61*len(subjects),sensitivity_cap=55*len(subjects),
        absolute_main_cap=732,absolute_sensitivity_cap=660,retries=0,Final_access=False,
        corrective_authorization_not_retroactive_compliance=True)

if __name__=='__main__':
    import json
    print(json.dumps(snapshot()))
