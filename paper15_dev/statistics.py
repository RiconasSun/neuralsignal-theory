"""Frozen exploratory mouse-level statistics; no holdout/causal validation labels."""
import itertools
import numpy as np

PRIMARY='B4-B1'
SECONDARY=['B4-B3','B4-B2','D-B4','C-B4','D-S']
CONTRASTS={PRIMARY:('B4','B1'),'B4-B3':('B4','B3'),'B4-B2':('B4','B2'),
    'D-B4':('D','B4'),'C-B4':('C','B4'),'D-S':('D','S')}


def holm(p):
    p=np.asarray(p,float);order=np.argsort(p,kind='stable')
    adjusted=np.maximum.accumulate(p[order]*(len(p)-np.arange(len(p))))
    out=np.empty_like(p);out[order]=np.minimum(1,adjusted);return out


def sign_flip(effects,two_sided=False):
    effects=np.asarray(effects,float);assert effects.ndim==1 and len(effects)>0 and np.isfinite(effects).all()
    signs=np.array(list(itertools.product([-1.,1.],repeat=len(effects))))
    null=(signs*effects).mean(axis=1);observed=float(effects.mean())
    # Same frozen M1 equality stabilization; never used to retune a threshold.
    if two_sided:return float(np.mean(np.abs(null)>=abs(observed)-1e-14))
    return float(np.mean(null>=observed-1e-14))


def summarize(effects,labs,contrast):
    d=np.asarray(effects,float);n=len(d);assert n and len(labs)==n and np.isfinite(d).all()
    rng=np.random.Generator(np.random.PCG64(150101));indices=rng.integers(0,n,(10000,n))
    bootstrap=d[indices].mean(axis=1);ci=np.quantile(bootstrap,[.025,.975],method='linear')
    unique=sorted(set(labs));labmeans={lab:float(d[np.array(labs)==lab].mean()) for lab in unique}
    labrng=np.random.Generator(np.random.PCG64(150102));draws=labrng.integers(0,len(unique),(10000,len(unique)))
    sums=np.array([d[np.array(labs)==lab].sum() for lab in unique]);sizes=np.array([np.sum(np.array(labs)==lab) for lab in unique])
    labboot=sums[draws].sum(axis=1)/sizes[draws].sum(axis=1)
    labci=np.quantile(labboot,[.025,.975],method='linear')
    return dict(contrast=contrast,n_mice=n,n_labs=len(unique),equal_mouse_mean=float(d.mean()),
        paired_sign_flip_p=sign_flip(d,contrast!=PRIMARY),test_side='one-sided-positive' if contrast==PRIMARY else 'two-sided',
        CI95=ci.tolist(),CI_width=float(ci[1]-ci[0]),bootstrap_replicates=10000,bootstrap_seed=150101,
        median=float(np.median(d)),IQR=np.quantile(d,[.25,.75],method='linear').tolist(),SD=float(d.std(ddof=1)) if n>1 else None,
        positive_mice=int(np.sum(d>0)),positive_fraction=float(np.mean(d>0)),
        leave_one_mouse_out_means=[float(np.delete(d,i).mean()) for i in range(n)] if n>1 else [],
        lab_means=labmeans,equal_lab_mean=float(np.mean(list(labmeans.values()))),
        leave_one_lab_out_means={lab:float(d[np.array(labs)!=lab].mean()) for lab in unique if len(unique)>1},
        lab_block_bootstrap_CI95=labci.tolist(),lab_bootstrap_seed=150102,
        inferential_assumption='Independent sign-exchangeable symmetric zero-centered mouse effects at null; lab dependence/asymmetry may invalidate interpretation',
        exploratory=True,heldout_animal_confirmation=False,validated=False)


def analyze(mouse_rows,expected_subjects):
    subjects=[r['subject'] for r in mouse_rows]
    assert len(expected_subjects)>0 and len(expected_subjects)==len(set(expected_subjects))
    assert len(subjects)==len(set(subjects)) and set(subjects)==set(expected_subjects)
    assert all('B1' in r['models'] and 'B4' in r['models'] for r in mouse_rows), 'Primary fixed cohort cannot silently shrink'
    for row in mouse_rows:
        for model in row['models'].values():assert model['unit_bins']>0 and np.isfinite(model['LL'])
    results={}
    for contrast,(left,right) in CONTRASTS.items():
        complete=[r for r in mouse_rows if left in r['models'] and right in r['models']]
        if len(complete)!=len(mouse_rows):
            results[contrast]=dict(contrast=contrast,status='UNAVAILABLE_FIXED_COHORT',paired_sign_flip_p=1.,validated=False,
                missing_subjects=[r['subject'] for r in mouse_rows if left not in r['models'] or right not in r['models']]);continue
        effects=[]
        for row in complete:
            a=row['models'][left];b=row['models'][right];assert a['unit_bins']==b['unit_bins']
            effects.append((a['LL']-b['LL'])/a['unit_bins'])
        results[contrast]=summarize(effects,[r['lab'] for r in complete],contrast)
        results[contrast]['mouse_effects']=[dict(subject=r['subject'],lab=r['lab'],effect=float(d),
            left_LL=r['models'][left]['LL'],right_LL=r['models'][right]['LL'],unit_bins=r['models'][left]['unit_bins']) for r,d in zip(complete,effects)]
        results[contrast]['status']='EXPLORATORY_PREDICTIVE_COMPARISON'
    adjusted=holm([results[k]['paired_sign_flip_p'] for k in SECONDARY])
    for key,p in zip(SECONDARY,adjusted):results[key]['Holm5_adjusted_p']=float(p)
    return results
