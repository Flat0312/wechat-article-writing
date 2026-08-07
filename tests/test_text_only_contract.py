"""Pure-text (schema 1.1) contract red-light tests.

These tests assert the five contract invariants for the future long-essay
pipeline before any implementation lands. They MUST fail on the current
1.0 codebase and turn green only after task 2 implementation.

The five invariants come from the task brief:
  1. New projects are schema 1.1 with nine stages, no visual_plan/visuals/html.
  2. The dependency rules and routing for the text-only long-essay path do
     not require gzh-design.
  3. Public publication registration requires a recorded, approved,
     non-stale final artifact and explicit user confirmation, without
     any HTML gate.
  4. Legacy schema 1.0 projects still load; historical HTML status and
     artifacts are not migrated, deleted, or rewritten by the new code.
  5. The news-card pipeline stays unchanged.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import article_state
from wechat_publish_bridge import PublishError, record_wechat_publish


SCHEMA_1_1_STAGES = (
    "brief",
    "topic",
    "evidence",
    "outline",
    "draft",
    "final",
    "prediction",
    "publish",
    "retro",
)


class TextOnlySchemaContractTests(unittest.TestCase):
    """Invariants 1 and 4: schema 1.1 stage set + legacy 1.0 read-only path."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "articles" / "article-text"
        self.state = self._build_1_1_state()
        article_state.write_state(self.project, self.state)

    def tearDown(self):
        self.temp.cleanup()

    def _build_1_1_state(self):
        if hasattr(article_state, "create_project_v11"):
            return article_state.create_project_v11(
                self.project, "article-text", "full", "account-profile", "primary"
            )
        raise AssertionError(
            "article_state.create_project_v11 is not implemented; schema 1.1 is not supported"
        )

    def test_1_1_project_schema_version_is_one_dot_one(self):
        persisted = json.loads(
            (self.project / "article-state.json").read_text(encoding="utf-8-sig")
        )
        self.assertEqual(persisted["schema_version"], "1.1")
        self.assertEqual(persisted["article_id"], "article-text")
        self.assertEqual(persisted["current_stage"], "brief")
        self.assertEqual(tuple(persisted["stage_status"].keys()), SCHEMA_1_1_STAGES)

    def test_1_1_project_stages_exclude_visual_plan_visuals_html(self):
        persisted = json.loads(
            (self.project / "article-state.json").read_text(encoding="utf-8-sig")
        )
        stage_names = set(persisted["stage_status"].keys())
        for forbidden in ("visual_plan", "visuals", "html"):
            self.assertNotIn(forbidden, stage_names)
        self.assertEqual(len(stage_names), 9)

    def test_1_1_invalidating_final_makes_prediction_publish_retro_stale(self):
        target = self.project / "drafts" / "final.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# final\n", encoding="utf-8")
        article_state.record_artifact(self.state, self.project, "final", Path("drafts/final.md"))
        article_state.record_approval(
            self.state, "final", "2026-08-07T10:00:00+08:00"
        )
        article_state.set_stage(self.state, "prediction", "completed")
        article_state.set_stage(self.state, "publish", "completed")
        article_state.set_stage(self.state, "retro", "completed")
        article_state.invalidate_from(self.state, "final")
        for downstream in ("prediction", "publish", "retro"):
            self.assertEqual(self.state["stage_status"][downstream], "stale")
        self.assertNotIn("html", self.state["stage_status"])
        self.assertNotIn("html", self.state["stale_artifacts"])

    def test_legacy_1_0_project_still_loads_with_full_twelve_stage_history(self):
        legacy_project = self.root / "articles" / "legacy-article"
        legacy_project.mkdir(parents=True)
        legacy_state = {
            "schema_version": "1.0",
            "article_id": "legacy-article",
            "mode": "full",
            "profile_ref": "account-profile",
            "cheat_binding": "primary",
            "current_stage": "publish",
            "stage_status": {stage: "completed" for stage in article_state.STAGES},
            "artifacts": {},
            "approvals": {},
            "skill_routes": {},
            "stale_artifacts": [],
            "required_actions": [],
            "created_at": "2026-07-01T00:00:00+08:00",
            "updated_at": "2026-07-01T00:00:00+08:00",
        }
        article_state.write_state(legacy_project, legacy_state)
        loaded = article_state.load_state(legacy_project)
        self.assertEqual(loaded["schema_version"], "1.0")
        self.assertEqual(tuple(loaded["stage_status"].keys()), tuple(article_state.STAGES))
        article_state.set_stage(loaded, "outline", "completed")
        article_state.invalidate_from(loaded, "outline")
        self.assertIn("html", loaded["stage_status"])
        self.assertEqual(loaded["stage_status"]["html"], "stale")


