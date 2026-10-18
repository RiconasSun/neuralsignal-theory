"""All registered interpretations from saved results; no new tests/predictions."""
from paper15_final1.source import P,read
from paper15_final1.statistics import CONTRASTS
from paper15_final1.final_statistics import MANDATORY_CASES
from paper15_final1.report import write_csv


def number(value):return 'unavailable' if value is None else format(value,'.8g')


def append_interpretation():
    assert read(P/'D_BATCH_CLAIM.json')['status']=='COMPLETE_REGISTERED_DESCRIPTIVE_D_BATCH'
    stats=read(P/'results/D_STATISTICS.json');sens=read(P/'results/D_SENSITIVITY_SUMMARY.json')
    controls=read(P/'results/D_CONTROL_SUMMARY.json');verdicts=read(P/'results/D_SCIENTIFIC_VERDICTS.json')
    development=read(P/'results/FINAL_DELIVERY.json')['DEVELOPMENT_FINAL_CONSISTENCY']
    labels={'B4-B1':'combined spike history beyond the strong measured nuisance baseline',
            'B4-B3':'own history conditional on other-unit history and measured nuisances',
            'B4-B2':'other-unit history conditional on own history and measured nuisances',
            'D-B4':'the selected discrete predictive model beyond the combined GLM',
            'C-B4':'the selected continuous predictive model beyond the combined GLM',
            'D-S':'the selected discrete model compared with the larger static mixture'}
    lines=['','## Scientific interpretation of the frozen assessment','',
           'The following interpretation covers every registered contrast. Displayed numbers are rounded; JSON and CSV retain full precision. All available comparisons remain DESCRIPTIVE ONLY in the prospectively fixed six-mouse fallback. The independent Final animals provide held-out predictive observations,not a validated cross-animal or independent-laboratory replication. No extra hypothesis or inferential test is introduced here.','']
    distributions=[]
    for c in CONTRASTS:
        r=stats[c];mean=r.get('equal_mouse_mean');ci=r.get('CI95');positive=mean is not None and mean>0
        if mean is None:
            lines.append(f"{c} ({labels[c]}) is unavailable at the original minimum paired-mouse gate; no absent effect or equivalence is inferred.");continue
        ci_text='['+', '.join(number(v) for v in ci)+']'
        p_label='one-sided raw p' if c=='B4-B1' else 'two-sided raw p'
        adjusted='' if c=='B4-B1' else f", Holm5 p={number(r['Holm5_adjusted_p'])}"
        lines.append(f"{c} examines {labels[c]}. The equal-mouse gain is {number(mean)} nats/nominal curated-release unit-bin,95% whole-mouse interval {ci_text}, {p_label}={number(r['paired_sign_flip_p'])}{adjusted}; {r['positive_mice']}/{r['n_mice']} mouse gains are positive. The mean is {'a positive descriptive predictive increment' if positive else 'not a positive descriptive predictive increment'} in this cohort. Its complete registered positive-claim conjunction is not satisfied; neither a favorable mean nor a nonsignificant comparison establishes a causal attribution,model equivalence or absence of biology.")
        effects=[m['effect'] for m in r['mouse_effects']]
        distributions.append(dict(contrast=c,n_mice=r['n_mice'],minimum=min(effects),maximum=max(effects),median=r['median'],IQR=r['IQR'],SD=r['SD'],
            positive_mice=r['positive_mice'],lab_means=r['lab_means'],equal_lab_mean=r['equal_lab_mean'],
            leave_one_mouse_out_means=r['leave_one_mouse_out_means'],leave_one_lab_out_means=r['leave_one_lab_out_means'],
            lab_block_bootstrap_CI95=r['lab_block_bootstrap_CI95'],CI_width=r['CI_width']))
        lines.append(f"Animal heterogeneity for {c}: range [{number(min(effects))}, {number(max(effects))}],median {number(r['median'])},SD {number(r['SD'])}; the equal-lab diagnostic mean is {number(r['equal_lab_mean'])}. Individual mouse effects,all leave-one-mouse/lab means,lab means and the four-lab block-bootstrap diagnostic are retained in FINAL_DISTRIBUTION_AND_LAB_DIAGNOSTICS.csv and the exact JSON. These dependence diagnostics do not increase the independent animal or lab denominator.")
        if c in ('B4-B1','B4-B3','B4-B2'):
            failures=[f"{case}(n={sens[case][c]['n_mice']},mean={number(sens[case][c].get('equal_mouse_mean'))})" for case in MANDATORY_CASES
                      if not sens[case][c]['minimum6_coverage'] or sens[case][c].get('equal_mouse_mean',0)<=0]
            lines.append(f"Mandatory baseline sensitivity failures/unavailable panels for {c}: {', '.join(failures) if failures else 'none under the original minimum-six/positive-mean rule'}. This reports the registered case conditions; it does not upgrade the six-mouse verdict or provide unperformed D/C/S sensitivity-refit robustness.")
        for suite in verdicts[c]['required_reference_suites']:
            panel=controls[c][suite]
            lines.append(f"{c}/{suite}: {panel['n_mice']} paired mice,status {panel['status']},above-reference-median mice {panel.get('mice_above_reference_median','unavailable')},mean degradation {number(panel.get('mean_degradation'))},reference p={number(panel['p_reference'])},Holm4 reference p={number(panel['Holm4_reference_p'])}; the original descriptive disruption gate is {bool(panel.get('descriptive_disruption_gate',False))}. This is a finite destructive-reference diagnostic,not an exact population/conditional null or causal mechanism test.")
        old=development[c]
        lines.append(f"Development-to-Final comparison for {c}: frozen Development mean {number(old['Development_mean'])} versus Final mean {number(old['Final_mean'])}. These are separately reported cohorts; no pooled estimate,new cross-cohort p-value,reselection or retrospective Development PASS is inferred.")
        lines.append('')
    write_csv('FINAL_DISTRIBUTION_AND_LAB_DIAGNOSTICS.csv',distributions)
    lines+=['The full case panel separates S01 five-unit,S02 twelve-unit and S03 twenty-unit populations; S04 uses100-ms bins; S05 shorter history; S06 stricter C physiology; S07 C-rate-defined thinning with independent role-local streams; S08/S09 saturation-mask dilation; S10 higher-order trial/session drift covariates; and S11 anatomy boundary proxies. Only four mice can supply S03 twenty-unit states. All outcomes and coverage failures remain in their original panels;100-ms gains are not interchangeable with50-ms gains. These checks characterize prediction conditional on measured wheel/task nuisances and available release units,not all movement,recording artifacts or anatomy uncertainty.','',
        'The N3 B4-likelihood wheel diagnostic is fully reported but is not a D/C wheel-null result. Aggregate N4 has only three eligible mice and remains unavailable at the original six-mouse minimum. Consequently no persistent temporal-state interpretation is established,including from any apparent D-versus-S difference. Static S has K=4 and discrete D has K=3 as frozen on Development B; neither is substituted or retuned using Final scores.','',
        'Author review must assess source/licence attribution,observational and sorting/anatomy limitations,conditional test assumptions,animal/laboratory heterogeneity,and the distinction between descriptive predictive evidence and the complete unsatisfied confirmation criteria. All broad causal,motor-command,all-movement-independent,discrete-neural-atom,CWP/NAP,human/BCI and independent-laboratory validation claims remain outside scope.']
    path=P/'FINAL_SCIENTIFIC_REPORT.md';text=path.read_text(encoding='utf8')
    assert '## Scientific interpretation of the frozen assessment' not in text
    path.write_text(text+'\n'.join(lines)+'\n',encoding='utf8')


if __name__=='__main__':append_interpretation()
