"""Prospective canonical-native metadata registration before fresh counts."""
import datetime,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent.parent;P=R/'paper14_native1';E=R/'ops/evidence/2026-10-17/p14-v2-canonical-native-recovery'
BASE='b09b1b254d3f8b9c5fd4be948befae0332f6b96a';MISSION='P14-V2-CANONICAL-NATIVE-RECOVERY'
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()==BASE
    now=datetime.datetime.now(datetime.timezone.utc).isoformat();E.mkdir(parents=True,exist_ok=True)
    owner=Path(r'C:\Users\85993\.codex\attachments\fd3d13b1-39e4-4b5c-8ae7-005038ce3c69\已粘贴的文本.txt')
    (E/'OWNER_MISSION.txt').write_bytes(owner.read_bytes())
    req=[
    'Exact BASE/fresh origin-test relation; preserve initial clean working tree',
    'One current mission; metadata only, no neural datasets/shapes/raw behavior decoding',
    'Preserve all P1-P13 and prior P14 failures, original source contract inconclusive',
    'Preserve missing old masks and exact794movement discrepancies; no retroactivePASS',
    'Retain original audited-one/unaudited-twelve historical state as historical evidence',
    'Register canonical-native amendment and atomic requirements before fresh cohort counts',
    'Use exclusively DANDI000409/0.260309.1324 CC-BY4; attribution and exact official asset identities',
    'Question remains scheduledprior.2vs.8 incremental predictive dynamics, not measured belief or causal mechanism',
    'Keep exactMOs/ACAd/ACAv/PL/ILA documenteddescendants; labelMEDIALFRONTALCORTEX',
    'One simultaneous probe/mouse; no probe/session/animal pooling/date substitution',
    'Bothcontexts and original maximalwhole-block chronological cut before exclusions',
    'Original.5second stimulus window and source-compatible ten-unit screen',
    'Retain>=2qualifyingruns/context,>=15usabletrials/run,>=60trials/context/originalhalf prospectively',
    'Strongcontextaware B0-B4 and D/C/invariant-dependent requirements retained for later protocol, no assumedwinner',
    'Exploratorywithin-animal temporalholdout; no independentanimalconfirmation',
    'New canonical policy has no oldtable byteequivalence requirement; never transferoldbwm/saturationflags',
    'Canonicalnative validity uses documentedtaskevents and authoritativeobservation/artifactsupport metadata',
    'Missing annotations UNKNOWN, never absent-artifactPASS or neural observation inferredfromtrialtimestamps',
    'Essential observationvalidity unknown ->sourceinconclusiveSTOP; no silent relaxation',
    'Audit historicalfirstMovement and canonicalwheelonset meanings/procedures/versionlimits',
    'Do not infer clockfault or increaseold1e-6comparison tolerance',
    'Movement versiondependent/unavailable nuisance excludedfrom primary canonical estimand prospectively',
    'Permanently withholdmovement/arousal-independentdynamics claims',
    'No canonicalmovementpredictor absent synchronizedmeaning verification; no futureevent/outcome featureleak',
    'Afterfreeze auditremainingtwelve same canonicalnative rules; retainall13identity/exclusionrows',
    'Reuse firstsession savedwhitelistedmetadata but supplementonly missingcanonicalmetadata through boundedreader',
    'Atmostone sourcewidemetadata re-enumeration onlyifnecessary under frozenpolicy; notautomaticornewdataset',
    'No outcome-basedmouse/probe/model selection or neuraloutcomes',
    'Exact independentmouse denominators distinguishmetadata candidates, supporteligible and physiologicaladmission',
    'Report canonical targetunitcoverage,leaf/MOscomposition and providerQC availability',
    'Report bothcontext trialcounts, originalblocks/halves and alltrial exclusionreasons',
    'Report observation/support evidence and remaining provenanceunknowns per session/probe',
    'Old13estimate never assertednewcanonicalcohort; preserve exactmismatches/exclusions',
    '>=8potential exploratoryinference,6-7restricteddescriptive,<6data-insufficient onlyaftertrustworthyeligibility',
    'Metadata capacities pendingactual A-onlyphysiology; none admittedbythismission',
    'Ifsource/cohort/timingPASS completeprospectiveM1 physiologyQC and preprocessingdefinitions',
    'Ifsource/cohort/timingPASS completeB0-B4/D/C modelmath/parameters/selection/budgets',
    'Ifsource/cohort/timingPASS completecausal/numerical/independentgradient/optimizergates',
    'Ifsource/cohort/timingPASS completevalidboundedfalsification/sensitivity/statistics/claimrules',
    'Ifsource/cohort/timingPASS one frozenlateholdoutpolicy withindependentreview beforeoutcomes',
    'Never accessneuralarrays or executeM2-M7,physiologicalfits,modelselection/finalevaluation',
    'Returnexactlyone of four registeredscientificdecisions, no metadata scientificvalidation',
    'Criticalsource/observationinsufficiencySTOPandrecommendarchivecurrentP14route',
    'No automaticnewsource/bridgerescue/thresholdchange/cryptoarchitecture',
    'Delivercanonicalsourceamendment,exactdenominators/exclusionmatrix/versiondifferences',
    'Completemission-only regressionsandsaved-only PowerShellreproduction withnetworkdenied',
    'Independentinternalprospectivecontract/readerreview before counts and finalcompletearchivereview',
    'Preserveunsuccessfulreviews/receipts and fixordinaryimplementationdefectswithregressioncoverage',
    'Fullatomicpreservationmatrix,bugwarncounts,honestblockedrequirements,no silentN/A or scope shrink',
    'Update daily-operations preserving oldbodybyteexact; exactstagingonly',
    'Normalcommit/pushorigin-test,no force/main/PR',
    'Live remoteSHA/changedfilemanifest/evidencehashes/clean gate verified',
    'Stopafterreviewedmetadataonlydecision; no automaticneuralactivation'
    ]
    write(E/'baseline.json',dict(mission=MISSION,base=BASE,frozen_at=now,count=len(req),requirements=[dict(id=f'REQ-{i:03}',requirement=t,status='OPEN') for i,t in enumerate(req,1)]))
    roster=json.loads((R/'paper14_v2/SOURCE_AUDIT_ROSTER.json').read_text())
    write(P/'SOURCE_AUDIT_ROSTER.json',dict(registered_at=now,records=roster['records'],scope='Historical13 exact sessions/probes retained as bounded audit frame only; first previouslyaudited,remainingtwelve previouslyunread. No oldunit/QC/masks imported as canonicaleligibility.'))
    contract=dict(mission=MISSION,base=BASE,frozen_at=now,mode='METADATA_ONLY_BEFORE_NEW_CANONICAL_COUNTS',
      source=dict(dandiset='000409',version='0.260309.1324',license='CC-BY-4.0'),
      estimand='Conditional incremental D/C vsstrongB4 predictivegain interaction scheduledprior.2minus.8 usingcanonicalnative trials/curation andsameunits;futurewithin-mouseearly/lateholdout. No movement-independent,belief,causal oranimalconfirmationclaim.',
      historical_policy='OldsourcebridgeFAIL/794differences/1e-6unchanged. Newroute doesNOT requireoldprocessingagreement; oldbwm/saturationannotations NEVER transferred.',
      anatomy=dict(parents=['MOs','ACAd','ACAv','PL','ILA'],laminae=['','1','2/3','4','5','6a','6b'],unit_mapping='Canonicalunit->max_electrode row->canonical localization localized_entity->brain_region/atlas_id; verify sameprobe,finitecoordinates,uniqueunitIDs/UUIDs. Exactacronyms only, no fuzzyfullname/oldunitatlasimport. AtlasreferenceID-to-acronym allowed as ontology only.',
        quality='canonicalibl_quality_score==1;providerrelease/sessionQC not trainingonlyphysiology',floor=10,selection='Preserve exact historicalsession+probe;one permouse. Sourcewide enumeration ifactivateduseshighestqualifiedtargetunitcount,minimumcontext-halfcoverage,lexicaleID/probe;no outcome.'),
      task=dict(contexts=[.2,.8],neutral=.5,window_seconds=.5,
        validity='Canonicalfiniteordered start<=stimOn<=goCue<=feedback<=stop,start<stop,stimOn+.5<=stop;finitechronologicalstim. Exactcanonicalstimulus/side/context fields required forbaseline; missingunknownexclude/report. No oldbwm/saturationreactiontime/performance mask.',
        blocks='Maximalconsecutive .2/.8 runs on ORIGINALroworder beforeexclusions;neutral/unknownbreak. Cutfloor(numbernonneutralruns/2) beforeexclusions;earlytraining/lateevaluation capacities, never random bins.',
        min_trials_per_run=15,min_runs_per_context=2,min_trials_per_context_half=60,
        movement='Prospectively version-dependent nuisance; NOT required forprimarytrialvalidity orprimarypredictors. No oldmovementmask; no movementindependenceclaim. Canonicalcausalpredictor onlyifmeaning/synchronizationindependentlyproved in futureprotocol.',
        future_behavior='Choice/reward/feedback/responsenever used beforemeasuredtime; thismission fits nothing.'),
      observation=dict(required='Exact.5s windows mustbe within authoritative neuralobservation/support intervals and exclude documented artifact/invalid intervals with completeness/scope provenance. Both recordingcoverage and artifactvalidity required independently of task-event validity.',
        evidence='Nativeunitobs_intervals/validobservationtables orrelease/probe-specific authoritativecoveragecertificate;artifact/bad/saturationintervals orverified exhaustive negativeannotationcertificate. Validateclock,probe/unit scope,finiteorderedintervals andwindowcoverage.',
        unknown='Absentrecording/artifactannotation UNKNOWN;emptyundocumentedtable isUNKNOWN,notproofartifactabsence. Trial/active-sessionepochs,providerunitquality,finitecoordinates,spikesortinglabel andfileexistence alone never certify continuousobserved/artifactvalidwindows. Knownartifactoverlap excludeswindow;unknownsupportblocksanalysis.',
        decision='Any essentialsource-supportunknown => SOURCE_CONTRACT_INCONCLUSIVE ratherthan interpretingunknownaszeroeligibleorDATA_INSUFFICIENT.'),
      operating=dict(preferred=8,restricted_descriptive=[6,7],stop_below=6,physiology='Allcapacities metadata-only pending A-onlyQC;zero neuraladmissions.'),
      bounded_audit=dict(primary_assets=13,sourcewide='ONEoptionalmetadataenumeration onlyifprimaryframe ordinaryeligibility<6 ANDsourceunit/task/observationcontract verified. DoNOT usemassre-enumerationtoevadecriticalobservation/provenanceunknown. No alternatedates/probepooling;fixedreleaseonly.',
        max_assets=13,max_requests=16000,max_total_bytes=100000000,max_metadata_bytes_per_asset=5000000,max_range_bytes=1000000,attempts_per_range=2,full_bulk_fallback=False,
        documentary_max_requests=24,documentary_max_bytes=12000000,
        boundary='Metadatafields only;no neural values/shapes orrawbehavior. Opaque exact HDF5 transport maycarryadjacentuninterpretedbytes;neverdecodeforbiddendatasets. Newjournals/cacheonly;oldfilesimmutable.'),
      next='Ifsourceunit/task/support andcapacityPASS completeM1protocolonly. No realneuralQC/fits/scoring/modelselection/final access underthismission.',
      scientific_verdicts=['CANONICAL_NATIVE_M1_READY_FOR_NEURAL_QC','CANONICAL_NATIVE_FEASIBLE_BUT_PROTOCOL_INCOMPLETE','SOURCE_CONTRACT_INCONCLUSIVE','DATA_INSUFFICIENT'])
    write(P/'CANONICAL_CONTRACT.json',contract)
    hashes={}
    for name in ['paper14_m0','paper14_m1','paper14_open1','paper14_pivot1','paper14_v2']:
        for f in sorted((R/name).rglob('*')):
            if f.is_file() and not {'work','__pycache__'}&set(f.relative_to(R/name).parts):hashes[f.relative_to(R).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
    for name in ['paper13/metadata/fixture.csv','paper13/metadata/atlas.json','paper13/metadata/atlas.provenance.json','paper13/metadata/bwm_loading.py.source','paper13/metadata/bwm_loading.py.source.receipt.json']:
        hashes[name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
    write(P/'INPUT_FREEZE.json',dict(base=BASE,hashes=hashes,scope='AllpriorP14packages excludingignoredrawcache;exactfixedreferenceontology/fixture/staticcurationcode, noneuraloutcomes. Gitmanifestprotectsallotherhistoricalfiles.'))
    write(E/'mission.json',dict(mission=dict(id=MISSION,objective='Oneboundedcanonicalnative metadata-only amendment andcohort/support audit;completeM1onlyifsourcegatesPASS,otherwisearchive truthfulSTOP.'),target=dict(workdir=str(R),files=['paper14_native1/**',E.relative_to(R).as_posix()+'/**','ops/daily-operations.md']),instructions=dict(requirements=req,constraints=['No neuralarrays/shapes/rawbehavior','Preservehistory','No scientificoutcomes orM2-M7','No oldmasktransfer']),acceptance=dict(validation=['Syntheticmetadata/causality/supporttests','Independentreview','Saved-onlyPowerShellreproduction','Exactorigin-test/readback/clean']),metadata=dict(base=BASE)))
    (E/'goldenstandards.md').write_text(f'''# Canonical-native prospective contract\n\nMission {MISSION};BASE {BASE};frozen {now};{len(req)} atomic items inbaseline.json.\n\nProduct/science decision: ownerresearcher asks whether fixedofficialcanonicalrelease can independentlysupport scheduledprior-context predictive-dynamicsquestion. Newcanonicalvalidity replacesoldtableequivalence forNEWtrackonly,explicitlyownerauthorized. OldsourceFAIL remainsimmutable. Bothcontext/sameprobe/wholeblock/.5s and scientificclaim boundariespreserved. Movementversiondependentnuisance unavailable;no movementindependence claim. Missingobservation/artifactevidence staysUNKNOWN. Openmaterialdecisions=0atmetadata-stage.\n\nPreflight: HEAD=origin/test=BASE,initialtreeclean,origin/mainabsent(TEST_ONLY_REMOTE_NO_MAIN);no branchrepair. Localopsfoundation/engineer/review/templatesabsent;userdirectiveused.\n\nPlan:freeze ->independentlyreviewcontract/readercanaries ->staticcanonicalsource/task/observationmetadata ->same13sessionauditincludingremaining12 ->canonicalunit/taskcapacityandobservationtri-state/exclusions -> independentdecision. Sourcewideenumeration isconditional andcannotrepairmissingobservationcontract. OnlysourcePASSpermitsfullM1freeze;thismissionNEVERneuralQC/fits/outcomes.\n\nOracle: exactassetID/blob/size/ETag/rangeandhash;whitelistmetadata;sourceunit-electrode-atlas/probeidentity;canonicaltaskorder/blockwindows;explicitneuralobservationsupportandartifactannotationprovenance. UnknownneverPASS. TestlevelL0-L2synthetic/savedmetadata;noUI/channelapplicability.\n\nExit:oneoffourregisteredscientificdecisions,separateK4Cterminalstatus. FullPASSonlyallatomicrequirementsverified/approvedequivalent,bug0warn0;sourceSTOPretainsblockeddownstreamrequirements andstillfinishesreport,repro,review,normalorigin-test/readback/clean. No hiddenrelaxation,datasetsearchornewcustodyarchitecture.\n''',encoding='utf8',newline='\n')
    write(E/'REGISTRATION_RECEIPT.json',dict(registered_at=now,base=BASE,requirements=len(req),historical_hashes=len(hashes),newcanonical_reads=0,newcohortcounts=0,neuraloutcomes=0,initial_clean=True,branch_relation='TEST_ONLY_REMOTE_NO_MAIN'))
    (P/'__init__.py').write_text('"""Canonical-native metadata-only P14 source contract."""\n',encoding='utf8');(P/'.gitignore').write_text('work/\n__pycache__/\n',encoding='utf8')
    print(json.dumps(dict(registered_at=now,requirements=len(req),historical_hashes=len(hashes))))
if __name__=='__main__':main()
