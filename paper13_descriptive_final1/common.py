"""Prospective descriptive prerequisites; historical evidence stays read-only."""
import json
from pathlib import Path
import numpy as np
from paper13_ki_execution1.source import ROOT, ALLOCATION, CONFIG, sha
from paper13_ki_execution1 import baseline_A as b
from paper13_ki_execution1.fit_engine import ScientificStop

P = Path(__file__).resolve().parent
OLD = ROOT / 'paper13_ki_execution1'
E = ROOT / 'ops/evidence/2026-10-16/p13-descriptive-final-closeout-1'
FINAL_MICE = ['128514','128516','152414','225757','225758','225759','258414','268947','273855']


def identities():
    for path in [P/'INPUT_FREEZE.json', OLD/'M6_E_IMPLEMENTATION_FREEZE_r2.json', ROOT/'paper13_ki_pl_contract1/FREEZE_r2.json']:
        for name, digest in b.read(path)['hashes'].items():
            if sha((ROOT/name).read_bytes()) != digest:
                raise ScientificStop('Frozen historical identity changed: '+name)
    return sha((P/'INPUT_FREEZE.json').read_bytes())


def amendment():
    a = b.read(P/'PRE_D_STOPPING_RULE_AMENDMENT.json')
    if a['mission']!='P13-DESCRIPTIVE-FINAL-CLOSEOUT-1' or a['final_D_outcome_access_before_amendment']:
        raise ScientificStop('Prospective pre-D owner amendment required')
    if a['known_failed_gate']['immutable_associated_claim_verdict']!='INCONCLUSIVE' or a['new_exception']['conditional_Bstar_null']!='FAILED_UNAVAILABLE':
        raise ScientificStop('Known failures/claim locks must remain immutable')
    if sha((E/'OWNER_MISSION.txt').read_bytes()) != a['owner_mission_sha256']:
        raise ScientificStop('Owner authorization changed')
    return a


def retained_E_gate():
    identities(); amendment()
    failed=b.read(OLD/'results/M6_E_CONTROLS_GATE.json')
    if failed['M6_E_CONTROLS']!='FAIL' or failed['attempt']!={'suite':'conditional_Bstar','replicate':0,'mouse_id':'156130'}:
        raise ScientificStop('Original failed null identity changed')
    diagnosis=b.read(ROOT/'paper13_bstar_diag1/results/SAVED_AUDIT.json')
    if diagnosis['diagnosis']!='DOCUMENTED_GENERATOR_INSTABILITY' or diagnosis['original_M6']!='FAIL_UNAVAILABLE':
        raise ScientificStop('Frozen generator diagnosis required')
    journal=[json.loads(line) for line in (OLD/'results/m6_controls_E/actions.jsonl').read_text(encoding='utf8').splitlines()]
    artifacts={}
    for suite in ['temporal','history','task_order']:
        path=OLD/'results/m6_controls_E'/(suite+'.npy')
        markers=[r for r in journal if r['event']=='SUITE_COMPLETE' and r['suite']==suite]
        if len(markers)!=1 or markers[0]['completed_replicates']!=999 or markers[0]['artifact_sha256']!=sha(path.read_bytes()):
            raise ScientificStop('Retained E suite incomplete/hash mismatch')
        array=np.load(path,allow_pickle=False,mmap_mode='r')
        if array.shape!=(999,10,9) or not np.isfinite(array).all():raise ScientificStop('Original complete E denominator/finite failure')
        artifacts[suite]={'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path.read_bytes())}
    return {'RETAINED_E_CONTROLS':'PASS','scope':'Three original completed E suites; not original M6 PASS',
        'conditional_Bstar':'FAILED_UNAVAILABLE','original_M6':'FAIL_RETAINED','artifacts':artifacts,
        'strict_recent_event_coverage':'FAIL6of9vs8_RETAINED','affected_broad_claims':'INCONCLUSIVE'}


def policies():
    retained_E_gate()
    m2=b.read(OLD/'results/M2_GATE.json');m3=b.read(OLD/'results/M3_BASELINE_SELECTION.json');m4=b.read(OLD/'results/M4_MODEL_SELECTION.json')
    if m2['M2']!='PASS' or m3['M3']!='PASS' or m4['M4']!='PASS':raise ScientificStop('Original physiology/development gates required')
    if sorted(m2['eligible_final'])!=FINAL_MICE or sorted(r['mouse_id'] for r in ALLOCATION if r['role']=='final')!=FINAL_MICE:
        raise ScientificStop('Original nine final identities required')
    coverage=b.read(OLD/'results/M6_SENSITIVITY_METADATA_AUDIT.json')
    if coverage['final_contributors'].get('recent_event')!=6 or coverage['required_final_contributors']!=8:
        raise ScientificStop('Original failed coverage identity changed')
    if any(count<8 for name,count in coverage['final_contributors'].items() if name!='recent_event'):
        raise ScientificStop('Another mandatory sensitivity coverage gate failed')
    return m2,m3,m4
