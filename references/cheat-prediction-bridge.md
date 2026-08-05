# Long-essay Cheat prediction bridge

`drafts/final.md` is the WeChat workflow's final artifact, while Cheat's
`cheat-predict` route accepts a `scripts/<id>.md` input. The total-control
adapter closes that boundary without copying an unapproved draft by hand.
Before the copy, the article must contain a verified
[`cheat-form-receipt.json`](cheat-form-contract.md) whose root Cheat call is
complete and whose rubric is explicitly compatible with
`content_form=long-essay`.

## Preconditions

`<ARTICLE_DIR>/article-state.json` must show:

- `stage_status.final` is `completed`;
- `artifacts.final.path` is exactly `drafts/final.md`;
- `artifacts.final.sha256` is a valid hash of the current file;
- `approvals.final.approved` is `true`, `artifact_role` is `final`, and
  `artifact_sha256` equals the current final hash;
- `final` is not listed in `stale_artifacts`.

The adapter rejects any missing field, hash mismatch, non-UTF-8 final, or
non-portable final path before it creates output.

## Command and outputs

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
`account-profile/bindings.local.json`. The resolved path is never written into
the portable receipt.
