"""Materialize only the registered one-character mechanical transform."""
import difflib
import py_compile
import study as r
from register import candidate


def main():
    record=r.verify();original=(r.HERE/'original/m4_numerical_tests.py.txt').read_bytes()
    if r.hashlib.sha256(original).hexdigest()!=record['original_test_sha256']:raise RuntimeError('ORIGINAL_COPY_CHANGED')
    repaired=candidate(original)
    if len(repaired)!=len(original)+1 or r.hashlib.sha256(repaired).hexdigest()!=record['candidate_sha256']:
        raise RuntimeError('OUT_OF_SCOPE_PATCH')
    target=r.HERE/'patched';target.mkdir(exist_ok=False)
    path=target/'m4_numerical_tests.py'
    with path.open('xb') as f:f.write(repaired)
    diff=''.join(difflib.unified_diff(original.decode().splitlines(keepends=True),repaired.decode().splitlines(keepends=True),
        fromfile='original/m4_numerical_tests.py',tofile='patched/m4_numerical_tests.py'))
    (r.HERE/'source.diff').write_text(diff,encoding='utf-8',newline='')
    py_compile.compile(str(path),doraise=True)
    r.save(r.HERE/'results/syntax_receipt.json',dict(py_compile_pass=True,original_sha256=record['original_test_sha256'],
        repaired_sha256=r.sha(path),diff_sha256=r.sha(r.HERE/'source.diff'),byte_delta=1,source_requests=0,neural_access=False),True)
    print('ONE_BYTE_REPAIR; PY_COMPILE_PASS')


if __name__=='__main__':main()
