from __future__ import annotations

from pathlib import Path
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]


class WeChatRouteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.routing = (
            SKILL_ROOT / "references" / "skill-routing.md"
        ).read_text(encoding="utf-8")
        cls.onboarding = (
            SKILL_ROOT / "references" / "onboarding.md"
        ).read_text(encoding="utf-8")

    def test_benchmark_learning_and_migration_are_explicit_root_routes(self):
        for route in ('cheat-learn-from', 'cheat-migrate'):
            self.assertIn(route, self.skill)
            self.assertIn(route, self.routing)
            self.assertIn(route, self.onboarding)
        self.assertIn('单独确认', self.skill)
        self.assertIn('separate user confirmation', self.onboarding)

    def test_video_route_is_excluded_and_trends_is_fifth_lane(self):
        for route in ('cheat-shoot', 'cheat-trends'):
            self.assertIn(route, self.skill)
            self.assertIn(route, self.routing)
        self.assertIn('Intentionally excluded Cheat routes', self.routing)
        self.assertIn('五路信号', self.skill)
        self.assertIn('fifth topic-signal lane', self.routing)

    def test_blind_scorer_remains_internal(self):
        self.assertIn('cheat-score-blind', self.skill)
        self.assertIn('cheat-score-blind', self.routing)
        self.assertIn('不得', self.skill)
        self.assertIn('Do not invoke `cheat-score-blind` directly', self.routing)

    def test_learn_from_expects_separate_user_confirmation(self):
        self.assertIn('separate user confirmation', self.onboarding)
        self.assertIn('sample scope and target Cheat project', self.routing)
        self.assertIn('separate user confirmation', self.routing)

    def test_cheat_status_and_migrate_are_import_prerequisites(self):
        self.assertIn('cheat-status', self.onboarding)
        self.assertIn('cheat-migrate', self.onboarding)
        self.assertIn('cheat-status', self.skill)

    def test_skill_routing_describes_required_creator_buddy_branch(self):
        text = self.routing
        self.assertIn('gzh-explosive-content-detector', text)
        self.assertIn('creator-buddy', text)
        self.assertIn('generic-keyword confirmation rule', text)

    def test_skill_routing_describes_excluded_capabilities(self):
        excluded = (
            'hv-analysis',
            'space-chart-image',
            'article-batch-illustration',
            'article-cover-and-batch-illustration',
            'baoyu-slide-deck',
            'neat-freak',
            'storage-analyzer',
        )
        for capability in excluded:
            self.assertIn(capability, self.routing)

    def test_onboarding_import_does_not_preview_after_migration_without_status(self):
        self.assertIn('obtain a compatible `cheat-status` result', self.onboarding)

    def test_execution_uses_absolute_skill_root_for_local_scripts(self):
        execution = (SKILL_ROOT / "references" / "execution.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("python scripts/", execution)
        self.assertIn("python <SKILL_ROOT>/scripts/dependency_check.py", execution)
        self.assertIn("python -m scripts qrcode", execution)

    def test_execution_lists_all_public_wechat_cheat_routes(self):
        execution = (SKILL_ROOT / "references" / "execution.md").read_text(
            encoding="utf-8"
        )
        routes = (
            "cheat-init",
            "cheat-learn-from",
            "cheat-seed",
            "cheat-recommend",
            "cheat-score",
            "cheat-predict",
            "cheat-publish",
            "cheat-retro",
            "cheat-persona",
            "cheat-bump",
            "cheat-status",
            "cheat-migrate",
        )
        for route in routes:
            self.assertIn(route, execution)

    def test_migration_requires_a_machine_readable_post_status_receipt(self):
        execution = (SKILL_ROOT / "references" / "execution.md").read_text(
            encoding="utf-8"
        )
        receipt = (
            SKILL_ROOT / "references" / "cheat-status-receipt.md"
        ).read_text(encoding="utf-8")
        self.assertIn("cheat-status-receipt.json", self.onboarding)
        self.assertIn("cheat-status-receipt.json", self.skill)
        self.assertIn("cheat-status-receipt.json", execution)
        for field in (
            "schema_version",
            "target_project_binding",
            "cheat_schema_version",
            '"status": "compatible"',
            '"source": "cheat-status"',
            "checked_at",
        ):
            self.assertIn(field, receipt)

    def test_topic_signal_registry_is_the_five_lane_source_of_truth(self):
        registry = (
            SKILL_ROOT / "references" / "topic-signal-registry.md"
        ).read_text(encoding="utf-8")
        execution = (SKILL_ROOT / "references" / "execution.md").read_text(
            encoding="utf-8"
        )
        quality = (SKILL_ROOT / "references" / "quality-gates.md").read_text(
            encoding="utf-8"
        )
        template = (
            SKILL_ROOT / "assets" / "article-project-template" / "topic-brief.md"
        ).read_text(encoding="utf-8")
        lanes = (
            "creator-buddy-cross-platform",
            "gzh-explosive-content-detector",
            "aihot",
            "x-tweet-fetcher",
            "cheat-trends",
        )
        for lane in lanes:
            self.assertIn(lane, registry)
            self.assertIn(lane, execution)
            self.assertIn(lane, self.routing)
            self.assertIn(lane, self.skill)
            self.assertIn(lane, template)
        self.assertIn("topic-signal-registry.md", execution)
        self.assertIn("topic-signal-registry.md", quality)
        self.assertNotIn("四路", execution)
        self.assertNotIn("前三路", execution)
        self.assertIn("not_applicable", registry)


if __name__ == '__main__':
    unittest.main()
