from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import upgrade_preview_copy
import validate_html_delivery
import wrap_preview


class WrapPreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "article.html"
        self.preview = self.root / "article-preview.html"

    def tearDown(self):
        self.temp.cleanup()

    def test_wraps_section_in_upgrade_compatible_preview(self):
        fragment = '<section><p><span leaf="">正文</span></p></section>'
        self.source.write_text(fragment, encoding="utf-8")

        wrap_preview.wrap_preview(self.source, self.preview)

        html = self.preview.read_text(encoding="utf-8")
        self.assertIn("<!doctype html>", html.lower())
        self.assertIn('<div id="gzh-content">', html)
        self.assertIn('id="gzhCopyBtn"', html)
        self.assertIn(fragment, html)
        self.assertEqual(self.source.read_text(encoding="utf-8"), fragment)
        self.assertTrue(upgrade_preview_copy.upgrade_preview(self.preview))
        upgraded = self.preview.read_text(encoding="utf-8")
        self.assertIn(
            "window.gzhCopy = async function wechatArticleRichCopy()",
            upgraded,
        )

    def test_cli_accepts_input_and_output_paths(self):
        self.source.write_text("<section>正文</section>\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(SKILL_ROOT / "scripts" / "wrap_preview.py"),
                str(self.source),
                str(self.preview),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.preview.is_file())
        self.assertEqual(json.loads(result.stdout)["ok"], True)

    def test_generated_previews_pass_five_file_delivery_gate(self):
        output = self.root / "output"
        output.mkdir()
        article = output / "article.html"
        article_copy = output / "article-copy.html"
        article_preview = output / "article-preview.html"
        copy_preview = output / "article-copy-preview.html"
        fragment = '<section><p><span leaf="">正文</span></p></section>\n'
        article.write_text(fragment, encoding="utf-8")
        article_copy.write_text(fragment, encoding="utf-8")
        wrap_preview.wrap_preview(article, article_preview)
        wrap_preview.wrap_preview(article_copy, copy_preview)
        upgrade_preview_copy.upgrade_preview(copy_preview)
        (output / "html-qc.md").write_text(
            "# HTML QC\n\noutput/article.html\n\n"
            "- validate_project: 通过\n- author_cta: disabled\n",
            encoding="utf-8",
        )
        state = {
            "current_stage": "html",
            "stage_status": {"html": "in_progress"},
            "artifacts": {},
        }

        self.assertEqual(
            validate_html_delivery.check_html_delivery(self.root, state),
            [],
        )

    def test_rejects_non_section_input_without_creating_output(self):
        self.source.write_text("<p>正文</p>\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "<section>"):
            wrap_preview.wrap_preview(self.source, self.preview)

        self.assertFalse(self.preview.exists())


if __name__ == "__main__":
    unittest.main()
