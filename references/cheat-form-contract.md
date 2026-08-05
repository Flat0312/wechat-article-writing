# Cheat content-form and rubric contract

For a long-essay article, two facts must be recorded separately before formal
prediction:

1. The root `cheat-on-content` Skill was actually called and completed the
   selected route.
2. The returned rubric is adapted and compatible with the current content
   form. A Cheat project initialized with an opinion-video rubric does not
   satisfy the second fact merely because the first fact is true.

Normalize the real root response into this input shape after `cheat-init` or a
fresh `cheat-status` check:

```json
{
  "source": "cheat-on-content",
  "root_skill_called": true,
  "root_route": "cheat-init",
  "root_call_status": "completed",
  "target_project_binding": "primary",
  "content_form": "long-essay",
  "cheat_schema_version": "1.2",
  "rubric_adapter": "wechat-long-essay-v1",
  "rubric_status": "compatible",
  "rubric_version": "v1",
  "rubric_form_mismatch": false,
  "checked_at": "2026-08-05T15:00:00+08:00"
}
```

Record and verify the normalized response against the live Cheat state:

```text
python <SKILL_ROOT>/scripts/cheat_form_adapter.py record <ARTICLE_PROJECT> --cheat-project <CHEAT_PROJECT> --status-receipt <CHEAT_FORM.json> --target-binding primary --content-form long-essay
python <SKILL_ROOT>/scripts/cheat_form_adapter.py verify <ARTICLE_PROJECT>/cheat-form-receipt.json --cheat-project <CHEAT_PROJECT> --target-binding primary --content-form long-essay
```

The receipt contains both `root_call_status` and `rubric_status`. It is a
precondition for `cheat_prediction_adapter.py`; a missing receipt, a
`rubric_form_mismatch=true` response, an opinion-video-only adapter, or a
schema/binding mismatch blocks prediction before any Cheat snapshot is
written. The receipt proves a normalized external response; it does not
replace the real root Skill call.
