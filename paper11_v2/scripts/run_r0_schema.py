"""Append-only R0 schema correction; frozen original auditor remains unchanged."""
import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone

import run_r0 as base

OUT = base.STUDY / "results/R0_schema1"


def register():
    base.verify_registration()
    paths = [base.STUDY / "scripts/run_r0_schema.py", base.STUDY / "tests/test_r0_schema.py",
             base.STUDY / "scripts/reproduce-r0-schema.ps1"]
    value = {"study": "P11-v2", "amendment": "R0-SCHEMA-1", "registered_utc": datetime.now(timezone.utc).isoformat(),
             "original_registration_sha256": base.digest(base.OUT / "registration.json"),
             "original_failure_retained": "results/R0/gate_result.json",
             "reason": "Original parser expected recognition rather than actual recog, and rejected site-qualified sub-TWH identifiers. Metadata-only bugs, not physiological results.",
             "semantic_equivalence": "recog is recognition in the source experiment; sub-TWHxxx is Toronto site-qualified identity. No spike/outcome exposure, threshold or predictive protocol change.",
             "source": "https://www.nature.com/articles/s41597-020-0415-9",
             "phase_mapping": {"recog": "recognition", "recognition": "recognition", "learn": "learning", "learning": "learning"},
             "patient_mapping": "Retain complete site-qualified P-number or TWH-number; strip only explicit repeated-session suffix _integer. Site-qualified IDs never merged across hospitals.",
             "unknown_phase_or_alias": "fail closed, not exclude as an unfavorable result",
             "unchanged_minimum": {"subjects": 8, "hippocampal_units": 5, "recognition_trials": 40},
             "observation_coverage_rule": "Before any physiological access in R2, require explicit unit obs_intervals or independently documented continuous recording support covering every frozen scored bin. Never use first/last spike as support. Unknown support cannot become zero counts; fail DATA_INSUFFICIENT and keep external locked. No final-bin pruning based on spikes or scores.",
             "external_null_detail": "For each unit and trial separately circularly rotate counts by uniformly seeded nonzero integer offset modulo its bin count (1..T-1), retain every trial count and partition. For external T=10 use 5,6,7,8,9 bins, never10 or20 identity; primary T=60 use5..20 bins. Event timing null rotates covariate sequence separately within trial using same admissible shifts, not response/future event attributes. These define the 500-2000ms policy within bounded epochs before any neural outcome access.",
             "exposure_read_correction": "Initial broad text scan already executed; archive outcome access cannot be undone. Audit it explicitly, treat primary development as exposed. Original gate receipts report no final spike/count access. Revised audits use exact provenance paths only; no outcome JSON or prediction summaries decoded. External physiological/final outputs were not present or read.",
             "checksums": {str(p.relative_to(base.ROOT)).replace('\\', '/'): base.digest(p) for p in paths}}
    target = OUT / "registration.json"
    if target.exists():
        verify()
        return
    base.save(target, value, immutable=True)
    print("Registered R0-SCHEMA-1 before corrected metadata audit/testing.")


def verify():
    base.verify_registration()
    reg = json.loads((OUT / "registration.json").read_text())
    if base.digest(base.OUT / "registration.json") != reg["original_registration_sha256"]:
        raise RuntimeError("Original registration changed")
    for rel, sha in reg["checksums"].items():
        if base.digest(base.ROOT / rel) != sha:
            raise RuntimeError(f"Amendment input changed: {rel}")
    return reg


def patient(path):
    sid = path.split('/')[0]
    if not re.fullmatch(r"sub-(?:P\d+(?:HMH|CS)|TWH\d+)(?:_\d+)?", sid):
        raise RuntimeError(f"Unregistered subject alias: {sid}")
    return re.sub(r"_\d+$", "", sid)


def summarize(file, ledger):
    result = base.summarize_metadata(file, ledger)
    starts = base.permitted_read(file, "intervals/trials/start_time", ledger)
    stops = base.permitted_read(file, "intervals/trials/stop_time", ledger)
    phases = base.permitted_read(file, "intervals/trials/stim_phase", ledger)
    valid = []
    previous = -math.inf
    for i, (a, b, phase) in enumerate(zip(starts, stops, phases)):
        a, b = float(a), float(b)
        if not math.isfinite(a) or a <= previous:
            raise RuntimeError("Nonfinite or nonchronological trial onset")
        previous = a
        phase = base.decode(phase).strip().lower()
        if phase not in {"recog", "recognition", "learn", "learning"}:
            raise RuntimeError(f"Unknown trial phase: {phase}")
        if phase in {"recog", "recognition"} and math.isfinite(b) and b > a and (i + 1 == len(starts) or starts[i + 1] >= a + 1):
            valid.append({"row": i, "start": a, "stimulus_stop": b})
    ntrain = math.floor(.6 * len(valid))
    result.update({"valid_recognition_trials": valid, "calibration_train_rows": [t["row"] for t in valid[:ntrain]],
                   "locked_final_rows": [t["row"] for t in valid[ntrain:]],
                   "metadata_candidate": len(result["hippocampal_units"]) >= 5 and len(valid) >= 40,
                   "observation_support_metadata_present": "units/obs_intervals" in file,
                   "observation_support_verified": False})
    return result


