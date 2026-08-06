"""Account profile package validation (account.json, profile docs, bindings, learning ledger).

Exposed through the stable cross-skill entry point
``validate_project.py profile <账号目录>``. Direct imports are for
in-repo tests and sibling modules only.
"""

from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile

from project_checks import (
    SHA256_RE,
    _is_logical_identifier,
    _is_portable_relative_path,
    _load_json,
)
from security_scan import _json_safety_errors


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
GITIGNORE_ENCODING_ERROR = (
    "bindings.local.json: .gitignore must be valid UTF-8"
)
GITIGNORE_GIT_ERROR = (
    "bindings.local.json: unable to verify .gitignore with git"
)
GITIGNORE_NOT_IGNORED_ERROR = (
    "bindings.local.json: must be ignored by .gitignore"
)


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
