from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
from typing import Any, Iterator

from article_state import ALLOWED_STATUS, STAGES, file_hash


PROFILE_DOCS = (
    "positioning.md",
    "audience.md",
    "voice.md",
    "content-patterns.md",
    "visual-style.md",
    "benchmarks.md",
)
PROFILE_REQUIRED_KEYS = (
    "schema_version",
    "account_id",
    "mode",
    "profile_docs",
    "created_at",
    "updated_at",
)
ARTICLE_REQUIRED_KEYS = (
    "schema_version",
    "article_id",
    "mode",
    "profile_ref",
    "cheat_binding",
    "current_stage",
    "stage_status",
    "artifacts",
    "approvals",
    "skill_routes",
    "stale_artifacts",
    "required_actions",
    "created_at",
    "updated_at",
)
HTML_DELIVERY_FILES = (
    "output/article.html",
    "output/article-preview.html",
    "output/article-copy.html",
    "output/article-copy-preview.html",
    "output/html-qc.md",
)
HTML_MINIMUM_MARKERS = {
    "output/article.html": ("<section", "</section>"),
    "output/article-copy-preview.html": (
        "<html",
        'id="gzh-content"',
        "gzhCopyBtn",
        "</body>",
    ),
}
HTML_QC_HEADING_RE = re.compile(r"(?m)^\s*#{1,6}\s+\S")
HTML_QC_VERIFICATION_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?.*(?:validate_project|验证|校验|validation).*$"
)
FORBIDDEN_KEY_PARTS = (
    "secret",
    "token",
    "cookie",
    "password",
    "credential",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "authorization",
    "bearer",
    "appkey",
    "app_key",
    "appsecret",
    "app_secret",
)
WINDOWS_DRIVE_REFERENCE = re.compile(r"(?i)^[A-Z]:")
WINDOWS_UNC = re.compile(r"^(?:\\\\|//)[^\\/]+[\\/]")
URI_SCHEME = re.compile(r"(?i)^[A-Z][A-Z0-9+.-]*:")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
LEARNING_RULE_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
LEARNING_RULE_TYPES = {
    "structure",
    "opening",
    "closing",
    "rhythm",
    "tone",
    "expression",
    "evidence",
}
NORMALIZED_FORBIDDEN_KEY_PARTS = tuple(
    re.sub(r"[^a-z0-9]", "", part.lower()) for part in FORBIDDEN_KEY_PARTS
)
GITIGNORE_ENCODING_ERROR = (
    "bindings.local.json: .gitignore must be valid UTF-8"
)
GITIGNORE_GIT_ERROR = (
    "bindings.local.json: unable to verify .gitignore with git"
)
GITIGNORE_NOT_IGNORED_ERROR = (
    "bindings.local.json: must be ignored by .gitignore"
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _walk(
    value: Any, location: str = "root"
) -> Iterator[tuple[str, str | None, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            child_location = f"{location}.{key_text}"
            yield child_location, key_text, item
            yield from _walk(item, child_location)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child_location = f"{location}[{index}]"
            yield child_location, None, item
            yield from _walk(item, child_location)


def _is_machine_absolute_path(value: str) -> bool:
    candidate = value.strip()
    return bool(
        WINDOWS_DRIVE_REFERENCE.match(candidate)
        or WINDOWS_UNC.match(candidate)
        or candidate.startswith("/")
        or candidate.startswith("\\")
        or candidate.lower().startswith("file:")
    )


def _is_portable_relative_path(value: str) -> bool:
    if (
        not value
        or "\\" in value
        or WINDOWS_DRIVE_REFERENCE.match(value)
        or URI_SCHEME.match(value)
        or _is_machine_absolute_path(value)
    ):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and path.parts != ()


def _is_logical_identifier(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and value
        and value[0].isalnum()
        and value[-1].isalnum()
        and ".." not in value
        and all(
            character.isalnum() or character in "._-" for character in value
        )
    )


def _json_safety_errors(
    payload: Any, allow_absolute_paths: bool = False
) -> list[str]:
    errors = []
    for location, key, value in _walk(payload):
        lowered = (
            re.sub(r"[^a-z0-9]", "", key.lower())
            if key is not None
            else ""
        )
        if key is not None and any(
            part in lowered for part in NORMALIZED_FORBIDDEN_KEY_PARTS
        ):
            errors.append(f"{location}: secret-like key is not allowed")
        if (
            not allow_absolute_paths
            and key is not None
            and _is_machine_absolute_path(key)
        ):
            errors.append(f"{location}: absolute path key is not allowed")
        if (
            not allow_absolute_paths
            and isinstance(value, str)
            and _is_machine_absolute_path(value)
        ):
            errors.append(f"{location}: absolute path is not allowed")
    return errors


def _gitignore_ignores_root_file(
    ignore_path: Path, target: str
) -> tuple[bool | None, str | None]:
    try:
        ignore_path.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError:
        return None, GITIGNORE_ENCODING_ERROR
    except OSError:
        return None, GITIGNORE_GIT_ERROR

    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    git = ["git", "-c", f"core.excludesFile={os.devnull}"]
    try:
        with tempfile.TemporaryDirectory() as temp:
            oracle_root = Path(temp)
            initialized = subprocess.run(
                [*git, "init", "-q"],
                cwd=oracle_root,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if initialized.returncode != 0:
                return None, GITIGNORE_GIT_ERROR
            shutil.copyfile(ignore_path, oracle_root / ".gitignore")
            (oracle_root / target).touch()
            checked = subprocess.run(
                [
                    *git,
                    "check-ignore",
                    "--no-index",
                    "--quiet",
                    "--",
                    target,
                ],
                cwd=oracle_root,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
    except (OSError, subprocess.SubprocessError):
        return None, GITIGNORE_GIT_ERROR
    if checked.returncode == 0:
        return True, None
    if checked.returncode == 1:
        return False, None
    return None, GITIGNORE_GIT_ERROR


def _validate_learning_ledger(root: Path) -> list[str]:
    edits_root = root / "history" / "edits"
    if not edits_root.exists():
        return []
    if not edits_root.is_dir():
        return ["history/edits: must be a directory"]
    index_path = edits_root / "index.json"
    if not index_path.is_file():
        return ["history/edits/index.json: missing"]
    try:
        index = _load_json(index_path)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"history/edits/index.json: invalid JSON: {exc}"]
    errors = []
    if not isinstance(index, dict):
        return ["history/edits/index.json: JSON root must be an object"]
    if set(index) != {"schema_version", "items"}:
        errors.append(
            "history/edits/index.json: only schema_version and items are allowed"
        )
    if index.get("schema_version") != "1.0":
        errors.append("history/edits/index.json: schema_version must be 1.0")
    items = index.get("items")
    if not isinstance(items, list):
        return errors + ["history/edits/index.json: items must be an array"]
    errors.extend(_json_safety_errors(index))
    for item_index, item in enumerate(items):
        prefix = f"history/edits/index.json: items[{item_index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required = {
            "source_ref",
            "article_id",
            "draft_sha256",
            "final_sha256",
            "created_at",
        }
        if set(item) != required:
            errors.append(f"{prefix} must contain only the required fields")
            continue
        source_ref = item.get("source_ref")
        if (
            not isinstance(source_ref, str)
            or not _is_portable_relative_path(source_ref)
            or not source_ref.startswith("history/edits/")
            or source_ref == "history/edits/index.json"
        ):
            errors.append(f"{prefix}.source_ref must name a portable lesson file")
            continue
        for hash_name in ("draft_sha256", "final_sha256"):
            if not isinstance(item.get(hash_name), str) or not SHA256_RE.fullmatch(
                item[hash_name]
            ):
                errors.append(f"{prefix}.{hash_name} must be SHA256")
        lesson_path = root.joinpath(*PurePosixPath(source_ref).parts)
        if not lesson_path.is_file():
            errors.append(f"{prefix}.source_ref is missing")
            continue
        try:
            lesson = _load_json(lesson_path)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"{source_ref}: invalid JSON: {exc}")
            continue
        if not isinstance(lesson, dict):
            errors.append(f"{source_ref}: JSON root must be an object")
            continue
        lesson_fields = {
            "schema_version",
            "article_id",
            "draft_sha256",
            "final_sha256",
            "created_at",
            "rules",
        }
        if set(lesson) != lesson_fields:
            errors.append(f"{source_ref}: contains unsupported fields")
            continue
        if lesson.get("schema_version") != "1.0":
            errors.append(f"{source_ref}: schema_version must be 1.0")
        for field in (
            "article_id",
            "draft_sha256",
            "final_sha256",
            "created_at",
        ):
            if lesson.get(field) != item.get(field):
                errors.append(f"{source_ref}: {field} does not match index")
        rules = lesson.get("rules")
        if not isinstance(rules, list) or not rules:
            errors.append(f"{source_ref}: rules must be a non-empty array")
        else:
            seen = set()
            for rule_index, rule in enumerate(rules):
                rule_prefix = f"{source_ref}: rules[{rule_index}]"
                if not isinstance(rule, dict) or set(rule) != {
                    "key",
                    "type",
                    "instruction",
                }:
                    errors.append(f"{rule_prefix} has an invalid shape")
                    continue
                key = rule.get("key")
                if not isinstance(key, str) or not LEARNING_RULE_KEY_RE.fullmatch(key):
                    errors.append(f"{rule_prefix}.key is invalid")
                elif key in seen:
                    errors.append(f"{rule_prefix}.key is duplicated")
                else:
                    seen.add(key)
                if rule.get("type") not in LEARNING_RULE_TYPES:
                    errors.append(f"{rule_prefix}.type is invalid")
                instruction = rule.get("instruction")
                if not isinstance(instruction, str) or not instruction.strip():
                    errors.append(f"{rule_prefix}.instruction is required")
        errors.extend(_json_safety_errors(lesson))
    return errors


def validate_profile(root: Path) -> list[str]:
    root = Path(root)
    errors = []
    account_path = root / "account.json"
    if not account_path.is_file():
        return ["account.json: missing"]
    try:
        account = _load_json(account_path)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"account.json: invalid JSON: {exc}"]
    if not isinstance(account, dict):
        return ["account.json: JSON root must be an object"]
    for key in PROFILE_REQUIRED_KEYS:
        if key not in account:
            errors.append(f"account.json: missing key {key}")
    if account.get("schema_version") != "1.0":
        errors.append("account.json: schema_version must be 1.0")
    if account.get("profile_docs") != list(PROFILE_DOCS):
        errors.append(
            "account.json: profile_docs must list the six profile documents"
        )
    has_cheat_binding = "cheat_binding" in account
    has_cheat_sources = "cheat_sources" in account
    if has_cheat_binding != has_cheat_sources:
        errors.append(
            "account.json: cheat_binding and cheat_sources must appear together"
        )
    if has_cheat_binding and not _is_logical_identifier(account["cheat_binding"]):
        errors.append(
            "account.json: cheat_binding must be a logical identifier"
        )
    if has_cheat_sources:
        cheat_sources = account["cheat_sources"]
        if not isinstance(cheat_sources, dict):
            errors.append("account.json: cheat_sources must be an object")
        else:
            for source_name, source_ref in cheat_sources.items():
                if not isinstance(source_ref, str) or not _is_portable_relative_path(
                    source_ref
                ):
                    errors.append(
                        "account.json: cheat_sources."
                        f"{source_name} must be a portable relative reference"
                    )
    errors.extend(_json_safety_errors(account))
    for name in PROFILE_DOCS:
        if not (root / name).is_file():
            errors.append(f"{name}: missing")
    binding_path = root / "bindings.local.json"
    if binding_path.is_file():
        ignore = root / ".gitignore"
        if not ignore.is_file():
            errors.append(GITIGNORE_NOT_IGNORED_ERROR)
        else:
            ignored, ignore_error = _gitignore_ignores_root_file(
                ignore, "bindings.local.json"
            )
            if ignore_error is not None:
                errors.append(ignore_error)
            elif not ignored:
                errors.append(GITIGNORE_NOT_IGNORED_ERROR)
        try:
            local_bindings = _load_json(binding_path)
            if not isinstance(local_bindings, dict):
                errors.append(
                    "bindings.local.json: JSON root must be an object"
                )
            else:
                errors.extend(
                    _json_safety_errors(
                        local_bindings, allow_absolute_paths=True
                    )
                )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"bindings.local.json: invalid JSON: {exc}")
    errors.extend(_validate_learning_ledger(root))
    return errors


