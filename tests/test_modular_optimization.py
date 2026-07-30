from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
COMPANION_ROOT = SKILL_ROOT / "companion-skills"
STYLE_ROOT = COMPANION_ROOT / "wechat-style-learning"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import profile_adapter
import dependency_check
import validate_project


def _load_edit_learning():
    path = STYLE_ROOT / "scripts" / "edit_learning.py"
    spec = importlib.util.spec_from_file_location("edit_learning", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


edit_learning = _load_edit_learning()


class ModularOptimizationTests(unittest.TestCase):
    def test_first_party_companion_skills_are_bundled(self):
        for name in ("wechat-content-strategy", "wechat-style-learning"):
            root = COMPANION_ROOT / name
            self.assertTrue((root / "SKILL.md").is_file())
            self.assertTrue((root / "agents" / "openai.yaml").is_file())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cheat = self.root / "cheat"
        self.cheat.mkdir()
        (self.cheat / ".cheat-state.json").write_text("{}\n", encoding="utf-8")
        self.profile = self.root / "profile"
        profile_adapter.create_profile(
            self.profile, "test-account", self.cheat, approved=True
        )

    def tearDown(self):
        self.temp.cleanup()

    def _pair(self, suffix: str, final_extra: str = "更短。"):
        draft = self.root / f"draft-{suffix}.md"
        final = self.root / f"final-{suffix}.md"
        draft.write_text("# 标题\n\n这是一个比较长的原始段落。\n", encoding="utf-8")
        final.write_text(f"# 标题\n\n{final_extra}\n", encoding="utf-8")
        return draft, final

    def _record(self, suffix: str, timestamp: datetime):
        draft, final = self._pair(suffix, f"更短。{suffix}")
        return edit_learning.record_lesson(
            self.profile,
            draft,
            final,
            f"article-{suffix}",
            [
                {
                    "key": "shorter_paragraphs",
                    "type": "rhythm",
                    "instruction": "在高密度信息后缩短段落。",
                }
            ],
            approved=True,
            timestamp=timestamp,
        )

    def test_new_profile_initializes_optional_edit_ledger(self):
        index = json.loads(
            (self.profile / "history" / "edits" / "index.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(index, {"schema_version": "1.0", "items": []})
        self.assertEqual(validate_project.validate_profile(self.profile), [])

    def test_first_confirmed_learning_is_provisional_and_body_free(self):
        draft, final = self._pair("one")
        result = edit_learning.record_lesson(
            self.profile,
            draft,
            final,
            "article-one",
            [
                {
                    "key": "shorter_paragraphs",
                    "type": "rhythm",
                    "instruction": "在高密度信息后缩短段落。",
                }
            ],
            approved=True,
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(result["rules"][0]["confidence"], 2)
        self.assertEqual(result["rules"][0]["status"], "provisional")
        lesson_text = (self.profile / result["source_ref"]).read_text(
            encoding="utf-8"
        )
        self.assertNotIn(str(self.root), lesson_text)
        self.assertNotIn("这是一个比较长的原始段落", lesson_text)
        self.assertNotIn("更短。", lesson_text)
        self.assertEqual(validate_project.validate_profile(self.profile), [])

    def test_repeated_confirmed_rule_promotes_then_decays(self):
        for day, suffix in enumerate(("one", "two", "three"), start=1):
            self._record(
                suffix,
                datetime(2026, 1, day, tzinfo=timezone.utc),
            )
        current = edit_learning.aggregate_rules(
            self.profile, as_of=date(2026, 1, 3)
        )[0]
        self.assertEqual(current["occurrences"], 3)
        self.assertEqual(current["confidence"], 6)
        self.assertEqual(current["status"], "validated")

        decayed = edit_learning.aggregate_rules(
            self.profile, as_of=date(2026, 7, 15)
        )[0]
        self.assertEqual(decayed["confidence"], 4)
        self.assertEqual(decayed["status"], "provisional")

    def test_duplicate_pair_is_idempotent(self):
        draft, final = self._pair("same")
        rules = [
            {
                "key": "shorter_paragraphs",
                "type": "rhythm",
                "instruction": "在高密度信息后缩短段落。",
            }
        ]
        first = edit_learning.record_lesson(
            self.profile, draft, final, "same", rules, approved=True
        )
        second = edit_learning.record_lesson(
            self.profile, draft, final, "same", rules, approved=True
        )
        self.assertEqual(first["status"], "recorded")
        self.assertEqual(second["status"], "already_recorded")
        self.assertEqual(second["rules"][0]["occurrences"], 1)

    def test_explicit_approval_and_long_term_profile_are_required(self):
        draft, final = self._pair("blocked")
        rules = [
            {
                "key": "shorter_paragraphs",
                "type": "rhythm",
                "instruction": "缩短段落。",
            }
        ]
        with self.assertRaises(PermissionError):
            edit_learning.record_lesson(
                self.profile, draft, final, "blocked", rules, approved=False
            )
        temporary_article = self.root / "temporary-article"
        temporary_article.mkdir()
        with self.assertRaises(ValueError):
            edit_learning.record_lesson(
                temporary_article,
                draft,
                final,
                "blocked",
                rules,
                approved=True,
            )
        self.assertFalse((temporary_article / "history" / "edits").exists())

    def test_old_profile_without_ledger_remains_valid_and_bootstraps(self):
        shutil.rmtree(self.profile / "history" / "edits")
        self.assertEqual(validate_project.validate_profile(self.profile), [])
        self._record("legacy", datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertTrue(
            (self.profile / "history" / "edits" / "index.json").is_file()
        )
        self.assertEqual(validate_project.validate_profile(self.profile), [])

    def test_machine_paths_are_rejected_from_learning_rules(self):
        draft, final = self._pair("unsafe")
        with self.assertRaises(ValueError):
            edit_learning.record_lesson(
                self.profile,
                draft,
                final,
                "unsafe",
                [
                    {
                        "key": "unsafe_path",
                        "type": "expression",
                        "instruction": "读取 C:\\Users\\name\\secret.txt。",
                    }
                ],
                approved=True,
            )


class TopicDependencyTests(unittest.TestCase):
    @staticmethod
    def _discovered(*names: str):
        return {name: Path("C:/skills") / name for name in names}

    def test_standard_topic_requires_cross_platform_wechat_and_cheat(self):
        result = dependency_check.check_dependencies(
            "topic",
            self._discovered("cheat-on-content", "creator-buddy"),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(
            result["missing_required"], ["cheat-trends", "gzh-explosive-content-detector"]
        )

    def test_standard_topic_passes_with_all_required_lanes(self):
        result = dependency_check.check_dependencies(
            "topic",
            self._discovered(
                "cheat-on-content",
                "cheat-trends",
                "creator-buddy",
                "gzh-explosive-content-detector",
            ),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["missing_required"], [])

    def test_ai_topic_additionally_requires_aihot(self):
        result = dependency_check.check_dependencies(
            "topic-ai",
            self._discovered(
                "cheat-on-content",
                "cheat-trends",
                "creator-buddy",
                "gzh-explosive-content-detector",
            ),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["missing_required"], ["aihot"])

    def test_topic_brief_preserves_signal_and_decision_receipts(self):
        template = (
            SKILL_ROOT / "assets" / "article-project-template" / "topic-brief.md"
        ).read_text(encoding="utf-8")
        for required_heading in (
            "## 数据源状态",
            "## 归一化候选池",
            "## 去重记录",
            "## Cheat 评分与决策引用",
            "## 用户确认",
        ):
            self.assertIn(required_heading, template)


class DeliveryContractTests(unittest.TestCase):
    def test_cover_is_21_9_only_while_body_illustrations_remain_enabled(self):
        routing = (SKILL_ROOT / "references" / "skill-routing.md").read_text(
            encoding="utf-8"
        )
        plan = (
            SKILL_ROOT
            / "assets"
            / "article-project-template"
            / "visuals"
            / "visual-plan.md"
        ).read_text(encoding="utf-8")
        self.assertIn("exactly one static `21:9`", routing)
        self.assertIn("不生成 `1:1` 分享卡", plan)
        self.assertIn("## 正文配图认知锚点", plan)
        self.assertIn("Dual-rail body illustration routing", routing)

    def test_publish_contract_is_manual_only(self):
        publishing = (SKILL_ROOT / "references" / "publishing.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Manual delivery only", publishing)
        self.assertNotIn("draft_uploaded", publishing)
        self.assertNotIn("upload_failed", publishing)

    def test_publish_dependency_no_longer_discovers_draft_adapter(self):
        result = dependency_check.check_dependencies(
            "publish", {"cheat-on-content": Path("C:/skills/cheat-on-content")}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["optional_missing"], [])

    def test_body_illustration_preflight_accepts_either_complete_route(self):
        ian = dependency_check.check_dependencies(
            "visual",
            {
                "ian-xiaohei-illustrations": Path("C:/skills/ian"),
                "imagegen": Path("C:/skills/imagegen"),
            },
        )
        baoyu = dependency_check.check_dependencies(
            "visual",
            {
                "baoyu-article-illustrator": Path("C:/skills/baoyu"),
                "imagegen": Path("C:/skills/imagegen"),
            },
        )
        self.assertTrue(ian["ok"])
        self.assertEqual(ian["optional_missing"], [])
        self.assertEqual(ian["runtime"]["ready_routes"], ["ian"])
        self.assertTrue(baoyu["ok"])
        self.assertEqual(baoyu["optional_missing"], [])
        self.assertEqual(
            baoyu["runtime"]["ready_routes"], ["baoyu-article-illustrator"]
        )


if __name__ == "__main__":
    unittest.main()
