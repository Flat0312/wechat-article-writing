# Account Profile Contract

## Purpose

The account profile stores portable creative context. It never stores credentials, article bodies, machine-specific absolute paths, or copies of Cheat state that can drift.

## Required files

| File | Responsibility |
|---|---|
| `account.json` | Schema, stable account ID, mode, logical bindings, document list, timestamps |
| `positioning.md` | Mission, author identity, content lanes, boundaries |
| `audience.md` | Audience, needs, evidence, anti-persona |
| `voice.md` | Tone, rhythm, preferred and forbidden expressions |
| `content-patterns.md` | Validated and provisional writing patterns |
| `visual-style.md` | Cover, illustration, palette, and forbidden visual styles |
| `benchmarks.md` | Benchmark accounts, lessons, and non-copy boundaries |

`history/articles/index.json` and `history/retros/index.json` contain source references only.

`history/edits/index.json` is an optional style-learning ledger. New profiles initialize it; older profiles without it remain valid and create it only after the user confirms the first learning operation. Its lesson files may store article ID, draft/final SHA256, confirmation time, and compact writing rules. They must not store article bodies, excerpts, absolute paths, credentials, or copies of Cheat state.

## Public account.json

Required keys are `schema_version`, `account_id`, `mode`, `profile_docs`, `created_at`, and `updated_at`. `schema_version` is `1.0`. The official `profile_adapter` writes `mode: "new"` for a created profile and `mode: "imported"` for an imported profile. A generic producer may instead record a custom mode only when it is a non-empty portable label: it must not contain a machine path, credential, or secret.

A Cheat-backed account uses `cheat_binding: "primary"` and relative source names under `cheat_sources`.

## Portable path rules

Every public path or source reference, including `profile_docs`, `cheat_sources`, and history `source_ref` values, MUST be a non-empty POSIX path relative to the profile or its logical source. It uses `/`, may not contain a `..` component, and may not be absolute. Windows drive paths, UNC paths, root-relative paths, and any value containing a Windows backslash (`\`) are rejected.

## Local bindings

`bindings.local.json` resolves logical binding names to local directories. It is never exported and must be ignored by Git. The importer may write it only after explicit approval.

## Source-of-truth rules

- Cheat `rubric_notes.md` remains the rubric source.
- Cheat `candidates.md` remains the candidate source.
- Cheat `predictions/` remains the prediction and retro source.
- The portable profile stores references, not snapshots of changing Cheat content.
- `voice.md` remains the confirmed account voice. Generated learning blocks in `content-patterns.md` may refine future execution but may not silently rewrite `voice.md`.

These four entries are **live-linked** through `cheat_binding`; `.cheat-state.json`, `rubric_notes.md`, `candidates.md`, and `predictions/` are never copied into the profile. At runtime the orchestrator resolves the ignored local binding, invokes root `cheat-on-content` for the required status or workflow, and reads the current source-of-truth semantics. This prevents a copied state snapshot from drifting away from the Cheat project.

`profile_adapter.py preview` reports copyable profile documents under `mapped` and changing Cheat sources under `live_linked`. The latter must match `account.json.cheat_sources` after import.

## Sanitization markers

`[local-path]` and `[local-source]` are final sanitization markers showing that machine-local material was intentionally removed during import. They are not unresolved placeholders and do not make a portable profile incomplete.

## Import safety

Import begins with a read-only preview. `profile_adapter` preview returns `requires_cheat_status_check`; it does not call Cheat or establish schema compatibility. Before import, the orchestrator MUST invoke `cheat-on-content` status for the source and successfully resolve a compatible state. If status is unresolved or incompatible, the orchestrator MUST NOT run import. The adapter's `approved` flag authorizes its local write only and never substitutes for the mandatory status check.

If Cheat reports an incompatible schema, migration requires separate explicit approval in the source project or in a copied working project. After migration, the orchestrator must obtain a compatible Cheat status before import. Authentication folders, secrets, caches, and absolute paths are excluded.

## Timestamp format

The official profile writer emits `created_at` and `updated_at` as timezone-aware ISO 8601 strings at second precision, for example `2026-07-11T14:30:00+08:00`. This is a schema contract even where the current helper or validator does not automatically enforce it.
