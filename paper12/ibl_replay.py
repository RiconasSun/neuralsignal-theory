"""Recheck IBL identity/anatomy joins offline, preserving original gate."""
import csv
import gzip
import io
import json
from pathlib import Path
from acquire import HERE
from audit import write_csv
from ibl_audit import cohort
from register import verify

def main(output=None):
    verify()
    output = Path(output) if output else HERE/'results'
    output.mkdir(exist_ok=True,parents=True)
    fixture = list(csv.DictReader(io.StringIO((HERE/'metadata/ibl_identity_fixture.receipt').read_text())))
    atlas = {str(r['id']):r['acronym'] for r in json.loads((HERE/'metadata/ibl_atlas_dictionary.receipt').read_text())['msg']}
    rows = list(csv.DictReader(io.StringIO(gzip.decompress((HERE/'metadata/ibl_identity_anatomy.csv.gz').read_bytes()).decode())))
    sessions, result = cohort(rows,fixture,atlas)
    write_csv(output/'ibl_sessions_code1.csv',sessions)
    (output/'ibl_coverage_code1.json').write_text(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps({k:v for k,v in result.items() if k!='other_or_unmapped_labels'},indent=2))
    return result

if __name__=='__main__': main()
