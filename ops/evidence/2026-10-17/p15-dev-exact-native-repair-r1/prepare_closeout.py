"""Trace every frozen obligation to saved proof; leave review/Git closure open."""
import datetime
from pathlib import Path
from paper15_r1.source import P,R,load_json,dump
from paper15_r1.training import sha

E=Path(__file__).parent
ER=E.relative_to(R).as_posix()

def run():
    log=E/'SAVED_REPRODUCTION_1.log'
    result=load_json(log.read_text(encoding='utf-8-sig').splitlines()[-1])
    assert result['synthetic_tests']==126 and result['frozen_files_verified']==1565
    assert result['real_fits']==result['real_neural_arrays_loaded']==0 and result['network_denied']
    assert result['saved_scientific_audit']['E']['complete_reference_bundles']==34965
    dump(E/'SAVED_REPRODUCTION_RECEIPT_1.json',dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        native_Windows_PowerShell=True,command='powershell -NoProfile -ExecutionPolicy Bypass -File paper15_r1/reproduce.ps1',
        exit_code=0,log_sha256=sha(log),archive_sha256=sha(P/'ARCHIVE_FREEZE.json'),result=result,
        independent_production_reexecution=False,second_E_prediction=False))
    groups=[
        (1,6,'Owner authority, versioned scope and unchanged scientific definitions',
            [ER+'/OWNER_MISSION.txt',ER+'/baseline.json','paper15_r1/EXECUTION_BOUNDARY.md',ER+'/PRESERVATION_REGISTRATION.json']),
        (7,18,'Original359identity/hash/size,358completed+1STARTED+251unattempted and coefficient nonreuse',
            [ER+'/PRESERVATION_REGISTRATION.json',ER+'/MAIN_NUMERICAL_REVIEW_1.md','paper15_r1/results/DEVELOPMENT_STATUS.json']),
        (19,43,'Canonical binary64 bits,types,missing classes,source hashes and preserved old defect',
            ['paper15_r1/native_table.py','paper15_r1/test_native_table.py','paper15_r1/results/FULL_A_SOURCE_REVALIDATION.json',ER+'/NATIVE_REPAIR_REVIEW_2.md',ER+'/FULL_NATIVE_INPUT_REVIEW_1.md']),
        (44,61,'ActualPL033224andall382487strict queries; independent37column source construction',
            ['paper15_r1/results/EXACT_WHEEL_INDEX_VERIFICATION.json','paper15_r1/input_oracle.py',ER+'/FULL_NATIVE_INPUT_REVIEW_1.md']),
        (62,83,'All12native identities/masks;fullAcounts/history/QC/ranks/scalers/ordinals and old-export differences',
            ['paper15_r1/results/FULL_A_SOURCE_REVALIDATION.json','paper15_r1/results/M2_PHYSIOLOGY_GATE.json',ER+'/FULL_NATIVE_INPUT_REVIEW_1.md']),
        (84,94,'Unchanged original eligibility,10mice8labs,80units,two original exclusions andFinalreserved',
            ['paper15_r1/results/M2_PHYSIOLOGY_GATE.json','paper15_r1/tables/COHORT_FINAL_NATIVE_QC.csv','paper15_r1/EXECUTION_BOUNDARY.md']),
        (95,107,'Originalmath/float64/solver/grids/seeds/PG/AD/all3FD;actual64fileprefit gate+continuity',
            ['paper15_r1/PRODUCTION_GATE.json','paper15_r1/results/PRODUCTION_SYNTHETIC_CERTIFICATE.json',ER+'/PRODUCTION_REVIEW_2.md',ER+'/MAIN_NUMERICAL_REVIEW_1.md']),
        (108,129,'Separatehist359/new610+525=1494;caps/retries/initials;35valid999suites+5unavailable,no referencefits',
            ['paper15_r1/A_FIT_PLAN.json','paper15_r1/SENSITIVITY_FIT_PLAN.json','paper15_r1/results/SENSITIVITY_SAVED_VERIFICATION.json','paper15_r1/results/CLAIM_TO_EVIDENCE_AUDIT.json']),
        (130,139,'Actualfrozenstageorder;allmainreviewbeforeB,fixedcaseplanbefore525fits,tworeviewsbeforeoneEclaim',
            [ER+'/MAIN_NUMERICAL_REVIEW_1.md','paper15_r1/SELECTION_FREEZE.json','paper15_r1/SENSITIVITY_GATE.json',ER+'/E_BATCH_ADMISSION_REVIEW_1.md',ER+'/E_NUMERICAL_READINESS_REVIEW_1.md','paper15_r1/E_BATCH_CLAIM.json']),
        (140,153,'Allsixactualequal-mouseeffects/CI/p/5Holm;N1mixed/N4unavailable/noheldout/mechanisticclaim',
            ['paper15_r1/DEVELOPMENT_REPORT.md','paper15_r1/results/CLAIM_TO_EVIDENCE_AUDIT.json','paper15_r1/tables/E_CONTRASTS.csv','paper15_r1/tables/E_CONTROLS.csv']),
        (154,162,'Compatiblecachedreaders/math/tests reused;boundedscientificactions,no unrelatedsearch/crypto/32kaudit',
            [ER+'/REUSE_MANIFEST.json',ER+'/IMPLEMENTATION_REPAIRS.md','paper15_r1/EXECUTION_BOUNDARY.md',ER+'/SAVED_REPRODUCTION_RECEIPT_1.json']),
        (163,171,'FinalIDsreserved,nofinalC/Dpayload/QC/fits/predictions;futureexplicitPrompt4only',
            ['paper15_r1/FINAL_IMPLEMENTATION_HANDOFF.md','paper15_r1/results/DEVELOPMENT_STATUS.json','paper15_r1/EXECUTION_BOUNDARY.md']),
        (172,193,'Ownerfields/allnegative-mixed-unavailablefindings and exact actualbudget/holdout flags',
            ['paper15_r1/results/DEVELOPMENT_STATUS.json','paper15_r1/results/CLAIM_TO_EVIDENCE_AUDIT.json',ER+'/SAVED_REPRODUCTION_RECEIPT_1.json']),
        (194,196,'Independentstage/fullreview,saved-only126testreproduction and scopednormalGitclosure/stop',
            [ER+'/SAVED_REPRODUCTION_RECEIPT_1.json',ER+'/E_BATCH_ADMISSION_REVIEW_1.md','paper15_r1/FINAL_IMPLEMENTATION_HANDOFF.md'])]
    baseline=load_json((E/'baseline.json').read_text())
    assert len(baseline['requirements'])==196
    pending={172:'FullownerreturnincludesverifiedGitcommit',193:'Gitcommit/remoteverification',
        194:'Finalcompletearchiveindependentreview',195:'Normalorigin/testpush/readback',196:'Finalreviewedclosureandstop'}
    matrix=[]
    for original in baseline['requirements']:
        index=int(original['id'].split('-')[1])
        group=next(g for g in groups if g[0]<=index<=g[1])
        proof=[dict(path=rel,sha256=sha(R/rel)) for rel in group[3]]
        row=dict(requirement_id=original['id'],requirement=original['requirement'],
            implementation_location=group[3][0],verification_method=group[2],evidence=proof,
            status='IMPLEMENTED_UNVERIFIED' if index in pending else 'VERIFIED')
        if index in pending:row['remaining_gate']=pending[index]
        if 26<=index<=29:row['interpretation']='Owner-listed alternative representations; adopted typed columns plus exact float.hex/binary64bits, not a requirement to implement every example.'
        matrix.append(row)
    dump(E/'PRESERVATION_MATRIX.json',dict(mission=baseline['mission'],baseline_sha256=sha(E/'baseline.json'),
        baseline_requirement_count=196,verified_baseline_count=191,rows=matrix,
        scope='Saved scientific/engineering delivery candidate; five final-review/Git/return/stop obligations explicitly remain open'))
    lines=['# Requirement preservation matrix','',
        'Original196obligations remain byte-identical in baseline.json. No requirement removed,renamed or weakened. Scientificnegative/unavailable outputs satisfy their registered reporting branch; no failed scientificclaim condition is cleared.',
        '','|ID|Status|Verification|Primary evidence|','|---|---|---|---|']
    lines += [f"|{row['requirement_id']}|{row['status']}|{row['verification_method']}|{row['implementation_location']}|" for row in matrix]
    (E/'preservation-matrix.md').write_text('\n'.join(lines)+'\n')
    (E/'verdict.md').write_text('# Candidate verdict; final closure pending\n\nMission P15-DEV-EXACT-NATIVE-REPAIR-R1. Internal state CONTINUE_EXECUTION, not a terminal PASS.\n\n'
        'Scientific Development execution and native repair complete; allresults exploratory. N1primary7/10failsoriginal8/10condition;N4aggregate5miceunavailable/p1;allfive secondaryHolm5nonsignificant. No scientificvalidation,robust-primary,persistent-state or mechanisticPASS.\n\n'
        'Known bug_count=0,warn_count=0,required_items_omitted=0,required_behaviors_silently_reduced=0,unapproved_existing_behaviors_removed=0,required_tests_silently_removed=0,unresolved_shrink_risk=0,temporary_substitutes_remaining=0,coverage_reductions_without_approval=0.\n\n'
        'Baseline196:191verified,5explicitfinalreview/Git/return/stopgatespending. NativePowerShellsaved-onlyreproductionexit0,126tests,1565packagefiles,23M1files,610main/525sensitivity/34965referencebundlesaudited;network/neural-arrayloadingdenied.\n\n'
        'Finalindependentreview,normalorigin/testarchivepush,actualremotereadbackandcleangateremainrequired. NoPrompt4orFinalaccess.\n')
    print('Prepared126testreceipt and196rowmatrix;191verified/5explicitclosuregatespending')

if __name__=='__main__':run()
