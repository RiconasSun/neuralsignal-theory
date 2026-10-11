"""Append-only full-package hash lock; earlier evidence locks never rewritten."""
from register import HERE, OUT, ROOT, save, sha, verify

verify()
excluded = {'complete_package_lock.json', 'complete_reproduction.log', 'complete_reproduction_receipt.json'}
files = [p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in excluded]
save(OUT / 'complete_package_lock.json', {p.relative_to(ROOT).as_posix(): sha(p) for p in files})
print('Complete package sealed, preserving original artifact lock.')
