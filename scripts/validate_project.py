"""Unified project validation CLI.

Stable cross-skill interface: only ``validate_project.py profile <账号目录>``
is promised to companion skills; its JSON output shape
``{"ok": bool, "errors": [...]}`` and exit codes (0 pass / 1 fail) are
stable. The ``article`` subcommand and all module-level symbols below are
internal to this Skill and may change.

Implementation lives in single-responsibility modules:

- ``project_checks``          shared JSON/path helpers
- ``security_scan``           secret-like key and absolute-path scanning
- ``validate_profile``        account profile packages and learning ledger
- ``validate_article``        article-state.json, artifacts and approvals
- ``validate_html_delivery``  HTML five-file delivery gate
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from article_state import ALLOWED_STATUS, STAGES, file_hash

from project_checks import (
    SHA256_RE,
    URI_SCHEME,
    WINDOWS_DRIVE_REFERENCE,
    WINDOWS_UNC,
    _is_logical_identifier,
    _is_machine_absolute_path,
    _is_portable_relative_path,
    _load_json,
    _walk,
)
from security_scan import (
    FORBIDDEN_KEY_PARTS,
    NORMALIZED_FORBIDDEN_KEY_PARTS,
    _json_safety_errors,
)
from validate_article import ARTICLE_REQUIRED_KEYS, validate_article_project
from validate_html_delivery import (
    HTML_AUTHOR_PLACEHOLDER_RE,
    HTML_DEFAULT_CTA_MARKERS,
    HTML_DELIVERY_FILES,
    HTML_MINIMUM_MARKERS,
    HTML_QC_AUTHOR_CTA_RE,
    HTML_QC_HEADING_RE,
    HTML_QC_VERIFICATION_RE,
    check_html_delivery,
)
from validate_profile import (
    GITIGNORE_ENCODING_ERROR,
    GITIGNORE_GIT_ERROR,
    GITIGNORE_NOT_IGNORED_ERROR,
    LEARNING_RULE_KEY_RE,
    LEARNING_RULE_TYPES,
    PROFILE_DOCS,
    PROFILE_REQUIRED_KEYS,
    _gitignore_ignores_root_file,
    _validate_learning_ledger,
    validate_profile,
)

__all__ = [
    "ALLOWED_STATUS",
    "STAGES",
    "file_hash",
    "SHA256_RE",
    "URI_SCHEME",
    "WINDOWS_DRIVE_REFERENCE",
    "WINDOWS_UNC",
    "_is_logical_identifier",
    "_is_machine_absolute_path",
    "_is_portable_relative_path",
    "_load_json",
    "_walk",
    "FORBIDDEN_KEY_PARTS",
    "NORMALIZED_FORBIDDEN_KEY_PARTS",
    "_json_safety_errors",
    "ARTICLE_REQUIRED_KEYS",
    "validate_article_project",
    "HTML_AUTHOR_PLACEHOLDER_RE",
    "HTML_DEFAULT_CTA_MARKERS",
    "HTML_DELIVERY_FILES",
    "HTML_MINIMUM_MARKERS",
    "HTML_QC_AUTHOR_CTA_RE",
    "HTML_QC_HEADING_RE",
    "HTML_QC_VERIFICATION_RE",
    "check_html_delivery",
    "GITIGNORE_ENCODING_ERROR",
    "GITIGNORE_GIT_ERROR",
    "GITIGNORE_NOT_IGNORED_ERROR",
    "LEARNING_RULE_KEY_RE",
    "LEARNING_RULE_TYPES",
    "PROFILE_DOCS",
    "PROFILE_REQUIRED_KEYS",
    "_gitignore_ignores_root_file",
    "_validate_learning_ledger",
    "validate_profile",
    "main",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("profile", "article"))
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    errors = (
        validate_profile(args.path)
        if args.kind == "profile"
        else validate_article_project(args.path)
    )
    print(
        json.dumps(
            {"ok": not errors, "errors": errors},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
