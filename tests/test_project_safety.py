from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def _ensure_scripts_on_path():
    sys = __import__('sys')
    scripts_path = str(SKILL_ROOT / 'scripts')
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
        return True
    return False


sys_path_inserted = _ensure_scripts_on_path()

import validate_project


class ProjectSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()
        if sys_path_inserted and sys.path[0] == str(SKILL_ROOT / 'scripts'):
            sys.path.pop(0)

    def test_secret_like_fields_are_rejected_recursively(self):
        payload = {'meta': {'secret_token': 'abc'}, 'settings': [{'api_key': 'xyz'}]}
        self.assertEqual(validate_project._json_safety_errors(payload), [
            'root.meta.secret_token: secret-like key is not allowed',
            'root.settings[0].api_key: secret-like key is not allowed',
        ])

    def test_absolute_paths_are_rejected_by_default(self):
        payload = {'paths': ['/abs/path', 'relative/path'], 'nested': {'key': 'C:/abs/path'}}
        self.assertEqual(validate_project._json_safety_errors(payload), [
            'root.paths[0]: absolute path is not allowed',
            'root.nested.key: absolute path is not allowed',
        ])

    def test_local_bindings_allow_absolute_paths(self):
        payload = {'bindings': {'primary': {'path': 'C:/local/project'}}}
        self.assertEqual(validate_project._json_safety_errors(payload, allow_absolute_paths=True), [])

    def test_gitignore_must_ignore_bindings(self):
        profile = self.root / 'profile'
        profile.mkdir()
        (profile / 'account.json').write_text(json.dumps({'schema_version': '1.0', 'account_id': 'account', 'mode': 'new', 'profile_docs': validate_project.PROFILE_DOCS, 'created_at': '2026-07-28T12:00:00+08:00', 'updated_at': '2026-07-28T12:00:00+08:00'}, ensure_ascii=False) + '\n', encoding='utf-8')
        for doc in validate_project.PROFILE_DOCS:
            (profile / doc).write_text('# doc\n', encoding='utf-8')
        (profile / 'bindings.local.json').write_text('{"schema_version":"1.0","bindings":{}}\n', encoding='utf-8')
        self.assertIn(validate_project.GITIGNORE_NOT_IGNORED_ERROR, validate_project.validate_profile(profile))

    def test_valid_profile_passes_validation(self):
        profile = self._valid_profile()
        self.assertEqual(validate_project.validate_profile(profile), [])

    def test_article_project_validates_artifacts_and_stage_status(self):
        project = self.root / 'article'
        project.mkdir()
        state = {
            'schema_version': '1.0',
            'article_id': 'article-1',
            'mode': 'full',
            'profile_ref': 'account-profile',
            'cheat_binding': 'primary',
            'current_stage': 'draft',
            'stage_status': {stage: 'pending' for stage in validate_project.STAGES},
            'artifacts': {'final': {'path': 'generated/wechat/final.md', 'sha256': 'a' * 64}},
            'approvals': {},
            'skill_routes': {},
            'stale_artifacts': [],
            'required_actions': [],
            'created_at': '2026-07-28T12:00:00+08:00',
            'updated_at': '2026-07-28T12:00:00+08:00',
        }
        (project / 'article-state.json').write_text(json.dumps(state, ensure_ascii=False) + '\n', encoding='utf-8')
        (project / 'generated' / 'wechat').mkdir(parents=True)
        (project / 'generated' / 'wechat' / 'final.md').write_text('final\n', encoding='utf-8')
        errors = validate_project.validate_article_project(project)
        self.assertEqual(errors, [])

    def test_article_project_rejects_invalid_status_and_path(self):
        project = self.root / 'article'
        project.mkdir()
        state = {
            'schema_version': '1.0',
            'article_id': 'article-1',
            'mode': 'full',
            'profile_ref': '..',
            'cheat_binding': 'primary',
            'current_stage': 'ghost',
            'stage_status': {**{stage: 'pending' for stage in validate_project.STAGES}, 'brief': 'soon'},
            'artifacts': {'final': {'path': 'generated/wechat/final.md', 'sha256': 'a' * 64}},
            'approvals': {},
            'skill_routes': {},
            'stale_artifacts': [],
            'required_actions': [],
            'created_at': '2026-07-28T12:00:00+08:00',
            'updated_at': '2026-07-28T12:00:00+08:00',
        }
        (project / 'article-state.json').write_text(json.dumps(state, ensure_ascii=False) + '\n', encoding='utf-8')
        (project / 'generated' / 'wechat').mkdir(parents=True)
        (project / 'generated' / 'wechat' / 'final.md').write_text('final\n', encoding='utf-8')
        self.assertEqual(validate_project.validate_article_project(project), [
            'article-state.json: current_stage must name one of the 12 stages',
            'article-state.json: profile_ref must be null or a portable relative reference',
            'article-state.json: stage_status.brief=soon is invalid',
        ])

    def _valid_profile(self) -> Path:
        profile = self.root / 'profile'
        profile.mkdir()
        (profile / 'account.json').write_text(json.dumps({'schema_version': '1.0', 'account_id': 'account', 'mode': 'new', 'profile_docs': list(validate_project.PROFILE_DOCS), 'created_at': '2026-07-28T12:00:00+08:00', 'updated_at': '2026-07-28T12:00:00+08:00'}, ensure_ascii=False) + '\n', encoding='utf-8')
        for doc in validate_project.PROFILE_DOCS:
            (profile / doc).write_text('# doc\n', encoding='utf-8')
        (profile / 'bindings.local.json').write_text('{"schema_version":"1.0","bindings":{"primary":{"path":"C:/local/project"}}}\n', encoding='utf-8')
        (profile / '.gitignore').write_text('bindings.local.json\n', encoding='utf-8')
        return profile


if __name__ == '__main__':
    unittest.main()
