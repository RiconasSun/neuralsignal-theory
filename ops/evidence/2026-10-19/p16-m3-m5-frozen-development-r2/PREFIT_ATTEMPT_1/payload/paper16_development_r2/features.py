"""Strict-past within-presentation features; original role cuts never close gaps."""
from dataclasses import dataclass
import math
import numpy as np
from .core import spec,dynamics,AccessStop,ImplementationStop,array_id

@dataclass
class Batch:
    raw:np.ndarray
    y:np.ndarray
    ordinals:np.ndarray
    unit_ids:np.ndarray
    colors:np.ndarray
    dt:float
    psth:int
    b1:int
    role:str
    panel:str
    running_missing:np.ndarray
    score_mask:np.ndarray

    @property
    def gates(self):return np.c_[np.ones(len(self.ordinals)),self.colors,self.ordinals/179.]
    def columns(self,model):
        if model in ['D','S']:model='B4'
        return {'B1':np.arange(self.b1),'B2':np.r_[np.arange(self.b1),self.b1+np.arange(3)],
            'B3':np.r_[np.arange(self.b1),self.b1+3+np.arange(3)],
            'B4':np.arange(self.b1+6),'C':np.arange(self.b1+10)}[model].astype(int)
    def identity(self):
        return {k:array_id(getattr(self,k)) for k in ['raw','y','ordinals','unit_ids','colors','running_missing','score_mask']}

def build(flashes,running,spikes,ordinals,unit_ids,role,panel='MAIN',history=True,pupil=None,pupil_median=None):
    if role not in ['A','B','E']:raise AccessStop('Final/unknown role denied')
    ids=np.asarray(unit_ids,dtype=np.int64);rows=np.asarray(ordinals,dtype=np.int64)
    lo,hi={'A':(0,90),'B':(90,120),'E':(120,150)}[role]
    if len(rows)==0 or np.any((rows<lo)|(rows>=hi)) or np.any(np.diff(rows)<=0):raise AccessStop('Original role/ordinal integrity')
    if len(ids)<2 or len(set(ids.tolist()))!=len(ids) or len(spikes)!=len(rows):raise ImplementationStop('Population identity')
    dt=.01 if panel=='S01' else .02;t=round(.12/dt);psth=2*t
    extra={'S02':4,'S05':2,'S09':2}.get(panel,0);b1=psth+12+extra
    X=np.zeros((len(rows),t,len(ids),b1+10));y=np.zeros(X.shape[:3]);missing=np.zeros((len(rows),t),bool)
    pupil_ok=np.ones((len(rows),t),bool)
    for j,original in enumerate(rows):
        a=float(flashes['start'][original]);edges=spec.grid(a,dt);color=int(flashes['color'][original])
        if color not in [-1,1] or len(spikes[j])!=len(ids):raise ImplementationStop('Condition/population source')
        for train in spikes[j]:
            if np.asarray(train).dtype!=np.dtype('float64') or not np.isfinite(train).all() or np.any(np.diff(train)<0):raise ImplementationStop('Native timestamp integrity')
        previous=int(original)-1
        known=previous>=0 and bool(flashes['main_valid'][previous]) and flashes['stop'][previous]<a and flashes['color'][previous] in [-1,1]
        pc=float(flashes['color'][previous]) if known else 0.
        gap=a-float(flashes['stop'][previous]) if known else 0.
        repeat=math.log1p(int(np.count_nonzero(flashes['color'][:original]==color)))/math.log(181)
        order=float(original)/179
        for k in range(t):
            index=round(.1/dt)+k;start=edges[index]
            r,m=spec.past_rotation(running['start'],running['end'],running['net_rotation_promoted'],start,running.get('invalid',()))
            missing[j,k]=bool(m);tau=(start-float(flashes['start'][0]))/400
            row=np.zeros(b1);row[(0 if color==-1 else t)+k]=1
            row[psth:psth+12]=[pc,float(not known),gap/(gap+2) if known else 0,repeat,order,tau,tau*tau,tau**3,r,r*r,color*r,m]
            if panel=='S02':row[psth+12:]=[color*repeat,pc*repeat,order**2,color*order]
            elif panel=='S09':row[psth+12:]=[tau**4,tau**5]
            elif panel=='S05':
                if pupil is None or pupil_median is None or not math.isfinite(pupil_median) or pupil_median<=0:raise ImplementationStop('Verified pupil timing/A median required')
                product,end=pupil[j,k]
                good=np.isfinite(product) and product>0 and np.isfinite(end) and end<start and 0<start-end<=.1
                row[psth+12:]=[math.tanh(math.log(product/pupil_median)) if good else 0,float(not good)];pupil_ok[j,k]=good
            if not np.isfinite(row).all() or np.max(np.abs(row))>1+1e-12:raise ImplementationStop('Frozen raw nuisance bound')
            X[j,k,:,:b1]=row
            for u,train in enumerate(spikes[j]):
                y[j,k,u]=np.searchsorted(train,edges[index+1],'left')-np.searchsorted(train,start,'left')
            if history:
                X[j,k,:,b1:b1+6]=spec.histories(spikes[j],a,index,dt)
                X[j,k,:,b1+6:]=dynamics.continuous_features(spikes[j],a,index,dt)
    mask=pupil_ok if panel=='S05' else np.ones((len(rows),t),bool)
    return Batch(X,y,rows,ids,np.asarray(flashes['color'][rows]),dt,psth,b1,role,panel,missing,mask)

@dataclass
class Scaling:
    mean:np.ndarray
    scale:np.ndarray
    active:np.ndarray
    psth:int
    @classmethod
    def fit(cls,batch):
        if batch.role!='A':raise AccessStop('Only A fits current-mission scaler')
        mean=batch.raw.mean(axis=(0,1));scale=np.maximum(.25,batch.raw.std(axis=(0,1)));active=batch.raw.var(axis=(0,1))>1e-12
        mean[:,:batch.psth]=0;scale[:,:batch.psth]=1;active[:,:batch.psth]=True
        return cls(mean,scale,active,batch.psth)
    def transform(self,batch):
        if batch.psth!=self.psth or batch.raw.shape[-2:]!=self.mean.shape:raise ImplementationStop('Frozen scaler/feature identity mismatch')
        return (batch.raw-self.mean)/self.scale

def middle_rate_units(batch):
    if batch.role!='A' or len(batch.unit_ids)!=8 or batch.dt!=.02:raise AccessStop('S07 exact main A score domain required')
    rates=batch.y.sum(axis=(0,1))/(batch.y.shape[0]*batch.y.shape[1]*batch.dt)
    rank=np.lexsort((batch.unit_ids,rates));return batch.unit_ids[rank[2:6]],rates

def wrong_map(batch,flip,shift):
    if batch.psth!=12 or flip not in [0,1] or shift not in range(6) or (flip,shift)==(0,0):raise ImplementationStop('Only11 registered primary N4 maps')
    out=batch.raw.copy();out[...,:12]=0
    for j,c in enumerate(batch.colors):
        wrong=-c if flip else c
        for k in range(6):
            out[j,k,:,int(wrong==1)*6+(k+shift)%6]=1
        if flip:out[j,:,:,batch.psth+10]=-batch.raw[j,:,:,batch.psth+10]
    return out
