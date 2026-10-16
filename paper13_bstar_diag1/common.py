"""Identity-bound development-E prefix inputs; no source or final-data reader."""
import hashlib
import json
from pathlib import Path
import numpy as np

P = Path(__file__).resolve().parent
ROOT = P.parent
OLD = ROOT / 'paper13_ki_execution1'
E = ROOT / 'ops/evidence/2026-10-16/p13-bstar-conditional-null-diagnosis-1'
MICE = ['147465', '152417', '152419', '156130']
BASE = 'c7ae3d4753f94ba50134d1f15a4a62dcb101d842'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def identities():
    freeze = read(P / 'INPUT_FREEZE.json')
    assert freeze['base'] == BASE and freeze['prefix_mouse_order'] == MICE
    for name, digest in freeze['hashes'].items():
        assert sha(ROOT / name) == digest, name
    for path in [OLD / 'M6_E_IMPLEMENTATION_FREEZE_r2.json', ROOT / 'paper13_ki_pl_contract1/FREEZE_r2.json']:
        for name, digest in read(path)['hashes'].items():
            assert sha(ROOT / name) == digest, name
    assert read(OLD / 'results/M6_E_CONTROLS_GATE.json')['M6_E_CONTROLS'] == 'FAIL'
    assert not (OLD / 'results/final_C').exists() and not (OLD / 'results/final_D').exists()
    assert not (OLD / 'FINAL_C_APPROVAL.json').exists() and not (OLD / 'FINAL_D_APPROVAL.json').exists()
    return freeze


def load_mouse(mouse):
    if mouse not in MICE:
        raise PermissionError('Only original four-mouse development-E diagnostic prefix')
    from paper13_ki_execution1.features import nuisance
    rows = read(OLD / 'EPOCH_UNIT_ALLOCATION.json')['records']
    record = next(r for r in rows if r['mouse_id'] == mouse)
    assert record['role'] == 'development'
    epochs = [r for r in record['epochs'] if r['partition'] == 'E']
    export = read(OLD / 'results/exploratory_E' / (mouse + '.json'))
    assert export['partition'] == 'E' and export['mouse_id'] == mouse
    m5 = read(OLD / 'results/M5_EXPLORATORY_RESULTS.json')
    model_path = OLD / 'results/development_models' / (mouse + '.json')
    state = ROOT / export['state_file']
    identity = m5['model_state_identities'][mouse]
    assert sha(model_path) == identity['model_bundle_sha256']
    assert sha(state) == identity['E_state_sha256']
    with np.load(state, allow_pickle=False) as arrays:
        y = arrays['counts'].copy()
        unit_ids = arrays['unit_ids'].copy()
    assert y.shape == (30, 30, 8) and len(epochs) == 30
    assert np.issubdtype(y.dtype, np.integer) and np.all(y >= 0)
    assert unit_ids.tolist() == export['unit_ids']
    return y, nuisance(record, epochs), read(model_path), [r['ordinal'] for r in epochs], unit_ids


def manual_B2(y, bundle):
    """Independent scalar-loop lag construction and coefficient decomposition."""
    y = np.asarray(y)
    epochs, bins, units = y.shape
    raw = np.ones((epochs, bins, units, 4))
    for epoch in range(epochs):
        for t in range(bins):
            for unit in range(units):
                for k, lags in enumerate(((1,), (2, 3), (4, 5)), 1):
                    raw[epoch, t, unit, k] = sum(float(y[epoch, t-lag, unit]) for lag in lags if t >= lag)
    scale = bundle['baseline_scalers']['B2']
    mean, sd = np.asarray(scale['mean']), np.asarray(scale['sd'])
    theta = np.asarray(bundle['baseline_thetas']['B2']).reshape(8, 4)
    standardized = np.divide(raw-mean, sd, out=np.zeros_like(raw), where=sd != 0)
    terms = standardized * theta
    eta = np.sum(terms, axis=-1)
    beta = np.divide(theta, sd, out=np.zeros_like(theta), where=sd != 0)
    intercept = beta[:, 0] - np.sum(beta[:, 1:] * mean[:, 1:], axis=1)
    return raw, terms, eta, beta, intercept
