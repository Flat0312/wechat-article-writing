from __future__ import annotations

import unittest


SKILL_ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]


class MultiplatformHardeningTests(unittest.TestCase):
    def test_skill_routing_does_not_simulate_cheat_workflows(self):
        routing = (SKILL_ROOT / 'references' / 'skill-routing.md').read_text(encoding='utf-8-sig')
        self.assertIn('simulate these actions', routing)
        self.assertNotIn('cheat-score-blind', (SKILL_ROOT / 'references' / 'onboarding.md').read_text(encoding='utf-8-sig'))


if __name__ == '__main__':
    unittest.main()
