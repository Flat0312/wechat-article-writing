from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import sys
import tempfile
from math import gcd

from article_state import file_hash


MANIFEST_PATH = PurePosixPath("visuals/assets/manifest.json")
COVER_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
FORBIDDEN_COVER_PARTS = (
    "square",
    "1x1",
    "pair",
    "carousel",
    "live-photo",
    "livephoto",
    ".pvt",
    ".mov",
    ".mp4",
)
ANCHOR_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


class VisualAssetError(RuntimeError):
    pass


def _project_root(project: Path) -> Path:
    try:
        root = Path(project).expanduser().resolve(strict=True)
    except FileNotFoundError as error:
        raise VisualAssetError(f"article project does not exist: {project}") from error
    if not root.is_dir():
        raise VisualAssetError(f"article project is not a directory: {project}")
    return root


def _article_id(project: Path) -> str:
    state_path = project / "article-state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise VisualAssetError(f"cannot read article-state.json: {error}") from error
    article_id = state.get("article_id") if isinstance(state, dict) else None
    if not isinstance(article_id, str) or not article_id:
        raise VisualAssetError("article-state.json article_id is required")
    return article_id


def _resolve_source(path: Path) -> Path:
    try:
        resolved = Path(path).expanduser().resolve(strict=True)
    except FileNotFoundError as error:
        raise VisualAssetError(f"source file does not exist: {path}") from error
    if not resolved.is_file():
        raise VisualAssetError(f"source is not a file: {path}")
    return resolved


def _resolve_directory(path: Path) -> Path:
    try:
        resolved = Path(path).expanduser().resolve(strict=True)
    except FileNotFoundError as error:
        raise VisualAssetError(f"route output directory does not exist: {path}") from error
    if not resolved.is_dir():
        raise VisualAssetError(f"route output is not a directory: {path}")
    return resolved


