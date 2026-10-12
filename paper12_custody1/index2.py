"""Append-only P1 index remediation; original counts remain until raw-index audit."""
import ast
import sys
from datetime import datetime,timezone
import numpy as np
import h5py
import register as r
import custodian as original
import transport1
from index_validation import identity,offsets


def session_callable():
    tree=ast.parse((r.HERE/'custodian.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='session')
    storage={'.private/real':'.private/real_index2','results/M2/sessions':'results/M2/index2/sessions',
             'results/M2/failures':'results/M2/index2/failures'}
    changed=[];cast_changes=[]
    class Fix(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in storage:
                changed.append(n.value);return ast.copy_location(ast.Constant(storage[n.value]),n)
            return n
        def visit_Assign(self,n):
            n=self.generic_visit(n)
            if len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
                target=n.targets[0].id
                if target in ('ids','channels','offsets') and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='asarray':
                    raw=n.value.args[0]
                    n.value=ast.Call(func=ast.Name(id='validated_identity' if target!='offsets' else 'np_raw_array',ctx=ast.Load()),args=[raw],keywords=[])
                    cast_changes.append(target)
                if target=='spikes':
                    extra=ast.parse('offsets=validated_offsets(offsets,len(ids),len(spikes))').body[0]
                    cast_changes.append('bounds_before_slicing')
                    return [n,extra]
            return n
    node=Fix().visit(node)
    if sorted(changed)!=sorted(storage) or sorted(cast_changes)!=sorted(['ids','channels','offsets','bounds_before_slicing']):
        raise RuntimeError('UNEXPECTED_INDEX_REPAIR_SCOPE')
    namespace=dict(vars(original));namespace.update(Source=transport1.Source,validated_identity=identity,validated_offsets=offsets,np_raw_array=np.asarray)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(r.HERE/'custodian.py'),'exec'),namespace)
    return namespace['session']


def register_fix():
    original.check_gate()
    record={'id':'P12-CUSTODY-INDEX-2','utc':datetime.now(timezone.utc).isoformat(),
            'reason':'Independent reviewer P1:negative/unsigned-overflow ragged offsets may pass original post-cast check. No real-output impact yet established.',
            'policy':'Validate raw integer representability/nonnegative/bounds/cardinality/monotonic/final-length before slicing. Audit all26raw source indices;old completedQC reusable only after exact valid-source cast equivalence proved. Original failures/counts retained,not rewritten.',
            'sha256':{name:r.sha(r.HERE/name) for name in ('index2.py','index_validation.py','test_index_validation.py','custodian.py','transport1.py')}}
    r.save(r.HERE/'index_registration2.json',record,True)


def audit_indices(animal,item):
    require=original.require_custodian;require()
    reader=transport1.Source(item)
    result={'mouse_id':animal['mouse_id'],'session_id':animal['session_id'],'group':animal['group'],
            'raw_index_valid':False,'old_cast_equivalence_proved':False,'spike_timestamps_decoded_for_audit':False,
            'final_values_exposed_to_analysis':False,'final_holdout_evaluated':False}
    try:
        with h5py.File(reader,'r') as f:
            ids_raw=original.dataset(f,'/units/id','iu')[:]
            channels_raw=original.dataset(f,'/units/peak_channel_id','iu')[:]
            raw=original.dataset(f,'/units/spike_times_index','iu')[:]
            identity(ids_raw);identity(channels_raw)
            safe=offsets(raw,len(ids_raw),len(original.dataset(f,'/units/spike_times','f')))
            result['raw_index_valid']=True
            result['old_cast_equivalence_proved']=np.array_equal(safe,np.asarray(raw,dtype=np.int64))
    except Exception as exc:
        result['error_type']=type(exc).__name__;result['error_code']='SOURCE_INDEX_AUDIT_FAILED'
    finally:reader.close()
    r.save(r.HERE/'results/index2/audit'/(animal['session_id']+'.json'),result,True)
    print({k:result[k] for k in ('session_id','raw_index_valid','old_cast_equivalence_proved')},flush=True)
    if not result['raw_index_valid'] or not result['old_cast_equivalence_proved']:
        raise RuntimeError('SOURCE_INDEX_INVALID_STOP')


def main():
    if '--register' in sys.argv:
        register_fix();print('P1 repair registered;all previous evidence preserved');return
    original.check_gate()
    record=r.load(r.HERE/'index_registration2.json')
    for name,value in record['sha256'].items():
        if r.sha(r.HERE/name)!=value:raise RuntimeError('INDEX_REPAIR_CHANGED')
    old=r.ROOT/'paper12_curated_v1';animals=r.load(old/'locks/animals.json');units=r.load(old/'locks/units.json');trials=r.load(old/'locks/trials.json')
    items={x['session_id']:x for x in r.load(r.ROOT/'paper12/metadata/allen_header_capability.json')}
    for animal in animals:
        path=r.HERE/'results/index2/audit'/(animal['session_id']+'.json')
        if not path.exists():audit_indices(animal,items[animal['session_id']])
        elif not r.load(path)['raw_index_valid']:raise RuntimeError('PRESERVED_INDEX_FAILURE_STOP')
    if '--audit-only' in sys.argv:return
    execute=session_callable()
    for a in animals:
        sid=a['session_id'];current=r.HERE/'results/M2/index2/sessions'/(sid+'.json');bad=r.HERE/'results/M2/index2/failures'/(sid+'.json')
        if bad.exists():raise RuntimeError('PRESERVED_INDEX2_EXTRACTION_FAILURE_STOP')
        if current.exists():continue
        previous=r.HERE/'results/M2/transport1/sessions'/(sid+'.json')
        if previous.exists():
            value=r.load(previous)
            value['index_validation']='Independent same-object raw-index audit proves pre-cast representation and exact old-cast equivalence'
            value['prior_output_sha256']=r.sha(previous)
            value['custody_artifact_namespace']='real_transport1'
            r.save(current,value,True)
            continue
        execute(a,items[sid],[u for u in units if u['session_id']==sid],[t for t in trials if t['session_id']==sid])


if __name__=='__main__':
    try:main()
    except Exception:
        print('INDEX2_STOP_CHECK_SANITIZED_RECEIPTS',flush=True);sys.exit(1)
