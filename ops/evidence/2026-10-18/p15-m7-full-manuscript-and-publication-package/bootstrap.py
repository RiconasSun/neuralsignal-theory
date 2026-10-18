"""Prospective results-locked manuscript baseline; no scientific workers."""
from pathlib import Path
import datetime,hashlib,json,subprocess

R=Path.cwd();E=Path(__file__).resolve().parent;P=R/'paper15_manuscript'
BASE='bdec0e19621cc8018abe11c5633ce76aff611443'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf8')

assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','rev-parse','origin/test']).decode().strip()==BASE
owner=Path('C:/Users/85993/.codex/attachments/181c120c-90bd-4262-b45a-723e0a27f59d/已粘贴的文本.txt')
E.mkdir(parents=True,exist_ok=True);P.mkdir(exist_ok=True)
(E/'OWNER_REQUEST.txt').write_bytes(owner.read_bytes())
rows=[]
for n,line in enumerate(owner.read_text(encoding='utf-8-sig').splitlines(),1):
    text=line.strip()
    if not text or text.startswith('#'):continue
    rows.append(dict(id=f'REQ-{len(rows)+1:03}',owner_line=n,requirement=text,status='OPEN'))
for text in ['Exact mission-only staging and normal origin/test push','Remote current SHA and every changed-file blob readback','Clean working tree before and after terminal receipt','Independent internal scientific/document review and all P0/P1 resolved','Final PDF pages visually inspected and no clipping/missing glyphs','STOP after manuscript handoff; no submission or next mission']:
    rows.append(dict(id=f'REQ-{len(rows)+1:03}',owner_line=None,requirement=text,status='OPEN'))
dump(E/'baseline.json',dict(mission='P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE',base=BASE,baseline_frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline_revision=1,source_sha256=sha(owner),baseline_requirement_count=len(rows),requirements=rows))
names=[p.decode() for p in subprocess.check_output(['git','ls-files','-z','--','paper15_m0','paper15_m1','paper15_dev','paper15_r1','paper15_final1']).split(b'\0') if p]
assert not any(Path(n).suffix.lower() in {'.npy','.npz','.nwb','.h5'} for n in names)
hashes={n:sha(R/n) for n in names}
archive=json.loads((R/'paper15_final1/ARCHIVE_FREEZE.json').read_text())
for n,h in archive['hashes'].items():assert sha(R/'paper15_final1'/n)==h,n
for n,h in archive['external_hashes'].items():assert sha(R/n)==h,n
for n,h in archive['external_hashes'].items():hashes.setdefault(n,h)
dump(P/'SOURCE_HASHES.json',dict(base=BASE,hashes=hashes,scope='Tracked saved scientific/protocol/source/review artifacts only; no neural arrays or work directories. No scientific executable imported.'))
dump(E/'BRANCH_PREFLIGHT.json',dict(base=BASE,HEAD=BASE,origin_test=BASE,origin_main=None,classification='TEST_ONLY_REMOTE_NO_MAIN',fetch_verified=True,initial_working_tree_clean=True))
dump(E/'MISSION_SPEC.json',dict(mission=dict(id='P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE',objective='Complete results-locked English Method Paper, supplement, seven saved-result figures, PDF and scientific audit/reproduction/normal Git handoff'),target=dict(workdir=str(R),files=['paper15_manuscript/**','ops/evidence/2026-10-18/p15-m7-full-manuscript-and-publication-package/**','ops/daily-operations.md new prefix only']),instructions=dict(constraints=['No neural source arrays','No imports or execution of scientific workers','No fitting/selection/AD/FD/new hypothesis tests/Final D reassessment','All old scientific bytes unchanged','No fabricated author/institution/funding/bibliography','No submission or main promotion']),acceptance=dict(validation=['Saved hashes and exact tables','Results-locked figure/Markdown/PDF rebuild','PDF text/visual page checks','Claim-by-claim review A-J and A1-A10','Independent internal consistency review','Exact Git readback and clean gate'])))
(E/'goldenstandards.md').write_text(f'''# Prospective manuscript contract

Mission P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE; BASE {BASE}; {len(rows)} atomic owner-line/operational requirements in baseline.json, frozen before manuscript code edits. One results-locked Method Paper. Product intent is explicit; ENGINEER_MODE for document production, then REVIEW_MODE and CLOSURE_MODE.

Actor: scientific authors. Outcome: complete truthful English manuscript and supplement, seven publication-quality saved-result figures and underlying tables, editable sources, verified references, PDFs, A1-A10 and A-J reviews, saved-only one-command reproduction and verified origin/test handoff. Final scientific interpretation remains DESCRIPTIVE ONLY throughout. Development10/8labs, Final originally8/admitted6/4labs. Preserve every source/QC/numerical/precision/control failure and historical correction.

Preservation: all five original scientific packages and archived source/review dependencies are hashed in SOURCE_HASHES.json. No neural arrays/work caches are inputs; do not import or execute prediction, fitting, selection, likelihood or AD/FD modules. No new statistics/hypotheses; only compare/reproduce existing saved arithmetic. No scientific thresholds or model changes. No fabricated identities/ORCIDs/funding, causal or confirmation labels. No external submission, main merge or Prompt beyond this mission.

Scope: new paper15_manuscript, this mission evidence and a current daily prefix preserving exact BASE bytes. No old file edits. Minimum patch means complete original contract, not a reduced draft. Full main/supplement and all requested metadata must exist. Scientific failures are findings, not publication success.

L0-L2 document oracle: exact input/hash equality; all six contrasts in registered order; every mouse/lab/sensitivity/reference/fit/selection row retained; figures use saved values and explicitly named units/intervals; all PDFs render without missing glyphs/clipping and private machine paths; citations verified from primary public sources; output/table/bibliography/PDF consistency. Fresh independent scientific/document review after final relevant changes. No UI/channel scope.

PASS requires full baseline verified, bug_count=0,warn_count=0,no shrink/deletions/substitutes, independent P0/P1=0, saved-only reproduction, actual remote changed-file hashes and clean current tree. Source/main templates absent as recorded; use explicit evidence artifacts rather than inventing templates. Current remote has test only; no invented main SHA. Exact-file staging, no force/main/PR. Tracked closure snapshots may precede actual transport; final live receipt goes to ignored work to avoid commit self-reference. STOP after handoff.
''',encoding='utf8')
(P/'.gitignore').write_text('work/\n__pycache__/\n*.pyc\n',encoding='utf8')
print('Baseline frozen',len(rows),'requirements; preserved',len(hashes),'scientific/source/review hashes')
