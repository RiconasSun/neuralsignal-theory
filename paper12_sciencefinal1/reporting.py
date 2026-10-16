"""Build paper artifacts from completed, frozen public scalar results only."""
import argparse
import csv
import json
from pathlib import Path
import textwrap
from .trusted_host import ROOT, HERE, E, canonical, digest, inventory, new, read_json, sha

PRIMARY = ('own', 'population', 'stimulus_time', 'combined')
LABELS = ('Own history', 'Other-unit history', 'Stimulus/time', 'Combined features')
VIEWS = ('primary', 'matched16', 'rate_matched', 'boundary20', 'boundary40')


def fmt(x):
    if isinstance(x, bool):
        return 'Yes' if x else 'No'
    return f'{x:.7g}' if isinstance(x, (float, int)) else str(x)


def table(headers, rows):
    return '\n' + '|' + '|'.join(headers) + '|\n|' + '|'.join(['---'] * len(headers)) + '|\n' + ''.join('|' + '|'.join(fmt(x).replace('|', '/') for x in r) + '|\n' for r in rows) + '\n'


def write(path, text):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f: f.write(text.rstrip('\n') + '\n')


def write_csv(path, rows):
    with Path(path).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def figures(out, final, dev):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False,
                         'axes.spines.right': False, 'svg.fonttype': 'none', 'svg.hashsalt': 'P12-FROZEN-FINAL-1', 'savefig.bbox': 'tight'})
    figdir = out / 'figures'; figdir.mkdir()
    def save(fig, name):
        for ext in ('png', 'pdf', 'svg'):
            metadata={'CreationDate': None, 'ModDate': None} if ext=='pdf' else ({'Date': None} if ext=='svg' else None)
            fig.savefig(figdir / (name + '.' + ext), dpi=300, metadata=metadata)
        plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.2), constrained_layout=True)
    for ax, k, label in zip(axes.flat, PRIMARY, LABELS):
        s = final['mouse_statistics']['primary']['statistics'][k]
        ax.axhline(0, color='.65', lw=.7); ax.scatter(range(1, 14), s['mouse_differences'], s=25, c='#28668a')
        ax.errorbar([14.5], [s['mean_CA1_minus_DG']], yerr=[[s['mean_CA1_minus_DG'] - s['CI95'][0]], [s['CI95'][1] - s['mean_CA1_minus_DG']]], fmt='D', color='#b04d31', capsize=4)
        ax.set(title=label + f"; Holm p={s['holm_p']:.4g}", xlabel='Mouse index; diamond = equal-mouse mean', ylabel='CA1 - DG gain (nats/unit-bin)', xticks=[1, 4, 7, 10, 13])
    save(fig, 'figure1_final_mouse_effects')
    fig, ax = plt.subplots(figsize=(7.2, 4), constrained_layout=True)
    for offset, stats, color, label in [(-.12, dev['primary']['statistics'], '#777777', 'Development (exploratory)'), (.12, final['mouse_statistics']['primary']['statistics'], '#28668a', 'Final held-out mice')]:
        means = [stats[k]['mean_CA1_minus_DG'] for k in PRIMARY]; cis = [stats[k]['CI95'] for k in PRIMARY]
        ax.errorbar(np.arange(4) + offset, means, yerr=np.array([[m-c[0], c[1]-m] for m,c in zip(means,cis)]).T, fmt='o', color=color, capsize=3, label=label)
    ax.axhline(0, color='.65', lw=.7); ax.set(xticks=range(4), xticklabels=LABELS, ylabel='CA1 - DG gain (nats/unit-bin)'); ax.legend(frameon=False, fontsize=8)
    save(fig, 'figure2_development_final')
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6), constrained_layout=True)
    for ax,k,label in zip(axes.flat,PRIMARY,LABELS):
        for i,v in enumerate(VIEWS):
            s=final['mouse_statistics'][v]['statistics'][k]; m=s['mean_CA1_minus_DG'];ci=s['CI95']
            ax.errorbar(i,m,yerr=[[m-ci[0]],[ci[1]-m]],fmt='o',color='#28668a',capsize=3)
        ax.axhline(0,color='.65',lw=.7);ax.set(title=label,xticks=range(5),xticklabels=['Primary','16 units','Rate','20 um','40 um'],ylabel='CA1 - DG (nats/unit-bin)');ax.tick_params(axis='x',labelsize=8)
    save(fig,'figure3_sensitivities')
    fig,axes=plt.subplots(2,2,figsize=(7.2,6),constrained_layout=True)
    for ax,k,label in zip(axes.flat,PRIMARY,LABELS):
        for i,suite in enumerate(('T','S','B','O')):
            s=final['null_statistics'][suite+'_'+k];m=s['null_pooled_mean'];ci=s['null_pooled95']
            ax.errorbar(i,m,yerr=[[m-ci[0]],[ci[1]-m]],fmt='o',color='#777777',capsize=3)
            ax.scatter(i,s['observed_pooled_gain'],marker='D',color='#b04d31',s=25)
        ax.set(title=label,xticks=range(4),xticklabels=['Temporal','Condition','Bin','Order'],ylabel='Pooled gain (nats/unit-bin)');ax.tick_params(axis='x',labelsize=8)
    save(fig,'figure4_conditional_nulls')


