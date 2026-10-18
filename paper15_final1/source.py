"""Final exact-roster identities and strict saved JSON; no payload side effects."""
from pathlib import Path
import csv
import hashlib
from paper15_r1.source import dump, load_json, json_safe, BUCKET

R=Path(__file__).resolve().parents[1]
P=R/'paper15_final1'
E=R/'ops/evidence/2026-10-18/p15-m6-independent-final-validation'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()


def read(path):return load_json(Path(path).read_text(encoding='utf-8-sig'))


def roster():
    with (R/'paper15_m1/COHORT.csv').open(newline='') as f:
        rows=[r for r in csv.DictReader(f) if r['allocation']=='FINAL_RESERVED']
    assert len(rows)==len({r['subject'] for r in rows})==8
    return rows


def frozen_definitions():
    reg=read(E/'PRESERVATION_REGISTRATION.json')
    assert sha(R/'paper15_m1/PROTOCOL_FREEZE.json')==reg['M1_freeze_sha256']
    assert sha(R/'paper15_r1/ARCHIVE_FREEZE.json')==reg['R1_archive_sha256']
    assert sha(R/'paper15_r1/SELECTION_FREEZE.json')==reg['selection_sha256']
    for rel,h in read(R/'paper15_m1/PROTOCOL_FREEZE.json')['hashes'].items():assert sha(R/'paper15_m1'/rel)==h,rel
    prior=read(R/'paper15_r1/ARCHIVE_FREEZE.json')['hashes']
    for rel in ['SOURCE_FILE_FREEZE.json','source.py','metadata_access.py','metadata_qc.py',
                'features.py','models.py','independent_ad.py','native_table.py','physiology.py',
                'source_integrity.py','statistics.py','controls.py']:
        assert sha(R/'paper15_r1'/rel)==prior[rel],rel
    assert read(R/'paper15_r1/SELECTION_FREEZE.json')['selected']==reg['selection']
    assert roster()==reg['final_roster']


def source_rows():
    rows=read(R/'paper15_r1/SOURCE_FILE_FREEZE.json')['subjects']
    out=[]
    for original in roster():
        row=next(x for x in rows if x['subject']==original['subject'])
        assert row['source_inventory_pass'] and row['allocation']=='FINAL_RESERVED'
        assert all(row[k]==original[k] for k in ('subject','eid','pid','allocation'))
        assert all(f['probe']==original['probe_name'] for f in row['files'])
        out.append(row)
    return out
