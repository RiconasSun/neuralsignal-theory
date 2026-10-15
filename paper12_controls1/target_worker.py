"""Native synthetic final-analysis principal. No model/data evaluation."""
import hashlib
import json
from pathlib import Path
import sys
import time
def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)]
    from native_analysis_check import check
    from release_control import package_sid
    data=Path(data);out=Path(output)
    def save(name,value):
        with (out/(name+'.json')).open('x') as f:json.dump(value,f,indent=2)
    proof=check(source,key,pid,sddl);save('role_proof',proof)
    if not proof['pass']:raise PermissionError('TARGET_ACTUAL_ROLE')
    protected=json.loads((data/'protected_probes.json').read_text());denials={}
    for name,path in protected.items():
        try:
            with open(path,'rb') as f:f.read(1)
            denials[name+'_read']=False
        except PermissionError:denials[name+'_read']=True
        try:
            with open(path,'ab') as f:f.write(b'UNAUTHORIZED_TEST')
            denials[name+'_write']=False
        except PermissionError:denials[name+'_write']=True
    save('key_ledger_denials',denials)
    if not all(denials.values()):raise PermissionError('FINAL_PRINCIPAL_PROTECTED_ACCESS')
    save('ready',{'pid':__import__('os').getpid(),'package_sid':package_sid(),'no_D_evaluation':True})
    start=time.monotonic()
    while not (data/'stop.json').exists() and time.monotonic()-start<600:time.sleep(.1)
    post={}
    for name,path in protected.items():
        try:
            with open(path,'rb') as f:f.read(1)
            post[name+'_read']=False
        except PermissionError:post[name+'_read']=True
        try:
            with open(path,'ab') as f:f.write(b'UNAUTHORIZED_POSTGRANT_TEST')
            post[name+'_write']=False
        except PermissionError:post[name+'_write']=True
    save('postgrant_key_ledger_denials',post)
    if not all(post.values()):raise PermissionError('POSTGRANT_PROTECTED_ACCESS')
    p=data/'synthetic_released_canary.bin'
    save('gate_result',{'gate':'PASS' if p.exists() else 'FAIL','synthetic_capability_sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None,
        'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False,'synthetic_only':True})
if __name__=='__main__':main()
