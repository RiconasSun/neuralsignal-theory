"""Exclusive prospective metadata-screening registration, before new KI counts."""
from pathlib import Path
import datetime
import hashlib
import json

P=Path(__file__).resolve().parent
ROOT=P.parent
E=ROOT/'ops/evidence/2026-10-15/p13-ki-pfc-metadata-feasibility-1'


def main():
    E.mkdir(parents=True,exist_ok=True)
    user=Path(r'C:\Users\85993\.codex\attachments\1190e432-7cfd-4c51-b2c2-5d653613be4c\已粘贴的文本.txt')
    with (E/'USER_MISSION.txt').open('xb') as f: f.write(user.read_bytes())
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    policy={
        'mission':'P13-KI-PFC-METADATA-FEASIBILITY-1','registered_utc':now,
        'base':'54f4bb572c33b11937b1939b4e643fda5269f58c',
        'datasets':[{'id':'001260','version':'0.250911.0744','priority':'primary'},
                    {'id':'000473','version':'0.230417.1502','priority':'secondary_separate'}],
        'screening_tiers':[5,8,10,20],
        'tier_meaning':{'5':'Minimal local population; at most2 HMM states and1 continuous component proposed',
                        '8':'Proposed modest primary design:2 states,1-2 continuous components',
                        '10':'More channels, but require more data and training regularization',
                        '20':'Higher coverage sensitivity only; not an inherited admission threshold'},
        'tiers_are_admission':False,
        'regions':['PL','ILA','ACAd','ACAv','MOs','ORBm','ORBvl','ORBl','AId','AIv','FRP'],
        'anatomy':'Exact provider acronym/laminar descendant, retain original labels and provenance; no inferred certainty or pooling',
        'primary_region_recommendation_priority':['PL','ILA','ACAd','ACAv','ORBm','ORBvl','ORBl','AId','AIv','FRP','MOs'],
        'primary_epoch':'Documented pre-tone[-3,0) seconds with common event/spike clock and observation support, nonoverlapping within recording',
        'candidate_design_minimum_units':8,
        'candidate_design_minimum_epochs':120,
        'minimum_mice_per_group':8,'target_mice_per_group':12,
        'threshold_justification':'8 units and120 three-second epochs are proposed, not admitted: 2-state HMM/1-2-dimensional history readout, bounded fitting and chronological60/30/30 fitting/selection/scoring epochs.120 epochs is360 seconds, not a universal power guarantee. Refuse to call feasible without documented support/exclusions. No IBL400-trial rule.',
        'partition_recommendation':'Mouse-disjoint development/final; all sessions from one animal stay together; identity-hash allocation before neural access. One prechosen simultaneous probe/session per mouse; chronological first50% fit/calibration, next25% dev selection or reserved transfer checking, last25% evaluation, with epoch reset and guard gaps. Exact roster/allocations require separately authorized P13-v2.',
        'unknown_policy':'Missing essential quality/anatomy/epoch/clock/support/exclusion evidence -> INCONCLUSIVE_METADATA, never assume pass; proven independent-animal upper bound<16 -> DATA_INSUFFICIENT.',
        'decision_values':['FEASIBLE_SINGLE_PFC_REGION','FEASIBLE_ONLY_UNDER_SEPARATE_POOLED_M PFC_DESIGN','DATA_INSUFFICIENT','INCONCLUSIVE_METADATA'],
        'pooled_design':'May describe medial PL+ILA+ACAd+ACAv separately if needed; never combine datasets, task settings or regions for a single-region verdict',
        'allowed_values':['subject/session/probe/unit identifiers','provider quality labels','atlas/location labels','electrode group mappings','stimulus event timestamps','trial/epoch start-stop and labels','observation/artifact/saturation/sleep/movement-exclusion intervals','documented clock/recording/preprocessing metadata'],
        'forbidden':['spike_times values','spike counts','waveforms','neural/LFP/EMG/behavior raw signal samples','neural outcome metrics','fits','final evaluation','P1-P12/P13-original mutation'],
        'bounds':{'datasets':2,'nwb_assets':200,'api_pages':20,'source_files':30,
                  'http_requests':6000,'transport_bytes':671088640,'header_bytes_per_asset':12582912,
                  'range_bytes':1048576,'attempts_per_request':2},
        'stop':'End after two-candidate metadata verdict, saved reproduction, independent internal review and verified origin/test archive. No M1-M7 or alternative dataset search.'}
    rows={
        'F0':['pin primary release','pin secondary release','pin source revision','record licenses','record complete asset manifests','document anatomy sources','document event sources','reconcile animals','reconcile sessions','reconcile probes','identify repeated recordings','identify cross-release overlap','separate passive auditory and aversive tasks'],
        'F1':['retain causal incremental prediction question','focus on documented primary pre-tone epochs','no passive-choice-mechanism claim','no P14 task study'],
        'F2':['all relevant region labels retained','PL coverage','ILA coverage','ACAd coverage','ACAv coverage','all animal denominator','sessions per animal','simultaneous units per probe/subregion','provider quality labels','anatomical localization provenance','region-specific animal counts','5-unit tier','8-unit tier','10-unit tier','20-unit tier','tier complexity implications','tiers do not auto-admit','no inherited20-unit admission','single-region priority','pooled medial-PFC proposal separate only'],
        'F3':['genuine pre-tone identity','epochs per session','epochs per mouse','common spike/event clock documentation','missingness intervals','saturation intervals','sleep-like exclusions','movement/licking exclusions','epoch overlap','within-mouse dependence','recording quality','preprocessing','causally available context','no inherited400-trial rule','train/validation structure','calibration/evaluation structure','justified proposed primary minimum','frozen proposed partition','8development+8final independent mouse minimum','prefer larger cohort','no session/unit pseudoreplication'],
        'F4':['baseline feasibility','exact-forward low-state HMM feasibility','fixed-timescale low-dimensional continuous feasibility','temporal null feasibility','nuisance null feasibility','one final-mouse evaluation feasibility','complexity proportional to data','no model fitting','no deep recurrent rescue','no latent-integration requirement','no cryptographic custody architecture','CCPN reuse requires math compatibility','CCPN reuse requires data-contract compatibility'],
        'F5':['one evidence-supported verdict per candidate','primary candidate decision','secondary candidate separate decision','prospective design for any feasible candidate','anatomical scope','mouse denominator','admission recommendation','causal predictors','strong baseline recommendation','numerical gates','falsification gates','final safeguards','interpretation limits','original IBL failure unchanged'],
        'EXEC':['bounded metadata/header access only','avoid bulk neural downloads','software/QC tests','saved-only reproduction','independent internal review','exact-file commit','normal origin/test push','remote manifest/hash readback','clean gate','no M1-M7','no spike access','name exact missing evidence','no indefinite dataset search','P1-P12 unchanged','preserve prior P13 unchanged']}
    requirements=[]
    for stage,items in rows.items():
        for item in items:requirements.append({'id':f'REQ-{len(requirements)+1:03}','stage':stage,'requirement':item,'status':'OPEN','evidence':None})
    outputs={P/'REGISTRATION.json':policy,E/'baseline.json':{'frozen_utc':now,'revision':1,'count':len(requirements),'requirements':requirements},
             E/'mission.json':{'mission':{'id':policy['mission'],'objective':'Two separately evaluated pinned KI/PFC metadata feasibility candidates only'},'target':{'workdir':str(ROOT),'files':['paper13_ki_feasibility1/**',str(E.relative_to(ROOT))+'/**','ops/daily-operations.md']},'metadata':{'base':policy['base'],'user_mission_sha256':hashlib.sha256(user.read_bytes()).hexdigest()}}}
    for path,obj in outputs.items():
        with path.open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(obj,indent=2)+'\n')
    with (E/'goldenstandards.md').open('x',encoding='utf8',newline='\n') as f:
        f.write(f'''# P13 KI/PFC metadata feasibility

Frozen at {now}; {len(requirements)} atomic requirements in baseline.json, unchanged complete USER_MISSION.txt. BASE54f4bb572c33b11937b1939b4e643fda5269f58c; initially clean test/origin/test, fetch verified, origin/main absent (TEST_ONLY_REMOTE_NO_MAIN). No merge/reset needed.

Decision block: trusted research analyst needs a viable metadata-supported PFC population after prior IBL stop. Approved outcome: bounded two-release feasibility with exact denominators, transparent missing evidence, tractable proposed design and independent internal review. No neural outcomes, pooled task substitution, manuscript or model fitting. Open decisions=0 for this metadata mission. Scientific admission and P13-v2 execution remain separately gated.

Verification L0-L2: strict-path synthetic HDF5 canaries; range/budget/source/identity tests; denominator and epoch oracles; saved-only replay and independent review for final source state. No channel/UI requirement. Final terminal status is distinct from scientific feasibility verdict. Do not equate engineering archive success with eligibility or scientific validation.

Preserve all previous-paper bytes and original P13 FAIL. No omitted requirements, threshold retrofitting or outcome-based choice. Freeze analysis/header source hashes before real header values. Unknown essential metadata remains unknown. Full asset license/version provenance and exact read paths/bytes/headers retained. Final zero bugs/zero unresolved evidence warnings needed for PASS; evidence-supported metadata limitation may require human follow-up without false PASS.

Tool route: JSON Mission Spec and current-session local tools. Prior external-model CLI rejection is not retried or bypassed. Required independent internal reviewer may use an authorized local subagent after implementation freezes; no review while code changes.
''')
    print(json.dumps({'registered_utc':now,'requirements':len(requirements),'policy_sha256':hashlib.sha256((P/'REGISTRATION.json').read_bytes()).hexdigest()}))


if __name__=='__main__':main()
