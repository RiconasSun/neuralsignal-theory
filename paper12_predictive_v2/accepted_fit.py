"""Original scientific PG acceptance around the frozen new-track solver."""
import numpy as np
from glm import fit,obj,independent_ad
def original_pg(theta,gradient):
    g=np.asarray(gradient,dtype=float).copy()
    g[(theta<=-8)&(g>0)]=0;g[(theta>=8)&(g<0)]=0
    return float(np.max(np.abs(g)))
def accepted_fit(x,y):
    w,record=fit(x,y);f,g=obj(w,x,y);af,ag=independent_ad(w,x,y)
    record.update(original_definition_PG=original_pg(w,g),AD_original_definition_PG=original_pg(w,ag))
    record['passed']=record['passed'] and record['original_definition_PG']<=.001 and record['AD_original_definition_PG']<=.001
    return w,record
