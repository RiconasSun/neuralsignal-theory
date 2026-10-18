"""Registered contact/layer proxy description from saved metadata/results only."""
from .source import load_json
import csv
import io
import json
import numpy as np
from .source import P,R,dump
from .calibration import admitted
from .source import sha


def composition(acronyms):
    n=len(acronyms);assert n>0
    superficial=sum(a in ('MOp1','MOp2/3') for a in acronyms)
    deep=sum(a in ('MOp5','MOp6a','MOp6b') for a in acronyms)
    middle=sum(a=='MOp4' for a in acronyms)
    return dict(units=n,superficial_units=superficial,deep_units=deep,middle_units=middle,
        unspecified_units=n-superficial-deep-middle,superficial_fraction=superficial/n,deep_fraction=deep/n,
        middle_fraction=middle/n,unspecified_fraction=(n-superficial-deep-middle)/n)


def association(x,y):
    x=np.asarray(x,float);y=np.asarray(y,float)
    assert x.shape==y.shape and np.isfinite(x).all() and np.isfinite(y).all()
    if len(x)<2 or np.ptp(x)==0 or np.ptp(y)==0:return dict(status='UNAVAILABLE_CONSTANT_OR_INSUFFICIENT',n_mice=len(x),Pearson_r=None,
        formal_hypothesis_test=False,p_value=None,causal_interpretation=False)
    return dict(status='DESCRIPTIVE_ASSOCIATION_ONLY',n_mice=len(x),Pearson_r=float(np.corrcoef(x,y)[0,1]),
        formal_hypothesis_test=False,p_value=None,causal_interpretation=False)


def build(write=True):
    atlaspath=R/'paper13/metadata/atlas.json'
    atlas={int(x['id']):x['acronym'] for x in load_json(atlaspath.read_text(encoding='utf8'))['msg']}
    rows=[];paired=[]
    for subject in admitted():
        state=load_json((P/'metadata'/(subject+'_task.json')).read_text(encoding='utf8'))
        main=load_json((P/'states'/(subject+'_C_PREPROCESSING.json')).read_text(encoding='utf8'))
        case=load_json((P/'sensitivity_states'/subject/'S11.json').read_text(encoding='utf8'))
        result=load_json((P/'results/D_sensitivities'/subject/'S11.json').read_text(encoding='utf8'))
        for label,units in [('PRIMARY8',main['units']),('S11_BOUNDARY5',case['units'])]:
            if not units:
                rows.append(dict(subject=subject,case=label,units=0,superficial_units=0,deep_units=0,middle_units=0,unspecified_units=0,
                    superficial_fraction=None,deep_fraction=None,middle_fraction=None,unspecified_fraction=None,
                    native_acronyms='[]',native_channel_indices='[]',native_depth_microns='NOT_AVAILABLE_IN_FROZEN_METADATA',
                    eligibility=case['status'] if label=='S11_BOUNDARY5' else 'PRIMARY_ADMITTED'));continue
            acronyms=[str(atlas.get(int(state['native_cluster_atlas'][u]),'UNKNOWN')) for u in units]
            row=dict(subject=subject,case=label,**composition(acronyms),native_acronyms=json.dumps(acronyms),
                native_channel_indices=json.dumps([state['native_cluster_channel'][u] for u in units]),
                native_depth_microns='NOT_AVAILABLE_IN_FROZEN_METADATA',eligibility=case['status'] if label=='S11_BOUNDARY5' else 'PRIMARY_ADMITTED')
            rows.append(row)
            if label=='S11_BOUNDARY5' and case['status']=='C_PREPROCESSING_SEALED':
                effects={}
                for contrast,baseline in [('B4-B1','B1'),('B4-B3','B3'),('B4-B2','B2')]:
                    if 'B4' not in result.get('models',{}) or baseline not in result['models']:continue
                    a,b=result['models']['B4'],result['models'][baseline];assert a['unit_bins']==b['unit_bins']>0
                    effects[contrast]=(a['LL']-b['LL'])/a['unit_bins']
                paired.append(dict(subject=subject,superficial_fraction=row['superficial_fraction'],deep_fraction=row['deep_fraction'],effects=effects))
    associations={}
    for fraction in ['superficial_fraction','deep_fraction']:
        associations[fraction]={contrast:association([r[fraction] for r in paired if contrast in r['effects']],
            [r['effects'][contrast] for r in paired if contrast in r['effects']]) for contrast in ['B4-B1','B4-B3','B4-B2']}
    output=dict(registered_scope='S11 native layer/contact-index description and descriptive effect association only',
        atlas_sha256=sha(atlaspath),subjects=admitted(),paired_rows=paired,associations=associations,
        fraction_denominator='All selected units, including unspecified/root anatomy; MOp4 separate',
        limitation='Native atlas layer labels and ±2contact indices are proxies; no histological distance, causal layer mechanism or new hypothesis test',Final_D_assessment=True,biological_layer_claim=False)
    text=io.StringIO(newline='');writer=csv.DictWriter(text,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    if write:
        dump(P/'results/LAYER_PROXY_ASSOCIATIONS.json',output)
        path=P/'tables/ANATOMY_LAYER_PROXY.csv';path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(text.getvalue().encode('utf8'))
    return output,text.getvalue().encode('utf8')


if __name__=='__main__':build()
