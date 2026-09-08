from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
HAS_DEPS = importlib.util.find_spec("numpy") is not None and importlib.util.find_spec("openpyxl") is not None


@unittest.skipUnless(HAS_DEPS, "C题实验的可选依赖未安装")
class CProblemExperimentTests(unittest.TestCase):
    def test_week_parser(self) -> None:
        from c_problem_experiment import week_num

        self.assertAlmostEqual(week_num("11w+6"), 11 + 6 / 7)
        self.assertEqual(week_num("14w"), 14.0)

    def test_binary_metrics(self) -> None:
        import numpy as np
        from c_problem_experiment import classification_metrics

        result = classification_metrics(np.array([0, 0, 1, 1]), np.array([0.1, 0.3, 0.7, 0.9]), 0.5)
        self.assertEqual(result["balanced_accuracy"], 1.0)
        self.assertEqual(result["pr_auc"], 1.0)

    def test_group_split_keeps_subject_together(self) -> None:
        import numpy as np
        from c_problem_experiment import group_folds

        groups = np.array(["A", "A", "B", "C", "C", "D"])
        masks = group_folds(groups, 2, 7)
        for mask in masks:
            for subject in set(groups.tolist()):
                positions = mask[groups == subject]
                self.assertTrue(np.all(positions) or np.all(~positions))


if __name__ == "__main__":
    unittest.main()
