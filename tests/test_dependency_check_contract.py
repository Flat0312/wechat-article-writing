from __future__ import annotations

import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / 'scripts'))


class DependencyCheckContractTests(unittest.TestCase):
    @staticmethod
    def _discovered(*names: str):
        return {name: Path("C:/skills") / name for name in names}

    @staticmethod
    def _cli_env(tmpdir: str):
        cli = Path(tmpdir) / "opencli.exe"
        cli.write_text("stub", encoding="utf-8")
        return {"OPENCLI_BIN": str(cli)}

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
            result["missing_required"],
            [
                "creator-buddy",
                "gzh-explosive-content-detector",
                "global-content-search",
            ],
        )

    def test_topic_reports_missing_optional_cli_without_blocking_fallbacks(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "topic",
            self._discovered(
                "cheat-on-content",
                "creator-buddy",
                "gzh-explosive-content-detector",
                "global-content-search",
            ),
            env={"OPENCLI_BIN": "C:/missing/opencli.exe"},
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["cli_runtime"]["missing_required"], [])
        self.assertEqual(
            result["cli_runtime"]["missing_optional"], ["opencli"]
        )
        self.assertIn("global-content-search", result["skill_presence"]["available"])

    def test_pipeline_stage_aliases_are_explicit(self):
        import dependency_check

        self.assertEqual(dependency_check.STAGE_ALIASES["brief"], "strategy")
        self.assertEqual(dependency_check.STAGE_ALIASES["evidence"], "topic")
        self.assertEqual(dependency_check.STAGE_ALIASES["prediction"], "publish")
        self.assertEqual(dependency_check.STAGE_ALIASES["visual_plan"], "visual")
        result = dependency_check.check_dependencies(
            "prediction", self._discovered("cheat-on-content")
        )
        self.assertEqual(result["resolved_stage"], "publish")

    def test_publish_stage_passes_with_only_cheat(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "publish", self._discovered("cheat-on-content")
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["optional_missing"], [])
        self.assertEqual(result["script_runtime"]["required"], [])
        self.assertEqual(result["script_runtime"]["missing_required"], [])

    def test_writing_requires_only_human_writing(self):
        import dependency_check

        missing = dependency_check.check_dependencies("writing", self._discovered())
        self.assertEqual(missing["missing_required"], ["human-writing"])
        ready = dependency_check.check_dependencies(
            "writing", self._discovered("human-writing")
        )
        self.assertTrue(ready["ok"])

    def test_editing_requires_human_writing_and_keeps_humanizer_optional(self):
        import dependency_check

        result = dependency_check.check_dependencies("editing", self._discovered())
        self.assertFalse(result["ok"])
        self.assertEqual(result["missing_required"], ["human-writing"])
        self.assertEqual(result["optional_missing"], ["humanizer-zh"])

    def test_topic_reports_script_import_runtime_separately(self):
        import dependency_check

        discovered = self._discovered(
            "cheat-on-content",
            "creator-buddy",
            "gzh-explosive-content-detector",
            "global-content-search",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(dependency_check.importlib.util, "find_spec", return_value=None):
                result = dependency_check.check_dependencies(
                    "topic", discovered, env=self._cli_env(tmpdir)
                )
        self.assertFalse(result["ok"])
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["cli_runtime"]["missing_required"], [])
        self.assertIn(
            "gzh-explosive-content-detector:requests",
            result["script_runtime"]["missing_required"],
        )
        self.assertIn(
            "requests", result["script_runtime"]["checks"]["gzh-explosive-content-detector"]["imports"]
        )

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

    def test_news_card_stage_requires_registered_signals_and_cover(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "news-card",
            self._discovered(
                "cheat-on-content",
                "creator-buddy",
                "gzh-explosive-content-detector",
                "wechat-content-strategy",
            ),
            env={"OPENCLI_BIN": "C:/missing/opencli.exe"},
        )
        self.assertFalse(result["ok"])
        self.assertEqual(
            result["missing_required"], ["global-content-search"]
        )
        self.assertEqual(
            result["missing_any"],
            [["guizang-social-card-skill", "imagegen"]],
        )

    def test_news_card_stage_passes_with_registered_signals(self):
        import dependency_check

        with tempfile.TemporaryDirectory() as tmpdir:
            result = dependency_check.check_dependencies(
                "news-card",
                self._discovered(
                    "cheat-on-content",
                    "creator-buddy",
                    "gzh-explosive-content-detector",
                    "wechat-content-strategy",
                    "global-content-search",
                    "guizang-social-card-skill",
                ),
                env=self._cli_env(tmpdir),
            )
        self.assertTrue(result["ok"])
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["missing_any"], [])
        self.assertEqual(result["optional_missing"], [])

    def test_news_card_stage_accepts_imagegen_as_cover_fallback(self):
        import dependency_check

        with tempfile.TemporaryDirectory() as tmpdir:
            result = dependency_check.check_dependencies(
                "news-card",
                self._discovered(
                    "cheat-on-content",
                    "creator-buddy",
                    "gzh-explosive-content-detector",
                    "wechat-content-strategy",
                    "global-content-search",
                    "imagegen",
                ),
                env=self._cli_env(tmpdir),
            )
        self.assertTrue(result["ok"])
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["missing_any"], [])

    def test_news_card_ai_stage_requires_aihot(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "news-card-ai",
            self._discovered(
                "cheat-on-content",
                "creator-buddy",
                "gzh-explosive-content-detector",
                "wechat-content-strategy",
                "global-content-search",
                "guizang-social-card-skill",
            ),
            env={"OPENCLI_BIN": "C:/missing/opencli.exe"},
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["missing_required"], ["aihot"])

    def test_news_card_ai_stage_passes_with_aihot(self):
        import dependency_check

        with tempfile.TemporaryDirectory() as tmpdir:
            result = dependency_check.check_dependencies(
                "news-card-ai",
                self._discovered(
                    "cheat-on-content",
                    "creator-buddy",
                    "gzh-explosive-content-detector",
                    "wechat-content-strategy",
                    "aihot",
                    "global-content-search",
                    "imagegen",
                ),
                env=self._cli_env(tmpdir),
            )
        self.assertTrue(result["ok"])
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["missing_any"], [])
        self.assertEqual(result["optional_missing"], [])


if __name__ == "__main__":
    unittest.main()