class TextOnlyDependencyContractTests(unittest.TestCase):
    """Invariants 2 and 5: dependency check has no gzh-design on text-only
    long-essay; news-card path remains untouched."""

    def test_text_only_long_essay_stage_does_not_require_gzh_design(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "text-only-long-essay",
            {
                name: Path("C:/skills") / name
                for name in ("cheat-on-content", "wechat-content-strategy", "human-writing")
            },
        )
        self.assertTrue(result["ok"], msg=json.dumps(result, ensure_ascii=False))
        self.assertNotIn("gzh-design", result.get("missing_required", []))
        self.assertNotIn("gzh-design", result.get("optional_missing", []))
        self.assertEqual(result["resolved_stage"], "text-only-long-essay")

    def test_html_stage_alias_is_unavailable_for_text_only_long_essay(self):
        import dependency_check

        self.assertNotIn(
            "text-only-long-essay",
            getattr(dependency_check, "STAGE_ALIASES", {}),
        )

    def test_news_card_route_is_unchanged(self):
        import dependency_check

        result = dependency_check.check_dependencies(
            "news-card",
            {
                name: Path("C:/skills") / name
                for name in (
                    "cheat-on-content",
                    "creator-buddy",
                    "gzh-explosive-content-detector",
                    "wechat-content-strategy",
                    "global-content-search",
                    "guizang-social-card-skill",
                )
            },
            env={
                "OPENCLI_BIN": str(Path("C:/missing/opencli.exe")),
                "AGENT_REACH_BIN": str(Path("C:/missing/agent-reach.exe")),
            },
        )
        self.assertFalse(
            result["ok"],
            msg="news-card still requires opencli/agent-reach CLIs",
        )
        self.assertNotIn("gzh-design", result.get("missing_required", []))
        self.assertNotIn("html", result.get("missing_required", []))


