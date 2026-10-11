"""Offline cryptographic binding of primary masked NIX objects to Git pointers."""
import re
import run_m1 as m1

PREFIX = 'https://nemar.s3.us-east-2.amazonaws.com/nm000363/objects/'


def validate(mapping):
    if mapping['dataset'] != 'nm000363' or mapping['commit'] != m1.m0.NM:
        raise ValueError('Wrong NIX dataset/version mapping')
    tree = m1.m0.load(m1.MANIFEST / 'repository_trees/nm000363.json')['response']['tree']
    blobs = {row['path']: row for row in tree}
    source_path = 'sourcedata/gin-USZ_NCH-Human_MTL_units_scalp_EEG_and_iEEG_verbal_WM/srcadd_provenance_2026-10-07.json'
    source = m1.PAPER / 'data_manifest/M2/source_audit/srcadd_provenance.json'
    if m1.blob_sha(source.read_bytes()) != blobs[source_path]['sha'] or m1.digest(source) != mapping['source_add_sha256']:
        raise ValueError('Pinned masked-source provenance mismatch')
    if mapping['source_add_git_blob_sha1'] != blobs[source_path]['sha']:
        raise ValueError('Provenance blob identity mismatch')
    provenance = m1.m0.load(source)
    if 'attributes only; no data array changed' not in provenance['note']:
        raise ValueError('Masked-source semantics unresolved')
    originals = {row['src']: row for row in provenance['sources']}
    sessions = m1.rows(m1.RESULTS / 'session_qc.csv')
    required = {row['subject'] + '/' + row['session'] for row in sessions if row['eligible'] == 'True'}
    objects = mapping['objects']
    if len(objects) != len(required) or {row['session_key'] for row in objects} != required:
        raise ValueError('Missing/duplicate/extraneous session object mapping')
    for row in objects:
        subject, session = row['session_key'].split('/')
        accepted = next(s for s in m1.rows(m1.DATA / 'nm000363' / subject / f'{subject}_sessions.tsv') if s['session_id'] == session)
        if row['filename'] != accepted['nix_source_file'] or not re.fullmatch('[0-9a-f]{64}', row['sha256']):
            raise ValueError('Wrong NIX filename or checksum syntax')
        original = originals[row['filename']]
        if original['mode'] != 'copy_nixmask' or row['original_sha256'] != original['sha256'] or original['sha256'] != accepted['nix_source_sha256'] or row['size'] != original['bytes']:
            raise ValueError('Original NIX source crosswalk mismatch')
        key = f"SHA256E-s{row['size']}--{row['sha256']}.h5"
        pointer = ('/annex/objects/' + key + '\n').encode()
        path = 'sourcedata/gin-USZ_NCH-Human_MTL_units_scalp_EEG_and_iEEG_verbal_WM/data_nix/' + row['filename']
        if m1.blob_sha(pointer) != blobs[path]['sha'] or row['pointer_git_blob_sha1'] != blobs[path]['sha'] or row['url'] != PREFIX + key:
            raise ValueError('NIX object not bound to frozen annex pointer')
    return mapping


def load():
    return validate(m1.m0.load(m1.PAPER / 'data_manifest/M2/nix_objects.json'))
