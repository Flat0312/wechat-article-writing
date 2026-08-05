from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import cheat_form_adapter


class CheatFormAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cheat = self.root / "cheat"
        self.cheat.mkdir()
        (self.cheat / ".cheat-state.json").write_text(
            '{"schema_version":"1.2"}\n', encoding="utf-8"
        )
        self.article = self.root / "article"
        self.article.mkdir()
        self.status = self.root / "form-status.json"
        self.status.write_text(
            json.dumps(
                {
                    "source": "cheat-on-content",
                    "root_skill_called": True,
                    "root_route": "cheat-init",
                    "root_call_status": "completed",
                    "target_project_binding": "primary",
                    "content_form": "long-essay",
                    "cheat_schema_version": "1.2",
                    "rubric_adapter": "wechat-long-essay-v1",
                    "rubric_status": "compatible",
                    "rubric_version": "v1",
                    "rubric_form_mismatch": False,
                    "checked_at": "2026-08-05T15:00:00+08:00",
                    "dashboard": "ignored",
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_record_separates_root_call_and_rubric_status(self):
        result = cheat_form_adapter.record_form(
            self.article, self.cheat, self.status, "primary"
        )
        receipt = json.loads(
            (self.article / "cheat-form-receipt.json").read_text(encoding="utf-8")
        )
        self.assertEqual(result["receipt_path"], "cheat-form-receipt.json")
        self.assertEqual(receipt["source"], "cheat-on-content")
        self.assertTrue(receipt["root_skill_called"])
        self.assertEqual(receipt["root_call_status"], "completed")
        self.assertEqual(receipt["rubric_status"], "compatible")
        self.assertEqual(receipt["content_form"], "long-essay")
        self.assertEqual(
            cheat_form_adapter.validate_receipt(receipt, "primary", self.cheat),
            receipt,
        )

    def test_record_is_idempotent_and_rejects_a_different_receipt(self):
        first = cheat_form_adapter.record_form(
            self.article, self.cheat, self.status, "primary"
        )
        second = cheat_form_adapter.record_form(
            self.article, self.cheat, self.status, "primary"
        )
        self.assertEqual(first, second)
        changed = json.loads(self.status.read_text(encoding="utf-8"))
        changed["rubric_version"] = "v2"
        self.status.write_text(json.dumps(changed), encoding="utf-8")
        with self.assertRaisesRegex(cheat_form_adapter.FormReceiptError, "already binds"):
            cheat_form_adapter.record_form(
                self.article, self.cheat, self.status, "primary"
            )

    def test_opinion_video_mismatch_cannot_be_marked_as_long_essay_compatible(self):
        payload = json.loads(self.status.read_text(encoding="utf-8"))
        payload["rubric_form_mismatch"] = True
        self.status.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(cheat_form_adapter.FormReceiptError, "mismatch"):
            cheat_form_adapter.record_form(
                self.article, self.cheat, self.status, "primary"
            )

        payload["rubric_form_mismatch"] = False
        payload["rubric_adapter"] = "opinion-video-v1"
        self.status.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(cheat_form_adapter.FormReceiptError, "not for"):
            cheat_form_adapter.record_form(
                self.article, self.cheat, self.status, "primary"
            )


if __name__ == "__main__":
    unittest.main()
