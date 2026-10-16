"""Independent metadata counting with openpyxl and filename-derived identities.

No import of production audit or transport; run with a Python having openpyxl.
"""
from collections import Counter,defaultdict
import argparse
import csv
import json
from pathlib import Path
import re
import openpyxl

P=Path(__file__).resolve().parent


def run(destination):
    workbook=openpyxl.load_workbook(P/'metadata/code__python__config__datatables__allrecs_allprobes.xlsx',read_only=True,data_only=True)
    tasks=defaultdict(set)
    for sheet in workbook:
        it=sheet.iter_rows(values_only=True);columns=list(next(it))
        recidx=columns.index('recid');taskidx=columns.index('exptype')
        for values in it:
            recid=values[recidx];task=values[taskidx]
            if recid and task:tasks[str(recid)].add(str(task).strip())
    workbook.close()
    expected=json.loads((P/'results/final/audit.json').read_text(encoding='utf8'))
    policy=json.loads((P/'REGISTRATION.json').read_text())
    groups=defaultdict(list);seen=set()
    for path in (P/'metadata/headers').glob('*.json'):
        h=json.loads(path.read_text());a=h['asset'];v=h['decoded_values']
        m=re.search(r'_ses-(.+)-(\d{8})-(probe\d+)_',a['path'])
        assert m,a['path']
        animal,date,probe=m.groups();recid=animal+'_'+date+'-'+probe
        assert recid==(v.get('/general/session_id') or v['/identifier'])
        assert (a['dandiset'],recid) not in seen;seen.add((a['dandiset'],recid))
        task=next(iter(tasks[recid])) if len(tasks[recid])==1 else 'UNKNOWN'
        if task=='UNKNOWN':
            desc=(v.get('/general/experiment_description') or v.get('/session_description') or '').lower()
            if 'passive listening' in desc:task='Passive'
            elif 'aversive' in desc:task='Aversion'
        counts=Counter();locs=v['/general/extracellular_ephys/electrodes/location']
        assert len(v['/units/id'])==len(v['/units/electrodes'])
        for electrode in v['/units/electrodes']:
            label=locs[electrode]
            for region in policy['regions']:
                if label in {region+s for s in ['','1','2','3','2/3','4','5','6','6a','6b']}:
                    counts[region]+=1;break
        groups[a['dandiset']].append({'mouse':animal,'session':animal+'_'+date,'task':task,'units':len(v['/units/id']),'counts':counts})
    summary={}
    for ds,records in groups.items():
        e=expected['candidates'][ds]
        n={'files':len(records),'canonical_mice':len({r['mouse'] for r in records}),'sessions':len({r['session'] for r in records}),'units':sum(r['units'] for r in records)}
        assert all(e[k]==v for k,v in n.items())
        checked=0
        for task in {r['task'] for r in records}:
            local=[r for r in records if r['task']==task]
            assert e['strata'][task]['mice']==len({r['mouse'] for r in local})
            for name in policy['regions']:
                assert e['strata'][task]['regions'][name]['total_labeled_units']==sum(r['counts'][name] for r in local)
                for tier in policy['screening_tiers']:
                    possible=[r for r in local if r['counts'][name]>=tier]
                    assert e['strata'][task]['regions'][name]['tiers'][str(tier)]['raw_anatomical_mice']==len({r['mouse'] for r in possible})
                    checked+=1
        summary[ds]={**n,'tier_mouse_counts_checked':checked}
    with destination.open('x',encoding='utf8',newline='\n') as f:
        f.write(json.dumps({'pass':True,'independent_implementation':'openpyxl task table + DANDI filename identities + direct electrode lookup','openpyxl_version':openpyxl.__version__,'counts':summary,'no_spike_array_or_model_score_access':True},indent=2)+'\n')
    print(json.dumps(summary))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);run(p.parse_args().output)
