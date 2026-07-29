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
