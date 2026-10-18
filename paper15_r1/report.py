"""Saved-result Development report and truthful future-Final handoff, no fitting."""
from .source import load_json
import csv
import json
from .source import P,R,dump
from .training import admitted,sha
from .ledger import snapshot
from .source import roster


def read(path):return load_json(path.read_text(encoding='utf8'))


def table(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def corrective_status():
    native=read(P/'results/FULL_A_SOURCE_REVALIDATION.json');wheel=read(P/'results/EXACT_WHEEL_INDEX_VERIFICATION.json')
    ledger=snapshot();registration=read(R/'ops/evidence/2026-10-17/p15-dev-exact-native-repair-r1/PRESERVATION_REGISTRATION.json')
    assert registration['original_fits_verified']==359 and registration['historical_complete']==358
    assert sha(R/'paper15_dev/STOP_ARCHIVE_FREEZE.json')==registration['historical_package_freeze_sha256']
    return dict(EXACT_NATIVE_REPAIR_PASS=native['EXACT_NATIVE_REPAIR_PASS'],NATIVE_TIME_BITWISE_VERIFICATION=native['NATIVE_TIME_BITWISE_VERIFICATION'],
        STRICT_PAST_WHEEL_GATE=wheel['STRICT_PAST_WHEEL_GATE'],FULL_A_SOURCE_REVALIDATION=native['FULL_A_SOURCE_REVALIDATION'],
        ORIGINAL_ATTEMPTS_PRESERVED=True,NEW_MAIN_ATTEMPTS=ledger['NEW_MAIN_ATTEMPTS'],NEW_SENSITIVITY_ATTEMPTS=ledger['NEW_SENSITIVITY_ATTEMPTS'],
        TOTAL_CUMULATIVE_ATTEMPTS=ledger['TOTAL_CUMULATIVE_ATTEMPTS'],HISTORICAL_STARTED_ATTEMPTS=359,
        HISTORICAL_COMPLETED_ROUNDED_INPUT_NUMERICAL_PASS=358,HISTORICAL_INTERRUPTED_WITHOUT_ENDPOINT=1,
        HISTORICAL_NEVER_STARTED=251,CORRECTIVE_BUDGET_SEPARATELY_AUTHORIZED=True,
        HISTORICAL_VERDICT='STOP_SOURCE_IMPLEMENTATION_DEFECT; no retroactive scientific PASS',
        HISTORICAL_COEFFICIENTS_REUSED=False,CORRECTIVE_EXECUTION_LEDGER=ledger)


def main():
    m2=read(P/'results/M2_PHYSIOLOGY_GATE.json');metadata=read(P/'results/METADATA_QC.json')
    qc={x['subject']:x for x in m2['subjects']}
    cohort=[]
    for row in metadata:
        state=read(P/'metadata'/(row['subject']+'_task.json'))
        actual=qc.get(row['subject'],{})
        cohort.append(dict(subject=row['subject'],lab=row['lab'],allocation=row['allocation'],eid=row['eid'],pid=row['pid'],
            native_trials=row['original_native_trials'],provider_good_MOp=row['source_mapping']['native_MOp_provider_good'],
            valid_epochs=json.dumps(row['structural_eligible_epochs'],sort_keys=True),
            development_physiology_admitted=actual.get('admitted','NOT_AUTHORIZED_FINAL'),qualified_units=actual.get('qualified_units','NOT_COMPUTED'),
            exclusion=actual.get('reason'),wheel_coverage=row['wheel_coverage'],
            source_clock_domain=json.dumps(row['recording_sync_support']),neural_access=row['neural_arrays_accessed'] if row['allocation']!='DEVELOPMENT' else actual.get('neural_access',False)))
    reserved=[row for row in roster() if row['allocation']=='FINAL_RESERVED'];assert len(reserved)==8
    for row in reserved:
        cohort.append(dict(subject=row['subject'],lab=row['lab'],allocation=row['allocation'],eid=row['eid'],pid=row['pid'],
            native_trials='NOT_REASSESSED_R1',provider_good_MOp='NOT_REASSESSED_R1',valid_epochs='NOT_REASSESSED_R1',
            development_physiology_admitted='NOT_AUTHORIZED_FINAL',qualified_units='NOT_COMPUTED',exclusion=None,
            wheel_coverage='NOT_AUTHORIZED_FINAL',source_clock_domain='NOT_REASSESSED_R1',neural_access=False))
    assert len(cohort)==20 and len({row['subject'] for row in cohort})==20
    table(P/'tables/COHORT_FINAL_NATIVE_QC.csv',cohort)
    selected=read(P/'SELECTION_FREEZE.json');candidates=read(P/'results/B_CANDIDATE_SCORES.json')
    fits=[]
    for subject in admitted():
        for path in sorted((P/'fits'/subject).glob('*.json')):
            row=read(path);check=row.get('independent',{})
            fits.append(dict(subject=subject,configuration=row['configuration']['id'],family=row['configuration']['family'],
                status=row['status'],PG=row.get('PG'),AD_scaled=check.get('AD_max_scaled'),
                FD_max_scaled=max((f['max_scaled'] for f in check.get('FD',[])),default=None),
                optimizer_success=row.get('optimizer_success'),termination=row.get('termination',row.get('error')),
                iterations=row.get('iterations'),calls=row.get('optimizer_objective_calls'),wall_seconds=row.get('wall_seconds'),
                journal_sha256=sha(path)))
    table(P/'tables/MAIN_ATTEMPTS.csv',fits)
    choice=[]
    for row in candidates:
        choice.append(dict(configuration=row['id'],family=row['configurations'][0]['family'],available=row['available'],
            equal_mouse_B_LL_unit_bin=row.get('equal_mouse_LL_per_unit_bin'),nominal_parameters=row['nominal_parameters'],
            selected=row['id'] in selected['selected'].values()))
    table(P/'tables/B_SELECTION.csv',choice)
    stats=read(P/'results/E_STATISTICS.json');effects=[]
    for key,row in stats.items():
        for m in row.get('mouse_effects',[]):effects.append(dict(contrast=key,**m))
    table(P/'tables/E_MOUSE_EFFECTS.csv',effects)
    summaries=[]
    for key,row in stats.items():
        summaries.append(dict(contrast=key,status=row['status'],mice=row.get('n_mice'),mean=row.get('equal_mouse_mean'),
            CI95=json.dumps(row.get('CI95')),raw_p=row['paired_sign_flip_p'],Holm5_p=row.get('Holm5_adjusted_p'),validated=False))
    table(P/'tables/E_CONTRASTS.csv',summaries)
    case_rows=[]
    for cid,panels in read(P/'results/E_SENSITIVITY_SUMMARY.json').items():
        for key,row in panels.items():case_rows.append(dict(case=cid,contrast=key,status=row['status'],mandatory=row['mandatory'],
            mice=row['n_mice'],mean=row.get('equal_mouse_mean'),CI95=json.dumps(row.get('CI95')),validated=False))
    table(P/'tables/E_SENSITIVITIES.csv',case_rows)
    control_rows=[]
    for key,panels in read(P/'results/E_CONTROL_SUMMARY.json').items():
        for suite,row in panels.items():control_rows.append(dict(contrast=key,suite=suite,status=row['status'],mice=row['n_mice'],
            p_reference=row['p_reference'],Holm4_reference_p=row['Holm4_reference_p'],
            mean_degradation=row.get('mean_degradation'),descriptive_gate=row.get('descriptive_disruption_gate'),
            statistic=row.get('statistic','Registered predictive gain'),exact_mechanistic_null=False))
    table(P/'tables/E_CONTROLS.csv',control_rows)
    dynamic=read(P/'results/DYNAMIC_ATTEMPTS_COMPLETE.json');baseline=read(P/'results/BASELINE_ATTEMPTS_COMPLETE.json')
    complete=read(P/'E_BATCH_CLAIM.json')['status']=='COMPLETE_EXPLORATORY_E_BATCH'
    dynamic_available=all(selected['selected'][f] is not None for f in ['D','C','S'])
    production=read(P/'PRODUCTION_GATE.json')['PRODUCTION_NUMERICAL_PASS']
    prerequisite=bool(m2['M2_SOURCE_QC_PASS'] and m2['development_eligible_mice']>=8 and m2['development_labs']>=4 and production
        and baseline['PRIMARY_BASELINE_NUMERICAL_GATE'] and baseline['attempted']==baseline['completed']==13*len(admitted())
        and dynamic['attempted']==dynamic['completed']==48*len(admitted()) and selected['subjects']==admitted()
        and selected['selected']['B1'] is not None and selected['selected']['B4'] is not None)
    status=dict(M2_SOURCE_QC_PASS=m2['M2_SOURCE_QC_PASS'],DEVELOPMENT_ELIGIBLE_MICE=m2['development_eligible_mice'],DEVELOPMENT_LABS=m2['development_labs'],
        FINAL_METADATA_READY=False,FINAL_RESERVED_IDENTITIES_PRESERVED=len(reserved),
        FINAL_METADATA_SCOPE='Eight original reserved identities retained; no corrected Final packet or new Final revalidation in R1; historical metadata remains preserved, actual C/D and physiology unauthorized',
        PRODUCTION_NUMERICAL_PASS=production,M3_BASELINE_PASS=baseline['PRIMARY_BASELINE_NUMERICAL_GATE'],
        M4_DYNAMIC_PASS=dynamic_available,M4_ALL_ATTEMPTS_NUMERICAL_PASS=dynamic['numerical_pass']==dynamic['attempted'],M5_DEVELOPMENT_COMPLETE=complete,
        PRIMARY_DEVELOPMENT_EFFECT=stats['B4-B1'],SECONDARY_DEVELOPMENT_EFFECTS={k:v for k,v in stats.items() if k!='B4-B1'},
        FROZEN_MODEL_SELECTION=selected['selected'],SENSITIVITY_IMPLEMENTATION_STATUS='All11 definitions/registered fixed-lambda fits and E panels preserved, including unavailable coverage',
        FINAL_C_ACCESS=False,FINAL_D_ACCESS=False,PROMPT_4_READY=bool(prerequisite and complete and dynamic_available),
        PROMPT_4_READINESS_SCOPE='Development handoff only; no assertion that actual Final C physiology, wheel support, numerics, assumptions or pre-D review have passed',
        SCIENTIFIC_VERDICT='EXPLORATORY_DEVELOPMENT_ONLY_NO_HELDOUT_VALIDATION',BUG_COUNT=0,WARN_COUNT=0,
        GIT_COMMIT='Recorded in external verified closure receipt to avoid self-referential commit hash',REMOTE_VERIFICATION='Recorded after reviewed commit/readback')
    status.update(corrective_status())
    status.update(CORRECTED_ELIGIBLE_DEVELOPMENT_MICE=m2['development_eligible_mice'],CORRECTED_DEVELOPMENT_LABS=m2['development_labs'],
        B_SELECTION_FROZEN=bool(selected['subjects']==admitted() and selected['candidates_sha256']==sha(P/'results/B_CANDIDATE_SCORES.json')),DEVELOPMENT_E_COMPLETE=complete,
        FALSIFICATION_RESULTS=dict(sensitivities=read(P/'results/E_SENSITIVITY_SUMMARY.json'),finite_references=read(P/'results/E_CONTROL_SUMMARY.json')))
    reference_metadata=read(P/'REFERENCE_METADATA_FREEZE.json')
    coverage={suite:[r['subject'] for r in reference_metadata['records'] if r['coverage'][suite]['available']]
        for suite in ['N1','N2','N3','N4']}
    status.update(PRE_E_REFERENCE_ELIGIBLE_SUBJECTS=coverage,
        N4_AGGREGATE_REFERENCE_METADATA_COVERAGE=len(coverage['N4'])>=6,
        PERSISTENT_STATE_INTERPRETATION='WITHHELD; Development exploratory and original N4 coverage/reference requirements remain applicable')
    primary_references=read(P/'results/E_CONTROL_SUMMARY.json')['B4-B1']
    status.update(PRIMARY_REFERENCE_N1_GATE=primary_references['N1'].get('descriptive_disruption_gate',False),
        PRIMARY_REFERENCE_N2_GATE=primary_references['N2'].get('descriptive_disruption_gate',False),
        ROBUST_POSITIVE_PRIMARY_CLAIM=False,
        CLAIM_RESTRICTION='Exploratory Development only; original reference and held-out claim conjunctions cannot be cleared by mean gain or significance')
    dump(P/'results/DEVELOPMENT_STATUS.json',status)
    lines=['# Paper15 Development scientific report','',
        'Corrective mission P15-DEV-EXACT-NATIVE-REPAIR-R1. Historical STOP_SOURCE_IMPLEMENTATION_DEFECT is immutable:358 completed numerical PASS fits on rounded inputs,1 interrupted STARTED without endpoint,251 never started(130 baseline/228 dynamic completed). None is reused or relabeled as a corrected scientific fit. The owner prospectively authorized a separate new Development budget of732MAIN/660sensitivity absolute,610/550 for the corrected10-mouse cohort. No aggregate-ceiling retrospective compliance is claimed.','',
        f"New ledger: {status['NEW_MAIN_ATTEMPTS']} main and{status['NEW_SENSITIVITY_ATTEMPTS']} sensitivity starts; historical-plus-new cumulative{status['TOTAL_CUMULATIVE_ATTEMPTS']}. Exact-native binary64/time/missingness/strict-past/source-A/QC/scaler/ordinal gates passed before new fitting, with independent review. Source-native audit verified96642finite binary64 numeric cells across table columns, not96642distinct event timestamps, and382487strict predecessor queries. PL033 trial224 excludes its equal-time wheel event. Historical source/fit/stop evidence remains in ../paper15_dev and the preceding mission archive.",'',
        'This is the completed registered Development study, not an independently held-out scientific validation. All Development A/B/E findings are exploratory. No Final C/D neural arrays, physiology, fitting, scores or release were used.','',
        f"The original20 animals remain12 Development and8 Final. Native QC admitted{m2['development_eligible_mice']} Development mice across{m2['development_labs']} laboratories, eight units per mouse. NYU-37 failed the frozen B>=40 epoch floor(31); CSHL059 supplied identity sync with domain[0,1] and no covered epochs. Neither was replaced, extrapolated or relabeled. The eight Final animals have metadata-only potential; actual wheel support, C physiology and all numerical/Final gates remain future requirements.",'',
        f"Main A attempts: {baseline['attempted']} baselines and{dynamic['attempted']} dynamic/static starts; numerical pass counts{baseline['numerical_pass']} and{dynamic['numerical_pass']}. Every original start, gradient check, fixed finite-difference step and optimizer termination is retained. A candidate is unavailable globally when any mandatory mouse/start fails; optimizer success alone is insufficient.",'',
        'B selection uses one equal-mouse configuration per family, fixed nominal-capacity ties and S at selected D_K+1. D/S prediction ensembles the three per-bin joint masses. No E result changes selection.','',
        '|Contrast|Mice|Mean nats/actual unit-bin|95% whole-mouse CI|Raw p|Holm5 p|','|---|---:|---:|---|---:|---:|']
    for row in summaries:lines.append('|'+ '|'.join(str(row[k]) for k in ['contrast','mice','mean','CI95','raw_p','Holm5_p'])+'|')
    lines+=['','The primary test is one-sided, the fixed five secondary tests two-sided with Holm adjustment. Whole-mouse10,000-replicate percentile intervals use PCG64 seed150101. Sign-flip calculations require independent sign-exchangeable symmetric zero-centered mouse effects under the null; shared-lab dependence/asymmetry can invalidate that interpretation. Equal-lab/leave-one-lab-out and lab-bootstrap outputs are dependence diagnostics, not independent-laboratory replication.','',
        'All eleven sensitivity cases and four fixed999-replicate references are reported in the tables and source journals. Missing capacity/coverage or numerical failures are unavailable panels, never successful controls. N3 is a B4-LL wheel reliance diagnostic copied/labeled in the four-suite family; its B4−B1 changes are descriptive. Surrogates destroy alignment/order and are not exact biological conditional-null draws. No recursively generated counts were used. D/C/S receive no baseline sensitivity-refit robustness claim.','',
        'Physiology uses A only within known observation support, provider-good native MOp identities and exact fixed ranking. Saturation masks cover known selected-probe annotations only; unknown artifacts remain unknown. The ±2contact-index boundary is a proxy, not true histological distance. Eight curated-release units do not represent the complete MOp population, layer balance or all sensorimotor mechanisms. Wheel covariates do not control all movement.','',
        'Negative, mixed and nonsignificant findings are retained; crossing-zero intervals do not prove equivalence or biological absence. No causal mechanism, biological discrete-state superiority, human validation, online intervention, NAP/CWP proof or independent-lab replication is claimed. Historical P1–P14 and P15 M0/M1 failures are unchanged.','',
        'Final handoff: Prompt4 must separately authorize the trusted Final C-only reader and calibration, actual C admission and numerical/source checks, independent scientific assumptions/pre-D review, frozen selected models and exactly one D batch. This mission grants no Final access. Do not retune against E or automatically progress.','',
        'Saved-only reproduction: `powershell -NoProfile -ExecutionPolicy Bypass -File paper15_r1/reproduce.ps1`. It denies network and neural-array loading, verifies source/artifact hashes and saved numerical arithmetic, regenerates selection/statistical/reference summaries, and runs synthetic tests. It does not reproduce raw-data QC, fit coefficients or make a second E prediction.','',
        'Detailed sources: `tables/COHORT_FINAL_NATIVE_QC.csv`, `tables/MAIN_ATTEMPTS.csv`, `tables/B_SELECTION.csv`, `tables/E_MOUSE_EFFECTS.csv`, `tables/E_CONTRASTS.csv`, `tables/E_SENSITIVITIES.csv`, `tables/E_CONTROLS.csv`, `results/DEVELOPMENT_STATUS.json` and the independent-review evidence folder.']
    lines+=['','S11 native layer/contact-index composition and descriptive association are reported in `tables/ANATOMY_LAYER_PROXY.csv` and `results/LAYER_PROXY_ASSOCIATIONS.json`. Superficial means native MOp1/2-3 labels, deep5/6, layer4 separate; root/unknown remains in the denominator. Native depth is unavailable in the frozen metadata. These atlas/contact proxies and descriptive correlations do not establish histological distance or causal layer mechanisms. S04 uses100-ms bins; raw nats/bin magnitudes are not interchangeable with50-ms magnitudes.']
    lines+=['',f"Before any E neural outcomes, original metadata-only N4 coverage passed for {len(coverage['N4'])}/{len(admitted())} mice: {', '.join(coverage['N4'])}. The original aggregate requires at least6. In this execution its five eligible mice cannot establish an available aggregate N4 panel; the fixed family retains p=1/UNAVAILABLE. No replacement draws, mice or relaxed block/coverage rules were used. The corresponding drift-independent and persistent-state interpretations are withheld, regardless of D/C/S predictive effects. All eligible per-mouse finite references and ineligible records remain reported. This applies the original rule, without a post-result scientific amendment."]
    n1,n2=primary_references['N1'],primary_references['N2']
    lines+=['',f"The primary N1 disruption condition is {n1.get('descriptive_disruption_gate',False)}: {n1.get('mice_above_reference_median')}/{n1['n_mice']} mice exceed their reference median, whereas the frozen 75-percent condition requires8 of10 here. Its positive mean degradation and Holm4 reference p={n1['Holm4_reference_p']} do not clear that failed condition. N2 has {n2.get('mice_above_reference_median')}/{n2['n_mice']} above the reference median and condition={n2.get('descriptive_disruption_gate',False)}. The primary falsification evidence is mixed, and a robust positive primary/history-order interpretation is withheld. None of the five secondary comparisons meets Holm5 alpha=.05. These are reports of the original conditions, with no gate relaxation, selective panel or second evaluation."]
    (P/'DEVELOPMENT_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')


if __name__=='__main__':main()
