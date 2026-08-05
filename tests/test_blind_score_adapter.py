from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import blind_score_adapter


V0_RUBRIC = """
**当前版本**: `v0`

## 当前评分维度
| 维度 | 权重 | 含义 |
|---|---:|---|
| emotional_resonance (ER) | 1 | 情绪 |
| social_resonance (SR) | 1 | 社会议题 |
| hook_potential (HP) | 1 | 开头 |
| quotable_lines (QL) | 1 | 金句 |
| narrativity (NA) | 1 | 叙事 |
| audience_breadth (AB) | 1 | 受众 |
| satire_depth (SAT) | 1 | 反讽 |
"""

V2_RUBRIC = """
rubric_version: v2
dimensions: [ER, SR, HP, QL, NA, AB, SAT, MS, TS]
"""


def score_payload(rubric_version: str = "v0", dimensions: tuple[str, ...] | None = None):
    names = dimensions or ("ER", "SR", "HP", "QL", "NA", "AB", "SAT")
    return {
        "subagent_version": "v1",
        "rubric_version": rubric_version,
        "script_path": "scripts/wechat-article-1.md",
        "script_hash": "a" * 12,
        "scored_at": "2026-08-05T12:00:00+08:00",
        "dimensions": {
            name: {"score": 4, "confidence": "high", "reason": "稿件开头有具体场景"}
            for name in names
        },
        "input_status": {
            "rubric_notes_read": True,
            "script_read": True,
            "any_other_file_read": False,
        },
        "self_check": {
            "saw_play_numbers": False,
            "saw_comments": False,
            "saw_retro_segment": False,
            "any_contamination_signal": False,
        },
        "refusal": None,
    }


class BlindScoreAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.rubric = self.root / "rubric_notes.md"
        self.rubric.write_text(V0_RUBRIC, encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_v0_seven_dimensions_pass_and_returns_contract(self):
        rubric = blind_score_adapter.parse_rubric(self.rubric)

        result = blind_score_adapter.validate_score(score_payload(), rubric)

        self.assertTrue(result["ok"])
        self.assertEqual(result["rubric_version"], "v0")
        self.assertEqual(result["dimension_count"], 7)

    def test_v2_nine_dimensions_pass_when_rubric_declares_them(self):
        rubric_path = self.root / "v2-rubric.md"
        rubric_path.write_text(V2_RUBRIC, encoding="utf-8")
        rubric = blind_score_adapter.parse_rubric(rubric_path)

        result = blind_score_adapter.validate_score(
            score_payload(
                "v2",
                ("ER", "SR", "HP", "QL", "NA", "AB", "SAT", "MS", "TS"),
            ),
            rubric,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["dimension_count"], 9)

    def test_wrong_dimension_set_is_rejected(self):
        rubric = blind_score_adapter.parse_rubric(self.rubric)
        payload = score_payload(dimensions=("ER", "SR", "HP", "QL", "NA", "AB", "MS"))

        with self.assertRaisesRegex(blind_score_adapter.BlindScoreError, "dimension set mismatch"):
            blind_score_adapter.validate_score(payload, rubric)

    def test_wrong_rubric_version_is_rejected(self):
        rubric = blind_score_adapter.parse_rubric(self.rubric)

        with self.assertRaisesRegex(blind_score_adapter.BlindScoreError, "rubric_version mismatch"):
            blind_score_adapter.validate_score(score_payload("v2"), rubric)

    def test_bad_score_and_composite_field_are_rejected(self):
        rubric = blind_score_adapter.parse_rubric(self.rubric)
        payload = score_payload()
        payload["dimensions"]["ER"]["score"] = 6
        with self.assertRaisesRegex(blind_score_adapter.BlindScoreError, "score must"):
            blind_score_adapter.validate_score(payload, rubric)

        payload = score_payload()
        payload["composite"] = 8.0
        with self.assertRaisesRegex(blind_score_adapter.BlindScoreError, "unsupported fields"):
            blind_score_adapter.validate_score(payload, rubric)

    def test_script_hash_can_be_verified_against_file(self):
        rubric = blind_score_adapter.parse_rubric(self.rubric)
        script = self.root / "script.md"
        script.write_text("# script\n", encoding="utf-8")
        payload = score_payload()
        payload["script_hash"] = hashlib.sha256(script.read_bytes()).hexdigest()[:12]

        result = blind_score_adapter.validate_score(payload, rubric, script)

        self.assertTrue(result["ok"])

    def test_rubric_without_version_or_dimensions_fails_closed(self):
        bad = self.root / "bad-rubric.md"
        bad.write_text("# rubric\n", encoding="utf-8")

        with self.assertRaisesRegex(blind_score_adapter.BlindScoreError, "rubric_version"):
            blind_score_adapter.parse_rubric(bad)


if __name__ == "__main__":
    unittest.main()