def build(run_path, output=None):
    run_path=Path(run_path); receipt=read_json(run_path/'run_receipt.json')
    if receipt['mode']!='REAL' or receipt['gate']!='PASS' or not receipt['SCIENTIFIC_EVALUATION_EXECUTED']:
        raise PermissionError('VALID_COMPLETE_ACTUAL_D_RESULTS_REQUIRED')
    if inventory(run_path/'results')!=receipt['result_sha256']:
        raise PermissionError('FINAL_RESULT_HASH')
    out=Path(output).resolve() if output is not None else HERE/'paper'
    if output is not None and not out.is_relative_to(HERE/'work'):
        raise PermissionError('ARTIFACT_REPRODUCTION_WORK_NAMESPACE')
    out.mkdir(parents=True,exist_ok=False)
    final=read_json(run_path/'results/final_statistics.json');dev=read_json(ROOT/'paper12_predictive_v2/results/primary_statistics.json')
    scores=read_json(run_path/'results/scientific_scores.json')['rows']
    probes=read_json(run_path/'results/probe_assessment.json')['rows']
    rates=read_json(run_path/'results/rate_assessment.json')['rows']
    stats=final['mouse_statistics'];primary=stats['primary']['statistics'];nulls=final['null_statistics']
    if stats['primary']['mice']!=13 or len(scores)!=290:raise PermissionError('FINAL_COMPLETENESS')
    prows=[]
    for k,label in zip(PRIMARY,LABELS):
        s=primary[k];prows.append([label,s['mean_CA1_gain'],s['mean_DG_gain'],s['mean_CA1_minus_DG'],f"[{fmt(s['CI95'][0])}, {fmt(s['CI95'][1])}]",s['paired_signflip_p'],s['holm_p']])
    primarytable=table(['Contrast','CA1 gain','DG gain','CA1-DG','95% CI','Exact p','Holm p'],prows)
    summary='; '.join(f"{label}: difference {primary[k]['mean_CA1_minus_DG']:.6g}, 95% CI [{primary[k]['CI95'][0]:.6g}, {primary[k]['CI95'][1]:.6g}], Holm p={primary[k]['holm_p']:.6g}" for k,label in zip(PRIMARY,LABELS))
    validated=[label for k,label in zip(PRIMARY,LABELS) if final['verdicts'][k]['registered_criteria_satisfied']]
    conclusion=('Registered positive evidence was obtained for '+', '.join(validated)+'.') if validated else 'None of the four regional hypotheses met every registered positive-claim condition.'
    classification=table(['Contrast','Registered classification','Holm criterion met','CI excludes zero','Development direction','Sensitivity signs','All LOMO signs','Relevant corrected control'],[[label,final['verdicts'][k]['classification'],final['verdicts'][k]['Holm_pass'],final['verdicts'][k]['CI_excludes_zero'],final['verdicts'][k]['direction_matches_development'],final['verdicts'][k]['sensitivity_signs_consistent'],final['verdicts'][k]['all_LOMO_signs_consistent'],final['verdicts'][k]['relevant_null_pass']] for k,label in zip(PRIMARY,LABELS)])
    nulltable=table(['Suite','Contrast','Observed pooled','Null pooled mean','Pooled Holm','Observed CA1-DG','Regional Holm'],[[s,k,nulls[s+'_'+k]['observed_pooled_gain'],nulls[s+'_'+k]['null_pooled_mean'],nulls[s+'_'+k]['pooled_holm_p'],nulls[s+'_'+k]['observed_CA1_minus_DG'],nulls[s+'_'+k]['regional_holm_p']] for s in ('T','S','B','O') for k in PRIMARY])
    sensitivity=table(['View','Mice']+list(LABELS),[[v,stats[v]['mice']]+[stats[v]['statistics'][k]['mean_CA1_minus_DG'] for k in PRIMARY] for v in VIEWS])
    comparison=table(['Contrast','Development mean','Development Holm','Final mean','Final Holm'],[[label,dev['primary']['statistics'][k]['mean_CA1_minus_DG'],dev['primary']['statistics'][k]['holm_p'],primary[k]['mean_CA1_minus_DG'],primary[k]['holm_p']] for k,label in zip(PRIMARY,LABELS)])
    probetable=table(['Mouse','Contrast','Shared-probe effect','LOPO views','LOPO min','LOPO max','Max absolute shift'],[[r['mouse_id'],r['contrast'],r['shared_difference'],len(r['LOPO_views']),r['LOPO_min'],r['LOPO_max'],r['max_abs_shift']] for r in probes])
    ratetable=table(['Mouse','Matched pairs','Median absolute log ratio','Maximum absolute log ratio','Within log(2)'],[[r['mouse_id'],r['matched_K'],r['median_abs_log_rate_ratio'],r['max_abs_log_rate_ratio'],r['within_original_log2']] for r in rates])
    methods='''## 2. Methods

### 2.1 Data, allocation and recorded exposure

This is a secondary analysis of the frozen curated Allen Visual Coding Neuropixels release. Provider-labeled CA1 and DG units were analyzed during repeated drifting gratings in the functional-connectivity stimulus block. Allen documentation describes released spike-sorted units and quality metrics and cautions that a unit cannot always be equated with an isolated neuron [1]. We did not acquire a new dataset or claim independent anatomical registration.

The original salted mouse allocation is unchanged: 26 mice, 13 development and 13 final. Development A/B data and earlier scores had already been examined, so every development inference remains exploratory. Final mice were calibrated on their C partitions, and the single D assessment used their frozen evaluation masks. The final analysis covers 3,120 trials, 20 nominal 100-ms bins per trial, and 32 primary selected units per subfield, with identical CA1/DG trial membership. The score denominator is the actual scored nominal curated-release unit-bin count. It does not establish uninterrupted native acquisition or lossless raw spike recovery.

Original C-only unit QC requires finite coordinates and valid provider labels, 0.1-100 Hz, active-trial fraction at least 0.1, refractory-interval violations at most 0.01, and frozen timestamp-integrity requirements. Probe 846401834 and invalid exported-rate metadata remain excluded. Unit ranks, cap, minimum trial-per-condition rules and source/trial masks were frozen before evaluation. Upstream provider whole-session sorting is distinct from downstream held-out outcome isolation.

### 2.2 Frozen predictive representations

The six Poisson representations share a 39-column basis: intercept, seven condition indicators, nineteen within-trial bin indicators, linear and quadratic provider trial order, five log(1+count) own-history lags, and five other-unit mean-history lags. Histories reset at each trial and contain only prior bins. The population feature averages the other selected same-subfield units and excludes the target. It does not represent the full recorded population or a causal interaction. Earlier population GLM work motivates predictive history models in a different system [2]; it provides no hippocampal validation here.

O contains intercept and order; N adds condition/bin context; NH adds own history to N; NP adds other-unit history to N; F contains the full basis; OHP removes condition/bin context from F. All share their target-specific C-only means/scales and zero embedding in this basis. The four conditional gains are F-NP (own), F-NH (other population), F-OHP (stimulus/time) and F-O (combined). Predictive log likelihood includes the Poisson log factorial and is divided by actual scored unit-bins. Penalized fitting and unpenalized evaluation are distinct; these regularized predictive contrasts are not likelihood-ratio tests or a unique causal decomposition.

C coefficients were reused without fitting. Ridge remains 0.1 on non-intercept coefficients, bounds [-8,8], and original outward-gradient PG acceptance <=0.001 with independent derivative scaled error <=1e-5. N uses all three frozen seeds 11/23/37 and their coefficient mean, calibrated on C. Other models retain their registered deterministic solver and initialization. The complete C bundle comprises 290 case states, 21,716 original GLM unit attempts, 78 N seed fits, 26 coefficient-mean certificates and 40,104 endpoint certificates. No final coefficient was borrowed from development. All C states, scalers, selected units, masks and sensitivity configurations were sealed before D access.

### 2.3 Statistical unit, inference and robustness

Mouse is the independent unit. We calculate CA1-minus-DG conditional gains within each mouse and average equally across 13 mice. Two-sided paired sign-flip tests enumerate all 8,192 sign assignments. Their validity depends on paired-difference symmetry; repeated units and probes are not extra independent observations. Holm correction covers exactly four primary hypotheses. Whole-mouse paired percentile intervals use 10,000 bootstrap replicates, seed 120214, and 95% endpoints. Intervals are not simultaneous four-hypothesis coverage and are not equivalence intervals.

Required views are primary, first 16 frozen units, C-rate matching, and 20/40-micrometer boundary proxies. Matching pairs available units within absolute log-rate ratio <=log(2), with at least five units per subfield and at least eight paired mice per mandatory view. It does not exactly equalize rates and changes the selected population. Boundary distances are provider-channel label proxies, not independent histology. All leave-one-mouse-out primary means, shared-probe and leave-probe-out views, unavailable probe strata and residual rate mismatch are reported without favorable subset selection.

### 2.4 Four conditional falsification suites

Each mouse/subfield uses 999 fixed-predictor replicates for each suite. T redistributes each trial/unit total across its 20 bins under its C-fitted N rate profile and rebuilds causal histories. S permutes conditions within fixed provider-order blocks; B permutes bin labels within each unchanged trial; O permutes provider order within condition. Trial membership and assignments stay fixed, and no null model is fitted. T is conditional on the nuisance model and observed count totals; label/order controls require exchangeability assumptions. These are conditional stress tests, not exact causal randomization tests or completion of original M5 refit nulls.

All 104 mouse/subfield suites and 103,896 replicate evaluations are retained. Pooled one-sided exceedance p=(1+number(null>=observed))/1000 and centered two-sided regional-reference exceedance are corrected in separate 16-test Holm families. Reported reference ranges describe null replicates, not bootstrap confidence intervals or independent experiments. O remains a mandatory nuisance assessment and cannot rescue a failed relevant control.

### 2.5 Prospective acceptance and governance amendment

Each positive regional claim requires complete data/provenance/numerical/coverage gates; at least eight paired mice in every mandatory view; primary Holm p<=0.05 and a 95% interval excluding zero; the original development effect direction (own positive, the other three negative); matching directions in every required sensitivity mean and all 13 primary leave-one-mouse-out means; and both pooled and regional corrected p<=0.05 for a relevant common suite. Relevant suites are T for own/population, S or B for stimulus/time, and T or S or B for combined. Neither optimizer success, successful software execution nor a favorable unrelated control substitutes for these conditions. The original acceptance document remains byte-identical.

Before D access, the owner prospectively replaced offline Ed25519 signing, separate physical signing equipment, cryptographic one-time entitlement and multi-principal release with an owner-authorized trusted local host. This reduced technical access-control assurance is disclosed rather than retrospectively clearing past security failures. Existing records showed no prior D outcomes exposed to model-selection analysis, but cannot exclude unlogged administrator actions. Trusted custody had previously decoded whole-session vectors before sealing D. There is no independent third-party custodian and no protection against a malicious machine administrator.

Source identities, complete C hashes, exact D metadata, execution identity and original statistical rules were registered before access. Synthetic numerical oracles and a complete 290-state production-schema synthetic D rehearsal used immutable C coefficients without real D counts. An exclusive durable local reservation preceded real source access and prevented accidental reruns; it is not a cryptographically or independently enforced entitlement. The full assessment used authenticated original D envelopes and frozen selection only. No threshold, exclusion, model, hypothesis, solver, seed or control was chosen from D outcomes. Technical failures and earlier stopped attempts are retained. There was no C refit or recurrent-model rescue in this mission.

'''
    text=f'''# Predictive Structure of Neural Population Activity Across Mouse Hippocampal Subfields

Complete scientific manuscript draft following one frozen held-out-mouse assessment. Author identities, affiliations, contributions, conflicts, ethics/data-use declarations and submission approval require author review; draft completion is not journal acceptance or independent peer review.

## Abstract

We asked whether provider-labeled mouse hippocampal CA1 and DG differ in predictive contributions from own spike history, other-unit history, stimulus/time context and combined features. We retained a frozen 26-mouse allocation, separated exploratory development evidence (13 mice) from a prospective held-out assessment (13 additional mice), and reused C-calibrated nested Poisson models without retuning. Mouse-level inference used exact paired sign flips, four-hypothesis Holm correction and 10,000 whole-mouse bootstrap resamples. {summary}. {conclusion} All mandatory sensitivity views and four 999-replicate conditional control suites were retained. Nonsignificance does not establish equivalence. Findings concern observational prediction in one curated release and do not establish causal interactions, independent anatomical localization or a recurrent dynamical regime.

## 1. Introduction

Neural population activity can depend predictively on a unit's recent activity, histories of other sampled units, and known trial context. Distinguishing these fitted contributions from a regional biological mechanism requires held-out prediction, nuisance controls and animal-level uncertainty. Provider subfield labels, selected populations and repeated trials create measurement and sampling constraints even when models predict well. We therefore ask a restricted question: do four predefined predictive gains differ consistently between CA1 and DG in held-out mice from the same curated release?

The original recurrent P12 model competition stopped at numerical gates. A separate tractable GLM track reused audited baselines and adopted nested, causal features. Development comparisons remained exploratory and none passed the four-test Holm threshold. The present evaluation retained all four hypotheses and acceptance conditions despite those outcomes. It contributes a fully reported within-release held-out assessment, including negative and mixed findings, rather than a claim of a new modeling method or a recovered recurrent-model result.

'''+methods+f'''## 3. Results

### 3.1 Execution, numerical evidence and coverage

The assessment validly completed 13 final mice, 26 subfields and all 290 registered model/view states. All five mandatory views retained 13 paired mice. All 104 conditional null cases completed 999 replicates, and no model was fitted during evaluation. The immutable C seal passed the original numerical and provenance validator before and after execution. Synthetic execution was reported separately and supplies no biological observations.

### 3.2 Primary held-out regional contrasts

{primarytable}

All values are nats per actual nominal curated-release unit-bin. Positive differences favor larger conditional predictive gain in CA1. The table reports every hypothesis, both p values and mouse uncertainty. Failure of a hypothesis does not establish equal physiology or absence of a biological effect.

### 3.3 Registered verdict and development comparison

{classification}

{conclusion} A primary statistical threshold alone is insufficient when direction, sensitivity, leave-one-mouse-out or relevant corrected controls fail.

All four final point estimates were negative, indicating larger mean fitted gains in DG in this cohort. Own history reversed the frozen positive development direction; its interval included zero and its sensitivity/leave-one-mouse-out signs were not consistently in that direction. Other-unit history and stimulus/time retained negative development directions, negative means in every mandatory sensitivity and every leave-one-mouse-out primary analysis. Their nominal intervals excluded zero, but their four-test Holm p values were 0.06347656 and 0.06445313. They therefore remain unconfirmed under the original gate. Combined features also retained its negative direction and robust signs, but its adjusted p was 0.1411133.

The combined-feature percentile interval excluded zero although its exact two-sided unadjusted p was 0.07055664. Percentile bootstrap intervals and exact sign-flip tests have different finite-sample calibrations; neither was substituted for the other. The registered rule required both the corrected test and the interval condition, and was applied unchanged. These descriptive intervals are not simultaneous four-comparison coverage.

{comparison}

Development evidence remains exploratory because data and scores were previously examined. Final mice are distinct animals within the same recording release, not independent-laboratory replication. Development and final results were not pooled to select or rescue a claim.

### 3.4 Sensitivity and conditional-control results

{sensitivity}

The supplement gives all view intervals, per-mouse differences, leave-one-mouse-out means, probe strata and C-rate residuals. Sensitivities are descriptive checks of the frozen claim, not a search for a replacement significant subset.

{nulltable}

Every T/S/B/O result remains reported, including unfavorable and nonsignificant references. Null mean comparisons and corrected exceedance tests answer different questions; none establishes a causal contribution. Full replicate distributions and every animal/subfield control are included in the saved evidence.

All four contrasts passed at least one originally relevant joint pooled-and-regional corrected control: T for own and other-unit history; B for stimulus/time; T and B for combined (both corrected p values 0.016 in each passing suite). This did not rescue any primary Holm failure. Condition-label S controls had pooled adjusted p=0.016 for stimulus/time and combined but regional adjusted p=0.09, so did not meet the required joint condition. Temporal T did not pass for stimulus/time, and order O did not pass the joint condition for any contrast. Bin B did not pass the pooled condition for other-unit history. These mixed nuisance-control outcomes remain explicit rather than selecting a universally favorable reference.

## 4. Discussion

{conclusion} The primary estimates, their uncertainty and the individual acceptance failures define the permitted regional interpretation. In particular, a nonsignificant comparison cannot be turned into proof of equivalence, and a significant fitted contrast cannot bypass a failed robustness condition. Positive within-subfield predictive gains and regional differences are distinct estimands. The study's scope is fixed conditional Poisson prediction from a selected subfield population and known context, not information capacity or a comprehensive feature hierarchy.

The consistent negative other-unit and stimulus/time point estimates across development and final mice are a descriptive pattern, not confirmation under Holm correction. Own-history direction reversal and wide mouse-level uncertainty argue against a single stable regional ordering across predictive feature classes. Both subfields had positive average gains for all four fitted contrasts, yet this does not establish a reproducible CA1-versus-DG difference. The final assessment therefore supports a cautious mixed-evidence account: audited conditional prediction in both labeled subfields, directional patterns for some contrasts, and no regional hypothesis validated by every prospective criterion.

Histories may predict activity through shared drive, stimulus modulation, behavioral state, heterogeneous rates, recording or sorting artifacts, and omitted variables. Regularization and correlated covariates affect nested fitted gains. Provider-channel boundary proxies and probe sampling leave anatomical uncertainty. Rate matching retains residual differences and modifies the selected population. Multiple units, trials and probes do not expand the independent animal count. Conditional temporal redistribution preserves trial/unit totals and can retain history gain through count heterogeneity; nuisance-model and exchangeability assumptions remain limitations even for corrected positive controls.

This is a within-release animal holdout, not an independent laboratory or independently acquired cohort. Whole-session upstream processing limits acquisition-level naivety. The trusted-host governance amendment weakened technical separation while retaining frozen science and explicit recorded access history; local reservations do not prove administrator-resistant one-time access. All original prerelease and numerical failures remain visible. These qualifications constrain reproducibility and interpretation without changing the original statistical thresholds.

Original recurrent M4 failures were not repaired: the CA1 Continuous dimension-4, ridge-0.001, seed-11 endpoint had PG about 0.693 against 0.001. Its fixed finite-difference gradient check failed, and a later diagnosis identified finite-difference instability without establishing convergence. All three bounded optimizer/conditioning candidates remained nonconvergent. Tractable GLM evaluation does not retrospectively pass M4, original M5/M6, NAP or CWP. No causal mechanism, human validation or independent histological confirmation is claimed.

## 5. Conclusion

{conclusion} The complete held-out effect table and registered decision matrix are the scientific outcome. Negative, mixed and inconclusive conditions remain part of the paper. A separate independently acquired/anatomically verified cohort and causal experiments would address different future questions; this mission performs no additional final assessment or retuning.

## Data and code availability

Original provider data are described by AllenSDK [1]. Exact source receipts, animal/trial/unit locks, calibration manifests, source hashes and all public scalar results accompany the repository. Protected count arrays, decryption keys and copied fitted-state bundles are not redistributed in Git. The public PowerShell command recomputes frozen statistics and validates saved hashes without opening neural arrays or rerunning D. A new checkout requires only public saved scalar evidence for that reproduction; it cannot silently substitute synthetic data for held-out observations.

## Reproducibility and author-review requirements

The A1-A10 supplement records protocol, dataset, pipeline, baselines, holdout audit, statistics, controls, leakage/QC, limitations and saved-only reproduction. Actual execution and saved reproduction are different evidence classes. The manuscript is complete as a draft when its artifacts pass rendering/content checks. The project owner must confirm author order/affiliations, actual contributions, conflicts/funding, provider data-use and any applicable institutional ethics determination before submission. No ethics identifier, trial registration, external custodian, affiliation or independent peer-review approval is invented.

## References

[1] Allen Institute. Visual Coding - Neuropixels, AllenSDK documentation. https://allensdk.readthedocs.io/en/latest/visual_coding_neuropixels.html (accessed 2026-10-15).

[2] Pillow JW, Shlens J, Paninski L, Sher A, Litke AM, Chichilnisky EJ, Simoncelli EP. Spatio-temporal correlations and visual signalling in a complete neuronal population. Nature 454, 995-999 (2008). doi:10.1038/nature07140. https://www.columbia.edu/cu/neurotheory/pdfs/Pillow_et_al_2008.pdf
'''
    write(out/'MANUSCRIPT.md',text)
    animal=[]
    for k in PRIMARY:
        for i,mouse in enumerate(stats['primary']['mouse_ids']):
            animal.append({'mouse_id':mouse,'contrast':k,'CA1_minus_DG':primary[k]['mouse_differences'][i],'leave_one_mouse_out_mean':primary[k]['leave_one_mouse_out_means'][i]})
    allviews=[]
    for v,stat in stats.items():
        for k,s in stat.get('statistics',{}).items():
            for i,mouse in enumerate(stat['mouse_ids']):allviews.append({'view':v,'mouse_id':mouse,'contrast':k,'CA1_minus_DG':s['mouse_differences'][i],'view_mean':s['mean_CA1_minus_DG'],'view_CI_low':s['CI95'][0],'view_CI_high':s['CI95'][1]})
    controlrows=[]
    for p in sorted((run_path/'results').glob('null_*.json')):
        z=read_json(p)
        for i,k in enumerate(PRIMARY):
            controlrows.append({'mouse_id':z['mouse_id'],'region':z['region'],'suite':z['suite'],'contrast':k,'observed':z['observed'][i],'null_mean':sum(r[i] for r in z['gains'])/999,'replicates':999})
    write_csv(out/'animal_primary_and_LOMO.csv',animal);write_csv(out/'all_mouse_view_differences.csv',allviews);write_csv(out/'all_animal_controls.csv',controlrows)
    write_csv(out/'all_mouse_probe_assessment.csv',[{k:(json.dumps(v) if isinstance(v,list) else v) for k,v in r.items()} for r in probes])
    write_csv(out/'all_C_rate_matching.csv',[{k:(json.dumps(v) if isinstance(v,list) else v) for k,v in r.items()} for r in rates])
    scalarrows=[]
    for r in scores:
        base={k:r[k] for k in ('mouse_id','session_id','region','view','case','D_trials','units','nominal_unit_bins')}
        base.update({'score_'+k:v for k,v in r['scores'].items()});base.update({'gain_'+k:v for k,v in r['gains'].items()});scalarrows.append(base)
    write_csv(out/'all_290_case_scores.csv',scalarrows)
    audit=[]
    sections=[
        ('A1 Frozen protocol', (ROOT/'paper12_predictive_v2/PROTOCOL.md').read_text(encoding='utf-8')+'\n\n'+(ROOT/'paper12_predictive_v2/FINAL_VALIDATION_PLAN.md').read_text(encoding='utf-8')+'\n\nThe new owner trusted-host amendment changes governance only; historical authorization restrictions above remain historical, not current permission. See mission human_authorization.txt and registration.json.'),
        ('A2 Dataset manifest',table(['Final mouse','Session','D trials','Primary CA1 units','Primary DG units'],[[m,next(r['session_id'] for r in scores if r['mouse_id']==m),next(r['D_trials'] for r in scores if r['mouse_id']==m),32,32] for m in final['cohort']])+'\nExact 26-mouse allocation and unit/trial metadata hashes are recorded in preflight_receipt.json. No reshuffling, replenishment or new acquisition.'),
        ('A3 Full pipeline',methods+'\n\nExecution source hashes and software versions are in the registration/preflight/run receipts. Original scientific evaluator and mathematical source bytes remain unchanged.'),
        ('A4 Baselines and all case results',primarytable+comparison+'\nAll original 1,638 M3 and 78 development shared-offset fits remain in paper12_predictive_v2/supplements/all_old_baseline_fits.csv and reuse evidence. Final coefficients were separately calibrated on C. The full 290-case score/denominator/gain table is all_290_case_scores.csv. No unrun final legacy-baseline competition is claimed.'),
        ('A5 Holdout and governance audit','One actual D assessment after scientific preflight; no result-based rerun. Exact exposure/custody limitations are in Methods 2.5 and registration.json. Original failures remain immutable. Trusted-local-host permission is prospective and does not clear failed older security gates. No independently enforced cryptographic entitlement or third-party custodian exists in this workflow.\n\n'+table(['Field','Value'],[['Real evaluation',True],['Final mice',13],['New C fits',0],['Run receipt SHA256',sha(run_path/'run_receipt.json')],['Frozen protocol SHA256',sha(ROOT/'paper12_predictive_v2/FINAL_VALIDATION_PLAN.md')]])),
        ('A6 Complete mouse-level statistics',primarytable+classification+sensitivity+'\n'+table(['Mouse','Contrast','CA1-DG','LOMO mean'],[[r['mouse_id'],r['contrast'],r['CA1_minus_DG'],r['leave_one_mouse_out_mean']] for r in animal])+'\nAll group-eligible view mouse differences and bootstrap intervals: all_mouse_view_differences.csv. All 8192 sign assignments and 10000 bootstrap replicates use unchanged code; saved result JSON includes the exact effect vectors and LOMO means.\n\n### Per-mouse probe dependence\n\n'+probetable+'\nAll available shared/leave-probe effects, including views without enough mice for group inference: all_mouse_probe_assessment.csv and saved probe_assessment.json. Missing strata are reported as None, not imputed.\n\n### C-only rate matching residuals\n\n'+ratetable+'\nEvery matched pair log-ratio is retained in all_C_rate_matching.csv. These are calibration rates only, not D-derived QC or rate-based exclusions.'),
        ('A7 All four falsification suites',nulltable+'\n'+table(['Mouse','Region','Suite','Contrast','Observed','Null mean'],[[r['mouse_id'],r['region'],r['suite'],r['contrast'],r['observed'],r['null_mean']] for r in controlrows])+'\nAll104 complete999x4 replicate arrays remain in saved results. No null fitting, selected suite replacement or trial repartitioning. These conditional reference distributions have nuisance/exchangeability assumptions.'),
        ('A8 QC and leakage audit','The exact immutable C bundle and failed partial bundle were hash-checked; the original complete C provenance/numerical validator passed. C-only QC, unit/scaler/trial selections and source masks were not recalculated using D. All required views retain13 mice; no D-derived QC, normalization or exclusions. Synthetic transport tests used artificial counts, authenticated envelopes, exact masks, ordered-unit canaries, tamper/wrong-key negatives, and no real source. Existing exposure records are evidence of recorded isolation, not proof against unlogged administrator activity. Whole-session upstream sorting remains a limitation.'),
        ('A9 Failures, limitations and claim audit',classification+'\nAll original scientific M4 and prerelease failures, finite-difference diagnosis, three nonconvergent conditioning candidates, partial seal/import failure and later repairs remain immutable. This mission does not retroactively validate them. Development is exploratory, anatomy is provider-proxy based, selected-unit populations and rate residuals remain confounds, and controls are conditional. Scientific claim status follows every original gate, with no equivalence/causal/human/NAP/CWP/independent-laboratory claim. Author declarations require owner review before submission.'),
        ('A10 Saved-only reproduction','From repository root:\n\n```powershell\n& ./paper12_sciencefinal1/reproduce_all.ps1\n```\n\nThis runs synthetic numerical/transport regressions, verifies final scalar-result hashes, reaggregates all primary/view statistics and both complete null families through the frozen implementation, and regenerates manuscript/figures/PDFs in a fresh ignored work directory. It performs zero fits and opens no raw counts, C states or D key/cipher. It is not permission or a method for repeating the one-shot D assessment. Original execution provenance is certified by saved preflight/run receipts; environment identity is recorded separately. Core scalar-only checks are also available through reproduce.ps1. Artifact generation requires the recorded Matplotlib environment, bundled ReportLab/PyPDF runtime and Windows Arial fonts; missing dependencies fail explicitly, without synthetic substitution.')]
    supplement='# Supplementary information\n\nPredictive Structure of Neural Population Activity Across Mouse Hippocampal Subfields\n\nComplete A1-A10; all reported animal and conditional-control outcomes.\n\n'
    for i,(name,body) in enumerate(sections,1):
        supplement+='## '+name+'\n\n'+body+'\n\n';audit.append({'attachment':f'A{i}','title':name,'status':'COMPLETE_AS_DRAFT','evidence': ['registration.json','preflight_receipt.json','run_receipt.json','final_statistics.json','all_290_case_scores.csv']})
    write(out/'SUPPLEMENT.md',supplement)
    new(out/'A1_A10_claim_audit.json',{'attachments':audit,'four_claim_decisions':final['verdicts'],'author_review_required':['author identities/order/affiliations','contributions','funding and conflicts','data-use and ethics determination','submission approval'],'scope':'Complete manuscript draft, not journal acceptance or independent peer review'})
    figures(out,final,dev)
    new(out/'paper_manifest.json',{'input_run_receipt_sha256':sha(run_path/'run_receipt.json'),'sha256':inventory(out),'MANUSCRIPT_COMPLETE':True,'meaning':'Complete generated scientific draft; PDF rendering and author submission review recorded separately','positive_claims':validated})
    return {'MANUSCRIPT_COMPLETE':True,'validated_contrasts':validated,'files':len(inventory(out))}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--output-newdir');a=p.parse_args();print(json.dumps(build(a.run,a.output_newdir)))
