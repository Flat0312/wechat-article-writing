from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / 'scripts'))

import article_state


class ArticleStateContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / 'article-project'
        self.state = article_state.create_project(self.project, 'article-1', 'full', 'account-profile', 'primary')

    def tearDown(self):
        self.temp.cleanup()

    def test_create_project_initializes_schema_and_history(self):
        persisted = json.loads((self.project / 'article-state.json').read_text(encoding='utf-8-sig'))
        self.assertEqual(persisted['schema_version'], '1.0')
        self.assertEqual(persisted['article_id'], 'article-1')
        self.assertEqual(persisted['mode'], 'full')
        self.assertEqual(persisted['profile_ref'], 'account-profile')
        self.assertEqual(persisted['cheat_binding'], 'primary')
        self.assertEqual(persisted['current_stage'], 'brief')
        self.assertEqual(list(persisted['stage_status']), list(article_state.STAGES))
        self.assertTrue((self.project / 'drafts' / 'draft-v1.md').is_file())
        self.assertTrue((self.project / 'research' / 'sources.json').is_file())

    def test_record_artifact_updates_hash_and_clears_role_approval(self):
        target = self.project / 'generated' / 'wechat' / 'final.md'
        target.parent.mkdir(parents=True)
        target.write_text('# 终稿\n', encoding='utf-8-sig')
        article_state.record_artifact(self.state, self.project, 'final', Path('generated/wechat/final.md'))
        self.assertEqual(self.state['artifacts']['final']['path'], 'generated/wechat/final.md')
        self.assertEqual(len(self.state['artifacts']['final']['sha256']), 64)
        self.assertEqual(self.state['approvals'], {})

    def test_final_approval_requires_recorded_final_artifact(self):
        with self.assertRaises(ValueError):
            article_state.record_approval(self.state, 'final', '2026-07-28T12:00:00+08:00')

    def test_final_approval_must_bind_final_artifact(self):
        target = self.project / 'generated' / 'wechat' / 'final.md'
        target.parent.mkdir(parents=True)
        target.write_text('# 终稿\n', encoding='utf-8-sig')
        article_state.record_artifact(self.state, self.project, 'final', Path('generated/wechat/final.md'))
        with self.assertRaises(ValueError):
            article_state.record_approval(self.state, 'final', '2026-07-28T12:00:00+08:00', artifact_role='prediction')

    def test_same_bytes_preserve_bound_final_approval(self):
        target = self.project / 'generated' / 'wechat' / 'final.md'
        target.parent.mkdir(parents=True)
        target.write_text('# 终稿\n', encoding='utf-8-sig')
        article_state.record_artifact(self.state, self.project, 'final', Path('generated/wechat/final.md'))
        article_state.record_approval(self.state, 'final', '2026-07-28T12:00:00+08:00')
        article_state.record_artifact(self.state, self.project, 'final', Path('generated/wechat/final.md'))
        self.assertIn('final', self.state['approvals'])
        self.assertEqual(self.state['approvals']['final']['artifact_sha256'], self.state['artifacts']['final']['sha256'])

    def test_invalidate_from_clears_downstream_approvals_and_marks_stale(self):
        article_state.set_stage(self.state, 'outline', 'completed')
        target = self.project / 'generated' / 'wechat' / 'final.md'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('# 终稿\n', encoding='utf-8-sig')
        article_state.record_artifact(self.state, self.project, 'final', Path('generated/wechat/final.md'))
        article_state.record_approval(self.state, 'final', '2026-07-28T12:00:00+08:00')
        article_state.set_stage(self.state, 'visuals', 'completed')
        prediction_target = self.project / 'generated' / 'wechat' / 'prediction.md'
        prediction_target.parent.mkdir(parents=True, exist_ok=True)
        prediction_target.write_text('# 预测\n', encoding='utf-8-sig')
        article_state.record_artifact(self.state, self.project, 'prediction', Path('generated/wechat/prediction.md'))
        article_state.record_approval(self.state, 'prediction', '2026-07-28T12:05:00+08:00')
        article_state.invalidate_from(self.state, 'final')
        self.assertNotIn('final', self.state['approvals'])
        self.assertNotIn('prediction', self.state['approvals'])
        self.assertEqual(self.state['stage_status']['prediction'], 'stale')
        self.assertIn('prediction', self.state['stale_artifacts'])
        self.assertIn('create_new_prediction_version', self.state['required_actions'])
        self.assertNotIn('outline', self.state['approvals'])

    def test_unknown_stage_and_status_are_rejected(self):
        with self.assertRaises(ValueError):
            article_state.set_stage(self.state, 'ghost', 'completed')
        with self.assertRaises(ValueError):
            article_state.set_stage(self.state, 'brief', 'ghost')

    def test_unknown_schema_version_is_rejected(self):
        with self.assertRaises(ValueError):
            article_state.write_state(self.project, {**self.state, 'schema_version': '2.0', 'updated_at': datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')})

    def test_absolute_artifact_path_is_rejected(self):
        with self.assertRaises(ValueError):
            article_state.record_artifact(self.state, self.project, 'final', Path('C:/tmp/final.md'))


if __name__ == '__main__':
    unittest.main()
