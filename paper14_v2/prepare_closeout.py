"""Prepare an explicit source-gate STOP archive; never reads source neural data."""
import datetime,hashlib,json,platform
from pathlib import Path
from .source_metadata import P,ROOT,read,write,verify_history
E=ROOT/'ops/evidence/2026-10-16/p14-v2-exploratory-context-dynamics'

def doc(path,text):
    with Path(path).open('x',encoding='utf8',newline='\n') as f:f.write(text)

def main():
    verify_history();s=read(P/'results/source_gate/SOURCE_COMPATIBILITY.json')
    assert s['source_compatibility']=='SOURCE_CONTRACT_INCONCLUSIVE'
    doc(P/'STOP_REPORT.md','''# P14-v2 source compatibility STOP report

Mission P14-V2-EXPLORATORY-CONTEXT-DYNAMICS. BASE b82425aab216f57b207d242c4361760f03b598d4.

The registered source gate is **SOURCE_CONTRACT_INCONCLUSIVE**. No neural QC, model fitting, prediction score, temporal evaluation, null test or findings manuscript was executed. The source gate must pass before a full scientific/model protocol or any neural execution can be activated. All original P14 and P1–P13 failures remain unchanged.

## Prospective contract and source

The owner's new exploratory question concerns differences in incremental predictive value between scheduled probabilityLeft 0.2 and 0.8 contexts in MEDIAL FRONTAL CORTEX. This is a within-animal temporal holdout proposal, not independent-animal confirmation. The exact proposed target is MOs/ACAd/ACAv/PL/ILA with documented laminar descendants, a single simultaneous probe per mouse and identical units across contexts. Old strict mPFC 8 and expanded 13 metadata candidates remain historical results; the old 8+8 confirmatory failure is immutable.

SOURCE_REGISTRATION.json was frozen at 2026-10-17T06:24:57.141607+00:00 before new canonical metadata counts or neural outcomes. Its exact SHA256 is 3e4b923a51fc55de63922fcb6cf5fe17cc1fe29759a976d045b24a3d411fc990. It retains the original whole-block cut and source masks, >=10 qualified same-probe units, >=2 qualifying runs/context, >=15 trials/run, >=60 trials/context/half and 0.5-second observation window. New train-only QC and model/statistics/control definitions were deliberately not activated before source compatibility.

Fixed public source: [DANDI 000409, release 0.260309.1324](https://dandiarchive.org/dandiset/000409/0.260309.1324), CC BY 4.0/OpenAccess as documented in the immutable prior official release metadata. Source attribution: International Brain Laboratory Brain Wide Map; conversion by CatalystNeuro/IBL-to-nwb. The audited conversion snapshot is 54030ac4eb40a74978ac1f6ef6e966278b9d3f34, not a demonstrated historical writer for every NWB. Upstream source curation is release/session based, not newly computed training-only physiology.

## Exact audited denominator and identity

13 historical session/probe triplets were prospectively listed. Only the first was read before its essential bridge failed; the other 12 were not read. The canonical eligible cohort count remains UNKNOWN, and zero mice are admitted by this audit. Physiological eligibility is NOT MEASURED. This is not evidence that fewer than 6 or 8 eligible mice exist in the full release.

Audited mouse CSHL049; session d2918f52-8280-43c0-924b-029b2317e62c; historical probe probe00/pid2564dc27-4eda-4fc3-a151-c13475796ee1; asset9e27ec60-e8d9-4dcf-a9a4-4b8acb6265ef; blob097f77c7-f16b-41a4-bb00-d034f1c47022; canonical asset size811136122. Subject identity, official asset/session path and original837 trial-row count agree. The NWB identifier is a distinct file UUID; no equality to the session UUID is assumed.

The 1088 canonical unit UUIDs form the same set as the historical session metadata, and their UUID-keyed quality labels agree at1e-12 comparison precision. Canonical max_electrode indices are in bounds and canonical unit probe labels agree internally with their indexed electrode groups. This does not certify historical per-unit probe equality, complete atlas leaf translation, sorting-writer identity or neural physiology. No anatomical eligibility or MOs percentage was recomputed from an incomplete source contract.

## Failed task/annotation bridge

The canonical trials table contains neither bwm_include nor saturation_stim_plus06. There is no canonical invalid_times table in the enumerated intervals group. The registered fallback allowed old annotation transfer only after original-row, identity, curatorial-event and missingness agreement within1e-6 seconds. This is a serialization comparison tolerance, not an estimated synchronization accuracy or a post-result scientific threshold.

Of837 original trials, firstMovement_times versus canonical wheel_movement_onset_time fails in794 rows; one row has different missingness. Canonical missing43 versus historical44; maximum finite absolute difference0.16523332996939644 seconds. Of the794 discrepant rows,592 carry old bwm_include=True. One gabor_stimulus_offset_time differs, by12.699666666666872 seconds. Start/stop, stimulus onset, auditory cue, response registration, feedback, context, choice, reward indicator/volume and stimulus side/contrast agree in this comparison. Complete finite values and missingness are preserved in results/source_gate/TRIAL_EVENT_COMPARISON.csv (837x8=6696rows).

The official static [IBL bwm_loading.py snapshot](https://github.com/int-brain-lab/paper-brain-wide-map/blob/118fc36cb3602934466ad2c6087c2b3b441f9f1f/brainwidemap/bwm_loading.py) documents firstMovement_times in default missing-event exclusions and reaction-time masking. Its frozen text and receipt are in sources/. It was never executed and is not proof of the exact historical annotation writer. The observed discrepancy establishes failure of the registered equivalence bridge; it does not prove every old mask bit would change, identify the cause of reprocessing, or establish a general NWB clock defect.

No old masks were transferred. No fields were dropped from the bridge, timestamps corrected, tolerance relaxed, trial rows reordered, source/session substituted or favorable mice selected. An outcome-blind fallback for ordinary eligibility loss does not authorize bypassing this essential provenance failure.

## Access and engineering evidence

The independently reviewed metadata reader used224 exact-range attempts/448 HTTP transactions and499986 opaque transport bytes, all for one registered asset. Maximum individual range61440bytes. No range failed, no bulk response was consumed. Each HTTP redirect was validated before contact and bound to the official blob; Content-Range, source size, ETag and range digest were checked. Raw opaque transport caches remain ignored in work/; only whitelisted metadata exports and receipts are committed. Adjacent uninterpreted HDF5 transport bytes are not decoded neural outcomes.

No spike_times, spike_times_index, count, rate, amplitude, waveform or raw continuous behavior dataset was opened, even for its shape. Protected dataset names may appear as unopened entries in schema exports. Synthetic canaries and the final reader implementation support this scoped claim; they do not establish independent provider instrumentation or immunity to a malicious administrator.

The original failed reader review (late redirect validation and unbound cache offsets) is retained; both defects were repaired before real source use and independently re-reviewed. Early transcripts retain a file-handle ResourceWarning and a later pandas deprecation warning. Both ordinary code warnings were fixed;28 focused tests run with warnings as errors. Original registration, failed attempts and all746 historical hashes are preserved. No scientific acceptance rule was changed.

## Results and claim boundary

BASELINE_SCORES, DISCRETE_SCORES, CONTINUOUS_SCORES, CONTEXT_INTERACTION_EFFECTS, CORRECTED_STATISTICS and NULL_AND_SENSITIVITY_RESULTS are all NOT_RUN_SOURCE_GATE. Training/evaluation identities were not finally frozen; only the proposed early/late whole-block rule was registered. No final model, hypothesis family, optimizer policy, sensitivity suite or manuscript result is represented as completed. MANUSCRIPT_COMPLETE=False; manuscript and supplement PDFs were not generated because there are no neural findings. This report fulfills the explicitly required truthful STOP-report branch.

There is no model-family winner, cross-animal confirmation, causal mechanism, movement/arousal-independent conclusion or CWP/NAP claim. Scores were not treated as zeros and nonsignificance was not inferred from missing analyses. All85 requirements remain individually traceable; downstream scientific items remain blocked, not silently removed or passed as N/A.

## Minimum next scientific action

Keep this route stopped. The exact missing item is an authoritative version-compatible canonical source curation/observation-support annotation bridge for this fixed release. A future separately authorized bounded protocol could establish canonical masks from documented source definitions or supply release-matched annotations, preserving all current failures. Reusing old masks despite failed equivalence or changing the frozen bridge requires a new prospective scientific decision. No additional dataset search, neural access, repeated audit or automatic model execution is authorized by this closeout.

Run `& .\\paper14_v2\\reproduce.ps1` from the repository to verify payload and746historical hashes,28synthetic regressions, access receipts and both saved source-gate outputs with network forbidden. Success means the STOP is reproduced; it is not scientific PASS.
''')
    deliver=dict(SOURCE_COMPATIBILITY=s['source_compatibility'],LICENSE_VERIFIED=True,
        CANONICAL_COHORT_COUNT=None,CANONICAL_ADMITTED_MICE=0,CANONICAL_AUDITED_ASSETS=1,HISTORICAL_CANDIDATE_MICE=13,
        PHYSIOLOGICAL_ELIGIBLE_MICE=None,TRAINING_EVALUATION_SPLIT='PROPOSED_EARLY_LATE_WHOLE_BLOCK_RULE_ONLY_NOT_FROZEN_OR_ACTIVATED',
        BASELINE_SCORES='NOT_RUN_SOURCE_GATE',DISCRETE_SCORES='NOT_RUN_SOURCE_GATE',CONTINUOUS_SCORES='NOT_RUN_SOURCE_GATE',
        CONTEXT_INTERACTION_EFFECTS='NOT_RUN_SOURCE_GATE',CORRECTED_STATISTICS='NOT_RUN_SOURCE_GATE',NULL_AND_SENSITIVITY_RESULTS='NOT_RUN_SOURCE_GATE',
        EXPLORATORY_SCIENTIFIC_VERDICT='SOURCE_CONTRACT_INCONCLUSIVE',MANUSCRIPT_COMPLETE=False,PDF_DELIVERABLES=[],
        REPRODUCTION_STATUS='REQUIRES_EXECUTED_RECEIPT',BUG_COUNT=0,WARN_COUNT=2,
        WARNINGS=['Essential canonical source-mask/event bridge unresolved','Full anatomy/cohort/physiology and scientific execution not certified'],
        GIT_COMMIT_REMOTE_VERIFICATION='REQUIRES_EXECUTED_EXTERNAL_CLOSURE_RECEIPT',new_fits=0,new_scores=0,neural_outcome_access=False)
    write(P/'FINAL_DELIVERY.json',deliver)
    doc(P/'A1_A10_STOP_AUDIT.md','''# A1–A10 source-stop evidence audit

This would be a Method Paper if later scientifically activated. It is currently a source STOP report, not a findings paper or completed manuscript.

| Attachment | Evidence / status |
|---|---|
| A1 Question and hypotheses | Owner question and two proposed interactions retained; full model/statistical activation blocked. |
| A2 Source and license | Fixed000409/0.260309.1324 CC-BY4; prior source evidence hash-bound; one canonical asset audited. |
| A3 Cohort/QC/splits | Historical13 not canonicalcohort; canonical/physiology UNKNOWN; no QC or neural split activation. |
| A4 Model mathematics | B0–B4/D/C requirements preserved; full protocol/implementation NOT_RUN_SOURCE_GATE. |
| A5 Numerical validation |28metadata/transport/bridge tests; no claim to HMM/GLM/AD numerical certification. |
| A6 Scores/statistics | NOT_RUN_SOURCE_GATE; no zero substitution, p-value or effect estimate. |
| A7 Nulls/sensitivities | NOT_RUN_SOURCE_GATE; no unstable P13generator or new null used. |
| A8 Leakage/provenance | Whitelisted metadata only, no neural outcomes; exact task bridge failure and receipt boundaries disclosed. |
| A9 Claims/limitations | Only source compatibility STOP supported; no source-wide insufficiency, model winner or biological claim. |
| A10 Reproduction/review/archive | Network-denied saved reproduction; independent reviews and exact origin/test closure receipts required. |
''')
    b=read(E/'baseline.json');blocked={9,15,19,20,22,23,24,25,26,*range(28,55),*range(56,63),65,66,67,*range(68,75)}
    matrix=[]
    for r in b['requirements']:
        i=int(r['id'].split('-')[1]);status='BLOCKED_NEED_ENV' if i in blocked else 'VERIFIED'
        if i in {83,84}:status='IMPLEMENTED_UNVERIFIED'
        matrix.append(dict(**{k:v for k,v in r.items() if k!='status'},status=status,
            evidence='paper14_v2/STOP_REPORT.md; results/source_gate/SOURCE_COMPATIBILITY.json; SOURCE_REGISTRATION.json; A1_A10_STOP_AUDIT.md; SOURCE_TESTS_r4.txt',
            verification='Source gate failed; downstream requirement retained, not executed or counted as PASS' if i in blocked else 'Saved evidence/report/policy; Git items require actual external closure receipt'))
    write(E/'preservation_matrix.json',dict(baseline_count=85,verified_count=sum(r['status']=='VERIFIED' for r in matrix),blocked_count=len(blocked),pending_git=2,requirements=matrix,required_items_omitted=0,unresolved_shrink_risk=0,full_scientific_pass=False))
    doc(E/'BLOCKER.md','''# Bounded source blocker

candidate_exit: NEED_ENV
mission: P14-V2-EXPLORATORY-CONTEXT-DYNAMICS
blocked requirements: REQ-009 and dependent scientific execution in preservation_matrix.json
missing item: authoritative release-compatible source curation/observation-support masks or a valid registered event/annotation equivalence bridge.
observed: first audited canonical NWB lacks bwm_include/saturation_stim_plus06;794movement-event discrepancies including1missingness disagreement fail the frozen bridge.
evidence: paper14_v2/results/source_gate/SOURCE_COMPATIBILITY.json and TRIAL_EVENT_COMPARISON.csv; canonical values/schema exports; frozen source registration.
alternatives: canonical trial/invalid_times fields inspected; verified old event/annotation join attempted and failed; official static curation definition inspected; unit UUID/QC and common event identity agreement cannot replace missing curatorial-event agreement.
why insufficient: masks cannot be silently inherited, omitted or recomputed under a changed protocol after this failure. No proof every mask bit differs is asserted.
autonomous exhaustion: reader defects and warnings repaired and regression tested; saved comparison/report/reproduction/review/archive can finish. New source chasing or changing the bridge would cross the explicit essential-provenance STOP rule, not repair a software defect.
restoration action: provide authoritative version-compatible canonical curation/observation support or separately authorize a prospective bounded canonical-mask protocol before new source/neural work; do not silently relax1microsecond, missingness or mask rules.
next: stopped after reviewed archive; no further automatic neural/data/model mission.
''')
    header='''# Current mission: P14-V2-EXPLORATORY-CONTEXT-DYNAMICS

Scientific SOURCE_CONTRACT_INCONCLUSIVE; new exploratory within-animal temporal track stopped at registered essential source gate. BASEb82425aab216f57b207d242c4361760f03b598d4. Historical13 not canonicalcohort;1of13registered assets audited,12unread,canonicaleligible/physiological counts UNKNOWN. CSHL049837trials: canonical bwm/saturation masks absent;794first-movement discrepancies/1missingness disagreement (max.16523333s),1stimOff discrepancy12.69967s. Frozen1e-6serialization bridge fails; no mask transfer or source-wide DATA_INSUFFICIENT claim.1088UUID-set/UUID-keyedQC match and internal electrode/probe consistency do not certify fullanatomy/writer identity.

No neural array/shapes/rawbehavior decoded,QC/fits/scores/lateevaluation.224range attempts448HTTP/499986opaque bytes; no fullNWB.28source/bridge tests, saved-only PowerShell and independent source/final reviews required for archive. All746historicalhashes/85requirements retained; downstream scientificrequirements blocked. No findingspaper/PDF,models/statistics/nulls NOTRUN; truthful STOPreport in paper14_v2/STOP_REPORT.md. bug_count0/warn_count2 source/scientific proofgaps. Exactcommit/origin-test/readback/clean only certified by executed externalclosure_receipt.json. No automatic continuation or newdataset/cryptoarchitecture. Prior headers preserved below.

---
'''
    daily=ROOT/'ops/daily-operations.md';daily.write_bytes(header.encode('utf8')+daily.read_bytes())
    import h5py,numpy,pandas,requests
    write(P/'RUNTIME.json',dict(python=platform.python_version(),numpy=numpy.__version__,pandas=pandas.__version__,h5py=h5py.__version__,requests=requests.__version__))
    hashes={f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and not {'work','__pycache__'}&set(f.relative_to(P).parts) and f.name!='PAYLOAD_HASHES.json'}
    write(P/'PAYLOAD_HASHES.json',dict(hashes=hashes,excludes=['work/ opaque uncommitted transport cache','__pycache__/','PAYLOAD_HASHES.json self'],purpose='Saved source STOP archive only; all historical inputs separately hash-bound'))
    print(json.dumps(dict(payload=len(hashes),baseline=85,verified=sum(r['status']=='VERIFIED' for r in matrix),blocked=len(blocked))))

if __name__=='__main__':main()
