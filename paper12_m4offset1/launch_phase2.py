"""Enforced source/state/record guards, preserving registered v1 code unchanged."""
import ast
import shutil
import sys
import study as r
import launch_phase as old


def main():
    phase=sys.argv[1]
    if phase not in ('smoke','small','full'):raise RuntimeError('DIAGNOSIS_USES_REGISTERED_V1')
    r.verify();guard=r.load(r.HERE/'guard_registration.json')
    for name,digest in guard['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('GUARD_IMPLEMENTATION_CHANGED')
    from amend import OLD,NEW
    amendment=r.load(r.HERE/'optimizer_amendment.json');patched=r.HERE/'patched/task_offset.py'
    original=(r.PREVIOUS/'task_offset.py').read_bytes()
    if original.count(OLD)!=1 or patched.read_bytes()!=original.replace(OLD,NEW,1) or r.sha(patched)!=amendment['amended_offset_source_sha256']:
        raise RuntimeError('EXACT_OFFSET_OPTIONS_ONLY_AMENDMENT_REQUIRED')
    previous={'smoke':'diagnosis','small':'smoke','full':'small'}[phase];old.completed(previous)
    if previous!='diagnosis':
        gate=r.load(r.HERE/f'results/{previous}/native/gate_result.json')
        if r.sha(r.HERE/f'results/{previous}/native/offset_records.json')!=gate['records_sha256'] or r.sha(r.HERE/f'results/{previous}/native/summary.json')!=gate['summary_sha256']:
            raise RuntimeError('PRECEDING_OFFSET_RECORDS_CHANGED')
    tree=ast.parse((r.HERE/'launch_phase.py').read_text());body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    code=ast.unparse(body)
    needle="for name, path in sources.items():"
    if code.count(needle)!=1:raise RuntimeError('SOURCE_COPY_GUARD_LOCATION')
    code=code.replace(needle,"sources['worker.py'] = r.HERE/'worker2.py'\n    sources['worker_v1.py'] = r.HERE/'worker.py'\n    sources['roster_guard.py'] = r.HERE/'roster_guard.py'\n    "+needle,1)
    needle="policy['reuse_states_sha256'] = r.sha(source)"
    if code.count(needle)!=1:raise RuntimeError('RECORD_COPY_GUARD_LOCATION')
    code=code.replace(needle,needle+"\n        policy['reuse_records_sha256'] = r.sha(code/'reuse_records.json')",1)
    ns=dict(vars(old));exec(compile(code,__file__,'exec'),ns);ns['main']()


if __name__=='__main__':main()
