"""Installation contract tests.

The companion skills are discovered through manual directory junctions
created from the README instructions. These tests lock every premise that
mechanism depends on: companion sources are versioned in the repo, their
frontmatter names match the junction directory names, every script path a
companion SKILL.md references actually exists, and the documented CLI
surfaces (edit_learning subcommands, validate_project stable profile
interface) still work as promised.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
COMPANIONS = ("wechat-content-strategy", "wechat-style-learning")


def _frontmatter_name(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"(?m)^name:\s*(\S+)\s*$", text)
    assert match is not None, f"{skill_md} has no frontmatter name"
    return match.group(1)


class InstallationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = (SKILL_ROOT / "README.md").read_text(encoding="utf-8")

    def test_companion_sources_are_versioned_in_repo(self):
        for name in COMPANIONS:
            companion_root = SKILL_ROOT / "companion-skills" / name
            self.assertTrue(
                (companion_root / "SKILL.md").is_file(),
                f"missing companion source: {companion_root / 'SKILL.md'}",
            )

    def test_frontmatter_names_match_junction_directory_names(self):
        for name in COMPANIONS:
            skill_md = SKILL_ROOT / "companion-skills" / name / "SKILL.md"
            self.assertEqual(
                _frontmatter_name(skill_md),
                name,
                "runtime discovery after junction creation relies on the "
                "frontmatter name matching the junction directory name",
            )

    def test_readme_junction_targets_point_at_versioned_sources(self):
        self.assertIn("Junction", self.readme)
        for name in COMPANIONS:
            self.assertIn(name, self.readme)
            self.assertTrue(
                (SKILL_ROOT / "companion-skills" / name).is_dir(),
                f"README junction target companion-skills/{name} is missing",
            )

    def test_style_learning_script_references_resolve(self):
        companion_root = SKILL_ROOT / "companion-skills" / "wechat-style-learning"
        skill_md = (companion_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(
            "<SKILL_ROOT>/scripts/edit_learning.py", skill_md
        )
        self.assertIn(
            "<WECHAT_ARTICLE_ROOT>/scripts/validate_project.py", skill_md
        )
        self.assertTrue(
            (companion_root / "scripts" / "edit_learning.py").is_file()
        )
        self.assertTrue(
            (SKILL_ROOT / "scripts" / "validate_project.py").is_file()
        )

    def test_edit_learning_cli_exposes_documented_subcommands(self):
        script = (
            SKILL_ROOT
            / "companion-skills"
            / "wechat-style-learning"
            / "scripts"
            / "edit_learning.py"
        )
        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for subcommand in (
            "record",
            "aggregate",
            "observe-final",
            "aggregate-observations",
        ):
            self.assertIn(subcommand, result.stdout)

    def test_validate_project_profile_interface_is_stable(self):
        script = SKILL_ROOT / "scripts" / "validate_project.py"
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [sys.executable, str(script), "profile", temp],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertIsInstance(payload, dict)
        self.assertEqual(set(payload), {"ok", "errors"})
        self.assertFalse(payload["ok"])
        self.assertIsInstance(payload["errors"], list)
        self.assertTrue(payload["errors"])

    def test_execution_declares_the_stable_cross_skill_interface(self):
        execution = (SKILL_ROOT / "references" / "execution.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("跨 Skill 稳定验证接口", execution)
        self.assertIn("validate_project.py profile", execution)
        self.assertIn('{"ok": bool, "errors": [...]}', execution)


if __name__ == "__main__":
    unittest.main()
