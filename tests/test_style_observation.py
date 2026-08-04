from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
STYLE_ROOT = SKILL_ROOT / "companion-skills" / "wechat-style-learning"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import profile_adapter


def _load_style_learning():
    path = STYLE_ROOT / "scripts" / "edit_learning.py"
    spec = importlib.util.spec_from_file_location("edit_learning_observation", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


edit_learning = _load_style_learning()


class StyleObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cheat = self.root / "cheat"
        self.cheat.mkdir()
        (self.cheat / ".cheat-state.json").write_text("{}\n", encoding="utf-8")
        self.profile = self.root / "profile"
        profile_adapter.create_profile(
            self.profile, "observation-account", self.cheat, approved=True
        )

    def tearDown(self):
        self.temp.cleanup()

    def _observe(self, article_id: str, text: str):
        final = self.root / f"{article_id}.md"
        final.write_text(text, encoding="utf-8")
        return edit_learning.observe_final(
            self.profile,
            final,
            article_id,
            [
                {
                    "key": "dry_self_deprecation",
                    "type": "tone",
                    "instruction": "在严肃判断后用低频自嘲放松语气，并立即回到论证。",
                }
            ],
            timestamp=datetime(2026, 8, 1, tzinfo=timezone.utc),
        )

    def test_new_profile_initializes_observation_ledger(self):
        index_path = self.profile / "history" / "voice-observations" / "index.json"
        self.assertEqual(
            json.loads(index_path.read_text(encoding="utf-8")),
            {"schema_version": "1.0", "items": []},
        )

    def test_final_observation_is_body_free_and_soft(self):
        result = self._observe("article-one", "# 标题\n\n正文内容。\n")
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["observations"][0]["status"], "observed")
        index_path = self.profile / "history" / "voice-observations" / "index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        self.assertEqual(len(index["items"]), 1)
        lesson = json.loads(
            (self.profile / index["items"][0]["source_ref"]).read_text(
                encoding="utf-8"
            )
        )
        self.assertNotIn("正文内容", json.dumps(lesson, ensure_ascii=False))
        self.assertNotIn(str(self.root), json.dumps(lesson, ensure_ascii=False))

    def test_repeated_final_observation_becomes_candidate_after_three_articles(self):
        for article_id in ("article-one", "article-two", "article-three"):
            self._observe(article_id, f"# {article_id}\n\n不同正文。\n")
        observations = edit_learning.aggregate_observations(self.profile)
        self.assertEqual(observations[0]["article_count"], 3)
        self.assertEqual(observations[0]["status"], "candidate")

    def test_same_final_hash_is_idempotent(self):
        first = self._observe("article-one", "# 标题\n\n固定正文。\n")
        second = self._observe("article-one", "# 标题\n\n固定正文。\n")
        self.assertEqual(first["status"], "observed")
        self.assertEqual(second["status"], "already_observed")
        index_path = self.profile / "history" / "voice-observations" / "index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        self.assertEqual(len(index["items"]), 1)

    def test_corrupted_instruction_is_rejected(self):
        final = self.root / "corrupted.md"
        final.write_text("# 标题\n\n正文。\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "corrupted text"):
            edit_learning.observe_final(
                self.profile,
                final,
                "corrupted",
                [
                    {
                        "key": "corrupted_rule",
                        "type": "tone",
                        "instruction": "????????????",
                    }
                ],
            )


class StyleContractTests(unittest.TestCase):
    def test_khazix_is_assistant_not_author_voice(self):
        routing = (SKILL_ROOT / "references" / "skill-routing.md").read_text(
            encoding="utf-8"
        )
        style = (SKILL_ROOT / "references" / "writing-style.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Required craft assistant", routing)
        self.assertIn("不是作者人格", style)
        self.assertNotIn("khazix-writer` as the sole author voice", routing)

    def test_continuous_learning_contract_is_documented(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        style = (SKILL_ROOT / "references" / "writing-style.md").read_text(
            encoding="utf-8"
        )
        learning = (
            SKILL_ROOT
            / "companion-skills"
            / "wechat-style-learning"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        for text in (skill, style, learning):
            self.assertIn("observe-final", text)
        self.assertIn("history/voice-observations", learning)


if __name__ == "__main__":
    unittest.main()
