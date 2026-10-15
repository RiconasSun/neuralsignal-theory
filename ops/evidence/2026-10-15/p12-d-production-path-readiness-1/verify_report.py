"""Independent saved scalar report oracle; no model fitting or neural loaders."""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=ROOT/'paper12_production1'

def require(condition,message):
    if not condition:raise RuntimeError(message)

def main():
    pointer=json.loads((HERE/'latest_saved_result.json').read_text())
    output=HERE/pointer['path'];saved=json.loads((output/'target/final_statistics.json').read_text());text=(output/'target/report.md').read_text()
    require(saved['scope']=='SYNTHETIC_ENGINEERING_ONLY' and text.startswith('# SYNTHETIC_ENGINEERING_ONLY\n'),'SYNTHETIC_REPORT_SCOPE')
    names=('own','population','stimulus_time','combined');found={}
    for line in text.splitlines():
        cells=[x.strip() for x in line.strip('|').split('|')]
        if cells[0] not in names:continue
        require(len(cells)==8 and cells[0] not in found,'EXACT_UNIQUE_REPORT_ROW')
        name=cells[0];record=saved['mouse_statistics']['primary']['statistics'][name]
        for i,key in ((1,'mean_CA1_gain'),(2,'mean_DG_gain'),(3,'mean_CA1_minus_DG'),(5,'paired_signflip_p'),(6,'holm_p')):require(float(cells[i])==record[key],name+':'+key)
        require(ast.literal_eval(cells[4])==record['CI95'],name+':CI95')
        require(cells[7]==saved['verdicts'][name]['classification'],name+':CLASSIFICATION');found[name]=True
    require(set(found)==set(names),'EXACT_FOUR_REPORT_CONTRASTS')
    print(json.dumps({'saved_report_semantic_reproduction':'PASS','four_contrasts':found,'report_sha256':hashlib.sha256((output/'target/report.md').read_bytes()).hexdigest(),'no_fits':True,'no_neural_arrays_or_keys_read':True,'D_EVALUATION_EXECUTED':False},sort_keys=True))

if __name__=='__main__':main()
