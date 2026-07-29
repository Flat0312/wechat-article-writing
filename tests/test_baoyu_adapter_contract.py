from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import article_state
import baoyu_adapter


class BaoyuAdapterContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "article"
        self.state = article_state.create_project(
            self.project, "article-1", "full", None, "cheat-project"
        )
        self.final = self.project / "drafts" / "final.md"
        self.final.write_text("# 已批准最终稿\n", encoding="utf-8")
        article_state.record_artifact(
            self.state, self.project, "final", Path("drafts/final.md")
        )

    def tearDown(self):
        self.temp.cleanup()

    def _approve_final(self):
        article_state.record_approval(
            self.state, "final", "2026-07-29T12:00:00+08:00"
        )
        article_state.write_state(self.project, self.state)

    def test_prepare_requires_current_final_approval(self):
        with self.assertRaisesRegex(baoyu_adapter.AdapterError, "not approved"):
            baoyu_adapter.prepare(self.project)

    def test_prepare_copies_only_portable_snapshot_and_verify_passes(self):
        self._approve_final()

        result = baoyu_adapter.prepare(self.project)

        source = self.project / result["source_path"]
        receipt_path = self.project / result["receipt_path"]
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(source.read_bytes(), self.final.read_bytes())
        self.assertEqual(receipt["final_path"], "drafts/final.md")
        self.assertNotIn(str(self.project), receipt_path.read_text(encoding="utf-8"))
        self.assertTrue(baoyu_adapter.verify(self.project)["ok"])

    def test_prepare_rejects_invalid_output_parent(self):
        self._approve_final()
        (self.project / "visuals" / "assets" / "baoyu").write_text(
            "not a directory", encoding="utf-8"
        )

        with self.assertRaisesRegex(baoyu_adapter.AdapterError, "output path"):
            baoyu_adapter.prepare(self.project)

    def test_verify_detects_final_text_mutation(self):
        self._approve_final()
        baoyu_adapter.prepare(self.project)
        self.final.write_text("# 被意外改写的最终稿\n", encoding="utf-8")

        with self.assertRaisesRegex(baoyu_adapter.AdapterError, "hash does not match"):
            baoyu_adapter.verify(self.project)

    def test_verify_ignores_changes_to_the_isolated_copy(self):
        self._approve_final()
        result = baoyu_adapter.prepare(self.project)
        (self.project / result["source_path"]).write_text(
            "# 外部 Skill 修改的隔离副本\n", encoding="utf-8"
        )

        self.assertTrue(baoyu_adapter.verify(self.project)["ok"])


if __name__ == "__main__":
    unittest.main()
