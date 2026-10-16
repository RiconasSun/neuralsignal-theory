"""Exclusive prospective registration of one bounded PL data-contract inquiry."""
import datetime
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parent
E=ROOT/'ops/evidence/2026-10-15/p13-ki-pl-quality-epoch-resolution-1'


def main():
    E.mkdir(parents=True,exist_ok=True)
    user=Path(r'C:\Users\85993\.codex\attachments\e8ed279d-0148-4992-a7ef-23a70be0fb83\已粘贴的文本.txt')
    with (E/'USER_MISSION.txt').open('xb') as f:f.write(user.read_bytes())
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    policy={'mission':'P13-KI-PL-QUALITY-EPOCH-RESOLUTION-1','utc':now,
            'base':'0eba2fe4a47b0d6392159bfe24a3343a0f7ff1c6',
            'candidate':{'dandiset':'000473','version':'0.230417.1502','region':'PL','task':'aversive-conditioning pre-tone'},
            'prior_evidence':'paper13_ki_feasibility1/results/review1/audit.json; historical findings never reclassified',
            'estimands':{'A':'recording-supported genuine pure-tone[-3,0)s windows, state/movement-unrestricted with explicit limitations and known invalid/saturation exclusions',
                         'B':'provider-active matched genuine pure-tone[-3,0)s windows only; no awake/state equivalence assumption'},
            'fixed':{'minimum_epochs':120,'epoch_seconds':3,'development_mice':8,'final_mice':8,'proposed_eligible_units_per_mouse':8,
                     'historical_raw_PL_mice':20,'historical_basic120_mice':20,'historical_active120_mice':15},
            'allowed':['existing saved000473metadata','source/licensing/schema/export definitions','published quality-selection documentation','provider event/observation/saturation/manual/active intervals and provenance','proposed future train-only QC and scientific protocol','synthetic metadata/config/interval tests'],
            'forbidden':['real spike values or cumulative-spike-index values','raw waveform/LFP/EMG/behavior samples','neural model fitting','final evaluation','new dataset search','historical gate promotion','threshold relaxation','P1-P12/originalP13/priorKI mutation','sending author requests without separate instruction'],
            'quality_policy':'Metadata-supported meanings only. If ratio/units/provenance cannot be verified within bounds, state unknown and propose explicit future training-only QC; no actual eligible-unit certification.',
            'epoch_policy':'Retain original bounds separately; source-backed known invalid masks can reduce newly proposed valid coverage without overwriting historical counts. Never equate basic and awake. Missing private creator hashes alone do not require an impossible packet-loss certificate.',
            'bounds':{'datasets':1,'existing_headers':25,'new_header_assets':25,'new_source_files':24,'new_repositories':3,'new_documentation_pages':8,
                      'new_http_requests':800,'new_transport_bytes':67108864,'per_object_range_bytes':12582912,'attempts_per_request':2},
            'source_selection':'Existing pinned pfcmap/DANDI references and directly linked converter/quality documentation only; no open-ended search or unrelated sources.',
            'decision':['PROTOCOL_READY_PENDING_NEURAL_QC','INCONCLUSIVE_METADATA','DATA_INSUFFICIENT'],
            'readiness':'A defensible explicitly limited source-backed contract and a proposed physiological-QC gate may be ready before neural QC; this does not certify16eligible animals. Essential clock/epoch/anatomy contract gaps cannot be waved through.',
            'stop':'Evidence-backed decision, complete proposed contract if supported, saved-only tests, independent internal review, verified normal origin/test archive then STOP. No M1-M7 activation.'}
    groups={
        'P1':['two quality field meanings','field units','field provenance','published rule reconstructibility','metadata-supported quality judgments','future train-only physiological QC','retrospective sorting selection limits','no undocumented ratio certification','bounded provenance search and explicit fallback','no actual eligible-unit certification'],
        'P2':['all25animal identities','all25session/probe identities','pure-tone event identities','documented[-3,0) windows','interval creator provenance','basic windows separately retained','provider-active windows separately retained','saturation masks','overlap audit','known invalid intervals','manual exclusions','quietdet ignore and ambiguity','clock limitations','recording-support limitations','no basic-as-awake claim','narrower source-supported alternative if creator unresolved','no artificial packet-loss requirement'],
        'P3':['estimandA definition','estimandB definition','rawPL20bound preserved','basic12020bound preserved','active12015bound preserved','120threshold unchanged','8+8mouse minimum unchanged','complete animal upper bounds forA','complete animal upper bounds forB','active-onlycannotmeet16under120','no state-equivalence claim','no score-driven estimand choice','scientific grounds for primary recommendation','metadata-informed decisions disclosed'],
        'P4':['complete proposed contract conditional on support','provider PL anatomy','aversive-task behavioral scope','no passive or choice mechanism','8development+8final minimum','8eligible simultaneous units pendingQC','120valid nonoverlapping3sepochs','mouse-disjoint split before spikes','train-only unitQC','train-only scaling','causal features','epoch resets','strong rate baseline','own-history baseline','population-history baseline','context baseline','drift baseline','two-state exact-forward HMM','low-dimensional fixed-timescale continuous model','matched complexity comparison','mouse effects','uncertainty','multiplicity','conditional nulls','one final animal evaluation','numerical acceptance boundaries','scientific stopping boundaries','no cryptographic custody','no incompatible P11/P12code reuse','no automatic study activation'],
        'P5':['exactlyone supported readiness outcome','readiness not16mice already eligible','exact essential missing evidence ifblocked','shortest draft author/source request ifneeded','no open-ended followup audit'],
        'DELIVERY':['quality provenance report','epoch provenance report','25animal disposition table','basic-active comparison','proposed frozen protocol ifsupported','limitations','claim audit','QC regressions','saved-only PowerShell reproduction','independent internal review','exact scoped commit','origin/test normal push','remote SHA/manifest/hash readback','clean gate','historical IBL failure preserved','priorKI inconclusive preserved','P1-P12 unchanged','no spike value access','no fitting','no M1-M7/final evaluation','stop after decision']}
    req=[]
    for group,items in groups.items():
        for item in items:req.append({'id':f'REQ-{len(req)+1:03}','phase':group,'requirement':item,'status':'OPEN','evidence':None})
    snapshots={P/'REGISTRATION.json':policy,E/'baseline.json':{'utc':now,'revision':1,'count':len(req),'requirements':req},
               E/'mission.json':{'mission':{'id':policy['mission'],'objective':'Resolve bounded000473PL quality/epoch source contract and propose, never activate, P13-v2'},'target':{'workdir':str(ROOT),'files':['paper13_ki_pl_contract1/**',str(E.relative_to(ROOT))+'/**','ops/daily-operations.md']},'metadata':{'base':policy['base'],'user_mission_sha256':hashlib.sha256(user.read_bytes()).hexdigest()}}}
    for path,value in snapshots.items():
        with path.open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(value,indent=2)+'\n')
    with (E/'goldenstandards.md').open('x',encoding='utf8',newline='\n') as f:
        f.write(f'''# PL final provenance resolution

Mission P13-KI-PL-QUALITY-EPOCH-RESOLUTION-1, BASE0eba2fe4a47b0d6392159bfe24a3343a0f7ff1c6. Frozen at {now}, {len(req)} atomic requirements. Original USER_MISSION.txt and baseline.json retained byte-for-byte. Source-of-truth is current user authorization, not old mission scope. Initially clean test=origin/test, fresh fetch; no origin/main (TEST_ONLY_REMOTE_NO_MAIN). Physical foundation/engineer/review/template files absent; user-pasted directive applies.

Decision block: trusted local research analyst needs a defensible PL data contract before neural QC, following known20basic/15active bounds. Approved flow: bounded source investigation, exact25animal metadata/exclusion audit, scientific estimand comparison, complete proposed contract if supported, tests, independent review, actual Git closure, stop. Outcome can be ready-pendingQC, metadata-inconclusive or insufficient; none activates neural access. Keep120epochs/8+8mice unchanged. Open material decisions=0 for this inquiry; future model protocol needs separate authorization.

Verification L0-L2: saved metadata joins/identity/mask/config oracles, explicit quality unknown handling, interval/exposure and partition invariants, reproducible new outputs and independent internal review. No fit or neural arrays. Original source/observations/failed attempts immutable. New exclusion masks may only produce separately labeled refined bounds. No hidden baseline shrink or automatic awake/quality/eligibility PASS.

Use current-session local tools and JSON Mission Spec; no retry/bypass of earlier external model-service CLI rejection. nsi-paper-builder discipline applies to the proposed methods/claims, not a completed manuscript. A separate reviewer is authorized after implementation freezes. Report historical source limitations, not fake reconstruction. Final engineering PASS is distinct from scientific readiness and all Git claims stay pending until actual readback/clean receipt.
''')
    print(json.dumps({'utc':now,'requirements':len(req),'policy_sha256':hashlib.sha256((P/'REGISTRATION.json').read_bytes()).hexdigest()}))


if __name__=='__main__':main()
