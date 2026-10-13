"""Unchanged verified functions, with custody paths restricted to this new study."""
import importlib.util
import sys
import types
from pathlib import Path
import study as r


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


sys.path.append(str(r.OLD))
sys.path.append(str(r.ROOT / 'paper12_checkpoint1'))
security_original = module('resume_archived_security', r.ROOT / 'paper12_checkpoint1/custody_security.py')
atomic_original = module('resume_archived_atomic', r.ROOT / 'paper12_checkpoint1/atomic_checkpoint.py')


def clone(function, namespace):
    return types.FunctionType(function.__code__, namespace, function.__name__, function.__defaults__, function.__closure__)


security_globals = dict(vars(security_original))
security_globals['r'] = r
protect_globals = dict(security_original.protect.__globals__)
protect_globals['r'] = types.SimpleNamespace(HERE=r.HERE)
protect = clone(security_original.protect, protect_globals)
security_globals['protect'] = protect
check_path = clone(security_original.check_path, security_globals)
security_globals['check_path'] = check_path
check_acl = clone(security_original.check_acl, security_globals)
security_globals['check_acl'] = check_acl
prepare = clone(security_original.prepare, security_globals)
require_custodian = security_original.require_custodian
native_path = security_original.native_path
atomic_globals = dict(vars(atomic_original))
atomic_globals.update(r=r, check_path=check_path, check_acl=check_acl, prepare=prepare,
                      protect=protect, require_custodian=require_custodian)
durable_record = clone(atomic_original.durable_record, atomic_globals)
read = clone(atomic_original.read, atomic_globals)
# contextmanager retains its original generator code and wraps only scoped globals.
from contextlib import contextmanager
writer_lock = contextmanager(clone(atomic_original.writer_lock.__wrapped__, atomic_globals))
atomic_globals.update(durable_record=durable_record, read=read, writer_lock=writer_lock)
commit = clone(atomic_original.commit, atomic_globals)


def verify_parity():
    for actual, original in ((commit, atomic_original.commit), (read, atomic_original.read),
                              (durable_record, atomic_original.durable_record),
                              (writer_lock.__wrapped__, atomic_original.writer_lock.__wrapped__),
                              (check_path, security_original.check_path), (check_acl, security_original.check_acl),
                              (prepare, security_original.prepare), (protect, security_original.protect)):
        if actual.__code__ is not original.__code__:
            raise RuntimeError('VERIFIED_BYTECODE_CHANGED')
    return True
