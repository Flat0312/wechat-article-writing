from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import article_state
import visual_asset_adapter


def png_header(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x06\x00\x00\x00"
    )


class VisualAssetAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "article"
        article_state.create_project(
            self.project, "article-1", "full", None, "cheat-project"
        )

    def tearDown(self):
        self.temp.cleanup()

    def _write_png(self, path: Path, width: int, height: int) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(png_header(width, height))
        return path

    def test_cover_accepts_one_21x9_asset_and_writes_manifest(self):
        route_output = self.root / "guizang-output"
        source = self._write_png(route_output / "wechat-21x9-cover.png", 2100, 900)

        result = visual_asset_adapter.prepare_cover(
            self.project, source, route_output, "guizang"
        )

        delivery = self.project / "visuals" / "assets" / "cover.png"
        manifest = json.loads(
            (self.project / "visuals" / "assets" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["delivery_path"], "visuals/assets/cover.png")
        self.assertTrue(delivery.is_file())
        self.assertEqual(manifest["cover"]["asset_id"], "wechat-cover-21x9")
        self.assertEqual(manifest["cover"]["aspect_ratio"], "21:9")
        self.assertEqual(manifest["body"], [])

    def test_cover_rejects_square_pair_output(self):
        route_output = self.root / "guizang-output"
        source = self._write_png(route_output / "wechat-21x9-cover.png", 2100, 900)
        self._write_png(route_output / "wechat-1x1-cover.png", 1080, 1080)

        with self.assertRaisesRegex(visual_asset_adapter.VisualAssetError, "forbidden"):
            visual_asset_adapter.prepare_cover(
                self.project, source, route_output, "guizang"
            )

    def test_cover_rejects_wrong_ratio(self):
        route_output = self.root / "guizang-output"
        source = self._write_png(route_output / "cover.png", 1000, 1000)

        with self.assertRaisesRegex(visual_asset_adapter.VisualAssetError, "21:9"):
            visual_asset_adapter.prepare_cover(
                self.project, source, route_output, "guizang"
            )

    def test_cover_rejects_different_bytes_without_replacing_delivery(self):
        first_output = self.root / "guizang-first"
        first_source = self._write_png(
            first_output / "cover.png", 2100, 900
        )
        visual_asset_adapter.prepare_cover(
            self.project, first_source, first_output, "guizang"
        )
        delivery = self.project / "visuals" / "assets" / "cover.png"
        original = delivery.read_bytes()

        second_output = self.root / "guizang-second"
        second_source = self._write_png(
            second_output / "cover.png", 2100, 900
        )
        second_source.write_bytes(second_source.read_bytes() + b"different")

        with self.assertRaisesRegex(visual_asset_adapter.VisualAssetError, "different cover"):
            visual_asset_adapter.prepare_cover(
                self.project, second_source, second_output, "guizang"
            )
        self.assertEqual(delivery.read_bytes(), original)

    def test_body_routes_are_copied_and_indexed_together(self):
        ian_source = self._write_png(self.root / "ian-result.png", 1600, 900)
        baoyu_source = self._write_png(self.root / "baoyu-result.png", 1200, 800)

        visual_asset_adapter.register_body(
            self.project,
            "ian",
            ian_source,
            "anchor-emotion",
            "narrative tension",
            "renders/ian-result.png",
        )
        visual_asset_adapter.register_body(
            self.project,
            "baoyu",
            baoyu_source,
            "anchor-flow",
            "ordered steps",
        )

        manifest = json.loads(
            (self.project / "visuals" / "assets" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            [item["route"] for item in manifest["body"]], ["ian", "baoyu"]
        )
        self.assertTrue(
            (self.project / "visuals" / "assets" / "ian" / "ian-anchor-emotion.png").is_file()
        )
        self.assertTrue(
            (self.project / "visuals" / "assets" / "baoyu" / "baoyu-anchor-flow.png").is_file()
        )
        self.assertNotIn(str(self.project), json.dumps(manifest))


if __name__ == "__main__":
    unittest.main()
