#!/usr/bin/env python3
"""Wrap a gzh-design section fragment in a browser preview shell."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from upgrade_preview_copy import EXPECTED_COPY_FUNCTION_TEXT


PREVIEW_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>微信公众号排版预览</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #f3f4f6; color: #111827; }
    .gzh-toolbar { position: sticky; top: 0; z-index: 10; display: flex; justify-content: flex-end; padding: 12px; background: rgba(255,255,255,.96); border-bottom: 1px solid #e5e7eb; }
    .gzh-copy { border: 0; border-radius: 8px; padding: 10px 16px; background: #059669; color: #fff; font-weight: 700; cursor: pointer; }
    .gzh-stage { max-width: 700px; margin: 24px auto 64px; padding: 0 8px; }
    #gzh-content { background: #fff; }
    .gzh-toast { position: fixed; top: 68px; left: 50%; z-index: 20; transform: translateX(-50%); padding: 10px 16px; border-radius: 8px; background: #111827; color: #fff; opacity: 0; pointer-events: none; transition: opacity .2s; }
    .gzh-toast.show { opacity: 1; }
  </style>
</head>
<body>
  <div class="gzh-toolbar">
    <button class="gzh-copy" id="gzhCopyBtn" type="button" onclick="gzhPrepareSelection(); return gzhCopy();">复制到公众号</button>
  </div>
  <div class="gzh-toast" id="gzhToast"></div>
  <main class="gzh-stage">
    <div id="gzh-content">
<!--GZH_CONTENT-->
    </div>
  </main>
  <script>
function gzhShowToast(message) {
  const toast = document.getElementById('gzhToast');
  toast.textContent = message;
  toast.classList.add('show');
  window.clearTimeout(toast._timer);
  toast._timer = window.setTimeout(() => toast.classList.remove('show'), 2800);
}
function gzhPrepareSelection() {
  const range = document.createRange();
  range.selectNodeContents(document.getElementById('gzh-content'));
  const selection = window.getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
}
/*GZH_COPY_FUNCTION*/</script>
</body>
</html>
"""


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
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
            temporary = Path(handle.name)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def wrap_preview(input_path: Path, output_path: Path) -> None:
    source = Path(input_path)
    target = Path(output_path)
    fragment = source.read_text(encoding="utf-8-sig").strip()
    lowered = fragment.lower()
    if not lowered.startswith("<section") or not lowered.endswith("</section>"):
        raise ValueError("input must be a non-empty <section>...</section> fragment")
    preview = PREVIEW_TEMPLATE.replace("<!--GZH_CONTENT-->", fragment).replace(
        "/*GZH_COPY_FUNCTION*/", EXPECTED_COPY_FUNCTION_TEXT
    )
    _atomic_write(target, preview)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    wrap_preview(args.input, args.output)
    print(
        json.dumps(
            {"ok": True, "input": str(args.input), "output": str(args.output)},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
