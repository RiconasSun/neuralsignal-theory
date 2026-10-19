"""Post-inspection regression of the observed storage mismatch, synthetic only."""
from pathlib import Path
import tempfile
import unittest

from .links import ALIAS, Inspector, LinkProblem, no_dataset_values
from .test_diagnostic import WORK, PATHS, fixture


class SavedEvidenceTests(unittest.TestCase):
    def test_float32_rotation_with_valid_alias_units_and_shapes_is_schema_failure(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            with fixture(str(Path(tmp)/'float32_rotation.h5')) as file:
                path = '/processing/running/running_wheel_rotation/data'
                del file[path]
                rotation = file.create_dataset(path, shape=(2,), dtype='float32')
                rotation.attrs['unit'] = 'radians'
                rotation.attrs['conversion'] = 1.
                with no_dataset_values() as canary:
                    inspector = Inspector(file)
                    with self.assertRaises(LinkProblem) as caught:
                        inspector.run(PATHS)
                    self.assertEqual((caught.exception.kind, caught.exception.path), ('SCHEMA', ALIAS))
                    self.assertEqual(caught.exception.detail, 'Native binary64/vector metadata contradicts contract')
                    self.assertEqual(inspector.objects[path]['dtype'], '<f4')
                    self.assertEqual(canary['forbidden_value_calls'], 0)
