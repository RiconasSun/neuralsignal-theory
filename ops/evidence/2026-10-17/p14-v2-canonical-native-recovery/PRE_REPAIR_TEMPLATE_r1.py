"""Prepare the reviewed metadata-only stopping branch without changing policy."""
import datetime,json,platform,hashlib,subprocess
from pathlib import Path
from .source_metadata import P,ROOT,read,write,verify_history
E=ROOT/'ops/evidence/2026-10-17/p14-v2-canonical-native-recovery'
BASE='b09b1b254d3f8b9c5fd4be948befae0332f6b96a'
def doc(path,body):
    with path.open('x',encoding='utf8',newline='\n') as f:f.write(body)
def main():
    verify_history();d=read(P/'results/audit/CANONICAL_NATIVE_DECISION.json');assert d['scientific_decision']=='SOURCE_CONTRACT_INCONCLUSIVE' and d['canonical_metadata_audited_mice']==13
    rows=d['summaries'];potential=d['potential_task_anatomy_mice']
    table='| Mouse | Frozen probe | Qualified target units | MOs units | .2 train / late | .8 train / late | Task/unit capacity | Neural support |\n|---|---|---:|---:|---:|---:|---|---|\n'
    for z in rows:
        c=z['task']['cell_trials'];u=z['units']
        table+=f"| {z['mouse']} | {z['historical_probe']} | {u['qualified_target_units']} | {u['MOs_units']} | {c['0.2_training']} / {c['0.2_evaluation']} | {c['0.8_training']} / {c['0.8_evaluation']} | {z['potential_task_anatomy_capacity']} | UNKNOWN |\n"
    http=[json.loads(s) for s in (P/'results/SOURCE_HTTP_ACCESS.jsonl').read_text().splitlines()];ranges=[json.loads(s) for s in (P/'results/SOURCE_ACCESS.jsonl').read_text().splitlines()]
    used=sum(x['bytes'] for x in ranges);qualified=sum(z['units']['qualified_target_units'] for z in rows);mos=sum(z['units']['MOs_units'] for z in rows)
    majority=sum(z['units']['MOs_majority'] is True for z in rows);exclusive=sum(z['units']['exclusively_MOs'] is True for z in rows)
    doc(P/'CANONICAL_NATIVE_REPORT.md',f'''# P14-v2 canonical-native source decision

**SOURCE_CONTRACT_INCONCLUSIVE**. Archive this P14 route. The new native contract resolves the requirement to reproduce an incompatible historical table, but does not establish the separate neural-observation and artifact-validity prerequisites. No neural outcomes or physiological fitting were authorized or accessed.

Mission P14-V2-CANONICAL-NATIVE-RECOVERY; BASE {BASE}. New registration2026-10-17T15:19:17.254245+00:00 preceded new canonical counts. The53-item baseline and all772 frozen historical package/reference hashes are retained. The prior confirmatory DATA_INSUFFICIENT and exploratory SOURCE_CONTRACT_INCONCLUSIVE results remain unchanged, including the exact794 movement differences, old missing masks, historical one-audited/twelve-unread state and1e-6 comparison tolerance. The new audit does not retroactively alter that historical state: it separately records the twelve additional sessions now inspected.

## Contract and interpretation

AMENDMENT.md and CANONICAL_CONTRACT.json freeze the new sampling definition. Source: [IBL Brain Wide Map, DANDI000409/0.260309.1324](https://dandiarchive.org/dandiset/000409/0.260309.1324), explicitlyCC BY4.0/OpenAccess in preserved official release evidence. Attribution belongs to the International Brain Laboratory and the documented conversion contributors. Exact asset metadata, blob identity, session/subject, size, ETag, declared digest and source receipts are retained. Only metadata ranges were downloaded; a full-file SHA256 was not recomputed.

The question remains incremental D/C predictive gain across scheduled probabilityLeft.2/.8 contexts in MEDIAL FRONTAL CORTEX. The exact target and laminar screen, one frozen simultaneous probe/session per mouse, original whole-block cut and0.5-second window remain fixed. The new rule excludes no trial using oldbwm/saturation/reaction-time masks and imports no historical unit/QC/atlas assignment. It uses canonical task events and canonical unit->electrode->localization mappings. This changes the sampling estimand prospectively with explicit owner authorization, not by claiming the old masks passed.

Movement is prospectively unavailable/version-dependent for the primary nuisance set and eligibility. Movement-independent and arousal-independent interpretation is permanently withheld. No response, reward, feedback or future count predictor was constructed; the eventual protocol would still require causal availability. Temporal holdout would be within the same animals, not independent-animal confirmation. Strong context-aware baselines and both model families remain required if scientific activation ever becomes separately possible; no family preference is inferred here.

## Exact canonical denominator

All13 historical fixed mouse/session/probe triplets were audited, including the formerly unread12. They remain a targeted historical audit frame, not an enumeration of all eligible animals in DANDI. Actual canonical task/anatomy-only potential capacity is **{potential}/13 mice**, recalculated from canonical values. Across frozen probes there are{qualified} qualified target units, of which{mos} are MOs; {majority} mice have MOs-majority selected metadata units and{exclusive} have exclusively MOs target units. Complete leaf-region compositions and every unit map are saved. These are source-QC metadata counts, not training-only physiological admissions.

{table}

The number of fully certified source-supported mice is0 currently certified; the scientifically eligible mouse count is **UNKNOWN**, not zero. Recording support and artifact validity remainUNKNOWN for all13. Physiological eligible mice are NOT_MEASURED. The>=8/6Ã¢â‚¬â€œ7/<6 operating rules therefore cannot yield a valid final eligible-cohort decision. Potential task/unit capacity does not establish admission, nor does uncertified support prove DATA_INSUFFICIENT.

ANIMAL_EXCLUSION_MATRIX.csv records every original mouse/session/probe/pid/asset and each failed or unknown gate. TRIAL_EXCLUSIONS.csv preserves original trial ordinals, context runs, half assignments and nonexclusive event/window/stimulus/context exclusion reasons. ORIGINAL_BLOCKS.csv preserves the cut before any exclusions. CANONICAL_UNIT_MAPPING.csv lists canonical IDs/UUIDs, probe/electrode/leaf/QC and exact target selection. No probe, session, date, source version or mouse was substituted; no pooling or score-based selection occurred.

## Source validity and unresolved observation evidence

Provider ibl_quality_score and canonical localization metadata are available. Canonical unit/probe/electrode relationships and matching localization tables are checked using canonical data. Unit quality is provider session/release curation; it is not newly computed A-only physiology. The native task screen requires finite ordered start/stimulus/go-cue/feedback/stop, a complete0.5-second in-trial window and available valid stimulus/context metadata. Task-event validity alone does not establish that the neural signal was continuously observed or free of documented source artifacts.

The inspected interval tables are trials and high-level epochs. No unitobs_intervals, verified recording-support/valid-observation table or native invalid/artifact/bad/saturation intervals were found in the registered metadata paths across the13 exports. The native bwm_include and saturation_stim_plus06 columns remain absent; they were not imported. No exhaustive source-scoped negative artifact certificate was established by the bounded official asset/converter documents.

The pinned converter [session epochs implementation](https://github.com/catalystneuro/IBL-to-nwb/blob/54030ac4eb40a74978ac1f6ef6e966278b9d3f34/src/ibl_to_nwb/datainterfaces/_session_epochs_interface.py) defines task time from zero to passive-phase start. That is behavioral phase labeling, not independent probe observation coverage, packet continuity or per-window artifact validity. Unit quality, electrode coordinates, nominal session duration and DANDI file existence do not fill those gaps. The requirement concerns source-defined artifacts with documented scope/completeness, not proof of absence of every physically possible artifact.

This is a bounded inspection of registered metadata fields and authoritative source documents. It is not a claim that no additional raw or provider annotations could exist anywhere. No complete-dataset download or indefinite provenance chase was attempted. The optional source-wide enumeration was not activated: counting more candidate animals cannot cure the critical observation-contract unknown. No additional dataset/source/bridge-rescue mission is automatically proposed.

## Movement and processing versions

VERSION_DIFFERENCES.md distinguishes intended measurement from verified processing. Canonical converter documentation maps historical-style firstMovement_times directly to wheel_movement_onset_time using a2025-05-06 SessionLoader revision. The old saved BWM loader and aggregate have different version history. Both fields concern first detected wheel movement; identical operational extraction/parameters, exact historical writers and per-session synchronization equivalence have not been independently established. The preserved794 discrepancies do not prove a clock fault. No tolerance increase, timestamp correction or version substitution was made.

Actual canonical Units prose describes the iblsorter/Kilosort2.5 family and three quality metrics. A converter snapshot or DANDI CLI metadata-generation version is not an exact historical spike-sorting writer certificate. Static converter task/camera QC fixtures were retained as documentary context only; they are not release-matched neural artifact/observation masks. Raw wheel/pupil/lick signals were not read or imputed. These provenance and nuisance limits remain explicit.

## Engineering evidence and scientific stop

The independently reviewed bounded reader made{len(ranges)} new exact-range attempts/{len(http)} HTTP transactions and read{used} opaque transport bytes, plus224 hash-validated prior metadata range pairs copied only into a new ignored cache. All prior cache files remain unchanged. Documentary fetching used20 fixed official URLs; all returned200. Raw opaque caches are not committed; only whitelisted metadata, static documents and receipts are archived. Adjacent uninterpreted HDF5 bytes are not decoded neural outcomes.

The38 synthetic/source regressions include protected neural/raw-behavior read denial, no neural shapes, exact range/redirect/cache identity, canonical task/chronological rules, oldmask/movement nondependence, mapping consistency and UNKNOWN-not-PASS observation handling. Reproduction verifies5 saved outputs byte-exact with network disabled. These tests are not GLM/HMM/AD validation, null tests or biological confirmation.

Full M1 physiological QC/model/numerical/falsification/statistical/one-shot holdout definitions remain incomplete because source prerequisites failed. They are retained as blocked requirements, not dropped or marked scientificallyPASS. No M2Ã¢â‚¬â€œM7, neural QC, model fit, model selection, prediction score, temporal evaluation, scientific null or findings manuscript/PDF was executed. No causal computation, isolated PFC mechanism, independent-animal confirmation, CWP/NAP claim or model-family winner is supported.

Recommendation: **archive the current P14 route and stop**. No automatic search, additional bridge-rescue, hidden relaxation or neural execution follows this mission. Saved-only reproduction: `& .\\paper14_native1\\reproduce.ps1`. Successful reproduction certifies this metadata decision and archive, not scientific validation.
''')
    write(P/'FINAL_DELIVERY.json',dict(mission='P14-V2-CANONICAL-NATIVE-RECOVERY',scientific_decision=d['scientific_decision'],LICENSE_VERIFIED=True,canonical_metadata_audited_mice=13,potential_task_anatomy_mice=potential,source_support_eligible_mice=None,source_support_unknown_mice=13,physiological_eligible_mice=None,sourcewide_enumeration_activated=False,M1_protocol_complete=False,neural_array_access=False,model_fits=0,scores=0,temporal_evaluations=0,bug_count=0,warn_count=2,warnings=['Neural recording coverage UNKNOWN','Source-defined artifact validity UNKNOWN'],reproduction='Requires executed saved-only PowerShell transcript',independent_review='Requires final complete archive review',git_remote_verification='Requires executed external closure receipt',recommendation='Archive current P14 route; stop.'))
    baseline=read(E/'baseline.json');blocked=set(range(36,41));matrix=[]
    for r in baseline['requirements']:
        i=int(r['id'].split('-')[1]);state='BLOCKED_NEED_ENV' if i in blocked else 'IMPLEMENTED_UNVERIFIED' if i in {51,52} else 'VERIFIED'
        matrix.append(dict(**{k:v for k,v in r.items() if k!='status'},status=state,evidence='paper14_native1/AMENDMENT.md; CANONICAL_CONTRACT.json; CANONICAL_NATIVE_REPORT.md; results/audit/; VERSION_DIFFERENCES.md; mission review/test receipts',verification='Conditional fullM1 source prerequisites not established; requirement retained and not executed' if i in blocked else 'Canonical saved evidence, frozen policy and tests; Git closure requires external receipt'))
    write(E/'preservation_matrix.json',dict(baseline_count=53,verified_count=46,blocked_count=5,pending_git=2,requirements=matrix,required_items_omitted=0,unresolved_shrink_risk=0,full_M1_ready=False))
    doc(E/'BLOCKER.md','''# Source observation blocker

candidate_exit: NEED_ENV
blocked requirements: REQ-036 through REQ-040, fullM1 source prerequisites
missing items: authoritative neural recording-coverage and source-defined artifact-validity evidence with scope, clock and completeness for the fixedrelease/probes/windows.
evidence: all13 canonical exports, official asset metadata, pinned epoch/converter documentation, CANONICAL_NATIVE_DECISION.json and ANIMAL_EXCLUSION_MATRIX.csv.
autonomous alternatives: audited remaining12 sessions; canonical unit/localization/task source redefinition; old movement dependence removed prospectively; native observation/invalid/artifact interval paths checked;20official documentary snapshots checked; independent source review and saved-only reproduction.
why insufficient: task epochs and quality labels are not neural observation/artifact certificates. Missing annotations cannot be declaredPASS. No oldmasktransfer or1e-6 relaxation is permitted or needed for newtaskvalidity.
exhaustion: bounded source audit complete; more animal counting cannot supply missing support provenance. No permitted code/environment repair can create authoritative source annotations, and user prohibits automatic further source/bridge-rescue.
restoration item: source-issued or otherwise authoritative release/probe/window-specific recording/artifact support; no new search or rescue is activated in this mission.
next required action: archive currentP14route and stop. No automatic neural execution or additional recovery mission.
''')
    doc(E/'verdict.md','''# Canonical-native metadata verdict

Scientific decision: SOURCE_CONTRACT_INCONCLUSIVE. Candidate terminal NEED_ENV after actual independent final review and Git/remote/clean receipts. No fullM1/source/neural/scientificPASS.

53atomic requirements retained:46verified,5source-blocked conditionalM1requirements,2pendingGit. Actual Git closure would yield48verified/5blocked. bug_count=0;warn_count=2 (recordingcoverageUNKNOWN, artifactvalidityUNKNOWN). required_items_omitted=0;required_behaviors_silently_reduced=0;unapproved_existing_behaviors_removed=0;required_tests_silently_removed=0;unresolved_shrink_risk=0;temporary_substitutes_remaining=0;coverage_reductions_without_approval=0.

Source contract was amended prospectively with explicit owner authorization; no oldfailure reclassified or post-count rule changed. Canonical task/anatomy capacity, source-supported eligibility and physiological admission remain separate. Unknown support is not a zero-mouse estimate. Movement is unavailable/versiondependent and no movement-independent claim is allowed. No neural or raw continuous behavior dataset/shapes, M2-M7, fits, scoring or final evaluation.

Required L0-L2 source/policy tests and saved-only native PowerShell reproduction; final executed receipts certify exact test/result/hash counts. These are not model/AD/null/biological tests. No UI/channel/screenshot requirement applies. Final review only permits exact blocked archive, not MERGE_ALLOWED/fullM1. Source/prospective reviews and all raw receipts preserved.

Deletion/narrowing audit: old packages unchanged across772hashes; daily priorbody byte-exact BASE; mission-only newfiles/header. No thresholds weakened, tests removed, dates/probes substituted or cohorts pooled. No mass source-wide recovery activated. Freeze and actual external closure_receipt.json bind final candidate, GitSHA, allchangedremoteblobs andclean tree; no prospectiveGitPASS.
''')
    previous=subprocess.check_output(['git','show',BASE+':ops/daily-operations.md'],cwd=ROOT)
    header=f'''# Current mission: P14-V2-CANONICAL-NATIVE-RECOVERY

Scientific SOURCE_CONTRACT_INCONCLUSIVE, metadata-only canonicalnative amendment. BASE{BASE};all13historical sessions audited includingprevious12unread;{potential}canonicaltask/anatomy-onlypotentialmice, source-supportedeligible/physiologicalcountsUNKNOWN. No oldbwm/saturationmasktransfer or1e-6relaxation;old794differences/sourceFAIL/confirmatoryFAIL preserved. Nativeunit/localization/QC andbothcontextcapacities reported; taskepochs arenotneuralrecording/artifactcertificates. BothessentialobservationsupportgatesUNKNOWN;source-wideenumerationnotactivated.

38synthetic/source tests and5savedoutputs withnetworkdenied;772historicalhashes unchanged.53requirements retained,5conditionalfullM1requirements sourceblocked;bug0/warn2. No neuralarrays/shapes/rawbehavior,QC/fits/modelselection/scores/temporalassessment/M2-M7. Report paper14_native1/CANONICAL_NATIVE_REPORT.md;reproduce & .\\paper14_native1\\reproduce.ps1. Independentreview/normalorigin-test/readback/clean certifiedonlybyexecuted externalreceipt. RecommendarchivecurrentP14route;stop,noautomaticnewsource/bridgerescue/neuralmission. Priorheaderspreservedbyteexactbelow.

---
'''
    (ROOT/'ops/daily-operations.md').write_bytes(header.encode('utf8')+previous)
    import numpy,h5py,requests
    write(P/'RUNTIME.json',dict(python=platform.python_version(),numpy=numpy.__version__,h5py=h5py.__version__,requests=requests.__version__))
    hashes={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.rglob('*')) if p.is_file() and not {'work','__pycache__'}&set(p.relative_to(P).parts) and p.name!='PAYLOAD_HASHES.json'}
    write(P/'PAYLOAD_HASHES.json',dict(hashes=hashes,scope='All canonical-native package files excluding work/,__pycache__,self; prior772 separately frozen'))
    print(json.dumps(dict(payload=len(hashes),potential=potential,qualified_units=qualified,MOs_units=mos,range_attempts=len(ranges),http_requests=len(http),bytes=used)))
if __name__=='__main__':main()
