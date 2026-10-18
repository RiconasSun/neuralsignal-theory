"""Independent saved synthetic-journal audit; no model, array-file or fit execution."""
import ast
import datetime
import hashlib
import json
import math
import socket
import sys
from pathlib import Path

import numpy as np

E = Path(__file__).resolve().parent
R = E.parents[3]
P = R / 'paper15_r1'


def denied(*args, **kwargs):
    raise AssertionError('No neural-array loading, network or numerical experiment')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def function_ast(path, name):
    tree = ast.parse(path.read_text(encoding='utf8'))
    return ast.dump(next(x for x in ast.walk(tree) if isinstance(x, ast.FunctionDef) and x.name == name), include_attributes=False)


def run():
    np.load = denied
    socket.create_connection = denied
    socket.socket.connect = denied
    receipt_path = E / 'M5_FULL_SYNTHETIC_CONTROL_INTEGRATION.json'
    original = read(receipt_path)
    assert original['fixture_seed'] == 150900 and original['epochs'] == 40
    assert original['units'] == 8 and original['bins_per_epoch'] == 20
    assert sha(E / 'synthetic_control_integration.py') == original['fixture_source_sha256']
    for name, value in original['source_hashes'].items():
        assert sha(P / name) == value, name
    for name, function in [('evaluation.py', 'run_controls'), ('evaluation_support.py', 'score'),
                           ('evaluation_support.py', 'control_arrays'), ('training.py', 'build_model')]:
        assert function_ast(P / name, function) == function_ast(R / 'paper15_dev' / name, function)
    pairs = [('B4', 'B1'), ('B4', 'B3'), ('B4', 'B2'), ('D', 'B4'), ('C', 'B4'), ('D', 'S')]
    summaries = {}
    total = family_outputs = 0
    for suite in ['N1', 'N2', 'N3', 'N4']:
        path = P / 'work/full_synthetic_reference_journals' / (suite + '.jsonl')
        assert sha(path) == original['suites'][suite]['journal_sha256']
        events = [json.loads(line) for line in path.read_text(encoding='utf8').splitlines()]
        assert len(events) == 2001 and events[0]['event'] == 'SUITE_STARTED'
        assert events[-1]['event'] == 'SUITE_COMPLETE' and events[-1]['replicates_completed'] == 999
        assert events[0]['subject'] == 'SYNTHETIC_ONLY_150900' and events[0]['suite'] == suite
        assert events[0]['coverage'] == dict(available=True, trial_ids=list(range(40)), epochs=40, total_epochs=40)
        assert [v['event'] for v in events[1:4]] == ['REPLICATE_STARTED', 'ORIGINAL_CONTROL_EXPOSURE', 'REPLICATE_COMPLETE']
        for replicate in range(1, 999):
            a, b = events[2 * replicate + 2:2 * replicate + 4]
            assert (a['event'], b['event']) == ('REPLICATE_STARTED', 'REPLICATE_COMPLETE')
            assert a['replicate'] == b['replicate'] == replicate
        starts = [v for v in events if v['event'] == 'REPLICATE_STARTED']
        done = [v for v in events if v['event'] == 'REPLICATE_COMPLETE']
        exposures = [v for v in events if v['event'] == 'ORIGINAL_CONTROL_EXPOSURE']
        assert len(starts) == len(done) == len({v['seed'] for v in starts}) == 999
        assert len(exposures) == 1
        families = {'B1', 'B4'} if suite == 'N3' else {'B1', 'B2', 'B3', 'B4', 'D', 'C', 'S'}

        def effects(models):
            assert set(models) == families and 'B0' not in models
            assert all(v['unit_bins'] == 3200 and math.isfinite(v['LL']) for v in models.values())
            return [(models[a]['LL'] - models[b]['LL']) / 3200 if a in models and b in models else None for a, b in pairs]

        exposure = exposures[0]
        assert exposure['trial_ids'] == list(range(40))
        observed = effects(exposure['models'])
        if suite == 'N3':
            observed = [exposure['models']['B4']['LL'] / 3200] * 6
        assert observed == original['suites'][suite]['original']
        for i, (start, item) in enumerate(zip(starts, done)):
            seed = int.from_bytes(hashlib.sha256(f'P15-M1|150107|{suite}|SYNTHETIC_ONLY_150900|E|{i}'.encode()).digest()[:8], 'big')
            assert start['replicate'] == item['replicate'] == i and start['seed'] == item['seed'] == seed
            rng = np.random.Generator(np.random.PCG64(seed))
            if suite == 'N1':
                mapping = dict(offsets=[dict(trial=t, offset=int(rng.integers(1, 20))) for t in range(40)], donors=None)
            else:
                if suite == 'N4':
                    indices = np.arange(40).reshape(8, 5)
                    donors = np.roll(indices, int(rng.integers(1, 8)), axis=0).ravel()
                else:
                    donors = np.empty(40, int)
                    for begin in [0, 20]:
                        donors[begin:begin + 20] = np.roll(np.arange(begin, begin + 20), int(rng.integers(1, 20)))
                mapping = dict(donors=[dict(target_trial=t, donor_trial=int(donors[t])) for t in range(40)])
            assert digest(mapping) == item['mapping_sha256']
            values = effects(item['models'])
            assert item['wheel_gain'] == (values[0] if suite == 'N3' else None)
            if suite == 'N3':
                values = [item['models']['B4']['LL'] / 3200] * 6
            assert values == item['reference_effects'] and all(math.isfinite(x) for x in values)
        panel = dict(status='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE', coverage=events[0]['coverage'], replicates_completed=999,
                     observed=observed, reference_effects=[v['reference_effects'] for v in done], original_model_scores=exposure['models'],
                     mapping_sha256=[v['mapping_sha256'] for v in done], seeds=[v['seed'] for v in done],
                     statistic='B4 LL/unit-bin wheel reliance diagnostic copied across contrast slots' if suite == 'N3' else 'Registered original-minus-comparator predictive gain',
                     wheel_gain_original=effects(exposure['models'])[0] if suite == 'N3' else None,
                     wheel_gain_reference=[v['wheel_gain'] for v in done] if suite == 'N3' else None,
                     original_targets_preserved=True, D_filter_assimilates_surrogate_past_counts=suite != 'N3',
                     exchangeability='Destructive reference, not exact mechanistic or population null; nuisance imbalance/stationarity limitations retained', A_matching_diagnostics={})
        assert digest(panel) == events[-1]['summary_sha256']
        total += len(done)
        family_outputs += len(done) * len(families)
        summaries[suite] = dict(journal_sha256=sha(path), events=2001, complete=999, families=len(families), unit_bins=3200,
                                all_seeds_mappings_arithmetic_verified=True, reconstructed_summary_sha256=digest(panel))
    assert total == original['replicate_bundles'] == 3996 and family_outputs == 22977
    result = dict(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1', reviewer='/root/gradient_review',
                  time=datetime.datetime.now(datetime.timezone.utc).isoformat(), status='SAVED_SYNTHETIC_JOURNAL_REVIEW_PASS',
                  replicate_bundles=total, family_outputs=family_outputs, suites=summaries,
                  integration_receipt_sha256=sha(receipt_path), fixture_source_sha256=original['fixture_source_sha256'],
                  source_hashes=original['source_hashes'], diagnostic_script_sha256=sha(Path(__file__)),
                  review_runtime=dict(python=sys.version, executable_sha256=sha(Path(sys.executable)), numpy=np.__version__),
                  fixture_rerun=False, likelihood_evaluations=0, real_fits=0, real_neural_arrays=False, B_E_Final_access=False,
                  scope='Saved four synthetic journals, independently regenerated mapping metadata and scalar arithmetic; no real-cohort or E admission certificate')
    target = E / 'FULL_SYNTHETIC_CONTROL_REVIEW_R1_RECEIPT.json'
    assert not target.exists()
    target.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf8')
    print('PASS: 3996 seeds/mappings/effects,22977 family outputs, four reconstructed complete-summary hashes; no likelihood/fit/array access')
    print('review_receipt_sha256=' + sha(target))


if __name__ == '__main__':
    run()
