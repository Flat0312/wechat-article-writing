# Blind Score Contract

`cheat-score-blind` remains an internal Cheat sub-agent. The WeChat total Skill
does not invoke it directly. When the root Cheat route returns its JSON, the
caller must validate the response before calculating `composite`, writing a
prediction, or using the score in a bump decision:

```text
python <SKILL_ROOT>/scripts/blind_score_adapter.py validate <BLIND_JSON> <RUBRIC_NOTES> --script <CHEAT_PROJECT>/scripts/<id>.md
```

The adapter reads the current `rubric_version` and dimension abbreviations from
`rubric_notes.md`. A rubric must resolve to exactly 7 or 9 dimensions; it does
not assume that the sub-agent frontmatter's prose is the schema. Use
`--dimensions ER,SR,...` only when the rubric has a non-standard but explicitly
known table, and record that decision in the caller's execution log.

The returned JSON must have the sub-agent schema's required top-level fields,
the exact rubric version, the exact dimension set, integer scores from 0 to 5,
`high|medium|low` confidence, one-line reasons of at most 30 characters, valid
blind-input booleans, a legal refusal code, and a 12-character script hash
prefix. The optional `--script` argument recomputes that prefix from the actual
script file. Unsupported fields, a composite supplied by the sub-agent, a
version mismatch, or a 7/9 dimension mismatch is a hard failure.

The adapter is read-only with respect to the Cheat project. A successful result
is a validation receipt, not a prediction and not permission to bypass the
root `cheat-predict` route. A refusal or contamination warning remains visible
to the parent route and must follow Cheat's refusal/review policy.
