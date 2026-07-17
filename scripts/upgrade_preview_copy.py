#!/usr/bin/env python3
"""Upgrade a gzh-design preview to copy explicit rich HTML.

The current gzh-design preview uses a DOM selection plus execCommand("copy").
Chromium can flatten block elements during that copy. This post-processor leaves
that function untouched and injects a wrapper that first writes explicit HTML.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import textwrap


UPGRADE_MARKER = '<script data-wechat-article-copy-upgrade="1">'
WRAPPER_SIGNATURE = "window.gzhCopy = async function wechatArticleRichCopy()"
SCRIPT_BLOCK = re.compile(r"(?is)<script(?:\s[^>]*)?>(.*?)</script>")
COPY_FUNCTION = re.compile(r"(?m)^[ \t]*function gzhCopy\(\)\s*\{")
KNOWN_GZH_COPY_SHA256 = {
    "e575eedeb599b666f9fa09f35bec432b78f0081b5015ae17723e95e5290d02c8"
}

WRAPPER = """
<script data-wechat-article-copy-upgrade="1">
  (() => {
    const fallbackCopy = window.gzhCopy;
    if (typeof fallbackCopy !== 'function') {
      throw new Error('gzhCopy fallback is unavailable');
    }
    window.gzhCopy = async function wechatArticleRichCopy() {
      const el = document.getElementById('gzh-content');
      const btn = document.getElementById('gzhCopyBtn');
      const oldText = btn.textContent;
      try {
        await navigator.clipboard.write([new ClipboardItem({
          'text/html': new Blob([el.innerHTML], {type: 'text/html'}),
          'text/plain': new Blob([el.innerText], {type: 'text/plain'})
        })]);
        btn.dataset.wechatCopyMethod = 'clipboard-api';
        if (typeof window.gzhShowToast === 'function') {
          window.gzhShowToast('✅ 已复制富文本，可粘贴到公众号');
        }
        btn.textContent = '✅ 已复制';
        window.setTimeout(() => { btn.textContent = oldText; }, 2200);
        return true;
      } catch (error) {
        btn.dataset.wechatCopyMethod = 'legacy-fallback';
        return fallbackCopy.apply(this, arguments);
      }
    };
  })();
</script>
"""


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.tmp-",
            delete=False,
        ) as handle:
            handle.write(text)
            temporary_path = Path(handle.name)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _has_recognized_copy_function(html: str) -> bool:
    for block in SCRIPT_BLOCK.findall(html):
        declaration = COPY_FUNCTION.search(block)
        if declaration is None:
            continue
        candidate = _extract_braced_function(block, declaration.start())
        if candidate is None:
            return False
        return _copy_fingerprint(candidate) in KNOWN_GZH_COPY_SHA256
    return False


def _copy_fingerprint(candidate: str) -> str:
    normalized = textwrap.dedent(
        candidate.replace("\r\n", "\n").replace("\r", "\n")
    )
    normalized = "\n".join(
        line.rstrip() for line in normalized.split("\n")
    ).strip() + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _extract_braced_function(script: str, start: int) -> str | None:
    opening = script.find("{", start)
    if opening < 0:
        return None

    depth = 0
    state = "code"
    quote = ""
    index = opening
    while index < len(script):
        char = script[index]
        following = script[index + 1] if index + 1 < len(script) else ""

        if state == "code":
            if char in ("'", '"', "`"):
                state = "string"
                quote = char
            elif char == "/" and following == "/":
                state = "line-comment"
                index += 1
            elif char == "/" and following == "*":
                state = "block-comment"
                index += 1
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return script[start : index + 1]
        elif state == "string":
            if char == "\\":
                index += 1
            elif char == quote:
                state = "code"
        elif state == "line-comment":
            if char in ("\r", "\n"):
                state = "code"
        elif state == "block-comment" and char == "*" and following == "/":
            state = "code"
            index += 1

        index += 1
    return None


def upgrade_preview(path: Path) -> bool:
    preview = Path(path)
    original = preview.read_text(encoding="utf-8")

    marker_count = original.count(UPGRADE_MARKER)
    if marker_count == 1 and WRAPPER_SIGNATURE in original:
        return False
    if marker_count:
        raise ValueError("preview contains an invalid copy-upgrade marker")
    if "id=\"gzh-content\"" not in original or "gzhCopyBtn" not in original:
        raise ValueError("preview does not contain the expected gzhCopy controls")
    if not _has_recognized_copy_function(original):
        raise ValueError("preview does not contain the expected gzhCopy function")

    body_end = original.lower().rfind("</body>")
    if body_end < 0:
        raise ValueError("preview does not contain a closing body tag")
    upgraded = original[:body_end] + WRAPPER + original[body_end:]

    _atomic_write(preview, upgraded)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("preview", type=Path)
    args = parser.parse_args()
    changed = upgrade_preview(args.preview)
    print(
        json.dumps(
            {"ok": True, "changed": changed, "path": str(args.preview)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
