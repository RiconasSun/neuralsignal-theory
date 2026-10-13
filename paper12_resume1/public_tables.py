"""Traceable public admission tables, with no private or neural-content accessor."""
import csv
from collections import Counter
import study as r


def main():
    path=r.HERE/'results/M2/mouse_disposition.csv'
    with path.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    if len(rows)!=26 or len({x['mouse_id'] for x in rows})!=26:raise RuntimeError('MOUSE_DENOMINATOR_INVALID')
    groups=[]
    for group in ('development','final'):
        local=[x for x in rows if x['group']==group]
        groups.append(dict(group=group,mice=len(local),eligible_mice=sum(x['eligible_mouse']=='True' for x in local),
            eligible_CA1=sum(int(x['eligible_CA1']) for x in local),eligible_DG=sum(int(x['eligible_DG']) for x in local),
            candidate_units=sum(int(x['candidate_units']) for x in local),excluded_units=sum(int(x['excluded_units']) for x in local),
            minimum_CA1=min(int(x['eligible_CA1']) for x in local),minimum_DG=min(int(x['eligible_DG']) for x in local),
            QC_partition='train' if group=='development' else 'calibration'))
    transport=[r.load(p) for p in sorted((r.HERE/'results/transport').glob('*.json'))]
    summary=dict(groups=groups,mouse_denominator=26,reused_sessions=8,new_sessions=len(transport),
        new_HTTP_requests=sum(x['requests'] for x in transport),transient_failures=sum(x['transient_failures'] for x in transport),
        accepted_new_HTTP_bytes=sum(x['accepted_network_bytes'] for x in transport),
        old_verified_blocks_reused=sum(x['old_verified_blocks'] for x in transport),
        old_pending_blocks_newly_verified_committed=sum(x['old_pending_recovered'] for x in transport),
        custodian_full_session_target_vectors_decoded=True,final_evaluation_exposed_to_analysis=False,final_evaluated=False,
        biological_model_preference_not_assessed=True,
        inputs_sha256={'mouse_disposition.csv':r.sha(path),'source_checkpoint_integrity.json':r.sha(r.HERE/'results/M2/source_checkpoint_integrity.json'),
                      **{'transport/'+p.name:r.sha(p) for p in (r.HERE/'results/transport').glob('*.json')}})
    r.save(r.HERE/'results/M2/cohort_summary.json',summary)
    with (r.HERE/'results/M2/group_summary.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(groups[0]));writer.writeheader();writer.writerows(groups)
    print({k:v for k,v in summary.items() if k!='inputs_sha256'})


if __name__=='__main__':main()
