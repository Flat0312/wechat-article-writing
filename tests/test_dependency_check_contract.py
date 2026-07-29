from __future__ import annotations

import unittest
from pathlib import Path


class DependencyCheckContractTests(unittest.TestCase):
    @staticmethod
    def _discovered(*names: str):
        return {name: Path("C:/skills") / name for name in names}

    def test_unknown_stage_raises(self):
        import dependency_check

        with self.assertRaises(ValueError):
            dependency_check.check_dependencies("ghost", {})

    def test_topic_stage_requires_explicit_creator_buddy_branch(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "topic", self._discovered("cheat-on-content")
        )
        self.assertFalse(result["ok"])
        self.assertEqual(
            result["missing_required"], ["creator-buddy", "gzh-explosive-content-detector"]
        )

    def test_publish_stage_passes_with_only_cheat(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "publish", self._discovered("cheat-on-content")
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["optional_missing"], [])

    def test_visual_any_route_reports_missing_routes_and_generator(self):
        import dependency_check

        result = dependency_check.check_dependencies("visual", self._discovered())
        self.assertFalse(result["ok"])
        self.assertEqual(result["runtime"]["ready_routes"], [])
        self.assertEqual(
            result["missing_any"],
            [["ian-xiaohei-illustrations", "baoyu-article-illustrator"]],
        )
        self.assertEqual(result["optional_missing"], ["imagegen"])
        self.assertEqual(result["runtime"]["missing_imagegen"], ["imagegen"])

    def test_visual_any_route_reports_missing_routes_with_generator(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "visual", self._discovered("imagegen")
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["runtime"]["ready_routes"], [])
        self.assertEqual(
            result["missing_any"],
            [["ian-xiaohei-illustrations", "baoyu-article-illustrator"]],
        )
        self.assertEqual(result["optional_missing"], [])
        self.assertEqual(result["runtime"]["missing_imagegen"], [])

    def test_visual_any_route_passes_with_one_route_and_generator(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "visual",
            self._discovered("ian-xiaohei-illustrations", "imagegen"),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["runtime"]["ready_routes"], ["ian"])
        self.assertEqual(result["missing_any"], [])
        self.assertEqual(result["optional_missing"], [])
        self.assertEqual(result["runtime"]["missing_imagegen"], [])

    def test_visual_any_route_passes_without_optional_imagegen_skill(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "visual", self._discovered("ian-xiaohei-illustrations")
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["runtime"]["ready_routes"], ["ian"])
        self.assertEqual(result["missing_any"], [])
        self.assertEqual(result["optional_missing"], ["imagegen"])
        self.assertEqual(result["runtime"]["missing_imagegen"], ["imagegen"])

    def test_selected_visual_route_requires_only_its_route_skill(self):
        import dependency_check

        ian = dependency_check.check_dependencies(
            "visual-ian", self._discovered("ian-xiaohei-illustrations")
        )
        structured = dependency_check.check_dependencies(
            "visual-structured", self._discovered("ian-xiaohei-illustrations")
        )
        self.assertTrue(ian["ok"])
        self.assertEqual(ian["optional_missing"], ["imagegen"])
        self.assertFalse(structured["ok"])
        self.assertEqual(
            structured["missing_required"], ["baoyu-article-illustrator"]
        )


if __name__ == "__main__":
    unittest.main()
