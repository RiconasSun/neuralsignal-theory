"""Prospective registration, before any new candidate eligibility calculation."""
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

R=Path(__file__).resolve().parent.parent
P=R/'paper14_open1'
E=R/'ops/evidence/2026-10-16/p14-m1-open-release-recovery'
BASE='35e344278cd25574764290b54550ec82d7e963a2'
MISSION='P14-M1-OPEN-RELEASE-RECOVERY'

def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n') as f: json.dump(obj,f,indent=2);f.write('\n')

def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()==BASE
    E.mkdir(parents=True,exist_ok=True)
    owner=Path(r'C:\Users\85993\.codex\attachments\fea8cb0c-d416-40ba-b5d8-303af893b0e1\已粘贴的文本.txt')
    (E/'OWNER_MISSION.txt').write_bytes(owner.read_bytes())
    requirements=[
    'Exact BASE and fresh remote branch classification; preserve initial clean tree',
    'One bounded mission, atomic baseline prospectively frozen before implementation/counts',
    'Preserve all P1-P13 and historical M0/M1 findings, identities, reservation, reviews and evidence',
    'No spike values, neural arrays, model fitting, neural scores or final assessment',
    'No continuous raw behavior samples, email, custody infrastructure or automatic next mission',
    'Official AWS AIND Open Data entry and permitted anonymous access verified',
    'Exact release/asset identity and processing version recorded',
    'Applicable explicit license covering selected objects; do not transfer across buckets',
    'Analysis/publication rights, attribution and redistribution terms recorded',
    'Recording/sorting/anatomy/processing provenance and limitations documented',
    'Original eighteen mouse/session/probe identities retained in matching table',
    'Exact date/session UUID and recording version distinguished from same mouse other date',
    'EXACT_SESSION_MATCH/SAME_MOUSE_DIFFERENT_SESSION/NO_VERIFIED_MATCH/RIGHTS_UNRESOLVED statuses',
    'No HDF5/Zarr or cohort equivalence inferred from mouse IDs',
    'If all original18 recovered assess schema equivalence; otherwise never call original cohort recovered',
    'If necessary prospectively register new licensed-cohort rules before eligibility counts',
    'Preserve within-session auditory/visual rewarded context question',
    'Exact ACAd/ACAv/PL/ILA descendants, same single probe/population; no MOs/orbital inclusion',
    'Canonical cohort inventory computed from licensed source metadata rather than imported scratch masks',
    'Use unchanged justified M0 thresholds; source-specific exceptions registered before counts',
    'At least eight development and eight final mice, prefer larger feasible roster',
    'No repeated mouse/session/probe pseudoreplication, no score-driven selection or threshold rescue',
    'At most one additional explicitly licensed context-PFC source if DR insufficient; no unbounded search',
    'Spike sorting and anatomical source provenance matrix',
    'Stimulus/reward context semantics and causal timing matrix',
    'Behavior/neural synchronization documentation; field names alone never prove actual quality',
    'Recording support and source exclusions/saturation annotations',
    'Running/lick/pupil availability and missingness separately recorded',
    'Exact missing response timestamps preserved; no flag-based event imputation',
    'Prospective source-supported missingness/exclusion and recomputed eligibility; essential timing stop',
    'Narrow estimand explicitly forbids unmeasured movement/arousal independence and causal mechanism claims',
    'Freeze A dataset/source revision/license if feasible',
    'Freeze B exact candidate mouse/session/probe roster if feasible',
    'Freeze C independent development/final identities with no swapping before neural outcomes if feasible',
    'Freeze D anatomy and subregion composition if feasible',
    'Freeze E both context labels and trial/epoch masks if feasible',
    'Freeze F A/C-only physiological QC if feasible; source QC distinguished',
    'Freeze G causal covariates/exclusions/scalers if feasible',
    'Freeze H all model equations if feasible',
    'Freeze I complexity/selection policies if feasible',
    'Freeze J numerical acceptance/stopping thresholds if feasible',
    'Freeze K animal-level statistics/multiplicity if feasible',
    'Freeze L finite defensible nulls/falsification if feasible; no unstable P13 autoregressive generator',
    'Freeze M sensitivities/coverage if feasible',
    'Freeze N one-time final holdout policy if feasible',
    'Retain two primary Delta_F=[LL(F)-LL(B4)]aud-[LL(F)-LL(B4)]vis hypotheses',
    'Mandatory B0-B4 task/stimulus/time/own/population/causal behavior strong baselines',
    'Tractable two-state Poisson HMM and two-dimensional continuous history, mathematical validation required',
    'No presumed family winner or post-outcome redesign',
    'Licensing gate supports actual chosen objects',
    'Independent-animal and both-context denominator gate',
    'Prospective allocation before outcomes gate',
    'Timebase/event semantics gate',
    'Full scientific model/statistical specification gate',
    'Bounded synthetic identity tests',
    'Bounded synthetic timing/missingness tests',
    'Bounded synthetic protocol/null-definition tests, not neural-model fitting',
    'Independent internal scientific/source review; retain unsuccessful reviews and fix in-scope defects',
    'Exactly one grounded scientific decision from the four owner outcomes',
    'READY never means physiological QC passed or neural execution authorized',
    'Source/license evidence artifact and eighteen-session matching artifact',
    'New-cohort inventory if necessary and exact animal/context denominator',
    'Timing/measured-behavior matrix and source/amendment registration record',
    'Complete scientific protocol if feasible, otherwise exact missing gate report without fabricated freeze',
    'Saved-only native PowerShell one-command reproduction with hash/integrity checks',
    'Full requirement preservation matrix, scientific limitations and bug/warning counts',
    'Normal exact-file origin/test archive, no force/main/PR',
    'Live full remote SHA, changed-file manifest/hash readback and clean tree',
    'Final status/evidence/review/blockers/next action; STOP after M1 recovery',
    ]
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    write(E/'baseline.json',dict(mission=MISSION,base=BASE,frozen_at=now,count=len(requirements),requirements=[dict(id=f'REQ-{i:03}',requirement=s,status='OPEN') for i,s in enumerate(requirements,1)]))
    hashes={}
    for root in [R/'paper14_m0',R/'paper14_m1']:
        for f in sorted(root.rglob('*')):
            if f.is_file() and 'work' not in f.relative_to(root).parts and '__pycache__' not in f.parts:
                hashes[f.relative_to(R).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
    write(P/'INPUT_FREEZE.json',dict(base=BASE,hashes=hashes))
    reg=dict(mission=MISSION,base=BASE,registered_at=now,before_new_eligibility_counts=True,
      known_history='M0/M1 publicly inspected behavior/anatomy metadata; no P14 neural values/outcomes inspected. New AWS registry read describes dataset-wide CC-BY-4.0 on aind-open-data; inspect binding and terms, no scratch license transfer.',
      scope='Official Dynamic Routing open releases first, across released processing versions; original18 reconciliation is separate from prospective canonical-only cohort.',
      release_snapshot='Freeze API result and processing/source/asset IDs, S3 metadata hashes and receipts; no assertion of immutable bucket. Prioritize latest npc_sessions conversion per exact session, version parsed semantically, then creation date/asset ID lexical; preserve all alternatives.',
      primary='brainwide AND provider behavior pass; no naive/Templeton/perturbation pooling. Require explicit source flags/documentation; missing is unresolved.',
      anatomy='ACAd/ACAv/PL/ILA exact laminar descendants, finite CCF coordinates, provider QC; one same probe same units supported in both contexts. No MOs/ORB.',
      original_thresholds=dict(provider_good_units=10,min_valid_trials_block=15,min_blocks_each_context=2,min_trials_each_context_half=60,min_development=8,min_final=8),
      trial_policy='Original six scheduled blocks; first five scheduled trials each excluded before masks; planned opto or unknown excluded; finite ordered trial/stimulus/stop times and 0.5s window within trial. Whole original block halves 1-3 vs4-6. Require exact aud/vis labels; no outcome-dependent engagement admission.',
      missing_event_policy='For any trial with response/reward flag true and nonfinite corresponding event timestamp exclude the entire trial from all primary/sensitivity bin masks, before counts; flag false requires no event. Never impute. This stricter canonical-source rule is registered before new counts and preserves original scratch masks/evidence.',
      support='Finite sorted nonoverlapping unit obs_intervals or explicit source recording support; every retained prediction window supported. Missing mandatory support/QC/clock evidence stays unresolved, never good.',
      selection='Among eligible metadata single probes choose greatest qualified unit count, greatest minimum four context-half count, then lexical session/probe; one per mouse, no model scores. Preserve alternative rows.',
      allocation='If >=16 qualified independent candidates sort SHA256(ASCII P14-OPEN-V1|canonical_mouse_id); first floor(n/2) development, rest final; no replacement/swap. Actual physiology remains unmeasured.',
      interpretation='Conditional on available measured task variables; permanently no movement/arousal-independent, causal/ontological, NAP/CWP or independent-lab replication claims.',
      access=dict(metadata_only=True,no_neural=True,no_raw_continuous_behavior=True,no_sdk=True,allowed='Official docs/metadata API/S3 object listings/JSON descriptors plus explicitly registered unit anatomy/QC/support and discrete trial-event columns. Never full NWB, spike values, waveforms or raw continuous channels. Inspect descriptors before registering any canonical column GET.'),
      budget=dict(attempts=900,total_bytes=120000000,single_response_bytes=8000000,attempts_per_request=2,max_sessions=500,additional_datasets=1),
      endpoints=['registry.opendata.aws','allenneuraldynamics.github.io','docs.allenneuraldynamics.org','api.allenneuraldynamics.org','raw.githubusercontent.com official repositories','api.github.com official repositories','aind-open-data.s3.us-west-2.amazonaws.com registered metadata paths','creativecommons.org/licenses/by/4.0/'],
      stop='No neural activation; exact source/timing/denominator failure -> report grounded owner outcome. Complete protocol only if prerequisites verified. No correspondence, no automatic additional mission.')
    write(P/'REGISTRATION.json',reg)
    write(E/'mission.json',dict(mission=dict(id=MISSION,objective='Resolve licensed P14 source route and freeze complete M1 only if source/timing/cohort gates justify it; otherwise evidence-backed bounded scientific stop.'),target=dict(workdir=str(R),files=['paper14_open1/**',str(E.relative_to(R))+'/**','ops/daily-operations.md']),instructions=dict(requirements=requirements,constraints=['No neural/raw continuous behavior samples or model fitting/scoring/final evaluation','Preserve all historical files; no email']),acceptance=dict(criteria=['All atomic requirements traceable; no fabricated readiness'],validation=['Saved-only PowerShell reproduction, synthetic tests, independent review, verified origin/test']),metadata=dict(base=BASE)))
    (E/'goldenstandards.md').write_text(f'''# Prospective requirement baseline\n\nMission {MISSION}; BASE {BASE}; frozen {now}.\n\n{len(requirements)} atomic items in baseline.json. No product/outcome ambiguity: the owner permits canonical-source recovery, new prospective licensed cohort if needed, and exactly one additional dataset at most. Original scratch history and 9/9 reservation are immutable. Scientific protocol completion is conditional on source/clock/cohort gates; no fake PASS.\n\nPreflight: HEAD=origin/test=BASE; origin/main absent (TEST_ONLY_REMOTE_NO_MAIN); initial tree clean. User K4C governs; ops foundation/engineer/review files absent, no invented templates.\n\nProduct decision: provide a scientifically defensible prospective P14 source/protocol, using applicable open licenses without researcher-permission ceremony. Primary actor is research owner. Preserve old findings and separate canonical cohort; no neural access.\n\nTest level L0-L2 metadata/synthetic only. Oracle: pinned metadata identities/permissions/schema/timing/denominators, original-versus-canonical match invariants, causal masks, finite null definitions, byte-exact saved reproduction with network blocked. Model tests do not claim real-model correctness until separately implemented.\n\nPlan: license and complete canonical inventory -> original18 reconciliation -> canonical descriptors and registered metadata-only fields -> source/cohort/timing audit -> conditional scientific freeze -> tests/saved reproduction -> independent review -> exact file archive and remote clean gate. No thresholds weakened; every unmet requirement remains traceable.\n\nNo external messages, raw arrays, scoring, fitting, cryptographic custody or next mission. Full engineering PASS requires zero bugs/warnings/shrink risk and all applicable items verified; scientific insufficiency remains explicit even if the diagnostic archive is sound.\n''',encoding='utf8',newline='\n')
    (P/'.gitignore').write_text('work/\n__pycache__/\n',encoding='utf8')
    (P/'__init__.py').write_text('"""P14 open-release metadata recovery; no neural data loader."""\n',encoding='utf8')
    write(E/'REGISTRATION_RECEIPT.json',dict(utc=now,base=BASE,baseline=len(requirements),historical_hashes=len(hashes),branch='test',remote_relation='TEST_ONLY_REMOTE_NO_MAIN',initial_clean=True,owner_sha256=hashlib.sha256(owner.read_bytes()).hexdigest()))
    print(json.dumps(dict(baseline=len(requirements),historical_hashes=len(hashes),registered_at=now)))

if __name__=='__main__':main()
