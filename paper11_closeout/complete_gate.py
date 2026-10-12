"""Check manuscript completion only; never amend scientific gate results."""
import shutil
from pathlib import Path
from freeze import HERE, ROOT, load, sha, verify
from build import write_json, Saved, validate
from reference_check import verify_references

record=verify();saved=Saved();grid,stats,coverage,original,patients=validate(saved)
output=HERE/'output'; replay=load(HERE/'reproduction/reproducibility_report.json')
assert replay['MANUSCRIPT_REPRODUCED'] and replay['test_exit_code']==0 and replay['tests']==21
assert len(replay['pdf_pixel_parity'])==2 and all(r['pixel_sha256_equal'] for r in replay['pdf_pixel_parity'])
bounds=load(output/'visual_qa/text_bounds.json')
assert all(not r['out_of_bounds_glyphs'] for r in bounds.values())
assert len(load(output/'figure_manifest.json'))==7
assert len(list((output/'attachments').glob('A*.md')))==10
evidence=HERE/'evidence';evidence.mkdir(exist_ok=True)
for filename in ('reproducibility_report.json','execution_log.json','tests.log'):
    shutil.copyfile(HERE/'reproduction'/filename,evidence/filename)
write_json(evidence/'reference_receipts.json',verify_references(output))
write_json(evidence/'QC.json',{'patients':9,'sessions':23,'session_local_units':592,'configurations':57,
     'fits_recorded':3887,'tests':21,'test_exit_code':0,'figures':7,'attachments':10,
     'pdf_pages':{k:v['pages'] for k,v in bounds.items()},'source_hashes_verified':len(record['previous_tracked_sha256']),
     'model_fits_executed':0,'new_statistical_inference':0,'metadata_searches':0,
     'raw_spike_values_accessed':False,'holdout_accessed':False,
     'scope':'Documentation completion only; no historical scientific warning cleared'})
write_json(evidence/'gate_result.json',{'mission':'P11-MANUSCRIPT-CLOSEOUT-1',
     'manuscript_verdict':'MANUSCRIPT_COMPLETE','SCIENTIFIC_VALIDATION_PASS':False,
     'original_P11_v2_R2':'FAIL / DATA_INSUFFICIENT','original_P11_v2_R3':'NOT EXECUTED',
     'original_v1_failures_unchanged':True,'holdout_locks_unchanged':True,
     'saved_only_reproduction_verified':True,'tests':21,
     'submission_ready':False,'author_declaration_approval':'NOT PROVIDED',
     'scientific_limitations_resolved':False,'stop':True,
     'manuscript_sha256':sha(output/'manuscript.pdf'),'supplement_sha256':sha(output/'supplement.pdf'),
     'publication_manifest_sha256':sha(output/'publication_manifest.json')})
print('MANUSCRIPT_COMPLETE; SCIENTIFIC_VALIDATION_PASS=false; oldR2FAIL/R3NOTEXECUTED preserved.')
