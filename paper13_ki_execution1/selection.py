"""Registered equal-mouse paired one-SE and strongest-baseline rules."""
import numpy as np


def ridge_choice(scores,ridges=(.1,1.,10.)):
    scores=np.asarray(scores,dtype=float);ridges=list(ridges)
    if scores.ndim!=2 or scores.shape[0]<8 or scores.shape[1]!=len(ridges) or not np.isfinite(scores).all():
        raise ValueError('Finite paired scores from at least8mice required')
    means=scores.mean(axis=0);maximum=float(means.max())
    best=max((j for j in range(len(ridges)) if maximum-means[j]<=1e-12),key=lambda j:ridges[j])
    differences=scores[:,best,None]-scores
    margin=differences.mean(axis=0);se=differences.std(axis=0,ddof=1)/np.sqrt(len(scores))
    eligible=np.flatnonzero(margin<=se).tolist()
    chosen=max(eligible,key=lambda j:ridges[j])
    return {'selected_index':chosen,'selected_ridge':ridges[chosen],'best_reference_index':best,
            'means':means.tolist(),'paired_mean_loss':margin.tolist(),'paired_SE':se.tolist(),
            'one_SE_eligible_indices':eligible,'mice':len(scores)}


def strongest(scores,parameters=None):
    parameters=parameters or {'B0':8,'B1':96,'B2':32,'B3':176,'B4':288}
    if set(scores)!=set(parameters):raise ValueError('All five baseline score vectors required')
    values={name:np.asarray(v,dtype=float) for name,v in scores.items()}
    n=len(values['B0'])
    if n<8 or any(v.shape!=(n,) or not np.isfinite(v).all() for v in values.values()):
        raise ValueError('Matched finite equal-mouse baseline scores required')
    means={name:float(v.mean()) for name,v in values.items()};best=max(means.values())
    chosen=min((name for name in means if best-means[name]<=1e-12),key=lambda name:(parameters[name],int(name[1:])))
    return {'B_star':chosen,'equal_mouse_means':means,'parameters':parameters,'mice':n}
