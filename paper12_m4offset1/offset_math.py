"""Same frozen29-feature definition; no validation fit or neural-history covariate."""
import hashlib
import numpy as np
from baseline_features import design,training_scaler,transform


def features(y,conditions,orders):
    raw=np.concatenate((design(y,conditions,orders,'event'),design(y,conditions,orders,'drift')[...,1:]),axis=-1)
    if raw.shape[-1]!=29:raise RuntimeError('FROZEN_29_FEATURES_REQUIRED')
    return transform(raw,training_scaler(raw))


def array_sha(y):return hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest()
