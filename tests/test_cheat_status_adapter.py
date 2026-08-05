from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import cheat_status_adapter


class CheatStatusAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cheat = self.root / "cheat"
        self.cheat.mkdir()
        (self.cheat / ".cheat-state.json").write_text(
            '{"schema_version":"1.2"}\n', encoding="utf-8"
        )
        self.account = self.root / "account"
        self.account.mkdir()
        self.status = self.root / "status.json"
        self.status.write_text(
            json.dumps(
                {
                    "source": "cheat-status",
                    "target_project_binding": "primary",
                    "cheat_schema_version": "1.2",
                    "status": "compatible",
                    "checked_at": "2026-08-05T15:00:00+08:00",
                    "dashboard": "ignored by the normalizer",
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_record_writes_portable_post_migrate_receipt(self):
        result = cheat_status_adapter.record_status(
            self.account, self.cheat, self.status, "primary"
        )
        receipt_path = self.account / "cheat-status-receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(result["receipt_path"], "cheat-status-receipt.json")
        self.assertEqual(receipt["schema_version"], "1.0")
        self.assertEqual(receipt["receipt_type"], "post-migrate-cheat-status")
        self.assertEqual(receipt["target_project_binding"], "primary")
        self.assertEqual(receipt["cheat_schema_version"], "1.2")
        self.assertEqual(receipt["status"], "compatible")
        self.assertEqual(receipt["source"], "cheat-status")
        self.assertEqual(receipt["checked_at"], "2026-08-05T15:00:00+08:00")
        self.assertNotIn(str(self.root), receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(
            cheat_status_adapter.validate_receipt(receipt, "primary", self.cheat),
            receipt,
        )

    def test_record_is_idempotent(self):
        first = cheat_status_adapter.record_status(
            self.account, self.cheat, self.status, "primary"
        )
        first_text = (self.account / "cheat-status-receipt.json").read_text(
            encoding="utf-8"
        )
        second = cheat_status_adapter.record_status(
            self.account, self.cheat, self.status, "primary"
        )
        self.assertEqual(second, first)
        self.assertEqual(
            (self.account / "cheat-status-receipt.json").read_text(encoding="utf-8"),
            first_text,
        )

    def test_incompatible_status_is_rejected(self):
        payload = json.loads(self.status.read_text(encoding="utf-8"))
        payload["status"] = "incompatible"
        self.status.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(
            cheat_status_adapter.StatusReceiptError, "must be compatible"
        ):
            cheat_status_adapter.record_status(
                self.account, self.cheat, self.status, "primary"
            )

    def test_live_schema_mismatch_is_rejected(self):
        payload = json.loads(self.status.read_text(encoding="utf-8"))
        payload["cheat_schema_version"] = "1.3"
        self.status.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(
            cheat_status_adapter.StatusReceiptError, "does not match"
        ):
            cheat_status_adapter.record_status(
                self.account, self.cheat, self.status, "primary"
            )

    def test_path_like_binding_and_timezone_less_time_are_rejected(self):
        payload = json.loads(self.status.read_text(encoding="utf-8"))
        payload["target_project_binding"] = "C:/secret/project"
        self.status.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(cheat_status_adapter.StatusReceiptError):
            cheat_status_adapter.record_status(
                self.account, self.cheat, self.status, "primary"
            )

        payload["target_project_binding"] = "primary"
        payload["checked_at"] = "2026-08-05T15:00:00"
        self.status.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(
            cheat_status_adapter.StatusReceiptError, "timezone"
        ):
            cheat_status_adapter.record_status(
                self.account, self.cheat, self.status, "primary"
            )


if __name__ == "__main__":
    unittest.main()
