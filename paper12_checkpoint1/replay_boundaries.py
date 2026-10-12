"""Same registered fixture code, exactly one output constant relocated for replay."""
import sys
import types
from pathlib import Path
import study as r
import boundary_cases
from custody_security import check_path


def main():
    output=check_path(Path(sys.argv[1])).relative_to(r.HERE).as_posix()
    saved=r.load(r.HERE/'results/boundaries.json')
    if saved['code_sha256']!=r.sha(r.HERE/'boundary_cases.py'):raise RuntimeError('BOUNDARY_CODE_CHANGED')
    old=boundary_cases.main
    if old.__code__.co_consts.count('results/boundaries.json')!=1:raise RuntimeError('BOUNDARY_REPLAY_SCOPE')
    code=old.__code__.replace(co_consts=tuple(output if x=='results/boundaries.json' else x for x in old.__code__.co_consts))
    types.FunctionType(code,old.__globals__)()


if __name__=='__main__':main()
