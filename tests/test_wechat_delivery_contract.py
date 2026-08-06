from __future__ import annotations

import unittest
import sys

from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / 'scripts'))


class WeChatDeliveryContractTests(unittest.TestCase):
    def test_cover_is_21_9_only_while_body_illustrations_remain_enabled(self):
        routing = (SKILL_ROOT / 'references' / 'skill-routing.md').read_text(encoding='utf-8')
        quality = (SKILL_ROOT / 'references' / 'quality-gates.md').read_text(encoding='utf-8')
        plan = (SKILL_ROOT / 'assets' / 'article-project-template' / 'visuals' / 'visual-plan.md').read_text(encoding='utf-8')
        self.assertIn('只生成一张静态 `21:9`', quality)
        self.assertIn('不生成 `1:1` 分享卡', plan)
        self.assertIn('## 正文配图认知锚点', plan)
        self.assertIn('每个正文认知锚点', quality)
        self.assertIn('quality-gates.md', routing)

    def test_publish_contract_is_manual_only(self):
        publishing = (SKILL_ROOT / 'references' / 'publishing.md').read_text(encoding='utf-8')
        self.assertIn('仅人工交付', publishing)
        self.assertNotIn('draft_uploaded', publishing)
        self.assertNotIn('upload_failed', publishing)

    def test_wechat_layout_contract_is_complete_and_overrides_theme_defaults(self):
        contract = (SKILL_ROOT / 'references' / 'wechat-layout-contract.md').read_text(encoding='utf-8')
        quality = (SKILL_ROOT / 'references' / 'quality-gates.md').read_text(encoding='utf-8')
        execution = (SKILL_ROOT / 'references' / 'execution.md').read_text(encoding='utf-8')

        for required_rule in (
            '窄屏首屏呈现一个完整阅读单元',
            '大标题与小标题使用明显不同的字体颜色',
            '行距与段间距保持舒适、疏密适度',
            '大标题全篇使用同一格式和醒目颜色',
            '默认移除装饰性横线和多余边框',
            '分行后仅剩两三个字的孤立短行',
            '禁止只高亮半句',
            '单段不超过五六行',
            '14 或 15 px 字号和 `#595757` 字色',
        ):
            self.assertIn(required_rule, contract)

        self.assertIn('本契约高于所选主题的组件配方', contract)
        self.assertIn('已登记的深色', contract)
        self.assertIn('`4.5:1` 的对比度', contract)
        self.assertIn('不得为单篇文章临时另定正文色', contract)
        # quality-gates.md 仍要在调用 gzh-design 时把契约作为上位约束传入
        self.assertIn('不可选的上位约束', quality)
        self.assertIn('references/wechat-layout-contract.md', quality)
        self.assertIn('quality-gates.md', execution)

    def test_gzh_design_author_cta_policy_is_explicit(self):
        cta = (SKILL_ROOT / 'references' / 'external-contracts.md').read_text(encoding='utf-8')
        quality = (SKILL_ROOT / 'references' / 'quality-gates.md').read_text(encoding='utf-8')
        execution = (SKILL_ROOT / 'references' / 'execution.md').read_text(encoding='utf-8')
        for required in ('author_cta: disabled', 'author_cta: explicit', '{{作者名}}', '{{简介}}'):
            self.assertIn(required, cta)
        self.assertIn('external-contracts.md#gzh-design-author-cta-override', quality)
        self.assertIn('quality-gates.md', execution)

    def test_publish_dependency_no_longer_discovers_draft_adapter(self):
        import dependency_check

        result = dependency_check.check_dependencies('publish', {'cheat-on-content': Path('C:/skills/cheat-on-content')})
        self.assertTrue(result['ok'])
        self.assertEqual(result['missing_required'], [])

    def test_long_essay_prediction_bridge_is_declared(self):
        bridge = (SKILL_ROOT / 'references' / 'cheat-contracts.md').read_text(encoding='utf-8')
        quality = (SKILL_ROOT / 'references' / 'quality-gates.md').read_text(encoding='utf-8')
        execution = (SKILL_ROOT / 'references' / 'execution.md').read_text(encoding='utf-8')
        self.assertIn('prediction-input-reference.json', bridge)
        self.assertIn('cheat_prediction_adapter.py', bridge)
        self.assertIn('输入回执', quality)
        self.assertIn('哈希绑定的只读 Cheat 输入', execution)

    def test_wechat_publish_bridge_and_metrics_contract_are_declared(self):
        bridge = (SKILL_ROOT / 'references' / 'wechat-publish-bridge.md').read_text(encoding='utf-8')
        publishing = (SKILL_ROOT / 'references' / 'publishing.md').read_text(encoding='utf-8')
        execution = (SKILL_ROOT / 'references' / 'execution.md').read_text(encoding='utf-8')
        for field in ('publish_json_sha256', 'public_url', 'cheat_prediction_file', 'platform', 'metrics.json'):
            self.assertIn(field, bridge)
        self.assertIn('wechat_publish_bridge.py', bridge)
        self.assertIn('根 `cheat-publish` 成功后', publishing)
        self.assertIn('publish-reference.json', execution)

    def test_body_illustration_preflight_accepts_either_complete_route(self):
        import dependency_check

        ian = dependency_check.check_dependencies('visual', {'ian-xiaohei-illustrations': Path('C:/skills/ian'), 'imagegen': Path('C:/skills/imagegen')})
        baoyu = dependency_check.check_dependencies('visual', {'baoyu-article-illustrator': Path('C:/skills/baoyu'), 'imagegen': Path('C:/skills/imagegen')})
        self.assertTrue(ian['ok'])
        self.assertEqual(ian['optional_missing'], [])
        self.assertEqual(ian['runtime']['ready_routes'], ['ian'])
        self.assertTrue(baoyu['ok'])
        self.assertEqual(baoyu['optional_missing'], [])
        self.assertEqual(baoyu['runtime']['ready_routes'], ['baoyu-article-illustrator'])


if __name__ == '__main__':
    unittest.main()
