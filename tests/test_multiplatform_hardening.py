from __future__ import annotations

import unittest


SKILL_ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]


class MultiplatformHardeningTests(unittest.TestCase):
    def test_skill_routing_does_not_simulate_cheat_workflows(self):
        skill = (SKILL_ROOT / 'SKILL.md').read_text(encoding='utf-8-sig')
        routing = (SKILL_ROOT / 'references' / 'skill-routing.md').read_text(encoding='utf-8-sig')
        self.assertIn('不得模拟', skill)
        self.assertIn('SKILL.md` 核心约束第 1 条', routing)
        self.assertNotIn('cheat-score-blind', (SKILL_ROOT / 'references' / 'onboarding.md').read_text(encoding='utf-8-sig'))


if __name__ == '__main__':
    unittest.main()
