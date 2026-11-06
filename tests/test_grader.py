import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "graders"))
from grade_benchmark import grade


class GraderTests(unittest.TestCase):
    def load_example(self, filename):
        return json.loads((ROOT / "examples" / filename).read_text(encoding="utf-8"))

    def test_task1_reference_passes(self):
        self.assertTrue(grade(self.load_example("task1_answer.json"))["all_passed"])

    def test_task2_reference_passes(self):
        self.assertTrue(grade(self.load_example("task2_answer.json"))["all_passed"])

    def test_task1_wrong_factor_fails(self):
        answer = self.load_example("task1_answer.json")
        answer["factor"] = "Instrument"
        self.assertFalse(grade(answer)["checks"]["factor"]["pass"])

    def test_task1_outside_tolerance_fails(self):
        answer = self.load_example("task1_answer.json")
        answer["r2_before"] = 0.07
        self.assertFalse(grade(answer)["checks"]["r2_before"]["pass"])

    def test_missing_field_fails(self):
        answer = self.load_example("task2_answer.json")
        del answer["taxa"]["Acidaminococcus intestini"]["estimate"]
        self.assertFalse(grade(answer)["all_passed"])

    def test_nonfinite_and_boolean_rejected(self):
        answer = self.load_example("task1_answer.json")
        answer["r2_before"] = float("nan")
        answer["r2_after"] = True
        report = grade(answer)
        self.assertFalse(report["checks"]["r2_before"]["pass"])
        self.assertFalse(report["checks"]["r2_after"]["pass"])

    def test_ci_inconsistent_flag_fails(self):
        answer = self.load_example("task2_answer.json")
        answer["taxa"]["Fusobacterium nucleatum_J"]["ci_excludes_zero"] = False
        self.assertFalse(grade(answer)["checks"]["Fusobacterium nucleatum_J.interpretation_consistent"]["pass"])

    def test_ci_reversed_fails(self):
        answer = self.load_example("task2_answer.json")
        answer["taxa"]["Acidaminococcus intestini"]["ci_lower"] = 0.002410
        answer["taxa"]["Acidaminococcus intestini"]["ci_upper"] = -0.006650
        self.assertFalse(grade(answer)["checks"]["Acidaminococcus intestini.ci_order_valid"]["pass"])


if __name__ == "__main__":
    unittest.main()
