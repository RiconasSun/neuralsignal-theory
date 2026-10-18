"""Copy saved evidence, reproduce existing arithmetic and render measured figures."""
import ast,csv,hashlib,itertools,math,shutil,os
from .source import P,R,E,ORDER,LABELS,COHORTS,read,rows,write_rows,dump,sha,stats,fmt
os.environ.setdefault('MPLCONFIGDIR',str(P/'work/matplotlib'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DEV='#35687b';FINAL='#996046';INK='#273540';GRAY='#72818a'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.labelcolor':INK,'text.color':INK,'axes.edgecolor':'#b0b8bc','axes.titlesize':10,
                     'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'P15-M7-results-locked','savefig.facecolor':'white'})

def existing_arithmetic():
    """Reproduce only the exact originally registered saved-mouse arithmetic."""
    checked={}
    for cohort,folder in COHORTS.items():
        s=stats(cohort);tab=rows(R/folder/'tables'/('E_MOUSE_EFFECTS.csv' if cohort=='Development' else 'FINAL_INDIVIDUAL_MOUSE_EFFECTS.csv'))
        for contrast in ORDER:
            source=[r for r in tab if r['contrast']==contrast]
            v=np.array([float(r['effect']) for r in source]);n=len(v)
            for r in source:
                assert math.isclose((float(r['left_LL'])-float(r['right_LL']))/int(r['unit_bins']),float(r['effect']),abs_tol=1e-13)
            assert math.isclose(float(np.mean(v)),s[contrast]['equal_mouse_mean'],abs_tol=1e-13)
            rng=np.random.Generator(np.random.PCG64(150101));ix=rng.integers(0,n,size=(10000,n))
            ci=np.quantile(v[ix].mean(axis=1),[.025,.975],method='linear')
            assert np.allclose(ci,s[contrast]['CI95'],atol=1e-13,rtol=0)
            signed=(np.array(list(itertools.product([-1.,1.],repeat=n)))*v).mean(axis=1)
            test=s[contrast]['test_side']
            p=np.mean(signed>=v.mean()-1e-14) if contrast=='B4-B1' else np.mean(np.abs(signed)>=abs(v.mean())-1e-14)
            assert math.isclose(p,s[contrast]['paired_sign_flip_p'],abs_tol=1e-15)
            checked[cohort+'/'+contrast]={'n':n,'exact_mean':True,'original_10000_CI':True,'original_sign_flips':True}
        # This is the original fixed five-test family, not an added test.
        raw=np.array([s[c]['paired_sign_flip_p'] for c in ORDER[1:]])
        order=np.argsort(raw,kind='stable');adjusted=np.empty(5);adjusted[order]=np.minimum(1,np.maximum.accumulate((5-np.arange(5))*raw[order]))
        existing=rows(R/folder/'tables'/('E_CONTRASTS.csv' if cohort=='Development' else 'FINAL_CONTRASTS.csv'))
        for c,p in zip(ORDER[1:],adjusted):
            r=next(r for r in existing if r['contrast']==c);assert abs(float(r['Holm5_p'])-p)<1e-14
    dump(P/'tables/ARITHMETIC_REPRODUCTION.json',dict(scope='Original published mouse-level arithmetic only; no new hypotheses,predictions or neural data',checks=checked,Final_D_reruns=0))

def collect():
    mapping={}
    for cohort,folder in COHORTS.items():
        for path in sorted((R/folder/'tables').glob('*.csv')):
            target=P/'tables'/f'{cohort.upper()}_{path.name}'
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
            assert sha(target)==sha(path)
            mapping[target.relative_to(P).as_posix()]={'source':path.relative_to(R).as_posix(),'sha256':sha(path)}
    roster=rows(R/'paper15_m1/COHORT.csv')
    dev={r['subject']:r for r in rows(R/'paper15_r1/tables/COHORT_FINAL_NATIVE_QC.csv')}
    final={r['subject']:r for r in rows(R/'paper15_final1/tables/FINAL_SOURCE_AND_C_QC.csv')}
    inventory=[]
    for r in roster:
        q=dev[r['subject']] if r['allocation']=='DEVELOPMENT' else final[r['subject']]
        admitted=q.get('development_physiology_admitted',q.get('C_admitted'))=='True'
        reason=q.get('exclusion',q.get('exclusion_reason',''))
        if r['subject']=='NYU-37':reason='31 B epochs, below40 frozen minimum'
        if r['subject']=='CSHL059':reason='sync domain[0,1] yields zero covered epochs'
        inventory.append({k:r[k] for k in ['subject','lab','allocation','date','session_number','probe_name','eid','pid']}|{'admitted':admitted,'exclusion':reason})
    write_rows(P/'tables/SOURCE_COHORT_IDENTITIES.csv',inventory)
    unitrows=[]
    for mouse,r in final.items():
        if r['C_admitted']!='True':continue
        q=read(R/f'paper15_final1/results/{mouse}_C_QC.json')
        phy={u['uuid']:u for u in q['physiology']}
        for rank,uuid in enumerate(q['selected_unit_uuids'],1):
            u=phy[uuid]
            unitrows.append(dict(subject=mouse,rank=rank,cluster_id=u['cluster_id'],UUID=uuid,C_rate_Hz=u['C_rate_Hz'],C_ISI_fraction=u['C_refractory_fraction'],C_spikes=u['C_spikes'],C_exposure_s=u['C_exposure_seconds'],quartile_rates_Hz=u['original_C_quartile_rates'],quartile_exposures_s=u['original_C_quartile_exposures'],primary_qualified=u['primary_qualified']))
    assert len(unitrows)==48;write_rows(P/'tables/FINAL_SELECTED_UNIT_QC.csv',unitrows)
    parameterrows=[]
    for name in ['FINAL_MAIN_ATTEMPTS.csv','FINAL_SENSITIVITY_ATTEMPTS.csv']:
        for r in rows(R/'paper15_final1/tables'/name):
            f=read(R/'paper15_final1'/r['path']);q=f['configuration']
            parts=r['path'].split('/')
            parameterrows.append(dict(subject=parts[1],case='PRIMARY' if parts[0]=='fits' else parts[2],configuration=parts[-1].removesuffix('.json'),family=r['family'],free_parameters=f['free_parameters'],stored_vector_length=len(f['coefficients']),PG=r['PG'],AD=r['AD_max_scaled'],FD=r['max_FD_scaled'],iterations=r['iterations'],status=r['status'],certificate=r['path'],sha256=r['sha256']))
    assert len(parameterrows)==392;write_rows(P/'tables/FINAL_NUMERICAL_CERTIFICATES.csv',parameterrows)
    dump(P/'tables/SAVED_TABLE_SOURCE_MAP.json',mapping)
    # Reorder only for reporting. Original CSV bytes are copied alongside this view.
    publication=[]
    for cohort in COHORTS:
        folder=COHORTS[cohort];old=rows(R/folder/'tables'/('E_CONTRASTS.csv' if cohort=='Development' else 'FINAL_CONTRASTS.csv'))
        for c in ORDER:publication.append({'cohort':cohort,**next(r for r in old if r['contrast']==c)})
    write_rows(P/'tables/REGISTERED_CONTRAST_ORDER.csv',publication)

def export(fig,name):
    folder=P/'figures';folder.mkdir(exist_ok=True)
    for ext in ['png','svg','pdf']:fig.savefig(folder/f'{name}.{ext}',dpi=450,bbox_inches='tight',metadata={'Creator':'P15 results-locked saved-table rendering','CreationDate':None,'ModDate':None} if ext=='pdf' else ({'Date':None} if ext=='svg' else None))
    plt.close(fig)

def figure1():
    fig,ax=plt.subplots(figsize=(7.2,4.5));ax.set_axis_off()
    boxes=[(.3,.86,.4,.10,'Original fixed MOp cohort:20 mice\n12 Development /8 Final','#e5ecef'),
           (.03,.59,.42,.14,'Development:12 originally allocated\nNYU-37:31 B epochs (<40)\nCSHL059:source support [0,1]s','#edf2f4'),
           (.55,.59,.42,.14,'Final:8 originally reserved\nNYU-21:non-strict wheel clock\nUCLA033:6 C-qualified units (<8)','#f3eeea'),
           (.03,.32,.42,.14,'10 admitted mice /8 labs\nA fit(60%); B selection(20%)\nE exploratory report(20%)','#edf2f4'),
           (.55,.32,.42,.14,'6 admitted mice /4 labs\nC-only calibration(60%)\nOne frozen D batch(40%)','#f3eeea')]
    for x,y,w,h,t,col in boxes:ax.add_patch(plt.Rectangle((x,y),w,h,facecolor=col,edgecolor='#aebbc1',lw=.8));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=9)
    for x in [.24,.76]:
        ax.annotate('',xy=(x,.73),xytext=(.5,.86),arrowprops={'arrowstyle':'->','color':GRAY});ax.annotate('',xy=(x,.46),xytext=(x,.59),arrowprops={'arrowstyle':'->','color':GRAY})
    ax.text(.5,.16,'Final interpretation fixed to DESCRIPTIVE ONLY\nSix<eight confirmation floor; original precision and reference gates unchanged',ha='center',va='center',fontsize=10)
    ax.text(.5,.025,'Counts denote independent mice; percentages denote original chronological trial-row partitions.\nBoundary guards and support masks precede scoring; no animal/session/probe replacement.',ha='center',va='center',fontsize=8,color=GRAY)
    export(fig,'Figure_1_Design_and_attrition')

def figure2():
    fig,axes=plt.subplots(1,2,figsize=(7.2,4.8),sharex=True)
    for ax,cohort,color in zip(axes,COHORTS,[DEV,FINAL]):
        folder=COHORTS[cohort];rs=rows(R/folder/'tables'/('E_MOUSE_EFFECTS.csv' if cohort=='Development' else 'FINAL_INDIVIDUAL_MOUSE_EFFECTS.csv'));rs=[r for r in rs if r['contrast']=='B4-B1'];s=stats(cohort)['B4-B1']
        y=np.arange(len(rs));ax.scatter([float(r['effect']) for r in rs],y,c=color,s=28,zorder=3)
        ax.set_yticks(y,[r['subject'] for r in rs]);ax.axvline(0,color=GRAY,lw=.7);ax.set_ylim(len(rs)+1,-1)
        mean=s['equal_mouse_mean'];lo,hi=s['CI95'];ax.errorbar(mean,len(rs)+.3,xerr=[[mean-lo],[hi-mean]],fmt='D',color=INK,capsize=3,ms=5)
        ax.set_yticks([*y,len(rs)+.3],[*[r['subject'] for r in rs],'Mean /95% CI'])
        ax.set_title(f'{cohort}:n={len(rs)} mice');ax.set_xlabel('B4-B1 gain (nats / nominal unit-bin)')
    axes[0].set_xlim(-.01,.245);fig.suptitle('Primary local-history prediction:separate cohorts',fontsize=12,y=1.01)
    fig.text(.5,.015,'Individual dots are mice; diamonds and bars are equal-mouse means and95% percentile bootstrap intervals.\n50-ms bins; Final remains DESCRIPTIVE ONLY. No pooled Development-Final test.',ha='center',va='bottom',fontsize=8)
    fig.tight_layout(rect=(0,.20,1,1));export(fig,'Figure_2_Primary_mouse_effects')

def figure3():
    fig,axes=plt.subplots(1,2,figsize=(7.3,4),sharey=True)
    for ax,cohort,col in zip(axes,COHORTS,[DEV,FINAL]):
        s=stats(cohort)
        for i,c in enumerate(ORDER):
            d=s[c];v=d['equal_mouse_mean'];lo,hi=d['CI95'];ax.errorbar(v,i,xerr=[[v-lo],[hi-v]],fmt='o',color=col,ms=4,capsize=3)
        ax.axvline(0,color=GRAY,lw=.8);ax.set_title(f'{cohort}:n={s[ORDER[0]]["n_mice"]} mice');ax.set_yticks(range(6),ORDER);ax.set_ylim(5.5,-.5);ax.set_xlabel('Gain (nats / nominal unit-bin)');ax.set_xlim(-.042,.18)
    fig.text(.5,.015,'Bars:95% whole-mouse percentile intervals. Fixed50-ms primary configuration.\nSecondary Holm5 tests are nonsignificant in both cohorts; Final:all six DESCRIPTIVE ONLY.',ha='center',va='bottom',fontsize=8)
    fig.tight_layout(rect=(0,.22,1,1));export(fig,'Figure_3_All_registered_contrasts')

def figure4():
    fig,axes=plt.subplots(1,2,figsize=(7.2,4.2),sharey=True)
    for ax,cohort,col in zip(axes,COHORTS,[DEV,FINAL]):
        folder=COHORTS[cohort];rs=rows(R/folder/'tables'/('E_MOUSE_EFFECTS.csv' if cohort=='Development' else 'FINAL_INDIVIDUAL_MOUSE_EFFECTS.csv'))
        own={r['subject']:float(r['effect']) for r in rs if r['contrast']=='B4-B3'};other={r['subject']:float(r['effect']) for r in rs if r['contrast']=='B4-B2'}
        for mouse in own:ax.plot([0,1],[own[mouse],other[mouse]],'-o',color=col,alpha=.65,lw=.8,ms=3)
        ax.axhline(0,color=GRAY,lw=.7);ax.set_xticks([0,1],['Own:B4-B3','Other:B4-B2']);ax.set_title(cohort);ax.set_xlim(-.25,1.25)
    axes[0].set_ylabel('Conditional contribution (nats / nominal unit-bin)')
    fig.text(.5,.015,'Lines pair the two saved predictive ablations within each mouse; no added comparison test.\nConditional predictive attribution is not causal connectivity.50-ms bins.',ha='center',va='bottom',fontsize=8)
    fig.tight_layout(rect=(0,.20,1,1));export(fig,'Figure_4_Own_and_other_history')

def figure5():
    fig,axes=plt.subplots(1,2,figsize=(7.0,5.7),sharey=True)
    for ax,cohort in zip(axes,COHORTS):
        summary=read(R/COHORTS[cohort]/'results'/('E_CONTROL_SUMMARY.json' if cohort=='Development' else 'D_CONTROL_SUMMARY.json'))
        # All 24 cells are shown; N3 is always labelled as its separate diagnostic.
        for i,c in enumerate(ORDER):
            for j,n in enumerate(['N1','N2','N3','N4']):
                r=summary[c][n];nm=int(r['n_mice'])
                missing='UNAVAILABLE' in r['status'];gate=r.get('descriptive_disruption_gate',False)
                count=r.get('mice_above_reference_median','')
                if missing:t=f'Unavailable\nn={nm}';fc='#ececec'
                elif n=='N3':t=f'Wheel LL\nn={nm}';fc='#f0f3f4'
                else:t=f'{count}/{nm}\n'+('gate met' if gate is True else 'gate failed');fc='#e7eef1' if gate is True else '#f0e8e2'
                ax.add_patch(plt.Rectangle((j-.48,i-.48),.96,.96,fc=fc,ec='white'));ax.text(j,i,t,ha='center',va='center',fontsize=8.5)
        ax.set(xlim=(-.5,3.5),ylim=(5.5,-.5));ax.set_xticks(range(4),['N1\nrotation','N2\nhistory','N3\nwheel','N4\nblocks']);ax.set_yticks(range(6),ORDER);ax.set_title(cohort)
        for spine in ax.spines.values():spine.set_visible(False)
        ax.tick_params(length=0)
    fig.text(.5,.015,'Counts are mice above their within-mouse999-reference median; gates require >=75% and positive mean degradation.\nN3 is a B4-likelihood wheel diagnostic,not six contrast-specific nulls. N4 unavailable in both cohorts.\nEvery available suite has999 frozen replicates/mouse. Colors identify panel status,not confirmation.',ha='center',va='bottom',fontsize=8)
    fig.tight_layout(rect=(0,.20,1,1));export(fig,'Figure_5_Reference_outcomes')

def figure6():
    fig,axes=plt.subplots(1,3,figsize=(7.0,6.0),sharey=True)
    labels=['S01:5 units','S02:12 units','S03:20 units','S04:100 ms','S05:250-ms history','S06:stricter QC','S07:rate thinning','S08:saturation10 ms','S09:saturation50 ms','S10:rich drift','S11:boundary5']
    rs=rows(P/'tables/FINAL_FINAL_SENSITIVITIES.csv')
    for ax,c in zip(axes,['B4-B1','B4-B3','B4-B2']):
        for i,case in enumerate([f'S{x:02}' for x in range(1,12)]):
            r=next(r for r in rs if r['case']==case and r['contrast']==c);v=float(r['mean']) if r['mean'] else None
            ci=ast.literal_eval(r['CI95']) if r['CI95'] and r['CI95']!='None' else None
            if r['coverage_pass']=='True' and ci is not None:
                ax.errorbar(v,i,xerr=[[v-ci[0]],[ci[1]-v]],fmt='o',color=FINAL,capsize=2,ms=3)
            else:ax.text(.02,i,'unavailable (n='+r['n_mice']+')',transform=ax.get_yaxis_transform(),va='center',fontsize=7.5,color=GRAY)
        ax.axvline(0,color=GRAY,lw=.6);ax.set_title(c);ax.set_xlabel('Nats / nominal unit-bin',fontsize=8);ax.set_yticks(range(11),labels);ax.set_ylim(10.7,-.7)
    fig.text(.5,.015,'Final B0-B4 sensitivity refits only; no D/C/S sensitivity refits. Bars:95% whole-mouse percentile intervals.\nAll available cases n=6; S03 n=4 is unavailable. S04 uses100-ms bins; all other cases use50-ms bins.\nPer-bin magnitudes across different bin widths are not interchangeable.',ha='center',va='bottom',fontsize=8)
    fig.tight_layout(rect=(0,.22,1,1));export(fig,'Figure_6_Final_baseline_sensitivities')

def figure7():
    fig,axes=plt.subplots(1,2,figsize=(7.5,5.8),gridspec_kw={'width_ratios':[1.2,1]})
    anatomy=[]
    for cohort in COHORTS:
        rs=rows(P/'tables'/f'{cohort.upper()}_ANATOMY_LAYER_PROXY.csv')
        for r in rs:
            if r['case']=='PRIMARY8':anatomy.append((cohort,r))
    ax=axes[0];bottom=np.zeros(len(anatomy));colors=['#6f91a1','#b7c7cd','#ccab91','#dddddd']
    for field,label,col in zip(['superficial_fraction','middle_fraction','deep_fraction','unspecified_fraction'],['MOp1/2-3','MOp4','MOp5/6','Root/unknown'],colors):
        v=np.array([float(r[field]) for _,r in anatomy]);ax.barh(range(len(anatomy)),v,left=bottom,color=col,label=label,height=.73);bottom+=v
    ax.set_yticks(range(len(anatomy)),[('Dev ' if co=='Development' else 'Final ')+r['subject'] for co,r in anatomy],fontsize=7);ax.invert_yaxis();ax.set_xlabel('Fraction of eight selected units');ax.set_title('Native atlas composition');ax.legend(fontsize=6.8,loc='lower center',bbox_to_anchor=(.5,-.24),ncol=2,frameon=False)
    ax=axes[1];s=stats('Final')['B4-B1'];labs=s['lab_means'];y=np.arange(len(labs));ax.scatter(list(labs.values()),y,color=FINAL,s=30)
    ax.set_yticks(y,[lab.replace('churchlandlab_ucla','UCLA').replace('lab','') for lab in labs],fontsize=8);ax.axvline(0,color=GRAY,lw=.6);ax.set_xlabel('Primary gain(nats / nominal unit-bin)');ax.set_title('Final lab means:descriptive')
    fig.text(.66,.11,'4 labs;1/2/2/1 mice\nEqual-mouse mean=0.08658\nEqual-lab mean=0.08070\nNo independent-lab replication',ha='center',fontsize=8,va='bottom')
    fig.text(.5,.015,'Atlas layer labels and contact-index neighborhoods are proxies; native depth is unavailable.\nNo anatomical reclassification or new association test. Lab points are means,without inferential error bars.',ha='center',va='bottom',fontsize=8)
    fig.tight_layout(rect=(0,.22,1,1));export(fig,'Figure_7_Anatomy_and_laboratories')

def render_figures():
    for fn in [figure1,figure2,figure3,figure4,figure5,figure6,figure7]:fn()
    manifest={p.name:sha(p) for p in (P/'figures').iterdir() if p.suffix in {'.png','.svg','.pdf'}}
    assert len(manifest)==21;dump(P/'figures/FIGURE_MANIFEST.json',manifest)
