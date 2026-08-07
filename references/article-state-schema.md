# Article State Contract

## Purpose

`article-state.json` makes a single article resumable and records which downstream artifacts became stale after an upstream change.

## Required fields

| Field | Meaning |
|---|---|
| `schema_version` | State schema; current projects use `1.1` (nine-stage text-only long-essay), historical projects keep `1.0` (twelve-stage with HTML five-file set) |
| `article_id` | Stable article identifier |
| `mode` | `full`, `fast`, or `temporary` |
| `profile_ref` | Portable profile reference or null |
| `cheat_binding` | Logical Cheat binding or null |
| `current_stage` | Current stage name |
| `stage_status` | Status for every stage in the project's schema (9 for 1.1, 12 for 1.0) |
| `artifacts` | Relative path and SHA256 by artifact role |
| `approvals` | User confirmations with timestamps and artifact hash bindings where required |
| `skill_routes` | Canonical Skill selected for each routed action |
| `stale_artifacts` | Artifact roles invalidated by upstream change |
| `required_actions` | Recovery actions such as a new prediction version |
| `created_at` | Article project creation timestamp |
| `updated_at` | Timestamp of the most recent persisted state update |

## Stage order and transitions

Two schemas are recognised:

- `1.0` (historical, HTML five-file set): `brief`, `topic`, `evidence`, `outline`, `draft`, `final`, `prediction`, `visual_plan`, `visuals`, `html`, `publish`, `retro`.
- `1.1` (current long-essay, pure text): `brief`, `topic`, `evidence`, `outline`, `draft`, `final`, `prediction`, `publish`, `retro`. The `visual_plan` / `visuals` / `html` stages are intentionally absent; no visual or HTML artifact is required for schema 1.1 projects.

`set_stage` changes only `current_stage` and the named `stage_status`; it does not propagate staleness or persist the state. After content or an artifact at an upstream stage changes, the orchestrator MUST explicitly call `invalidate_from` with that changed stage and MUST persist the resulting state before continuing the workflow. A status-only transition is not an upstream content change. For schema 1.1 projects, changes at or before `final` invalidate `prediction`, `publish`, and `retro`; for schema 1.0 projects, the same change also invalidates the three visual / HTML stages.

### Stage → confirmation class mapping

`wechat-article-writing` 公开 5 个用户确认节点（见 `references/onboarding.md` "Five confirmation classes"），
但 `article-state.json` 跟踪 9（1.1）或 12（1.0）个 stage。本表把确认节点和 stage 显式对齐：

| 确认节点 | 关联 stage（1.1） | 关联 stage（1.0） | 隐式校验 |
|---|---|---|---|
| 1. 账号配置 / 导入预览 | （项目级，不在 article-state） | （项目级，不在 article-state） | `account.json` 校验 |
| 2. 选题角度 + 受众 | `brief`, `topic` | `brief`, `topic` | `evidence` 阶段事实核查后回链 |
| 3. 大纲事实边界 | `outline` | `outline` | `evidence` 锚点校验 + `outline` 写前卡片 8 项 |
| 4. 最终正文 | `draft`, `final` | `draft`, `final` | `final.artifact_sha256` 绑定 |
| 5. 视觉交付（news-card / 1.0 历史） | 不适用 | `visual_plan`, `visuals`, `html` | news-card 走独立 21:9 头图交付；1.0 走 `html-qc.md` 全部通过 + 5 件套存在 |

`evidence` 和 `draft` 不单独暴露给用户确认——它们由相邻 stage 的确认隐式覆盖
（`outline` 必须以 `evidence.md` 为前提；`final` 必须以 `drafts/final.md` 为前提）。
任一上游被改都触发 `invalidate_from` 链路；用户最坏情况下需要重新确认 `final`。


## Status values

Allowed values are `pending`, `in_progress`, `awaiting_confirmation`, `completed`, `failed`, `skipped`, and `stale`.

## Artifact rules

Serialized artifact paths MUST be non-empty POSIX paths relative to the article project. They use `/`, may not contain a `..` component, and may not be absolute. Windows drive paths, UNC paths, root-relative paths, and any value containing a Windows backslash (`\`) are rejected. `profile_ref` is either null or follows the same portable relative-path rules.

For HTML-complete long essays, the `html` artifact role is the manual-paste deliverable and its
path MUST be `output/article-copy.html`. The associated HTML contract also retains
`output/article.html`, `output/article-preview.html`, `output/article-copy-preview.html`, and
`output/html-qc.md`; the validator enforces the five-file contract for current work while
preserving completed historical projects. **These five-file HTML rules apply only to
schema 1.0 long essays; schema 1.1 projects do not record an `html` artifact, do not
generate an `output/article.html` and do not depend on `gzh-design`.**

For visual completion in schema 1.0 long essays, `artifacts.visuals.path` should be
`visuals/assets/manifest.json`. The manifest is the canonical article-local index
for the one cover and selected body assets; external Skill output directories are
provenance only. **Schema 1.1 long essays do not record a `visuals` artifact; the
`visual_plan` / `visuals` keys are absent from their state.** The news-card pipeline keeps
its own 21:9 cover flow under `news-card/`, independent of long-essay state.

Every recorded artifact must point to an existing file and include a lowercase
64-character SHA256 that matches the file bytes. The project validator recomputes
that hash; a missing, malformed, stale, or escaping artifact blocks validation.

Article bodies and credentials are never embedded in state. Cheat prediction and retro files remain in the Cheat project and are referenced through the logical binding.

## Approval rules

An approval bound to an artifact records both `artifact_role` and `artifact_sha256`. A `final` approval MUST bind the recorded `final` artifact; omitting `artifact_role` when calling `record_approval` for key `final` selects that role automatically, while explicitly selecting any other role is rejected. The final artifact must already be recorded.

The project validator also checks every approval that declares an artifact
binding. Its `artifact_sha256` must be a valid SHA256 and equal the referenced
artifact hash; a `final` approval without a `final` binding is invalid.

Before Cheat prediction, `approvals.final.artifact_sha256` MUST equal the current `artifacts.final.sha256`. A missing binding, missing final artifact, or hash mismatch blocks prediction and requires the user to confirm the current final text.

When `record_artifact` replaces a role with different bytes, it removes every approval bound to that role. Re-recording the same SHA256 preserves those approvals. `invalidate_from` removes approvals whose key names the changed stage or a downstream stage, and approvals whose `artifact_role` is the changed stage or a downstream stage; approvals for unaffected earlier stages remain valid.

## Invalidation

`invalidate_from` marks every completed downstream stage, and every downstream stage with a recorded artifact, as stale. It also clears approvals in the changed-stage range as defined above. When a stage at or before `final` changes, it adds the `create_new_prediction_version` required action.

`required_actions` is a workflow gate, not a version allocator. While `create_new_prediction_version` is present, the orchestrator MUST make the mandatory `cheat-on-content` call and obtain a new prediction version before treating prediction as current. Prediction immutability, version allocation, and preservation of Cheat history are guaranteed by that mandatory Skill call and by the orchestrator, not by article-state helpers.

`record_artifact` does not allocate prediction versions and never overwrites or deletes prediction history in the Cheat project. Recording `prediction` again updates only the current local receipt/reference and hash for that role, then clears the local required action. The first external prediction is `v1`; every later external prediction uses a new version and leaves all earlier versions intact.

## Timestamp format

The official state writer emits `created_at` and `updated_at` as timezone-aware ISO 8601 strings at second precision, for example `2026-07-11T14:30:00+08:00`. Orchestrators MUST record every approval timestamp in the same format. This is a schema contract even where the current helper or validator does not automatically enforce it.
