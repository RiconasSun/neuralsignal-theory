"""Prospective Prompt4 contract registration; no neural reads or model imports."""
from pathlib import Path
import csv
import datetime
import hashlib
import json
import subprocess

R = Path(__file__).resolve().parents[4]
E = R / 'ops/evidence/2026-10-18/p15-m6-independent-final-validation'
BASE = '47608d2db5bae32b150e6fccd9567c059fe43e63'
OWNER = Path(r'C:\Users\85993\.codex\attachments\83803580-afd2-44b5-bc6a-fb155483a2e9\已粘贴的文本.txt')


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(p, obj):
    Path(p).write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n', encoding='utf-8')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=R).decode().strip()


assert git('rev-parse', 'HEAD') == git('rev-parse','origin/test') == BASE
assert git('branch', '--show-current') == 'test'
assert not (R/'paper15_final1').exists()
E.mkdir(parents=True, exist_ok=False)
when = datetime.datetime.now(datetime.timezone.utc).isoformat()
(E/'OWNER_MISSION.txt').write_bytes(OWNER.read_bytes())
requirements=[]
for number, line in enumerate(OWNER.read_text(encoding='utf-8-sig').splitlines(), 1):
    text=line.strip()
    if not text or text.startswith('#') or text in ['origin/test @ '+BASE,'BASE:', 'PRIORITY: HIGH','MODE: SCIENCE-FIRST / FROZEN PROTOCOL / ONE FINAL ASSESSMENT'] or text.startswith('MISSION:'):
        continue
    requirements.append(dict(id=f'REQ-{len(requirements)+1:03}',requirement=text,owner_line=number,status='OPEN'))
dump(E/'baseline.json',dict(mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',base=BASE,
    baseline_frozen_at=when,baseline_revision=1,baseline_requirement_count=len(requirements),
    source_sha256=digest(OWNER),requirements=requirements,
    interpretation='Every non-heading owner source line retained as an individually traceable obligation, including explanations, exact output fields and all named conjunctive acceptance bullets. Frozen M1 predicates additionally retain their named scientific test map.'))
m1=json.loads((R/'paper15_m1/PROTOCOL_FREEZE.json').read_text())
for rel,h in m1['hashes'].items(): assert digest(R/'paper15_m1'/rel)==h,rel
archive=json.loads((R/'paper15_r1/ARCHIVE_FREEZE.json').read_text())
for rel,h in archive['hashes'].items(): assert digest(R/'paper15_r1'/rel)==h,rel
for rel,h in archive['external_hashes'].items(): assert digest(R/rel)==h,rel
roster=list(csv.DictReader((R/'paper15_m1/COHORT.csv').open(newline='')))
final=[r for r in roster if r['allocation']=='FINAL_RESERVED']
assert len(final)==8 and len({r['subject'] for r in final})==8
selection=json.loads((R/'paper15_r1/SELECTION_FREEZE.json').read_text())
assert selection['selected']==dict(B0='B0',B1='B1_l0.01',B2='B2_l0.01',B3='B3_l1.0',B4='B4_l0.1',C='C_r1_t0.1_l0.1',D='D_k3_l0.01',S='S_k4_l0.01')
dump(E/'PRESERVATION_REGISTRATION.json',dict(time=when,base=BASE,prechange_tree=git('rev-parse','HEAD^{tree}'),
    original_daily_bytes=(R/'ops/daily-operations.md').stat().st_size,
    original_daily_sha256=digest(R/'ops/daily-operations.md'),
    M1_freeze_sha256=digest(R/'paper15_m1/PROTOCOL_FREEZE.json'),M1_files_verified=len(m1['hashes']),
    R1_archive_sha256=digest(R/'paper15_r1/ARCHIVE_FREEZE.json'),R1_files_verified=len(archive['hashes']),
    R1_external_files_verified=len(archive['external_hashes']),
    selection_sha256=digest(R/'paper15_r1/SELECTION_FREEZE.json'),selection=selection['selected'],
    final_roster=final,Final_C_neural_access=False,Final_D_neural_access=False,real_fits=0,
    historical_attempts=359,R1_corrective_attempts=1135,cumulative_pre_Final=1494,
    preservation='All prior papers/M0/M1/Dev/R1/failed reviews/partial attempts unchanged; only new final package/evidence and prepended current daily header may change.'))
remote=git('ls-remote','--heads','origin','refs/heads/main','refs/heads/test')
dump(E/'BRANCH_PREFLIGHT.json',dict(time=when,fetch_completed_before_registration=True,branch='test',HEAD=BASE,origin_test=git('rev-parse','origin/test'),
    remote_readback=remote,origin_main=None,classification='TEST_ONLY_REMOTE_NO_MAIN',working_tree_before_bootstrap='CLEAN',force=False))
