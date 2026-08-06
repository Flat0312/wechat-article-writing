from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PATH_FRAGMENT = (
    r"(?:references/[A-Za-z0-9_.-]+\.md|"
    r"scripts/[A-Za-z0-9_.-]+\.py|"
    r"assets/[A-Za-z0-9_./-]+)"
)
ROOTED_PATH_RE = re.compile(
    rf"(?P<root><SKILL_ROOT>|<WECHAT_ARTICLE_ROOT>)/(?P<path>{PATH_FRAGMENT})"
)
BARE_PATH_RE = re.compile(
    rf"(?<![A-Za-z0-9_./<>-])(?P<path>{PATH_FRAGMENT})"
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\((?P<target>[^)\s]+)")


def _scanned_markdown() -> list[Path]:
    files = [SKILL_ROOT / "SKILL.md"]
    files.extend(sorted((SKILL_ROOT / "references").rglob("*.md")))
    files.extend(
        sorted((SKILL_ROOT / "companion-skills").glob("*/SKILL.md"))
    )
    return files


def _skill_root_for(source: Path) -> Path:
    companion_root = SKILL_ROOT / "companion-skills"
    try:
        source.relative_to(companion_root)
    except ValueError:
        return SKILL_ROOT
    return source.parent


def _inline_targets(source: Path, text: str) -> set[Path]:
    targets: set[Path] = set()
    occupied: list[tuple[int, int]] = []
    for match in ROOTED_PATH_RE.finditer(text):
        root = (
            SKILL_ROOT
            if match.group("root") == "<WECHAT_ARTICLE_ROOT>"
            else _skill_root_for(source)
        )
        targets.add(root / match.group("path"))
        occupied.append(match.span())
    for match in BARE_PATH_RE.finditer(text):
        if any(start <= match.start() < end for start, end in occupied):
            continue
        targets.add(SKILL_ROOT / match.group("path").rstrip(".,;:"))
    return targets


def _markdown_link_targets(source: Path, text: str) -> set[Path]:
    targets: set[Path] = set()
    for match in MARKDOWN_LINK_RE.finditer(text):
        raw = match.group("target").split("#", 1)[0]
        if not raw or "://" in raw or raw.startswith("#"):
            continue
        candidate = (source.parent / raw).resolve()
        try:
            relative = candidate.relative_to(SKILL_ROOT)
        except ValueError:
            continue
        parts = set(relative.parts)
        if (
            parts.intersection({"references", "scripts", "assets"})
            or (
                source.parent.name == "references"
                and "/" not in raw
                and "\\" not in raw
                and raw.endswith(".md")
            )
        ):
            targets.add(candidate)
    return targets


class ReferenceIntegrityTests(unittest.TestCase):
    def test_scanner_covers_inline_code_and_markdown_links(self):
        source = SKILL_ROOT / "SKILL.md"
        text = (
            "`references/missing-contract.md`\n"
            "`python <SKILL_ROOT>/scripts/missing_tool.py`\n"
            "[template](assets/missing/template.md)\n"
        )
        targets = _inline_targets(source, text)
        targets.update(_markdown_link_targets(source, text))

        self.assertEqual(
            targets,
            {
                SKILL_ROOT / "references" / "missing-contract.md",
                SKILL_ROOT / "scripts" / "missing_tool.py",
                SKILL_ROOT / "assets" / "missing" / "template.md",
            },
        )

    def test_all_local_path_references_exist(self):
        missing: list[str] = []
        for source in _scanned_markdown():
            text = source.read_text(encoding="utf-8")
            targets = _inline_targets(source, text)
            targets.update(_markdown_link_targets(source, text))
            for target in sorted(targets):
                if not target.exists():
                    missing.append(
                        f"{source.relative_to(SKILL_ROOT)} -> "
                        f"{target.relative_to(SKILL_ROOT)}"
                    )
        self.assertEqual(missing, [], "missing local references:\n" + "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
