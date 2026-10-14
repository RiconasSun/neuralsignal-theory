"""Scientific plots from public saved histories only."""
from pathlib import Path
import study as r
def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    target=r.HERE/'figures';target.mkdir(exist_ok=False)
    audit=r.load(r.HERE/'results/audit/native/conditioning_audit.json');plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11.8,4))
    block=audit['stages']['endpoint']['blocks'];names=list(block)
    axes[0].bar(names,[block[n]['physical_PG'] for n in names],color=['#316a9b','#c47727','#388c73','#777777']);axes[0].axhline(.001,color='#b63744',linestyle='--',label='PG threshold');axes[0].set_yscale('log');axes[0].set_ylabel('Original physical block PG');axes[0].legend(fontsize=8)
    for scale,color in (('1e-07','#316a9b'),('1e-08','#c47727')):
        values=np.array(audit['curvature'][scale]['spectrum']['eigenvalues']);axes[1].plot(values,'.-',markersize=2,linewidth=.7,label=scale,color=color)
    axes[1].set_yscale('symlog',linthresh=.01);axes[1].set_xlabel('Sorted eigenvalue index');axes[1].set_ylabel('Local symmetric Hessian eigenvalue');axes[1].legend(fontsize=8)
    fig.suptitle('Frozen failing endpoint: input PG dominates; local curvature is indefinite');fig.tight_layout();fig.savefig(target/'conditioning.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.2))
    colors={'A':'#316a9b','B':'#c47727','C':'#388c73'}
    for name,color in colors.items():
        history=r.load(r.HERE/f'results/{name}/native/termination_history.json')['accepted']
        if history:
            x=[z['accepted'] for z in history];axes[0].plot(x,[z['objective'] for z in history],label=name,color=color,linewidth=1);axes[1].semilogy(x,[max(z['PG'],1e-14) for z in history],label=name,color=color,linewidth=1)
    axes[0].axhline(19.87905908627809,color='#777777',linestyle=':',label='common start');axes[1].axhline(.001,color='#b63744',linestyle='--',label='unchanged PG threshold')
    for ax in axes:ax.set_xlabel('Recorded callback / warm-update state');ax.legend(fontsize=8);ax.grid(alpha=.15)
    axes[0].set_ylabel('Original penalized Training-A objective');axes[1].set_ylabel('Full original physical projected gradient');fig.suptitle('Three fixed candidates; all outcomes retained');fig.tight_layout();fig.savefig(target/'candidate_trajectories.png',dpi=180);plt.close(fig)
    r.save(target/'bindings.json',{'audit_sha256':r.sha(r.HERE/'results/audit/native/conditioning_audit.json'),'history_sha256':{n:r.sha(r.HERE/f'results/{n}/native/termination_history.json') for n in colors},'figures_sha256':{n:r.sha(target/n) for n in ('conditioning.png','candidate_trajectories.png')},'source':'saved public metrics; no new model calls','trust_callbacks_may_repeat_same_iterate':True})
    print('SAVED_FIGURES_CREATED')
if __name__=='__main__':main()
