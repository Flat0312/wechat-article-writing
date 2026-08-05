from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path, PurePosixPath
import re
import sys

from article_state import file_hash


class BlindScoreError(RuntimeError):
    pass


REFUSAL_CODES = {
    "blocked_contaminated_input",
    "blocked_rubric_memo",
    "blocked_audience",
    "script_path_invalid",
    "rubric_unparseable",
    "non_blind_warning",
}
CONFIDENCE_VALUES = {"high", "medium", "low"}
SCRIPT_HASH_RE = re.compile(r"^[0-9a-f]{12}$")
VERSION_RE = re.compile(
    r"(?im)(?:当前版本|current\s+version|rubric[_ -]?version)"
    r"[^:\n]{0,20}[:：]\s*`?([A-Za-z0-9][A-Za-z0-9_.-]*)"
)
DIMENSION_LIST_RE = re.compile(
    r"(?im)^\s*(?:dimensions?|维度)\s*[:=：]\s*\[?"
    r"([A-Z][A-Z0-9]{1,5}(?:\s*[,，/|]\s*[A-Z][A-Z0-9]{1,5})+)"
)
DIMENSION_TABLE_RE = re.compile(
    r"(?im)^\s*\|\s*[^|\n]*\(([A-Z][A-Z0-9]{1,5})\)\s*\|"
)
FORMULA_TOKEN_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,5}\b")
ALLOWED_FORMULA_NON_DIMENSIONS = {"N", "MAX", "MIN"}
REQUIRED_TOP_LEVEL = {
    "subagent_version",
    "rubric_version",
    "script_path",
    "script_hash",
    "scored_at",
    "dimensions",
    "input_status",
    "self_check",
    "refusal",
}
OPTIONAL_TOP_LEVEL = {"contamination_note"}
REQUIRED_INPUT_STATUS = {
    "rubric_notes_read",
    "script_read",
    "any_other_file_read",
}
REQUIRED_SELF_CHECK = {
    "saw_play_numbers",
    "saw_comments",
    "saw_retro_segment",
    "any_contamination_signal",
}


@dataclass(frozen=True)
class RubricContract:
    version: str
    dimensions: tuple[str, ...]


def _read_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise BlindScoreError(f"cannot read {label}: {error}") from error


def _dimension_names(text: str, override: str | None) -> tuple[str, ...]:
    if override is not None:
        raw_names = [item.strip().upper() for item in override.split(",")]
    else:
        list_match = DIMENSION_LIST_RE.search(text)
        if list_match:
            raw_names = [
                item.strip().upper()
                for item in re.split(r"[,，/|]", list_match.group(1))
            ]
        else:
            raw_names = [item.upper() for item in DIMENSION_TABLE_RE.findall(text)]
            if not raw_names:
                formula_lines = [
                    line
                    for line in text.splitlines()
                    if "composite" in line.lower()
                ]
                raw_names = [
                    token
                    for line in formula_lines
                    for token in FORMULA_TOKEN_RE.findall(line)
                    if token not in ALLOWED_FORMULA_NON_DIMENSIONS
                ]
    names: list[str] = []
    for name in raw_names:
        if not re.fullmatch(r"[A-Z][A-Z0-9]{1,5}", name):
            raise BlindScoreError(f"invalid rubric dimension name: {name}")
        if name not in names:
            names.append(name)
    if len(names) not in {7, 9}:
        raise BlindScoreError(
            "rubric must declare exactly 7 or 9 dimensions; "
            f"parsed {len(names)}"
        )
    return tuple(names)


def parse_rubric(path: Path, dimensions_override: str | None = None) -> RubricContract:
    text = _read_text(path, "rubric")
    version_match = VERSION_RE.search(text)
    if version_match is None:
        raise BlindScoreError("rubric_version is missing from rubric")
    version = version_match.group(1)
    dimensions = _dimension_names(text, dimensions_override)
    return RubricContract(version=version, dimensions=dimensions)


