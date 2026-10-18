"""Freeze saved-only negative archive once; no scientific execution."""
import datetime
import shutil
from paper15_dev.source import P,R,dump
from paper15_dev.training import sha
from paper15_dev.stop_verify import paths,POST_FREEZE_EVIDENCE

E=R/'ops/evidence/2026-10-17/p15-m2-m5-native-qc-development'
for name in ('real_dynamic_fits.log','real_baseline_fits.log','time_serialization_audit.log'):
    src=P/'work'/name
    if src.exists():
        dst=E/('PRESERVED_'+name);assert not dst.exists();shutil.copyfile(src,dst)
target=P/'STOP_ARCHIVE_FREEZE.json';assert not target.exists()
dump(target,dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    mission='P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT',base='30cb925f505d63ae52bb1461d9ab153a52f1888e',
    package_hashes={rel:sha(P/rel) for rel in sorted(paths())},
    evidence_hashes={p.relative_to(E).as_posix():sha(p) for p in sorted(E.rglob('*')) if p.is_file()
        and '__pycache__' not in p.parts and p.relative_to(E).as_posix() not in POST_FREEZE_EVIDENCE},
    postfreeze_evidence_exclusions=sorted(POST_FREEZE_EVIDENCE),
    evidence_policy='All current mission evidence is frozen, including failed reviews, source diagnostic scripts/receipts and historical preservation manifest. Only named later saved-reproduction/review/verdict/Git closure receipts are excluded from this manifest; those bind the freeze SHA and are verified by final Git blobs. No unlisted evidence is silently ignored.',
    scientific_gate_pass=False,repair_executed=False,retries=0,B_E_neural_access=False,Final_access=False))
print('STOP archive frozen',sha(target))
