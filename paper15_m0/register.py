"""P15 data-first rules, frozen before new regional counts or spike access."""
import datetime,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent.parent;P=R/'paper15_m0';E=R/'ops/evidence/2026-10-17/p15-sensorimotor-data-first-m0'
BASE='3f8e903d68c0990af1e1891c7444ff1210830f43';MISSION='P15-SENSORIMOTOR-DATA-FIRST-M0'
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()==BASE
    E.mkdir(parents=True,exist_ok=True);now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    owner=Path(r'C:\Users\85993\.codex\attachments\e574530a-90b4-4a20-b28d-63b26a2d239f\已粘贴的文本.txt');(E/'OWNER_MISSION.txt').write_bytes(owner.read_bytes())
    req=[
    'Verify exactBASE, cleaninitialtree andfreshorigin-test/mainrelation',
    'PreserveP1-P14results/negativefindings; P14remainsarchived/sourcecontractinconclusive',
    'Data-firstM0only; do notfinalizebiology/modelarchitecture/confirmatoryclaims beforefeasibility',
    'AssessnativeIBLBWMfirst,preferONE/ALFwithoutNWBconversionwhenadequate',
    'ConditionalDANDI000010onlyifAunsuitable; exactrelease/license/modalities/uniqueanimals/populations/event/supportcheck',
    'AtmostoneexceptionalexplicitlylicensedpublishedsensorimotorephysfallbackonlyafterAandBunsuitable; preregisterreason',
    'Registeratomicrequirements/scientificscreenbeforefreshregionalcandidatecounts',
    'Registerindependentmouse/session/probeidentitiesandone-localpopulationrule',
    'MOpandSSp/SSssubregionsexactanatomy; noautomaticpooling or artificialpopulationcoverage',
    'Registersimultaneousunit/providerQCtiers5,8,12,20asfeasibilityscreensnotphysiologicaladmission',
    'Registertrial/recordingsupport,eventtiming,artifactexclusions/movementavailability/provenance/license',
    'Prospectiveindependentheldout/temporalexploratory/limitedpilotboundaries,noP14rigid8+8default',
    'Mouseindependentstatisticalunit,notunit/trial/probe/session',
    'Enumerateoriginaldatasetmice,anatomicalmice,probes/labeled/provider-qualityunits',
    'Enumerateusabletrial/windows,motorcoverage,independentmiceperdistinctregion',
    'Reportmultiple-sessions/mouse,lab/sourcecomposition andmetadataexclusions',
    'Selectoneadequatelysupportedanatomicalregion; anywiderestimandmustbeseparatelynamed/prospectivelyauthorized',
    'Neverglobaldatasetsize==localsample; exactdenominators andnoanimalpseudoreplication',
    'Beforepilot verifyrights/provisionalanatomy/mouseidentity/evaluationaccessboundaries',
    'Prespecifyatmosttwodevelopment/pilotsessionsby metadata-onlyrules; nofinalreservedanimals',
    'Demonstraterealspiketimestamploadusingprovider-supportedAPI/documentedreader',
    'Verifyactualunit-probe-anatomymapping; nonfinite/ordering underdocumentedcuration',
    'Smallnonpredictivebin-countdemonstration,zero-spikebinsretained',
    'Verifyevent/spikeclockjoin,recordinginterval/supportandknownartifacthandling',
    'Recordactualdataaccess/processinglimitations; nofeasibilityPASSfrommetadataalone',
    'Bounddownloads/cacheessentialfilesonly; nofullcohortspikeacquisition',
    'Nopredictivemodelfit/dynamicscomparisons/modelwinningscores orreservedtestoutcomes',
    'Normalcurated-releaseQCaccepted samplingframewithlimits; noabsolutelosslesshardwarecertificate',
    'Useknowninvalid/artifactannotationswhenavailable; absenceisnotartifact-freeproof',
    'Distinguishverifiedobservations,conventionalcuratedobservations,knowninvalid,essentialtiming/sourceunknown',
    'Stoponlyessentialmeasurementfailure,notnonessentialadministrativecertificateabsence',
    'Nocryptographiccustody/offlineauthorizationinfrastructureorunrelatedframework',
    'Selectoneprimaryquestionfromhistoryincrement/motorpreparation-dynamics/epochtransitionbydatarelevanceandnuisancecoverage',
    'Questionselectionneverbasedonmodelresults; noassumedHMMwinner/physicalprimitive',
    'Movement-alignedwindowsofflineevent-conditionednotreal-timemovementforecasting',
    'Allfuturepredictorscausallyavailablebeforepredictionbin',
    'AssessB0stationary/B1task-time-stim-movement/B2ownhistory/B3population/B4combinedfeasibility',
    'AssesscompactD/lowdimC andstaticmixtureiftemporal-stateclaim; noimplementationorfitting',
    'DonotimportP13unstableautoregressivePoissonnull; distinguishmovement/timing/simplehistory',
    'ReturnoneoffivefrozenM0scientificverdictswithgatedlicense/cohort/pilot/timing/question/design',
    'Metadataeligibleanimalsnotphysiologicallyadmitted; nosuperiority/neurodynamicsvalidationclaim',
    'Ifneitherpublicsourcesupportsusefulstudy,stopwithconciseevidence',
    'ProposedM1handoffonlyiffeasible:dataset/region/question/source/version/cohort/pilottestedspikes',
    'Handoffincludesobservationcontract/proposedphysiologyQC/dev-holdoutstrategy',
    'Handoffincludesstrongbaselines/D-C/statisticalunit/inference/falsification/limitations',
    'M1specificationisproposalNOTactivation; noM1-M7autostart',
    'Reusetrustedtools/metadataproportionally,norepeatedfullsourceauditsordecorativehashthousands',
    'Repairordinaryparser/API/sourceextractionbugsautonomouslywithregressions;preservefailures',
    'Noopenendedsourcearchaeology/result-driveneligibility/newdatasetoutsidebound',
    'Independentinternal scientificreviewofM0conclusion,notexternalpeerreviewclaim',
    'DeliverP15_M0_REPORT.md andsource/licenseregistry',
    'Delivermouse-session-probe-regioncoverage/realspikepilotreport/observation-timing-artifactlimits',
    'Deliverquestion/rationale/proposedM1protocolspec',
    'Compactsynthetic/regressions andsaved-onlynativePowerShellreproduction',
    'AllrequestedM0status/verdict/dataset/region/mice/pilot/contract/holdout/limitations/readinessfields',
    'Freezeallrequirements,traceeveryitem,bugwarncounts/honestblockers/nosilentcontractshrink',
    'Mission-onlydiff/dailyheaderpreservepriorbytes;exactstagingnormalorigin-testcommit/push',
    'ReviewedGitarchivewithliveremoteSHA/allchangedblobverification/cleanworkingtree',
    'StopafterM0,nofullstudyactivation,reservedoutcomereleaseorretrospectiveoldPASS'
    ]
    write(E/'baseline.json',dict(mission=MISSION,base=BASE,frozen_at=now,count=len(req),requirements=[dict(id=f'REQ-{i:03}',requirement=s,status='OPEN') for i,s in enumerate(req,1)]))
    policy=dict(mission=MISSION,base=BASE,registered_at=now,stage='BEFORE_NEW_SENSORIMOTOR_COUNTS_OR_SPIKE_OUTCOMES',
      candidates=['A_native_IBL_Brainwidemap','B_DANDI000010_only_if_A_unsuitable','C_one_extra_only_if_A_and_B_unsuitable_with_prior_reason'],
      sourceA=dict(tag='Brainwidemap',metadata_insertion_fixture='2023_12_bwm_release',metadata_aggregate='2024_Q2_IBL_et_al_BWM',provider_code_commit='118fc36cb3602934466ad2c6087c2b3b441f9f1f',sorting_revision='2024-05-06',
        source='NativeONE/ALFpublicIBL; exactpilotdatasetUUID/revision/size/hashfrozensubsequentlybeforedataaccess. NoNWBconversiondependency. Originalmatchedaggregatemetadatacountsarecandidates,notguaranteeofcurrentper-sessionannotationequivalence.'),
      regions=['MOp','SSp-ul','SSp-bfd','SSp-ll','SSp-tr','SSp-n','SSp-m','SSp-un','SSs'],
      anatomy='Exactparentorstandardlaminardescendants(1,2/3,4,5,6a,6b); distinctSSpsubdivisionsreportseparately,noMOp-SSp/SSs/probepooling. Unrecognizedparent-prefixedlabelsreported,notfuzzyjoined.',
      unit_tiers=[5,8,12,20],primary_population_screen=8,unit_QC='Providerlabel==1 ononeprobe. Sourcecuration canusesession-widespikes; notnewtrainingonlyphysiology.',
      trial_screen=dict(window=[0.,.5],anchor='stimOn_times',metadata_rule='Finiteintervalstart/stim/goCue/feedback/stop;start<=stim<=feedback<=stop,cueinsidetrialbeforefeedback,stim+.5<=stop;bwm_includeTrue andsaturation_stim_plus06False forpairednativeaggregatemetadata. Cue/stimneednotarbitraryfixedordering. No taskcontextrequirement.',
        minimum_total=100,minimum_per_original_half=40,
        halves='Originaltrialordinalfloor(N/2) beforeexclusion;wholechronologicaltrialgroups, no adjacentbinrandomization.',
        pilot_rule='Nativepilotactualevent/mask/intervalrevisionsverified. DoNOTtransferoldaggregatemasksifsourceevents/revisionsincompatible. Nativecurrent documentedtrialcuration andknownbadintervals maybeused transparentlywithoutold-equivalenceclaim; exactsourcepin/curationfacts frozenbeforepilot.'),
      design=dict(independent='>=12metadata-candidatemiceattier8andtrialscreen;dev=n-max(6,floor(.4*n)),final=max(6,floor(.4*n));both>=6. Feasibilityonly,notpower/confirmatoryPASS. n_final6minsignflip2/64=.03125foronesinglecontrast;anyfuturefamily/powerneedsM1assessment.',
        temporal='6-11candidateindependentmiceattier8:within-mouseearly/latewholetrialholdout,exploratoryonly.',
        pilot_capacity='1-5candidateindependentmice:limitedpilot/feasibility,nopopulationconfirmation;0qualifiedmiceinsufficientforthisregion.',
        tier_role='5/8/12/20screensnotuniversalphysiologythresholds. Primary8permitslocalpopulationhistorywith>=7otherunits;smallcapacityrequiresrestrictedinterpretation.',
        region_selection='Firstregioninregisteredorderqualifyingindependentdesign,elsefirsttemporaldesign,elsefirstlimitedpilot;notbestneuraloutcome. Sameprobe/sessionwithinmouse rankedgoodtargetunits,minhalftrials,lexicaleID/pid.',
        allocation='Onceprimaryregionselected,sortmicebySHA256(mission+subject) withinlabs andinterleaveorderedlabs;finalinitialeveryroughly40percent usingfloor cumulativefinalfraction,devotherwise. No neuraloutcomes/exposedpilotcanenterfinal.',
        pilot='Atmosttwo distinctdevelopmentmice,metadata-only highestavailabletier/validtrials thenlexicaleID/probe;theirwholemouse isdevelopment permanently. FreezeexactIDs beforefirstspikeread. No replacementafter neuralfeasibilityfailure without newprospective scope.'),
      validity=dict(accepted='ConventionalpubliccuratedALFspikes/providerQC+documentedtimebaseandusableboundedobservations,withtransparentmeasurementlimits. Notabsolutelosslesshardwareguarantee.',
        artifacts='Useproviderknownsaturation/badintervals/releasecurationwhenavailable. Missingannotations=>unknownartifactburden/limitation,notautomaticallywhole-recordinginvalidorartifact-free.',
        essential='Mustdefendunit/probe/anatomyidentity,finiteorderedspikes,task/spikecommonclock,realrecording/trialwindowmeaning. Source/timebasecontradictionorindefensibleduration=>INCONCLUSIVE_DATA_VALIDITY.',
        zeros='Binswithzerospikesretainedinsideconventionalcoveredtaskwindows;knowninvalidsupportmaskedseparately(not0). Neverinfervalidextentsolelyfirst/lastobservedspike.'),
      limits=dict(real_pilot_sessions=2,real_spike_files_total_bytes=1200000000,max_file_bytes=450000000,metadata_documents_bytes=30000000,metadata_requests=200,download_attempts_per_file=2,
        essential_files='spikes.times/clusters;clustermetrics/UUID/channel/atlasmapping;trialevents,wheelposition/timestamps andsourceinvalid/saturationintervals ifavailable. No rawAP/LFP/video/waveforms/fullcohortspikes.',
        supported_api='OfficialONE/ALFobject/datasetreader;isolateinstallruntimeandcacheundernewwork/. Registeredexactnativefileinventorybeforeaccess.'),
      questions=['Localown/populationhistoryincrementbeyondmovement/task/ratebaselines','Compactdiscrete/continuousincrementaroundmotorpreparation/execution','Predictivestructuretransitionacrossdocumentedsensory/motorepochs'],
      question_selection='Aftermetadataandpilotchooseonescientificquestiononcausalnuisanceavailability/timebaseandregionrelevance;no predictivefit/scores;M1mustfreezehypotheses/architecture.',
      exposure='P13IBLroutewasmetadataonly;P13realexposedKIandP14metadatastudiesarenotfreshconfirmationdata. Verifysource/exposurebeforepilot;allP15pilotmicepermanentlydevelopment. Allotherreservedfinalneuraloutcomesforbidden.',
      scientific_verdicts=['FEASIBLE_INDEPENDENT_HOLDOUT','FEASIBLE_TEMPORAL_EXPLORATORY','LIMITED_PILOT_ONLY','INCONCLUSIVE_DATA_VALIDITY','DATA_INSUFFICIENT'],
      no_models=True,stop_after='M0reviewedhandoffandverifiedGitarchive;noM1-M7activation')
    write(P/'M0_REGISTRATION.json',policy)
    inputs=['paper13/metadata/fixture.csv','paper13/metadata/clusters_metadata.csv.gz','paper13/metadata/trials_metadata.csv.gz','paper13/metadata/atlas.json','paper13/metadata/bwm_loading.py.source','paper13/M0_REPORT.md','paper14_native1/FINAL_DELIVERY.json']
    write(P/'INPUT_PINS.json',dict(base=BASE,hashes={s:hashlib.sha256((R/s).read_bytes()).hexdigest() for s in inputs},purpose='Sevenloadbearingreusedinputs only; no decorativehistoricalhashscan. Gitmissionmanifestpreservesallotherhistoricalfiles.'))
    write(E/'mission.json',dict(mission=dict(id=MISSION,objective='Data-firstM0:onepublicsensorimotorregion/native-sourcefeasibilityplusatmosttwodevelopmentspikepilots;proposedM1only,nofit/finaloutcomes.'),target=dict(workdir=str(R),files=['paper15_m0/**',E.relative_to(R).as_posix()+'/**','ops/daily-operations.md']),instructions=dict(requirements=req,constraints=['PreserveP1-P14','No model fitting orfinalspikes','Boundedcandidates/pilots','NormalcuratedscientificQCnotabsolutecertificates']),acceptance=dict(validation=['Compactsynthetic/regression','Atmosttworealpilots','Saved-onlyPowerShell','Independentinternalreview','origin-test/readback/clean']),metadata=dict(base=BASE)))
    (E/'goldenstandards.md').write_text(f'''# P15 M0 data-first baseline\n\n{MISSION};BASE{BASE};frozen{now};{len(req)}atomicitems. Ownerauthorizesonedatasetfeasibilityselection,atmosttwoprespecifieddevelopmentspikepilots,nomodelscores/finaloutcomes. ThisisnewP15,notP14recovery.\n\nProduct/sciencedecision: scientificdatafeasibilityprecedesbiologicalhypothesis/modelarchitecture. NativeIBLfirst,conditionalDANDI000010second,atmostoneexceptionalfallbackonlyifbothunsuitable. Targetregionsdistinct,tiers5/8/12/20,primarytier8;independentdesign>=12with>=6dev/6final,temporal6-11,limited1-5. Nopowerprooforforcedconfirmatoryclaimfromcounts. Openmaterialdecisions=0atmetadata-stage.\n\nFreshfetchHEAD=origin/test=BASE;initialclean;origin/mainabsent(TEST_ONLY_REMOTE_NO_MAIN). Repositoryfoundation/engineer/review/templatesabsent;userdirectiveretained.\n\nPlan:freeze ->nativeofficiallicense/methods ->reusedmatchedmetadataregioncoverage ->selectregion/dev-final/pilotIDsandexactsourceinventory ->compactcanaries ->boundedtwo-realspikepilots ->scientificquestion/M1proposal ->independentM0review ->savedrepro/normalGit/remotehash/clean ->STOP. Nounnecessarycodeframework/custody/thousandsoffilehashes.\n\nValidityoracle: normalpubliccuration/timebase/identity/orderedtimestamps,knowninvalidintervalmaskseparatefromzeroobservedbins;noabsolutepacketcertificate. Allpredictorsfuturecausal,butnonefittedhere. L0-L2scientificbackend,realpilotproofcannotbereplacedbymetadata/synthetic. NoUI/channelcertificationapplicable. Allrequirementsretained;conditionalitemsnotactivatedmusthaveexplicitreason. PASSonlycompleteapplicablecontractbug0warn0;source/physiologylimitationsneverbecamemodelvalidation.\n''',encoding='utf8',newline='\n')
    write(E/'REGISTRATION_RECEIPT.json',dict(mission=MISSION,base=BASE,frozen_at=now,requirements=len(req),reused_input_pins=len(inputs),new_region_counts=0,real_spike_sessions=0,predictive_fits=0,final_outcomes=0,branch_relation='TEST_ONLY_REMOTE_NO_MAIN',initial_clean=True))
    (P/'__init__.py').write_text('"""P15 data-first bounded feasibility."""\n',encoding='utf8');(P/'.gitignore').write_text('work/\n__pycache__/\n',encoding='utf8');(P/'work').mkdir(exist_ok=True)
    print(json.dumps(dict(requirements=len(req),registered_at=now,input_pins=len(inputs))))
if __name__=='__main__':main()
