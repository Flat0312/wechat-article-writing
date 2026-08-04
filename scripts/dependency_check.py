import argparse
import json
import os
import re
import shutil
from pathlib import Path


ALIASES = {
    "gzh-design-skill": "gzh-design",
    "Humanizer-zh": "humanizer-zh",
}

# These pipeline stages intentionally reuse an existing preflight rule. The
# resolved stage is returned so callers can distinguish an alias from a gap.
STAGE_ALIASES = {
    "brief": "strategy",
    "evidence": "topic",
    "prediction": "publish",
    "visual_plan": "visual",
}

CLI_RULES = {
    "x-tweet-fetcher": {
        "env": ("X_TWEET_FETCHER_BIN", "XTF_BIN"),
        "commands": ("xtf", "xtf.exe", "x-tweet-fetcher"),
    },
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
            "xiaohongshu-skill",
        ],
        "required_cli": ["x-tweet-fetcher"],
    },
    "topic-ai": {
        "required": [
            "cheat-on-content",
            "cheat-trends",
            "creator-buddy",
            "gzh-explosive-content-detector",
            "aihot",
            "xiaohongshu-skill",
        ],
        "required_cli": ["x-tweet-fetcher"],
    },
    # 资讯贴图（news-card）：与 long-essay 并行但走独立轻量分支。
    # 不进 12 阶段 article-state.json，不走 long-essay 视觉/HTML 轨道。
    # 卡图走 guizang 合成或 imagegen 兜底（与 long-essay 头图相同的 21:9 单图契约）。
    # AI 账号或 AI 主题改用 news-card-ai，加 aihot。
    "news-card": {
        "required": [
            "cheat-on-content",
            "cheat-trends",
            "creator-buddy",
            "gzh-explosive-content-detector",
            "wechat-content-strategy",
            "xiaohongshu-skill",
        ],
        "required_cli": ["x-tweet-fetcher"],
        "any": [["guizang-social-card-skill", "imagegen"]],
    },
    "news-card-ai": {
        "required": [
            "cheat-on-content",
            "cheat-trends",
            "creator-buddy",
            "gzh-explosive-content-detector",
            "wechat-content-strategy",
            "aihot",
            "xiaohongshu-skill",
        ],
        "required_cli": ["x-tweet-fetcher"],
        "any": [["guizang-social-card-skill", "imagegen"]],
    },
    # 卡兹克必须参与技法辅助，但不得成为账号作者声音。
    "writing": {"required": ["khazix-writer"]},
    "strategy": {"required": ["wechat-content-strategy"]},
    # 去 AI 痕迹是可执行的第一方门禁；Humanizer-zh 只作为可选诊断器。
    "editing": {"optional": ["humanizer-zh"]},
    "learning": {"required": ["wechat-style-learning"]},
    "cover": {"any": [["guizang-social-card-skill", "imagegen"]]},
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
        Path.home() / ".workbuddy" / "skills",
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


def _resolve_stage(stage):
    resolved = stage
    seen = set()
    while resolved in STAGE_ALIASES:
        if resolved in seen:
            raise ValueError(f"Cyclic stage alias: {stage}")
        seen.add(resolved)
        resolved = STAGE_ALIASES[resolved]
    return resolved


def _resolve_executable(candidate, env):
    if not candidate:
        return None
    candidate_path = Path(str(candidate)).expanduser()
    if candidate_path.is_file():
        return str(candidate_path.resolve())
    return shutil.which(str(candidate), path=env.get("PATH"))


def _find_cli(cli_name, env):
    spec = CLI_RULES[cli_name]
    # An explicit override is authoritative, including an invalid path.
    for env_name in spec["env"]:
        if env_name in env:
            path = _resolve_executable(env.get(env_name), env)
            return {
                "ok": path is not None,
                "path": path,
                "source": f"env:{env_name}",
            }

    default_paths = []
    if cli_name == "x-tweet-fetcher":
        default_paths.append(
            Path.home()
            / ".codex"
            / "tools"
            / "x-tweet-fetcher"
            / ".venv"
            / "Scripts"
            / "xtf.exe"
        )
    for candidate in default_paths:
        path = _resolve_executable(candidate, env)
        if path:
            return {"ok": True, "path": path, "source": "default"}
    for command in spec["commands"]:
        path = _resolve_executable(command, env)
        if path:
            return {"ok": True, "path": path, "source": "PATH"}
    return {"ok": False, "path": None, "source": None}


def _cli_runtime(required_cli, env=None):
    environment = os.environ if env is None else env
    checks = {name: _find_cli(name, environment) for name in required_cli}
    available = [name for name, result in checks.items() if result["ok"]]
    missing_required = [name for name, result in checks.items() if not result["ok"]]
    return {
        "required": list(required_cli),
        "available": available,
        "missing_required": missing_required,
        "checks": checks,
    }


def check_dependencies(stage, discovered, env=None):
    resolved_stage = _resolve_stage(stage)
    if resolved_stage not in STAGE_RULES:
        raise ValueError(f"Unknown stage: {stage}")

    rules = STAGE_RULES[resolved_stage]
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
    cli_runtime = _cli_runtime(rules.get("required_cli", []), env=env)
    skill_presence = {
        "available": available,
        "paths": {
            canonical_name(name): str(path) for name, path in discovered.items()
        },
        "missing_required": missing_required,
        "missing_any": missing_any,
        "optional_missing": optional_missing,
    }

    result = {
        "stage": stage,
        "resolved_stage": resolved_stage,
        "ok": not missing_required
        and not missing_any
        and not cli_runtime["missing_required"],
        "available": available,
        "missing_required": missing_required,
        "missing_any": missing_any,
        "optional_missing": optional_missing,
        "skill_presence": skill_presence,
        "cli_runtime": cli_runtime,
    }
    if resolved_stage in {"visual", "visual-ian", "visual-structured"}:
        result["runtime"] = _visual_runtime(discovered)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        required=True,
        choices=sorted(set(STAGE_RULES) | set(STAGE_ALIASES)),
    )
    parser.add_argument("--root", action="append", type=Path, dest="roots")
    args = parser.parse_args(argv)

    result = check_dependencies(args.stage, discover_skills(args.roots))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
