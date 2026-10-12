"""Read-only reuse of archived exact-forward/causal recurrence mathematics.

This module does not authorize a P12 fit policy or select an offset recipe.
It imports archived source without changing any P11 file.
"""
import importlib.util
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parent.parent / 'paper11_v2/scripts'
path = SCRIPTS / 'predictive_models.py'
spec = importlib.util.spec_from_file_location('p12_archived_predictive_math', path)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

# The append-only recurrence repair imports the original module by its name.
previous = sys.modules.get('predictive_models')
sys.modules['predictive_models'] = core
try:
    path = SCRIPTS / 'predictive_models_code1.py'
    spec = importlib.util.spec_from_file_location('p12_archived_recurrence_math', path)
    corrected = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(corrected)
finally:
    if previous is None:
        del sys.modules['predictive_models']
    else:
        sys.modules['predictive_models'] = previous

StatePoisson = core.StatePoisson
RecurrentPoisson = corrected.RecurrentPoisson
