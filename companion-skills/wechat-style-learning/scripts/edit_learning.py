from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_VERSION = "1.0"
RULE_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
RULE_TYPES = {
    "structure",
    "opening",
    "closing",
    "rhythm",
    "tone",
    "expression",
    "evidence",
}
MACHINE_PATH_RE = re.compile(
    r"(?i)(?:[a-z]:[\\/]|\\\\[^\\/\s]+[\\/]|file:/{1,3}|"
    r"(?:^|[\s\"'（(])/(?:users|home|var|etc|tmp)/)"
)
VALIDATED_START = "<!-- style-learning:validated:start -->"
VALIDATED_END = "<!-- style-learning:validated:end -->"
PROVISIONAL_START = "<!-- style-learning:provisional:start -->"
PROVISIONAL_END = "<!-- style-learning:provisional:end -->"
OBSERVATION_SCHEMA_VERSION = "1.0"
OBSERVATION_PREFIX = "history/voice-observations/"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        delete=False,
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_write_json(path: Path, payload: Any) -> None:
    _atomic_write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _portable_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._")
    return slug[:48] or "article"


def _normalize_timestamp(value: datetime | None) -> datetime:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc)


def _validate_profile(profile: Path) -> dict[str, Any]:
    account_path = profile / "account.json"
    patterns_path = profile / "content-patterns.md"
    if not account_path.is_file() or not patterns_path.is_file():
        raise ValueError("A standard long-term account profile is required")
    account = _read_json(account_path)
    if not isinstance(account, dict) or account.get("schema_version") != "1.0":
        raise ValueError("Unsupported account profile")
    if str(account.get("mode", "")).lower() in {"temporary", "fast"}:
        raise ValueError("Temporary profiles cannot learn account-level style")
    return account


def _normalize_rules(rules: list[dict[str, str]]) -> list[dict[str, str]]:
    if not isinstance(rules, list) or not rules:
        raise ValueError("At least one confirmed rule is required")
    normalized = []
    seen = set()
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict) or set(rule) != {
            "key",
            "type",
            "instruction",
        }:
            raise ValueError(f"Rule {index} must contain only key, type, instruction")
        key = rule["key"]
        rule_type = rule["type"]
        instruction = rule["instruction"]
        if not isinstance(key, str) or not RULE_KEY_RE.fullmatch(key):
            raise ValueError(f"Rule {index} has an invalid key")
        if key in seen:
            raise ValueError(f"Rule key is duplicated: {key}")
        if rule_type not in RULE_TYPES:
            raise ValueError(f"Rule {key} has an invalid type")
        if not isinstance(instruction, str) or not instruction.strip():
            raise ValueError(f"Rule {key} needs an instruction")
        instruction = instruction.strip()
        if MACHINE_PATH_RE.search(instruction):
            raise ValueError(f"Rule {key} contains a machine path")
        if "\ufffd" in instruction or re.fullmatch(r"[?？\s]+", instruction):
            raise ValueError(f"Rule {key} contains corrupted text")
        if "\n" in instruction or len(instruction) > 240:
            raise ValueError(f"Rule {key} must be a compact single-line instruction")
        seen.add(key)
        normalized.append(
            {"key": key, "type": rule_type, "instruction": instruction}
        )
    return normalized


def _load_index(profile: Path) -> dict[str, Any]:
    index_path = profile / "history" / "edits" / "index.json"
    if not index_path.exists():
        return {"schema_version": SCHEMA_VERSION, "items": []}
    index = _read_json(index_path)
    if (
        not isinstance(index, dict)
        or index.get("schema_version") != SCHEMA_VERSION
        or not isinstance(index.get("items"), list)
    ):
        raise ValueError("Invalid style-learning index")
    return index


def _lesson_path(profile: Path, source_ref: str) -> Path:
    reference = PurePosixPath(source_ref)
    if (
        reference.is_absolute()
        or ".." in reference.parts
        or not source_ref.startswith("history/edits/")
    ):
        raise ValueError("Invalid lesson source reference")
    return profile.joinpath(*reference.parts)


