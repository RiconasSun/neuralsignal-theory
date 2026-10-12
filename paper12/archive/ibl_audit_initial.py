"""One conditional IBL identity/anatomy-only assessment, no spike loader."""
import csv
import gzip
import io
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
import requests
from acquire import HERE, API, get
from audit import classify, potential, write_csv
from header_metadata import RangeReader
from register import verify, sha

sys.path.insert(0, str(HERE / 'deps'))

class ParquetRanges(RangeReader):
    def read(self, n=-1):
        if n < 0: raise RuntimeError('Unbounded Parquet read forbidden')
        return b''.join(super(ParquetRanges, self).read(min(131072, n - i))
                        for i in range(0, n, 131072))

def cohort(rows, fixture, atlas):
    sessions = defaultdict(list)
    for r in fixture: sessions[r['eid']].append(r)
    counts = defaultdict(Counter)
    outside, unknown = 0, Counter()
    for r in rows:
        if r['eid'] not in sessions:
            outside += 1
            continue
        label = atlas.get(str(abs(int(r['atlas_id']))))
        region = classify(label)
        if region: counts[r['eid']][region] += 1
        else: unknown[str(label)] += 1
    output = []
    for eid, insertions in sorted(sessions.items()):
        identities = {r['subject'] for r in insertions}
        if len(identities) != 1: raise RuntimeError('Conflicting session mouse identities')
        output.append({'eid': eid, 'mouse_id': next(iter(identities)), 'probes': len(insertions),
                       **{key + '_candidate_units': counts[eid][key] for key in ('CA1', 'CA3', 'DG')},
                       'potential_paired_CA1_DG': potential(counts[eid]),
                       'recording_support': 'UNKNOWN'})
    mice = {r['mouse_id'] for r in output}
    paired = {r['mouse_id'] for r in output if r['potential_paired_CA1_DG']}
    return output, {'mice': len(mice), 'sessions': len(output), 'probes': len(fixture),
                    'anatomy_rows': len(rows), 'outside_fixture_rows': outside,
                    'potential_paired_mice': len(paired),
                    'potential_paired_sessions': sum(r['potential_paired_CA1_DG'] for r in output),
                    'admitted_mice': 0, 'other_or_unmapped_labels': dict(unknown)}

def main():
    verify()
    primary = json.loads((HERE / 'results/allen_gate_result.json').read_text())
    if primary['pass']: raise RuntimeError('Conditional alternative forbidden after primary PASS')
    registration = {'utc': datetime.now(timezone.utc).isoformat(), 'policy_sha256': sha(HERE/'IBL_POLICY.json'),
                    'primary_failed_gate_sha256': sha(HERE/'results/allen_gate_result.json'),
                    'code_sha256': sha(Path(__file__))}
    with (HERE/'ibl_registration.json').open('x') as out: json.dump(registration, out, indent=2)
    get('ibl_documentation', 'https://docs.internationalbrainlab.org/notebooks_external/2025_data_release_brainwidemap.html')
    commit_response, _ = get('ibl_source_commit', 'https://api.github.com/repos/int-brain-lab/paper-brain-wide-map/commits/main')
    commit = commit_response.json()['sha']
    base = 'https://raw.githubusercontent.com/int-brain-lab/paper-brain-wide-map/' + commit + '/brainwidemap/'
    get('ibl_loader_source', base + 'bwm_loading.py')
    response, _ = get('ibl_identity_fixture', base + 'fixtures/2023_12_bwm_release.csv')
    fixture = list(csv.DictReader(io.StringIO(response.text)))
    allowed = {'', 'pid', 'eid', 'probe_name', 'session_number', 'date', 'subject', 'lab'}
    if not fixture or set(fixture[0]) - allowed: raise RuntimeError('Unexpected fixture columns')
    print(json.dumps({'fixture_rows': len(fixture), 'columns': list(fixture[0])}), flush=True)
    atlas_response, _ = get('ibl_atlas_dictionary', API, {'criteria': "model::Structure,rma::options[tabular$eq'id,acronym'][num_rows$eq'all']"})
    atlas_data = atlas_response.json()
    if not atlas_data['success'] or len(atlas_data['msg']) != atlas_data['total_rows']: raise RuntimeError('Incomplete atlas')
    atlas = {str(r['id']): r['acronym'] for r in atlas_data['msg']}
    url = 'https://ibl-brain-wide-map-public.s3.amazonaws.com/aggregates/2024_Q2_IBL_et_al_BWM/clusters.pqt'
    head = requests.head(url, timeout=30)
    head.raise_for_status()
    remote = {'url': url, 'bytes': int(head.headers['Content-Length']), 'etag_not_locally_verified': head.headers.get('ETag'),
              'last_modified': head.headers.get('Last-Modified'), 'source_commit': commit}
    (HERE/'metadata/ibl_aggregate_descriptor.json').write_text(json.dumps(remote, indent=2))
    import pyarrow.parquet as pq
    reader = ParquetRanges(url, remote['bytes'], max_bytes=25000000)
    file = pq.ParquetFile(reader)
    permitted = {'eid', 'pid', 'cluster_id', 'atlas_id', 'uuids'}
    columns = [name for name in file.schema_arrow.names if name in permitted]
    if not {'eid', 'atlas_id'}.issubset(columns): raise RuntimeError('Missing identity/anatomy columns')
    frame = file.read(columns=columns, use_threads=False).to_pydict()
    rows = [dict(zip(columns, values)) for values in zip(*(frame[name] for name in columns))]
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader(); writer.writerows(rows)
    (HERE/'metadata/ibl_identity_anatomy.csv.gz').write_bytes(gzip.compress(stream.getvalue().encode(), mtime=0))
    access = {'columns_requested': columns, 'rows': len(rows), 'transport_bytes': reader.used,
              'ranges': reader.ranges, 'full_object_checksum_verified': False,
              'neural_column_values_requested': False, 'pyarrow_version': __import__('pyarrow').__version__}
    (HERE/'metadata/ibl_parquet_access.json').write_text(json.dumps(access, indent=2))
    reader.http.close()
    output, summary = cohort(rows, fixture, atlas)
    write_csv(HERE/'results/ibl_sessions.csv', output)
    (HERE/'results/ibl_coverage.json').write_text(json.dumps(summary, indent=2, sort_keys=True))
    gate = {'phase': 'M0 IBL alternative', 'pass': False,
            'verdict': 'DATA_INSUFFICIENT' if summary['potential_paired_mice'] < 16 else 'INCONCLUSIVE',
            'minimum_required_mice': 16, 'coverage': summary,
            'blockers': ['Native recording support and per-session trial alignment not admitted',
                         'Cross-release fixture/aggregate compatibility and upstream admission are not independent anatomy verification'],
            'next': 'STOP, no M1 or additional candidate search'}
    (HERE/'results/ibl_gate_result.json').write_text(json.dumps(gate, indent=2, sort_keys=True))
    print(json.dumps(gate, indent=2))

if __name__ == '__main__':
    from pathlib import Path
    main()