def validate_article_project(root: Path) -> list[str]:
    root = Path(root)
    errors = []
    state_path = root / "article-state.json"
    if not state_path.is_file():
        return ["article-state.json: missing"]
    try:
        state = _load_json(state_path)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"article-state.json: invalid JSON: {exc}"]
    if not isinstance(state, dict):
        return ["article-state.json: JSON root must be an object"]
    for key in ARTICLE_REQUIRED_KEYS:
        if key not in state:
            errors.append(f"article-state.json: missing key {key}")
    if state.get("schema_version") != "1.0":
        errors.append("article-state.json: schema_version must be 1.0")
    if state.get("current_stage") not in STAGES:
        errors.append(
            "article-state.json: current_stage must name one of the 12 stages"
        )
    profile_ref = state.get("profile_ref")
    if profile_ref is not None and (
        not isinstance(profile_ref, str)
        or not _is_portable_relative_path(profile_ref)
    ):
        errors.append(
            "article-state.json: profile_ref must be null or a portable "
            "relative reference"
        )
    cheat_binding = state.get("cheat_binding")
    if cheat_binding is not None and not _is_logical_identifier(cheat_binding):
        errors.append(
            "article-state.json: cheat_binding must be null or a logical "
            "identifier"
        )
    status = state.get("stage_status", {})
    if not isinstance(status, dict):
        errors.append("article-state.json: stage_status must be an object")
    else:
        if set(status) != set(STAGES):
            errors.append(
                "article-state.json: stage_status keys do not match STAGES"
            )
        for stage, value in status.items():
            if not isinstance(value, str) or value not in ALLOWED_STATUS:
                errors.append(
                    f"article-state.json: stage_status.{stage}={value} is invalid"
                )
    artifacts = state.get("artifacts", {})
    if not isinstance(artifacts, dict):
        errors.append("article-state.json: artifacts must be an object")
    else:
        artifact_hashes: dict[str, str] = {}
        for role, artifact in artifacts.items():
            if not isinstance(artifact, dict):
                errors.append(
                    f"article-state.json: artifact {role} must be an object"
                )
                continue
            value = artifact.get("path")
            if not isinstance(value, str):
                errors.append(
                    f"article-state.json: artifact {role} path must be a string"
                )
            elif not _is_portable_relative_path(value):
                errors.append(
                    "article-state.json: artifact "
                    f"{role} path must be portable and relative"
                )
            recorded_hash = artifact.get("sha256")
            if not isinstance(recorded_hash, str) or not SHA256_RE.fullmatch(
                recorded_hash
            ):
                errors.append(
                    "article-state.json: artifact "
                    f"{role} sha256 must be a 64-character lowercase hex SHA256"
                )
            else:
                artifact_hashes[role] = recorded_hash
            if not isinstance(value, str) or not _is_portable_relative_path(value):
                continue
            target = root.joinpath(*PurePosixPath(value).parts)
            try:
                resolved_target = target.resolve(strict=True)
                resolved_target.relative_to(root.resolve())
            except FileNotFoundError:
                errors.append(
                    f"article-state.json: artifact {role} path does not exist"
                )
                continue
            except (OSError, RuntimeError, ValueError):
                errors.append(
                    f"article-state.json: artifact {role} path escapes article project"
                )
                continue
            if not resolved_target.is_file():
                errors.append(
                    f"article-state.json: artifact {role} path is not a file"
                )
                continue
            if isinstance(recorded_hash, str) and SHA256_RE.fullmatch(recorded_hash):
                actual_hash = file_hash(resolved_target)
                if actual_hash != recorded_hash:
                    errors.append(
                        "article-state.json: artifact "
                        f"{role} sha256 does not match file contents"
                    )
        approvals = state.get("approvals", {})
        if not isinstance(approvals, dict):
            errors.append("article-state.json: approvals must be an object")
        else:
            for approval_key, approval in approvals.items():
                if not isinstance(approval, dict):
                    errors.append(
                        f"article-state.json: approval {approval_key} must be an object"
                    )
                    continue
                artifact_role = approval.get("artifact_role")
                approval_hash = approval.get("artifact_sha256")
                has_role = artifact_role is not None
                has_hash = approval_hash is not None
                if approval_key == "final" and (
                    artifact_role != "final" or not has_hash
                ):
                    errors.append(
                        "article-state.json: final approval must bind artifact final"
                    )
                if has_role != has_hash:
                    errors.append(
                        "article-state.json: approval "
                        f"{approval_key} must contain artifact_role and artifact_sha256 together"
                    )
                    continue
                if not has_role:
                    continue
                if not isinstance(artifact_role, str) or artifact_role not in artifacts:
                    errors.append(
                        "article-state.json: approval "
                        f"{approval_key} references unknown artifact role {artifact_role}"
                    )
                    continue
                if not isinstance(approval_hash, str) or not SHA256_RE.fullmatch(
                    approval_hash
                ):
                    errors.append(
                        "article-state.json: approval "
                        f"{approval_key} artifact_sha256 must be a 64-character lowercase hex SHA256"
                    )
                    continue
                artifact_hash = artifact_hashes.get(artifact_role)
                if artifact_hash is not None and approval_hash != artifact_hash:
                    errors.append(
                        "article-state.json: approval "
                        f"{approval_key} hash does not match artifact {artifact_role}"
                    )
    html_status = status.get("html") if isinstance(status, dict) else None
    current_stage = state.get("current_stage")
    html_stage_reached = (
        current_stage in STAGES
        and STAGES.index(current_stage) >= STAGES.index("html")
    )
    html_work_started = (
        html_stage_reached
        or html_status
        in {"in_progress", "awaiting_confirmation", "failed", "stale"}
        or (isinstance(artifacts, dict) and "html" in artifacts)
    )
    if html_status != "completed" and html_work_started:
        html_contents: dict[str, str] = {}
        for relative in HTML_DELIVERY_FILES:
            target = root.joinpath(*PurePosixPath(relative).parts)
            if not target.is_file():
                errors.append(
                    f"{relative}: missing required HTML delivery file"
                )
                continue
            try:
                content = target.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                errors.append(f"{relative}: must be valid UTF-8 text")
                continue
            if not content.strip():
                errors.append(
                    f"{relative}: required HTML delivery file must be non-empty"
                )
                continue
            html_contents[relative] = content
        for relative, markers in HTML_MINIMUM_MARKERS.items():
            content = html_contents.get(relative)
            if content is None:
                continue
            lowered = content.lower()
            for marker in markers:
                if marker.lower() not in lowered:
                    errors.append(
                        f"{relative}: missing required marker {marker}"
                    )
        qc_content = html_contents.get("output/html-qc.md")
        if qc_content is not None:
            if not HTML_QC_HEADING_RE.search(qc_content):
                errors.append(
                    "output/html-qc.md: must contain a Markdown heading"
                )
            if "output/article.html" not in qc_content:
                errors.append(
                    "output/html-qc.md: must reference output/article.html"
                )
            if not HTML_QC_VERIFICATION_RE.search(qc_content):
                errors.append(
                    "output/html-qc.md: must contain a validation record"
                )
    errors.extend(_json_safety_errors(state))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("profile", "article"))
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    errors = (
        validate_profile(args.path)
        if args.kind == "profile"
        else validate_article_project(args.path)
    )
    print(
        json.dumps(
            {"ok": not errors, "errors": errors},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
