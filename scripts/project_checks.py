"""Shared helpers for project validation modules.

Only consumed by sibling validation modules inside ``scripts/``; not a
stable cross-skill interface. The stable cross-skill entry point remains
``validate_project.py profile <账号目录>``.
"""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterator


WINDOWS_DRIVE_REFERENCE = re.compile(r"(?i)^[A-Z]:")
WINDOWS_UNC = re.compile(r"^(?:\\\\|//)[^\\/]+[\\/]")
URI_SCHEME = re.compile(r"(?i)^[A-Z][A-Z0-9+.-]*:")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _walk(
    value: Any, location: str = "root"
) -> Iterator[tuple[str, str | None, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            child_location = f"{location}.{key_text}"
            yield child_location, key_text, item
            yield from _walk(item, child_location)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child_location = f"{location}[{index}]"
            yield child_location, None, item
            yield from _walk(item, child_location)


def _is_machine_absolute_path(value: str) -> bool:
    candidate = value.strip()
    return bool(
        WINDOWS_DRIVE_REFERENCE.match(candidate)
        or WINDOWS_UNC.match(candidate)
        or candidate.startswith("/")
        or candidate.startswith("\\")
        or candidate.lower().startswith("file:")
    )


def _is_portable_relative_path(value: str) -> bool:
    if (
        not value
        or "\\" in value
        or WINDOWS_DRIVE_REFERENCE.match(value)
        or URI_SCHEME.match(value)
        or _is_machine_absolute_path(value)
    ):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and path.parts != ()


def _is_logical_identifier(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and value
        and value[0].isalnum()
        and value[-1].isalnum()
        and ".." not in value
        and all(
            character.isalnum() or character in "._-" for character in value
        )
    )
