# Humanizer diagnostic contract

`humanizer-zh` is an optional diagnostic input after facts, structure, and
account voice stabilize. It must return a local issue list, never a replacement
draft:

```json
{
  "schema_version": "1.0",
  "source_skill": "humanizer-zh",
  "mode": "diagnostic",
  "input_sha256": "<SHA256 of the current draft>",
  "issues": [
    {
      "location": "paragraph:3",
      "pattern": "机械连接词",
      "suggestion": "删去连接词并让因果关系承担转场。",
      "scope": "local",
      "adds_facts": false,
      "changes_meaning": false,
      "severity": "medium"
    }
  ]
}
```

Validate the response against the current draft before applying any change:

```text
python <SKILL_ROOT>/scripts/humanizer_diagnostic_adapter.py <DIAGNOSTIC_JSON> --input <DRAFT>
```

The adapter rejects full-text fields, scores used as approval, missing input
hashes, non-local scope, and suggestions that add facts or change meaning. The
total-control Skill applies the smallest compatible local edit, rechecks facts
and account voice, and records any resulting final-artifact hash change. A
missing humanizer is allowed; the built-in AI-pattern pass remains mandatory.
