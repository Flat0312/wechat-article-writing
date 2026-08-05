from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import article_state
import cheat_form_adapter
import craft_only_adapter
import humanizer_diagnostic_adapter
import visual_asset_adapter
import validate_project


FIXTURE = SKILL_ROOT / "tests" / "fixtures" / "external_contracts.json"
EXPECTED_EXTERNAL = {
    "cheat-on-content",
    "creator-buddy",
    "gzh-explosive-content-detector",
    "aihot",
    "khazix-writer",
    "humanizer-zh",
    "guizang-social-card-skill",
    "ian-xiaohei-illustrations",
    "baoyu-article-illustrator",
    "gzh-design",
    "x-tweet-fetcher",
}
EXPECTED_LANES = {
    "creator-buddy-cross-platform",
    "gzh-explosive-content-detector",
    "aihot",
    "x-tweet-fetcher",
    "cheat-trends",
}


def _load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _assert_portable_paths(test: unittest.TestCase, value: object) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _assert_portable_paths(test, item)
    elif isinstance(value, list):
        for item in value:
            _assert_portable_paths(test, item)
    elif isinstance(value, str) and ("/" in value or "\\" in value):
        path = PurePosixPath(value.replace("\\", "/"))
        test.assertFalse(path.is_absolute(), value)
        test.assertNotIn("..", path.parts, value)
        test.assertFalse(len(value) > 1 and value[1] == ":", value)


class ExternalContractFixtureTests(unittest.TestCase):
    def test_fixture_covers_external_skills_and_portable_receipts(self):
        payload = _load_fixture()
        self.assertEqual(payload["schema_version"], "1.0")
        self.assertEqual(payload["fixture_kind"], "offline-normalized-boundary")
        contracts = payload["contracts"]
        self.assertEqual(set(contracts), EXPECTED_EXTERNAL)
        for skill, contract in contracts.items():
            self.assertTrue(contract["input"], skill)
            self.assertIn(
                contract["output"].get("status", "response"),
                {"completed", "not_applicable", "blocked", "response"},
            )
            _assert_portable_paths(self, contract)

    def test_fixture_declares_all_five_topic_lanes(self):
        contracts = _load_fixture()["contracts"]
        lanes = {
            contracts["creator-buddy"]["input"]["lane"],
            contracts["gzh-explosive-content-detector"]["input"]["lane"],
            contracts["aihot"]["input"]["lane"],
            contracts["x-tweet-fetcher"]["input"]["lane"],
            "cheat-trends",
        }
        self.assertEqual(lanes, EXPECTED_LANES)
        override = contracts["creator-buddy"]["input"]["route_override"]
        self.assertEqual(override["provider"], "xiaohongshu-skill")
        self.assertFalse(override["allow_fallback"])

    def test_writing_and_form_fixtures_pass_total_control_adapters(self):
        contracts = _load_fixture()["contracts"]
        self.assertTrue(
            craft_only_adapter.validate_payload(
                contracts["khazix-writer"]["output"]
            )["accepted_for_integration"]
        )
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.md"
            draft.write_text("# Draft\n\nLocal text.\n", encoding="utf-8")
            humanizer = dict(contracts["humanizer-zh"]["output"])
            humanizer["input_sha256"] = hashlib.sha256(draft.read_bytes()).hexdigest()
            result = humanizer_diagnostic_adapter.validate_payload(humanizer, draft)
            self.assertTrue(result["requires_local_rewrite"])

            article = Path(temp) / "article"
            cheat = Path(temp) / "cheat"
            article.mkdir()
            cheat.mkdir()
            (cheat / ".cheat-state.json").write_text(
                '{"schema_version":"1.2"}\n', encoding="utf-8"
            )
            status_path = Path(temp) / "cheat-form.json"
            status_path.write_text(
                json.dumps(contracts["cheat-on-content"]["form_receipt"]),
                encoding="utf-8",
            )
            receipt = cheat_form_adapter.record_form(
                article, cheat, status_path, "primary"
            )
            self.assertEqual(receipt["rubric_status"], "compatible")

    def test_fixture_paths_match_prediction_publish_retro_html_and_cover_contracts(self):
        contracts = _load_fixture()["contracts"]
        cheat_paths = contracts["cheat-on-content"]["output"]["paths"]
        for required in (
            "prediction-input-reference.json",
            "publish-reference.json",
            "metrics.json",
            "retro/article-1.md",
        ):
            self.assertIn(required, cheat_paths)
        html_paths = contracts["gzh-design"]["output"]["paths"]
        self.assertEqual(tuple(html_paths), validate_project.HTML_DELIVERY_FILES)
        self.assertEqual(
            contracts["guizang-social-card-skill"]["input"]["asset_contract"],
            "one-static-21x9",
        )

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "article"
            article_state.create_project(project, "article-1", "full", None, "primary")
            route = root / "guizang-output"
            route.mkdir()
            source = route / "wechat-21x9-cover.png"
            source.write_bytes(
                b"\x89PNG\r\n\x1a\n"
                + (13).to_bytes(4, "big")
                + b"IHDR"
                + (2100).to_bytes(4, "big")
                + (900).to_bytes(4, "big")
                + b"\x08\x06\x00\x00\x00"
            )
            result = visual_asset_adapter.prepare_cover(
                project, source, route, "guizang"
            )
            self.assertEqual(result["delivery_path"], "visuals/assets/cover.png")


if __name__ == "__main__":
    unittest.main()
