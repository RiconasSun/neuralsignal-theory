"""Verified original launcher with append-only progressive worker/output namespace."""
import ast
from datetime import datetime, timezone
import sys
import register as r
import launch_analysis as original


def verify_old():
    r.verify()
    record = r.load(r.HERE / 'development_registration.json')
    for name, digest in record['implementation_sha256'].items():
        if r.sha(r.HERE / name) != digest:
            raise RuntimeError('PREPARED_IMPLEMENTATION_CHANGED')


def main():
    verify_old()
    names = ('launch_progress1.py', 'analysis_worker_progress1.py', 'stage_gate.py', 'test_stage_gate.py')
    if '--register' in sys.argv:
        result = dict(utc=datetime.now(timezone.utc).isoformat(),
                      implementation_sha256={p: r.sha(r.HERE / p) for p in names},
                      original_registration_sha256=r.sha(r.HERE / 'development_registration.json'),
                      method_registration_sha256=r.sha(r.HERE / 'method_registration1.json'),
                      policy='Fixed metadata roster order: first eligible mouse smoke,first4 small,then all eligible development mice. All21baseline configs/all3seeds/bothregions at every admitted mouse. Stop if any mandatory baseline has no eligible config; no tuning or pruning of seeds.',
                      real_development_analysis_started=False, final_holdout_evaluated=False)
        r.save(r.HERE / 'progressive_registration1.json', result, True)
        print('PROGRESSIVE_IMPLEMENTATION_FROZEN_BEFORE_REAL_DEVELOPMENT_ANALYSIS')
        return
    registration = r.load(r.HERE / 'progressive_registration1.json')
    for name, digest in registration['implementation_sha256'].items():
        if r.sha(r.HERE / name) != digest:
            raise RuntimeError('PROGRESSIVE_IMPLEMENTATION_CHANGED')
    if registration['original_registration_sha256'] != r.sha(r.HERE / 'development_registration.json') or registration['method_registration_sha256'] != r.sha(r.HERE / 'method_registration1.json'):
        raise RuntimeError('PROGRESSIVE_POLICY_BINDING_CHANGED')
    tree = ast.parse((r.HERE / 'launch_analysis.py').read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    mapping = {'results/M3/native1': 'results/M3/progressive1',
               'results/M3/synthetic_native1': 'results/M3/synthetic_progress1',
               'results/M3/native_launch_receipt.json': 'results/M3/progressive_launch_receipt.json',
               'results/M3/synthetic_native_launch_receipt.json': 'results/M3/synthetic_progress_launch_receipt.json'}
    changed = []
    class Rewrite(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str) and node.value in mapping:
                changed.append(node.value); return ast.copy_location(ast.Constant(mapping[node.value]), node)
            return node
        def visit_BinOp(self, node):
            if isinstance(node.op, ast.Div) and isinstance(node.left, ast.Name) and node.left.id == 'code' and isinstance(node.right, ast.Constant) and node.right.value == 'analysis_worker.py':
                changed.append('worker_entrypoint')
                return ast.copy_location(ast.BinOp(left=node.left, op=node.op, right=ast.Constant('analysis_worker_progress1.py')), node)
            return self.generic_visit(node)
        def visit_For(self, node):
            if isinstance(node.target, ast.Name) and node.target.id == 'filename':
                if not isinstance(node.iter, ast.Tuple): raise RuntimeError('COPY_SCOPE_CHANGED')
                node.iter.elts.extend([ast.Constant('analysis_worker_progress1.py'), ast.Constant('stage_gate.py')])
                changed.append('worker_copy')
            return self.generic_visit(node)
    function = Rewrite().visit(function)
    if sorted(changed) != sorted(list(mapping) + ['worker_entrypoint', 'worker_copy']):
        raise RuntimeError('UNEXPECTED_PROGRESSIVE_PATCH_SCOPE')
    namespace = dict(vars(original))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])),
                 str(r.HERE / 'launch_analysis.py'), 'exec'), namespace)
    namespace['main']()


if __name__ == '__main__':
    main()
