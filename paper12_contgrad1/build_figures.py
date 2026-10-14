"""Static scientific figures from saved public numerical evidence only."""
import csv
from pathlib import Path
import study as r

def main(destination=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    public=r.HERE/'results/diagnostic/native';gate=r.load(public/'gate_result.json')
    target=Path(destination) if destination else r.HERE/'figures';target.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    scales=r.load(r.HERE/'protocol.json')['scales'];fig,axes=plt.subplots(1,3,figsize=(13.5,4.2),sharey=True)
    for ax,stage in zip(axes,gate['stages']):
        for method,color in (('central','#245f9e'),('fourth','#2c896c'),('richardson','#b76b1c')):
            values=[max(stage['scan'][str(s)][method],1e-17) for s in scales]
            ax.loglog(scales,values,'o-',color=color,label=method)
        ax.axhline(1e-5,color='#bb3944',linewidth=1.,label='frozen tolerance')
        ax.axhline(max(stage['AD_gradient_scaled_error_max'],1e-17),color='#555555',linestyle='--',label='analytic vs AD')
        ax.axvline(1e-5,color='#999999',linestyle=':');ax.set_title(stage['stage']);ax.set_xlabel('Step multiplier s');ax.grid(True,which='major',alpha=.18)
    axes[0].set_ylabel('Maximum scaled gradient error');axes[-1].legend(fontsize=8,loc='best')
    fig.suptitle('Continuous d4 / ridge 0.001 / seed 11: training-A derivative audit')
    fig.text(.5,.01,'All 384 coordinates; h_i = s max(1, |theta_i|). Original fixed-step checker and PG failure remain unchanged.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.05,1,.94));fig.savefig(target/'step_scan.png',dpi=180);plt.close(fig)
    with (public/'gradient_scan.csv').open(encoding='utf-8',newline='') as f:rows=[z for z in csv.DictReader(f) if z['stage']=='endpoint' and float(z['scale'])==1e-5]
    rows.sort(key=lambda z:int(z['coordinate']));fig,ax=plt.subplots(figsize=(11.5,3.8))
    ax.semilogy(range(384),[max(float(z['central_scaled_error']),1e-17) for z in rows],'.',label='central FD at frozen scale vs AD',color='#b76b1c')
    ax.semilogy(range(384),[max(float(z['AD_scaled_error']),1e-17) for z in rows],'.',label='analytical vs independent AD',color='#245f9e')
    for a,b,label in ((0,16,'recurrent'),(16,144,'past counts'),(144,256,'context'),(256,384,'readout')):
        ax.axvline(a,color='#999999',linewidth=.5);ax.text((a+b)/2,.99,label,transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=8)
    ax.axhline(1e-5,color='#bb3944',linewidth=1);ax.set_xlabel('Parameter coordinate');ax.set_ylabel('Scaled gradient error');ax.legend(fontsize=8,loc='lower right');ax.set_title('Reproduced endpoint: coordinate-level error; no model repair');fig.tight_layout();fig.savefig(target/'endpoint_coordinates.png',dpi=180);plt.close(fig)
    return {'input_csv_sha256':r.sha(public/'gradient_scan.csv'),'input_gate_sha256':r.sha(public/'gate_result.json'),'output_sha256':{name:r.sha(target/name) for name in ('step_scan.png','endpoint_coordinates.png')},'matplotlib_version':matplotlib.__version__}

if __name__=='__main__':
    binding=main();r.save(r.HERE/'figures/input_hashes.json',binding);print('SAVED_EVIDENCE_FIGURES_CREATED')
