"""Compare regenerated paginated PDF text/pages; no result reevaluation."""
import argparse
import json
from pathlib import Path
from pypdf import PdfReader

parser=argparse.ArgumentParser();parser.add_argument('--original',required=True);parser.add_argument('--regenerated',required=True)
args=parser.parse_args();report={}
for name in ('manuscript','supplement'):
    original=PdfReader(Path(args.original)/(name+'.pdf'));other=PdfReader(Path(args.regenerated)/(name+'.pdf'))
    assert len(original.pages)==len(other.pages)
    for a,b in zip(original.pages,other.pages):
        assert a.extract_text()==b.extract_text()
        assert a.mediabox==b.mediabox
    report[name]={'pages':len(original.pages),'extracted_text_equal':True,'page_geometry_equal':True}
print(json.dumps(report))
