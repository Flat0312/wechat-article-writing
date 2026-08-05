from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import craft_only_adapter
import humanizer_diagnostic_adapter


class WritingAdapterTests(unittest.TestCase):
    def setUp(self):
        self.draft = SKILL_ROOT / "tests" / "_adapter-draft-fixture.md"
        self.draft.write_text("# Draft\n\n事实段落。\n", encoding="utf-8")
        self.draft_hash = hashlib.sha256(self.draft.read_bytes()).hexdigest()

    def tearDown(self):
        self.draft.unlink(missing_ok=True)

    def test_craft_adapter_accepts_only_bounded_suggestions(self):
        result = craft_only_adapter.validate_payload(
            {
                "schema_version": "1.0",
                "source_skill": "khazix-writer",
                "mode": "craft-only",
                "suggestions": [
                    {
                        "kind": "transition",
                        "section_ref": "section-2",
                        "text": "让转场由上一节的因果后果推动。",
                    }
                ],
            }
        )
        self.assertTrue(result["accepted_for_integration"])
        self.assertEqual(result["draft_owner"], "wechat-article-writing")

    def test_craft_adapter_rejects_full_draft_and_external_identity(self):
        full_draft = {
            "schema_version": "1.0",
            "source_skill": "khazix-writer",
            "mode": "craft-only",
            "suggestions": [],
            "draft": "全文",
        }
        with self.assertRaisesRegex(craft_only_adapter.CraftContractError, "only"):
            craft_only_adapter.validate_payload(full_draft)

        identity = {
            "schema_version": "1.0",
            "source_skill": "khazix-writer",
            "mode": "craft-only",
            "suggestions": [
                {"kind": "scene", "text": "用数字生命卡兹克的固定口吻。"}
            ],
        }
        with self.assertRaisesRegex(craft_only_adapter.CraftContractError, "identity"):
            craft_only_adapter.validate_payload(identity)

    def test_humanizer_adapter_binds_a_local_diagnostic_to_current_draft(self):
        result = humanizer_diagnostic_adapter.validate_payload(
            {
                "schema_version": "1.0",
                "source_skill": "humanizer-zh",
                "mode": "diagnostic",
                "input_sha256": self.draft_hash,
                "issues": [
                    {
                        "location": "paragraph:2",
                        "pattern": "机械连接词",
                        "suggestion": "删除连接词，让因果关系承担转场。",
                        "scope": "local",
                        "adds_facts": False,
                        "changes_meaning": False,
                        "severity": "low",
                    }
                ],
            },
            self.draft,
        )
        self.assertTrue(result["requires_local_rewrite"])
        self.assertEqual(result["input_sha256"], self.draft_hash)

    def test_humanizer_adapter_rejects_rewrite_and_stale_or_fact_changing_advice(self):
        base = {
            "schema_version": "1.0",
            "source_skill": "humanizer-zh",
            "mode": "diagnostic",
            "input_sha256": self.draft_hash,
            "issues": [],
        }
        with self.assertRaisesRegex(humanizer_diagnostic_adapter.DiagnosticContractError, "only"):
            humanizer_diagnostic_adapter.validate_payload({**base, "rewritten_text": "全文"})

        with self.assertRaisesRegex(humanizer_diagnostic_adapter.DiagnosticContractError, "does not match"):
            humanizer_diagnostic_adapter.validate_payload(
                base, SKILL_ROOT / "SKILL.md"
            )

        fact_changing = {
            **base,
            "issues": [
                {
                    "location": "paragraph:2",
                    "pattern": "空泛",
                    "suggestion": "加入一个用户没有提供的经历。",
                    "scope": "local",
                    "adds_facts": True,
                    "changes_meaning": False,
                }
            ],
        }
        with self.assertRaisesRegex(humanizer_diagnostic_adapter.DiagnosticContractError, "adds_facts"):
            humanizer_diagnostic_adapter.validate_payload(fact_changing)


if __name__ == "__main__":
    unittest.main()
