from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from hashlib import sha256
from pathlib import Path, PurePosixPath, PureWindowsPath

import article_state


SCHEMA_VERSION = "1.0"
PUBLISH_REFERENCE = "publish-reference.json"
METRICS_PATH = "metrics.json"


class PublishError(ValueError):
    """Raised when a public WeChat record cannot be safely registered."""


def _load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as error:
        raise PublishError(f"missing JSON file: {path}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PublishError(f"invalid JSON file: {path}") from error
    if not isinstance(value, dict):
        raise PublishError(f"JSON root must be an object: {path}")
    return value


def _json_bytes(value: dict[str, object]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _write_json(path: Path, value: dict[str, object]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(_json_bytes(value))
    temporary.replace(path)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _portable_relative(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise PublishError("prediction path must be a non-empty relative path")
    windows = PureWindowsPath(value)
    portable = PurePosixPath(value.replace("\\", "/"))
    if windows.anchor or portable.is_absolute() or ".." in portable.parts:
        raise PublishError("prediction path must be portable and relative")
    return portable.as_posix()


def _resolve_under(root: Path, relative: str) -> Path:
    root = root.resolve()
    target = (root / Path(*PurePosixPath(relative).parts)).resolve()
    try:
        target.relative_to(root)
    except ValueError as error:
        raise PublishError("prediction path escapes the Cheat project") from error
    return target


def _timestamp(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise PublishError(f"{field} must be an ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise PublishError(f"{field} must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None:
        raise PublishError(f"{field} must include a timezone")
    return value


def _public_wechat_url(value: object) -> str:
    if not isinstance(value, str) or not value.startswith("https://mp.weixin.qq.com/s/"):
        raise PublishError("public_url must be an HTTPS mp.weixin.qq.com article URL")
    return value


def _article_dir(project: Path) -> str:
    parts = project.resolve().parts
    for index, part in enumerate(parts):
        if part.lower() == "articles" and index + 1 < len(parts):
            return PurePosixPath(*parts[index:]).as_posix()
    return project.name


def _prediction_info(cheat_project: Path, cheat_receipt: dict[str, object]) -> tuple[str, str, str]:
    if cheat_receipt.get("status") != "published":
        raise PublishError("Cheat publish receipt must have status=published")
    if cheat_receipt.get("platform") != "wechat":
        raise PublishError("Cheat publish receipt must have platform=wechat")
    path = _portable_relative(
        cheat_receipt.get("prediction_file", cheat_receipt.get("prediction_path"))
    )
    if not path.startswith("predictions/"):
        raise PublishError("Cheat prediction file must be under predictions/")
    prediction = _resolve_under(cheat_project, path)
    if not prediction.is_file():
        raise PublishError(f"Cheat prediction file is missing: {path}")
    actual_hash = _sha256(prediction)
    expected_hash = cheat_receipt.get("prediction_sha256")
    if not isinstance(expected_hash, str) or expected_hash != actual_hash:
        raise PublishError("Cheat prediction SHA256 does not match the file")
    cheat_published_at = _timestamp(
        cheat_receipt.get("published_at"), "Cheat published_at"
    )
    return path, actual_hash, cheat_published_at


def _compatible_existing(
    path: Path, value: dict[str, object], immutable_fields: tuple[str, ...]
) -> dict[str, object]:
    if not path.is_file():
        return value
    existing = _load_json(path)
    for field in immutable_fields:
        if field in existing and existing.get(field) != value.get(field):
            raise PublishError(f"{path.name} already records a different {field}")
    return existing


def record_wechat_publish(
    project: Path,
    cheat_project: Path,
    cheat_receipt: dict[str, object],
    public_url: str,
    published_at: str,
    user_confirmed: bool,
) -> dict[str, object]:
    article_project = Path(project).expanduser().resolve()
    cheat_root = Path(cheat_project).expanduser().resolve()
    if not cheat_root.is_dir():
        raise PublishError(f"Cheat project does not exist: {cheat_root}")
    state_path = article_project / "article-state.json"
    state = _load_json(state_path)
    statuses = state.get("stage_status")
    if not isinstance(statuses, dict) or statuses.get("html") != "completed":
        raise PublishError("HTML must be completed before public publication")
    if "html" in (state.get("stale_artifacts") or []):
        raise PublishError("HTML is stale; rebuild and approve it before publication")
    if not user_confirmed:
        raise PublishError("explicit user confirmation is required for public publication")

    public_url = _public_wechat_url(public_url)
    published_at = _timestamp(published_at, "published_at")
    prediction_path, prediction_hash, cheat_published_at = _prediction_info(
        cheat_root, cheat_receipt
    )
    article_dir = _article_dir(article_project)
    publish_path = article_project / "publish.json"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "publicly_published",
        "platform": "wechat",
        "article_dir": article_dir,
        "public_url": public_url,
        "published_at": published_at,
        "cheat_prediction_file": prediction_path,
        "cheat_prediction_sha256": prediction_hash,
        "cheat_published_at": cheat_published_at,
        "metrics_path": METRICS_PATH,
    }
    existing_publish = _compatible_existing(
        publish_path,
        payload,
        ("public_url", "published_at", "cheat_prediction_file", "cheat_prediction_sha256"),
    )
    if existing_publish:
        if existing_publish.get("status") not in (None, "html_ready", "publicly_published"):
            raise PublishError("publish.json has an unsupported status")
        payload = {**existing_publish, **payload}

    publish_bytes = _json_bytes(payload)
    publish_hash = sha256(publish_bytes).hexdigest()
    reference_payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "publicly_published",
        "platform": "wechat",
        "article_dir": article_dir,
        "publish_json_path": "publish.json",
        "publish_json_sha256": publish_hash,
        "public_url": public_url,
        "cheat_prediction_file": prediction_path,
        "cheat_prediction_sha256": prediction_hash,
        "published_at": published_at,
        "cheat_published_at": cheat_published_at,
        "metrics_path": METRICS_PATH,
    }
    reference_path = article_project / PUBLISH_REFERENCE
    _compatible_existing(
        reference_path,
        reference_payload,
        ("publish_json_sha256", "public_url", "cheat_prediction_file"),
    )

    _write_json(publish_path, payload)
    _write_json(reference_path, reference_payload)
    article_state.record_artifact(state, article_project, "publish", Path("publish.json"))
    return reference_payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Register a successful WeChat Cheat publication")
    parser.add_argument("project", type=Path)
    parser.add_argument("--cheat-project", type=Path, required=True)
    parser.add_argument("--cheat-receipt", type=Path, required=True)
    parser.add_argument("--public-url", required=True)
    parser.add_argument("--published-at", required=True)
    parser.add_argument("--confirmed", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = record_wechat_publish(
            args.project,
            args.cheat_project,
            _load_json(args.cheat_receipt),
            args.public_url,
            args.published_at,
            args.confirmed,
        )
    except (OSError, PublishError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
