"""Small synthetic reference operators for proposed protocol ambiguities, not models."""
import itertools

def scalar_leaky_states(standardized_counts,rho):
    # Output predicting count index0 is reset; index1uses observed count index0.
    states=[];h=0.0
    for i in range(len(standardized_counts)):
        if i:h=rho*h+(1-rho)*standardized_counts[i-1]
        states.append(h)
    return states

def restricted_linear(terms,retained):
    # term=(already-standardized feature, coefficient, neural source id or None).
    return sum(value*coef for value,coef,source in terms if source is None or source in retained)

def state_prior(p,posterior):
    return [p*posterior[0]+(1-p)*posterior[1],(1-p)*posterior[0]+p*posterior[1]]

def sign_flip_p(differences):
    n=len(differences)
    if not n:raise ValueError('Paired differences required')
    observed=abs(sum(differences))
    return sum(abs(sum(s*x for s,x in zip(signs,differences)))>=observed for signs in itertools.product([-1,1],repeat=n))/(2**n)

def censor_recent_epoch(epoch,onsets,intervals=()):
    a,b=epoch[0]-5,epoch[1]
    return any(a<=t<b for t in onsets) or any(x<b and a<y for x,y in intervals)

def shifted_score_bins(epoch,shift):
    if shift not in [-.1,.1]:raise ValueError('Frozen shift only')
    start=epoch[0]+shift
    return [(start+.1*i,start+.1*(i+1)) for i in range(5,30) if start+.1*(i+1)<=epoch[1]+1e-10]

def broad_baseline_direction(model,b4,strongest):
    return model>b4 and model>strongest

def temporal_direction(p,model,static):
    return p>.5 and model>static

def deep_laminar_mask(labels):return [k for k,label in labels.items() if label in {'PL5','PL6a'}]
