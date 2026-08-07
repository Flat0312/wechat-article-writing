from __future__ import annotations

import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class MultiplatformContractTests(unittest.TestCase):
    def test_current_wechat_skill_is_single_platform(self):
        self.assertEqual(
            (SKILL_ROOT / 'agents' / 'openai.yaml').read_text(encoding='utf-8-sig'),
            'interface:\n'
            '  display_name: "WeChat Article Writing"\n'
            '  short_description: "从账号状态、内容策略与风格学习到终稿落盘、发布登记和复盘的公众号总控工作流（中长文 schema 1.1 纯文字交付，资讯贴图走独立 21:9 头图分支）"\n'
            '  default_prompt: "Use $wechat-article-writing to create or improve a Chinese WeChat article through verified pure-text delivery (schema 1.1) or news-card image generation, and, when enabled, continuously observe the account\'s approved final drafts for style evolution."\n',
        )

    def test_wechat_delivery_contract_does_not_register_other_platforms(self):
        routing = (SKILL_ROOT / 'references' / 'skill-routing.md').read_text(encoding='utf-8-sig')
        self.assertIn('跨平台选题信号', routing)
        self.assertIn('global-content-search', routing)
        self.assertNotIn('Douyin keyword heat', routing)
        self.assertNotIn('Generate both routes for one anchor', (SKILL_ROOT / 'SKILL.md').read_text(encoding='utf-8-sig'))


if __name__ == '__main__':
    unittest.main()
