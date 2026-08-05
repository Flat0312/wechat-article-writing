from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


SCHEMA_VERSION = "1.0"
RECEIPT_NAME = "cheat-status-receipt.json"
RECEIPT_TYPE = "post-migrate-cheat-status"
_BINDING_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class StatusReceiptError(ValueError):
    """Raised when a Cheat status result cannot establish compatibility."""


def _load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as error:
        raise StatusReceiptError(f"missing JSON file: {path}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise StatusReceiptError(f"invalid JSON file: {path}") from error
    if not isinstance(value, dict):
        raise StatusReceiptError("status receipt JSON root must be an object")
    return value


def _timestamp(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise StatusReceiptError("checked_at must be an ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise StatusReceiptError("checked_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None:
        raise StatusReceiptError("checked_at must include a timezone")
    return value


def _binding(value: object) -> str:
    if not isinstance(value, str) or not _BINDING_RE.fullmatch(value):
        raise StatusReceiptError(
            "target_project_binding must be a portable logical binding name"
        )
    return value


def _schema_version(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or any(
        char.isspace() for char in value
    ):
        raise StatusReceiptError("cheat_schema_version must be a non-empty version")
    return value


def _read_cheat_schema(cheat_project: Path) -> str:
    state_path = cheat_project.expanduser().resolve() / ".cheat-state.json"
    state = _load_json(state_path)
    version = state.get("schema_version")
    if not isinstance(version, str) or not version:
        raise StatusReceiptError("Cheat state has no schema_version")
    return version


def _validate_normalized_status(
    payload: dict[str, object], expected_binding: str, actual_schema: str
) -> dict[str, object]:
    if payload.get("source") != "cheat-status":
        raise StatusReceiptError("status receipt source must be cheat-status")
    if payload.get("status") != "compatible":
        raise StatusReceiptError("post-migrate Cheat status must be compatible")
    binding = _binding(payload.get("target_project_binding"))
    if binding != expected_binding:
        raise StatusReceiptError("status receipt target binding does not match")
    cheat_schema = _schema_version(payload.get("cheat_schema_version"))
    if cheat_schema != actual_schema:
        raise StatusReceiptError(
            "status receipt schema version does not match .cheat-state.json"
        )
    checked_at = _timestamp(payload.get("checked_at"))
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "target_project_binding": binding,
        "cheat_schema_version": cheat_schema,
        "status": "compatible",
        "source": "cheat-status",
        "checked_at": checked_at,
    }


def validate_receipt(
    receipt: dict[str, object], expected_binding: str, cheat_project: Path
) -> dict[str, object]:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise StatusReceiptError("unsupported status receipt schema_version")
    if receipt.get("receipt_type") != RECEIPT_TYPE:
        raise StatusReceiptError("receipt_type must be post-migrate-cheat-status")
    actual_schema = _read_cheat_schema(cheat_project)
    return _validate_normalized_status(receipt, expected_binding, actual_schema)


def record_status(
    target_project: Path,
    cheat_project: Path,
    status_receipt: Path,
    target_binding: str,
) -> dict[str, object]:
    target_project = target_project.expanduser().resolve()
    cheat_project = cheat_project.expanduser().resolve()
    if not target_project.is_dir():
        raise StatusReceiptError(f"target project does not exist: {target_project}")
    if not cheat_project.is_dir():
        raise StatusReceiptError(f"Cheat project does not exist: {cheat_project}")
    payload = _load_json(status_receipt.expanduser().resolve())
    normalized = _validate_normalized_status(
        payload, target_binding, _read_cheat_schema(cheat_project)
    )
    output = target_project / RECEIPT_NAME
    temporary = output.with_suffix(output.suffix + ".tmp")
    try:
        temporary.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output)
    except OSError as error:
        raise StatusReceiptError(f"cannot write status receipt: {output}") from error
    return {**normalized, "receipt_path": RECEIPT_NAME}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and record a post-migrate Cheat status receipt"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("target_project", type=Path)
    record_parser.add_argument("--cheat-project", type=Path, required=True)
    record_parser.add_argument("--status-receipt", type=Path, required=True)
    record_parser.add_argument("--target-binding", required=True)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("receipt", type=Path)
    verify_parser.add_argument("--cheat-project", type=Path, required=True)
    verify_parser.add_argument("--target-binding", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "record":
            result = record_status(
                args.target_project,
                args.cheat_project,
                args.status_receipt,
                args.target_binding,
            )
        else:
            result = validate_receipt(
                _load_json(args.receipt),
                args.target_binding,
                args.cheat_project,
            )
    except (OSError, StatusReceiptError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
