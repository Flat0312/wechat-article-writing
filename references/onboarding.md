# Onboarding Protocol

## Entry routing

Ask the user to choose or infer one path: import an account, create a long-term account, or create a temporary article. Do not create files until the path and destination are known.

Use these trigger examples and inference rules:

- "从零写一篇公众号文章，主题是……" means a temporary article when the user does not ask to preserve long-term account state.
- "从零初始化一个长期运营的公众号账号" means create a long-term account and invoke Cheat initialization.
- "导入这个已有账号目录：……" means preview and import an existing account.
- "继续处理这份 draft：……" preserves the supplied draft and uses its selected profile when one is given; otherwise treat it as a temporary article. Do not force it back to topic discovery.

## Workspace layout

Confirm one workspace before writing. Keep the portable profile and individual article projects separate:

```text
<workspace>/account-profile/
<workspace>/articles/<YYYY-MM-DD-slug>/
```

### Canonical workspace guard

Before writing, read the selected workspace's `START-HERE.md` and project governance file when
they exist. If the project declares a canonical root and a read-only backup:

- write all new profiles, article state, predictions, publish records, and generated artifacts
  only under the canonical root;
- use the read-only backup only as a recovery or migration-check input;
- never choose the backup as an output directory, write state into it, synchronize both
  directions, or clean it up;
- on Windows, resolve absolute paths and compare them case-insensitively before authorizing a
  write.

Pass only a target already confirmed inside the canonical root to
`wechat-content-strategy` or `wechat-style-learning`.

For an imported source, recommend a sibling workspace such as `<source-name>-articles`, but let the user choose it. The output may not be the source, its ancestor, or its descendant. 账号包与文章项目不得写入导入源目录。

## Import account

1. If the supplied directory already contains `account.json`, validate it and use it directly; do not duplicate a standard profile.
2. Otherwise run `profile_adapter.py preview` against the supplied directory.
3. Show copied `mapped` documents separately from `live_linked` Cheat sources. A live-linked source remains in the Cheat project and is resolved through the local binding; it is not copied into the portable profile.
4. If `.cheat-state.json` exists, run `python <SKILL_ROOT>/scripts/dependency_check.py --stage account`. If the report is `ok: false`, stop before Cheat status or import and report the missing dependency.
5. When the dependency check passes, invoke the root `cheat-on-content` Skill for status inspection and compare the observed schema with its migrations registry. 未取得兼容的 `cheat-status` 结果前，不得继续 preview 或 import。
   For benchmark or imported evidence, use the explicit `cheat-learn-from` route and keep it scoped to the sample scope and target Cheat project. If migration is required, use the explicit `cheat-migrate` route only after explicit approval or in a copied working project, and re-obtain a compatible `cheat-status` result before continuing.
6. If its schema is incompatible, stop the read-only import. Offer migration in the source after explicit approval or migration in a copied working project.
7. Show mapped, live-linked, missing, conflicting, and excluded fields.
8. Run `profile_adapter.py import` only after approval and only into the confirmed workspace's `account-profile/` directory.
9. Validate the result before using it.

The adapter's `approved` flag authorizes its local write only. It never substitutes for the mandatory root `cheat-on-content` status check or proves schema compatibility.

Never import `.auth`, cookies, API keys, cached login state, or secret files. Never change the source during preview or ordinary import.

## Create long-term account

First invoke root `cheat-on-content` and complete its initialization with content form `long-essay`. Preserve every confirmation required by Cheat.

After Cheat initialization, collect only WeChat-specific context in three compact groups:

1. Account identity, creation goal, and intended audience.
2. Content lanes, author evidence, boundaries, and voice.
3. Historical articles, benchmarks, visual preferences, and delivery preferences.

Summarize a complete profile draft. Ask one follow-up at a time only for contradictions or missing fields. Show the final profile before writing it. After approval, run `profile_adapter.py create` with the initialized Cheat project, write the approved answers into the profile Markdown files, and validate the result.

Initialize an empty optional `history/edits/index.json` for future confirmed edit learning. Do not infer style rules from imported files during onboarding; learning requires a separate explicit user request.

## Temporary article

Temporary mode requires a clear topic. It may run research, writing, editing, visual, and HTML stages without a persistent profile. If the user asks for Cheat scoring, prediction, publish registration, or retro, require an existing Cheat project or upgrade to long-term account mode. Never simulate those actions.

## Learning confirmation

When the user explicitly asks to register learning, show candidate rules first and obtain separate user confirmation before writing them into the account learning ledger.

## Five confirmation classes

1. Account import preview or new profile.
2. Topic, angle, and audience.
3. Outline, core claims, and fact boundary.
4. Final text before Cheat prediction and visual production.
5. Visual delivery: confirm the plan before generation and confirm HTML after layout.

External Skills keep their own mandatory confirmations. The visual confirmation covers the single `21:9` WeChat main-cover plan; no square sharing card or body-illustration confirmation is needed because those assets are outside this workflow.
