from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


SCHEMA_VERSION = "1.0"
RECEIPT_NAME = "cheat-form-receipt.json"
RECEIPT_TYPE = "wechat-cheat-form"
_BINDING_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
FORM_VALUES = {"long-essay", "news-card"}
ROOT_ROUTES = {
    "cheat-init",
    "cheat-status",
    "cheat-score",
    "cheat-predict",
}


class FormReceiptError(ValueError):
    """Raised when Cheat invocation and content-form adaptation are not proven."""


def _load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as error:
        raise FormReceiptError(f"missing JSON file: {path}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise FormReceiptError(f"invalid JSON file: {path}") from error
    if not isinstance(value, dict):
        raise FormReceiptError("form receipt JSON root must be an object")
    return value


def _binding(value: object) -> str:
    if not isinstance(value, str) or not _BINDING_RE.fullmatch(value):
        raise FormReceiptError("target_project_binding must be a logical binding name")
    return value


def _version(value: object, label: str) -> str:
    if not isinstance(value, str) or not _VERSION_RE.fullmatch(value):
        raise FormReceiptError(f"{label} must be a logical version or adapter name")
    return value


def _timestamp(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise FormReceiptError("checked_at must be a timezone-aware ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise FormReceiptError("checked_at must be a timezone-aware ISO 8601 timestamp") from error
    if parsed.tzinfo is None:
        raise FormReceiptError("checked_at must include a timezone")
    return value


def _form(value: object) -> str:
    if value not in FORM_VALUES:
        raise FormReceiptError("content_form must be long-essay or news-card")
    return value


def _read_cheat_schema(cheat_project: Path) -> str:
    state = _load_json(cheat_project.expanduser().resolve() / ".cheat-state.json")
    version = state.get("schema_version")
    if not isinstance(version, str) or not version:
        raise FormReceiptError("Cheat state has no schema_version")
    return version


def _normalize(
    payload: dict[str, object],
    expected_binding: str,
    expected_form: str,
    actual_schema: str,
) -> dict[str, object]:
    if payload.get("source") != "cheat-on-content":
        raise FormReceiptError("form receipt source must be cheat-on-content")
    if payload.get("root_skill_called") is not True:
        raise FormReceiptError("root_skill_called must be true")
    if payload.get("root_call_status") != "completed":
        raise FormReceiptError("root Cheat call must be completed")
    root_route = payload.get("root_route")
    if root_route not in ROOT_ROUTES:
        raise FormReceiptError("root_route is not a supported Cheat root route")
    binding = _binding(payload.get("target_project_binding"))
    if binding != expected_binding:
        raise FormReceiptError("form receipt target binding does not match")
    content_form = _form(payload.get("content_form"))
    if content_form != expected_form:
        raise FormReceiptError("form receipt content_form does not match")
    cheat_schema = _version(payload.get("cheat_schema_version"), "cheat_schema_version")
    if cheat_schema != actual_schema:
        raise FormReceiptError("form receipt schema version does not match .cheat-state.json")

    if payload.get("rubric_form_mismatch") is True:
        raise FormReceiptError("Cheat reports rubric_form_mismatch=true")
    rubric_status = payload.get("rubric_status")
    if rubric_status != "compatible":
        raise FormReceiptError("rubric_status must be compatible")
    rubric_adapter = _version(payload.get("rubric_adapter"), "rubric_adapter")
    expected_prefix = f"wechat-{content_form}-"
    if not rubric_adapter.startswith(expected_prefix):
        raise FormReceiptError("rubric_adapter is not for the requested content form")
    rubric_version = _version(payload.get("rubric_version"), "rubric_version")
    checked_at = _timestamp(payload.get("checked_at"))
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "target_project_binding": binding,
        "content_form": content_form,
        "cheat_schema_version": cheat_schema,
        "source": "cheat-on-content",
        "root_skill_called": True,
        "root_route": root_route,
        "root_call_status": "completed",
        "rubric_adapter": rubric_adapter,
        "rubric_status": "compatible",
        "rubric_version": rubric_version,
        "checked_at": checked_at,
    }


def validate_receipt(
    receipt: dict[str, object],
    expected_binding: str,
    cheat_project: Path,
    expected_form: str = "long-essay",
) -> dict[str, object]:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise FormReceiptError("unsupported form receipt schema_version")
    if receipt.get("receipt_type") != RECEIPT_TYPE:
        raise FormReceiptError("receipt_type must be wechat-cheat-form")
    actual_schema = _read_cheat_schema(cheat_project)
    normalized = _normalize(
        receipt,
        expected_binding,
        expected_form,
        actual_schema,
    )
    if receipt != normalized:
        raise FormReceiptError("form receipt contains unsupported or non-normalized fields")
    return normalized


def record_form(
    target_project: Path,
    cheat_project: Path,
    status_receipt: Path,
    target_binding: str,
    content_form: str = "long-essay",
) -> dict[str, object]:
    target_project = target_project.expanduser().resolve()
    cheat_project = cheat_project.expanduser().resolve()
    if not target_project.is_dir():
        raise FormReceiptError(f"target project does not exist: {target_project}")
    if not cheat_project.is_dir():
        raise FormReceiptError(f"Cheat project does not exist: {cheat_project}")
    payload = _load_json(status_receipt.expanduser().resolve())
    normalized = _normalize(
        payload,
        target_binding,
        content_form,
        _read_cheat_schema(cheat_project),
    )
    output = target_project / RECEIPT_NAME
    if output.is_file():
        existing = _load_json(output)
        if existing != normalized:
            raise FormReceiptError("cheat-form-receipt.json already binds another form or rubric")
        return {**normalized, "receipt_path": RECEIPT_NAME}
    temporary = output.with_suffix(output.suffix + ".tmp")
    try:
        temporary.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output)
    except OSError as error:
        raise FormReceiptError(f"cannot write form receipt: {output}") from error
    return {**normalized, "receipt_path": RECEIPT_NAME}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Record and verify Cheat content-form and rubric adaptation status"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("target_project", type=Path)
    record_parser.add_argument("--cheat-project", type=Path, required=True)
    record_parser.add_argument("--status-receipt", type=Path, required=True)
    record_parser.add_argument("--target-binding", required=True)
    record_parser.add_argument("--content-form", choices=sorted(FORM_VALUES), default="long-essay")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("receipt", type=Path)
    verify_parser.add_argument("--cheat-project", type=Path, required=True)
    verify_parser.add_argument("--target-binding", required=True)
    verify_parser.add_argument("--content-form", choices=sorted(FORM_VALUES), default="long-essay")

    args = parser.parse_args(argv)
    try:
        if args.command == "record":
            result = record_form(
                args.target_project,
                args.cheat_project,
                args.status_receipt,
                args.target_binding,
                args.content_form,
            )
        else:
            result = validate_receipt(
                _load_json(args.receipt),
                args.target_binding,
                args.cheat_project,
                args.content_form,
            )
    except (OSError, FormReceiptError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
