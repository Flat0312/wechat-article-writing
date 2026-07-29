from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import sys
import tempfile

from article_state import file_hash


SOURCE_PATH = PurePosixPath("visuals/assets/baoyu/source.md")
RECEIPT_PATH = PurePosixPath("visuals/assets/baoyu/receipt.json")


class AdapterError(RuntimeError):
    pass


def _project_root(project: Path) -> Path:
    try:
        root = Path(project).expanduser().resolve(strict=True)
    except FileNotFoundError as error:
        raise AdapterError(f"article project does not exist: {project}") from error
    if not root.is_dir():
        raise AdapterError(f"article project is not a directory: {project}")
    return root


def _load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as error:
        raise AdapterError(f"required file is missing: {path.name}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AdapterError(f"cannot read valid JSON from {path.name}: {error}") from error
    if not isinstance(value, dict):
        raise AdapterError(f"{path.name} must contain a JSON object")
    return value


def _resolve_recorded_file(project: Path, value: object, label: str) -> tuple[str, Path]:
    if not isinstance(value, str) or not value or "\\" in value:
        raise AdapterError(f"{label} must be a portable relative path")
    portable = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if portable.is_absolute() or windows.anchor or ".." in portable.parts:
        raise AdapterError(f"{label} must be a portable relative path")
    try:
        target = (project / Path(*portable.parts)).resolve(strict=True)
        target.relative_to(project)
    except FileNotFoundError as error:
        raise AdapterError(f"{label} does not exist: {value}") from error
    except (OSError, RuntimeError, ValueError) as error:
        raise AdapterError(f"{label} escapes the article project") from error
    if not target.is_file():
        raise AdapterError(f"{label} is not a file: {value}")
    return portable.as_posix(), target


def _safe_output_path(project: Path, relative: PurePosixPath) -> Path:
    target = project / Path(*relative.parts)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.parent.resolve(strict=True).relative_to(project)
    except (OSError, RuntimeError, ValueError) as error:
        raise AdapterError(f"output path escapes the article project: {relative}") from error
    if target.is_symlink():
        raise AdapterError(f"output path must not be a symbolic link: {relative}")
    if target.exists() and not target.is_file():
        raise AdapterError(f"output path is not a file: {relative}")
    return target


def _approved_final(project: Path) -> tuple[str, Path, str]:
    state = _load_json(project / "article-state.json")
    artifacts = state.get("artifacts")
    approvals = state.get("approvals")
    if not isinstance(artifacts, dict) or not isinstance(approvals, dict):
        raise AdapterError("article-state.json has invalid artifacts or approvals")

    artifact = artifacts.get("final")
    if not isinstance(artifact, dict):
        raise AdapterError("record the final artifact before preparing Baoyu input")
    final_path, final_file = _resolve_recorded_file(
        project, artifact.get("path"), "artifacts.final.path"
    )
    recorded_hash = artifact.get("sha256")
    if not isinstance(recorded_hash, str) or not recorded_hash:
        raise AdapterError("artifacts.final.sha256 is missing")
    actual_hash = file_hash(final_file)
    if actual_hash != recorded_hash:
        raise AdapterError("the recorded final artifact hash does not match the file")

    approval = approvals.get("final")
    if (
        not isinstance(approval, dict)
        or approval.get("approved") is not True
        or approval.get("artifact_role") != "final"
        or approval.get("artifact_sha256") != actual_hash
    ):
        raise AdapterError("the current final artifact is not approved against its SHA256")
    return final_path, final_file, actual_hash


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.tmp-", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise


def prepare(project: Path) -> dict[str, object]:
    root = _project_root(project)
    final_path, final_file, final_hash = _approved_final(root)
    source = _safe_output_path(root, SOURCE_PATH)
    receipt = _safe_output_path(root, RECEIPT_PATH)

    try:
        final_bytes = final_file.read_bytes()
    except OSError as error:
        raise AdapterError(f"cannot read the approved final artifact: {error}") from error
    try:
        _write_atomic(source, final_bytes)
    except OSError as error:
        raise AdapterError(f"cannot write the isolated Baoyu source: {error}") from error
    receipt_data = {
        "schema_version": "1.0",
        "final_path": final_path,
        "final_sha256": final_hash,
        "source_path": SOURCE_PATH.as_posix(),
    }
    try:
        _write_atomic(
            receipt,
            (json.dumps(receipt_data, ensure_ascii=False, indent=2) + "\n").encode(
                "utf-8"
            ),
        )
    except OSError as error:
        raise AdapterError(f"cannot write the Baoyu receipt: {error}") from error
    return {
        "ok": True,
        "source_path": SOURCE_PATH.as_posix(),
        "receipt_path": RECEIPT_PATH.as_posix(),
        "final_sha256": final_hash,
    }


def verify(project: Path) -> dict[str, object]:
    root = _project_root(project)
    _, receipt_file = _resolve_recorded_file(
        root, RECEIPT_PATH.as_posix(), "Baoyu receipt"
    )
    receipt = _load_json(receipt_file)
    if receipt.get("schema_version") != "1.0":
        raise AdapterError("unsupported Baoyu receipt schema_version")
    if receipt.get("source_path") != SOURCE_PATH.as_posix():
        raise AdapterError("Baoyu receipt source_path is invalid")
    _resolve_recorded_file(root, receipt.get("source_path"), "receipt.source_path")

    final_path, _, final_hash = _approved_final(root)
    if receipt.get("final_path") != final_path or receipt.get("final_sha256") != final_hash:
        raise AdapterError("the approved final artifact changed after Baoyu prepare; run prepare again")
    return {
        "ok": True,
        "source_path": SOURCE_PATH.as_posix(),
        "final_path": final_path,
        "final_sha256": final_hash,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("project", type=Path)
    args = parser.parse_args(argv)
    try:
        result = prepare(args.project) if args.command == "prepare" else verify(args.project)
    except AdapterError as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
