"""Prospective registration; exclusive writes prevent retrospective replacement."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'paper13'
E = ROOT / 'ops/evidence/2026-10-15/p13-pfc-local-predictive-dynamics'


def main():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    source = E / 'USER_MISSION.txt'
    # Keep each user bullet as its own requirement; preserve full source verbatim.
    lines = source.read_text(encoding='utf-8-sig').splitlines()
    stage, requirements = 'GLOBAL', []
    for line in lines:
        if line.startswith('## M'):
            stage = line.split()[1]
        if line.startswith('- ') or (line[:1].isdigit() and '. ' in line[:5]):
            requirements.append({'id': f'REQ-{len(requirements)+1:03}',
                                 'stage': stage, 'requirement': line,
                                 'status': 'OPEN', 'evidence': None})
    # Prose requirements are explicit independent items, not lost between bullets.
    for stage, item in [
        ('M0', 'Single probe >=20 provider-good units and >=400 usable trials; >=8 independent mice/group; target12'),
        ('M0', 'Pin release, full identity denominator, timing, masks and covariate availability before admission'),
        ('M0', 'Stop on IBL insufficiency without unbounded alternative search'),
        ('M1', 'Freeze all eligibility splits hypotheses models scores tests nulls and numerical criteria before scores'),
        ('M2', 'Training-only QC and scaling; no current/future spikes or unavailable behavioral outcomes in predictors'),
        ('M3', 'B0 stationary; B1 task/time/order; B2 own history; B3 population history; mandatory B4 combined nuisance GLMs'),
        ('M4', 'Discrete exact log-space forward HMM and continuous low-dimensional fixed-timescale causal history readout'),
        ('M4', 'Score before assimilating current counts; include nuisance structure; retain all invalid fits'),
        ('M5', 'Three comparisons to strongest baseline and each other; equal mouse paired inference and lab/session heterogeneity'),
        ('M6', 'Freeze development selection then one final assessment; calibration-only transfer; no retuning or equivalence claim'),
        ('M7', 'Complete manuscript and supplement PDFs only if scientific route valid; honest narrower report on failed gates'),
        ('GLOBAL', 'Preserve all P1-P12 bytes; no crypto custody architecture; no silent shrink'),
        ('GLOBAL', 'Fresh tests, separate review, exact-file normal origin/test push, remote readback and clean gate'),
    ]:
        requirements.append({'id': f'REQ-{len(requirements)+1:03}', 'stage': stage,
                             'requirement': item, 'status': 'OPEN', 'evidence': None})
    policy = {
        'mission': 'P13-PFC-LOCAL-PREDICTIVE-DYNAMICS', 'registered_utc': now,
        'base': '88a5873972b43f2f0ff5b28400f6a9cbb941add7',
        'paper_type': 'Method Paper', 'stage': 'M0_METADATA_ONLY',
        'region_priority': ['ACAd', 'ORBvl', 'PL'],
        'anatomy': 'Provider Allen exact acronym or laminar descendants only; no pooling distinct areas',
        'minimum_good_units_single_probe': 20, 'minimum_usable_trials': 400,
        'good_units': 'Provider label==1 is metadata feasibility only, not training-only physiological QC admission',
        'minimum_mice_per_group': 8, 'target_mice_per_group': 12,
        'sample_justification': '8 is feasibility floor, not efficacy power assurance. With 8 final mice, minimum two-sided exact signflip p=2/256=.0078125, Holm3 minimum=.0234375. Target12 improves precision. No prospective power claim.',
        'selection': 'Audit all3. Choose first priority area with >=16 independent mice meeting all verified metadata gates. Unknown essential metadata does not pass. Target>=24. No relaxation.',
        'one_session_per_mouse': 'Largest same-probe provider-good population, then most usable trials, then lexicographic eid/pid; before neural outcomes',
        'allocation': 'M1 will freeze deterministic lab-stratified identity-hash allocation of all eligible mice into near-equal halves; no outcome replacement',
        'source_pin': 'Brainwidemap provider tag plus frozen Git commit/fixture/aggregate header and downloaded-column SHA256; exact identity compatibility required',
        'allowed': ['identities', 'atlas', 'provider quality label', 'trial event timestamps/masks', 'covariate availability/timestamps', 'curated observation and saturation metadata'],
        'forbidden_M0': ['spike times', 'count arrays', 'predictive scores', 'fits', 'P1-P12 mutation'],
        'bounds': {'datasets': 1, 'regions': 3, 'probe_records': 800, 'sessions': 600,
                   'http_requests': 1800, 'transport_bytes': 250000000, 'attempts_per_request': 2},
        'support': 'Curated active-task intervals, finite ordered event times and documented ephys clock, invalid/saturation masks where supplied. No absolute lossless hardware-packet assertion.',
        'stop': 'Insufficiency/leakage/essential incompatibility -> scientific STOP, no M1. Network failures are environment blockers, not scientific insufficiency.',
        'downstream': 'All M1-M7 conditional requirements retained; exact scientific protocol before relevant score access, not yet executed.'}
    outputs = {
        P / 'M0_REGISTRATION.json': policy,
        E / 'requirement_baseline.json': {'frozen_utc': now, 'revision': 1,
                                         'count': len(requirements), 'requirements': requirements},
        E / 'mission.json': {'mission': {'id': policy['mission'], 'objective': 'Execute registered M0-M7 scientific gates; begin bounded metadata feasibility'},
                            'target': {'workdir': str(ROOT), 'files': ['paper13/**', str(E.relative_to(ROOT))+'/**', 'ops/daily-operations.md']},
                            'metadata': {'base': policy['base'], 'user_mission_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}}
    }
    for path, obj in outputs.items():
        with path.open('x', encoding='utf8') as f:
            f.write(json.dumps(obj, indent=2)+'\n')
    text = f'''# P13-PFC-LOCAL-PREDICTIVE-DYNAMICS

Frozen revision1 at {now}; {len(requirements)} individually traceable requirements in requirement_baseline.json, full verbatim USER_MISSION.txt. Current mode ENGINEER_MODE, M0 only. No previous paper bytes may change. Original prior failures remain immutable.

## Decision block
Actor: trusted local researcher. Problem: determine whether tractable local PFC dynamics add prediction beyond strong causal nuisance/history baselines. Outcome: valid positive/negative/inconclusive study. Flow: metadata admission -> scientific freeze -> causal features/baselines/dynamics -> development selection -> one final assessment -> manuscript. Preserve identities, partitions and failures. No-goals: custom security architecture, regional pooling, physical neural atoms or journal claims. Open material decisions=0 for M0; downstream scientific choices freeze before relevant access.

## Verification and preservation
Level L0-L2 scientific backend: synthetic admission/identity/denominator/causality oracles, real bounded metadata transport and saved-only reproduction. Unknown coverage cannot pass; no pseudoreplicated mice, region pooling, or score access. Requirement matrix remains OPEN until independently evidenced. Downstream conditional stages never silently dropped.

Branch preflight: fresh fetch succeeded, HEAD=origin/test={policy['base']}, working tree clean. origin/main absent: TEST_ONLY_REMOTE_NO_MAIN; no invented base or reset/merge.

Tool route: JSON Mission Spec. Prior P12 automatic approval review rejected external model-service CLI retry; no retry or bypass. Use current-session local tools. No external-model delegation.

Pass needs complete baseline, fresh evidence/review, bugs0/warnings0, no shrink and actual normal Git closure. Scientific stop remains distinct from engineering archival completion. No neural values loaded in M0.
'''
    with (E/'goldenstandards.md').open('x',encoding='utf8') as f:
        f.write(text)
    print(json.dumps({'registered_utc': now, 'requirements': len(requirements),
                      'policy_sha256': hashlib.sha256((P/'M0_REGISTRATION.json').read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
