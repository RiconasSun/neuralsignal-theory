"""Native MOp membership and original contact-index sensitivity proxy."""
import re
import numpy as np
from .source import R,read
from .metadata_access import local_path


def candidate_units(state):
    atlas={int(x['id']):x['acronym'] for x in read(R/'paper13/metadata/atlas.json')['msg']}
    return [u for u,(a,label) in enumerate(zip(state['native_cluster_atlas'],state['native_provider_labels']))
            if label==1 and re.fullmatch(r'MOp(?:1|2/3|4|5|6a|6b)?',str(atlas.get(int(a))))]


def boundary_units(state,row):
    atlas={int(x['id']):x['acronym'] for x in read(R/'paper13/metadata/atlas.json')['msg']}
    file=next(f for f in row['files'] if f['role']=='atlas');contacts=np.load(local_path(row,file),allow_pickle=False)
    return {u for u,ch in enumerate(state['native_cluster_channel']) if 2<=ch<len(contacts)-2
        and all(re.fullmatch(r'MOp(?:1|2/3|4|5|6a|6b)?',str(atlas.get(int(a)))) for a in contacts[ch-2:ch+3])}
