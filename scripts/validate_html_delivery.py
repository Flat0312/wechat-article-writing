"""HTML five-file delivery gate for article projects.

Extracted from the monolithic validator; invoked by ``validate_article``
once the article state shows HTML work has started. Not a stable
cross-skill interface on its own.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
import re
from typing import Any

from article_state import STAGES


HTML_DELIVERY_FILES = (
    "output/article.html",
    "output/article-preview.html",
    "output/article-copy.html",
    "output/article-copy-preview.html",
    "output/html-qc.md",
)
HTML_MINIMUM_MARKERS = {
    "output/article.html": ("<section", "</section>"),
    "output/article-copy-preview.html": (
        "<html",
        'id="gzh-content"',
        "gzhCopyBtn",
        "</body>",
    ),
}
HTML_QC_HEADING_RE = re.compile(r"(?m)^\s*#{1,6}\s+\S")
HTML_QC_VERIFICATION_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?.*(?:validate_project|验证|校验|validation).*$"
)
HTML_QC_AUTHOR_CTA_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?author_cta\s*:\s*(disabled|explicit)\s*$"
)
HTML_AUTHOR_PLACEHOLDER_RE = re.compile(r"\{\{\s*(?:作者名|简介)\s*\}\}")
HTML_DEFAULT_CTA_MARKERS = (
    "点赞、在看、转发",
    "如果你觉得今天这篇有收获",
)


def check_html_delivery(root: Path, state: dict[str, Any]) -> list[str]:
    root = Path(root)
    errors = []
    status = state.get("stage_status", {})
    html_status = status.get("html") if isinstance(status, dict) else None
    current_stage = state.get("current_stage")
    html_stage_reached = (
        current_stage in STAGES
        and STAGES.index(current_stage) >= STAGES.index("html")
    )
    artifacts = state.get("artifacts", {})
    html_work_started = (
        html_stage_reached
        or html_status
        in {"in_progress", "awaiting_confirmation", "failed", "stale"}
        or (isinstance(artifacts, dict) and "html" in artifacts)
    )
    if html_status != "completed" and html_work_started:
        html_contents: dict[str, str] = {}
        for relative in HTML_DELIVERY_FILES:
            target = root.joinpath(*PurePosixPath(relative).parts)
            if not target.is_file():
                errors.append(
                    f"{relative}: missing required HTML delivery file"
                )
                continue
            try:
                content = target.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                errors.append(f"{relative}: must be valid UTF-8 text")
                continue
            if not content.strip():
                errors.append(
                    f"{relative}: required HTML delivery file must be non-empty"
                )
                continue
            html_contents[relative] = content
        for relative, markers in HTML_MINIMUM_MARKERS.items():
            content = html_contents.get(relative)
            if content is None:
                continue
            lowered = content.lower()
            for marker in markers:
                if marker.lower() not in lowered:
                    errors.append(
                        f"{relative}: missing required marker {marker}"
                    )
        qc_content = html_contents.get("output/html-qc.md")
        if qc_content is not None:
            if not HTML_QC_HEADING_RE.search(qc_content):
                errors.append(
                    "output/html-qc.md: must contain a Markdown heading"
                )
            if "output/article.html" not in qc_content:
                errors.append(
                    "output/html-qc.md: must reference output/article.html"
                )
            if not HTML_QC_VERIFICATION_RE.search(qc_content):
                errors.append(
                    "output/html-qc.md: must contain a validation record"
                )
            cta_match = HTML_QC_AUTHOR_CTA_RE.search(qc_content)
            if cta_match is None:
                errors.append(
                    "output/html-qc.md: must record author_cta: disabled or author_cta: explicit"
                )
            elif cta_match.group(1) == "disabled":
                for relative in (
                    "output/article.html",
                    "output/article-copy.html",
                ):
                    content = html_contents.get(relative, "")
                    if HTML_AUTHOR_PLACEHOLDER_RE.search(content):
                        errors.append(
                            f"{relative}: author placeholders are forbidden when author_cta is disabled"
                        )
                    if any(marker in content for marker in HTML_DEFAULT_CTA_MARKERS):
                        errors.append(
                            f"{relative}: gzh-design default author CTA is forbidden when author_cta is disabled"
                        )
    return errors
