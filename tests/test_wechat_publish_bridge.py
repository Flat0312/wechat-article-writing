from __future__ import annotations

import json
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import article_state
from wechat_publish_bridge import PublishError, record_wechat_publish


class WeChatPublishBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "articles" / "article-1"
        self.cheat = self.root / "cheat"
        self.cheat.mkdir()
        self.state = article_state.create_project(
            self.project, "article-1", "full", None, "primary"
        )
        self.state["stage_status"]["html"] = "completed"
        article_state.write_state(self.project, self.state)
        self.prediction = self.cheat / "predictions" / "v1.md"
        self.prediction.parent.mkdir()
        self.prediction.write_text("# Prediction\n", encoding="utf-8")
        self.prediction_hash = sha256(self.prediction.read_bytes()).hexdigest()
        self.cheat_receipt = {
            "status": "published",
            "platform": "wechat",
            "prediction_file": "predictions/v1.md",
            "prediction_sha256": self.prediction_hash,
            "published_at": "2026-08-05T12:00:00+08:00",
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_success_writes_publish_records_and_state_hash(self):
        receipt = record_wechat_publish(
            self.project,
            self.cheat,
            self.cheat_receipt,
            "https://mp.weixin.qq.com/s/example",
            "2026-08-05T12:01:00+08:00",
            True,
        )

        publish = json.loads((self.project / "publish.json").read_text(encoding="utf-8"))
        reference = json.loads(
            (self.project / "publish-reference.json").read_text(encoding="utf-8")
        )
        state = json.loads((self.project / "article-state.json").read_text(encoding="utf-8"))
        publish_hash = sha256((self.project / "publish.json").read_bytes()).hexdigest()
        self.assertEqual(publish["platform"], "wechat")
        self.assertEqual(publish["status"], "publicly_published")
        self.assertEqual(reference["publish_json_sha256"], publish_hash)
        self.assertEqual(reference["publish_json_sha256"], receipt["publish_json_sha256"])
        self.assertEqual(state["artifacts"]["publish"]["sha256"], publish_hash)
        self.assertEqual(state["stage_status"]["publish"], "completed")
        self.assertEqual(publish["metrics_path"], "metrics.json")

    def test_missing_user_confirmation_does_not_write_public_record(self):
        with self.assertRaisesRegex(PublishError, "confirmation"):
            record_wechat_publish(
                self.project,
                self.cheat,
                self.cheat_receipt,
                "https://mp.weixin.qq.com/s/example",
                "2026-08-05T12:01:00+08:00",
                False,
            )
        self.assertFalse((self.project / "publish.json").exists())

    def test_prediction_hash_mismatch_does_not_write_public_record(self):
        bad_receipt = {**self.cheat_receipt, "prediction_sha256": "0" * 64}
        with self.assertRaisesRegex(PublishError, "SHA256"):
            record_wechat_publish(
                self.project,
                self.cheat,
                bad_receipt,
                "https://mp.weixin.qq.com/s/example",
                "2026-08-05T12:01:00+08:00",
                True,
            )
        self.assertFalse((self.project / "publish.json").exists())

    def test_non_wechat_url_is_rejected(self):
        with self.assertRaisesRegex(PublishError, "mp.weixin.qq.com"):
            record_wechat_publish(
                self.project,
                self.cheat,
                self.cheat_receipt,
                "https://example.com/article",
                "2026-08-05T12:01:00+08:00",
                True,
            )
        self.assertFalse((self.project / "publish.json").exists())


if __name__ == "__main__":
    unittest.main()
