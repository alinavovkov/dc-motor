import unittest

import numpy as np

from dc_motor.metrics import mae, rmse, step_info


class MetricsTest(unittest.TestCase):
    def test_error_metrics(self):
        actual = np.array([1.0, 2.0, 3.0])
        expected = np.array([1.0, 1.0, 5.0])
        self.assertAlmostEqual(mae(actual, expected), 1.0)
        self.assertAlmostEqual(rmse(actual, expected), np.sqrt(5.0 / 3.0))

    def test_step_info(self):
        t = np.linspace(0.0, 1.0, 11)
        y = np.array([0, 1, 3, 6, 9, 10.5, 10.1, 10.0, 10.0, 10.0, 10.0])
        reference = np.full_like(t, 10.0)
        info = step_info(t, y, reference)
        self.assertAlmostEqual(info["rise_time"], 0.3)
        self.assertAlmostEqual(info["overshoot_percent"], 5.0)
        self.assertAlmostEqual(info["settling_time"], 0.6)


if __name__ == "__main__":
    unittest.main()
