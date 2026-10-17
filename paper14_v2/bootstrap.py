"""Prospective source-first exploratory mission registration, no neural outcomes."""
import datetime,hashlib,json,subprocess
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parent.parent;P=R/'paper14_v2';E=R/'ops/evidence/2026-10-16/p14-v2-exploratory-context-dynamics'
BASE='b82425aab216f57b207d242c4361760f03b598d4';MISSION='P14-V2-EXPLORATORY-CONTEXT-DYNAMICS'
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(obj,f,indent=2);f.write('\n')
def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()==BASE
    E.mkdir(parents=True,exist_ok=True)
    owner=Path(r'C:\Users\85993\.codex\attachments\bbb9e3f5-146e-464a-bf04-88bbbfa4fc5c\已粘贴的文本.txt')
    (E/'OWNER_MISSION.txt').write_bytes(owner.read_bytes())
    requirements=[
    'Exact BASE/fresh origin-test preflight and preserve initial clean tree',
    'New prospective exploratory study, preserve all P1-P13/P14historic failures and source evidence',
    'Freeze atomic requirements and source/eligibility registration before fresh canonical counts or neural outcomes',
    'Within-animal temporal holdout only; never independent-animal confirmation or retroactive oldPASS',
    'Scheduled probabilityLeft0.2/0.8 contexts, not measured beliefs; no presumed discretewinner',
    'Use only DANDI000409/0.260309.1324 CC-BY4; exact attribution/version/source identities',
    'One bounded canonical compatibility audit; no new dataset search or indefinite provenance chase',
    'Historical13is metadata upper bound only, not established canonical cohort',
    'Verify canonical mouse/session/probe and actual unit/atlas/QC/task-clock mappings; never assume old equality',
    'Preserve exact mismatches; any new candidate frame selected outcome-blind and prospectively registered',
    'No other session/version silently called equivalent; critical mapping failure -> SOURCE_CONTRACT_INCONCLUSIVE',
    'Exact MOs/ACAd/ACAv/PL/ILA descendants, one simultaneously recorded probe/population per mouse',
    'Never pool probes/sessions/animals to meet size floor; identical selectedunits across contexts',
    'Name MEDIAL FRONTAL CORTEX; no isolatedPFC claim for MOs-dominant data',
    'Report leaf composition,MOspercentage/majority/exclusivelyMOs and nonMOs sensitivity',
    'Register source-compatible ten-unit metadata screen before fresh counts',
    'Register whole original block segmentation,bothcontexts,>=2runs/context and>=15usabletrials/run',
    'Register>=60trials/context/originalhalf and original0.5s stimulus window,justify anychange prospectively',
    'All newly computed physiological QC/unit ranking training-only; providerwhole-releasecuration disclosed',
    'Report original and postQC denominators;>=8preferred,6-7limiteddescriptive,<6STOP_DATA_INSUFFICIENT',
    'No favorable replacement of QCfailedmice after neural outcomes',
    'Early whole blocks for training/development,latewholeblocksreserved; bothcontexts present',
    'Training-internal guarded validation only, no randomly mixed adjacent trials/bins',
    'Freeze late evaluation identities/code before evaluation outcomes; no late-derived QC/scaling/selection',
    'Only permittedtrain/validation fit transformations/hyperparameters/coefficients',
    'One frozen reserved temporal assessment, no model modification or second evaluation after scores',
    'Disclose sessiondrift/blockorder confounding; temporalholdout not animalreplication',
    'B0stationaryPoisson baseline exact likelihood',
    'B1context/stimulus/trialtime/blocktrend/causallyavailable measurednuisance baseline',
    'B2B1plus ownspikehistory; no current/futurespikefeatures',
    'B3B1plus other-unit populationhistory, targetexcluded',
    'B4mandatory strongcombinedcontext/task/own/population baseline',
    'No event/outcome/movement before observedtimestamp; freeze predictor/missingnessrules before scoring',
    'No unaligned wheel/pupil imputation; narrow measuredtaskconditional estimand with permanent movement/arousal-independent claimban',
    'Discrete two-statecausalconditionalPoissonHMM,exactforwardloglikelihood,strongB4offset',
    'No backward smoothing for prediction; currentcounts assimilated onlyafter scoring; fixedtransition policy',
    'Continuous two-dimensional causal leakyhistory, fixedprojection/timescales, pastcounts,Poissonreadout/sameB4',
    'Fit and compare contextinvariant/contextdependent D and C variants',
    'Freeze parametercounts,ridge,initialization,fitbudgets,complexityselection before fitting',
    'Equal nominalparameters not treated equalcapacity; no unregistered outcome-driven redesign',
    'Synthetic scalarPoissonoracle and exact likelihooddenominators',
    'Synthetic HMMforward/enumeration identity',
    'Causal futureperturbation and trial-reset tests',
    'Analytic/independentgradientagreement,finiteobjectives/scores,registeredPGconvergence gates',
    'No unlimitedoptimizerrescue; required numericalfailure preserved, no favorable substitute',
    'Two two-sidedprimaryDelta_D/Delta_C gaininteractions .2minus.8 vsB4, no assumed direction',
    'Matched units/masks/scoring denominators withinmouse, absolute scores and all differences',
    'Essential dependent-minus-invariant checks for bothfamilies, not proofbiologicaltransitionmechanism',
    'Contextinterpretation addresses contextbaseline,complexity,stimulus/behavior anddrift',
    'Mouse independentunit, never neuralbin/trial/unit/probe/session pseudoreplication',
    'Report everyanimal,equalmouseeffects,directionconsistency,LOMO and heterogeneity',
    'Wholemousebootstrapuncertainty,corrected/uncorrectedpvalues,twohypothesismultiplicity',
    'Signflipconditionalfair-sign/symmetryassumptions explicit, exactenumeration not assumptionfree mean-test',
    'Small/unsupportedassumptions -> descriptiveinference; nonsignificance not equivalence',
    'No independentanimalconfirmation,universalPFC,causalatoms or ontologyclaim',
    'Preregister bounded temporalhistorydependence control before lateoutcomes',
    'Preregister context/tasklabel interpretation and blockorder/drift controls',
    'Preregister stimulusimbalance and priorreward/responsehistory controls',
    'Preregister animalheterogeneity and unitcount/firingrate sensitivities',
    'Preregister MOs/nonMOs composition sensitivity',
    'Preregister measuredmovement/arousal and sourceQC/support limitations/sensitivities',
    'Defensible conditionalnullassumptions, no arbitrarycontextshuffle calledrandomization',
    'No unstable recursivelysimulated P13Bstar generator; failed/unavailable controls retained',
    'No new controls after late scores; no selectivemouseexclusion or retuning',
    'Before reserved evaluation freeze model/hyperparameters,trainQC/preprocess,masks/statistics/nulls/sensitivities/reporting',
    'Independent implementation/scientific review before reserved evaluation',
    'One validlateassessment reports allmodels/bothinteractions evenifnegative',
    'If evaluation valid fullmanuscript with fullmethods/results and supplement',
    'Completeanimal/unit/contexttables andbaseline/dynamic/dep-invariantcomparisons',
    'All effect uncertainty/null/sensitivity/failedcontrols/source limitations',
    'Publicationqualityfigures and A1-A10claim-evidence audit',
    'Saved-results and executable reproduction instructions,manuscriptPDF and supplementPDF',
    'Disclose retrospective context of old metadata failures,eligibleidentities,temporalholdout,MOs/source/behavior limits',
    'No validatedCWP/NAP/causalcomputation/humanclaim; draftcompletion distinctfromscientificvalidation',
    'If gatefails deliver completeSTOPreport instead of fabricated findingspaper',
    'Reuse validated repo components where mathematicallycompatible; no rerun oldauditswithout source need',
    'No offlinesigning,cryptoledger,multi-principalcustody or unrelatedlargemodelframework',
    'Routineengineeringfixes withregressions/failurepreservation allowed; substantivescientificchangeSTOPrequiresowner',
    'Deliver SOURCE_COMPATIBILITY/LICENSE_VERIFIED/CANONICAL_COHORT_COUNT/PHYSIOLOGICAL_ELIGIBLE_MICE',
    'Deliver TRAINING_EVALUATION_SPLIT and allbaseline/discrete/continuousscores or honestNOTRUN',
    'Deliver interactions/statistics/nullsensitivities/verdict/manuscript/PDFstatus,never inventedresults',
    'Deliver reproductionstatus,bugwarncounts,fullatomicpreservationmatrix andindependentreview',
    'Exactmission-only commit/push origin-test,no force/main/PR',
    'Live remoteSHA/allchangedblobhashes/cleanworkingtree verified',
    'Stop after reviewed validmanuscript or evidence-backedscientificblocker; no automaticnextmission'
    ]
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    write(E/'baseline.json',dict(mission=MISSION,base=BASE,frozen_at=now,count=len(requirements),requirements=[dict(id=f'REQ-{i:03}',requirement=s,status='OPEN') for i,s in enumerate(requirements,1)]))
    historical=pd.read_csv(R/'paper14_pivot1/results/EXPANDED_METADATA_CANDIDATES.csv',dtype=str)
    fixture=pd.read_csv(R/'paper13/metadata/fixture.csv',dtype=str)
    assets=[]
    for i in [1,2,3]:assets+=json.loads((R/f'paper14_pivot1/sources/assets_page{i}.json').read_text())['results']
    processed={}
    import re
    for a in assets:
        if a['path'].endswith('_desc-processed_behavior+ecephys.nwb'):
            m=re.search(r'_ses-([a-f0-9-]{36})_',a['path']);assert m and m[1] not in processed;processed[m[1]]=a
    records=[]
    for f in historical.itertuples():
        a=processed[f.eid];records.append(dict(mouse=f.mouse,canonical_subject=f.canonical_DANDI_subject,eid=f.eid,pid=f.pid,probe=f.probe,asset=a,phase='Historical13canonicalmetadataaudit',not_canonical_admitted=True))
    write(P/'SOURCE_AUDIT_ROSTER.json',dict(registered_at=now,records=records,scope='Exact historical13sessionUUIDs as targeted source-compatibility sample; never infer globalDANDIupperbound or sourceunit-equality. Do not silently switchsessions.',fallback='If metadata-only ordinaryeligibility failures reduce this frame, a separately registered outcome-blind subset of the fixedofficialrelease may be considered withinthissameaudit before anyneuraloutcomes; no implicitfallbackactivated. Essentialsource-mappingfailure stops ratherthan cherry-picking anothermouse.'))
    write(P/'SOURCE_REGISTRATION.json',dict(mission=MISSION,base=BASE,registered_at=now,stage='SOURCE_METADATA_ONLY_BEFORE_FRESH_CANONICAL_COUNTS_OR_NEURAL_OUTCOMES',source=dict(dandiset='000409',version='0.260309.1324',license='CC-BY-4.0',frozen_directory='paper14_pivot1/sources/assets_page1-3.json; exact2048IDs'),old13='Historicalmetadataupperbound only, not canonicalcohort; exactsubject/session/probe discrepancies preserved.',anatomy=['MOs','ACAd','ACAv','PL','ILA'],laminae=['','1','2/3','4','5','6a','6b'],unit_screen='Canonicalibl_quality_score==1 plus documented canonicalunit->maxelectrode->atlaslabel finitecoordinate/probe mapping. Never import oldunitID/QC/anatomy byassumption. >=10sameprobe; identicalunitset acrosscontexts latertrain-onlyselected.',trial_screen='Retain>=2qualifyingoriginalnonneutralruns/context,>=15usabletrials/run,>=60trials/context/wholeoriginalhalf,0.5sstimwindow. Runs/cut before exclusions; neutral/unknownbreak. Finiteorderedstart/stim/goCue/feedback/stop,windowinside; providerbwm_includeTrue andsaturation_stim_plus06False neededfromcanonicalfields or verified matchingoldannotationjoin.',annotation_compatibility='IfcanonicalNWBdoesnotcarrybwm/saturation flags, transferonly after every originalrow is matched bysessionUUID/originalorder/trialboundaries/context and allavailable fields needed bysourcecuration, withfinite-timestampdifference<=1e-6seconds andidenticalcategoricvalues/missingness. 1microsecond isprospective serialization/timebasecomparison tolerance, not clock-quality/PG/scientificacceptancethreshold. No reordering, imputation or relaxedmask. Unresolvedessentialannotation/timebasejoin ->SOURCE_CONTRACT_INCONCLUSIVE.',selection='No scores;canonicalprobes ranked byqualifiedtargetunitcount,min4context-halfcellcount,lexicaleID/probename;one exactsession perregisteredmouse. CanonicalUUID/probe identities used;oldtriplet comparisontable retained.',physiology='NOT_AUTHORIZED_BY_SOURCE_STAGE. Fulltrain-onlyQC/model/split/controlprotocol must be frozen after sourcePASS and before any decodedneuraloutcomes. Prefer>=8physmice,6-7descriptive,<6stop; no replacements afterneuralQC/outcomes.',neural_boundary='Thisstage NEVERopens/decodes spike_times,spike_times_index,spikecounts,firingrates,amplitudes,waveforms orrawcontinuousbehavior arrays,evenforschema shapes. Whitelistedunitanatomy/curation anddiscrete taskeventvalues only. Opaque HDF5metadata transport maycontainadjacentuninterpretedbytes; no neuraldatasetvaluesdecoded/exported/used.',access=dict(max_assets=13,max_requests=6000,max_total_bytes=150000000,max_metadata_bytes_per_asset=10000000,max_range_bytes=1000000,attempts_per_range=2,full_bulk_fallback=False,source_downloads=0),source_gate='Require trustworthy canonicalunit-anatomy-QC andtask-clock/annotationmapping. No missingessentialfields assumedpass; criticalsourcefailureSTOP. Oneboundedaudit,no newdatasetsearch.',unchanged_scientific_rules='Oldconfirmatory8+8failure unchanged;newexploratory6/8operatingfloors explicitlyowner-authorized. No otherthresholdchange.',next='OnlysourcePASS permitsfullscientificprotocol/numericalimplementation/training-onlyneuralQC; reservedlateoutcomesneveraccessed until allprereleasegates andindependentreviewPASS.'))
    hashes={}
    for root in ['paper14_m0','paper14_m1','paper14_open1','paper14_pivot1']:
        for f in sorted((R/root).rglob('*')):
            if f.is_file() and not {'work','__pycache__'}&set(f.relative_to(R/root).parts):hashes[f.relative_to(R).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
    for path in ['paper13/metadata/fixture.csv','paper13/metadata/clusters_metadata.csv.gz','paper13/metadata/trials_metadata.csv.gz','paper13/metadata/atlas.json','paper13/M0_SOURCE_PIN.json','paper13_ki_feasibility1/transport.py','paper13_ki_feasibility1/headers.py']:
        hashes[path]=hashlib.sha256((R/path).read_bytes()).hexdigest()
    write(P/'INPUT_FREEZE.json',dict(base=BASE,hashes=hashes,scope='HistoricalP14packages and exactreusedmetadata/referencecode only, no P13neuraloutcomes'))
    write(E/'mission.json',dict(mission=dict(id=MISSION,objective='Newexploratorysame-animaltemporalholdoutstudy;source-firstboundedcanonicalaudit;fullscientificexecutiononlyaftereachgatePASS,otherwisehonestSTOP.'),target=dict(workdir=str(R),files=['paper14_v2/**',E.relative_to(R).as_posix()+'/**','ops/daily-operations.md']),instructions=dict(requirements=requirements,constraints=['Preserveallhistory','No newdatasets/cryptoarchitectures','No lateoutcomesbeforefullyfrozenprereleasegates','SOURCEstage metadataonly']),acceptance=dict(validation=['Source/identity/timing/numericalsynthetic tests','Stagegates','Saved/executablereproduction','Independent review','origin-test/readback/clean']),metadata=dict(base=BASE)))
    (E/'goldenstandards.md').write_text(f'''# P14-v2 prospective exploratory mission\n\n{MISSION};BASE{BASE};registered{now};{len(requirements)}atomicrequirements inbaseline.json. Userexplicitlychangesanimalholdout tosame-animaltemporalexploration;oldfailuresimmutable.\n\nProduct/sciencedecisionblock:target ownerresearcher,question scheduledpriorcontextvariationinlocalpredictivevalue;exactmedialfrontalMOs+ACAd+ACAv+PL+ILA;sourceDANDI000409fixedrelease;sourceauditfirst,thenfullnumerical/scientificfreeze,trainQC/development,reviewedone-shotlateevaluation,manuscriptifevaluationvalid. Noordinaryengineeringapprovalneeded;essentialsourcefailure/substantivescientificchanges/numericalcriticalfailureSTOP. No intentambiguityatmetadataauditstage.\n\nFreshHEAD=origin/test=BASE,initialtreeclean;origin/mainabsent(TEST_ONLY_REMOTE_NO_MAIN). Existingopsfoundation/engineer/review/templatesabsent,notinvented. No oldauditrerunwithoutsourcecompatibilityneed.\n\nSource-stageplan:metadata-reader canaries/rangeintegrity/whitelisttests -> schema-firstfixed13canonicalNWBmetadata -> exactunit/atlas/QC andevent/annotationcomparisons -> sourcegate/report. No neuralvalues orneuralshapesdecodedatthisstage. OnlysourcePASS enablesfullmodel/preprocessing/statistics/null/sensitivityregistrationbeforeanyneuraloutcomes. Alllaterrequirementsretained,not replacedbymetadataPASS.\n\nTestlevelL0-L2backend/scientificsynthetic,optionalscientificfigurerender/PDFQAiflatercompleted. Sourceoracle:immutableversion/assetID/size/ETag,hardlinks andexactwhitelistedmetadata,reference-coordinate/UUID/probe/clockconsistency; preserveallmismatches andfailedreceipts. No fullNWBbulk/no protectedneuraldatasetdecoding.\n\nFullPASSrequiresallbaselineitems individuallyverified,bug_count0/warn_count0/unresolvedshrinkrisk0. Failedscientificgateisnotfixedbychangingcriteria. Stopreportandrepro/independentreview/Gitarchive muststillcompleteaftera scientificstop.\n''',encoding='utf8',newline='\n')
    (P/'__init__.py').write_text('"""Source-first registered exploratory P14-v2 study."""\n',encoding='utf8')
    (P/'.gitignore').write_text('work/\n__pycache__/\n',encoding='utf8')
    write(E/'REGISTRATION_RECEIPT.json',dict(utc=now,base=BASE,baseline=len(requirements),historical_hashes=len(hashes),source_assets=13,initial_clean=True,branch_relation='TEST_ONLY_REMOTE_NO_MAIN',owner_sha256=hashlib.sha256(owner.read_bytes()).hexdigest()))
    print(json.dumps(dict(baseline=len(requirements),historical_hashes=len(hashes),source_assets=13,registered_at=now,source_stage='METADATA_ONLY')))
if __name__=='__main__':main()
