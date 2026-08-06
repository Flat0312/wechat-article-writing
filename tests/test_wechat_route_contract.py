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
            self.assertIn(route, self.onboarding)
        self.assertIn('SKILL.md` 核心约束第 1 条', self.routing)
        self.assertIn('单独确认', self.skill)
        self.assertIn('单独的用户确认', self.onboarding)

    def test_video_route_is_excluded_and_topic_signals_use_eight_lanes(self):
        registry = (SKILL_ROOT / 'references' / 'topic-signal-registry.md').read_text(encoding='utf-8')
        for route in ('cheat-shoot', 'cheat-trends'):
            self.assertIn(route, self.skill)
        self.assertIn('明确排除的 Cheat 路由', self.routing)
        self.assertIn('八路信号', self.skill)
        self.assertIn('cheat-trends', registry)
        self.assertIn('not a WeChat topic-signal lane', registry)

    def test_blind_scorer_remains_internal(self):
        self.assertIn('cheat-score-blind', self.skill)
        self.assertIn('不得', self.skill)
        self.assertIn('SKILL.md` 核心约束第 1 条', self.routing)

    def test_learn_from_expects_separate_user_confirmation(self):
        self.assertIn('单独的用户确认', self.onboarding)
        self.assertIn('样本范围与目标 Cheat 项目', self.onboarding)

    def test_cheat_status_and_migrate_are_import_prerequisites(self):
        self.assertIn('cheat-status', self.onboarding)
        self.assertIn('cheat-migrate', self.onboarding)
        self.assertIn('cheat-status', self.skill)

    def test_skill_routing_describes_required_creator_buddy_branch(self):
        text = self.routing
        self.assertIn('gzh-explosive-content-detector', text)
        self.assertIn('creator-buddy', text)
        self.assertIn('通用关键词确认规则', text)

    def test_creator_buddy_xiaohongshu_route_is_explicitly_overridden(self):
        override = (
            SKILL_ROOT
            / "references"
            / "external-contracts.md"
        ).read_text(encoding="utf-8")
        for required in (
            '"provider": "global-content-search"',
            '"route": "agent-reach-opencli->redfox->guaikei->public-api"',
            '"allow_fallback": true',
            'status` may be `completed`, `missing`, or `blocked`',
        ):
            self.assertIn(required, override)
        registry = (SKILL_ROOT / "references" / "topic-signal-registry.md").read_text(encoding="utf-8")
        self.assertIn('external-contracts.md#creator-buddy-wechat-route-override', registry)
        self.assertIn('OpenCLI first', registry)

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
        self.assertIn('未取得兼容的 `cheat-status` 结果', self.onboarding)

    def test_execution_uses_absolute_skill_root_for_local_scripts(self):
        execution = (SKILL_ROOT / "references" / "execution.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("python scripts/", execution)
        self.assertIn("python <SKILL_ROOT>/scripts/dependency_check.py", execution)
        registry = (SKILL_ROOT / "references" / "topic-signal-registry.md").read_text(encoding="utf-8")
        self.assertIn("agent-reach doctor --json", registry)

    def test_skill_lists_all_public_wechat_cheat_routes(self):
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
            self.assertIn(route, self.skill)
        self.assertIn("SKILL.md` 核心约束第 1 条", execution)

    def test_migration_requires_a_machine_readable_post_status_receipt(self):
        execution = (SKILL_ROOT / "references" / "execution.md").read_text(
            encoding="utf-8"
        )
        receipt = (
            SKILL_ROOT / "references" / "cheat-contracts.md"
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

    def test_long_essay_prediction_separates_cheat_call_and_rubric_adaptation(self):
        contract = (
            SKILL_ROOT / "references" / "cheat-contracts.md"
        ).read_text(encoding="utf-8")
        bridge = (
            SKILL_ROOT / "references" / "cheat-contracts.md"
        ).read_text(encoding="utf-8")
        quality = (
            SKILL_ROOT / "references" / "quality-gates.md"
        ).read_text(encoding="utf-8")
        for required in (
            "root_call_status",
            "rubric_status",
            "rubric_form_mismatch",
            "wechat-long-essay-v1",
        ):
            self.assertIn(required, contract)
        self.assertIn("cheat-form-receipt.json", bridge)
        self.assertIn("rubric_status=compatible", quality)

    def test_cheat_seed_generic_humanizer_mismatch_is_registered(self):
        register = (
            SKILL_ROOT / "references" / "cheat-contracts.md"
        ).read_text(encoding="utf-8")
        for required in (
            "generic `humanizer`",
            "humanizer-zh",
            "Do not install, discover, or invoke a second",
            "cannot replace",
        ):
            self.assertIn(required, register)
        self.assertIn("cheat-contracts.md#cheat-seed-humanizer-compatibility-register", self.routing)

    def test_topic_signal_registry_is_the_eight_lane_source_of_truth(self):
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
            "creator-buddy-xiaohongshu",
            "gzh-explosive-content-detector",
            "aihot",
            "creator-buddy-bilibili",
            "creator-buddy-douyin",
            "creator-buddy-zhihu",
            "creator-buddy-weibo",
            "creator-buddy-toutiao",
        )
        for lane in lanes:
            self.assertIn(lane, registry)
            self.assertIn(lane, template)
        self.assertIn("topic-signal-registry.md", execution)
        self.assertIn("topic-signal-registry.md", quality)
        self.assertIn("topic-signal-registry.md", self.routing)
        for duplicated_lane in (
            "creator-buddy-xiaohongshu",
            "creator-buddy-bilibili",
            "creator-buddy-douyin",
            "creator-buddy-zhihu",
            "creator-buddy-weibo",
            "creator-buddy-toutiao",
        ):
            self.assertNotIn(duplicated_lane, execution)
            self.assertNotIn(duplicated_lane, self.routing)
        self.assertNotIn("四路", execution)
        self.assertNotIn("前三路", execution)
        self.assertIn("not_applicable", registry)


if __name__ == '__main__':
    unittest.main()
