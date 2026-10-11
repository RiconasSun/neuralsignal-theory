"""Independent controlled-sequence quadrature; never experimental findings."""
import itertools
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.special import gammaln
import guided_poisson_filter as guided
import run_m4_amendment1 as previous

PAPER = previous.PAPER
OUTPUT = PAPER / 'results/M4_amendment2'


def fixture(states=1):
    return {'family': 'continuous' if states == 1 else 'hybrid', 'dimension': 2, 'states': states,
            'initial': np.array([1.]) if states == 1 else np.array([.7, .3]),
            'transition': np.array([[1.]]) if states == 1 else np.array([[.8, .2], [.3, .7]]),
            'biases': np.zeros((states, 4)) + np.arange(states)[:, None] * .2,
            'dynamics': np.stack([np.array([[.35, .1], [-.1, .3]]) + np.eye(2) * .05*s for s in range(states)]),
            'loadings': np.array([[.3, -.15], [-.2, .25], [.1, .2], [-.25, -.1]])}


def quadrature(model, y, offsets, order):
    roots, weights = hermgauss(order)
    indices = np.asarray(list(itertools.product(range(order), repeat=model['dimension'])))
    nodes = np.sqrt(2) * roots[indices]
    base = np.prod(weights[indices] / np.sqrt(np.pi), axis=1)
    filtered, scores = None, []
    for t in range(len(y)):
        likes = []
        for state in range(model['states']):
            eta = offsets[t] + model['biases'][state] + nodes @ model['loadings'].T
            likes.append(np.exp(np.sum(y[t] * eta - np.exp(eta) - gammaln(y[t]+1), axis=1)))
        likes = np.asarray(likes)
        if t == 0:
            predicted = model['initial'][:, None] * base
        else:
            previous_by_next = model['transition'].T @ filtered
            predicted = np.empty_like(filtered)
            for state in range(model['states']):
                means = nodes @ model['dynamics'][state].T
                kernel = np.exp(means @ nodes.T - .5*np.sum(means**2, axis=1)[:, None])
                predicted[state] = base * (previous_by_next[state] @ kernel)
        unnormalized = predicted * likes
        evidence = unnormalized.sum()
        scores.append(np.log(evidence))
        filtered = unnormalized / evidence
    return np.asarray(scores)


def evaluate(unit_success):
    rows, errors = [], []
    if not unit_success:
        return rows, ['Proposal unit tests failed']
    for states in (1, 2):
        model = fixture(states)
        y = np.array([[0, 1, 0, 2], [1, 0, 2, 0], [0, 1, 1, 0]])
        offsets = np.full(y.shape, -1.)
        low, high = quadrature(model, y, offsets, 24), quadrature(model, y, offsets, 32)
        uncertainty = float(np.max(np.abs(high-low)) / y.shape[1])
        if uncertainty > 1e-6:
            return rows, [f'Quadrature oracle unresolved: K{states}']
        for seed in (1103, 2207, 3301, 4409, 5519, 6607, 7717, 8803):
            scores, diagnostic = guided.particle(model, y, offsets, 8192, seed)
            discrepancy = float(np.max(np.abs(scores-high)) / y.shape[1])
            rows.append({'fixture': f'controlled_K{states}_D2', 'seed': seed, 'particles': 8192,
                         'oracle_scores': high.tolist(), 'particle_scores': scores.tolist(),
                         'maximum_error_nats_unit_bin': discrepancy, 'oracle_budget_shift_nats_unit_bin': uncertainty,
                         'diagnostics': diagnostic})
            if discrepancy+uncertainty > .001:
                return rows, [f'Controlled sequence numerical oracle FAIL: K{states}/seed{seed}']
    return rows, errors


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(PAPER/'tests'), '-p', 'test_m4_num2.py', '-v'], capture_output=True, text=True)
    (OUTPUT/'oracle_tests.txt').write_text(tests.stdout+tests.stderr, encoding='utf-8')
    rows, errors = evaluate(tests.returncode == 0)
    audit = {'gate': 'FAIL' if errors else 'PASS', 'tests_exit_code': tests.returncode, 'errors': errors,
             'fixtures_not_experimental_findings': True, 'real_neural_data_access': False, 'rows': rows,
             'source_sha256': previous.digest(Path(__file__)),
             'proposal_sha256': previous.digest(PAPER/'scripts/guided_poisson_filter.py'),
             'tests_sha256': previous.digest(PAPER/'tests/test_m4_num2.py'), 'finished_at_utc': previous.now()}
    previous.write(OUTPUT/'numerical_oracle_audit.json', audit)
    print(json.dumps({'gate': audit['gate'], 'errors': errors, 'controlled_sequence_replicates': len(rows)}))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
