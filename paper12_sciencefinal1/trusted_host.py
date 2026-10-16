"""Trusted-local-host adapter. Original scientific evaluator and C validator are reused.

This is accidental-rerun protection, not independent custody or administrator security.
Synthetic rehearsal uses genuine sealed C coefficients and artificial D counts; C
provenance remains unchanged. Actual D lineage is recorded separately from the old
evaluator's return flag, which infers D provenance solely from the C manifest.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback

import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from paper12_singleowner1.common import canonical, digest, new, read_json, safe, sha
from paper12_singleowner1.common import validate_state_manifest
from paper12_singleowner1.custodian_producer import validate_catalog
from paper12_singleowner1.real_metadata import materialize
from paper12_singleowner1.scientific_evaluator import evaluate, summarize_nulls, verdict
from paper12_singleowner1.frozen_math import load

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'paper12_sciencefinal1'
E = ROOT / 'ops/evidence/2026-10-15/p12-science-first-final-closeout-1'
C_ROOT = ROOT / 'paper12_cseal1/.private/sealed_C_recovery_1'
OLD = ROOT / 'ops/evidence/2026-10-14/p12-c-seal-host-import-repair-1'
BASE = '8d1d77615f50d79e158787544b4993daefe16ca3'
MISSION = 'P12-SCIENCE-FIRST-FINAL-CLOSEOUT-1'


def utc():
    return datetime.now(timezone.utc).isoformat()


def verify_sources():
    reg = read_json(E / 'registration.json')
    for n, h in reg['source_sha256'].items():
        if sha(ROOT / n) != h:
            raise PermissionError('REGISTERED_SOURCE_HASH:' + n)
    freeze = read_json(E / 'adapter_source_freeze.json')
    for n, h in freeze['sha256'].items():
        if sha(ROOT / n) != h:
            raise PermissionError('ADAPTER_SOURCE_HASH:' + n)
    if subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() != BASE:
        raise PermissionError('EXACT_BASE_REQUIRED_BEFORE_EVALUATION')
    return {'original_sources': reg['source_sha256'], 'adapter_sources': freeze['sha256']}


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(Path(root).rglob('*')) if p.is_file()}


def check_C():
    expected = read_json(OLD / 'complete_seal_inventory.json')['sha256']
    actual = inventory(C_ROOT)
    if actual != expected or len(actual) != 1862:
        raise PermissionError('EXACT_COMPLETE_C_SEAL')
    m = read_json(C_ROOT / 'C_state_manifest.json')
    validate_state_manifest(m, C_ROOT)
    if m['synthetic'] is not False or len(m['cases']) != 290:
        raise PermissionError('ORIGINAL_REAL_C_CASES')
    return m, digest(canonical(actual))


def exposure_audit():
    paths = [ROOT / 'paper12_resume1/results/M2/gate_result.json']
    paths += [ROOT / p for p in (
        'ops/evidence/2026-10-14/p12-c-seal-host-import-repair-1/HANDOFF.md',
        'ops/evidence/2026-10-15/p12-real-d-single-approver-amend-1/HANDOFF.json')]
    gate = read_json(paths[0])
    if any(gate[k] is not False for k in ('final_evaluation_exposure', 'final_holdout_evaluated', 'final_values_exposed_to_analysis')):
        raise PermissionError('PRIOR_D_EXPOSURE')
    previous = read_json(paths[-1])
    if previous['flags']['D_EVALUATION_EXECUTED'] or previous['flags']['D_RELEASE_CONSUMED']:
        raise PermissionError('PRIOR_FINAL_ASSESSMENT')
    return {'evidence_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in paths},
            'prior_model_selection_D_outcome_exposure_evidenced': False,
            'qualification': 'Existing recorded access evidence, not proof against unlogged administrator activity. Original trusted custody decoded whole-session vectors and sealed D; this is distinct from analysis-role outcome exposure.'}


def preflight(output):
    sources = verify_sources()
    m, c_hash = check_C()
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    materialize(output / 'metadata')
    metadata = output / 'metadata'
    mm, partition, catalog = validate_catalog(metadata, {'realm': 'REAL_D'})
    frozen = read_json(metadata / 'final_D_partition_manifest.json')
    if frozen['cohort'] != m['cohort'] or frozen['D_trial_ids'] != partition['D_trial_ids']:
        raise PermissionError('FROZEN_D_PARTITION_MISMATCH')
    if frozen['animals_sha256'] != sha(metadata / 'animals.json') or frozen['trials_sha256'] != sha(metadata / 'trials.json'):
        raise PermissionError('FROZEN_D_METADATA_HASH')
    if mm != m or len(catalog['sessions']) != 13:
        raise PermissionError('C_METADATA_BINDING')
    receipt = {'mission': MISSION, 'gate': 'PASS', 'utc': utc(), 'base': BASE,
               'sources': sources, 'C_inventory_sha256': c_hash,
               'metadata_sha256': inventory(metadata), 'cohort': m['cohort'],
               'cases': len(m['cases']), 'coverage': m['coverage'],
               'D_trials': sum(map(len, partition['D_trial_ids'].values())),
               'access_audit': exposure_audit(), 'raw_C_D_reads': 0, 'D_key_cipher_reads': 0,
               'new_fits': 0, 'free_disk_bytes': shutil.disk_usage(ROOT).free}
    if receipt['free_disk_bytes'] < 10 * 1024 ** 3:
        raise RuntimeError('INSUFFICIENT_DISK')
    new(output / 'preflight_receipt.json', receipt)
    return receipt


def verify_preflight(path):
    path = Path(path).resolve(); r = read_json(path / 'preflight_receipt.json')
    if r['gate'] != 'PASS' or r['base'] != BASE or r['sources'] != verify_sources():
        raise PermissionError('PREFLIGHT_REQUIRED')
    _, actual = check_C()
    if r['C_inventory_sha256'] != actual or inventory(path / 'metadata') != r['metadata_sha256']:
        raise PermissionError('PREFLIGHT_INPUT_CHANGED')
    exposure_audit()
    return r


def reserve(path, record):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    new(path, record)  # exclusive create + flush/fsync, never reset or delete


def decode_selected(envelope, key, item, cases, part):
    if digest(envelope) != item['ciphertext_sha256'] or envelope[:8] != b'P12GCM1\0' or len(envelope) < 36:
        raise PermissionError('D_ENVELOPE_INTEGRITY')
    if len(key) != 32:
        raise PermissionError('D_KEY_LENGTH')
    raw = AESGCM(key).decrypt(envelope[8:20], envelope[20:], canonical(item['context']))
    shape = item['context']['shape']
    if len(raw) != int(np.prod(shape)) * 4 or shape[:2] != [len(part['trial_ids']), 20]:
        raise PermissionError('D_PAYLOAD_LENGTH')
    tensor = np.frombuffer(raw, dtype='<u4').reshape(shape)
    fields = {}
    for region in ('CA1', 'DG'):
        case = next(c for c in cases if c['region'] == region and c['view'] == 'primary')
        ids = case['unit_ids']; indices = [item['source_unit_ids'].index(u) for u in ids]
        fields[region + '_D'] = tensor[:, :, indices].copy()
        fields[region + '_unit_ids'] = np.array(ids)
    fields.update(trial_ids_D=np.array(part['trial_ids']), conditions_D=np.array(part['conditions']), orders_D=np.array(part['orders']))
    return fields


def source_files(root, item, mode, run):
    root = Path(root).resolve()
    if mode == 'SYNTHETIC' and not root.is_relative_to((Path(run) / 'private/synthetic_sources').resolve()):
        raise PermissionError('SYNTHETIC_SOURCE_BOUNDARY')
    if mode not in ('REAL', 'SYNTHETIC'):
        raise PermissionError('EXPLICIT_MODE_REQUIRED')
    return safe(root, root / item['cipher_file']), safe(root, root / item['key_file'])


def synthetic_sources(binding, run, m, p, catalog):
    """Artificial counts at exact original metadata shape; no real source reads."""
    rng = np.random.default_rng(20261015)
    synroot = Path(run) / 'private/synthetic_sources'; synroot.mkdir()
    roots = {'sessions': {}}
    catalog = json.loads(json.dumps(catalog))
    for mouse in m['cohort']:
        item = catalog['sessions'][mouse]; root = synroot / item['session_id']; root.mkdir()
        original_units = item['source_unit_ids']; selected = set()
        for c in m['cases']:
            if c['mouse_id'] == mouse and c['view'] == 'primary':
                selected.update(c['unit_ids'])
        shape = item['context']['shape']
        counts = np.full(shape, 777, dtype='<u4')
        indices = [i for i, u in enumerate(original_units) if u in selected]
        counts[:, :, indices] = rng.poisson(.25, size=(shape[0], 20, len(indices))).astype('<u4')
        key = rng.bytes(32); nonce = rng.bytes(12)
        envelope = b'P12GCM1\0' + nonce + AESGCM(key).encrypt(nonce, counts.tobytes(), canonical(item['context']))
        # Files are synthetic, but have the original declared compartment/name/schema.
        cp = synroot / item['cipher_file']; kp = synroot / item['key_file']
        if cp.parent != root or kp.parent != root:
            raise PermissionError('SYNTHETIC_SESSION_LAYOUT')
        with cp.open('xb') as f: f.write(envelope)
        with kp.open('xb') as f: f.write(key)
        item['ciphertext_sha256'] = digest(envelope)
        roots['sessions'][mouse] = {'root': str(synroot)}
    return catalog, roots


def verify_run(run, mode):
    run = Path(run).resolve(); receipt = read_json(run / 'run_receipt.json')
    if receipt['mode'] != mode or receipt['gate'] != 'PASS' or receipt['sources'] != verify_sources():
        raise PermissionError('COMPLETE_EXACT_RUN_REQUIRED')
    if receipt['gate_counts'] != {'mice': 13, 'cases': 290, 'null_cases': 104, 'null_evaluations': 103896}:
        raise PermissionError('COMPLETE_SCHEMA_COUNTS')
    for name, h in receipt['result_sha256'].items():
        if sha(safe(run / 'results', run / 'results' / name)) != h:
            raise PermissionError('RESULT_CHANGED')
    return receipt


def run(mode, preflight_path, output, synthetic=None):
    pre = verify_preflight(preflight_path)
    if mode == 'REAL':
        if synthetic is None:
            raise PermissionError('FULL_SYNTHETIC_GATE_REQUIRED')
        verify_run(synthetic, 'SYNTHETIC')
        review = read_json(E / 'pre_D_review.json')
        if review['decision'] != 'APPROVE_FROZEN_SCIENTIFIC_EXECUTION' or review['adapter_freeze_sha256'] != sha(E / 'adapter_source_freeze.json') or review['synthetic_receipt_sha256'] != sha(Path(synthetic) / 'run_receipt.json'):
            raise PermissionError('CURRENT_SCIENTIFIC_REVIEW_REQUIRED')
        reserve(HERE / 'private/REAL_D_RESERVED.json', {'mission': MISSION, 'utc': utc(), 'mode': mode,
                'preflight_sha256': sha(Path(preflight_path) / 'preflight_receipt.json'),
                'synthetic_receipt_sha256': sha(Path(synthetic) / 'run_receipt.json'), 'sources': verify_sources(),
                'owner_authorization_sha256': sha(E / 'human_authorization.txt'), 'pid': os.getpid(),
                'retry': 'FORBIDDEN; preserve partial run on failure'})
    elif mode != 'SYNTHETIC':
        raise PermissionError('EXPLICIT_MODE_REQUIRED')
    output = Path(output).resolve()
    if not output.is_relative_to(HERE / 'work'):
        raise PermissionError('REGISTERED_WORK_NAMESPACE')
    output.mkdir(parents=True, exist_ok=False)
    private = output / 'private'; private.mkdir()
    binding = private / 'binding'; shutil.copytree(C_ROOT, binding)
    for src in (Path(preflight_path) / 'metadata').iterdir():
        if src.name == 'C_state_manifest.json':
            if sha(binding / src.name) != sha(src): raise PermissionError('C_MANIFEST_COPY')
        else: shutil.copyfile(src, binding / src.name)
    m, p, catalog = validate_catalog(binding, {'realm': 'REAL_D'})
    roots = read_json(binding / 'source_roots.json')
    if mode == 'SYNTHETIC':
        catalog, roots = synthetic_sources(binding, output, m, p, catalog)
    # The frozen evaluator checks identical identity tuples without requiring a
    # signature. REAL/SYN source provenance is explicit in this adapter's receipt.
    expected = {'realm': 'REAL_D' if mode == 'REAL' else 'SYNTHETIC_D',
                'authorization_id': MISSION + '_' + mode, 'binding': sha(E / 'registration.json'),
                'principal': {'trusted_local_host_pid': os.getpid()},
                'C_manifest_sha256': digest(canonical(m)), 'partition_sha256': sha(binding / 'partition_manifest.json'),
                'code_sha256': sha(E / 'adapter_source_freeze.json')}
    delivery = private / 'delivery'; delivery.mkdir(); sessions = {}
    for mouse in m['cohort']:
        item = catalog['sessions'][mouse]; part = p['sessions'][mouse]
        cp, kp = source_files(roots['sessions'][mouse]['root'], item, mode, output)
        if mode == 'REAL':
            original = read_json(binding / 'source_roots.json')['sessions'][mouse]['root']
            if cp != safe(original, Path(original) / item['cipher_file']) or kp != safe(original, Path(original) / item['key_file']):
                raise PermissionError('EXACT_ORIGINAL_REAL_SOURCE')
        fields = decode_selected(cp.read_bytes(), kp.read_bytes(), item, [c for c in m['cases'] if c['mouse_id'] == mouse], part)
        if mode == 'SYNTHETIC' and any(np.any(fields[r + '_D'] == 777) for r in ('CA1', 'DG')):
            raise PermissionError('UNSELECTED_CANARY_LEAK')
        name = item['session_id'] + '.npz'
        with (delivery / name).open('xb') as f:
            np.savez(f, **fields); f.flush(); os.fsync(f.fileno())
        sessions[mouse] = {'file': name, 'sha256': sha(delivery / name)}
    new(delivery / 'delivery_manifest.json', dict(expected, complete=True, cohort=m['cohort'], sessions=sessions))
    results = output / 'results'; results.mkdir()
    raw_gate = evaluate(binding, delivery, results, expected, wall_limit=43200)
    if raw_gate['gate'] != 'PASS' or raw_gate['mice'] != 13 or raw_gate['scored_cases'] != 290 or raw_gate['null_evaluations'] != 103896 or raw_gate['new_fits'] != 0:
        raise PermissionError('FULL_SCIENTIFIC_EXECUTION_GATE')
    final = read_json(results / 'final_statistics.json')
    # Preserve raw evaluator output unchanged. The accompanying receipt is the
    # authoritative actual-input lineage for the synthetic preflight.
    receipt = {'mission': MISSION, 'utc': utc(), 'gate': 'PASS', 'mode': mode,
               'sources': verify_sources(), 'preflight_sha256': sha(Path(preflight_path) / 'preflight_receipt.json'),
               'actual_D_input': 'FROZEN_ORIGINAL_D' if mode == 'REAL' else 'DETERMINISTIC_SYNTHETIC_D_WITH_REAL_SEALED_C',
               'SCIENTIFIC_EVALUATION_EXECUTED': mode == 'REAL', 'raw_evaluator_gate': raw_gate,
               'synthetic_flag_caveat': 'Raw evaluator flag follows C manifest, which is genuine real C in both modes; actual input lineage/mode determine real D exposure.',
               'gate_counts': {'mice': 13, 'cases': 290, 'null_cases': 104, 'null_evaluations': 103896},
               'new_fits': 0, 'C_unchanged': check_C()[1] == pre['C_inventory_sha256'],
               'result_sha256': inventory(results), 'verdicts': final['verdicts']}
    if not receipt['C_unchanged']: raise PermissionError('C_SEAL_MODIFIED')
    new(output / 'run_receipt.json', receipt)
    return receipt


def reproduce(run_path):
    run_path = Path(run_path).resolve(); r = read_json(run_path / 'run_receipt.json')
    # After archival commit, source hashes remain verifiable without the old HEAD.
    for group in r['sources'].values():
        for n, h in group.items():
            if sha(ROOT / n) != h: raise PermissionError('REPRODUCTION_SOURCE_HASH')
    results = run_path / 'results'
    if inventory(results) != r['result_sha256']: raise PermissionError('SAVED_RESULT_INVENTORY')
    math = load(); rows = read_json(results / 'scientific_scores.json')['rows']
    stats = math['mouse_statistics'].aggregate(rows)
    stats['primary']['status'] = 'HELD_OUT_REGISTERED_PRIMARY'
    nulls = summarize_nulls({'cohort': read_json(results / 'final_statistics.json')['cohort']}, results, math['mouse_statistics'].holm)
    saved = read_json(results / 'final_statistics.json')
    if canonical(stats) != canonical(saved['mouse_statistics']) or canonical(nulls) != canonical(saved['null_statistics']) or verdict(stats, nulls, True) != saved['verdicts']:
        raise PermissionError('SAVED_STATISTICAL_REPRODUCTION')
    return {'gate': 'PASS', 'saved_only': True, 'raw_neural_reads': 0, 'new_fits': 0, 'mice': 13,
            'null_cases': 104, 'verified_outputs': len(r['result_sha256']), 'original_mode': r['mode']}


def main():
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('preflight'); p.add_argument('--output', required=True)
    for mode in ('synthetic', 'real'):
        p = sub.add_parser(mode); p.add_argument('--preflight', required=True); p.add_argument('--output', required=True)
        if mode == 'real': p.add_argument('--synthetic', required=True)
    p = sub.add_parser('reproduce'); p.add_argument('--run', required=True)
    a = parser.parse_args()
    try:
        if a.command == 'preflight': result = preflight(a.output)
        elif a.command == 'reproduce': result = reproduce(a.run)
        else: result = run(a.command.upper(), a.preflight, a.output, getattr(a, 'synthetic', None))
        print(json.dumps(result, sort_keys=True, allow_nan=False))
    except Exception:
        # No retry or partial-outcome inspection; preserve traceback and reservation.
        traceback.print_exc(); sys.exit(2)


if __name__ == '__main__':
    main()