def _portable_script_path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise BlindScoreError("script_path must be a portable relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not value.startswith("scripts/"):
        raise BlindScoreError("script_path must be below scripts/")
    if path.suffix.lower() != ".md":
        raise BlindScoreError("script_path must point to a Markdown script")
    return path.as_posix()


def _require_boolean_map(
    payload: object, required: set[str], label: str
) -> dict[str, bool]:
    if not isinstance(payload, dict) or set(payload) != required:
        raise BlindScoreError(f"{label} fields do not match the blind score schema")
    result: dict[str, bool] = {}
    for key, value in payload.items():
        if not isinstance(value, bool):
            raise BlindScoreError(f"{label}.{key} must be boolean")
        result[key] = value
    return result


def validate_score(
    payload: object,
    rubric: RubricContract,
    script: Path | None = None,
) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise BlindScoreError("blind score output must be a JSON object")
    unknown = set(payload) - REQUIRED_TOP_LEVEL - OPTIONAL_TOP_LEVEL
    missing = REQUIRED_TOP_LEVEL - set(payload)
    if missing:
        raise BlindScoreError(
            "blind score output is missing fields: " + ", ".join(sorted(missing))
        )
    if unknown:
        raise BlindScoreError(
            "blind score output has unsupported fields: " + ", ".join(sorted(unknown))
        )
    if not isinstance(payload.get("subagent_version"), str) or not payload[
        "subagent_version"
    ].strip():
        raise BlindScoreError("subagent_version is required")
    if payload.get("rubric_version") != rubric.version:
        raise BlindScoreError(
            "rubric_version mismatch: "
            f"expected {rubric.version}, got {payload.get('rubric_version')}"
        )
    script_path = _portable_script_path(payload.get("script_path"))
    script_hash = payload.get("script_hash")
    if not isinstance(script_hash, str) or not SCRIPT_HASH_RE.fullmatch(script_hash):
        raise BlindScoreError("script_hash must be a 12-character lowercase hex prefix")
    scored_at = payload.get("scored_at")
    if not isinstance(scored_at, str) or not scored_at.strip():
        raise BlindScoreError("scored_at is required")
    try:
        datetime.fromisoformat(scored_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise BlindScoreError("scored_at must be ISO 8601") from error

    dimensions = payload.get("dimensions")
    if not isinstance(dimensions, dict):
        raise BlindScoreError("dimensions must be an object")
    actual_names = tuple(dimensions)
    if set(actual_names) != set(rubric.dimensions):
        missing_dimensions = sorted(set(rubric.dimensions) - set(actual_names))
        extra_dimensions = sorted(set(actual_names) - set(rubric.dimensions))
        raise BlindScoreError(
            "dimension set mismatch: "
            f"missing={missing_dimensions}, extra={extra_dimensions}"
        )
    for name in rubric.dimensions:
        value = dimensions[name]
        if not isinstance(value, dict) or set(value) != {"score", "confidence", "reason"}:
            raise BlindScoreError(
                f"dimension {name} must contain score, confidence, and reason only"
            )
        score = value["score"]
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 5:
            raise BlindScoreError(f"dimension {name}.score must be an integer from 0 to 5")
        if value["confidence"] not in CONFIDENCE_VALUES:
            raise BlindScoreError(
                f"dimension {name}.confidence must be high, medium, or low"
            )
        reason = value["reason"]
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 30:
            raise BlindScoreError(
                f"dimension {name}.reason must be a non-empty one-line string of 30 characters or fewer"
            )

    input_status = _require_boolean_map(
        payload.get("input_status"), REQUIRED_INPUT_STATUS, "input_status"
    )
    if (
        input_status["rubric_notes_read"] is not True
        or input_status["script_read"] is not True
        or input_status["any_other_file_read"] is not False
    ):
        raise BlindScoreError("input_status does not prove the two-file blind boundary")
    _require_boolean_map(payload.get("self_check"), REQUIRED_SELF_CHECK, "self_check")
    refusal = payload.get("refusal")
    if refusal is not None and refusal not in REFUSAL_CODES:
        raise BlindScoreError(f"unsupported refusal code: {refusal}")
    contamination_note = payload.get("contamination_note")
    if contamination_note is not None and not isinstance(contamination_note, str):
        raise BlindScoreError("contamination_note must be a string when present")

    if script is not None:
        script_file = Path(script).expanduser().resolve(strict=True)
        actual_prefix = file_hash(script_file)[:12]
        if actual_prefix != script_hash:
            raise BlindScoreError(
                "script_hash does not match the supplied script file"
            )
    return {
        "ok": True,
        "rubric_version": rubric.version,
        "dimensions": list(rubric.dimensions),
        "dimension_count": len(rubric.dimensions),
        "score": payload,
        "script_path": script_path,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("score_json", type=Path)
    validate.add_argument("rubric", type=Path)
    validate.add_argument("--script", type=Path)
    validate.add_argument(
        "--dimensions",
        help="explicit comma-separated dimensions when the rubric uses a non-standard table",
    )
    args = parser.parse_args(argv)
    try:
        rubric = parse_rubric(args.rubric, args.dimensions)
        try:
            payload = json.loads(_read_text(args.score_json, "blind score JSON"))
        except json.JSONDecodeError as error:
            raise BlindScoreError(f"blind score JSON is invalid: {error}") from error
        result = validate_score(payload, rubric, args.script)
    except (BlindScoreError, FileNotFoundError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
