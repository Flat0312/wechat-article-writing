import argparse
import json
import os
import re
from pathlib import Path


ALIASES = {
    "gzh-design-skill": "gzh-design",
    "Humanizer-zh": "humanizer-zh",
}

STAGE_RULES = {
    "account": {"required": ["cheat-on-content"]},
    "calibration": {"required": ["cheat-on-content"]},
    "topic": {
        "required": [
            "cheat-on-content",
            "cheat-trends",
            "creator-buddy",
            "gzh-explosive-content-detector",
        ],
    },
    "topic-ai": {
        "required": [
            "cheat-on-content",
            "cheat-trends",
            "creator-buddy",
            "gzh-explosive-content-detector",
            "aihot",
        ],
    },
    "writing": {"required": ["khazix-writer"]},
    "strategy": {"required": ["wechat-content-strategy"]},
    "editing": {"required": ["humanizer-zh"]},
    "learning": {"required": ["wechat-style-learning"]},
    "cover": {"required": ["guizang-social-card-skill"]},
    "visual": {
        "any": [["ian-xiaohei-illustrations", "baoyu-article-illustrator"]],
        "optional": ["imagegen"],
    },
    "visual-ian": {
        "required": ["ian-xiaohei-illustrations"],
        "optional": ["imagegen"],
    },
    "visual-structured": {
        "required": ["baoyu-article-illustrator"],
        "optional": ["imagegen"],
    },
    "html": {"required": ["gzh-design"]},
    "publish": {"required": ["cheat-on-content"]},
    "retro": {"required": ["cheat-on-content"]},
}

_FRONTMATTER_RE = re.compile(
    r"\A---[ \t]*\r?\n(?P<body>.*?)(?:\r?\n)---[ \t]*(?:\r?\n|\Z)",
    re.DOTALL,
)
_NAME_RE = re.compile(
    r"^name[ \t]*:[ \t]*(?:(?P<quote>['\"])(?P<quoted>.*?)(?P=quote)|"
    r"(?P<plain>[^#\r\n]*?))[ \t]*(?:#[^\r\n]*)?$",
    re.MULTILINE,
)


def canonical_name(name):
    normalized = name.strip()
    canonical = ALIASES.get(normalized, ALIASES.get(normalized.lower(), normalized))
    return canonical.lower()


def parse_skill_name(skill_file):
    text = Path(skill_file).read_text(encoding="utf-8-sig")
    frontmatter = _FRONTMATTER_RE.match(text)
    if not frontmatter:
        return None
    name_match = _NAME_RE.search(frontmatter.group("body"))
    if not name_match:
        return None
    name = name_match.group("quoted")
    if name is None:
        name = name_match.group("plain")
    name = name.strip()
    if not name:
        return None
    return canonical_name(name)


def default_roots():
    roots = [
        Path.home() / ".codex" / "skills",
        Path.home() / ".agents" / "skills",
        Path.home() / ".claude" / "skills",
    ]
    extra_roots = os.environ.get("WECHAT_ARTICLE_SKILL_ROOTS", "")
    roots.extend(
        Path(root.strip()).expanduser()
        for root in extra_roots.split(os.pathsep)
        if root.strip()
    )
    return roots


def discover_skills(roots=None):
    discovered = {}
    search_roots = default_roots() if roots is None else roots
    for root in search_roots:
        root_path = Path(root).expanduser()
        if not root_path.is_dir():
            continue
        for skill_file in sorted(root_path.rglob("SKILL.md")):
            try:
                name = parse_skill_name(skill_file)
            except (OSError, UnicodeError):
                continue
            if name:
                discovered.setdefault(name, skill_file.parent.resolve())
    return discovered


def _visual_runtime(discovered):
    available = {canonical_name(name) for name in discovered}
    routes = {
        "ian": {
            "ready": "ian-xiaohei-illustrations" in available,
            "missing": (
                []
                if "ian-xiaohei-illustrations" in available
                else ["ian-xiaohei-illustrations"]
            ),
        },
        "baoyu-article-illustrator": {
            "ready": "baoyu-article-illustrator" in available,
            "missing": (
                []
                if "baoyu-article-illustrator" in available
                else ["baoyu-article-illustrator"]
            ),
        },
    }
    return {
        "ready_routes": [name for name, value in routes.items() if value["ready"]],
        "routes": routes,
        "missing_imagegen": [] if "imagegen" in available else ["imagegen"],
    }


def check_dependencies(stage, discovered, env=None):
    if stage not in STAGE_RULES:
        raise ValueError(f"Unknown stage: {stage}")

    rules = STAGE_RULES[stage]
    available = sorted({canonical_name(name) for name in discovered})
    available_set = set(available)
    missing_required = [
        name for name in rules.get("required", []) if name not in available_set
    ]
    missing_any = [
        list(candidates)
        for candidates in rules.get("any", [])
        if not available_set.intersection(candidates)
    ]
    optional_missing = [
        name for name in rules.get("optional", []) if name not in available_set
    ]

    result = {
        "stage": stage,
        "ok": not missing_required and not missing_any,
        "available": available,
        "missing_required": missing_required,
        "missing_any": missing_any,
        "optional_missing": optional_missing,
    }
    if stage in {"visual", "visual-ian", "visual-structured"}:
        result["runtime"] = _visual_runtime(discovered)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=STAGE_RULES)
    parser.add_argument("--root", action="append", type=Path, dest="roots")
    args = parser.parse_args(argv)

    result = check_dependencies(args.stage, discover_skills(args.roots))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
