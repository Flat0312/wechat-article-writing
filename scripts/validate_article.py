"""Article project state validation (article-state.json, artifacts, approvals).

Delegates the HTML five-file gate to ``validate_html_delivery``. Not a
stable cross-skill interface; the stable entry point is the
``validate_project.py`` CLI.
"""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

from article_state import ALLOWED_STATUS, STAGES, file_hash

from project_checks import (
    SHA256_RE,
    _is_logical_identifier,
    _is_portable_relative_path,
    _load_json,
)
from security_scan import _json_safety_errors
from validate_html_delivery import check_html_delivery


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
    errors.extend(check_html_delivery(root, state))
    errors.extend(_json_safety_errors(state))
    return errors