def _read_png_size(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 24:
        return None
    if data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def _read_gif_size(data: bytes) -> tuple[int, int] | None:
    if not data.startswith((b"GIF87a", b"GIF89a")) or len(data) < 10:
        return None
    return struct.unpack("<HH", data[6:10])


def _read_webp_size(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"RIFF") or len(data) < 30 or data[8:12] != b"WEBP":
        return None
    if data[12:16] != b"VP8X":
        return None
    width = 1 + int.from_bytes(data[24:27], "little")
    height = 1 + int.from_bytes(data[27:30], "little")
    return width, height


def _read_jpeg_size(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    sof_markers = set(range(0xC0, 0xC4)) | set(range(0xC5, 0xC8))
    sof_markers |= set(range(0xC9, 0xCC)) | set(range(0xCD, 0xD0))
    index = 2
    while index + 1 < len(data):
        while index < len(data) and data[index] != 0xFF:
            index += 1
        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            break
        marker = data[index]
        index += 1
        if marker in (0xD8, 0xD9):
            continue
        if index + 1 >= len(data):
            break
        segment_length = int.from_bytes(data[index : index + 2], "big")
        if segment_length < 2 or index + segment_length > len(data):
            break
        if marker in sof_markers and segment_length >= 7:
            height = int.from_bytes(data[index + 3 : index + 5], "big")
            width = int.from_bytes(data[index + 5 : index + 7], "big")
            return width, height
        index += segment_length
    return None


def _image_size(path: Path) -> tuple[int, int]:
    suffix = path.suffix.lower()
    if suffix not in COVER_IMAGE_SUFFIXES:
        raise VisualAssetError(
            f"unsupported visual asset format: {path.name}; "
            f"expected one of {sorted(COVER_IMAGE_SUFFIXES)}"
        )
    try:
        data = path.read_bytes()
    except OSError as error:
        raise VisualAssetError(f"cannot read visual asset: {path}") from error
    size = (
        _read_png_size(data)
        or _read_gif_size(data)
        or _read_webp_size(data)
        or _read_jpeg_size(data)
    )
    if size is None or size[0] <= 0 or size[1] <= 0:
        raise VisualAssetError(f"cannot determine image dimensions: {path.name}")
    return size


def _aspect_ratio(width: int, height: int) -> str:
    divisor = gcd(width, height)
    return f"{width // divisor}:{height // divisor}"


def _relative_path(path: Path, root: Path, label: str) -> str:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError) as error:
        raise VisualAssetError(f"{label} must be inside the route output directory") from error
    return PurePosixPath(*relative.parts).as_posix()


def _safe_destination(project: Path, relative: PurePosixPath) -> Path:
    target = project / Path(*relative.parts)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.parent.resolve(strict=True).relative_to(project.resolve())
    except (OSError, RuntimeError, ValueError) as error:
        raise VisualAssetError(f"delivery path escapes article project: {relative}") from error
    if target.is_symlink():
        raise VisualAssetError(f"delivery path must not be a symbolic link: {relative}")
    if target.exists() and not target.is_file():
        raise VisualAssetError(f"delivery path is not a file: {relative}")
    return target


def _atomic_write(path: Path, data: bytes) -> None:
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


def _load_manifest(project: Path, article_id: str) -> dict[str, object]:
    manifest_path = _safe_destination(project, MANIFEST_PATH)
    if not manifest_path.exists():
        return {
            "schema_version": "1.0",
            "article_id": article_id,
            "cover": None,
            "body": [],
        }
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise VisualAssetError(f"cannot read visual manifest: {error}") from error
    if not isinstance(manifest, dict):
        raise VisualAssetError("visual manifest must contain a JSON object")
    if set(manifest) != {"schema_version", "article_id", "cover", "body"}:
        raise VisualAssetError("visual manifest has an unsupported schema")
    if manifest.get("schema_version") != "1.0" or manifest.get("article_id") != article_id:
        raise VisualAssetError("visual manifest schema or article_id is invalid")
    if manifest.get("cover") is not None and not isinstance(manifest["cover"], dict):
        raise VisualAssetError("visual manifest cover must be an object or null")
    if not isinstance(manifest.get("body"), list):
        raise VisualAssetError("visual manifest body must be an array")
    return manifest


def _write_manifest(project: Path, manifest: dict[str, object]) -> None:
    path = _safe_destination(project, MANIFEST_PATH)
    payload = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    try:
        _atomic_write(path, payload)
    except OSError as error:
        raise VisualAssetError(f"cannot write visual manifest: {error}") from error


def _copy_asset(source: Path, project: Path, relative: PurePosixPath) -> str:
    destination = _safe_destination(project, relative)
    try:
        _atomic_write(destination, source.read_bytes())
    except OSError as error:
        raise VisualAssetError(f"cannot copy visual asset to {relative}: {error}") from error
    return file_hash(destination)


def _validate_cover_route_output(source: Path, route_output_dir: Path) -> str:
    source_relative = _relative_path(source, route_output_dir, "cover source")
    files = [path for path in route_output_dir.rglob("*") if path.is_file()]
    for path in files:
        relative = path.relative_to(route_output_dir).as_posix().lower()
        if any(part in relative for part in FORBIDDEN_COVER_PARTS):
            raise VisualAssetError(
                "cover route produced a forbidden square/pair/Live Photo artifact: "
                f"{path.name}"
            )
    image_files = [path for path in files if path.suffix.lower() in COVER_IMAGE_SUFFIXES]
    if len(image_files) != 1:
        raise VisualAssetError(
            "cover route must expose exactly one static image; "
            f"found {len(image_files)}"
        )
    if image_files[0].resolve() != source.resolve():
        raise VisualAssetError("cover source is not the only static image in route output")
    return source_relative


def _cover_record(
    source: Path,
    route: str,
    source_relative: str,
    delivery_path: PurePosixPath,
    dimensions: tuple[int, int],
    sha256: str,
) -> dict[str, object]:
    width, height = dimensions
    return {
        "asset_id": "wechat-cover-21x9",
        "role": "cover",
        "route": route,
        "delivery_path": delivery_path.as_posix(),
        "source_name": source.name,
        "source_relative": source_relative,
        "sha256": sha256,
        "width": width,
        "height": height,
        "aspect_ratio": "21:9",
    }


def prepare_cover(
    project: Path,
    source: Path,
    route_output_dir: Path,
    route: str = "guizang",
) -> dict[str, object]:
    if route not in {"guizang", "imagegen"}:
        raise VisualAssetError("cover route must be guizang or imagegen")
    root = _project_root(project)
    article_id = _article_id(root)
    source_file = _resolve_source(source)
    output_dir = _resolve_directory(route_output_dir)
    source_relative = _validate_cover_route_output(source_file, output_dir)
    dimensions = _image_size(source_file)
    width, height = dimensions
    if width * 9 != height * 21:
        raise VisualAssetError(
            f"cover must be exactly 21:9; received {width}x{height}"
        )
    delivery_path = PurePosixPath(
        "visuals/assets/cover" + source_file.suffix.lower()
    )
    manifest = _load_manifest(root, article_id)
    digest = file_hash(source_file)
    previous = manifest.get("cover")
    if isinstance(previous, dict) and previous.get("sha256") != digest:
        raise VisualAssetError(
            "visual manifest already contains a different cover; use a new article project"
        )
    _copy_asset(source_file, root, delivery_path)
    record = _cover_record(
        source_file, route, source_relative, delivery_path, dimensions, digest
    )
    manifest["cover"] = record
    _write_manifest(root, manifest)
    return {
        "ok": True,
        "article_id": article_id,
        "manifest_path": MANIFEST_PATH.as_posix(),
        "delivery_path": delivery_path.as_posix(),
        "width": width,
        "height": height,
        "sha256": digest,
    }


def _anchor_slug(anchor_id: str) -> str:
    if not ANCHOR_ID_RE.fullmatch(anchor_id):
        raise VisualAssetError(
            "anchor_id must use 1-64 ASCII letters, numbers, '-' or '_'"
        )
    return anchor_id.lower()


def _validate_provenance(value: str | None) -> str | None:
    if value is None:
        return None
    if not value or "\\" in value:
        raise VisualAssetError("provenance_ref must be a portable reference or URL")
    if re.match(r"(?i)^https?://", value):
        return value
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise VisualAssetError("provenance_ref must be a portable reference or URL")
    return path.as_posix()


def register_body(
    project: Path,
    route: str,
    source: Path,
    anchor_id: str,
    information_job: str,
    provenance_ref: str | None = None,
) -> dict[str, object]:
    if route not in {"ian", "baoyu"}:
        raise VisualAssetError("body route must be ian or baoyu")
    if not information_job.strip():
        raise VisualAssetError("information_job is required")
    root = _project_root(project)
    article_id = _article_id(root)
    source_file = _resolve_source(source)
    dimensions = _image_size(source_file)
    slug = _anchor_slug(anchor_id)
    provenance = _validate_provenance(provenance_ref)
    delivery_path = PurePosixPath(
        "visuals/assets" / PurePosixPath(route) / PurePosixPath(
            f"{route}-{slug}{source_file.suffix.lower()}"
        )
    )
    digest = file_hash(source_file)
    manifest = _load_manifest(root, article_id)
    body = manifest["body"]
    assert isinstance(body, list)
    existing = next(
        (
            item
            for item in body
            if isinstance(item, dict) and item.get("asset_id") == f"{route}-{slug}"
        ),
        None,
    )
    if isinstance(existing, dict) and existing.get("sha256") != digest:
        raise VisualAssetError(
            f"visual manifest already contains a different asset for {route}-{slug}"
        )
    _copy_asset(source_file, root, delivery_path)
    width, height = dimensions
    record: dict[str, object] = {
        "asset_id": f"{route}-{slug}",
        "role": "body",
        "route": route,
        "anchor_id": anchor_id,
        "information_job": information_job.strip(),
        "delivery_path": delivery_path.as_posix(),
        "source_name": source_file.name,
        "sha256": digest,
        "width": width,
        "height": height,
        "aspect_ratio": _aspect_ratio(width, height),
    }
    if provenance is not None:
        record["provenance_ref"] = provenance
    if existing is None:
        body.append(record)
    else:
        body[body.index(existing)] = record
    _write_manifest(root, manifest)
    return {
        "ok": True,
        "article_id": article_id,
        "manifest_path": MANIFEST_PATH.as_posix(),
        "delivery_path": delivery_path.as_posix(),
        "sha256": digest,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    cover = subparsers.add_parser("cover")
    cover.add_argument("project", type=Path)
    cover.add_argument("--source", type=Path, required=True)
    cover.add_argument("--route-output-dir", type=Path, required=True)
    cover.add_argument("--route", choices=("guizang", "imagegen"), default="guizang")
    body = subparsers.add_parser("body")
    body.add_argument("project", type=Path)
    body.add_argument("--route", choices=("ian", "baoyu"), required=True)
    body.add_argument("--source", type=Path, required=True)
    body.add_argument("--anchor-id", required=True)
    body.add_argument("--information-job", required=True)
    body.add_argument("--provenance-ref")
    args = parser.parse_args(argv)
    try:
        if args.command == "cover":
            result = prepare_cover(
                args.project,
                args.source,
                args.route_output_dir,
                args.route,
            )
        else:
            result = register_body(
                args.project,
                args.route,
                args.source,
                args.anchor_id,
                args.information_job,
                args.provenance_ref,
            )
    except VisualAssetError as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
