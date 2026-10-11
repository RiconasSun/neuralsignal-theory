"""Document-only prospective registration and author-source acquisition."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'results'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)


def register():
    if (OUT / 'protocol_registration.json').exists():
        verify(); return
    files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    hashes = {p: sha(ROOT / p) for p in files if p and p != 'ops/daily-operations.md'}
    ops = (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8')
    policy = load(HERE / 'protocol.json')
    gate = ROOT / 'paper11_v2/results/R2/gate_result.json'
    split = ROOT / 'paper11_v2/results/R0_schema1/final_validation_lock.json'
    assert sha(gate) == policy['original_R2_gate_sha256'] and load(gate)['gate_verdict'] == 'FAIL'
    assert sha(split) == policy['split_sha256']
    save(OUT / 'protocol_registration.json', {
        'mission': policy['mission'], 'registered_utc': datetime.now(timezone.utc).isoformat(),
        'before_new_source_or_asset_acquisition': True, 'preserved_tracked_sha256': hashes,
        'historical_ops_text': ops, 'source_sha256': {str(p.relative_to(ROOT)).replace('\\','/'): sha(p)
              for p in [HERE / 'protocol.json', Path(__file__), ROOT / 'paper11_v2/mission-boundary-audit1.json']},
        'exposure': 'Existing52metadata identities/onsets;47previous endpoints and5firstTTLunknowns; publishedTTL definitions. No external neural data.'})
    verify()


def verify():
    reg = load(OUT / 'protocol_registration.json')
    for field in ['preserved_tracked_sha256', 'source_sha256']:
        for p, digest in reg[field].items():
            if sha(ROOT / p) != digest:
                raise RuntimeError('Frozen prior/protocol source changed: ' + p)
    if reg['historical_ops_text'] not in (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8'):
        raise RuntimeError('Historical operations record changed')
    return reg


def sources():
    import requests
    verify()
    folder = OUT / 'sources'
    if folder.exists():
        raise RuntimeError('Source attempt already exists; do not overwrite')
    folder.mkdir()
    receipts, total = [], 0
    session = requests.Session()

    def get(url, name):
        nonlocal total
        with session.get(url, timeout=60, stream=True) as r:
            r.raise_for_status()
            data = b''.join(r.iter_content(16384))
        if len(data) > 262144 or total + len(data) > 2097152:
            raise RuntimeError('Document source budget exceeded')
        total += len(data)
        (folder / name).write_bytes(data)
        receipts.append({'url': url, 'local': name, 'bytes': len(data), 'sha256': sha(folder/name)})
        return data

    api = 'https://api.github.com/repos/rutishauserlab/recogmem-release-NWB'
    try:
        meta = json.loads(get(api, 'repository.json'))
        commit = json.loads(get(api + '/commits/' + meta['default_branch'], 'commit.json'))['sha']
        tree = json.loads(get(api + '/git/trees/' + commit + '?recursive=1', 'tree.json'))
        if tree.get('truncated'):
            raise RuntimeError('Author source tree truncated')
        selected = [n for n in tree['tree'] if n['type']=='blob' and
                    (n['path'] in ['README.MD','LICENSE.txt'] or
                     ('3rd' not in n['path'].lower() and 'third' not in n['path'].lower()
                      and Path(n['path']).suffix.lower() in ['.py','.m','.ini','.txt']
                      and ('export' in n['path'].lower() or 'helper' in n['path'].lower()
                           or 'no2nwb' in n['path'].lower())))]
        for i, entry in enumerate(selected):
            get('https://raw.githubusercontent.com/rutishauserlab/recogmem-release-NWB/' + commit + '/' + entry['path'],
                f'{i:03d}_' + entry['path'].replace('/','__'))
        save(folder / 'receipt.json', {'author_commit': commit, 'source_tree_sha': tree['sha'],
             'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'receipts': receipts,
             'neural_values_accessed': False, 'downloaded_code_executed': False})
    except Exception as e:
        save(folder / 'failure.json', {'class': type(e).__name__, 'message': 'Document source acquisition failed; see preserved receipts', 'receipts': receipts})
        raise


if __name__ == '__main__':
    {'register': register, 'verify': verify, 'sources': sources}[sys.argv[1]]()
    print('Document-only ' + sys.argv[1] + ' complete; R2 remains FAIL.')
