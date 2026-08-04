import argparse
import json
import re
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "account-profile-template"

COPY_MAP = {
    "audience.md": "audience.md",
    "benchmark.md": "benchmarks.md",
    "script_patterns.md": "content-patterns.md",
}
PROFILE_DOCS = (
    "positioning.md",
    "audience.md",
    "voice.md",
    "content-patterns.md",
    "visual-style.md",
    "benchmarks.md",
)
EXCLUDED = (".auth", ".auth-xhs", ".auth-linkedin", ".cheat-cache")

_CHEAT_SOURCES = {
    "state": ".cheat-state.json",
    "rubric": "rubric_notes.md",
    "candidates": "candidates.md",
    "predictions": "predictions/",
}
_URL_RE = re.compile(
    r"https?://[^\s<>'\"]+"
    r"|(?<=\]\()/(?!/)[^)\s]+"
    r"|(?<=\]\(<)/(?!/)[^>\s]+>"
    r"|\[[^\]\r\n]+\]:[ \t]+/(?!/)[^\s<>'\"]+"
)
_FILE_URI_RE = re.compile(
    r"(?i)(?<![\w/])file://[^\s<>'\"\)\]\}，。；！？]+"
)
_WINDOWS_ABSOLUTE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    r"[A-Za-z]:[\\/][^\s<>'\"\)\]\}]*"
    r"|\\\\[^\\/\s]+[\\/][^\s<>'\"\)\]\}]*"
    r")"
)
_POSIX_ABSOLUTE_PATH_RE = re.compile(
    r"(?<![\w/])/(?!/)"
    r"[^\s/<>\'\"\)\]\}]+"
    r"(?:/[^\s/<>\'\"\)\]\}]*)*"
)


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _slug(value):
    slug = re.sub(r"[^a-z0-9-]+", "-", str(value).lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "wechat-account"


def _portable_markdown(text, source):
    urls = []

    def protect_url(match):
        marker = f"\x00PROFILE_ADAPTER_URL_{len(urls)}\x00"
        urls.append(match.group(0))
        return marker

    portable = _URL_RE.sub(protect_url, text)
    portable = _FILE_URI_RE.sub("[local-path]", portable)
    source = Path(source).expanduser().resolve()
    source_variants = {str(source), source.as_posix()}
    for source_value in sorted(source_variants, key=len, reverse=True):
        portable = re.sub(
            re.escape(source_value),
            "[local-source]",
            portable,
            flags=re.IGNORECASE,
        )
    portable = _WINDOWS_ABSOLUTE_PATH_RE.sub("[local-path]", portable)
    portable = _POSIX_ABSOLUTE_PATH_RE.sub("[local-path]", portable)
    for index, url in enumerate(urls):
        portable = portable.replace(
            f"\x00PROFILE_ADAPTER_URL_{index}\x00",
            url,
        )
    return portable


def preview_profile(source):
    source = Path(source).expanduser().resolve()
    if not (source / ".cheat-state.json").is_file():
        raise ValueError("Cheat project is not initialized")

    mapped = sorted(name for name in COPY_MAP if (source / name).is_file())
    available_targets = {COPY_MAP[name] for name in mapped}
    missing_profile_docs = sorted(
        name for name in PROFILE_DOCS if name not in available_targets
    )
    excluded = sorted(name for name in EXCLUDED if (source / name).exists())
    return {
        "source_type": "cheat-on-content",
        "mapped": mapped,
        "live_linked": dict(_CHEAT_SOURCES),
        "excluded": excluded,
        "missing_profile_docs": missing_profile_docs,
        "requires_cheat_status_check": True,
        "source_writes_planned": False,
    }


def _write_json(path, value):
    Path(path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _relative_index(source, folder):
    source = Path(source)
    directory = source / folder
    if not directory.is_dir():
        return {"items": []}
    files = sorted(
        (path for path in directory.glob("*.md") if path.is_file()),
        key=lambda path: path.name,
    )
    return {
        "items": [
            {"source_ref": path.relative_to(source).as_posix()} for path in files
        ]
    }


def _create_layout(output):
    output = Path(output).expanduser()
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")

    output.mkdir(parents=True)
    (output / "history" / "articles").mkdir(parents=True)
    (output / "history" / "retros").mkdir(parents=True)
    (output / "history" / "edits").mkdir(parents=True)
    (output / "history" / "voice-observations").mkdir(parents=True)
    for profile_doc in PROFILE_DOCS:
        shutil.copyfile(TEMPLATE_ROOT / profile_doc, output / profile_doc)
    _write_json(output / "history" / "articles" / "index.json", {"items": []})
    _write_json(output / "history" / "retros" / "index.json", {"items": []})
    _write_json(
        output / "history" / "edits" / "index.json",
        {"schema_version": "1.0", "items": []},
    )
    _write_json(
        output / "history" / "voice-observations" / "index.json",
        {"schema_version": "1.0", "items": []},
    )
    (output / ".gitignore").write_text(
        "bindings.local.json\n",
        encoding="utf-8",
    )
    return output


def _separate_output(source, output):
    source = Path(source).expanduser().resolve()
    output = Path(output).expanduser().resolve()
    if source == output or source in output.parents or output in source.parents:
        raise ValueError("Output must be outside the Cheat project")
    return output


@contextmanager
def _atomic_layout(output):
    output = Path(output).expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")

    temp_root = Path(
        tempfile.mkdtemp(
            prefix=f".{output.name}.tmp-",
            dir=output.parent,
        )
    )
    staging = temp_root / "profile"
    try:
        _create_layout(staging)
        yield staging
        if output.exists():
            raise FileExistsError(f"Output already exists: {output}")
        staging.rename(output)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def _account(account_id, mode):
    timestamp = _now()
    return {
        "schema_version": "1.0",
        "account_id": _slug(account_id),
        "mode": mode,
        "cheat_binding": "primary",
        "profile_docs": list(PROFILE_DOCS),
        "cheat_sources": dict(_CHEAT_SOURCES),
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def _bindings(source):
    return {
        "schema_version": "1.0",
        "bindings": {
            "primary": {
                "type": "cheat-on-content",
                "path": str(Path(source).expanduser().resolve()),
            }
        },
    }


def create_profile(output, account_id, cheat_project, approved):
    if not approved:
        raise PermissionError("Explicit approval is required")

    cheat_project = Path(cheat_project).expanduser().resolve()
    if not cheat_project.exists():
        raise FileNotFoundError(f"Cheat project does not exist: {cheat_project}")
    if not cheat_project.is_dir() or not (
        cheat_project / ".cheat-state.json"
    ).is_file():
        raise ValueError("Cheat project is not initialized")

    output = _separate_output(cheat_project, output)
    with _atomic_layout(output) as staging:
        account = _account(account_id, "new")
        _write_json(staging / "account.json", account)
        _write_json(staging / "bindings.local.json", _bindings(cheat_project))
    return account


def import_profile(source, output, approved):
    if not approved:
        raise PermissionError("Explicit approval is required")

    source = Path(source).expanduser().resolve()
    preview = preview_profile(source)
    output = _separate_output(source, output)
    with _atomic_layout(output) as staging:
        for source_name in preview["mapped"]:
            target_name = COPY_MAP[source_name]
            source_text = (source / source_name).read_text(encoding="utf-8-sig")
            (staging / target_name).write_text(
                _portable_markdown(source_text, source),
                encoding="utf-8",
            )

        account = _account(source.name, "imported")
        _write_json(staging / "account.json", account)
        _write_json(staging / "bindings.local.json", _bindings(source))
        _write_json(
            staging / "history" / "articles" / "index.json",
            _relative_index(source, "scripts"),
        )
        _write_json(
            staging / "history" / "retros" / "index.json",
            _relative_index(source, "predictions"),
        )
    return preview


def _build_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    preview_parser = subparsers.add_parser("preview")
    preview_parser.add_argument("source", type=Path)

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("output", type=Path)
    create_parser.add_argument("--account-id", required=True)
    create_parser.add_argument("--cheat-project", required=True, type=Path)
    create_parser.add_argument("--approved", action="store_true")

    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("source", type=Path)
    import_parser.add_argument("output", type=Path)
    import_parser.add_argument("--approved", action="store_true")
    return parser


def main(argv=None):
    args = _build_parser().parse_args(argv)
    if args.command == "preview":
        result = preview_profile(args.source)
    elif args.command == "create":
        result = create_profile(
            args.output,
            args.account_id,
            args.cheat_project,
            args.approved,
        )
    else:
        result = import_profile(args.source, args.output, args.approved)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
