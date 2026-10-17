"""New scientific estimand and source screen registered before expanded counts."""
import datetime,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent.parent;P=R/'paper14_pivot1';E=R/'ops/evidence/2026-10-16/p14-m1-bounded-context-pivot'
BASE='c02eadba8e4770490f2f8a5787a90dfaa5b38550';MISSION='P14-M1-BOUNDED-CONTEXT-PIVOT'
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(obj,f,indent=2);f.write('\n')
def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()==BASE
    E.mkdir(parents=True,exist_ok=True)
    reqs=[
    'Exact BASE/fresh remote preflight; clean initial tree; one bounded mission',
    'Freeze populated atomic baseline, new estimand/anatomy/screens before new eligibility counts',
    'Preserve every historical P14/P1-P13 failure, source freeze, review and strict mPFC8 result',
    'No neural values, fitting/scoring/final access, no extra dataset search or cryptographic architecture',
    'New probabilityLeft0.2vs0.8 contrast is experimenter scheduled prior, not observed belief or rewritten DR result',
    'DANDI000409 exact public CC-BY4 release identity/license/provenance verification',
    'Reuse compatible existing IBL metadata; do not download full dataset or assume cross-version equality',
    'Register single expanded target MOs+ACAd+ACAv+PL+ILA exact laminar descendants on same probe',
    'Label expanded target medial frontal cortex, never single PFC leaf',
    'Report full region composition, MOs dominance and strict-composite comparator without reselecting anatomy',
    'Source-specific unchanged justified unit threshold registered before counts',
    'Source-specific trial/block/context/temporal/screens registered before counts',
    'Observation support and source saturation/quality/timebase boundaries registered',
    'Canonical mouse/session/probe identities; one same-probe/session per mouse; no pooling or pseudoreplication',
    'At least8development plus8independent final mice, no floor relaxation',
    'Both contexts and adequate observations in each chronological whole-block half',
    'Actual source task event timing, wheel/lick/movement variables and metadata quality verified or explicit unresolved',
    '139all-source mice never treated as eligible target cohort',
    'Expanded target below16 -> DATA_INSUFFICIENT; no other dataset or threshold tuning',
    'If viable freeze exact source and animal identities',
    'If viable freeze anatomical target/composition/context labels and fixed dev/final allocation',
    'If viable freeze actual trial/observation masks and A/C-only physiological QC',
    'If viable freeze strong B0-B4 stimulus/time/history/behavior baselines',
    'If viable freeze tractable discrete2stateHMM and continuous2Dhistory models, no favored winner',
    'If viable freeze two new context-interaction hypotheses',
    'If viable freeze numerical gradients, PG/solver/stopping and causal-prediction validation',
    'If viable freeze scientifically defensible finite nulls, no unstable P13 conditional Bstar generator',
    'If viable freeze equal-mouse inference, corrections, sensitivities and one held-out final assessment',
    'Exactly one grounded owner scientific outcome; only READY permits future Prompt3 consideration',
    'If infeasible recommend archive instead of indefinite recovery chain',
    'Exact source/animal/context/region denominators and exclusion records',
    'Bounded synthetic identity/context/timing/composition/source compatibility tests',
    'Saved-only native PowerShell reproduction, frozen hashes and no new model evaluation',
    'Independent internal scientific/source review; preserve unsuccessful evidence and repair defects',
    'Full atomic preservation matrix, bugs/warnings, explicit scientific limitations and no fakePASS',
    'Exact-file normal origin/test commit; no force/main/PR',
    'Live remote SHA, all changed-file hashes and clean tree readback',
    'Final handoff with status/evidence/review/Git/blocker/nextaction; STOP after this bounded decision'
    ]
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    write(E/'baseline.json',dict(mission=MISSION,base=BASE,frozen_at=now,count=len(reqs),requirements=[dict(id=f'REQ-{i:03}',requirement=s,status='OPEN') for i,s in enumerate(reqs,1)]))
    write(P/'REGISTRATION.json',dict(mission=MISSION,base=BASE,registered_at=now,before_expanded_eligibility_counts=True,
      scientific_amendment='New priorLeft interaction estimand; original DynamicRouting auditory/visual experiment and all failed gates remain immutable. No P14 neural predictive outcomes examined.',
      source=dict(dandiset='000409',published_version='0.260309.1324',status='Verify exact published version and CC-BY4 from official API before adoption; no release substitution',reuse='Existing pinned2024_Q2_IBL_et_al_BWM clusters/trials/fixture and M0 behavior-only extras. Join to DANDI lineage/identities where independently supported; mismatch cannot be waived.'),
      contexts=dict(low_priorLeft=.2,high_priorLeft=.8,neutral_excluded=.5,meaning='Experimenter-scheduled uncued block prior; not directly measured belief, no neural-derived context'),
      strict_historical='Exact ACAd/ACAv/PL/ILA same-probe metadata result8candidates preserved, not expanded retrospectively',
      expanded_target=['MOs','ACAd','ACAv','PL','ILA'],anatomy='Exact atlas acronym or laminar descendants 1/2/3/4/5/6a/6b only; no orbital/lateral/MOp. Label medial frontal cortex. Same simultaneous probe population throughout contexts/halves.',
      rationale='A prospective heterogeneous medial-frontal sampling target that includes premotor MOs is scientifically plausible for task/context prediction but changes anatomical scope; no uniform PFC mechanism, belief or regional localization claim. Preserve composition, report MOs fraction and whether>50percent; no post-count anatomy choice.',
      unit_screen=dict(minimum_provider_good_units=10,label='exact provider label==1; externally curated full-session frame, not A/Cphysiology; missing notgood',future='A/C-only physiology separate, must retain>=10units on frozenprobe. No spikes accessed now.'),
      trial_screen='Reuse exact M0 IBL session_blocks algorithm: required finite interval/start/stim/goCue/feedback/stop;start<=stim<=goCue<=feedback<=stop;stim+.5<=stop;bwm_include=True;saturation_stim_plus06=False. Missing timing/masks fail closed. Masks are source/exclusion metadata, never causal predictors. Record outcome-dependent source frame limitation.',
      blocks='Maximal contiguous original-trial probabilityLeft runs before filtering; neutral/unknown breaks. Original trial-order stimulus times strictly increase. Cut all nonneutral runs atfloor(K/2); first whole-block half A/C, last B/EorD. Runs<15valid trials notqualifying but never merged/removed before cut.',
      observations=dict(min_valid_trials_qualifying_run=15,min_qualifying_runs_each_context=2,min_usable_trials_each_context_each_half=60,prediction_window=[0,.5],bin_seconds=.1,min_development=8,min_final=8),
      support='Provider curated active-task intervals and saturation mask, finite within-trial timestamps, documented ephys timebase; never infer neural recording support from spike endpoints or field names. DANDI/aggregate source equality and any needed packet/annotation support remain explicit gates. No full-record raw values.',
      selection='Among qualifying same-probe target populations choose most good units, then greatest minimum4context-half cells, then lexical eid/pid. One canonical mouse only; report all exclusions/otherprobes, no cross-session pooling.',
      allocation='Only if >=16verifiedmetadata-qualified independent animals and source gates pass: sortSHA256(ASCII P14-IBL-MFC-V1|canonical_mouse_id), firstfloor(n/2)development,lastremainingfinal. No replacements/swaps. Do not execute allocation before source compatibility established.',
      MOs_dominance='For each selected probe list all five good-unit counts;MOsfractionofexpandedgood;>0.5 dominance descriptive flag, not tuned eligibility rule. Future mandatoryMOs-removal sensitivity must retain>=8paired final mice or broad composite claims INCONCLUSIVE, never retargetafteroutcomes.',
      new_hypotheses=['Delta_D=(LL(D)-LL(B4))_pLeft0.2-(LL(D)-LL(B4))_pLeft0.8','Delta_C=(LL(C)-LL(B4))_pLeft0.2-(LL(C)-LL(B4))_pLeft0.8'],
      conditional_freeze='Complete fullM1onlyif>=8+8and source/clockcompatible. If below16 STOP DATA_INSUFFICIENT, recommendarchive; no otherdataset or floor change.',
      access=dict(allowed='Source/license/provenance API JSON, official docs/code, reused whitelisted identity/anatomy/label/discrete trial metadata. No SDKfallthrough, fullNWB, spike/count/amplitude/waveform/rawbehavior arrays, fits/scores/finalvalues.',http_attempts=100,total_bytes=30000000,single_response_bytes=5000000,attempts_per_request=2),
      interpretation='Conditional observational predictive structure; no direct beliefs, causality, movement/arousal independence, unit/session pseudoreplication or independent-lab proof',stop='One bounded P14M1decision; no automatic nextmission, email or newdataset search.'))
    hashes={}
    paths=[]
    for d in ['paper14_m0','paper14_m1','paper14_open1']:
      paths.extend(f for f in (R/d).rglob('*') if f.is_file() and not {'work','__pycache__'}&set(f.relative_to(R/d).parts))
    for name in ['M0_SOURCE_PIN.json','M0_REGISTRATION.json','metadata/fixture.csv','metadata/fixture.csv.receipt.json','metadata/clusters_metadata.csv.gz','metadata/trials_metadata.csv.gz','metadata/atlas.json','metadata/clusters_schema.json','metadata/trials_schema.json','metadata/bwm_loading.py.source','metadata/bwm_loading.py.source.receipt.json','metadata/release_documentation.html']:
      paths.append(R/'paper13'/name)
    for f in sorted(paths):hashes[f.relative_to(R).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
    write(P/'INPUT_FREEZE.json',dict(base=BASE,hashes=hashes,scope='AllhistoricalP14packages plus exact reused IBLmetadata only; no neural artifacts'))
    write(E/'mission.json',dict(mission=dict(id=MISSION,objective='One prospective IBL prior-context/expanded medial-frontal metadata screen and conditional M1freeze; preserve historical strict8 and stop honestly if insufficient.'),target=dict(workdir=str(R),files=['paper14_pivot1/**',E.relative_to(R).as_posix()+'/**','ops/daily-operations.md']),instructions=dict(requirements=reqs,constraints=['No new neural values/fits/scores/finalaccess','OnlyDANDI000409/IBL; no datasetsearch','No thresholdrelaxation']),acceptance=dict(validation=['Syntheticmetadata tests','Saved-onlyPowerShell','Independentreview','origin-test/readback/clean']),metadata=dict(base=BASE)))
    (E/'goldenstandards.md').write_text(f'''# Prospective bounded scientific pivot\n\nMission {MISSION}; BASE {BASE}; registered {now}. {len(reqs)} frozen atomic requirements in baseline.json.\n\nApproved scientific decision block: estimate scheduled priorLeft0.2minus0.8 predictive interactions, target exact MOs+ACAd+ACAv+PL+ILA on one probe and call it medial frontal cortex. Preserve strict composite8 and all DRhistory. At least8development+8final; counts below16 mandate DATA_INSUFFICIENT and archive recommendation. Source DANDI000409 exact version/license verified before adoption; reused metadata needs source compatibility, not an assumption. No remaining intent ambiguity.\n\nHEAD=origin/test=BASE, initial tree clean; no origin/main exists, TEST_ONLY_REMOTE_NO_MAIN. UserK4C applies; absent opsfoundation/engineer/review/templates are not invented. Use narrow explicit files.\n\nPlan: freeze rules -> official release/source/provenance -> reuse historical whitelisted tables -> strict8regression/newexpandedcounts -> exact animal/context/composition/supportaudit -> fullM1onlyiffeasible, otherwise precise stop -> synthetic tests/saved reproduction -> independent review -> exactGitarchive/remotehash/clean. No fits or raw arrays.\n\nVerificationL0-L2 metadata/source/synthetic; oracle is exact stable source/identity/trial masks and independent-animal denominators, MOscomposition, causal leakage/unknown failclosed and unchanged history. Preserve all failed receipts. No results-driven anatomy/mask/threshold choices, no fake fullM1PASS.\n''',encoding='utf8',newline='\n')
    write(E/'REGISTRATION_RECEIPT.json',dict(utc=now,base=BASE,baseline=len(reqs),historical_input_hashes=len(hashes),branch='test',initial_clean=True,remote_relation='TEST_ONLY_REMOTE_NO_MAIN'))
    (P/'__init__.py').write_text('"""Bounded IBL medial-frontal metadata context pivot; no neural loader."""\n',encoding='utf8')
    (P/'.gitignore').write_text('work/\n__pycache__/\n',encoding='utf8')
    print(json.dumps(dict(baseline=len(reqs),historical_hashes=len(hashes),registered_at=now,before_counts=True)))
if __name__=='__main__':main()
