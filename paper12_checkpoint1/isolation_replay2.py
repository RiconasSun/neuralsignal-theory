"""Explicitly bind the existing exact-history guard through the nested harness."""
import types
import study as r
import isolation
from history_guard import verify


def adapted():
    namespace=dict(isolation.main.__globals__)
    proxy=types.SimpleNamespace(**vars(r));proxy.verify=verify
    namespace['r']=proxy
    return types.FunctionType(isolation.main.__code__,namespace)


if __name__=='__main__':adapted()()
