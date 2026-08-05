from __future__ import annotations

import argparse
import json
import re
import stat
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path, PurePosixPath, PureWindowsPath

from cheat_form_adapter import FormReceiptError, validate_receipt


SCHEMA_VERSION = "1.0"
FINAL_PATH = "drafts/final.md"
RECEIPT_NAME = "prediction-input-reference.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class SnapshotError(ValueError):
    """Raised when a final artifact cannot be safely bridged to Cheat."""


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as error:
        raise SnapshotError(f"missing JSON file: {path}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SnapshotError(f"invalid JSON file: {path}") from error
    if not isinstance(value, dict):
        raise SnapshotError(f"JSON root must be an object: {path}")
    return value


def _hash_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def _portable_relative(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise SnapshotError("artifact path must be a non-empty relative path")
    windows = PureWindowsPath(value)
    portable = PurePosixPath(value.replace("\\", "/"))
    if (
        windows.anchor
        or portable.is_absolute()
        or ".." in portable.parts
        or "." in portable.parts
    ):
        raise SnapshotError("artifact path must be portable and relative")
    return portable.as_posix()


def _safe_article_id(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise SnapshotError("article_id must be a non-empty string")
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip(".-")
    return safe or "article"


def _resolve_under(root: Path, relative: str) -> Path:
    root = root.resolve()
    target = (root / Path(*PurePosixPath(relative).parts)).resolve()
    try:
        target.relative_to(root)
    except ValueError as error:
        raise SnapshotError("resolved path escapes its project root") from error
    return target


def _read_final(project: Path, state: dict[str, object]) -> tuple[Path, bytes, str]:
    artifacts = state.get("artifacts")
    approvals = state.get("approvals")
    statuses = state.get("stage_status")
    if not isinstance(artifacts, dict) or not isinstance(approvals, dict):
        raise SnapshotError("article state must contain artifacts and approvals")
    if not isinstance(statuses, dict) or statuses.get("final") != "completed":
        raise SnapshotError("final stage must be completed before prediction")
    if "final" in (state.get("stale_artifacts") or []):
        raise SnapshotError("final artifact is stale; obtain a new approval")

    artifact = artifacts.get("final")
    approval = approvals.get("final")
    if not isinstance(artifact, dict) or not isinstance(approval, dict):
        raise SnapshotError("final artifact and final approval are required")
    path = _portable_relative(artifact.get("path"))
    if path != FINAL_PATH:
        raise SnapshotError(f"final artifact path must be {FINAL_PATH}")
    if approval.get("approved") is not True:
        raise SnapshotError("final approval must be explicitly approved")
    if approval.get("artifact_role") != "final":
        raise SnapshotError("final approval must bind artifact_role=final")

    recorded_hash = artifact.get("sha256")
    approval_hash = approval.get("artifact_sha256")
    if not isinstance(recorded_hash, str) or not SHA256_RE.fullmatch(recorded_hash):
        raise SnapshotError("artifacts.final.sha256 must be a SHA256 value")
    if not isinstance(approval_hash, str) or not SHA256_RE.fullmatch(approval_hash):
        raise SnapshotError("approvals.final.artifact_sha256 must be a SHA256 value")
    if recorded_hash != approval_hash:
        raise SnapshotError("final approval hash does not match the recorded final hash")

    final_path = _resolve_under(project, path)
    try:
        final_bytes = final_path.read_bytes()
        final_bytes.decode("utf-8")
    except (OSError, UnicodeError) as error:
        raise SnapshotError(f"final artifact cannot be read as UTF-8: {final_path}") from error
    actual_hash = _hash_bytes(final_bytes)
    if actual_hash != recorded_hash or actual_hash != approval_hash:
        raise SnapshotError("final artifact bytes do not match the approved SHA256")
    return final_path, final_bytes, actual_hash


def _resolve_cheat_project(
    article_project: Path, state: dict[str, object], explicit: Path | None
) -> Path:
    if explicit is not None:
        cheat_project = explicit.expanduser().resolve()
    else:
        binding_name = state.get("cheat_binding")
        binding_file = article_project.parent.parent / "account-profile" / "bindings.local.json"
        if not isinstance(binding_name, str) or not binding_file.is_file():
            raise SnapshotError("--cheat-project is required when no local Cheat binding is available")
        bindings = _load_json(binding_file).get("bindings")
        binding = bindings.get(binding_name) if isinstance(bindings, dict) else None
        path = binding.get("path") if isinstance(binding, dict) else None
        if not isinstance(path, str) or not path:
            raise SnapshotError(f"Cheat binding is missing a path: {binding_name}")
        cheat_project = Path(path).expanduser().resolve()
    if not cheat_project.is_dir():
        raise SnapshotError(f"Cheat project does not exist: {cheat_project}")
    return cheat_project


def _validate_form_receipt(
    article_project: Path, state: dict[str, object], cheat_project: Path
) -> dict[str, object]:
    receipt_path = article_project / "cheat-form-receipt.json"
    try:
        receipt = _load_json(receipt_path)
        binding = state.get("cheat_binding")
        if not isinstance(binding, str):
            raise FormReceiptError("article state has no logical Cheat binding")
        return validate_receipt(
            receipt,
            binding,
            cheat_project,
            expected_form="long-essay",
        )
    except (SnapshotError, FormReceiptError) as error:
        raise SnapshotError(
            "Cheat content-form and rubric adaptation receipt is required: "
            f"{error}"
        ) from error


def _make_read_only(path: Path) -> None:
    path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)


def _write_receipt(path: Path, receipt: dict[str, object]) -> dict[str, object]:
    if path.is_file():
        existing = _load_json(path)
        immutable_fields = (
            "article_id",
            "final_path",
            "final_sha256",
            "snapshot_path",
            "snapshot_sha256",
        )
        if any(existing.get(field) != receipt.get(field) for field in immutable_fields):
            raise SnapshotError("prediction-input-reference.json already binds another final")
        return existing
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return receipt


def create_snapshot(project: Path, cheat_project: Path | None = None) -> dict[str, object]:
    article_project = Path(project).expanduser().resolve()
    state = _load_json(article_project / "article-state.json")
    _, final_bytes, final_hash = _read_final(article_project, state)
    cheat_root = _resolve_cheat_project(article_project, state, cheat_project)
    _validate_form_receipt(article_project, state, cheat_root)
    scripts_root = cheat_root / "scripts"
    scripts_root.mkdir(exist_ok=True)

    article_id = _safe_article_id(state.get("article_id"))
    snapshot_name = f"wechat-{article_id}-{final_hash}.md"
    snapshot_path = scripts_root / snapshot_name
    metadata = {
        "wechat_snapshot_schema": SCHEMA_VERSION,
        "content_form": "long-essay",
        "article_id": state.get("article_id"),
        "source_path": FINAL_PATH,
        "source_sha256": final_hash,
    }
    header = "---\n" + "\n".join(
        f"{key}: {json.dumps(value, ensure_ascii=False)}"
        for key, value in metadata.items()
    ) + "\n---\n"
    expected_bytes = header.encode("utf-8") + final_bytes
    if snapshot_path.exists():
        try:
            if snapshot_path.read_bytes() != expected_bytes:
                raise SnapshotError("immutable Cheat snapshot already contains different bytes")
        except OSError as error:
            raise SnapshotError(f"Cheat snapshot cannot be read: {snapshot_path}") from error
    else:
        snapshot_path.write_bytes(expected_bytes)
    _make_read_only(snapshot_path)

    snapshot_relative = snapshot_path.relative_to(cheat_root).as_posix()
    snapshot_hash = _hash_bytes(expected_bytes)
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "status": "input_ready",
        "content_form": "long-essay",
        "article_id": state.get("article_id"),
        "cheat_binding": state.get("cheat_binding"),
        "final_path": FINAL_PATH,
        "final_sha256": final_hash,
        "snapshot_path": snapshot_relative,
        "snapshot_sha256": snapshot_hash,
        "read_only": True,
        "created_at": _now(),
    }
    receipt_path = article_project / RECEIPT_NAME
    return _write_receipt(receipt_path, receipt)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Bridge an approved WeChat final into a Cheat script snapshot")
    parser.add_argument("project", type=Path)
    parser.add_argument("--cheat-project", type=Path)
    args = parser.parse_args(argv)
    try:
        receipt = create_snapshot(args.project, args.cheat_project)
    except (OSError, SnapshotError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
