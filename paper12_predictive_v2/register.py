"""Prospective registration: metadata/evidence only, zero neural analysis."""
import subprocess
import study as r
requirements=[
 'Exact authorized base and remote branch preflight', 'Separate new exploratory track and title',
 'Preserve all previous failures and diagnoses', 'Preserve 26-mouse allocation and 13/13 split',
 'Preserve trial/unit QC and data custody', 'No final C fitting or D release',
 'Disclose examined development A/B and scores', 'Register hypotheses before evaluation',
 'Register clean nested models and nuisance contrasts', 'Register actual nominal unit-bin gains',
 'Register numerical policy and stopping conditions', 'Register fixed sensitivity selection',
 'Register nulls and multiplicity before evaluation', 'Audit/reuse all 1638 M3 fits',
 'Audit/reuse all 78 offset fits', 'No unnecessary successful refits',
 'Stationary/history/population/event/drift/combined comparison', 'Other-unit history excludes target',
 'A-only scaler, ridge, bounds and nested embeddings', 'Finite/PG/independent numerical gates',
 'Synthetic regression/oracle tests', 'Native zero-capability role fresh proof',
 'Exact data/runtime/code execution bindings', 'Retain all failed new attempts',
 'Equal-mouse aggregation and paired differences', 'Whole-mouse bootstrap intervals',
 'Paired mouse tests with multiplicity correction', 'Matched unit count sensitivity',
 'Training-rate matching sensitivity', 'Stimulus/time/order controls',
 'Anatomy boundary proxy sensitivity with minimum coverage', 'Probe dependence assessment',
 'Report negative/mixed/inconclusive outcomes', 'Count-preserving temporal falsification',
 'Stimulus/bin/order disruptions with fixed trials', 'Full manuscript methods and baseline results',
 'Mouse-level results and uncertainty', 'Null results and scientific limitations',
 'Disclose original M4 failures in manuscript', 'Scientific figures and supplements',
 'A1 protocol/A2 manifest/A3 pipeline', 'A4 baselines/A5 holdout/A6 statistics',
 'A7 nulls/A8 QC/A9 limitations/A10 reproduction', 'Verified one-command PowerShell reproduction',
 'Freeze hypotheses/configurations/code/acceptance', 'Final calibration-only prospective validation plan',
 'Review final relevant evidence and claim audit', 'Exact-file commit and normal origin/test push',
 'Remote SHA/readback/hash/clean gate', 'STOP at critical gate or final authorization boundary']
def main():
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=r.ROOT,text=True).strip()!=r.BASE:raise RuntimeError('EXACT_BASE')
    if subprocess.check_output(['git','rev-parse','origin/test'],cwd=r.ROOT,text=True).strip()!=r.BASE:raise RuntimeError('REMOTE_BASE')
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',r.BASE],cwd=r.ROOT,text=True).splitlines()
    preserved={n:r.sha(r.ROOT/n) for n in names}
    r.save(r.HERE/'preservation_manifest.json',{'base':r.BASE,'tracked_working_bytes_sha256':preserved})
    r.save(r.HERE/'mission.json',{'mission':r.MISSION,'base':r.BASE,'requirements':[{ 'id':f'REQ-{i:03d}','requirement':v,'status':'OPEN'} for i,v in enumerate(requirements,1)],'stages':6,'final_access_authorized':False})
    r.save(r.HERE/'protocol_registration.json',{'mission':r.MISSION,'base':r.BASE,'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_new_scientific_evaluation':True,'new_fits':0,'protocol_sha256':r.sha(r.HERE/'PROTOCOL.md'),'mission_sha256':r.sha(r.HERE/'mission.json'),'preservation_manifest_sha256':r.sha(r.HERE/'preservation_manifest.json'),'branch_relation':'origin/main absent; origin/test exact BASE','scientific_scope':'Development A/B exploratory; final C/D locked','baseline_requirement_count':len(requirements)})
    evidence=r.ROOT/'ops/evidence/2026-10-14/p12-predictive-structure-v2';evidence.mkdir(parents=True,exist_ok=False)
    text='# Golden standards — P12-PREDICTIVE-STRUCTURE-V2\n\nENGINEER_MODE after user-approved scientific redesign. Exact BASE '+r.BASE+'. New exploratory predictive Method Paper; no causal/mechanistic validation. Product intent is fully specified by the scientific contract; open material decisions=0.\n\nProtocol frozen before new evaluations: paper12_predictive_v2/PROTOCOL.md and protocol_registration.json. Source files foundation/engineer/review/templates are absent in this repository; direct user contract applies. Native scientific role and synthetic L0 plus saved integrity/reproduction are required. Previous M4 A-only authority does not constrain the newly authorized A/B exploratory track. All historical working bytes are bound in preservation_manifest.json.\n\nNumerical gates: PG<=0.001, gradient<=1e-5; no relaxed gates, no result-selected methods. Critical scientific STOP takes precedence over generic completion claims. A stopped mission cannot claim the full paper is complete.\n\n| ID | Frozen requirement | Verification | Status |\n|---|---|---|---|\n'
    text+=''.join(f'| REQ-{i:03d} | {v} | Protocol/source/native/saved evidence as applicable | OPEN |\n' for i,v in enumerate(requirements,1))
    (evidence/'goldenstandards.md').write_text(text,encoding='utf-8')
    print('PROSPECTIVE_PROTOCOL_REGISTERED',len(requirements))
if __name__=='__main__':main()
