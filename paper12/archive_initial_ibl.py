"""Mechanically reconstruct and hash-check the registered pre-review source."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

if __name__=='__main__':
    text = (HERE/'ibl_audit.py').read_text()
    text = text.replace('from pathlib import Path\n','',1)
    text = text.replace("    pairs = {(r['eid'], r['pid']) for r in fixture}\n    if len(pairs) != len(fixture): raise RuntimeError('Duplicate fixture insertion')\n    seen, orphans = set(), Counter()\n",'')
    text = text.replace("        if (r['eid'], r['pid']) not in pairs:\n            orphans['unlisted_probe'] += 1\n            continue\n        key = (r['pid'], str(r['cluster_id']))\n        if key in seen: raise RuntimeError('Duplicate unit identity')\n        seen.add(key)\n",'')
    text = text.replace("identities = {(r['lab'], r['subject']) for r in insertions}","identities = {r['subject'] for r in insertions}")
    text = text.replace("        identity = next(iter(identities))\n",'')
    text = text.replace("'mouse_id': identity[0] + '/' + identity[1]", "'mouse_id': next(iter(identities))")
    text = text.replace("                    'admitted_mice': 0, 'orphan_units': dict(orphans),\n                    'distinct_unit_identities': len(seen),\n                    'fixture_probes_without_anatomy_rows': len({p for _, p in pairs} - {p for p, _ in seen}),\n                    'other_or_unmapped_labels': dict(unknown)}", "                    'admitted_mice': 0, 'other_or_unmapped_labels': dict(unknown)}")
    text = text.replace("'verdict': 'INCONCLUSIVE',", "'verdict': 'DATA_INSUFFICIENT' if summary['potential_paired_mice'] < 16 else 'INCONCLUSIVE',")
    digest = json.loads((HERE/'ibl_registration.json').read_text())['code_sha256']
    candidates = [text.encode(), text.replace('\n','\r\n').encode()]
    exact = next((b for b in candidates if hashlib.sha256(b).hexdigest()==digest),None)
    if exact is None: raise RuntimeError('Cannot reconstruct exact registered source; do not invent archive')
    directory = HERE/'archive'
    directory.mkdir(exist_ok=True)
    (directory/'ibl_audit_initial.py').write_bytes(exact)
    print('Registered initial source preserved exactly:',digest)
