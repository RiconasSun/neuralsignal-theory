"""One necessary native canary; original eight hash verification; no source requests."""
import ctypes
import hashlib
import platform
import sys
import types
import uuid
from pathlib import Path
from datetime import datetime, timezone
import study as r
import verified_atomic as a


def verify_reuse():
    reg = r.verify()
    old = r.ROOT / 'paper12_transport1/implementation_registration.json'
    issuer_path = r.OLD / '.private/transport_recovery1/reuse_issuer.json'
    if r.sha(issuer_path) != r.load(old)['private_reuse_issuer_sha256']:
        raise RuntimeError('ORIGINAL_REUSE_ISSUER_CHANGED')
    issuer = r.load(issuer_path)
    if set(issuer) != set(reg['reuse']) or len(issuer) != 8:
        raise RuntimeError('EIGHT_REUSE_IDENTITIES_CHANGED')
    rows = []
    for sid, value in issuer.items():
        path = r.OLD / 'results/M2/index2/sessions' / (sid + '.json')
        if r.sha(path) != reg['reuse'][sid]['receipt_sha256']:
            raise RuntimeError('ORIGINAL_RECEIPT_CHANGED')
        root = r.OLD / '.private' / value['namespace'] / sid
        for name, digest in value['fingerprints'].items():
            if r.sha(root / name) != digest:
                raise RuntimeError('ORIGINAL_ARTIFACT_CHANGED')
        rows.append(dict(session_id=sid, original_receipt_sha256=r.sha(path),
            artifacts_verified=len(value['fingerprints']), decrypted=False, unchanged=True))
    return rows


def seal():
    r.verify()
    names = sorted(p.name for p in r.HERE.glob('*.py'))
    r.save(r.HERE / 'implementation_registration.json', dict(utc=datetime.now(timezone.utc).isoformat(),
        registration_sha256=r.sha(r.HERE / 'registration.json'),
        sha256={name:r.sha(r.HERE / name) for name in names}, requests_before_seal=0), True)


def guard(require_proof=True):
    reg = r.verify()
    a.require_custodian()
    a.verify_parity()
    seal = r.load(r.HERE / 'implementation_registration.json')
    if seal['registration_sha256'] != r.sha(r.HERE / 'registration.json'):
        raise RuntimeError('REGISTRATION_CHANGED')
    for name, digest in seal['sha256'].items():
        if r.sha(r.HERE / name) != digest:
            raise RuntimeError('IMPLEMENTATION_CHANGED')
    import custodian
    custodian.check_gate()
    if require_proof:
        proof = r.load(r.HERE / 'results/preflight.json')
        isolation = r.load(r.HERE / 'results/isolation.json')
        if proof['passed'] is not True or isolation['mandatory_isolation_pass'] is not True:
            raise RuntimeError('PREFLIGHT_OR_ISOLATION_FAILED')
        if proof['implementation_sha256'] != r.sha(r.HERE / 'implementation_registration.json'):
            raise RuntimeError('PREFLIGHT_STALE')
    return reg


def main():
    if '--seal' in sys.argv:
        seal(); print('IMPLEMENTATION_SEALED_BEFORE_SOURCE_ACCESS'); return
    guard(False)
    reuse = verify_reuse()
    namespace = 'run_' + uuid.uuid4().hex
    root = a.prepare(r.HERE / '.private' / namespace / 'main/trial_0')
    body = b'P12 real-resume prerequisite synthetic canary; no neural values.'
    source = dict(dataset='synthetic', version=1, block=0)
    receipt = a.commit(root, 'block', body, source)
    if a.read(root / 'block.checkpoint', source, hashlib.sha256(body).hexdigest()) != body:
        raise RuntimeError('PREFLIGHT_CHECKPOINT_FAILED')
    again = a.commit(root, 'block', body, source)
    if not again['idempotent']:
        raise RuntimeError('PREFLIGHT_RESUME_FAILED')
    fs = ctypes.create_unicode_buffer(64)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    ok = kernel.GetVolumeInformationW(str(Path(root.anchor)), None, 0, None, None, None, fs, 64)
    if not ok or fs.value != 'NTFS' or root.stat().st_dev != (root / 'staging').stat().st_dev:
        raise RuntimeError('NATIVE_VOLUME_ASSUMPTION_FAILED')
    r.save(r.HERE / 'results/native_canary.json', dict(synthetic_only=True,
        synthetic_run_namespace=namespace, noninjected_commits=[dict(receipt=receipt,payload_bytes=len(body))]), True)
    # Rebind the previously reviewed five-change native harness, not its security logic.
    archived = a.module('resume_isolation_harness', r.ROOT / 'paper12_checkpoint1/isolation.py')
    globals_copy = dict(archived.main.__globals__)
    globals_copy.update(r=r, verify_history=r.verify, protect=a.protect,
                       require_custodian=a.require_custodian, check_path=a.check_path, read=a.read)
    scoped = types.FunctionType(archived.main.__code__, globals_copy)
    prior_args = sys.argv[:]
    try:
        sys.argv = [__file__, '--native', str(r.HERE / 'results/native_canary.json'),
                    '--output', str(r.HERE / 'results/isolation.json'), '--runtime']
        scoped()
    finally:
        sys.argv = prior_args
    proof = r.load(r.HERE / 'results/isolation.json')
    passed = proof.get('mandatory_isolation_pass') is True
    r.save(r.HERE / 'results/preflight.json', dict(passed=passed,
        utc=datetime.now(timezone.utc).isoformat(), filesystem=fs.value,
        platform=platform.platform(), volume=root.anchor, same_volume=True,
        reparse_checks=True, protected_DACL_verified=True, closed_handle_publication=True,
        bytecode_unchanged=a.verify_parity(), original_eight=reuse,
        source_requests=0, neural_values_decoded=False, final_evaluation_exposure=False,
        implementation_sha256=r.sha(r.HERE / 'implementation_registration.json')), True)
    if not passed:
        raise RuntimeError('NATIVE_ACCESS_ISOLATION_FAILED')
    print('CURRENT_ENVIRONMENT_AND_EIGHT_REUSE_PREFLIGHT_PASS; NO SOURCE REQUESTS')


if __name__ == '__main__':
    main()
