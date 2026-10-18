"""Saved-evidence Final reporting. Never opens neural arrays or runs predictions."""
import csv
import io
import datetime
from .source import P,R,read,dump,sha,roster
from .statistics import CONTRASTS,SECONDARY


def write_csv(name,rows):
    assert rows
    fields=list(dict.fromkeys(k for row in rows for k in row))
    text=io.StringIO(newline='');writer=csv.DictWriter(text,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    path=P/'tables'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(text.getvalue().encode('utf-8'))


def attempts(folder):
    rows=[]
    for path in sorted((P/folder).rglob('*.json')):
        try:
            record=read(path);status=record['status']
        except Exception as exc:
            rows.append(dict(path=path.relative_to(P).as_posix(),status='CORRUPT_OR_INCOMPLETE_ATTEMPT',error=type(exc).__name__));continue
        rows.append(dict(path=path.relative_to(P).as_posix(),status=status,sha256=sha(path),
            family=record.get('configuration',{}).get('family'),PG=record.get('PG'),iterations=record.get('iterations'),
            AD_max_scaled=record.get('independent',{}).get('AD_max_scaled'),
            max_FD_scaled=max((x['max_scaled'] for x in record.get('independent',{}).get('FD',[])),default=None),
            optimizer_success=record.get('optimizer_success'),termination=record.get('termination'),error=record.get('error')))
    return rows


def build():
    metadata=read(P/'results/FINAL_METADATA_GATE.json');qc=read(P/'results/FINAL_C_QC_GATE.json')
    mains=attempts('fits');sensfits=attempts('sensitivity_fits')
    claim=read(P/'D_BATCH_CLAIM.json') if (P/'D_BATCH_CLAIM.json').exists() else None
    complete=bool(claim and claim['status']=='COMPLETE_REGISTERED_DESCRIPTIVE_D_BATCH')
    if not claim:
        stops=[p for p in [P/'results/C_MAIN_REQUIRED_STOP.json',P/'results/C_SENSITIVITY_REQUIRED_STOP.json',P/'PRE_D_STOP_DECISION.json'] if p.exists()]
        assert stops or not qc['descriptive_cohort_eligible'],'C-only stop report needs an actual required-stop decision, not unfinished implementation'
    source_by={r['subject']:r for r in metadata['subjects']};qc_by={r['subject']:r for r in qc['subjects']};source_rows=[]
    for original in roster():
        subject=original['subject'];source=source_by[subject];state=qc_by[subject]
        full=read(P/'results'/(subject+'_C_QC.json')) if state['C_neural_access'] else None
        source_rows.append(dict(subject=subject,lab=original['lab'],eid=original['eid'],pid=original['pid'],probe=original['probe_name'],
            source_pass=source['source_metadata_pass'],C_access=state['C_neural_access'],C_admitted=state['admitted'],
            C_qualified_units=full['qualified_units'] if full else None,C_epochs=full['C_epochs'] if full else None,
            D_metadata_epochs=state.get('D_metadata_epochs'),selected_unit_UUIDs=';'.join(full['selected_unit_uuids']) if full else '',
            exclusion_reason=source.get('reason') if not source['source_metadata_pass'] else state.get('reason')))
    write_csv('FINAL_SOURCE_AND_C_QC.csv',source_rows)
    if mains:write_csv('FINAL_MAIN_ATTEMPTS.csv',mains)
    if sensfits:write_csv('FINAL_SENSITIVITY_ATTEMPTS.csv',sensfits)
    delivery=dict(mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        FINAL_SOURCE_PASS=dict(admitted_cohort=True,all_eight_candidates=False,source_excluded=['NYU-21']),
        FINAL_C_READER_SCOPE='Explicitly authorized whole-record ALF decode only inside trusted reader to classify/export C; no pre-D D scientific counts/QC/scaling/selection/random streams. Ordinary local scientific controls, not cryptographic or independent-third-party custody.',
        FINAL_C_QC_PASS=dict(descriptive_floor=qc['descriptive_cohort_eligible'],eight_mouse_primary=False,C_QC_excluded=['UCLA033']),
        FINAL_ELIGIBLE_MICE=qc['eligible_mice'],FINAL_ELIGIBLE_LABS=qc['eligible_labs'],
        FINAL_C_MODEL_CALIBRATION='COMPLETE_SEALED' if (P/'FINAL_C_STATE_SEAL.json').exists() else 'INCOMPLETE_REQUIRED_STOP',
        FINAL_MAIN_FIT_ATTEMPTS=len(mains),FINAL_SENSITIVITY_FIT_ATTEMPTS=len(sensfits),
        cumulative_attempts=1494+len(mains)+len(sensfits),historical_original_attempts=359,R1_corrective_attempts=1135,
        historical_failures_preserved=True,no_retry=True,
        PRE_D_INDEPENDENT_REVIEW='ACCEPTED' if complete else 'See actual gate/required-stop evidence',
        ONE_SHOT_D_EXECUTED=bool(claim and claim.get('D_projection_completed_subjects')),
        D_ACCESS_ATTEMPTED=bool(claim and claim.get('D_neural_access_attempted')),D_BATCH_COMPLETE=complete,
        FINAL_PRIMARY_EFFECT=None,FINAL_PRIMARY_CI=None,FINAL_PRIMARY_P_VALUE=None,
        FINAL_SECONDARY_EFFECTS=None,FINAL_HOLM_ADJUSTED_RESULTS=None,FINAL_FALSIFICATION_RESULTS=None,
        DEVELOPMENT_FINAL_CONSISTENCY=None,
        SCIENTIFIC_PRIMARY_VERDICT='INCONCLUSIVE REQUIRED GATE',SCIENTIFIC_SECONDARY_VERDICTS={c:'INCONCLUSIVE REQUIRED GATE' for c in SECONDARY},
        PROMPT_5_READY=complete,BUG_COUNT=0,WARN_COUNT=0,
        candidate_defect_count_scope='Known unresolved engineering defects only; final independent-review and live Git closure evidence are external and remain mandatory',
        GIT_COMMIT='Actual reviewed archive/remote receipt supplied at closure; no self-referential invented SHA',REMOTE_VERIFICATION='Pending live Git closure',
        completed_paper=False,confirmatory_validation=False,manuscript_and_PDF_not_this_mission=True)
    lines=['# P15 registered Final scientific handoff','',
        '**Independent-animal descriptive assessment; no confirmatory or causal label.**','',
        'Eight original Final identities remain in the ledger. NYU-21 failed the frozen native wheel strict-order screen (16,485 equal adjacent timestamp pairs); no deduplication, replacement or source repair. UCLA033 had6 C-qualified units,below the original8-unit floor. Six mice from4 laboratories passed the original C-only physiology/source rules. The prospectively authorized6–7mouse fallback fixes the maximum interpretation to DESCRIPTIVE ONLY regardless of effect size or p-value.','',
        'C extraction used the explicitly authorized trusted low-level whole-record ALF decoder solely to classify/export C observations. Scientific C roles received only C exports; upstream whole-session release curation is disclosed. No D scientific counts,QC,scalers,selection or thinning streams were used before the reviewed pre-D gate. Local access discipline is not an independent custodian or malicious-administrator guarantee.','',
        f'Actual Final fit attempts: main{len(mains)},sensitivity{len(sensfits)}; historical359 and separately authorized corrective1135 remain distinct; cumulative{1494+len(mains)+len(sensfits)}. No model search,development coefficient reuse,seed replacement,budget expansion or retry. Original PG<=.001,AD<=1e-5 and all3FD<=1e-5 remain unchanged.','']
    if complete:
        from .anatomy_report import build as build_anatomy
        build_anatomy()
        stats=read(P/'results/D_STATISTICS.json');sens=read(P/'results/D_SENSITIVITY_SUMMARY.json');controls=read(P/'results/D_CONTROL_SUMMARY.json');verdicts=read(P/'results/D_SCIENTIFIC_VERDICTS.json')
        primary=stats['B4-B1']
        delivery.update(FINAL_PRIMARY_EFFECT=primary.get('equal_mouse_mean'),FINAL_PRIMARY_CI=primary.get('CI95'),
            FINAL_PRIMARY_P_VALUE=primary['paired_sign_flip_p'],FINAL_SECONDARY_EFFECTS={c:stats[c].get('equal_mouse_mean') for c in SECONDARY},
            FINAL_HOLM_ADJUSTED_RESULTS={c:stats[c]['Holm5_adjusted_p'] for c in SECONDARY},FINAL_FALSIFICATION_RESULTS=controls,
            SCIENTIFIC_PRIMARY_VERDICT=verdicts['B4-B1']['verdict'],SCIENTIFIC_SECONDARY_VERDICTS={c:verdicts[c]['verdict'] for c in SECONDARY})
        contrasts=[];individual=[]
        lines+=['Exactly one frozen D batch completed. No D fitting,retuning,surrogate replacement or second assessment. Likelihoods include factorial/exposure terms; gains use each mouse\'s actual valid scored nominal curated-release unit-bin denominator,then equal-mouse aggregation. The sign-flip calculations remain conditional on independent,symmetric sign-exchangeable mouse effects; this observational cohort/shared laboratories cannot empirically establish those assumptions. No D assumption pretest selected a different method.','',
                'At n=6 the exact sign-flip test has64 assignments: the smallest one-sided p is1/64=.015625 and the smallest two-sided p is2/64=.03125. Thus the smallest possible five-test Holm-adjusted secondary p is.15625. None of the secondary comparisons can meet.05 under this frozen design. This discrete resolution limitation was documented before D; it is not evidence of equivalence or a post hoc power calculation.','',
                '|Contrast|Mice|Mean nats/unit-bin|95% whole-mouse interval|Raw p|Holm5 p|Verdict|','|---|---:|---:|---|---:|---:|---|']
        for c,r in stats.items():
            row=dict(contrast=c,n_mice=r['n_mice'],mean=r.get('equal_mouse_mean'),CI95=r.get('CI95'),CI_width=r.get('CI_width'),raw_p=r['paired_sign_flip_p'],Holm5_p=r.get('Holm5_adjusted_p'),verdict=verdicts[c]['verdict'])
            contrasts.append(row);individual += [dict(contrast=c,**m) for m in r['mouse_effects']]
            lines.append(f"|{c}|{r['n_mice']}|{row['mean']}|{row['CI95']}|{row['raw_p']}|{row['Holm5_p']}|{row['verdict']}|")
        write_csv('FINAL_CONTRASTS.csv',contrasts);write_csv('FINAL_INDIVIDUAL_MOUSE_EFFECTS.csv',individual)
        sensitivity_rows=[dict(case=case,contrast=c,n_mice=p['n_mice'],mean=p.get('equal_mouse_mean'),CI95=p.get('CI95'),mandatory=p['mandatory'],coverage_pass=p['minimum6_coverage'],status=p['status']) for case,panels in sens.items() for c,p in panels.items()]
        write_csv('FINAL_SENSITIVITIES.csv',sensitivity_rows)
        control_rows=[dict(contrast=c,suite=suite,status=p['status'],n_mice=p['n_mice'],mean_degradation=p.get('mean_degradation'),above_median=p.get('mice_above_reference_median'),disruption_gate=p.get('descriptive_disruption_gate'),p_reference=p['p_reference'],Holm4_p=p['Holm4_reference_p']) for c,panels in controls.items() for suite,p in panels.items()]
        write_csv('FINAL_CONTROLS.csv',control_rows)
        dev=read(R/'paper15_r1/results/E_STATISTICS.json')
        consistency={c:dict(Development_mean=dev[c].get('equal_mouse_mean'),Final_mean=stats[c].get('equal_mouse_mean'),
            Development_n=dev[c].get('n_mice'),Final_n=stats[c]['n_mice'],pooled_or_reselected=False,formal_new_difference_test=False) for c in CONTRASTS}
        delivery['DEVELOPMENT_FINAL_CONSISTENCY']=consistency;write_csv('DEVELOPMENT_VS_FINAL.csv',[dict(contrast=c,**v) for c,v in consistency.items()])
        lines+=['','All33baseline sensitivity panels and24contrast/reference panels appear in the tables,including every failed/unavailable case. These are baseline sensitivities; no D/C/S sensitivity-refit robustness was performed or credited. S02/S03 capacity failures remain explicit,and100ms nats/bin magnitudes are not interchangeable with50ms values.','',
            'N1/N2 are destructive history-order/alignment diagnostics,not exact mechanistic nulls. N3 is the B4 likelihood wheel-reliance diagnostic copied/labeled across contrast slots,not D/C wheel evidence or all-movement independence. N4 pre-D metadata supported only3 mice,below the original aggregate6mouse floor; its aggregatep=1/unavailable panel and persistent-state restriction remain mandatory. No favorable statistic rescues a missing condition.','',
            'Development remains exploratory: B4-B1 mean+0.1125291851; N1 only7/10<8; CIwidth0.09622>0.01; N4 aggregate unavailable; all5secondaryHolm tests nonsignificant. Final outcomes do not rewrite those findings or the rounded-input STOP. No pooled Development/Final inference or new cross-cohort hypothesis was added.']
        lines+=['','The registered S11 anatomy table reports native layer acronyms/contact indices,superficial/deep/middle/root fractions and descriptive effect associations without new tests. Native physical depths are unavailable in the frozen metadata; contact neighborhoods and atlas labels are proxies,not histological distance or causal layer findings.']
        dump(P/'results/FINAL_CLAIM_TO_EVIDENCE_AUDIT.json',dict(scope='Complete registered Final descriptive assessment',verdicts=verdicts,
            source_table='tables/FINAL_SOURCE_AND_C_QC.csv',main_table='tables/FINAL_CONTRASTS.csv',sensitivity_table='tables/FINAL_SENSITIVITIES.csv',
            controls_table='tables/FINAL_CONTROLS.csv',Development_Final=consistency,original_M1_claim_map_retained=True,
            biological_discrete_states=False,causal_connectivity=False,motor_command_mechanism=False,all_movement_independence=False,
            independent_lab_replication=False,NAP_CWP_proof=False,human_or_BCI_validation=False))
    else:
        lines+=['The registered Final assessment did not validly complete. The source/C-only or immutable partial-D stop evidence is retained. No missing likelihood,effect,interval,p-value,null or model state is invented. No second D assessment or mathematical/optimizer rescue is authorized.']
    lines+=['','Recording/anatomy limitations: public curated sorting/provider whole-session labels,known selected-probe saturation masks only,unknown unannotated artifacts,atlas boundary/layer/contact-index proxies rather than histology,and observational wheel nuisances that do not measure all face/body/arousal movement. The fixed cohort was selected for available MOp observations; it is not a random population/laboratory sample. Conditional predictive information is not connectivity,mechanism,biological primitives,CWP/NAP proof,independent-lab replication or human/BCI validation.','',
        'Author review remains necessary for source attribution,interpretation and eventual manuscript drafting. Prompt5 manuscript/publication-qualityPDF is outside this mission. No next stage is started automatically.','',
        'Saved-only reproduction: `powershell -NoProfile -ExecutionPolicy Bypass -File paper15_final1/reproduce.ps1`. It audits saved artifacts/statistics and synthetic regressions; it never refits or reopens/reassesses D. Executable one-shot source is archived for audit,the existing claim denies a second real run.']
    dump(P/'results/FINAL_DELIVERY.json',delivery)
    (P/'FINAL_SCIENTIFIC_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Saved-only Final report assembled;scientific_complete',complete,'main',len(mains),'sensitivity',len(sensfits))


if __name__=='__main__':build()