class TextOnlyPublishBridgeTests(unittest.TestCase):
    """Invariants 3 and 4: 1.1 publish bridge gates on final/approval/non-stale;
    1.0 bridge still gates on html/approval."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "articles" / "article-text"
        self.cheat = self.root / "cheat"
        self.cheat.mkdir()
        self.state = self._build_1_1_state()
        article_state.write_state(self.project, self.state)
        self.final = self.project / "drafts" / "final.md"
        self.final.parent.mkdir(parents=True, exist_ok=True)
        self.final.write_text("# final\n", encoding="utf-8")
        article_state.record_artifact(self.state, self.project, "final", Path("drafts/final.md"))
        article_state.record_approval(
            self.state, "final", "2026-08-07T10:00:00+08:00"
        )
        self.prediction = self.cheat / "predictions" / "v1.md"
        self.prediction.parent.mkdir()
        self.prediction.write_text("# prediction\n", encoding="utf-8")
        self.prediction_hash = sha256(self.prediction.read_bytes()).hexdigest()
        self.receipt = {
            "status": "published",
            "platform": "wechat",
            "prediction_file": "predictions/v1.md",
            "prediction_sha256": self.prediction_hash,
            "published_at": "2026-08-07T10:01:00+08:00",
        }
        article_state.write_state(self.project, self.state)

    def tearDown(self):
        self.temp.cleanup()

    def _build_1_1_state(self):
        if hasattr(article_state, "create_project_v11"):
            return article_state.create_project_v11(
                self.project, "article-text", "full", "account-profile", "primary"
            )
        raise AssertionError("article_state.create_project_v11 is not implemented")

    def test_1_1_publish_requires_explicit_user_confirmation(self):
        with self.assertRaises(PublishError):
            record_wechat_publish(
                self.project,
                self.cheat,
                self.receipt,
                "https://mp.weixin.qq.com/s/example",
                "2026-08-07T10:01:00+08:00",
                False,
            )

    def test_1_1_publish_requires_final_approval(self):
        self.state["approvals"] = {}
        article_state.write_state(self.project, self.state)
        with self.assertRaises(PublishError):
            record_wechat_publish(
                self.project,
                self.cheat,
                self.receipt,
                "https://mp.weixin.qq.com/s/example",
                "2026-08-07T10:01:00+08:00",
                True,
            )

    def test_1_1_publish_requires_non_stale_final(self):
        article_state.invalidate_from(self.state, "final")
        article_state.write_state(self.project, self.state)
        with self.assertRaises(PublishError):
            record_wechat_publish(
                self.project,
                self.cheat,
                self.receipt,
                "https://mp.weixin.qq.com/s/example",
                "2026-08-07T10:01:00+08:00",
                True,
            )

    def test_1_1_publish_does_not_require_html_stage(self):
        reference = record_wechat_publish(
            self.project,
            self.cheat,
            self.receipt,
            "https://mp.weixin.qq.com/s/example",
            "2026-08-07T10:01:00+08:00",
            True,
        )
        self.assertEqual(reference["status"], "publicly_published")
        final_state = json.loads(
            (self.project / "article-state.json").read_text(encoding="utf-8-sig")
        )
        self.assertNotIn("html", final_state["stage_status"])
        self.assertNotIn("html", final_state["artifacts"])

    def test_legacy_1_0_publish_bridge_still_requires_html(self):
        legacy_project = self.root / "articles" / "legacy-article"
        legacy_project.mkdir()
        legacy_statuses = {stage: "pending" for stage in article_state.STAGES}
        legacy_statuses["html"] = "pending"
        legacy_state = {
            "schema_version": "1.0",
            "article_id": "legacy-article",
            "mode": "full",
            "profile_ref": "account-profile",
            "cheat_binding": "primary",
            "current_stage": "publish",
            "stage_status": legacy_statuses,
            "artifacts": {},
            "approvals": {},
            "skill_routes": {},
            "stale_artifacts": [],
            "required_actions": [],
            "created_at": "2026-07-01T00:00:00+08:00",
            "updated_at": "2026-07-01T00:00:00+08:00",
        }
        article_state.write_state(legacy_project, legacy_state)
        with self.assertRaises(PublishError):
            record_wechat_publish(
                legacy_project,
                self.cheat,
                self.receipt,
                "https://mp.weixin.qq.com/s/example",
                "2026-08-07T10:01:00+08:00",
                True,
            )

    def test_legacy_1_0_publish_succeeds_when_html_completed_and_not_stale(self):
        legacy_project = self.root / "articles" / "legacy-article"
        legacy_project.mkdir()
        legacy_statuses = {stage: "completed" for stage in article_state.STAGES}
        legacy_state = {
            "schema_version": "1.0",
            "article_id": "legacy-article",
            "mode": "full",
            "profile_ref": "account-profile",
            "cheat_binding": "primary",
            "current_stage": "publish",
            "stage_status": legacy_statuses,
            "artifacts": {},
            "approvals": {},
            "skill_routes": {},
            "stale_artifacts": [],
            "required_actions": [],
            "created_at": "2026-07-01T00:00:00+08:00",
            "updated_at": "2026-07-01T00:00:00+08:00",
        }
        article_state.write_state(legacy_project, legacy_state)
        reference = record_wechat_publish(
            legacy_project,
            self.cheat,
            self.receipt,
            "https://mp.weixin.qq.com/s/example",
            "2026-08-07T10:01:00+08:00",
            True,
        )
        self.assertEqual(reference["status"], "publicly_published")


if __name__ == "__main__":
    unittest.main()