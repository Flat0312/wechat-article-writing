from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import validate_project


class HtmlFiveFileContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "article"
        self.project.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def _write_state(
        self,
        *,
        current_stage: str = "html",
        html_status: str = "in_progress",
    ) -> None:
        stage_status = {
            stage: "pending" for stage in validate_project.STAGES
        }
        stage_status["html"] = html_status
        state = {
            "schema_version": "1.0",
            "article_id": "article-1",
            "mode": "full",
            "profile_ref": None,
            "cheat_binding": "primary",
            "current_stage": current_stage,
            "stage_status": stage_status,
            "artifacts": {},
            "approvals": {},
            "skill_routes": {},
            "stale_artifacts": [],
            "required_actions": [],
            "created_at": "2026-07-30T12:00:00+08:00",
            "updated_at": "2026-07-30T12:00:00+08:00",
        }
        (self.project / "article-state.json").write_text(
            json.dumps(state, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def _write_html_files(self, *, omit: str | None = None) -> None:
        payloads = {
            "output/article.html": (
                '<section><p><span leaf="">正文</span></p></section>\n'
            ),
            "output/article-preview.html": (
                '<html><body><div id="gzh-content">正文</div></body></html>\n'
            ),
            "output/article-copy.html": (
                '<section><p><span leaf="">正文</span></p></section>\n'
            ),
            "output/article-copy-preview.html": (
                '<html><body><div id="gzh-content">正文</div>'
                '<button id="gzhCopyBtn">复制</button></body></html>\n'
            ),
            "output/html-qc.md": (
                "# HTML QC\n\n"
                "output/article.html\n\n"
                "- validate_project: 通过\n"
                "- author_cta: disabled\n"
            ),
        }
        for relative in validate_project.HTML_DELIVERY_FILES:
            if relative == omit:
                continue
            target = self.project.joinpath(*Path(relative).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(payloads[relative], encoding="utf-8")

    def test_new_html_work_reports_missing_copy_preview(self):
        self._write_state()
        self._write_html_files(omit="output/article-copy-preview.html")

        self.assertEqual(
            validate_project.validate_article_project(self.project),
            [
                "output/article-copy-preview.html: "
                "missing required HTML delivery file"
            ],
        )

    def test_new_html_work_with_five_files_passes(self):
        self._write_state()
        self._write_html_files()

        self.assertEqual(
            validate_project.validate_article_project(self.project),
            [],
        )

    def test_completed_historical_article_is_grandfathered(self):
        self._write_state(
            current_stage="publish",
            html_status="completed",
        )

        self.assertEqual(
            validate_project.validate_article_project(self.project),
            [],
        )

    def test_zero_byte_delivery_file_is_rejected(self):
        self._write_state()
        self._write_html_files()
        (self.project / "output" / "article-copy.html").write_bytes(b"")

        self.assertEqual(
            validate_project.validate_article_project(self.project),
            [
                "output/article-copy.html: "
                "required HTML delivery file must be non-empty"
            ],
        )

    def test_article_html_minimum_structure_is_required(self):
        self._write_state()
        self._write_html_files()
        (self.project / "output" / "article.html").write_text(
            "<p>not a section</p>\n", encoding="utf-8"
        )

        self.assertEqual(
            validate_project.validate_article_project(self.project),
            [
                "output/article.html: missing required marker <section",
                "output/article.html: missing required marker </section>",
            ],
        )

    def test_author_cta_policy_must_be_recorded(self):
        self._write_state()
        self._write_html_files()
        qc = self.project / "output" / "html-qc.md"
        qc.write_text(
            qc.read_text(encoding="utf-8").replace("- author_cta: disabled\n", ""),
            encoding="utf-8",
        )
        self.assertEqual(
            validate_project.validate_article_project(self.project),
            [
                "output/html-qc.md: must record author_cta: disabled or author_cta: explicit"
            ],
        )

    def test_disabled_author_cta_rejects_gzh_placeholders_and_default_copy(self):
        self._write_state()
        self._write_html_files()
        (self.project / "output" / "article.html").write_text(
            '<section><p><span leaf="">{{作者名}}</span></p>'
            '<p><span leaf="">点赞、在看、转发</span></p></section>\n',
            encoding="utf-8",
        )
        (self.project / "output" / "article-copy.html").write_text(
            '<section><p><span leaf="">{{简介}}</span></p></section>\n',
            encoding="utf-8",
        )
        self.assertEqual(
            validate_project.validate_article_project(self.project),
            [
                "output/article.html: author placeholders are forbidden when author_cta is disabled",
                "output/article.html: gzh-design default author CTA is forbidden when author_cta is disabled",
                "output/article-copy.html: author placeholders are forbidden when author_cta is disabled",
            ],
        )

    def test_explicit_author_cta_is_allowed_when_recorded(self):
        self._write_state()
        self._write_html_files()
        qc = self.project / "output" / "html-qc.md"
        qc.write_text(
            qc.read_text(encoding="utf-8").replace(
                "- author_cta: disabled", "- author_cta: explicit"
            ),
            encoding="utf-8",
        )
        (self.project / "output" / "article.html").write_text(
            '<section><p><span leaf="">我是作者，欢迎点赞、在看、转发。</span></p>'
            '</section>\n',
            encoding="utf-8",
        )
        self.assertEqual(validate_project.validate_article_project(self.project), [])


def run_reverse_demo() -> int:
    fixture = HtmlFiveFileContractTests()
    fixture.setUp()
    try:
        fixture._write_state()
        fixture._write_html_files(
            omit="output/article-copy-preview.html"
        )
        command = [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "validate_project.py"),
            "article",
            str(fixture.project),
        ]

        red = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
        )
        print("===== RED: missing article-copy-preview.html =====")
        print(red.stdout.rstrip())
        if red.stderr:
            print(red.stderr.rstrip())
        print(f"red_exit={red.returncode}")

        (
            fixture.project
            / "output"
            / "article-copy-preview.html"
        ).write_text(
            '<html><body><div id="gzh-content">正文</div>'
            '<button id="gzhCopyBtn">复制</button></body></html>\n',
            encoding="utf-8",
        )
        green = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
        )
        print("===== GREEN: five files present =====")
        print(green.stdout.rstrip())
        if green.stderr:
            print(green.stderr.rstrip())
        print(f"green_exit={green.returncode}")

        return int(red.returncode != 1 or green.returncode != 0)
    finally:
        fixture.tearDown()


if __name__ == "__main__":
    if sys.argv[1:] == ["--reverse-demo"]:
        raise SystemExit(run_reverse_demo())
    unittest.main()
