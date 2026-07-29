from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import upgrade_preview_copy


class PreviewCopyUpgradeTests(unittest.TestCase):
    def test_upgrade_injects_clipboard_wrapper(self):
        preview = self._write_text(
            f'<html><body><div id="gzh-content">body</div><button id="gzhCopyBtn">copy</button><script>{upgrade_preview_copy.EXPECTED_COPY_FUNCTION_TEXT}</script></body></html>'
        )
        self.assertEqual(upgrade_preview_copy.upgrade_preview(preview), True)
        html = preview.read_text(encoding="utf-8")
        self.assertIn("window.gzhCopy = async function wechatArticleRichCopy()", html)
        self.assertIn("navigator.clipboard.write", html)

    def test_already_upgraded_preview_is_idempotent(self):
        preview = self._write_text(
            f'<html><body><div id="gzh-content">body</div><button id="gzhCopyBtn">copy</button><script>{upgrade_preview_copy.EXPECTED_COPY_FUNCTION_TEXT}</script><script data-wechat-article-copy-upgrade="1">window.gzhCopy = async function wechatArticleRichCopy() {{}}</script></body></html>'
        )
        self.assertEqual(upgrade_preview_copy.upgrade_preview(preview), False)
        html = preview.read_text(encoding="utf-8")
        self.assertEqual(html.count('<script data-wechat-article-copy-upgrade="1">'), 1)
        self.assertIn("window.gzhCopy = async function wechatArticleRichCopy()", html)

    def test_known_function_sha_remains_accepted(self):
        preview = self._write_text(
            f'<html><body><div id="gzh-content">body</div><button id="gzhCopyBtn">copy</button><script>{upgrade_preview_copy.EXPECTED_COPY_FUNCTION_TEXT}</script></body></html>'
        )
        self.assertEqual(upgrade_preview_copy.upgrade_preview(preview), True)

    def test_compatible_stable_copy_function_is_accepted(self):
        script = (
            "function gzhCopy() {"
            + "\n  const selection = window.getSelection();\n  if (!selection.rangeCount) {\n    return false;\n  }\n  document.execCommand('copy');\n  return true;\n}\n"
            + "}"
        )
        preview = self._write_text(
            f'<html><body><div id="gzh-content">body</div><button id="gzhCopyBtn">copy</button><script>{script}</script></body></html>'
        )
        self.assertEqual(upgrade_preview_copy.upgrade_preview(preview), True)
        html = preview.read_text(encoding="utf-8")
        self.assertIn("window.gzhCopy = async function wechatArticleRichCopy()", html)
        self.assertIn("navigator.clipboard.write", html)

    def test_modified_copy_function_is_rejected(self):
        preview = self._write_text('<html><body><div id="gzh-content">body</div><button id="gzhCopyBtn">copy</button><script>function gzhCopy() { return true; }' + '\nconst extra = true;\n' + '</script></body></html>')
        with self.assertRaises(ValueError):
            upgrade_preview_copy.upgrade_preview(preview)

    def test_unknown_copy_function_is_rejected(self):
        preview = self._write_text('<html><body><div id="gzh-content">body</div><button id="gzhCopyBtn">copy</button><script>function gzhCopy() { return true; }</script></body></html>')
        with self.assertRaises(ValueError):
            upgrade_preview_copy.upgrade_preview(preview)

    def test_double_upgrade_is_rejected(self):
        preview = self._write_text(
            f'<html><body><div id="gzh-content">body</div><button id="gzhCopyBtn">copy</button><script>{upgrade_preview_copy.EXPECTED_COPY_FUNCTION_TEXT}</script><script data-wechat-article-copy-upgrade="1">extra</script></body></html>'
        )
        with self.assertRaises(ValueError):
            upgrade_preview_copy.upgrade_preview(preview)

    def _write_text(self, html: str) -> Path:
        path = Path(self.temp.name) / "preview.html"
        path.write_text(html, encoding="utf-8")
        return path

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp.cleanup()


if __name__ == "__main__":
    unittest.main()
