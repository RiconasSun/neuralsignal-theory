import datetime,hashlib
from paper15_r1.source import P,R,dump
E=R/'ops/evidence/2026-10-17/p15-dev-exact-native-repair-r1'
review=E/'NATIVE_REPAIR_REVIEW_2.md';assert review.exists()
files=['source.py','native_table.py','cached_source.py','metadata_access.py','metadata_qc.py','reader.py','physiology.py',
    'SOURCE_FILE_FREEZE.json','NEURAL_HEADER_FREEZE.json','test_native_table.py','input_oracle.py']
files += ['metadata/'+p.name for p in sorted((P/'metadata').glob('*_task.json'))]
assert len(list((P/'metadata').glob('*_task.json')))==12
target=P/'READER_GATE.json';assert not target.exists()
dump(target,dict(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    approved_for_A_only=True,review_sha256=hashlib.sha256(review.read_bytes()).hexdigest(),
    hashes={rel:hashlib.sha256((P/rel).read_bytes()).hexdigest() for rel in files},
    Final_access=False,coefficient_reuse=False,new_real_fits=0,scope='Reviewed exact native serialization and verified original cache A-only reconstruction; actual physiology and source-level comparisons still required before fitting'))
