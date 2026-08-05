from __future__ import annotations

import stat
import sys
import tempfile
import unittest
import json
from hashlib import sha256
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import article_state
import cheat_form_adapter
from cheat_prediction_adapter import SnapshotError, create_snapshot


class CheatPredictionAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "article"
        self.cheat = self.root / "cheat"
        self.cheat.mkdir()
        (self.cheat / ".cheat-state.json").write_text(
            '{"schema_version":"1.2"}\n', encoding="utf-8"
        )
        self.state = article_state.create_project(
            self.project, "article-1", "full", None, "primary"
        )
        self.final = self.project / "drafts" / "final.md"
        self.final.write_text("# Approved final\n\n正文。\n", encoding="utf-8")
        article_state.record_artifact(
            self.state, self.project, "final", Path("drafts/final.md")
        )
        article_state.record_approval(
            self.state, "final", "2026-08-05T10:00:00+08:00"
        )
        article_state.write_state(self.project, self.state)
        self.form_status = self.root / "form-status.json"
        self.form_status.write_text(
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
                    "checked_at": "2026-08-05T15:00:00+08:00",
                }
            ),
            encoding="utf-8",
        )
        cheat_form_adapter.record_form(
            self.project, self.cheat, self.form_status, "primary"
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_creates_hash_bound_read_only_cheat_input_and_idempotently_reuses_it(self):
        receipt = create_snapshot(self.project, self.cheat)
        snapshot = self.cheat / receipt["snapshot_path"]

        self.assertTrue(snapshot.is_file())
        self.assertEqual(
            receipt["final_sha256"], self.state["artifacts"]["final"]["sha256"]
        )
        self.assertEqual(
            receipt["snapshot_sha256"], sha256(snapshot.read_bytes()).hexdigest()
        )
        self.assertTrue(receipt["read_only"])
        self.assertEqual(snapshot.stat().st_mode & stat.S_IWUSR, 0)
        text = snapshot.read_text(encoding="utf-8")
        self.assertIn('source_path: "drafts/final.md"', text)
        self.assertIn("# Approved final", text)
        receipt_path = self.project / "prediction-input-reference.json"
        receipt_text = receipt_path.read_text(encoding="utf-8")

        second = create_snapshot(self.project, self.cheat)
        self.assertEqual(second["snapshot_path"], receipt["snapshot_path"])
        self.assertEqual(receipt_path.read_text(encoding="utf-8"), receipt_text)

    def test_rejects_final_bytes_when_approval_hash_is_stale(self):
        self.final.write_text("# Changed after approval\n", encoding="utf-8")

        with self.assertRaisesRegex(SnapshotError, "approved SHA256"):
            create_snapshot(self.project, self.cheat)
        self.assertFalse((self.cheat / "scripts").exists())

    def test_rejects_approval_hash_mismatch_before_writing(self):
        self.state["approvals"]["final"]["artifact_sha256"] = "0" * 64
        article_state.write_state(self.project, self.state)

        with self.assertRaisesRegex(SnapshotError, "approval hash"):
            create_snapshot(self.project, self.cheat)
        self.assertFalse((self.cheat / "scripts").exists())

    def test_rejects_prediction_when_form_adaptation_receipt_is_missing(self):
        (self.project / "cheat-form-receipt.json").unlink()
        with self.assertRaisesRegex(SnapshotError, "form and rubric adaptation"):
            create_snapshot(self.project, self.cheat)
        self.assertFalse((self.cheat / "scripts").exists())


if __name__ == "__main__":
    unittest.main()