def aggregate_rules(
    profile: str | Path,
    as_of: date | None = None,
) -> list[dict[str, Any]]:
    profile_path = Path(profile).expanduser().resolve()
    _validate_profile(profile_path)
    index = _load_index(profile_path)
    target_date = as_of or datetime.now(timezone.utc).date()
    grouped: dict[str, dict[str, Any]] = {}

    for item in index["items"]:
        lesson = _read_json(_lesson_path(profile_path, item["source_ref"]))
        observed = datetime.fromisoformat(lesson["created_at"]).date()
        for rule in lesson["rules"]:
            current = grouped.get(rule["key"])
            if current is None:
                current = {
                    "key": rule["key"],
                    "type": rule["type"],
                    "instruction": rule["instruction"],
                    "occurrences": 0,
                    "first_seen": observed,
                    "last_seen": observed,
                    "source_refs": [],
                }
                grouped[rule["key"]] = current
            current["occurrences"] += 1
            current["first_seen"] = min(current["first_seen"], observed)
            if observed >= current["last_seen"]:
                current["last_seen"] = observed
                current["type"] = rule["type"]
                current["instruction"] = rule["instruction"]
            current["source_refs"].append(item["source_ref"])

    result = []
    for current in grouped.values():
        age_days = max(0, (target_date - current["last_seen"]).days)
        confidence = max(0, min(10, current["occurrences"] * 2 - age_days // 90))
        result.append(
            {
                "key": current["key"],
                "type": current["type"],
                "instruction": current["instruction"],
                "occurrences": current["occurrences"],
                "confidence": confidence,
                "status": "validated" if confidence >= 6 else "provisional",
                "first_seen": current["first_seen"].isoformat(),
                "last_seen": current["last_seen"].isoformat(),
                "source_refs": current["source_refs"],
            }
        )
    return sorted(result, key=lambda rule: (-rule["confidence"], rule["key"]))


def _render_rule(rule: dict[str, Any]) -> str:
    return (
        f"- **{rule['key']}**（{rule['type']}，"
        f"置信度 {rule['confidence']}，确认 {rule['occurrences']} 次）："
        f"{rule['instruction']}"
    )


def _replace_block(text: str, start: str, end: str, lines: list[str]) -> str:
    body = "\n".join(lines) if lines else "- 暂无"
    replacement = f"{start}\n{body}\n{end}"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return text.rstrip() + f"\n\n{replacement}\n"


def _update_patterns(profile: Path, rules: list[dict[str, Any]]) -> None:
    path = profile / "content-patterns.md"
    text = path.read_text(encoding="utf-8-sig")
    validated = [_render_rule(rule) for rule in rules if rule["status"] == "validated"]
    provisional = [
        _render_rule(rule) for rule in rules if rule["status"] == "provisional"
    ]
    text = _replace_block(text, VALIDATED_START, VALIDATED_END, validated)
    text = _replace_block(
        text,
        PROVISIONAL_START,
        PROVISIONAL_END,
        provisional,
    )
    _atomic_write_text(path, text.rstrip() + "\n")


def _load_observation_index(profile: Path) -> dict[str, Any]:
    index_path = profile / "history" / "voice-observations" / "index.json"
    if not index_path.exists():
        return {"schema_version": OBSERVATION_SCHEMA_VERSION, "items": []}
    index = _read_json(index_path)
    if (
        not isinstance(index, dict)
        or index.get("schema_version") != OBSERVATION_SCHEMA_VERSION
        or not isinstance(index.get("items"), list)
    ):
        raise ValueError("Invalid voice-observation index")
    return index


def _observation_path(profile: Path, source_ref: str) -> Path:
    reference = PurePosixPath(source_ref)
    if (
        reference.is_absolute()
        or ".." in reference.parts
        or not source_ref.startswith(OBSERVATION_PREFIX)
    ):
        raise ValueError("Invalid voice-observation source reference")
    return profile.joinpath(*reference.parts)


def aggregate_observations(
    profile: str | Path,
    as_of: date | None = None,
) -> list[dict[str, Any]]:
    profile_path = Path(profile).expanduser().resolve()
    _validate_profile(profile_path)
    index = _load_observation_index(profile_path)
    target_date = as_of or datetime.now(timezone.utc).date()
    grouped: dict[str, dict[str, Any]] = {}

    for item in index["items"]:
        lesson = _read_json(_observation_path(profile_path, item["source_ref"]))
        observed = datetime.fromisoformat(lesson["created_at"]).date()
        for rule in lesson["rules"]:
            current = grouped.get(rule["key"])
            if current is None:
                current = {
                    "key": rule["key"],
                    "type": rule["type"],
                    "instruction": rule["instruction"],
                    "occurrences": 0,
                    "article_ids": set(),
                    "first_seen": observed,
                    "last_seen": observed,
                    "source_refs": [],
                }
                grouped[rule["key"]] = current
            current["occurrences"] += 1
            current["article_ids"].add(lesson["article_id"])
            current["first_seen"] = min(current["first_seen"], observed)
            if observed >= current["last_seen"]:
                current["last_seen"] = observed
                current["type"] = rule["type"]
                current["instruction"] = rule["instruction"]
            current["source_refs"].append(item["source_ref"])

    result = []
    for current in grouped.values():
        age_days = max(0, (target_date - current["last_seen"]).days)
        article_count = len(current["article_ids"])
        result.append(
            {
                "key": current["key"],
                "type": current["type"],
                "instruction": current["instruction"],
                "occurrences": current["occurrences"],
                "article_count": article_count,
                "status": "candidate" if article_count >= 3 else "observed",
                "first_seen": current["first_seen"].isoformat(),
                "last_seen": current["last_seen"].isoformat(),
                "stale": age_days >= 180,
                "source_refs": current["source_refs"],
            }
        )
    return sorted(result, key=lambda rule: (-rule["article_count"], -rule["occurrences"], rule["key"]))


def observe_final(
    profile: str | Path,
    final: str | Path,
    article_id: str,
    rules: list[dict[str, str]],
    timestamp: datetime | None = None,
) -> dict[str, Any]:
    """Record final-only style observations without promoting them to hard rules."""
    profile_path = Path(profile).expanduser().resolve()
    final_path = Path(final).expanduser().resolve()
    _validate_profile(profile_path)
    if not final_path.is_file():
        raise FileNotFoundError("The final file is required")
    if not isinstance(article_id, str) or not article_id.strip():
        raise ValueError("article_id is required")

    normalized_rules = _normalize_rules(rules)
    final_hash = _sha256(final_path)
    observed = _normalize_timestamp(timestamp)
    index = _load_observation_index(profile_path)
    for item in index["items"]:
        if item.get("article_id") == article_id.strip() and item.get("final_sha256") == final_hash:
            return {
                "status": "already_observed",
                "source_ref": item["source_ref"],
                "observations": aggregate_observations(profile_path, as_of=observed.date()),
            }

    stamp = observed.strftime("%Y%m%d")
    filename = f"{stamp}-{_portable_slug(article_id)}-{final_hash[:8]}.json"
    source_ref = f"{OBSERVATION_PREFIX}{filename}"
    created_at = observed.isoformat(timespec="seconds")
    lesson = {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "article_id": article_id.strip(),
        "final_sha256": final_hash,
        "created_at": created_at,
        "rules": normalized_rules,
    }
    index_item = {
        "source_ref": source_ref,
        "article_id": lesson["article_id"],
        "final_sha256": final_hash,
        "created_at": created_at,
    }
    _atomic_write_json(_observation_path(profile_path, source_ref), lesson)
    index["items"].append(index_item)
    _atomic_write_json(
        profile_path / "history" / "voice-observations" / "index.json", index
    )
    return {
        "status": "observed",
        "source_ref": source_ref,
        "observations": aggregate_observations(profile_path, as_of=observed.date()),
    }


def record_lesson(
    profile: str | Path,
    draft: str | Path,
    final: str | Path,
    article_id: str,
    rules: list[dict[str, str]],
    approved: bool,
    timestamp: datetime | None = None,
) -> dict[str, Any]:
    if not approved:
        raise PermissionError("Explicit approval is required")

    profile_path = Path(profile).expanduser().resolve()
    draft_path = Path(draft).expanduser().resolve()
    final_path = Path(final).expanduser().resolve()
    _validate_profile(profile_path)
    if not draft_path.is_file() or not final_path.is_file():
        raise FileNotFoundError("Both draft and final files are required")
    if not isinstance(article_id, str) or not article_id.strip():
        raise ValueError("article_id is required")

    normalized_rules = _normalize_rules(rules)
    draft_hash = _sha256(draft_path)
    final_hash = _sha256(final_path)
    if draft_hash == final_hash:
        raise ValueError("Draft and final must contain different content")

    observed = _normalize_timestamp(timestamp)
    index = _load_index(profile_path)
    for item in index["items"]:
        if (
            item.get("draft_sha256") == draft_hash
            and item.get("final_sha256") == final_hash
        ):
            return {
                "status": "already_recorded",
                "source_ref": item["source_ref"],
                "rules": aggregate_rules(profile_path, as_of=observed.date()),
            }

    stamp = observed.strftime("%Y%m%d")
    filename = (
        f"{stamp}-{_portable_slug(article_id)}-"
        f"{draft_hash[:8]}-{final_hash[:8]}.json"
    )
    source_ref = f"history/edits/{filename}"
    created_at = observed.isoformat(timespec="seconds")
    lesson = {
        "schema_version": SCHEMA_VERSION,
        "article_id": article_id.strip(),
        "draft_sha256": draft_hash,
        "final_sha256": final_hash,
        "created_at": created_at,
        "rules": normalized_rules,
    }
    index_item = {
        "source_ref": source_ref,
        "article_id": lesson["article_id"],
        "draft_sha256": draft_hash,
        "final_sha256": final_hash,
        "created_at": created_at,
    }

    lesson_path = _lesson_path(profile_path, source_ref)
    index_path = profile_path / "history" / "edits" / "index.json"
    _atomic_write_json(lesson_path, lesson)
    index["items"].append(index_item)
    _atomic_write_json(index_path, index)
    aggregated = aggregate_rules(profile_path, as_of=observed.date())
    _update_patterns(profile_path, aggregated)
    return {
        "status": "recorded",
        "source_ref": source_ref,
        "rules": aggregated,
    }


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    record = subparsers.add_parser("record")
    record.add_argument("--profile", required=True, type=Path)
    record.add_argument("--draft", required=True, type=Path)
    record.add_argument("--final", required=True, type=Path)
    record.add_argument("--article-id", required=True)
    record.add_argument("--rules", required=True, type=Path)
    record.add_argument("--approved", action="store_true")

    aggregate = subparsers.add_parser("aggregate")
    aggregate.add_argument("--profile", required=True, type=Path)
    aggregate.add_argument("--as-of", type=date.fromisoformat)

    observe = subparsers.add_parser(
        "observe-final",
        help="Record style observations from one approved final without promotion",
    )
    observe.add_argument("--profile", required=True, type=Path)
    observe.add_argument("--final", required=True, type=Path)
    observe.add_argument("--article-id", required=True)
    observe.add_argument("--rules", required=True, type=Path)
    observe.add_argument("--timestamp", type=datetime.fromisoformat)

    observations = subparsers.add_parser(
        "aggregate-observations",
        help="Read final-only observations and candidate status",
    )
    observations.add_argument("--profile", required=True, type=Path)
    observations.add_argument("--as-of", type=date.fromisoformat)

    args = parser.parse_args(argv)
    if args.command == "record":
        payload = record_lesson(
            args.profile,
            args.draft,
            args.final,
            args.article_id,
            _read_json(args.rules),
            approved=args.approved,
        )
    elif args.command == "aggregate":
        payload = {
            "status": "ok",
            "rules": aggregate_rules(args.profile, as_of=args.as_of),
        }
    elif args.command == "observe-final":
        payload = observe_final(
            args.profile,
            args.final,
            args.article_id,
            _read_json(args.rules),
            timestamp=args.timestamp,
        )
    else:
        payload = {
            "status": "ok",
            "observations": aggregate_observations(
                args.profile, as_of=args.as_of
            ),
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
