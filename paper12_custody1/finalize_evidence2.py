"""Preserve original seal/replay; add a candidate-bound public seal and receipt."""
import os
import shutil
import sys
from datetime import datetime, timezone
import register as r
from reproduce_saved2 import verify_manifest


def main():
    if '--bind-reproduction' in sys.argv:
        receipt = r.load(r.HERE / 'replay/revision2/reproduction_receipt.json')
        expected = receipt['start_manifest_sha256']
        if receipt['end_manifest_sha256'] != expected or receipt['end_inputs_revalidated'] is not True or receipt['saved_checks_pass'] is not True or receipt['saved_M2_gate'] != 'FAIL':
            raise RuntimeError('FRESH_REPRODUCTION_RECEIPT_INVALID')
        verify_manifest(expected)
        root = r.HERE / 'results/reproduction_logs2'; root.mkdir(exist_ok=True)
        for item in receipt['checks']:
            source = r.HERE / item['log']
            if r.sha(source) != item['sha256']:
                raise RuntimeError('FRESH_REPRODUCTION_LOG_CHANGED')
            shutil.copy2(source, root / source.name)
        verify_manifest(expected)
        r.save(r.HERE / 'results/reproduction_binding2.json',
               dict(receipt=receipt, source_manifest_sha256=expected,
                    candidate_verified_at_binding=True, experiments_reproduced=False), True)
        print('START_END_AND_BINDING_CANDIDATE_IDENTITY_VERIFIED;M2_STILL_FAIL')
        return
    r.verify()
    initial = r.HERE / 'results/reproduction_initial1'; initial.mkdir(exist_ok=True)
    old_receipt = r.load(r.HERE / 'replay/reproduction_receipt.json')
    r.save(initial / 'receipt.json', old_receipt, True)
    for item in old_receipt['checks']:
        source = r.HERE / item['log']
        if r.sha(source) != item['sha256']:
            raise RuntimeError('ORIGINAL_REPLAY_LOG_CHANGED')
        shutil.copy2(source, initial / source.name)
    excluded = {'.private', 'exports', 'replay', '__pycache__', 'reproduction_logs', 'reproduction_logs2'}
    hashes = {}
    for root, dirs, files in os.walk(r.HERE):
        dirs[:] = [d for d in dirs if d not in excluded]
        for name in files:
            if name.endswith('.pyc') or name in ('final_source_manifest2.json', 'reproduction_binding.json', 'reproduction_binding2.json'):
                continue
            path = r.HERE.__class__(root) / name
            hashes[path.relative_to(r.HERE).as_posix()] = r.sha(path)
    r.save(r.HERE / 'final_source_manifest2.json', dict(utc=datetime.now(timezone.utc).isoformat(), sha256=hashes,
           scope='Append-only candidate-bound saved-evidence repair;original seal/receipt retained'), True)
    verify_manifest()
    print('REPLAY_FRESHNESS_REPAIR_SEALED;ORIGINAL_RECORDS_PRESERVED')


if __name__ == '__main__':
    main()
