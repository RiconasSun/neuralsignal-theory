"""Progressive checksum-bound public NIX acquisition; no signal decoding."""
import hashlib
import json
import re
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import run_m1 as m1
import run_m2 as m2
import nix_mapping

MANIFEST = m2.MANIFEST / 'nix_objects.json'
RAW = m1.PAPER / 'raw' / 'NIX'
PREFIX = 'https://nemar.s3.us-east-2.amazonaws.com/nm000363/objects/'


def mapping():
    tree = m1.m0.load(m1.MANIFEST / 'repository_trees/nm000363.json')['response']['tree']
    blobs = {row['path']: row for row in tree}
    source = m2.MANIFEST / 'source_audit/srcadd_provenance.json'
    source_path = 'sourcedata/gin-USZ_NCH-Human_MTL_units_scalp_EEG_and_iEEG_verbal_WM/srcadd_provenance_2026-10-07.json'
    if m1.blob_sha(source.read_bytes()) != blobs[source_path]['sha']:
        raise ValueError('Source-add provenance differs from pinned release')
    provenance = json.loads(source.read_text())
    if 'attributes only; no data array changed' not in provenance['note']:
        raise ValueError('NIX source modification semantics unresolved')
    originals = {row['src']: row for row in provenance['sources']}
    objects = []
    for key in sorted(m2.selection()):
        subject, session = key.split('/')
        row = next(row for row in m1.rows(m1.DATA / 'nm000363' / subject / f'{subject}_sessions.tsv') if row['session_id'] == session)
        name = row['nix_source_file']
        path = 'sourcedata/gin-USZ_NCH-Human_MTL_units_scalp_EEG_and_iEEG_verbal_WM/data_nix/' + name
        item = blobs[path]
        if item['size'] > 256:
            raise ValueError('Expected tiny annex pointer, not signal content')
        url = f'https://raw.githubusercontent.com/nemarDatasets/nm000363/{m1.m0.NM}/{path}'
        with urllib.request.urlopen(url, timeout=30) as response:
            pointer = response.read(257)
        if m1.blob_sha(pointer) != item['sha']:
            raise ValueError('Annex pointer blob mismatch')
        match = re.fullmatch(rb'/annex/objects/(SHA256E-s(\d+)--([0-9a-f]{64})\.h5)\s*', pointer)
        if not match:
            raise ValueError('Unexpected annex object pointer')
        original = originals[name]
        if original['mode'] != 'copy_nixmask' or original['sha256'] != row['nix_source_sha256'] or original['bytes'] != int(match[2]):
            raise ValueError('NIX source crosswalk or modification provenance mismatch')
        objects.append({'session_key': key, 'filename': name, 'size': int(match[2]),
                        'sha256': match[3].decode(), 'original_sha256': original['sha256'],
                        'pointer_git_blob_sha1': item['sha'], 'url': PREFIX + match[1].decode(),
                        'modification': 'source-added NEMAR NIX: timestamp attributes masked; arrays unchanged per pinned provenance'})
    result = {'dataset': 'nm000363', 'commit': m1.m0.NM, 'source_add_git_blob_sha1': blobs[source_path]['sha'],
              'source_add_sha256': m1.digest(source), 'annex_remote_commit': '8ddfc6f2e0a09710aeb27b2cff443990de8fb3a2', 'objects': objects}
    if MANIFEST.exists() and m1.m0.load(MANIFEST) != result:
        raise ValueError('Frozen NIX object mapping changed')
    nix_mapping.validate(result)
    m1.write_json(MANIFEST, result)
    return objects


def download(item):
    target = RAW / item['filename']
    if target.exists():
        if target.stat().st_size != item['size'] or m1.digest(target) != item['sha256']:
            raise ValueError('Existing NIX file does not match frozen primary annex object')
        return {**item, 'mode': 'verified_cache', 'verified_at_utc': m1.now()}
    part = target.with_suffix('.h5.part')
    if part.exists():
        raise ValueError('Partial NIX acquisition exists; investigate before replacing')
    request = urllib.request.Request(item['url'], headers={'User-Agent': 'NSI-P11-checksum-acquisition'})
    digest, total = hashlib.sha256(), 0
    with urllib.request.urlopen(request, timeout=120) as response, part.open('wb') as handle:
        if response.status != 200 or int(response.headers['Content-Length']) != item['size']:
            raise ValueError('NIX download status/size mismatch')
        while chunk := response.read(4 * 1024 * 1024):
            handle.write(chunk)
            digest.update(chunk)
            total += len(chunk)
            if total > item['size']:
                raise ValueError('NIX size exceeds declared object')
    if total != item['size'] or digest.hexdigest() != item['sha256']:
        raise ValueError('Whole-file NIX SHA256 mismatch')
    part.rename(target)
    return {**item, 'mode': 'http200_whole_file_checksum', 'verified_at_utc': m1.now()}


def main():
    m2.prerequisite()
    RAW.mkdir(parents=True, exist_ok=True)
    objects = mapping()
    if shutil.disk_usage(RAW).free < sum(item['size'] for item in objects if not (RAW / item['filename']).exists()) + 1024**3:
        raise ValueError('Insufficient local space for checksum-bound NIX acquisition')
    results = {}
    stages = [('smoke', objects[:1]), ('small_cohort', [item for item in objects if item['session_key'].startswith(('sub-01/', 'sub-02/'))]), ('full_cohort', objects)]
    for stage, items in stages:
        with ThreadPoolExecutor(max_workers=3) as pool:
            for row in pool.map(download, items):
                results[row['session_key']] = row
        m1.write_json(m2.RESULTS / 'nix_acquisition.json', {'timestamp_values_decoded': False, 'stage': stage,
                      'files': [results[key] for key in sorted(results)]})
        print(json.dumps({'stage': stage, 'sessions_verified': len(results), 'total_bytes': sum(row['size'] for row in results.values())}), flush=True)


if __name__ == '__main__':
    main()
