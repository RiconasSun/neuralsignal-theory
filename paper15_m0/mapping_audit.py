"""Explain native-versus-aggregate anatomy differences from saved non-spike metadata."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from one.alf.io import load_file_content
from .coverage import P,R,dump,region_of
def main():
    old=pd.read_csv(R/'paper13/metadata/clusters_metadata.csv.gz')
    atlas={int(a['id']):a['acronym'] for a in json.loads((R/'paper13/metadata/atlas.json').read_text(encoding='utf8'))['msg']}
    freeze=json.loads((P/'PILOT_FILE_FREEZE.json').read_text(encoding='utf8'));out=[]
    for p in json.loads((P/'PILOT_IDENTITY_FREEZE.json').read_text(encoding='utf8'))['pilots']:
        d={r['role']:load_file_content(P/'work/native'/r['eid']/Path(r['key']).name) for r in freeze['files'] if r['eid']==p['eid'] and r['role'] in ['metrics','atlas','cluster_channels']}
        o=old[old.pid.eq(p['pid'])].sort_values('cluster_id');n=d['atlas'][d['cluster_channels']];a=o.atlas_id.to_numpy()
        changed=np.flatnonzero(n!=a)
        dif=pd.DataFrame(dict(cluster_id=changed,aggregate_atlas=a[changed],native_atlas=n[changed],
            aggregate_acronym=[atlas.get(int(a[i]),'UNKNOWN') for i in changed],native_acronym=[atlas.get(int(n[i]),'UNKNOWN') for i in changed]))
        dif.to_csv(P/'results'/(p['subject']+'_ANATOMY_DIFFERENCES.csv'),index=False,lineterminator='\n')
        oldtarget=[i for i,z in enumerate(a) if region_of(atlas.get(int(z)),['MOp'])=='MOp' and o.label.to_numpy()[i]==1]
        newtarget=[i for i,z in enumerate(n) if region_of(atlas.get(int(z)),['MOp'])=='MOp' and d['metrics'].label.to_numpy()[i]==1]
        out.append(dict(subject=p['subject'],changed_clusters=len(changed),transitions=dif.groupby(['aggregate_acronym','native_acronym']).size().reset_index(name='clusters').to_dict('records'),
            good_MOp_cluster_set_equal=oldtarget==newtarget,aggregate_good_MOp=len(oldtarget),native_good_MOp=len(newtarget),
            conclusion='Native channel-linked anatomy used; no silent aggregate mapping transfer. Full native annotation freeze/revalidation for remaining candidate mice is future M1 work.'))
    dump(P/'results/MAPPING_AUDIT.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
