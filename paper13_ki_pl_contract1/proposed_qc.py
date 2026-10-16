"""Synthetic-test reference for the proposed unit screen; no file/data loaders."""
import math

def screen(epoch_spikes,duration=3.0):
    if len(epoch_spikes)!=60 or duration!=3.0:raise ValueError('Frozen60training epochs required')
    intervals=[];n=0;occupied=0
    for times in epoch_spikes:
        if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not 0<=x<duration for x in times):raise ValueError('Invalid relative training time')
        if any(b<=a for a,b in zip(times,times[1:])):raise ValueError('Non-increasing training times')
        n+=len(times);occupied+=bool(times)
        intervals.extend(b-a for a,b in zip(times,times[1:]))
    rate=n/(len(epoch_spikes)*duration)
    fraction=sum(x<0.0015 for x in intervals)/len(intervals) if intervals else None
    passed=n>=50 and len(intervals)>=30 and occupied>=12 and .1<=rate<=100 and fraction is not None and fraction<=.01
    return {'pass':passed,'training_spikes':n,'adjacent_ISIs':len(intervals),'occupied_training_epochs':occupied,'rate_hz':rate,'refractory_fraction':fraction,'exposure_seconds':180.0}

def projected_gradient(x,g,lower=-8.0,upper=8.0):
    if len(x)!=len(g) or any(not math.isfinite(z) for z in x+g) or any(z<lower or z>upper for z in x):raise ValueError('Invalid gradient/bounds')
    projected=[0.0 if (z==lower and v>0) or (z==upper and v<0) else v for z,v in zip(x,g)]
    return max(map(abs,projected),default=0.0)
