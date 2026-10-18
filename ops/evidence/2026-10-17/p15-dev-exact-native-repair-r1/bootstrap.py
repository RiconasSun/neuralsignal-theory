"""Mission registration only; freeze before corrected implementation edits."""
import datetime,json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
E=R/'ops/evidence/2026-10-17/p15-dev-exact-native-repair-r1'
assert not E.exists();E.mkdir(parents=True)
owner=Path('C:/Users/85993/.codex/attachments/997b688b-9feb-486a-92fb-7932801efef9/已粘贴的文本.txt').read_bytes()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n',encoding='utf8')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()=='b0b692bd9b7e42f767117a51d0119644327a97f0'
(E/'OWNER_MISSION.txt').write_bytes(owner)
lines=owner.decode('utf8-sig' if False else 'utf-8-sig').splitlines()
requirements=[]
for line in lines:
    line=line.strip()
    if not line or line.startswith('#') or line.startswith(('MISSION:','BASE:','MODE:','origin/test','BEGIN ')):continue
    requirements.append(dict(id=f'REQ-{len(requirements)+1:03}',requirement=line,status='OPEN',verification='Explicit stage evidence, original scope or preserved required stop'))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
dump(E/'baseline.json',dict(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',base='b0b692bd9b7e42f767117a51d0119644327a97f0',frozen_at=now,requirements=requirements))
dump(E/'mission.json',dict(mission=dict(id='P15-DEV-EXACT-NATIVE-REPAIR-R1',objective='Lossless native-input repair and bounded corrective Development A/B/E execution, with original scientific definitions and no Final access'),target=dict(workdir=str(R),files=['paper15_r1',str(E),'ops/daily-operations.md']),instructions=dict(requirements=[r['requirement'] for r in requirements],constraints=['Historical paper15_dev and M1 immutable','No C/D neural access','No retries or scientific changes']),acceptance=dict(validation=['Bitwise/strict-past/source-level independent input validation','Original numerical gates before new fits','Fresh ledger caps MAIN732/SENS660; actual10 =>610/550','One E batch after B/sensitivity freezes','Saved-only reproduction/internal review/origin-test readback/clean']),openrouter=dict(enabled=False)))
(E/'goldenstandards.md').write_text(f'''# Exact-native corrective requirement baseline
Mission P15-DEV-EXACT-NATIVE-REPAIR-R1. ENGINEER_MODE; original scientific contract and owner corrective budget are explicit, no new product/scientific design. ExactBASE b0b692bd9b7e42f767117a51d0119644327a97f0. Frozen {now}; {len(requirements)} original line-level obligations in baseline.json, no omitted normative paragraphs. Literal format examples are examples, not simultaneous implementation requirements.

Sequence: preserve359 historical attempts and23 M1 files -> versioned exact-native serializer and strict-past regressions -> independently reviewed Development-only cached-source reconstruction -> all12 candidate masks/A source projection/QC/ranks/scalers/ordinals -> independent native integration/numerical review -> fresh61/main per admitted mouse -> saved numerical review -> B-only global selection -> original11 sensitivities/five baselines -> fixed one E batch/four999 references -> exploratory report, reproduction, review, normal origin/test closure.

Oracle L0-L2: bit patterns/exact integer membership/source masks/independently constructed37features; original mathematics/AD/FD/PG and fixed budget. No timestamp tolerance, smoothing, clock correction or fallback. No coefficient reuse. All failures/exclusions remain, no favorable retry. Native caches reused only after identity/hash verification. Final neural arrays/physiology/fits/scores never loaded. Only new paper15_r1 and this evidence plus current daily prefix may change; paper15_dev and M1 remain byte-identical. User explicitly forbids repeated full historical32k audits; verify original exact stage manifest/critical receipt hashes and Git preservation instead.

Terminal PASS requires all applicable original requirements verified,bug0warn0 and fresh review. Source/numerical required failure halts downstream; unavailable secondary policies follow original M1, never altered. Atomic rows remain individually traceable through final preservation matrix. Hist359 + newmain + newsensitivity totals reported separately. No automatic Prompt4/Final or next mission.

Skill workflow: nsi-paper-builder A1-A10 discipline; codex-code-wrapper structured Mission Spec. The prior recorded external CLI auto-review restriction persists; do not retry a refused external orchestration path. Local tools perform scoped edits and independent review without additional network-agent delegation. Optional ops/foundation/engineer/review/template paths absent at prior bootstrap; recheck only those exact paths. No unrelated framework rebuild.
''',encoding='utf8')
old=R/'paper15_dev';seal=json.loads((R/'ops/evidence/2026-10-17/p15-m2-m5-native-qc-development/INTERRUPTION_SEAL.json').read_text())
assert (seal['attempted'],seal['completed'],seal['interrupted'],seal['unattempted'])==(359,358,1,251)
for r in seal['attempt_rows']:assert sha(old/'fits'/r['subject']/(r['configuration']+'.json'))==r['sha256']
m1=json.loads((R/'paper15_m1/PROTOCOL_FREEZE.json').read_text())
for rel,h in m1['hashes'].items():assert sha(R/'paper15_m1'/rel)==h
critical=['INTERRUPTION_SEAL.json','TIME_SERIALIZATION_AUDIT_1.json','TIME_INDEX_AUDIT_1.json','TIME_PRECISION_REVIEW_1.md','TIME_PRECISION_REVIEW_2.md','INDEPENDENT_INTERRUPTION_REVIEW_1.md','INDEPENDENT_STOP_ARCHIVE_REVIEW_2.md']
prev=R/'ops/evidence/2026-10-17/p15-m2-m5-native-qc-development'
dump(E/'PRESERVATION_REGISTRATION.json',dict(time=now,historical_started=359,historical_complete=358,historical_interrupted=1,historical_unattempted=251,historical_baseline=130,historical_dynamic=228,historical_admission_mice=10,historical_admission_labs=8,original_fits_verified=359,M1_files_verified=len(m1['hashes']),historical_evidence={x:sha(prev/x) for x in critical},historical_package_freeze_sha256=sha(old/'STOP_ARCHIVE_FREEZE.json'),new_budget=dict(main_per_mouse=61,main_absolute=732,sensitivity_per_case=5,cases=11,sensitivity_absolute=660,references=4,replicates=999,retries=0),initial_branch='test',remote_test='b0b692bd9b7e42f767117a51d0119644327a97f0',branch_relation='TEST_ONLY_REMOTE_NO_MAIN',initial_clean_before_registration=True,missing_optional_ops=[x for x in ['ops/foundation.skill.md','ops/engineer.skill.md','ops/review.skill.md','ops/templates/goldenstandards.template.md'] if not (R/x).exists()]))
daily=(R/'ops/daily-operations.md').read_bytes()
dump(E/'DAILY_PRESERVATION.json',dict(original_sha256=hashlib.sha256(daily).hexdigest(),original_bytes=len(daily)))
prefix=b'# Current mission: P15-DEV-EXACT-NATIVE-REPAIR-R1\n\nRegistered corrective Development execution. Historical359attempts remain immutable; separate new caps MAIN732/SENS660, actual cohort dependent. Exact-native/source/A-QC/production review before fitting. No Final C/D neural access. Evidence:ops/evidence/2026-10-17/p15-dev-exact-native-repair-r1. No scientific PASS yet.\n\n---\n'
(R/'ops/daily-operations.md').write_bytes(prefix+daily)
print('Registered',len(requirements),'obligations;359historical fits and M1 verified')
