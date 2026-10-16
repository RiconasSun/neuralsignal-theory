"""Export all release mouse/session identities from saved M0 metadata."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from metadata_audit import read_csv

P=Path(__file__).resolve().parent


def main():
    rows=list(read_csv(P/'results/M0/all_probe_region_denominators.csv'))
    sessions=defaultdict(list);mice=defaultdict(list)
    for row in rows:
        sessions[row['eid']].append(row);mice[row['mouse_id']].append(row)
    output=P/'results/M0'
    for name,groups,keyname in [('all_session_denominators.csv',sessions,'eid'),('all_mouse_denominators.csv',mice,'mouse_id')]:
        records=[]
        for key,group in sorted(groups.items()):
            first=group[0]
            row={keyname:key,'mouse_id':first['mouse_id'],'lab':first['lab'],'subject':first['subject'],
                 'sessions':len({r['eid'] for r in group}),'probes':len({r['pid'] for r in group}),
                 'usable_trial_max':max(int(r['usable_timing_provider_trials']) for r in group)}
            for region in ['ACAd','ORBvl','PL']:
                local=[r for r in group if r['region']==region]
                row[region+'_max_same_probe_good']=max(int(r['provider_good_units']) for r in local)
                row[region+'_unit_count_possible']=any(r['unit_count_pass']=='True' for r in local)
                row[region+'_both_counts_possible']=any(r['count_upper_bound_pass']=='True' for r in local)
            row['admission']='NOT_ADMITTED_M0_STOP'
            records.append(row)
        with (output/name).open('x',encoding='utf8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    print(json.dumps({'mice':len(mice),'sessions':len(sessions),'probe_region_rows':len(rows)}))


if __name__=='__main__':main()
