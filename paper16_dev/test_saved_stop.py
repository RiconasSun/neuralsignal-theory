from pathlib import Path
import tempfile
import unittest
import json
import h5py
import numpy as np
import requests
from .source_running import hard_object


class Tests(unittest.TestCase):
    def test_current_link_rejection_is_not_actual_type_diagnosis(self):
        # All three distinct representations fail the same guard. This is why
        # the saved traceback alone cannot identify the actual native link.
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent/'work') as tmp:
            for kind in ['missing', 'soft', 'external']:
                with h5py.File(str(Path(tmp)/'canary.h5'),'w',driver='core',backing_store=False) as f:
                    f.create_group('/processing/running/running_wheel_rotation')
                    target='/processing/running/running_wheel_rotation/timestamps'
                    if kind == 'soft': f[target]=h5py.SoftLink('/processing/running/running_speed/timestamps')
                    if kind == 'external': f[target]=h5py.ExternalLink('never_open_real.nwb','/timestamps')
                    with self.assertRaisesRegex(ValueError,'External/soft/noncanonical source link denied'):
                        hard_object(f,target)

    def test_saved_scope_denies_native_neural_and_network_and_worker(self):
        from .verify_saved import saved_scope
        import subprocess,sys
        with saved_scope():
            for fn in [lambda:requests.get('https://example.invalid'),lambda:np.load('never_read_counts.npy'),
                       lambda:h5py.File('never_open_source.nwb','r'),
                       lambda:subprocess.Popen([sys.executable,'-m','paper16_dev.source_running'])]:
                with self.assertRaises(RuntimeError): fn()


if __name__ == '__main__':
    unittest.main()
