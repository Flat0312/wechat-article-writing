from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCHEMA_VERSION = "1.0"
ALLOWED_KINDS = {
    "structure",
    "scene",
    "analogy",
    "rhythm",
    "transition",
    "self_check",
}
TOP_LEVEL_FIELDS = {"schema_version", "source_skill", "mode", "suggestions"}
SUGGESTION_FIELDS = {"kind", "text", "section_ref", "reason"}
IDENTITY_MARKERS = (
    "卡兹克",
    "数字生命",
    "khazix",
    "永远对世界保持好奇",
)


class CraftContractError(ValueError):
    """Raised when a writing Skill response crosses the craft-only boundary."""


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as error:
        raise CraftContractError(f"missing JSON file: {path}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CraftContractError(f"invalid craft JSON: {path}") from error


def _text(value: object, label: str, limit: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CraftContractError(f"{label} must be a non-empty string")
    if len(value) > limit:
        raise CraftContractError(f"{label} is too long")
    return value.strip()


def _reject_identity(value: str, label: str) -> None:
    lowered = value.casefold()
    if any(marker.casefold() in lowered for marker in IDENTITY_MARKERS):
        raise CraftContractError(f"{label} contains the external author identity")


def validate_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise CraftContractError("craft response must be a JSON object")
    if set(payload) != TOP_LEVEL_FIELDS:
        raise CraftContractError(
            "craft response must contain only schema_version, source_skill, mode, and suggestions"
        )
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise CraftContractError("unsupported craft schema_version")
    if payload.get("source_skill") != "khazix-writer":
        raise CraftContractError("craft response source_skill must be khazix-writer")
    if payload.get("mode") != "craft-only":
        raise CraftContractError("craft response mode must be craft-only")

    suggestions = payload.get("suggestions")
    if not isinstance(suggestions, list) or not suggestions:
        raise CraftContractError("suggestions must be a non-empty array")
    if len(suggestions) > 50:
        raise CraftContractError("suggestions may contain at most 50 items")

    normalized: list[dict[str, str]] = []
    for index, item in enumerate(suggestions):
        label = f"suggestions[{index}]"
        if not isinstance(item, dict) or not set(item).issubset(SUGGESTION_FIELDS):
            raise CraftContractError(f"{label} has unsupported fields")
        if "kind" not in item or "text" not in item:
            raise CraftContractError(f"{label} must contain kind and text")
        kind = item["kind"]
        if not isinstance(kind, str) or kind not in ALLOWED_KINDS:
            raise CraftContractError(f"{label}.kind is not a craft-only kind")
        text = _text(item["text"], f"{label}.text", 2000)
        _reject_identity(text, f"{label}.text")
        result = {"kind": kind, "text": text}
        for optional in ("section_ref", "reason"):
            if optional in item:
                value = _text(item[optional], f"{label}.{optional}", 500)
                _reject_identity(value, f"{label}.{optional}")
                result[optional] = value
        normalized.append(result)
    return {
        "schema_version": SCHEMA_VERSION,
        "source_skill": "khazix-writer",
        "mode": "craft-only",
        "suggestions": normalized,
        "draft_owner": "wechat-article-writing",
        "accepted_for_integration": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a bounded Khazix craft-assistant response"
    )
    parser.add_argument("input_json", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate_payload(_load_json(args.input_json))
    except (CraftContractError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
