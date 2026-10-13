"""Rebuild public table without overwriting the audited live scientific gate."""
import types
import study as r
import summarize


def main():
    namespace=dict(summarize.main.__globals__)
    proxy=types.SimpleNamespace(**vars(r))
    def save(path,value,exclusive=False):
        if path==r.HERE/'results/M2/gate_result.json':path=r.HERE/'replay/reconstructed_M2_gate.json'
        r.save(path,value,exclusive)
    proxy.save=save;namespace['r']=proxy
    types.FunctionType(summarize.main.__code__,namespace)()


if __name__=='__main__':main()
