"""Exact integer predecessor verification on all corrected A query timestamps."""
from bisect import bisect_left
import datetime
import numpy as np
from .source import P,R,dump,load_json
from .metadata_access import local_path
from .features import held
from .training import admitted,sha

def run():
    frozen=load_json((P/'SOURCE_FILE_FREEZE.json').read_text());rows=[];witness=None
    for subject in admitted():
        row=next(x for x in frozen['subjects'] if x['subject']==subject)
        state=load_json((P/'metadata'/(subject+'_task.json')).read_text())
        ids=np.flatnonzero(np.asarray(state['valid'])&(np.asarray(state['roles'])=='A'))
        s=np.array([state['trials'][i]['stimOn_times'] for i in ids]);b=s[:,None]+(np.arange(20)-10)*.05;b[:,10]=s
        files={f['role']:local_path(row,f) for f in row['files'] if f['role'] in ('wheel_times','wheel_position')}
        wt=np.load(files['wheel_times'],allow_pickle=False);wp=np.load(files['wheel_position'],allow_pickle=False);timestamps=wt.tolist()
        counts={}
        for key,query in [('bin',b),('past.05',b-.05),('past.1',b-.1),('past.25',b-.25),('past.5',b-.5),('epoch',s-.5)]:
            positions,index=held(wt,wp,query)
            expected=np.array([bisect_left(timestamps,x)-1 for x in query.ravel()]).reshape(query.shape)
            np.testing.assert_array_equal(index,expected)
            assert np.all(wt[index]<query) and np.all((index+1==len(wt))|(wt[np.minimum(index+1,len(wt)-1)]>=query))
            counts[key]=int(query.size)
        if subject=='PL033':
            i=list(ids).index(224);boundary=b[i,10];assert boundary==1150.1833035011502
            _,index=held(wt,wp,boundary);assert int(index)==394299 and wt[index+1]==boundary
            witness=dict(subject=subject,trial=224,bin=10,native_query=boundary,native_hex=boundary.hex(),
                predecessor_index=int(index),excluded_equal_event=wt[index+1],equal_event_excluded=True,
                original_rounded_query=1150.1833035012,original_rounded_predecessor=394300)
        rows.append(dict(subject=subject,counts=counts,all_integer_indices_exact=True,all_events_strictly_past=True,
            task_sha256=sha(P/'metadata'/(subject+'_task.json')),wheel_sha256={k:sha(v) for k,v in files.items()}))
    assert witness is not None;target=P/'results/EXACT_WHEEL_INDEX_VERIFICATION.json';assert not target.exists()
    dump(target,dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,PL033_trial224=witness,
        STRICT_PAST_WHEEL_GATE=True,new_timestamp_tolerance=None,real_fits=0,Final_access=False))
    print('Exact strict-past indices verified',sum(sum(r['counts'].values()) for r in rows),'queries; PL033 equal event excluded')

if __name__=='__main__':run()
