"""Shared synthetic/REAL production delivery core; no signer or automatic bootstrap."""
from pathlib import Path
if __package__:
    from .common import *
    from .authority import trusted_public
    from .custodian_producer import validate_catalog,produce
else:
    from common import *
    from authority import trusted_public
    from custodian_producer import validate_catalog,produce

class VerifiedContext:
    __slots__=('_encoded',)
    def __init__(self,value):object.__setattr__(self,'_encoded',canonical(value))
    def __setattr__(self,name,value):raise TypeError('IMMUTABLE_PRODUCTION_CONTEXT')
    def __getitem__(self,key):return __import__('json').loads(self._encoded)[key]

class RegisteredDeployment(VerifiedContext):
    """Trusted host enrollment, not a worker/request-supplied trust root.

    The expected digest is supplied by the separately reviewed operator deployment.
    Root and file ACLs exclude the controller and analysis packages.
    """
    def __init__(self,path,expected_sha256):
        if __package__:
            from .native_host import assert_private
        else:from native_host import assert_private
        path=Path(path);assert_private(path.parent);assert_private(path)
        if sha(path)!=expected_sha256:raise PermissionError('REGISTERED_DEPLOYMENT_HASH')
        super().__init__(read_json(path));object.__setattr__(self,'path',str(path));object.__setattr__(self,'file_sha256',expected_sha256)
    def get(self,key,default=None):return __import__('json').loads(self._encoded).get(key,default)
    def export(self):return __import__('json').loads(self._encoded)

def host_identity(root,expected):
    for filename,value in expected.items():
        if sha(Path(root)/filename)!=value:raise PermissionError('HOST_PRODUCTION_CODE_DRIFT:'+filename)

def complete_code_identity(identity,host_root,target_root,controller_root):
    host_root=Path(host_root);freeze=read_json(host_root/'source_freeze.json')
    if set(identity)!={'source_sha256','target_code_sha256','controller_code_sha256','new_source_freeze_sha256'} or identity['new_source_freeze_sha256']!=sha(host_root/'source_freeze.json') or identity['source_sha256']!=freeze['source_sha256']:raise PermissionError('EXACT_HOST_CODE_FREEZE_ROSTER')
    host_identity(host_root,freeze['source_sha256'])
    frozen={'release_control.py':host_root.parent/'paper12_controls1/release_control.py','test_controller.py':host_root.parent/'paper12_controls1/test_controller.py','access_check.py':host_root.parent/'paper12_controls1/access_check.py','selection.py':host_root.parent/'paper12_predictive_v2/selection.py','native_analysis_check.py':host_root.parent/'paper12_custody1/native_analysis_check.py'}
    for name in ('glm','nulls','null_cache','mouse_statistics'):frozen[name+'.py']=host_root.parent/('paper12_predictive_v2/'+name+'.py')
    py={k:v for k,v in freeze['source_sha256'].items() if k.endswith('.py')};mathmap={name:sha(p) for name,p in frozen.items() if name in ('glm.py','nulls.py','null_cache.py','mouse_statistics.py')}
    for role,root in (('target',target_root),('controller',controller_root)):
        expected=dict(py,**{name:sha(p) for name,p in frozen.items()});expected['worker.py']=py[role+'_worker.py'];expected['math_sources.json']=digest(canonical(mathmap)+b'\n');expected['bootstrap_manifest.json']=digest(canonical(expected)+b'\n')
        if identity[role+'_code_sha256']!=expected or {p.name for p in Path(root).iterdir() if p.is_file()}!=set(expected):raise PermissionError('EXACT_'+role.upper()+'_CODE_ROSTER')
        check_hashes(root,expected)

def preflight(deployment,verify_target):
    if not isinstance(deployment,RegisteredDeployment):raise PermissionError('REGISTERED_HOST_DEPLOYMENT_REQUIRED')
    # Authority_PENDING denies REAL before source resolution, D opens or consumption.
    public=trusted_public(deployment);binding=Path(deployment['binding_root']);anchor=read_json(deployment['anchor_path']);approval=read_json(deployment['approval_path'])
    if anchor['realm']!=deployment['realm'] or anchor['authority_public']!=public or anchor['mission']!=deployment['mission'] or anchor['base']!=deployment['base']:raise PermissionError('REGISTERED_DEPLOYMENT_TRUST_ROOT')
    if sha(deployment['anchor_path'])!=deployment['anchor_sha256']:raise PermissionError('REGISTERED_ANCHOR_HASH')
    body=verify_approval(approval,anchor,binding);verify_target(body['principal'])
    identity=read_json(binding/'code_identity.json');complete_code_identity(identity,Path(__file__).parent,deployment['target_code_root'],deployment['controller_code_root'])
    check_hashes(deployment['runtime_root'],read_json(binding/'runtime_identity.json')['runtime_sha256'])
    validate_catalog(binding,body)
    spec=read_json(binding/'analysis_spec.json')
    if spec['hypotheses']!=list(PRIMARY) or spec['Holm']!=4 or spec['bootstrap']!=10000 or spec['controls']!=4 or spec['replicates']!=999 or spec['one_assessment'] is not True:raise PermissionError('EXACT_ONE_SHOT_SPEC')
    return body,anchor

