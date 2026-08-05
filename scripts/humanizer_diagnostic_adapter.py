from __future__ import annotations

import argparse
import json
import re
import sys
from hashlib import sha256
from pathlib import Path


SCHEMA_VERSION = "1.0"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TOP_LEVEL_FIELDS = {"schema_version", "source_skill", "mode", "input_sha256", "issues"}
ISSUE_FIELDS = {
    "location",
    "pattern",
    "suggestion",
    "scope",
    "adds_facts",
    "changes_meaning",
    "severity",
}
SEVERITY_VALUES = {"low", "medium", "high"}


class DiagnosticContractError(ValueError):
    """Raised when a humanizer response is not a local diagnostic report."""


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as error:
        raise DiagnosticContractError(f"missing JSON file: {path}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DiagnosticContractError(f"invalid diagnostic JSON: {path}") from error


def _text(value: object, label: str, limit: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DiagnosticContractError(f"{label} must be a non-empty string")
    if len(value) > limit:
        raise DiagnosticContractError(f"{label} is too long")
    return value.strip()


def _hash_file(path: Path) -> str:
    digest = sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
    except (OSError, UnicodeError) as error:
        raise DiagnosticContractError(f"cannot read diagnostic input: {path}") from error
    return digest.hexdigest()


def validate_payload(payload: object, input_path: Path | None = None) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise DiagnosticContractError("diagnostic response must be a JSON object")
    if set(payload) != TOP_LEVEL_FIELDS:
        raise DiagnosticContractError(
            "diagnostic response must contain only schema_version, source_skill, mode, input_sha256, and issues"
        )
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise DiagnosticContractError("unsupported diagnostic schema_version")
    if payload.get("source_skill") != "humanizer-zh":
        raise DiagnosticContractError("diagnostic response source_skill must be humanizer-zh")
    if payload.get("mode") != "diagnostic":
        raise DiagnosticContractError("diagnostic response mode must be diagnostic")

    input_hash = payload.get("input_sha256")
    if not isinstance(input_hash, str) or not SHA256_RE.fullmatch(input_hash):
        raise DiagnosticContractError("input_sha256 must be a lowercase SHA256 value")
    if input_path is not None:
        actual_hash = _hash_file(input_path.expanduser().resolve())
        if actual_hash != input_hash:
            raise DiagnosticContractError("input_sha256 does not match the supplied draft")

    issues = payload.get("issues")
    if not isinstance(issues, list):
        raise DiagnosticContractError("issues must be an array")
    if len(issues) > 100:
        raise DiagnosticContractError("issues may contain at most 100 items")

    normalized: list[dict[str, object]] = []
    for index, item in enumerate(issues):
        label = f"issues[{index}]"
        if not isinstance(item, dict) or not set(item).issubset(ISSUE_FIELDS):
            raise DiagnosticContractError(f"{label} has unsupported fields")
        required = {"location", "pattern", "suggestion", "scope", "adds_facts", "changes_meaning"}
        if set(item) != required and set(item) != required | {"severity"}:
            raise DiagnosticContractError(
                f"{label} must contain location, pattern, suggestion, scope, adds_facts, and changes_meaning"
            )
        location = _text(item.get("location"), f"{label}.location", 200)
        pattern = _text(item.get("pattern"), f"{label}.pattern", 200)
        suggestion = _text(item.get("suggestion"), f"{label}.suggestion", 1000)
        if item.get("scope") != "local":
            raise DiagnosticContractError(f"{label}.scope must be local")
        if item.get("adds_facts") is not False:
            raise DiagnosticContractError(f"{label}.adds_facts must be false")
        if item.get("changes_meaning") is not False:
            raise DiagnosticContractError(f"{label}.changes_meaning must be false")
        result: dict[str, object] = {
            "location": location,
            "pattern": pattern,
            "suggestion": suggestion,
            "scope": "local",
            "adds_facts": False,
            "changes_meaning": False,
        }
        if "severity" in item:
            if item["severity"] not in SEVERITY_VALUES:
                raise DiagnosticContractError(f"{label}.severity is invalid")
            result["severity"] = item["severity"]
        normalized.append(result)
    return {
        "schema_version": SCHEMA_VERSION,
        "source_skill": "humanizer-zh",
        "mode": "diagnostic",
        "input_sha256": input_hash,
        "issues": normalized,
        "draft_owner": "wechat-article-writing",
        "requires_local_rewrite": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a local-only humanizer diagnostic response"
    )
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--input", type=Path, help="draft whose SHA256 must match input_sha256")
    args = parser.parse_args(argv)
    try:
        result = validate_payload(_load_json(args.input_json), args.input)
    except (DiagnosticContractError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
