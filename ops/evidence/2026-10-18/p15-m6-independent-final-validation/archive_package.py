"""Freeze saved artifacts after reporting; no model or neural-data execution."""
import datetime
from paper15_final1.source import P,R,E,read,dump,sha
from paper15_final1.saved_audit import archive_paths,required_external_paths,verify_archive

MUTABLE_CLOSURE={'verdict.md','review.md','PRESERVATION_MATRIX.json','GIT_READBACK_H1.json','GIT_READBACK_H2.json',
                 'METADATA_ONLY_CLOSURE_DIFF.json'}


def external_evidence_paths():
    # A freeze's stdout log is populated after the snapshot. It is retained in
    # Git,never recursively certified as an input to the same invocation.
    return {p.relative_to(R).as_posix() for p in E.rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and p.name not in MUTABLE_CLOSURE and p.suffix!='.pyc'
            and not (p.name.startswith('ARCHIVE_FREEZE_') and p.suffix=='.log')}


def freeze():
    delivery=read(P/'results/FINAL_DELIVERY.json')
    assert delivery['FINAL_MAIN_FIT_ATTEMPTS']<=96 and delivery['FINAL_SENSITIVITY_FIT_ATTEMPTS']<=440
    names=archive_paths();external=required_external_paths()
    external|=external_evidence_paths()
    freeze=dict(mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',
                time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                hashes={n:sha(P/n) for n in sorted(names)},external_hashes={n:sha(R/n) for n in sorted(external)},
                scope='Saved artifact hashes; no new fits,source-array reads or D reassessment',
                closure_metadata_scope='Mutable closure snapshots and post-freeze review/reproduction/live Git receipts are independently reviewed and bound by the final Git changed-file manifest,not recursively embedded here')
    verify_archive(freeze)
    dump(P/'ARCHIVE_FREEZE.json',freeze)
    print('Saved archive frozen',len(names),'package files',len(external),'source/evidence dependencies')


if __name__=='__main__':freeze()
