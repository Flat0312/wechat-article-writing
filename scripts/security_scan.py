"""Secret-like key and machine-path scanning for project JSON payloads.

Only consumed by sibling validation modules inside ``scripts/``; not a
stable cross-skill interface.
"""

from __future__ import annotations

import re
from typing import Any

from project_checks import _is_machine_absolute_path, _walk


FORBIDDEN_KEY_PARTS = (
    "secret",
    "token",
    "cookie",
    "password",
    "credential",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "authorization",
    "bearer",
    "appkey",
    "app_key",
    "appsecret",
    "app_secret",
)
NORMALIZED_FORBIDDEN_KEY_PARTS = tuple(
    re.sub(r"[^a-z0-9]", "", part.lower()) for part in FORBIDDEN_KEY_PARTS
)


def _json_safety_errors(
    payload: Any, allow_absolute_paths: bool = False
) -> list[str]:
    errors = []
    for location, key, value in _walk(payload):
        lowered = (
            re.sub(r"[^a-z0-9]", "", key.lower())
            if key is not None
            else ""
        )
        if key is not None and any(
            part in lowered for part in NORMALIZED_FORBIDDEN_KEY_PARTS
        ):
            errors.append(f"{location}: secret-like key is not allowed")
        if (
            not allow_absolute_paths
            and key is not None
            and _is_machine_absolute_path(key)
        ):
            errors.append(f"{location}: absolute path key is not allowed")
        if (
            not allow_absolute_paths
            and isinstance(value, str)
            and _is_machine_absolute_path(value)
        ):
            errors.append(f"{location}: absolute path is not allowed")
    return errors
