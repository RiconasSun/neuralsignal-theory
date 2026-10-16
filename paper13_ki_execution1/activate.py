"""Owner-authorized M1activation from saved metadata, before neural access."""
import csv
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

P=Path(__file__).resolve().parent
ROOT=P.parent
OLD=ROOT/'paper13_ki_pl_contract1'
E=ROOT/'ops/evidence/2026-10-16/p13-ki-pl-science-first-execution'
BASE='60aaf834becb176d38a3b8a598c90d88054bb1cc'
MISSION='P13-KI-PL-SCIENCE-FIRST-EXECUTION'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(path,obj):
    with path.open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(obj,indent=2,allow_nan=False)+'\n')

def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==BASE
    snap=json.loads((OLD/'FREEZE_r2.json').read_text())
    for name,h in snap['hashes'].items():
        if sha((ROOT/name).read_bytes())!=h:raise ValueError('Frozen source mismatch: '+name)
    protocol=json.loads((OLD/'PROPOSED_PROTOCOL_FREEZE_r2.json').read_text())
    for name,h in protocol['hashes'].items():
        if sha((OLD/name).read_bytes())!=h:raise ValueError('Frozen protocol mismatch: '+name)
    expected='3129ee6017232db49a68136cc0cf04942d4abbf31081ef54782a23ddd3f01660'
    if sha((OLD/'PROPOSED_P13_V2.md').read_bytes())!=expected:raise ValueError('Wrong reviewed protocol')
    E.mkdir(parents=True,exist_ok=True)
    user=Path(r'C:\Users\85993\.codex\attachments\46b4a23f-c60f-45f0-9e2a-d0a8e2f24c89\已粘贴的文本.txt').read_bytes()
    with (E/'USER_MISSION.txt').open('xb') as f:f.write(user)
    allocation=json.loads((OLD/'PROPOSED_ALLOCATION.json').read_text())
    roles={x:'development' for x in allocation['development']}|{x:'final' for x in allocation['final']}
    headers={}
    for f in (ROOT/'paper13_ki_feasibility1/metadata/headers').glob('000473_*.json'):
        h=json.loads(f.read_text());headers[h['decoded_values']['/general/session_id']]=(f,h)
    with (OLD/'results/initial/epoch_disposition.csv').open(newline='') as f:epochs=list(csv.DictReader(f))
    records=json.loads((OLD/'results/initial/audit.json').read_text())['records'];output=[]
    for r in records:
        if r['mouse_id'] not in roles:continue
        hf,h=headers[r['recording_id']];v=h['decoded_values'];role=roles[r['mouse_id']]
        eps=sorted([[float(x['start']),float(x['stop'])] for x in epochs if x['recording_id']==r['recording_id'] and x['refined_A']=='True'])[:120]
        if len(eps)!=120:raise ValueError('Incomplete epoch allocation')
        units=[];locs=v['/general/extracellular_ephys/electrodes/location']
        for i,(uid,e) in enumerate(zip(v['/units/id'],v['/units/electrodes'])):
            if locs[e] in {'PL','PL1','PL2','PL3','PL2/3','PL4','PL5','PL6','PL6a','PL6b'}:units.append({'unit_id':uid,'row':i,'electrode_row':e,'label':locs[e]})
        units.sort(key=lambda x:x['unit_id'])
        if len(units)!=r['PL_raw_units'] or len(units)<8:raise ValueError('PLmapping mismatch')
        parts=['A']*60+['B']*30+['E']*30 if role=='development' else ['C']*60+['D']*60
        output.append({'mouse_id':r['mouse_id'],'role':role,'recording_id':r['recording_id'],'asset':h['asset'],'etag':h['etag'],
                       'header_file':str(hf.relative_to(ROOT)).replace('\\','/'),'header_sha256':sha(hf.read_bytes()),'PL_units_numeric_order':units,
                       'epochs':[{'ordinal':i+1,'start':a,'stop':b,'partition':part} for i,((a,b),part) in enumerate(zip(eps,parts))],
                       'QC_partition':'A' if role=='development' else 'C','original_support':[r['support_start_seconds'],r['support_stop_seconds']]})
    output.sort(key=lambda x:(x['role'],x['mouse_id']))
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    registration={'mission':MISSION,'utc':now,'base':BASE,'protocol_sha256':expected,'protocol_snapshot_sha256':sha((OLD/'PROPOSED_PROTOCOL_FREEZE_r2.json').read_bytes()),
                  'authorization_sha256':sha(user),'allocation':allocation,'status':'ACTIVATED_BY_OWNER','candidate_mice':19,'full_denominator':25,
                  'fixed_science':'All reviewed equations/QC/grids/bounds/thresholds/partitions/guards/nulls/stopping unchanged; no scientific redesign permitted.',
                  'execution_order':['M1hashes/identities/epochs','synthetic source-window/QC and numerical implementation gates','M2A/C-onlyQC','M3developmentbaselines','M4developmentD/C/S','M5Bselection/Ereport','M6Ccalibration/review/oneDassessment','M7paperifvalid'],
                  'source_policy':'Trusted local source extraction, deterministic window export, no B/E/DQC or neural outcome summaries before their gate; no independent-principal/admin protection claimed.',
                  'pre_final_allowed_exports':['developmentA','finalC'],'pre_final_denied_exports':['finalD'],'development_B_E':'Only after required train-QC/numerical fits; never QC/scaling/initialization.',
                  'budgets':{'unique_NWB_assets':19,'transport_bytes_max':21474836480,'requests_max':40000,'range_bytes':1048576,'attempts_per_request':2,'model_development_fit_cap_per_mouse':93,'model_final_fit_cap_per_mouse':22,'neural_reruns_for_policy_tuning':0},
                  'stopping':'Any scientific data insufficiency, leakage or required real numerical failure stops forward progression. Ordinary demonstrable software defects require preserved evidence, independent synthetic regression and reviewed source re-freeze; no optimizer rescue.'}
    write(P/'ACTIVATION.json',registration);write(P/'EPOCH_UNIT_ALLOCATION.json',{'utc':now,'records':output,'full25_disposition_reference':'paper13_ki_pl_contract1/results/initial/animal_disposition.csv'})
    groups={
      'M1':['exactBASE','owner-authorized protocolhash','85associatedsourcehashes','original25denominator','19fixedcandidateidentities','10dev9finalallocation','first120valid3sepochs','A60B30E30/C60D60','unitordering/QCpolicies','nohistoricalmutation','noautomaticDaccess'],
      'M2':['sourceidentity/custodylogs','syntheticpartitioncanaries','A/C-onlyphysiologicalQC','50spikes30ISI12occupied','0.1to100Hz','within-epochfraction<=.01','finitestrictlyorderedtimes','first8passingnumericPLids','atleast8dev8final','warmup5/25scored100msbins','trainingonlyscalers','noDQCunitrankingscaling','retainallQCfailures'],
      'M3':['B0stationary','B1nuisance','B2ownhistory','B3allotherhistory','B4mandatorycombined','ridge.1/1/10seeds11/23/37','identicalboundednormalizedobjective','independentnumericaloracles/AD/FD','PG<=.001gradient<=1e-5','all39attemptsperdevmouse','B*B-onlyselection','failedfitstop'],
      'M4':['2statefixedtransitiongrid','exactcausaljointforward','16Dparameters','2Dleakyhistoryfixedtau/QR','16Cparameters','samefrozenB4offset','staticSfromp=.5','enumeration/independentAD/futureperturbation','all27D+27Cconfigs','noextraoptimizerbudget','allattemptstrajectories','numericalfailurestop'],
      'M5':['threeprimaries','threeguards','B-onlyoneSEselection','Ereportonly','equalmouseunit-bins','mouseintervals/signflips/Holm','sign-nullassumptions','complexityaccounting','negative/mixedreporting'],
      'M6':['999temporalcontrols','999historycontrols','999taskordercontrols','999conditionalB*nulls','allmandatoryunit/rate/QC/anatomy/alignment/eventpanels','coveragefailedpanelsretained','C-onlyfromscratchcalibration','finalsource/model/statisticfreeze','atleast8finalmice','independentrelease/numericalreview','exactlyoneDassessment','allprimary/guardstats','noDretune/rerun','conditionalclaimcriteria'],
      'M7':['truthfulstopreportifpriorgatefails','manuscriptifvalidfinalnegativeormixed','supplement/tables/figures','fullmouseandfailureevidence','A1-A10claim/numeric/anatomyaudit','savedandfullreproductionseparate','main/suppPDFifvalidfinal','noinventedfindings/replication'],
      'CLOSE':['independentinternalreview','exactfilecommit','normalorigin/testpush','SHA/manifest/hashreadback','cleanworkingtree','allhistoricalP1-P13failurespreserved','stopafterapprovedmission']}
    req=[]
    for phase,items in groups.items():
        for item in items:req.append({'id':f'REQ-{len(req)+1:03}','phase':phase,'requirement':item,'status':'OPEN','evidence':None})
    write(E/'baseline.json',{'utc':now,'revision':1,'count':len(req),'requirements':req})
    write(E/'mission.json',{'mission':{'id':MISSION,'objective':'Execute exact reviewed P13-v2science-first protocol, stop at genuine failed gate, complete paper if valid final assessment completes'},'target':{'workdir':str(ROOT),'files':['paper13_ki_execution1/**',str(E.relative_to(ROOT))+'/**','ops/daily-operations.md']},'metadata':{'base':BASE,'user_mission_sha256':sha(user)}})
    (E/'goldenstandards.md').write_text(f'''# P13-v2scientific activation\n\nFrozen {now}; {len(req)}atomic requirements. ExactBASE{BASE}, initiallyclean test=origin/test, no origin/main(TEST_ONLY_REMOTE_NO_MAIN). Owner's attachedmission activates exactreviewed protocolhash{expected}, overrides old NOTACTIVATED/STOPinstructions only prospectively. All original scientific content and old sources stay unchanged.\n\nProduct/scientific contract: trustedlocal analyst executes fixed19candidatePLaversive-pre-tone study, no dataset/scope/threshold changes. Gates: metadataidentity/splits -> testedA/CwindowQC -> baseline/dynamicnumerics -> developmentselection -> Ccalibration/review -> exactlyoneD -> fullpaperortruthfulstop. No keys/ledger/multiprincipal claims. Open intended scientific decisions=0. Implementation details must preserve semantics; genuine protocol gaps cannot be guessed after outcomes.\n\nRequiredL0-L2plus scientific oracles, realtrainQC, every fit/gradient/PGgate, allregisteredcontrols/onefinalboundary, independentinternalreview and actualGitclosure. Saved/synthetic replay cannot certify realQC/model convergence/finalscience. All attempts and failures append-only. Scientificfailures invoke the owner's STOP, not unlimitedengineeringrescue. Final task PASS may certify a completed truthfulstop/archive but never a failed scientificstudy; scientificgate status separate.\n\nJSONMissionSpec and current-sessionlocaltools; no retry of earlier rejected external-model CLIservice. nsi-paper-builder MethodPaper/A1-A10discipline applies. Required physical opsfoundation/engineer/review/templates absent; currentuserdirective/mission/protocol/dailyapply. Originalsourceidentity and scienceboundary dominate implementation convenience.\n''',encoding='utf8',newline='\n')
    print(json.dumps({'mission':MISSION,'requirements':len(req),'records':len(output),'protocol_verified':True,'utc':now}))

if __name__=='__main__':main()
