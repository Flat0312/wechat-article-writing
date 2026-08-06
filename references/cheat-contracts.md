# Cheat Contracts

## Cheat content-form and rubric contract

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

## Long-essay Cheat prediction bridge

`drafts/final.md` is the WeChat workflow's final artifact, while Cheat's
`cheat-predict` route accepts a `scripts/<id>.md` input. The total-control
adapter closes that boundary without copying an unapproved draft by hand.
Before the copy, the article must contain a verified
[`cheat-form-receipt.json`](#cheat-content-form-and-rubric-contract) whose root Cheat call is
complete and whose rubric is explicitly compatible with
`content_form=long-essay`.

### Preconditions

`<ARTICLE_DIR>/article-state.json` must show:

- `stage_status.final` is `completed`;
- `artifacts.final.path` is exactly `drafts/final.md`;
- `artifacts.final.sha256` is a valid hash of the current file;
- `approvals.final.approved` is `true`, `artifact_role` is `final`, and
  `artifact_sha256` equals the current final hash;
- `final` is not listed in `stale_artifacts`.

The adapter rejects any missing field, hash mismatch, non-UTF-8 final, or
non-portable final path before it creates output.

### Command and outputs

Run:

```text
python <SKILL_ROOT>/scripts/cheat_prediction_adapter.py <ARTICLE_DIR> --cheat-project <CHEAT_PROJECT>
```

The adapter creates an immutable Cheat input at:

```text
<CHEAT_PROJECT>/scripts/wechat-<article_id>-<final_sha256>.md
```

The file contains a small machine-readable header with `source_path` and
`source_sha256`, followed by the final text unchanged. It is made read-only;
an existing file with the same name must have byte-identical contents or the
adapter fails rather than overwriting prediction input.

The article project receives `prediction-input-reference.json` with
`final_sha256`, `snapshot_path`, `snapshot_sha256`, `content_form`, and
`read_only`. This is an input receipt, not a Cheat prediction; only a real
`cheat-predict` call may create the immutable prediction record.

When no `--cheat-project` is supplied, the adapter resolves the article's
`cheat_binding` through the canonical workspace's ignored
the resolved `<account_profile>/bindings.local.json`. The resolved path is never written into
the portable receipt.

## Post-migrate Cheat status receipt

`cheat-migrate` changes the source project's `.cheat-state.json`, but its own
workflow does not produce a machine-readable compatibility receipt. The total
control therefore requires a fresh root `cheat-status` call after every
successful migration. The root call must normalize its result into this input
shape before handing it to the adapter:

```json
{
  "source": "cheat-status",
  "target_project_binding": "primary",
  "cheat_schema_version": "1.2",
  "status": "compatible",
  "checked_at": "2026-08-05T15:00:00+08:00"
}
```

The adapter independently reads `<CHEAT_PROJECT>/.cheat-state.json` and rejects
the receipt when its `schema_version` differs. It also rejects a non-compatible
status, another source, a missing timezone, or a machine path disguised as a
binding. `target_project_binding` is a logical name such as `primary`; it is
not a filesystem path.

Run it only after the real `cheat-migrate` and the fresh root `cheat-status`:

```text
python <SKILL_ROOT>/scripts/cheat_status_adapter.py record <ACCOUNT_DIR> --cheat-project <CHEAT_PROJECT> --status-receipt <CHEAT_STATUS.json> --target-binding primary
python <SKILL_ROOT>/scripts/cheat_status_adapter.py verify <ACCOUNT_DIR>/cheat-status-receipt.json --cheat-project <CHEAT_PROJECT> --target-binding primary
```

The successful output is `<ACCOUNT_DIR>/cheat-status-receipt.json`:

| Field | Required value |
|---|---|
| `schema_version` | `1.0` (receipt schema) |
| `receipt_type` | `post-migrate-cheat-status` |
| `target_project_binding` | The confirmed logical binding, for example `primary` |
| `cheat_schema_version` | The version reported by `cheat-status` and the live state file |
| `status` | `compatible` |
| `source` | `cheat-status` |
| `checked_at` | Timezone-aware ISO 8601 timestamp |

The receipt is evidence of a fresh compatible status check, not a substitute
for invoking the root Cheat Skill. Import or downstream work must stop when the
receipt is absent or `verify` fails.

## Cheat seed humanizer compatibility register

The external `cheat-seed` route currently mentions a generic `humanizer`
Skill, while this WeChat total-control workflow declares `humanizer-zh` as
the only optional diagnostic Skill. This is an external contract mismatch;
the total-control repository does not rewrite the external route.

When invoking the real root `cheat-on-content` Skill for `cheat-seed`:

- Do not install, discover, or invoke a second Skill named `humanizer` because
  of text emitted by the external route.
- Keep the root Cheat seed result scoped to topic seeding. It is not a
  humanizer diagnostic and cannot replace the `humanizer-zh` contract in
  [`external-contracts.md`](external-contracts.md#humanizer-diagnostic-contract).
- If the external seed route hard-blocks on its generic humanizer dependency,
  mark the seed stage `failed` or `blocked`, preserve the raw failure, and do
  not simulate a candidate or continue as if `humanizer-zh` satisfied it.
- If the seed route completes without using that branch, record the external
  mismatch in the execution notes and continue only with the real root result.

This register is a boundary adaptation, not a claim that the external
`cheat-seed` implementation has been fixed. The external route must be updated
separately to name `humanizer-zh` or to remove that dependency.

## Blind Score Contract

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