dump(E/'mission.json',dict(mission=dict(id='P15-M6-INDEPENDENT-FINAL-VALIDATION',objective='Frozen eight-mouse Final source/C calibration and conditionally one D scientific assessment; reviewed handoff then STOP'),
    target=dict(workdir=str(R),files=['paper15_final1/**',E.relative_to(R).as_posix()+'/**','ops/daily-operations.md']),
    instructions=dict(requirements_file=str(E/'baseline.json'),constraints=['Frozen M1 and exact R1 selection','No Development rerun','No D neural scientific use before complete reviewed pre-D gate','No C fit retry, D replacement, scientific amendment, new dataset or cryptographic architecture','No Prompt5/PDF'],
    implementation_workflow='Reuse previously accepted local scoped tools. Prior external CLI orchestration was auto-review rejected; do not repeat that path or transmit protected source/data to another service.'),
    acceptance=dict(criteria=['Every original obligation traceable','Scientific reporting preserves all negative/mixed/unavailable outcomes','Source/C stop branch if required gate fails','Independent internal scientific/numerical review','Saved-only native PowerShell reproduction','Normal scoped origin/test commit/remote blob verification/clean gate']),
    openrouter=dict(enabled=False)))
(E/'goldenstandards.md').write_text(
    '# Prospective Final mission requirement baseline\n\n'
    f'Mission P15-M6-INDEPENDENT-FINAL-VALIDATION. Exact BASE {BASE}; frozen {when}; {len(requirements)} owner line-level obligations in baseline.json. ENGINEER_MODE: scientific behavior, actor, access boundaries, models, outcomes and stopping branches already explicit; no new scientific design.\n\n'
    'Sequence: verify historical/source hashes and selection -> versioned Final-native metadata/partition masks -> independently reviewed C-only trusted-reader projection and synthetic production tests -> C physiology only -> cohort/source gate -> up to12selected main attempts/mouse and original11case baseline calibrations -> complete model/preprocessing/case freeze -> independent scientific/numerical pre-D review and full synthetic or C-only batch rehearsal -> exactlyone D batch only if every required gate passes -> complete sixcontrast/sensitivity/four999reference reporting or preserved source/C-only STOP -> saved-only reproduction/review/normal origin/test handoff -> STOP.\n\n'
    'Preserve all prior directories and failed evidence; never rewrite R1 Development. New code/artifacts only paper15_final1 and this evidence; daily original bytes remain a suffix. Original M1 scientific definitions and R1 B-selected globals immutable. Minimal ordinary local scientific controls; no new signing/custody infrastructure.\n\n'
    'Trusted low-level reader may decode whole-record spike time/cluster ALF arrays only to classify/export C observations. No D neural counts, QC/range summaries, scaling, selection, streams or fitted parameters reach scientific roles pre-D. Unassignable timestamps cannot silently become zero or be imputed; fail closed with a generic source-classification error without D summaries. Provider upstream whole-session curation/header identities remain explicitly upstream. C within-role spike ordinals include outside-epoch observations for exact S07; no D stream consumed. D-only integrity errors discovered during one authorized batch cannot cause C repair/unit replacement/retry.\n\n'
    'Frozen limits: Final main<=12/mouse,<=96 total; sensitivity<=5per applicable case,<=440 total; no retries. Keep old359 and corrective1135 separately; never claim retrospective compliance with original aggregate1928 ceiling. This current explicit Final authorization supplies its96/440caps; track actual full historical cumulative count without hiding old attempts. No budget increase inside this mission.\n\n'
    'Source floors >=80C/>=60Dmetadata epochs,8units,unchanged physiology. Eightprimary-mice/4labs and<=50%one lab necessary but not sufficient for positive labeling;6–7 descriptive,less6source/C-onlySTOP. Independence/sign-symmetry assumptions cannot be proved from this observational convenience cohort: independent pre-D review must explicitly qualify them; retain frozen statistic and withhold confirmatory interpretation if not defensible. No D-driven assumption pretest or alternative test. Sensitivity/reference availability follows exact original gates; missing mandatory positive-claim coverage is reported and cannot be rescued.\n\n'
    'Oracle L0-L2: bitwise native clocks/strict< wheel/causal features, C-only projection canaries including hidden D corruption, exact model/objective/PG/independentAD/allthreeFD thresholds, complete state schemas/identity/tamper/one-batch guard, original synthetic HMM/state/reset/reference operators and inference. Production gate before realC fitting; synthetic tests cannot stand in for actualC physiology/numerics or D results. No real stage repetition after essential failure; preserve started/failed/partial artifacts.\n\n'
    'PASS means complete approved mission branch and reviewed truthful scientific report or required source/C-only stop report, not necessarily a positive scientific finding. Terminal transport PASS requires every applicable baseline row verified,bug0warn0,no shrink,exact scoped origin/test normal push/readback/clean. Named scientific verdicts are reported separately. Full source and frozen-stage hashes bind final relevant proof. No new mission or Prompt5 without explicit authorization.\n\n'
    'Skills: nsi-paper-builder reproducibility/claim discipline, no manuscript/PDF in this mission; codex-code-wrapper Mission Spec and scoped write discipline. Optional ops foundation/engineer/review/templates absent at bootstrap; no invented template requirement or unrelated framework. Prior rejected external CLI route not retried; scoped local tools remain authorized.\n',encoding='utf-8')
print(json.dumps(dict(evidence=E.relative_to(R).as_posix(),baseline_requirements=len(requirements),M1_hashes=len(m1['hashes']),R1_hashes=len(archive['hashes']),Final_mice=[r['subject'] for r in final],new_neural_access=False)))
