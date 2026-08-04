from __future__ import annotations

import unittest

from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class WeChatDeliveryContractTests(unittest.TestCase):
    def test_cover_is_21_9_only_while_body_illustrations_remain_enabled(self):
        routing = (SKILL_ROOT / 'references' / 'skill-routing.md').read_text(encoding='utf-8')
        plan = (SKILL_ROOT / 'assets' / 'article-project-template' / 'visuals' / 'visual-plan.md').read_text(encoding='utf-8')
        self.assertIn('exactly one static `21:9`', routing)
        self.assertIn('不生成 `1:1` 分享卡', plan)
        self.assertIn('## 正文配图认知锚点', plan)
        self.assertIn('Dual-rail body illustration routing', routing)

    def test_publish_contract_is_manual_only(self):
        publishing = (SKILL_ROOT / 'references' / 'publishing.md').read_text(encoding='utf-8')
        self.assertIn('Manual delivery only', publishing)
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
        # execution.md 仍要记录"9 项排版检查"到 html-qc
        self.assertIn('九项排版检查', execution)

    def test_publish_dependency_no_longer_discovers_draft_adapter(self):
        import dependency_check

        result = dependency_check.check_dependencies('publish', {'cheat-on-content': Path('C:/skills/cheat-on-content')})
        self.assertTrue(result['ok'])
        self.assertEqual(result['missing_required'], [])

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
