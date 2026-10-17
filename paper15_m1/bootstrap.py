"""Register the bounded M1 specification task before implementation/testing."""
import datetime,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent.parent;P=R/'paper15_m1';E=R/'ops/evidence/2026-10-17/p15-m1-scientific-protocol-freeze'
BASE='bac678914065609bb3786ea9437fb2c5a215fb38'
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()==BASE
    assert not subprocess.check_output(['git','diff','--name-only'],cwd=R).strip()
    E.mkdir(parents=True,exist_ok=True);now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (E/'OWNER_MISSION.txt').write_bytes(Path(r'C:\Users\85993\.codex\attachments\db20976a-890c-4047-a3c7-0e9060b7cdee\已粘贴的文本.txt').read_bytes())
    req=[
    'Exact BASE/current origin-test and clean prechange; absent origin/main explicitly recorded',
    'Preserve P1-P14/M0 and historical failures; only new M1 files/prepended daily header',
    'M1 only, no new real neural access/C-D/fitting/scoring/M2-M7 or dataset/source rescue',
    'Primary causal local MOp B4-B1 estimand in nats/actual scored nominal curated unit-bin',
    'Secondary own/other history,D/C vs B4,D vs capacity-controlled S without assumed winner',
    'Native IBL CC BY4 source/global139-459-699 and exact20candidate identities',
    'One fixed probe/session per mouse; MOp exact parent/laminar,no regional/probe pooling or replacement',
    'Exact12dev/8final allocation, all mouse sessions same role, both pilot mice permanentdev',
    'Pin sorting/task/mapping/wheel/sync native policy and saved pilot identities;18remaining unknown equivalence explicit',
    'No repeat pilot download/audit absent exact unresolved issue; reuse M0 proof',
    'Chronological original whole-trial A/B/E and C/D partitions; boundary guards/history resets',
    'C-only QC/scaling/fits;D never affects selection/calibration',
    'Final>=8 inferentialcandidate,6-7registereddescriptivefallback,<6stop; independent Development minimum',
    'Sample floors not power; no outcome replacement/allocation reroll',
    'Freeze bin width/history lag/horizon/stimuluswindow/warmup/reset before neural fitting',
    'Native AP duration/sync/trial/knowninvalid support, masks/zero retention; no impossible certificate',
    'Saturation-neighborhood sensitivity and unresolved other artifact burden',
    'Eight-unit primary population with prespecified unitcount/rate sensitivities',
    'Provider-good upstream whole-session frame distinguished from new A/C-only physiology',
    'Freeze rate/refractory/coverage/unitranking/scaling rules using A/C only',
    'Stop on essential source/identity/timing contradiction, never fabricate equivalence',
    'Exact causal stimulus/task/time/order/previous events/wheel feature availability',
    'No current/futuretargetcounts,wheel,future smoothing or earlyresponse/reward/retrospectiveonsetpredictor',
    'Measured-wheel-only limits and offline eventconditioned vs realtime distinction',
    'Exact B0/B1/B2/B3/B4 equations,parametercounts,nesting and common exposures',
    'Likelihood factorial/normalization and A/C-only transforms; avoid weak nuisance comparator',
    'Exact grids/developmentselection/tiebreak/search budgets;no final selection',
    'Small conditional Poisson HMM D exact causal forward,no smoothing,same B4 structure',
    'Fixed-timescale lowdim history C,past only,fixed projection/budget,same B4 structure',
    'Capacity-controlled static mixture S for temporal interpretation;effectivecapacity caveat',
    'Exact D/C/S complexity/penalties/bounds; no failed recurrent or selfexciting simulation inheritance',
    'Numerical contract likelihood/exposure/nesting/parametercount synthetic oracles',
    'Analytic derivatives + independentAD + fixedFD + outwardPG bounds before Prompt3realfit',
    'HMM forward/enumeration,causality/futureperturbation/reset/gap,finite/state-mixture tests',
    'Exact solverbudgets,seeds,no-retry and invalidfit treatment;bounded no rescue',
    'Equalmouse individualeffects/wholemousebootstrap intervals and paired signflips',
    'Explicit symmetry/independence assumptions, no assumptionfree claim; withholdconfirmation whenindefensible',
    'Secondary multiplicity,LOMO,labdependence/heterogeneity and minimumprecision',
    'Positive/mixed/negative/inconclusive rules; nonsignificance not equivalence/no externalreplication',
    'Finite controls rate/unitcount,own/other attribution,withintrialordering',
    'Controls task/stimulus/wheel/order/drift/anatomy/laminar/saturation/labs/static state',
    'Exact nulloperators,assumptions,replicates,RNG/correction; failed controls neverPASS',
    'No unstable recursively simulated Poisson nulls',
    'One-shot futureD boundary developmentfreeze/Cstates/numerical/source/preDreview/Prompt4authorization',
    'No postDretuning/refit/replacement/modelthresholdchanges/repeatedevaluation',
    'Complete scientificprotocol/cohort/nativecontract/QC/features/model/numerical/hypothesisdeliverables',
    'Statistics/falsification/finalclaimboundarydeliverables',
    'Compact meaningful synthetic regressions without accessing extra real data',
    'Saved-only PowerShell reproduce protocol/counts/tests, not fictitious realfit proof',
    'Independent INTERNAL scientific review and preservation of unsuccessful review/fixes',
    'One of four M1 scientificstatuses, all requested finalfields, readiness distinguished from admission',
    'Freeze/trace baseline,bug0warn0,no silent scope/test/claim shrink',
    'Exact mission staging,normal origin-test commit/push,no main/force/PR',
    'Live remote SHA/all changed blob readback/evidencehashes/clean gate and STOPafterM1'
    ]
    write(E/'baseline.json',dict(mission='P15-M1-SCIENTIFIC-PROTOCOL-FREEZE',base=BASE,frozen_at=now,count=len(req),requirements=[dict(id=f'REQ-{i:03}',requirement=x,status='OPEN') for i,x in enumerate(req,1)]))
    inputs=['paper15_m0/results/ALLOCATION.csv','paper15_m0/FINAL_DELIVERY.json','paper15_m0/PILOT_FILE_FREEZE.json','paper15_m0/results/PILOT_RESULTS.json','paper15_m0/INPUT_PINS.json','paper15_m0/SOURCE_REGISTRY.md']
    write(P/'M0_INPUTS.json',dict(base=BASE,hashes={s:hashlib.sha256((R/s).read_bytes()).hexdigest() for s in inputs}))
    (P/'COHORT.csv').write_bytes((R/inputs[0]).read_bytes())
    (P/'.gitignore').write_text('work/\n__pycache__/\n',encoding='utf8',newline='\n');(P/'work').mkdir(exist_ok=True)
    (P/'__init__.py').write_text('"""Frozen P15 M1 protocol and synthetic-only specification checks."""\n',encoding='utf8',newline='\n')
    (P/'.gitattributes').write_text('* whitespace=cr-at-eol\n',encoding='utf8',newline='\n')
    (E/'.gitattributes').write_text('* whitespace=cr-at-eol\n',encoding='utf8',newline='\n')
    (E/'goldenstandards.md').write_text(f'''# P15 M1 requirement baseline\n\nMission P15-M1-SCIENTIFIC-PROTOCOL-FREEZE; exact BASE {BASE}; registration {now}; {len(req)} atomic requirements. Initial tracked and untracked state was clean before bootstrap.py. Fresh fetch matched HEAD/origin/test. origin/main is absent (TEST_ONLY_REMOTE_NO_MAIN); no invented relation count or repair. Repo foundation/engineer/review/templates unavailable; user directive applies.\n\nApproved scientific contract: freeze a complete predictive protocol from reviewed M0, 20 fixed metadata candidates/12dev8final, one local MOp population, no real-data access or fitting. Primary B4-B1 nuisance-adjusted predictive information; no neural causal/physical primitive claims. Ordinary numerical/source definitions may be resolved autonomously, no result-driven eligibility. Open material user-intent decisions=0. Scientific model/QC choices are prospective design choices, subject to independent internal review, not empirical discoveries.\n\nPlan: baseline -> exact source/cohort/partitions/QC -> feature/model/stats/control specification -> small synthetic implementation tests through JSON Mission Spec wrapper -> independent mathematical/scientific review and any bounded corrections -> freeze final source hashes/protocol -> saved-only reproduction -> exact origin/test archive/remote/clean -> STOP. Use Method Paper evidence chain with no fabricated results; A4 outcomes not run, A5 D access=0.\n\nRequired L0-L2 checks: likelihood/nesting/parameter math, fixed finite differences/independent AD, causal-forward enumeration/perturbation/reset, partition and statistics/control canaries. These certify synthetic specification only; full production implementation gate before Prompt3 remains separate. No UI/channel tests applicable. Baseline immutable; individual requirement mapping mandatory. No giant framework, source discovery, pilot reacquisition, final access, security custody or M2-M7. bug_count=warn_count=unresolved_shrink_risk=0 for archive PASS.\n''',encoding='utf8',newline='\n')
    write(E/'BOOTSTRAP_RECEIPT.json',dict(base=BASE,frozen_at=now,requirements=len(req),initial_clean=True,remote_base_verified=True,origin_main='ABSENT',real_data_access=0,model_fits=0))
    print(json.dumps(dict(requirements=len(req),frozen_at=now)))
if __name__=='__main__':main()
