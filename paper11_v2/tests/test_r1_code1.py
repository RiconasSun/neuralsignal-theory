"""Run all unchanged original assertions against the registered repaired model."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import predictive_models_code1 as repaired
import test_r1_models as original_tests
import test_r1_runner as runner_tests

repaired.original.RecurrentPoisson = repaired.RecurrentPoisson
original_tests.models = repaired.original
TEST_TEMP = Path(__file__).resolve().parents[1] / 'results/R1_code1/test_tmp'
TEST_TEMP.mkdir(parents=True, exist_ok=True)
tempfile.tempdir = str(TEST_TEMP)
ModelTests = original_tests.ModelTests
RunnerTests = runner_tests.RunnerTests


class DeterminismTests(unittest.TestCase):
    def test_batch_permutation_and_single_trial_identical(self):
        y, x, offset = original_tests.fixture()
        for dim in [1,2,4]:
            model = repaired.RecurrentPoisson(y, x, offset, dim)
            theta = model.initial(23)
            expected = model.log_means(theta)
            for index in [0,1]:
                single = repaired.RecurrentPoisson(y[index:index+1], x[index:index+1], offset[index:index+1], dim)
                original_tests.np.testing.assert_array_equal(expected[index:index+1], single.log_means(theta))
            permuted = repaired.RecurrentPoisson(y[::-1], x[::-1], offset[::-1], dim)
            original_tests.np.testing.assert_array_equal(expected[::-1], permuted.log_means(theta))


if __name__ == '__main__':
    unittest.main()
