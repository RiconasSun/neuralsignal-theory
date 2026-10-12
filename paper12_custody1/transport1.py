"""Bounded transport retry; original smoke abort and source implementation retained."""
import ast
import json
import sys
from datetime import datetime,timezone
import requests
import register as r
import custodian as original


class TraceSession(requests.Session):
    def __init__(self,owner):
        super().__init__();self.owner=owner;self.headers['Accept-Encoding']='identity'
    def get(self,*args,**kwargs):
        response=super().get(*args,**kwargs)
        self.owner.diagnostics.append({'status':response.status_code,'content_range':response.headers.get('Content-Range'),
                                      'content_length':response.headers.get('Content-Length'),
                                      'content_encoding':response.headers.get('Content-Encoding')})
        return response


class Source(original.Source):
    def __init__(self,item):
        super().__init__(item);self.http.close();self.diagnostics=[];self.http=TraceSession(self)
    def close(self):
        if hasattr(self,'diagnostics'):
            root=r.HERE/'.private/transport_diagnostics'
            root.mkdir(parents=True,exist_ok=True)
            original.protect(root)
            path=root/('transport_'+str(id(self))+'.json')
            r.save(path,self.diagnostics,True);original.protect(path)
        super().close()


def session_callable():
    # Only storage literals are changed; frozen source validation/QC/scoring is unchanged.
    tree=ast.parse((r.HERE/'custodian.py').read_text())
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='session')
    mapping={'.private/real':'.private/real_transport1','results/M2/sessions':'results/M2/transport1/sessions',
             'results/M2/failures':'results/M2/transport1/failures'}
    changed=[]
    class Redirect(ast.NodeTransformer):
        def visit_Constant(self,node):
            if isinstance(node.value,str) and node.value in mapping:
                changed.append(node.value);return ast.copy_location(ast.Constant(mapping[node.value]),node)
            return node
    function=Redirect().visit(function)
    if sorted(changed)!=sorted(mapping):raise RuntimeError('UNEXPECTED_STORAGE_PATCH_SCOPE')
    namespace=dict(vars(original));namespace['Source']=Source
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),str(r.HERE/'custodian.py'),'exec'),namespace)
    return namespace['session']


def register_transport():
    original.check_gate()
    record={'utc':datetime.now(timezone.utc).isoformat(),'id':'P12-CUSTODY-TRANSPORT-1',
            'failure_preserved':'results/M2/failures/766640955.json','failure_code':'SOURCE_RESPONSE_LENGTH_INVALID',
            'diagnosis':'One frozen-source response failed byte-length validation before timestamps. Header and exact-first-range diagnostics passed. Content negotiation is a hypothesis,not a proven rootcause.',
            'policy':'One complete smoke attempt with Accept-Encoding identity and private response-header diagnostics; no accepted-byte threshold relaxation or scientific changes. Any repeated mismatch stops. No favorable neural-outcome selection.',
            'sha256':{'transport1.py':r.sha(r.HERE/'transport1.py'),'custodian.py':r.sha(r.HERE/'custodian.py')},
            'source_full_session_decoded_by_custodian':False,'final_values_exposed_to_analysis':False,'final_holdout_evaluated':False}
    r.save(r.HERE/'transport_registration1.json',record,True)


def main():
    if '--register' in sys.argv:
        register_transport();print('Prospective transport retry registered;original failure unchanged');return
    original.check_gate()
    record=r.load(r.HERE/'transport_registration1.json')
    for path,value in record['sha256'].items():
        if r.sha(r.HERE/path)!=value:raise RuntimeError('TRANSPORT_IMPLEMENTATION_CHANGED')
    old=r.ROOT/'paper12_curated_v1';animals=r.load(old/'locks/animals.json');units=r.load(old/'locks/units.json');trials=r.load(old/'locks/trials.json')
    items={x['session_id']:x for x in r.load(r.ROOT/'paper12/metadata/allen_header_capability.json')}
    if '--smoke' in sys.argv:animals=animals[:1]
    execute=session_callable()
    for animal in animals:
        sid=animal['session_id']
        if (r.HERE/'results/M2/transport1/failures'/(sid+'.json')).exists():raise RuntimeError('TRANSPORT_RETRY_FAILED_STOP')
        if (r.HERE/'results/M2/transport1/sessions'/(sid+'.json')).exists():continue
        execute(animal,items[sid],[u for u in units if u['session_id']==sid],[t for t in trials if t['session_id']==sid])


if __name__=='__main__':
    try:main()
    except Exception:
        print('TRANSPORT_RETRY_ABORTED_CHECK_SANITIZED_RECEIPT',flush=True);sys.exit(1)
