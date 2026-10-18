"""Public, projected metadata only. No NWB body, spike or analysis-metric access."""
import datetime
import json
import shutil
import urllib.parse
import urllib.request
from pathlib import Path
from .core import dump_json, read_json, sha256
from .http_metadata import sanitize_headers

P = Path(__file__).resolve().parents[1]
R = P.parent
E = R / 'ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0'
API = 'https://api.brain-map.org/api/v2/data/query.json'


def fetch(name, url, maximum=25_000_000, archive_body=True):
    receipt = P / 'metadata' / (name + '.json')
    if receipt.exists():
        d = read_json(receipt)
        if d.get('status') != 200:
            raise RuntimeError('Saved failed metadata request; choose an evidenced repair, not silent retry')
        return (P / d['body']).read_bytes()
    folder = P / ('metadata' if archive_body else 'work/source_documents')
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (name + '.body')
    data = bytearray()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'P16-M0-noncommercial-source-audit'}), timeout=90) as res:
            headers = sanitize_headers(res.headers)
            status, final = res.status, res.url
            while True:
                block = res.read(min(262144, maximum - len(data) + 1))
                if not block:
                    break
                data.extend(block)
                if len(data) > maximum:
                    raise RuntimeError('Projected metadata response exceeds registered audit limit')
        target.write_bytes(data)
        dump_json(receipt, {'url': url, 'resolved_url': final, 'status': status,
                           'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           'bytes': len(data), 'sha256': sha256(target), 'headers': headers,
                           'body': target.relative_to(P).as_posix(), 'neural_arrays_decoded': False})
        return bytes(data)
    except Exception as exc:
        target.write_bytes(data)
        dump_json(receipt, {'url': url, 'status': 'FAILED', 'error_type': type(exc).__name__,
                           'error': str(exc), 'bytes': len(data), 'sha256': sha256(target),
                           'body': target.relative_to(P).as_posix(), 'neural_arrays_decoded': False})
        raise


def copy_prior(name, source):
    target = P / 'metadata' / (name + '.body')
    if not target.exists():
        shutil.copyfile(R / source, target)
        dump_json(P / 'metadata' / (name + '.json'), {
            'source': source, 'source_sha256': sha256(R / source), 'sha256': sha256(target),
            'bytes': target.stat().st_size, 'status': 200, 'body': target.relative_to(P).as_posix(),
            'reuse': 'Prior pinned Allen public metadata, exact bytes; no old worker imported',
            'neural_arrays_decoded': False})
    data = read_json(target)
    if not data['success'] or len(data['msg']) != data['total_rows']:
        raise ValueError('Incomplete prior public source inventory')
    return data['msg']


def main():
    freeze = read_json(E / ('REGISTRATION_RECEIPT_2.json' if (E / 'REGISTRATION_RECEIPT_2.json').exists() else 'REGISTRATION_RECEIPT.json'))
    assert freeze['registration_sha256'] == sha256(P / 'FEASIBILITY_REGISTRATION.json')
    sessions = copy_prior('sessions', 'paper12/metadata/allen_sessions.receipt')
    probes = copy_prior('probes', 'paper12/metadata/allen_probes.receipt')
    channels = copy_prior('channels', 'paper12/metadata/allen_channels.receipt')
    fields = 'id,ecephys_channel_id,quality,amplitude_cutoff,presence_ratio,isi_violations'
    criteria = "model::EcephysUnit,rma::options[tabular$eq'" + fields + "'][num_rows$eq'all'][order$eq'id']"
    raw = fetch('source_unit_qc', API + '?' + urllib.parse.urlencode({'criteria': criteria}))
    units = json.loads(raw)
    if not units['success'] or len(units['msg']) != units['total_rows']:
        raise ValueError('Incomplete projected unit metadata')
    if any(set(u) != set(fields.split(',')) for u in units['msg']):
        raise ValueError('Unregistered source columns returned')
    # No response-selectivity/tuning or raw spike fields are requested.
    dump_json(P / 'metadata' / 'METADATA_INPUTS_ACTIVE.json', {
        'sessions': 'sessions.body', 'probes': 'probes.body', 'channels': 'channels.body',
        'units': 'source_unit_qc.body', 'registration_sha256': sha256(P / 'FEASIBILITY_REGISTRATION.json'),
        'note': 'All-source metadata; no eligibility counts computed by acquisition'})
    print('Complete projected source metadata saved; still no spike arrays or prediction')


if __name__ == '__main__':
    main()
