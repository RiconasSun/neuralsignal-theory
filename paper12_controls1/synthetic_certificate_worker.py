"""Fresh native saved-state certification. Zero fits or neural input arrays."""
import json
from pathlib import Path
import sys
def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)]
    from native_analysis_check import check
    from release_control import read_json,validate_state_manifest
    data=Path(data);out=Path(output)
    def save(name,value):
        with (out/(name+'.json')).open('x') as f:json.dump(value,f,indent=2)
    proof=check(source,key,pid,sddl);save('role_proof',proof)
    if not proof['pass']:raise PermissionError('FRESH_NATIVE_ROLE')
    m=read_json(data/'C_state_manifest.json');validate_state_manifest(m,data)
    prior=read_json(data/'prior_execution.json')
    if prior['original_gate']['gate']!='PASS' or not prior['original_oracles']['passed'] or prior['original_oracles']['tests']!=27 or not prior['original_role']['pass']:raise RuntimeError('SAVED_SCIENTIFIC_EVIDENCE_FAILED')
    save('gate_result',{'gate':'PASS','scope':'Fresh saved-state certificate; original launch exit/cleanup UNPUBLISHED',
        'new_fits':0,'neural_count_arrays_opened':0,'cases':len(m['cases']),'seed_certificates':len(m['seed_certificates']),
        'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False})
if __name__=='__main__':main()
