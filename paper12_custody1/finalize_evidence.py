"""Seal public stopped evidence and bind actual saved-only reproduction output."""
import os
import shutil
from datetime import datetime, timezone
import sys
import register as r


def main():
    if '--bind-reproduction' in sys.argv:
        receipt = r.load(r.HERE / 'replay/reproduction_receipt.json')
        if receipt['saved_checks_pass'] is not True or receipt['saved_M2_gate'] != 'FAIL' or receipt['saved_manifest_verified'] is not True:
            raise RuntimeError('FINAL_SAVED_REPRODUCTION_NOT_VERIFIED')
        target = r.HERE / 'results/reproduction_logs'
        target.mkdir(exist_ok=True)
        for item in receipt['checks']:
            source = r.HERE / item['log']
            if r.sha(source) != item['sha256']:
                raise RuntimeError('REPRODUCTION_LOG_CHANGED')
            shutil.copy2(source, target / source.name)
        r.save(r.HERE / 'results/reproduction_binding.json',
               dict(receipt=receipt, source_manifest_sha256=r.sha(r.HERE / 'final_source_manifest.json'),
                    scope='Saved hashes/tests/public QC only;no live source/security/experiments rerun'), True)
        print('ACTUAL_POWERSHELL_SAVED_REPRODUCTION_BOUND;M2_REMAINS_FAIL')
        return
    r.verify()
    excluded = {'.private', 'exports', 'replay', '__pycache__', 'reproduction_logs'}
    names = {}
    for root, dirs, files in os.walk(r.HERE):
        dirs[:] = [d for d in dirs if d not in excluded]
        for name in files:
            if name.endswith('.pyc') or name in ('final_source_manifest.json', 'reproduction_binding.json'):
                continue
            path = r.HERE.__class__(root) / name
            names[path.relative_to(r.HERE).as_posix()] = r.sha(path)
    r.save(r.HERE / 'final_source_manifest.json', dict(utc=datetime.now(timezone.utc).isoformat(), sha256=names,
            scope='Public mission implementation/registrations/receipts/stopped reports only',
            excluded='All private values/keys,permitted exports/runtime,transient replay and bound reproduction outputs'), True)
    print('PUBLIC_STOPPED_EVIDENCE_SEALED')


if __name__ == '__main__':
    main()
