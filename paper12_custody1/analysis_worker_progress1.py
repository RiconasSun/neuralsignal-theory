"""Append-only smoke/small/full stage gates over the sealed original M3 runner."""
import ast
from pathlib import Path


def main():
    path = Path(__file__).with_name('analysis_worker.py')
    tree = ast.parse(path.read_text(encoding='utf-8'))
    body = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    loop = next(n for n in body.body if isinstance(n, ast.For) and isinstance(n.target, ast.Name) and n.target.id == 'session')
    hook = ast.parse('''
completed_sessions = list(dict.fromkeys(x['session_id'] for x in results))
if len(completed_sessions) in (1, 4):
    from stage_gate import assess
    stage = 'smoke' if len(completed_sessions) == 1 else 'small'
    stage_result = assess(results, completed_sessions)
    stage_result['stage'] = stage
    (output / ('stage_' + stage + '.json')).write_text(json.dumps(stage_result, indent=2), encoding='utf-8')
    if stage_result['gate'] != 'PASS':
        stage_result['full_cohort_execution'] = False
        stage_result['reason'] = 'MANDATORY_BASELINE_NO_VALID_CONFIG_WITH_ALL_SEEDS'
        (output / 'gate_result.json').write_text(json.dumps(stage_result, indent=2), encoding='utf-8')
        sys.exit(2)
''').body
    loop.body.extend(hook)
    namespace = dict(__file__=str(path), __name__='p12_progressive_worker')
    exec(compile(ast.fix_missing_locations(tree), str(path), 'exec'), namespace)
    namespace['main']()


if __name__ == '__main__':
    main()
