"""Build the M0 assessment from saved evidence,including negative/incomplete gates."""
import csv,json,datetime
from collections import Counter
from pathlib import Path
from .core import *
P=Path(__file__).resolve().parents[1];R=P.parent

def write(name,text): (P/name).write_text(text.strip()+'\n',encoding='utf8',newline='\n')

def main():
    s=read_json(P/'results/METADATA_SUMMARY.json');pilots=read_json(P/'results/PILOT_METADATA_SELECTION.json');roles=read_json(P/'results/ROLE_ALLOCATION.json')
    completed=[];execution=[];families=[]
    for p in pilots:
        sid=p['session_id'];transfer=P/'results'/f'TRANSFER_{sid}.json';attempt=P/'results'/f'PILOT_ATTEMPT_{sid}.json';result=P/'results'/f'PILOT_{sid}.json'
        status=read_json(transfer)['status'] if transfer.exists() else 'UNATTEMPTED'
        state=read_json(attempt)['status'] if attempt.exists() else 'NO_NEURAL_ACCESS'
        execution.append({'session_id':sid,'mouse_id':p['mouse_id'],'probe_id':p['probe_id'],'declared_bytes':p['declared_bytes'],'transfer_status':status,'pilot_status':state})
        if result.exists() and state=='COMPLETE':
            d=read_json(result);completed.append(d)
            for f in d['families']:
                families.append({'session_id':sid,'family':f['family'],'original_presentations':f['original_presentations'],'valid_presentations':f['valid_presentations'],'invalid_presentations':f['invalid_or_nonfinite'],'distinct_conditions':f['distinct_conditions'],'repeated_conditions':f['repeated_conditions'],'repetition_min':f['condition_repetition_min'],'repetition_max':f['condition_repetition_max'],'duration_min':f['duration_min'],'duration_max':f['duration_max'],'positive_gaps':f['positive_interpresentation_gaps'],'overlaps':f['overlapping_intervals'],'condition_columns':'|'.join(f['condition_columns']),'pilot_coverage_gate':f['coverage_gate']})
    valid=len(completed)==2 and all(x['coverage_gate'] and x['clock_reference_equal'] and x['event_binary64_roundtrip_pass'] for x in completed)
    independent=s['selected_mice']>=16 and s['Development']>=8 and s['Final_candidates']>=8
    verdict='FEASIBLE_INDEPENDENT_HOLDOUT' if valid and independent else ('FEASIBLE_TEMPORAL_EXPLORATORY' if valid and s['selected_mice']>=4 else 'SOURCE_OR_TIMING_INCONCLUSIVE')
    status={'MISSION_ID':MISSION,'M0_STATUS':'ASSESSMENT_COMPLETE_PENDING_REVIEW_AND_GIT','SCIENTIFIC_FEASIBILITY_VERDICT':verdict,'SELECTED_DATASET':'Allen Brain Observatory Visual Coding Neuropixels','SELECTED_SOURCE_VERSION':'2026-10-18 official warehouse projected manifest + exact EcephysNwb IDs/ETags/SHA256;NWB2.2.2 checked on completed pilots;AllenSDK definitions v2.16.2 commit a9b5c685396126d9748f1ccecf7c00f440569f69;PyNWB3.1.3 actual reader','SOURCE_RIGHTS_PASS':True,'SELECTED_REGION':'VISp plus registered valid laminar descendants;one probe per mouse','INDEPENDENT_CANDIDATE_MICE':s['selected_mice'],'QUALIFIED_POPULATION_DISTRIBUTION':s['tiers'],'STIMULUS_COVERAGE':{'completed_pilots':len(completed),'families_observed':len(families),'both_pilot_coverage_gates':valid},'REAL_SPIKE_PILOT_PASS':valid,'STIMULUS_SPIKE_ALIGNMENT_PASS':valid,'OBSERVATION_CONTRACT':'Nominal curated-release original scheduled presentation intervals minus known selected-probe/global invalid masks;documented common elapsed clock. No raw AP continuity/unknown-dropout certification.','PROPOSED_PRIMARY_QUESTION':'A:strictly past local VISp history increment beyond strong visual/rate/time/measured-behavior baselines','PROPOSED_HOLDOUT_DESIGN':{'Development':s['Development'],'prospective_Final':s['Final_candidates'],'Final_outcomes_accessed':0,'protocol_imbalance':'Dev5BO/23FC;Final27BO. Shared-stimulus prospective estimand and source-transport restrictions required in M1;not an IID8+8 same-protocol claim.'},'KNOWN_LIMITATIONS':['Metadata capacity is not physiological admission or power','Single source/laboratory;sex/genotype/protocol and anatomical proxy limitations','Whole-session providerQC not future A/C-only physiologicalQC','Curated support cannot identify unknown dropout/packet loss/artifacts','Measured running/pupil do not exhaust behavior/arousal','Historical23/55mouse overlap;all26oldroster conservatively exposed;13oldFinal protected','No model,numerical-convergence,effect,confirmation or CWP/NAP evidence'],'PROMPT_2_READY':valid,'BUG_COUNT':0,'WARN_COUNT':0,'GIT_COMMIT':'Resolve from executed live Git closure receipt;not self-certified in this precommit artifact','REMOTE_VERIFICATION':'Pending executed normal origin/test push/readback/clean gate','execution':execution,'assessment_time':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if not valid:status['KNOWN_LIMITATIONS'].append('Required bounded real-pilot/source gate did not complete;no M1activation or positive source/timing claim')
    dump_json(P/'results/FINAL_M0_STATUS.json',status)
    if families:
        with (P/'tables/stimulus_family_feasibility.csv').open('w',encoding='utf8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(families[0]));w.writeheader();w.writerows(families)
    else:write('tables/stimulus_family_feasibility.csv','session_id,family,status\nNOT_COMPLETED,NOT_OBSERVED,Required real-pilot gate incomplete')
    counts=sorted(r['qualified_units'] for r in roles)
    execution_table='\n'.join(f"| {x['mouse_id']} | {x['session_id']} | {x['probe_id']} | {x['declared_bytes']} | {x['transfer_status']} | {x['pilot_status']} |" for x in execution)
    family_table='\n'.join(f"| {f['session_id']} | {f['family']} | {f['valid_presentations']}/{f['original_presentations']} | {f['distinct_conditions']} | {f['repeated_conditions']} | {f['repetition_min']}–{f['repetition_max']} |" for f in families)
    write('P16_M0_REPORT.md',f'''# Paper16 bounded data-first M0 assessment

Mission `{MISSION}`. Exact BASE `bf0e948f57dc49d7c315170c67b9911f72d92530`. Scientific feasibility verdict **{verdict}**. This is an M0 assessment,not a completed paper,physiological admission,model result or confirmatory validation. Engineering closure requires the independent final review and executed Git readback/clean receipt;precommit files do not certify a future SHA.

Primary proposed question **A**,history increment beyond strong causal visual stimulus/rate/time/measured-behavior baselines. B repetition-context differences and C discrete/continuous representations remain prospective secondary possibilities,not active experiments. Title/dataset/hypotheses are not a definitive M1 freeze. The old Transcriptomic/Gene Mapping topic and distinct Closed-Loop roadmap are retained in HISTORICAL_ROADMAP.md.

## Source rights and exact identity

Only CandidateA activated. B/C unassessed,not failed. Official Allen warehouse manifest projected on2026-10-18,all source bodies/queries/SHA256 receipts in metadata/. Exact two NWB file IDs/ETags/byte lengths/currentHEAD are frozen in results/PILOT_OBJECT_FREEZE.json,complete-transfers SHA256 in per-session receipts. Official SDK v2.16.2 source commit a9b5c685396126d9748f1ccecf7c00f440569f69 defines source conventions;actual reader is PyNWB3.1.3,not an executed SDK installation. NWB version/schema compatibility is only established for completed pilots. Last-Modified does not prove release generation.

[Allen terms](https://alleninstitute.org/legal/terms-use/) permit the intended noncommercial research/copying/distribution and attributed academic publication,subject to their conditions,including Freedom to Innovate;commercial redistribution needs separate permission. This is **not CC BY4.0**. [Official registry](https://registry.opendata.aws/allen-brain-observatory/) points to those terms;[citation policy](https://alleninstitute.org/legal/citation-policy/) applies. Data terms are separate from SDK license. No raw-neural Git redistribution or external correspondence. Cite Siegle,Jia,Durand etal.(2021),[Survey of spiking in the mouse visual system reveals functional hierarchy](https://doi.org/10.1038/s41586-020-03171-x),plus Allen dataset/software provenance.

## Actual denominators and anatomy

Source **58 mice/58sessions/332probes/123224channels/135275unfiltered unit IDs**. VISp anatomy in56mice. Do not substitute the tutorial's differently filtered unit denominator. Tiers use same-probe quality good,finite valid-domain metrics,amplitude cutoff<=.1,presence ratio>=.95,ISI violations<=.5,inclusive,and finite positive acquisition rate. Values were registered before first eligibility count;source-validity additions explicitly clarified in revision2 after failed preaccess review,without threshold changes. One invalid probe acquisition rate remains reported;no source-domain invalid metric rows. Whole-session source QC is screening,not future A/C physiological admission.

| Tier units | Mice | Sessions | Probe populations |
|---|---:|---:|---:|
{chr(10).join(f"| {tier} | {v['mice']} | {v['sessions']} | {v['populations']} |" for tier,v in s['tiers'].items())}

One earliest eligible session per mouse,and maximal qualified VISp probe within it,numeric ties. No probe/session/mouse pooling. Selected55populations contain3615metadata-qualified units,min{min(counts)},median{counts[len(counts)//2]},max{max(counts)}. Full tables retain all58mice/all332probes,unselected/excluded rows,IDs,sex/genotype/session type,source eye-tracking flags and available stimulus-family metadata. Official Structure ontology verifies385VISp and all six registered layer descendants,and every used channel structure ID. Atlas/peak-channel membership is a proxy,not histological certainty.

## Prospective roles and contamination boundaries

All26oldP12roster mice conservatively treated exposed;13historical Final mice protected across all sessions. All26source mappings verified against complete session/specimen/donor roster;23overlap the selected55. Historical session protection was repaired to whole-mouse protection before counting. Original failure/cross-session synthetic counterexamples and registration1 remain immutable in evidence. No old worker imported or old neural outcome reopened. P11was a distinct human source;later KI/IBL/other-source tracks do not provide new Allen Visual Coding outcome evidence. Bounded source-history search and conservatism do not establish biological independence across laboratories.

Frozen allocation **28Development/27prospective Final**;all Final are fresh relative to the historical Allen roster. Dev has5BO/23FC;Final27BO. Sex Dev22M/6F,Final22M/5F. Genotype composition remains in all-mouse table. **This is not evidence of IID8+8 within the same protocol.** Proposed primary shared-grating conditional estimand and BO-targeted heldout transport require explicit M1 compatibility/precision rules. No reroll to improve balance after pilot outcomes. Entire pilot mice remain Development. No Final spike access,calibration,QC,scoring or D.

## Bounded real source execution

| Mouse | Session | Probe | Declared bytes | Transfer | Pilot |
|---|---|---|---:|---|---|
{execution_table}

Both objects selected by metadata size before spikeGET;planned3640631888NWBbytes. Payload ledger includes actual newly acquired metadata and conservatively reserves full object bytes before each GET. It never refunds failures/crashes. Exclusive durable attempt prevents duplicate GET;no replacement/retry. Read only first8numeric qualified VISp unit IDs per pilot using lazy PyNWB ragged row access;no other region's spike arrays,no fits or likelihoods. Raw NWB remains ignored local work. Per-unit finite/order/duplicate/binary64 SHA certificates,events/countexamples and complete attempts preserve negative findings.

{len(completed)}/2pilots completed. REAL_SPIKE_PILOT_PASS={valid};STIMULUS_SPIKE_ALIGNMENT_PASS={valid}. Interpretation is curated-release elapsed-clock agreement,not fresh raw/AP or absolute calendar synchronization proof. See alignment and source-compatibility reports for exact successful and failed panels.

## Stimulus and strong-baseline feasibility

| Session | Native family | Valid/original | Conditions | Repeated conditions | Repetitions min–max |
|---|---|---:|---:|---:|---:|
{family_table if families else '| — | No completed real pilot | — | — | — | — |'}

Full family table and per-pilot JSON retain every native family,condition scalar columns/values,repeats,original IDs/order,positive gaps/overlap,durations,blank/NaN parameters,first64valid examples and behavior missingness. Condition metadata str is not causal timestamp serialization;all native start/stop/ID arrays are lossless npz. Nonpilot family presence is source metadata only;their trial/physiological coverage is untested.

Gratings offer orientation/contrast/frequency/phase and onset/offset controls;gabors need position/size;static/natural images need exact image identity;movies require frame/repeat/order and adaptation/drift controls;motion requires direction/speed. Strong B1 must handle these and measured running/pupil availability before attributing any increment to local history. A future movie frame is online only if its predetermined schedule is actually available;otherwise an analysis is offline conditional. Missing behavior cannot be filled with future samples or indefinitecarryforward. No family was selected on neural scores.

## Scientific scope and stopping decision

M0 no B0-B4/D/C/S fitting,hyperparameter selection,null simulation,effect size,power,heldout likelihood or numerical-convergence assessment. The21synthetic regression tests validate source/time/access primitives,not model scientific acceptance. Eight+eight and20aspirational are metadata-capacity concepts,not power/admission guarantees. Future M1 must freeze exact physiological,quantitative precision,causal feature,numerical,inference and falsification rules before model outcomes. No P15 bins/horizons/features/grid/solver thresholds copied. No P13 unstable B* null reused. Single source/recording-anatomy/curated-support/protocol/sex/genotype/behavior limitations remain. No mechanism,independent-lab replication,discrete superiority,confirmation or CWP/NAP claim.

PROMPT_2_READY={valid},conditional only on separately authorized complete M1 registration;no automatic activation. Stop after reviewed M0 archive. Saved-only command: `& .\\paper16_m0\\reproduce_saved.ps1`;it validates source metadata,archived certificates/native events/count aggregates and synthetic regressions,never redownloads or reopens real spike NWB. Source execution and saved-results reproduction are separate evidence levels.
''')
    write('SPIKE_STIMULUS_BEHAVIOR_ALIGNMENT.md','# Real pilot alignment audit\n\n'+json.dumps({'execution':execution,'pilots':[{'session_id':d['session_id'],'unit_certificates':d['unit_certificates'],'behavior':d['behavior'],'invalid_intervals_applied':d['invalid_intervals_applied'],'event_roundtrip':d['event_binary64_roundtrip_pass'],'coverage_gate':d['coverage_gate'],'true_zero_bins':d['true_zero_bins'],'missing_bins':d['missing_bins']} for d in completed]},indent=2)+'\n\nRaw spike arrays are not archived. SHA certificates bind binary64 source rows;native nonneural presentation time arrays/IDs are archived losslessly. Only first64valid presentations/family and8fixed units,10/50ms illustrative bins;no predictive feature or bin selection. Equality/nextafter/zero-vs-missing/gaps tested synthetically. Zero actual missing bins would mean no known support exclusion in these examples,not proof of no unknown dropouts. Running/pupil finite values and timestamp coverage are measurements,not all behavior/arousal. Missingness/eye-tracking failures retained,not imputed. Source-prealigned elapsed clock plus original event boundaries is the accepted curated estimand;no new clock correction or tolerance tuning.')
    write('OBSERVATION_AND_ARTIFACT_LIMITATIONS.md','''# Observation and artifact contract

Use source-curated scheduled original presentation intervals on the documented common elapsed session clock,minus known global or selected-probe invalid masks. Do not infer support from first/last spike or NWB presence. Count only fully supported half-open bins;missing/invalid is None,not zero. Histories reset at presentation/gap/invalid boundaries. Eight fixed metadata-selected units demonstrate access/order/native time,not physiological admission of the full candidate population.

The original P12 native-support failure remains unchanged:raw/AP continuity,packet/dropout completeness and some source calendar/sync provenance were not certified. Existing selected-probe relative-clock diagnostics and physical-stimulus timing metadata are compatible with elapsed curated time,but are historical supporting evidence,not a fresh raw synchronization experiment or retrospective PASS. Absolute calendar metadata disagreement is not corrected here. This study proposes conditional prediction within the curated release,not physical wall-clock inference or spike silence outside observed schedule. Unknown artifacts/missed spikes/drift and sorting contamination remain possible.

Future M1 must specify physiological admission using A/C only,complete exposure/missingness denominators,artifact guards,QC attrition and source-bound timestamps before model evaluation. Source-wide providerQC does not substitute for that. Running/pupil measures are incomplete behavioral nuisance control;protocol/genotype/sex,stimulus repetition/adaptation and atlas/probe location remain possible confounding. No laminar mechanism or causal biological claim. A genuine contradiction invalidating the curated elapsed estimand stops the study;mere file existence does not establish observation.
''')
    write('SOURCE_COMPATIBILITY.md',f'''# Source/interface compatibility

Allen Visual Coding extracellular spikes only. Metadata sources are exact official RMA projections with original bodies and request/SHA receipts. No calcium/Visual Behavior/IBL substitution. Anatomy ontology385and registered layer IDs verified;source unit peak channel->probe->session->specimen mapping preserved. Unit screen follows verified AllenSDK v2.16.2 inclusive defaults explicitly. Last-Modified2020-05-26 is not used as a release-generation proof.

Actual runtime Python3.11.15,PyNWB3.1.3,HDMF4.3.1,h5py3.16.0,NumPy2.4.6. Official PyNWB selective lazy interface;SDK source pinned but package not executed. Reader checks actual NWB root version2.2.2 before namespace loading,and identifier/reference clock before selected spikes. Completed real pilot count={len(completed)};real version/clock/ID/finite/order/native-event certificates exist only for complete receipts. Failed/unattempted states remain explicit in FINAL_M0_STATUS. Synthetic official NWB integration tests use their actual newly written schema through an explicit test-only expected-version substitution;they do not fabricate NWB2.2.2 proof.

Native presentation start/stop/ID arrays are exact npz float64/int values;raw-spike binary64 roundtrip digests are certified without neural redistribution. Condition scalar strings preserve source null/blank values for descriptive metadata and are never causal time inputs. Strict past is event_time<prediction_start,not <=. Reproduction checks adjacent representable/equality and half-open zero/missing/gap behavior. Independent synthetic spy confirms only8selected rows,including refusal to touch a ninth nonfinite sentinel.

All original source/version failures retained. Public response-cookie values redacted at both acquisition writers;original receipt digests preserved. Three failed/interrupted preaccess reviews and their repairs are disclosed in evidence;an intermediate concurrent review was explicitly revoked before any real access,then replaced by a fresh quiescent independently accepted freeze. No cryptographic custody architecture or independent third-party custodian is claimed.
''')
    write('PROPOSED_PRIMARY_QUESTION.md','''# One proposed primary question

A — Does strictly past local VISp neural history improve prediction beyond a strong visual-stimulus,rate,session/time and measured-behavior baseline? This is a proposed observational predictive estimand,not a frozen M1 hypothesis or causal mechanism. Controlled repeated gratings are the suitability preference;shared original condition support across BO/FC and the exact analysis population must be registered before future fitting. No favorable score was used. B repetition-conditioned history differences and C small discrete/continuous models remain prospective secondary possibilities requiring their own falsification/numerical design. No discrete-state winner is assumed.
''')
    write('PROPOSED_EVALUATION_STRATEGY.md',f'''# Proposed evaluation strategy — future authorization required

Current metadata roles28Development/27prospective Final,one same-probe population per independent mouse. All26historical Allen roster mice conservatively excluded from freshFinal;all13historical Final mice barred from pilot. Selected historical overlaps23remain Development. Only2frozen Development pilots authorized;no Final neural outcomes. Preserve exact roles,no result-driven reroll.

Important transport limitation:Development5BO/23FC,Final27BO. A future protocol must define a common-stimulus conditional estimand and BO-targeted heldout generalization,not pretend IID8+8within protocol. The5BODevelopment subset is small. M0 capacity is not power;M1must preregister quantitative precision and attrition thresholds,physiologicalA/CQC and model/inference/null policies. If these cannot support the intended claim,limit or stop before outcomes,not reroll Final.

Future possible DevelopmentA/B/E and FinalC/oneD,all scaling/QC/fitsA/Conly. Calibration/evaluation separation and native causal timestamps required. Mouse-level aggregation/uncertainty/multiplicity,matched units/rates,stimulus/order/repetition/drift,behavior missingness,atlas/probe and protocol sensitivities must be frozen in M1. Proposed endpoint could be gain per nominal curated-release unit-bin with an explicit exposure/missingness denominator,but exact definition is not silently inherited from P15. No Final calibration/D/null/score now. Current readiness={valid};stop after this assessment.
''')
    print(json.dumps(status,indent=2))

if __name__=='__main__':main()
