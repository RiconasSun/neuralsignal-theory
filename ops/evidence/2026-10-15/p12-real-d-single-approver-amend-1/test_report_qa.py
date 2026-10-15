"""Optimized-Python fail-closed tests using invented saved scalar fixtures only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];TEMP=ROOT/'paper12_singleowner1/jobs/test_tmp'

def main():
    TEMP.mkdir(parents=True,exist_ok=True);names=('own','population','stimulus_time','combined');stats={};verdicts={};lines=['# SYNTHETIC_ENGINEERING_ONLY','']
    for name in names:
        stats[name]={'mean_CA1_gain':1.,'mean_DG_gain':0.,'mean_CA1_minus_DG':1.,'CI95':[.5,1.5],'paired_signflip_p':.1,'holm_p':.4};verdicts[name]={'classification':'NOT VALIDATED / MIXED'}
        lines.append('|'+name+'|1.0|0.0|1.0|[0.5, 1.5]|0.1|0.4|NOT VALIDATED / MIXED|')
    runner="import importlib.util,sys;from pathlib import Path;s=importlib.util.spec_from_file_location('qa',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.HERE=Path(sys.argv[2]);m.main()"
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        root=Path(folder).resolve()
        if not root.is_relative_to(TEMP.resolve()):raise RuntimeError('WORKSPACE_TEMP_BOUNDARY')
        out=root/'result/target';out.mkdir(parents=True);(root/'latest_saved_result.json').write_text(json.dumps({'path':'result'}))
        state={'scope':'SYNTHETIC_ENGINEERING_ONLY','mouse_statistics':{'primary':{'statistics':stats}},'verdicts':verdicts};(out/'final_statistics.json').write_text(json.dumps(state))
        for mode in ('valid','tampered_p','missing_row','duplicate_row','wrong_scope'):
            content='\n'.join(lines)+'\n'
            if mode=='tampered_p':content=content.replace('|0.1|0.4|','|0.01|0.4|',1)
            if mode=='missing_row':content='\n'.join(lines[:-1])+'\n'
            if mode=='duplicate_row':content+=lines[-1]+'\n'
            if mode=='wrong_scope':content=content.replace('SYNTHETIC_ENGINEERING_ONLY','REAL_D')
            (out/'report.md').write_text(content)
            result=subprocess.run([sys.executable,'-O','-B','-c',runner,str(HERE/'verify_report.py'),str(root)],capture_output=True,text=True)
            if (mode=='valid')!=(result.returncode==0):raise RuntimeError('OPTIMIZED_QA_ORACLE:'+mode)
            print(json.dumps({'case':mode,'optimized_python':True,'PASS':True,'expected_exit':'0' if mode=='valid' else 'nonzero'}))
    print('SAVED_SCALAR_QA_REGRESSION_5_PASS_NO_NEURAL_ARRAYS')

if __name__=='__main__':main()
