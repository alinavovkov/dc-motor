import unittest

from dc_motor.scenarios import default_scenarios, random_load, step_load


class ScenarioTest(unittest.TestCase):
    def test_default_scenarios_count(self):
        self.assertGreaterEqual(len(default_scenarios()), 10)

    def test_step_load(self):
        load = step_load(before=0.2, after=1.0, at=2.0)
        self.assertEqual(load(1.99), 0.2)
        self.assertEqual(load(2.0), 1.0)

    def test_random_load_is_deterministic(self):
        first = random_load(seed=4)
        second = random_load(seed=4)
        self.assertEqual(first(0.6), second(0.6))


if __name__ == "__main__":
    unittest.main()

