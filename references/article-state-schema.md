# Article State Contract

## Purpose

`article-state.json` makes a single article resumable and records which downstream artifacts became stale after an upstream change.

## Required fields

| Field | Meaning |
|---|---|
| `schema_version` | State schema; v1 uses `1.0` |
| `article_id` | Stable article identifier |
| `mode` | `full`, `fast`, or `temporary` |
| `profile_ref` | Portable profile reference or null |
| `cheat_binding` | Logical Cheat binding or null |
| `current_stage` | Current stage name |
| `stage_status` | Status for all twelve stages |
| `artifacts` | Relative path and SHA256 by artifact role |
| `approvals` | User confirmations with timestamps and artifact hash bindings where required |
| `skill_routes` | Canonical Skill selected for each routed action |
| `stale_artifacts` | Artifact roles invalidated by upstream change |
| `required_actions` | Recovery actions such as a new prediction version |
| `created_at` | Article project creation timestamp |
| `updated_at` | Timestamp of the most recent persisted state update |

## Stage order and transitions

The authoritative `STAGES` order is exactly:

`brief`, `topic`, `evidence`, `outline`, `draft`, `final`, `prediction`, `visual_plan`, `visuals`, `html`, `publish`, `retro`.

`set_stage` changes only `current_stage` and the named `stage_status`; it does not propagate staleness or persist the state. After content or an artifact at an upstream stage changes, the orchestrator MUST explicitly call `invalidate_from` with that changed stage and MUST persist the resulting state before continuing the workflow. A status-only transition is not an upstream content change.

## Status values

Allowed values are `pending`, `in_progress`, `awaiting_confirmation`, `completed`, `failed`, `skipped`, and `stale`.

## Artifact rules

Serialized artifact paths MUST be non-empty POSIX paths relative to the article project. They use `/`, may not contain a `..` component, and may not be absolute. Windows drive paths, UNC paths, root-relative paths, and any value containing a Windows backslash (`\`) are rejected. `profile_ref` is either null or follows the same portable relative-path rules.

Article bodies and credentials are never embedded in state. Cheat prediction and retro files remain in the Cheat project and are referenced through the logical binding.

## Approval rules

An approval bound to an artifact records both `artifact_role` and `artifact_sha256`. A `final` approval MUST bind the recorded `final` artifact; omitting `artifact_role` when calling `record_approval` for key `final` selects that role automatically, while explicitly selecting any other role is rejected. The final artifact must already be recorded.

Before Cheat prediction, `approvals.final.artifact_sha256` MUST equal the current `artifacts.final.sha256`. A missing binding, missing final artifact, or hash mismatch blocks prediction and requires the user to confirm the current final text.

When `record_artifact` replaces a role with different bytes, it removes every approval bound to that role. Re-recording the same SHA256 preserves those approvals. `invalidate_from` removes approvals whose key names the changed stage or a downstream stage, and approvals whose `artifact_role` is the changed stage or a downstream stage; approvals for unaffected earlier stages remain valid.

## Invalidation

`invalidate_from` marks every completed downstream stage, and every downstream stage with a recorded artifact, as stale. It also clears approvals in the changed-stage range as defined above. When a stage at or before `final` changes, it adds the `create_new_prediction_version` required action.

`required_actions` is a workflow gate, not a version allocator. While `create_new_prediction_version` is present, the orchestrator MUST make the mandatory `cheat-on-content` call and obtain a new prediction version before treating prediction as current. Prediction immutability, version allocation, and preservation of Cheat history are guaranteed by that mandatory Skill call and by the orchestrator, not by article-state helpers.

`record_artifact` does not allocate prediction versions and never overwrites or deletes prediction history in the Cheat project. Recording `prediction` again updates only the current local receipt/reference and hash for that role, then clears the local required action. The first external prediction is `v1`; every later external prediction uses a new version and leaves all earlier versions intact.

## Timestamp format

The official state writer emits `created_at` and `updated_at` as timezone-aware ISO 8601 strings at second precision, for example `2026-07-11T14:30:00+08:00`. Orchestrators MUST record every approval timestamp in the same format. This is a schema contract even where the current helper or validator does not automatically enforce it.