def acquire():
    verify()
    import h5py
    import requests
    session = requests.Session()
    roster = json.loads((base.OUT / "metadata/asset_roster.json").read_text())
    for asset in sorted(roster["results"], key=lambda a: a["path"]):
        aid = asset['asset_id']
        target = OUT / "audits" / f"{aid}.json"
        if target.exists():
            print(f"READBACK {asset['path']}", flush=True)
            continue
        source = base.OUT / "metadata/assets" / f"{aid}.json"
        if source.exists():
            info = json.loads(source.read_text())
        else:
            info = base.request_json(session, f"{base.API}/assets/{aid}/")
        base.save(OUT / "assets" / f"{aid}.json", info, immutable=True)
        sha = info.get('digest', {}).get('dandi:sha2-256')
        if not sha or not re.fullmatch('[0-9a-f]{64}', sha):
            raise RuntimeError('Missing published checksum')
        url = next(u for u in info['contentUrl'] if u.startswith('https://dandiarchive.s3.amazonaws.com/blobs/'))
        reader = base.RangeReader(url, asset['size'], session)
        ledger = []
        result = {'asset_id': aid, 'path': asset['path'], 'size': asset['size'], 'published_sha256': sha, 'patient': patient(asset['path'])}
        try:
            with h5py.File(reader, 'r') as file:
                result.update(summarize(file, ledger))
            result['schema_status'] = 'VERIFIED'
        except (RuntimeError, KeyError, ValueError, OSError) as exc:
            result.update({'schema_status': 'FAIL', 'reason': str(exc), 'metadata_candidate': False})
        result.update({'decoded_paths': ledger, 'range_receipts': reader.receipts, 'transport_bytes': reader.fetched,
                       'neural_values_decoded': False, 'whole_asset_checksum_verified': False})
        base.save(target, result, immutable=True)
        print(f"AUDIT {asset['path']} {result['schema_status']} hippocampal_units={len(result.get('hippocampal_units', []))} recognition_trials={len(result.get('valid_recognition_trials', []))}", flush=True)
        if result['schema_status'] != 'VERIFIED':
            break


def evaluate():
    verify()
    rosterpath = base.OUT / 'metadata/asset_roster.json'
    roster = json.loads(rosterpath.read_text())
    audits = [json.loads(p.read_text()) for p in sorted((OUT / 'audits').glob('*.json'))]
    candidate = sorted({a['patient'] for a in audits if a['metadata_candidate']})
    complete = {a['asset_id'] for a in audits} == {a['asset_id'] for a in roster['results']}
    schemas = all(a['schema_status'] == 'VERIFIED' for a in audits)
    pass_gate = complete and schemas and len(candidate) >= 8
    result = {'study': 'P11-v2', 'milestone': 'R0', 'schema_amendment': 'R0-SCHEMA-1',
              'gate_verdict': 'PASS' if pass_gate else 'FAIL', 'assets_expected': len(roster['results']),
              'assets_audited': len(audits), 'complete_roster': complete, 'all_schema_verified': schemas,
              'candidate_subjects': candidate, 'candidate_subject_count': len(candidate),
              'eligible_session_count': sum(a['metadata_candidate'] for a in audits),
              'neural_values_accessed': False, 'v1_failures_unchanged': True,
              'scientific_regime_verdict': 'NOT_EVALUATED', 'external_final_locked': True,
              'metadata_only_not_physiological_QC': True, 'source_cohort_site_independence': True,
              'private_patient_cross_site_identity_certified': False,
              'observation_support_verified': False,
              'r2_support_preflight_mandatory': True,
              'limitation': None if pass_gate else 'Independent candidate anatomy/trial/subject coverage not verified; R1-R3 forbidden.'}
    base.save(OUT / 'gate_result.json', result)
    base.save(OUT / 'QC.json', result)
    if pass_gate:
        base.save(OUT / 'final_validation_lock.json', {'study': 'P11-v2', 'dataset': 'DANDI:000004',
                  'version': base.VERSION, 'roster_sha256': base.digest(rosterpath),
                  'protocol_sha256': base.digest(base.STUDY / 'protocol/protocol.json'),
                  'amendment_sha256': base.digest(OUT / 'registration.json'),
                  'eligible_sessions': [a for a in audits if a['metadata_candidate']],
                  'policy': 'All eligible sessions; development-only hyperparameters, calibration60%/final40% chronologically; final spike access prohibited until R1 and R2 selection freeze.'}, immutable=True)
    print(json.dumps(result, indent=2))
    return 0 if pass_gate else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['register', 'acquire', 'evaluate', 'verify'])
    args = parser.parse_args()
    action = globals()[args.action]
    code = action()
    sys.exit(code if isinstance(code, int) else 0)