def consumption_proof(deployment,body,anchor,receipt):
    ledger=Path(deployment['ledger']);binding=digest(canonical(body));ident=body['authorization_id']
    if receipt['realm']!=body['realm'] or receipt['authorization_id']!=ident or receipt['binding']!=binding or receipt['principal']!=body['principal']:raise PermissionError('CONSUMPTION_RECEIPT_BINDING')
    genesis=read_json(ledger/'genesis.json')
    if digest(canonical(genesis))!=anchor['genesis_sha256']:raise PermissionError('BROKER_GENESIS')
    events=(ledger/'events.jsonl').read_bytes()
    if not events.endswith(b'\n'):raise PermissionError('BROKER_PARTIAL_LEDGER')
    lines=[__import__('json').loads(x) for x in events.splitlines()];previous=anchor['genesis_sha256']
    if len(lines)!=3:raise PermissionError('BROKER_EXACT_CONSUMPTION_STATES')
    for i,event in enumerate(lines):
        if event['sequence']!=i or event['previous']!=previous or event['state']!=('GENESIS','INTENT','CONSUMED')[i] or event['authorization_id']!=ident or event['binding']!=(anchor['genesis_sha256'] if i==0 else binding):raise PermissionError('BROKER_LEDGER_CHAIN')
        previous=digest(canonical(event))
    intent=read_json(ledger/'intent.json');used=read_json(ledger/'consumed.json');fence=read_json(Path(anchor['fence_root'])/(ident+'.json'))
    if any(x['binding']!=binding or x['authorization_id']!=ident for x in (intent,used,fence)) or previous!=receipt['ledger_tail'] or used['ledger_tail']!=previous:raise PermissionError('BROKER_DURABLE_CONSUMPTION_REQUIRED')

def revalidate_context(context,verify_target,require_delivery_fence=False):
    if not isinstance(context,VerifiedContext):raise PermissionError('VERIFIED_IMMUTABLE_CONTEXT_REQUIRED')
    d=RegisteredDeployment(context['deployment_path'],context['deployment_sha256']);body,anchor=preflight(d,verify_target);consumption_proof(d,body,anchor,context['consumed_receipt'])
    for key in ('realm','authorization_id','principal'):
        if context[key]!=body[key]:raise PermissionError('PRODUCER_CONTEXT_BINDING')
    if context['binding']!=digest(canonical(body)) or context['C_manifest_sha256']!=body['C_manifest_sha256'] or context['partition_sha256']!=body['partition_sha256']:raise PermissionError('PRODUCER_ARTIFACT_CONTEXT')
    if any(context[k]!=d[k] for k in ('binding_root','job_root','source_root','delivery_root')) or context['code_sha256']!=sha(Path(d['binding_root'])/'code_identity.json'):raise PermissionError('PRODUCER_CONTEXT_PATHS')
    if require_delivery_fence:
        started=read_json(Path(d['ledger'])/'delivery_started.json')
        if started['binding']!=context['binding'] or started['principal']!=body['principal'] or started['authorization_id']!=body['authorization_id']:raise PermissionError('DELIVERY_FENCE_REQUIRED')
    return body

def deliver(deployment,receipt,verify_target,protect,grant,hook=lambda point:None):
    body,anchor=preflight(deployment,verify_target);consumption_proof(deployment,body,anchor,receipt)
    ledger=Path(deployment['ledger']);bound=digest(canonical(body))
    # Exclusive creation permanently poisons delivery after every interruption.
    new(ledger/'delivery_started.json',{'authorization_id':body['authorization_id'],'binding':bound,'principal':body['principal']});hook('after_delivery_fence')
    context=VerifiedContext({'deployment_path':deployment.path,'deployment_sha256':deployment.file_sha256,'consumed_receipt':receipt,'realm':body['realm'],'authorization_id':body['authorization_id'],'binding':bound,'principal':body['principal'],'C_manifest_sha256':body['C_manifest_sha256'],'partition_sha256':body['partition_sha256'],'code_sha256':sha(Path(deployment['binding_root'])/'code_identity.json'),'binding_root':deployment['binding_root'],'job_root':deployment['job_root'],'source_root':deployment['source_root'],'delivery_root':deployment['delivery_root']})
    delivered=produce(context,verify_target,protect,hook)
    revalidate_context(context,verify_target,True)
    manifest=Path(deployment['delivery_root'])/'delivery_manifest.json'
    grant(Path(deployment['delivery_root']),body['principal']['package_sid'],False);hook('after_acl_grant')
    verify_target(body['principal'])
    completion={'realm':body['realm'],'authorization_id':body['authorization_id'],'binding':bound,'principal':body['principal'],'delivery_manifest_sha256':sha(manifest),'complete':True}
    new(ledger/'delivery_complete.json',completion)
    new(Path(deployment['target_data_root'])/'start_evaluation.json',dict(completion,expected={k:context[k] for k in ('realm','authorization_id','binding','principal','C_manifest_sha256','partition_sha256','code_sha256')}));hook('after_signal')
    return completion
