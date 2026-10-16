"""Frozen saved-result reporting; never fits, reads neural sources or rescores D."""
import csv
import json
from pathlib import Path
import numpy as np
from .common import P, OLD
from paper13_ki_execution1 import baseline_A as b

CONTRASTS=['D_minus_B4','C_minus_B4','D_minus_C','D_minus_Bstar','C_minus_Bstar','D_minus_S']
MODELS=['B0','B1','B2','B3','B4','D','C','S','Bstar']


def fmt(value):
    return 'UNAVAILABLE' if value is None else format(float(value),'.8g')


def md_table(headers,rows):
    # Raw labels remain exact in CSV/JSON; slash is the displayed pipe separator.
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(cell).replace('|',' / ') for cell in row)+' |' for row in rows])


def write_csv(path,headers,rows):
    with path.open('w',encoding='utf8',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(headers);writer.writerows(rows)


def prepare(out=None):
    out=Path(out or P/'manuscript');out.mkdir(parents=True,exist_ok=True)
    final=b.read(P/'results/FINAL_D_RESULTS.json');calibration=b.read(P/'results/FINAL_C_FULL_STATE_MANIFEST.json')
    if final['FINAL_D_EXECUTION']!='VALIDLY_COMPLETED_ONCE_DESCRIPTIVE' or calibration['COMPLETE_C_STATE']!='PASS':
        raise RuntimeError('Valid complete descriptive result and sealed C required for manuscript')
    if final['null_controls']['conditional_Bstar_status']!='FAILED_UNAVAILABLE':raise RuntimeError('Missing null must not be relabeled')
    development=b.read(OLD/'results/M5_EXPLORATORY_RESULTS.json')
    stats=final['statistics']['contrasts'];devstats=development['registered_statistics']['contrasts']
    rows=[];rawrows=[]
    for name in CONTRASTS:
        for label,values in [('E (exploratory)',devstats[name]),('D (descriptive)',stats[name])]:
            lo,hi=values['CI95_percentile'];n=len(values['mouse_effects'])
            rows.append([label,name,fmt(values['mean_nats_per_nominal_unit_bin']),fmt(values['Holm_adjusted_p']),f'[{fmt(lo)}, {fmt(hi)}]',f"{values['positive_mice']}/{n}"])
            rawrows.append([label,name,values['mean_nats_per_nominal_unit_bin'],values['signflip']['p'],values['Holm_adjusted_p'],lo,hi,values['positive_mice'],n,min(values['leave_one_mouse_out_means'])])
    write_csv(out/'contrasts.csv',['partition','contrast','mean','raw_signflip_p','Holm_p','CI_low','CI_high','positive_mice','n','minimum_LOMO_mean'],rawrows)
    score_rows=[]
    for label,data,mice in [('E',development['per_mouse'],development['mouse_order']),('D',final['per_mouse'],final['mouse_order'])]:
        for mouse in mice:score_rows.append([label,mouse]+[data[mouse]['scores'][name] for name in MODELS])
    write_csv(out/'animal_model_scores.csv',['partition','mouse']+MODELS,score_rows)
    panels=final['sensitivity_report']['panels'];sens_rows=[];all_cells=[]
    for name,panel in panels.items():
        sens_rows.append([name,panel['mandatory'],len(panel['contributing_mice']),len(panel['computed_mice_including_subthreshold']),panel['required_coverage_pass']]+(panel['equal_mouse_effect_means'] or [None]*6))
    write_csv(out/'sensitivity_summary.csv',['panel','mandatory','qualified_mice','computed_mice','coverage_pass']+CONTRASTS,sens_rows)
    for mouse in final['mouse_order']:
        cells=b.read(P/'results/final_D/sensitivities'/(mouse+'.json'))
        for name,cell in cells.items():
            if name=='descriptive_metadata':continue
            all_cells.append([mouse,name,cell['retained_epochs'],cell['retained_units'],cell['nominal_unit_bins'],cell['coverage_eligible']]+[None if cell['scores'] is None else cell['scores'][model] for model in MODELS])
    write_csv(out/'all_sensitivity_cells.csv',['mouse','panel','epochs','units','nominal_unit_bins','qualified']+MODELS,all_cells)
    e_null=b.read(P/'results/RETAINED_E_CONTROLS_SUMMARY.json');null_rows=[]
    for label,report in [('E',e_null),('D',final['null_controls'])]:
        for suite,ref in report['stress_references'].items():
            for j,name in enumerate(CONTRASTS):null_rows.append([label,suite,name,ref['mean_effects'][j],ref['q95_effects'][j],report['observed_equal_mouse_effects'][j],ref['observed_minus_reference_mean'][j]])
    write_csv(out/'retained_null_references.csv',['partition','suite','contrast','reference_mean','reference_q95','observed','observed_minus_reference_mean'],null_rows)
    group_rows=[]
    for variable,description in final['descriptive_group_dependence']['groups'].items():
        for value,group in description['groups'].items():
            group_rows.append([variable,value,group['n'],group['leave_group_out_status']]+group['equal_mouse_effect_means']+(group['leave_group_out_means'] or [None]*6))
    write_csv(out/'descriptive_groups.csv',['variable','value','n','leave_group_out_status']+CONTRASTS+['leave_group_out_'+n for n in CONTRASTS],group_rows)
    primary_text='; '.join(f"{name.replace('_minus_',' minus ')} {fmt(stats[name]['mean_nats_per_nominal_unit_bin'])} nats/unit-bin (Holm p={fmt(stats[name]['Holm_adjusted_p'])},95%CI[{fmt(stats[name]['CI95_percentile'][0])},{fmt(stats[name]['CI95_percentile'][1])}])" for name in CONTRASTS[:3])
    interpretation=' '.join(f"For {name}, the frozen statistical component {'met' if stats[name]['positive_statistical_conditions_met'] else 'did not meet'} its positive criteria. This is a conditional/descriptive component, not a validated broad claim." for name in CONTRASTS)
    null_text=md_table(['Partition','Model','Temporal>q95','History>q95','Conditional reference'],[[label,model,report['beyond_baseline_null_guards'][model]['above_temporal_q95'],report['beyond_baseline_null_guards'][model]['above_history_q95'],'FAILED / UNAVAILABLE'] for label,report in [('E',e_null),('D',final['null_controls'])] for model in ['D','C']])
    sens_text=md_table(['Mandatory panel','Qualified mice','Coverage status'],[[name,len(panel['contributing_mice']),'PASS' if panel['required_coverage_pass'] else 'FAIL - retained'] for name,panel in panels.items() if panel['mandatory']])
    caltext=f"All {calibration['verified_fits']}/198required C fits completed across nine mice, with {calibration['initial_intermediate_endpoint_certificates']}initial/intermediate/endpoint certificates. Maximum PG={fmt(calibration['max_PG'])}; maximum AD relative error={fmt(calibration['max_AD_relative'])}; maximum fixed-FD relative error={fmt(calibration['max_fixed_FD_relative'])}. Full coefficients, preprocessing and sensitivity states were sealed before one D assessment. Final D scored all nine mice,12,000nominalunit-bins each (108,000total), with no D fitting or selection."
    replacements={'ABSTRACT_RESULTS':primary_text+'.','CALIBRATION_RESULTS':caltext,'CONTRAST_TABLE':md_table(['Partition','Contrast','Mean gain','Holm p','95%CI','Positive mice'],rows),
        'RESULT_INTERPRETATION':interpretation,'MOUSE_RESULTS':md_table(['Mouse']+[name.replace('_minus_','-') for name in CONTRASTS],[[mouse]+[fmt(stats[name]['mouse_effects'][i]) for name in CONTRASTS] for i,mouse in enumerate(final['mouse_order'])]),
        'NULL_RESULTS':null_text+'\n\nEach retained D suite completed999replicates across all nine mice. Full reference means/quantiles for all six contrasts and both partitions are in retained_null_references.csv. Conditional p-values and Holm2reference values remain unavailable, not nonsignificant. Stress-pass components cannot recover the missing required reference.',
        'SENSITIVITY_RESULTS':sens_text+'\n\nAll computed and subthreshold cells remain in all_sensitivity_cells.csv. The recent-event panel retains the original6/9qualified mice and failed>=8gate; other mandatory coverage conditions are reported without relaxation. All optional anatomy, order, active-status and coordinate panels remain descriptive.',
        'DISCUSSION_RESULTS':primary_text+'. '+interpretation,
        'CONCLUSION_RESULTS':'The held-out descriptive results are: '+primary_text+'. No affected broad confirmatory or validated-temporal conclusion follows.'}
    text=(P/'paper_template.md').read_text(encoding='utf8')
    for key,value in replacements.items():text=text.replace('{{'+key+'}}',value)
    if '{{' in text:raise RuntimeError('Unresolved manuscript result placeholder')
    (out/'Manuscript.md').write_text(text,encoding='utf8',newline='\n')
    attachments=[('A1 Protocol and amendments','Original protocol hash and preserved source freezes; pre-D scope change after E/generator/coverage evidence; all broad confirmation withheld. OWNER_MISSION and PRE_D_STOPPING_RULE_AMENDMENT document prospective authority.'),
        ('A2 Dataset manifest','DANDI000473/0.230417.1502; original25animals,19fixed candidates/10development9final; original asset/ETag/epoch/unit and all exclusions in old EPOCH_UNIT_ALLOCATION and QC journals; no source/animal replacement.'),
        ('A3 Pipeline and environment','Raw timestamp reader -> C-only selected QC/counts -> frozen Cscalers/models -> one D/count/score bundle -> fixed mouse statistics/controls/sensitivities -> saved figures. Original scientific models/solver/AD rules preserved; completeCmanifest contains198fit identities/594certificates.'),
        ('A4 All baselines and animals','All B0-B4,D,C,S,Bstar scores are in the full tables below and animal_model_scores.csv; no favorable baseline or mouse pruning. Bstar=B2 and sharedoffset=B4 are distinct.'),
        ('A5 Holdout audit','C-only admission/scaling/fitting precedes D; Dstates/once marker/exportattempts/sourceandactionjournals preserve one assessment. Trusted raw fullrecord decode is disclosed; no D outcome selects models. No second D or repaired evaluation is authorized.'),
        ('A6 Statistics','Exact inclusive sign tests require conditional fair signs, not arbitrary meanzero. Holm3primary and Holm3guards,10000jointwholemousebootstrap/linear95CI,directionandLOMO all retained; fullprecision CSV accompanies rounded display. Nonsignificance is not equivalence.'),
        ('A7 Falsification and failed reference','Three original999stress suites reported for E/D; conditionalBstar failed at156130rep0and remains unavailable. Diagnostic prefix excluded from originalstatistics; all historicalpartialarrays/failure receipts preserved. No replacementnull or clippedsimulation.'),
        ('A8 QC/leakage/sensitivity','Original C-onlyphysiological screen; exactunit/trialmasks/scalers; fixedparentalignedwindows exclude responsebins; allmandatory sensitivities and failed6of9recent coverage retained. Singleprobe/singlelab/unknownstate andsorting/anatomylimits remain.'),
        ('A9 Reproduction','Saved-only reproduction verifies source/result hashes and renders figures without source access/fits/D rescoring. Original complete scientific entrypoints are consumed; full-executable path is documented but not rerun. Author uses current final saved evidence only.'),
        ('A10 Claim-to-evidence','Held-out descriptive gain supported only by saved9mouse Dscores; conditional statistical evidence by exactregistered summaries under assumptions; Bstar/S comparisons retain guards; originalM6conditional reference failed andcoverageinsufficient. All broadconfirmation/validatedtemporal/NAP/CWP/causal/independentlabclaims withheld.')]
    supplement=['# Supplementary Methods and Reproducibility Attachments','Descriptive post-amendment analysis; complete original confirmation requirements were not met.','## Detailed methods','The full original frozen protocol and main Methods define all mathematical objectives, feature groups, solver/numerical policies, inference and sensitivities. This supplement supplies complete animal scores and all registered panel/reference summaries; machine-readable tables retain every computed cell and fullprecision.']
    for heading,body in attachments:supplement.extend(['## '+heading,body])
    supplement+=['## Full E and D animal model scores',md_table(['Partition','Mouse']+MODELS,[[row[0],row[1]]+[fmt(x) for x in row[2:]] for row in score_rows]),
        '## All six contrast statistics',md_table(['Partition','Contrast','Mean','Raw p','Holm p','CI low','CI high','Positive/n','Min LOMO'],[[r[0],r[1]]+[fmt(v) for v in r[2:7]]+[f'{r[7]}/{r[8]}',fmt(r[9])] for r in rawrows]),
        '## Full retained reference summaries',md_table(['Part','Suite','Contrast','Mean ref','q95 ref','Observed','Obs-ref'],[[r[0],r[1],r[2]]+[fmt(x) for x in r[3:]] for r in null_rows]),
        '## All sensitivity panels',md_table(['Panel','Mandatory','Qualified','Computed','Coverage']+['D-B4','C-B4','D-C','D-Bstar','C-Bstar','D-S'],[[r[0],str(r[1]),r[2],r[3],r[4]]+[fmt(x) for x in r[5:]] for r in sens_rows]),
        '## Anatomical and dependence summaries',md_table(['Variable','Group','n','D-B4','C-B4','D-C'],[[r[0],r[1],r[2]]+[fmt(v) for v in r[4:7]] for r in group_rows]),
        'Full six-contrast group and leave-group-out means, including empty remainders, are retained in descriptive_groups.csv and original FINAL_D_RESULTS.json. Raw coordinate groups do not establish physical-depth equivalence; missing genotype means not decoded, not provider absence. These are not new hypothesis tests.',
        '## Generator failure and numerical history','Original conditional B2 exponential failed on a reproduced feedback path; all old P12M4andP13failures remain unchanged. No mathematical repair, count censoring or different null was used. Current C198fits are a separate finite observed-data numerical result, not evidence that recursive B2simulation is stable.',
        '## Author review requirements','Confirm author/affiliation/contribution/conflict and ethics/data-use statements; audit scientific wording, tables and declared assumptions; approve any submission separately. Internal agent review is not external peer review.',
        '## Reproduction boundary','Run the saved-only PowerShell reproduction supplied with this task. It does not refit C, export raw D, rescore D, generate a new real control, select models or consume a second assessment. Machine-readable CSV/JSON/manifests and preserved old archives contain all per-cell details; no hypothetical model recovery is executed.']
    (out/'Supplement.md').write_text('\n\n'.join(supplement)+'\n',encoding='utf8',newline='\n')
    b.save_matching(out/'CLAIM_AUDIT.json',{'attachments':dict(attachments),'all_affected_broad_claims':'INCONCLUSIVE','conditional_reference':'FAILED_UNAVAILABLE','paper_type':'METHOD_PAPER_DESCRIPTIVE_POST_AMENDMENT','author_submission_review_required':True})
    figures(out,stats,devstats,final['mouse_order'])
    return {'manuscript_complete':True,'scope':'Descriptive paper draft, not original scientific validation','csv_files':6,'all_final_mice':len(final['mouse_order'])}


def figures(out,stats,devstats,mice):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    folder=out/'figures';folder.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(10,4.2))
    for ax,names in zip(axes,[CONTRASTS[:3],CONTRASTS[3:]]):
        for offset,values,color,label in [(-.1,devstats,'#787d89','Development E, n=10'),(.1,stats,'#176b87','Final D descriptive, n=9')]:
            for j,name in enumerate(names):
                item=values[name];mean=item['mean_nats_per_nominal_unit_bin'];lo,hi=item['CI95_percentile']
                ax.plot([lo,hi],[j+offset]*2,color=color,lw=2)
                ax.scatter([mean],[j+offset],color=color,s=28,label=label if j==0 else None,zorder=3)
        ax.axvline(0,color='black',lw=.7);ax.set_yticks(range(3),[n.replace('_minus_',' - ') for n in names]);ax.invert_yaxis()
        ax.set_xlabel('Gain (nats / nominal unit-bin)');ax.legend(fontsize=8)
    fig.suptitle('Descriptive effects; original confirmation gates not met',fontsize=12)
    fig.tight_layout();fig.savefig(folder/'effects.png',dpi=200);fig.savefig(folder/'effects.svg');plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(10,4.5),sharey=True)
    for ax,name in zip(axes,CONTRASTS[:3]):
        ax.scatter(stats[name]['mouse_effects'],np.arange(9),color='#176b87');ax.axvline(0,color='black',lw=.7)
        ax.set_title(name.replace('_minus_',' - '));ax.set_xlabel('Nats / nominal unit-bin');ax.set_yticks(range(9),mice);ax.invert_yaxis()
    fig.suptitle('Every held-out mouse; no confirmatory claim',fontsize=12);fig.tight_layout();fig.savefig(folder/'mice.png',dpi=200);fig.savefig(folder/'mice.svg');plt.close(fig)


if __name__=='__main__':print(json.dumps(prepare()))
