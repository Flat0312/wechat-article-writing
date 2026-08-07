# Recovery Rules

## Status model

Every stage uses `pending`, `in_progress`, `awaiting_confirmation`, `completed`, `failed`, `skipped`, or `stale`.

A status-only transition does not invalidate content. After an upstream artifact or its content changes, identify the earliest changed stage, explicitly call `invalidate_from(state, stage)`, and persist `article-state.json` before resuming downstream work. Calling `set_stage` does not replace invalidation.

## Change-to-stage map

| Change | Earliest stage passed to `invalidate_from` | Required recovery |
|---|---|---|
| The theme input, article goal, or target audience in `brief.md` changes | `brief` | Re-run topic selection and rebuild every affected downstream artifact. |
| The confirmed topic angle, topic strategy, or selected topic proposition changes | `topic` | Rebuild evidence and every affected downstream artifact. |
| Evidence, source, factual support, or `research/evidence.md` / `research/sources.json` changes | `evidence` | Recheck facts, then rebuild affected outline, text, prediction, and (for schema 1.0) visuals/HTML/publish/retro. |
| Outline-local thesis, section order, argument structure, or `outline.md` changes without changing the topic | `outline` | Rebuild affected drafts and every downstream artifact. |
| A full body rewrite starts at the draft while approved evidence and outline remain unchanged | `draft` | Rebuild final text, obtain its approval, create a new immutable Cheat prediction version, and rebuild every affected downstream artifact. |
| Any content in `drafts/final.md` changes, including wording-only edits | `final` | Create a new immutable Cheat prediction version; for schema 1.0 projects also recheck image positions and regenerate HTML. |
| `visuals/visual-plan.md` changes (schema 1.0 only) | `visual_plan` | Regenerate affected visual assets and every downstream artifact. |
| A visual asset changes without changing text or the visual plan (schema 1.0 only) | `visuals` | Preserve text and prediction; regenerate and validate HTML and later delivery records. |

If one edit spans multiple rows, use the earliest applicable stage. For example, correcting an external fact in both the evidence package and final text invalidates from `evidence`, not from `final`. A change to the brief's goal or target audience invalidates from `brief`; a change only to the confirmed topic angle or strategy invalidates from `topic`; an outline-only structural change invalidates from `outline`. schema 1.1 projects (no `visual_plan` / `visuals` / `html` stages) only invalidate `prediction`, `publish`, and `retro` from `final`.

## Stale propagation

- A brief theme, article goal, or target-audience change calls `invalidate_from(state, "brief")` and invalidates topic selection plus every later stage.
- A confirmed topic angle or topic-strategy change calls `invalidate_from(state, "topic")` and invalidates evidence, outline, drafts, prediction reference, and (for schema 1.0) visual plan, visuals, HTML, publish, and retro.
- Fact or structural change in final text invalidates the fact gate, prediction, and (for schema 1.0) visual plan, visuals, HTML, publish, and retro. Recovery must continue through every previously completed downstream stage; in schema 1.0 it cannot stop after regenerating HTML.
- Wording-only final-text change is still a final-content change: call `invalidate_from(state, "final")`, obtain a newly versioned prediction, and (for schema 1.0) regenerate HTML. Any completed publish and retro work also becomes stale. Do not reuse an old prediction merely because the meaning appears unchanged, and (for schema 1.0) do not stop recovery at HTML.
- Image-only change preserves text and prediction; call `invalidate_from(state, "visuals")` and rerun HTML layout and validation (schema 1.0 only). Any completed publish and retro work becomes stale and must be recovered after the new HTML is approved.
- Visual-plan change calls `invalidate_from(state, "visual_plan")`; visuals, HTML, completed publish work, and completed retro work become stale (schema 1.0 only). Do not treat it as an image-only replacement or stop recovery at HTML.
- An immutable Cheat prediction is never edited or overwritten. Keep `create_new_prediction_version`, invoke root `cheat-on-content` under its protocol, and retain all earlier prediction versions.

When the affected article was already public, a changed local artifact does not update the public article. Complete the required external update or republish operation, obtain explicit user confirmation that the changed version is public, and record its current public URL when known. Then invoke root `cheat-on-content` through `cheat-publish` for the changed public version. Never reuse the old publication registration. Recover retro only from performance data for that confirmed public version.

`invalidate_from` marks completed downstream work and recorded downstream artifacts stale while preserving incomplete downstream statuses that have no artifact. The downstream set is schema-aware: schema 1.1 invalidates from `final` only `prediction`, `publish`, `retro`; schema 1.0 also invalidates `visual_plan`, `visuals`, and `html`. It clears approvals keyed to the changed or a downstream stage and approvals bound to artifacts in that range, while preserving earlier unaffected approvals. After rebuilding one role, call `record_artifact` for that role. Re-recording different bytes clears every approval bound to that role; re-recording the same SHA256 preserves them. Re-recording also clears only that role's stale artifact marker and marks that role completed; it does not clear or validate any unrecovered downstream role. The current final artifact must be approved again before prediction, and the approval hash must equal the current final artifact hash. The orchestrator may re-record `prediction`, thereby clearing `create_new_prediction_version`, only after the mandatory Cheat call has produced and preserved the new external version. Continue recovery until every affected downstream stale marker has been regenerated and validated.

## Failure policy

- Incomplete profile import: report missing fields and continue only after they are resolved or explicitly accepted.
- Unsupported fact: remove it, rewrite it as opinion, or label it unverified before final text. A time-sensitive AI claim without an external source cannot pass the fact gate.
- Missing `cheat-on-content`: block every related init, seed, recommend, score, predict, publish, retro, persona, bump, or status stage. Do not simulate, approximate, or locally reproduce Cheat output.
- Missing other Skill: continue only if the routing contract has a legitimate available route, and record the downgrade.
- Missing `gzh-design` (schema 1.0 only): block HTML generation, validation, preview completion, and HTML delivery. There is no generic fallback route for the HTML gate.
- 21:9 cover or body-illustration failure (schema 1.0 / news-card only): preserve the prompt and failure record; do not mark visual delivery complete.
- HTML failure (schema 1.0 only): preserve valid upstream artifacts and block HTML completion.
- schema 1.1 long-essay missing `final.md` / `final` approval / non-stale / user confirmation: block `publish.json.status=publicly_published`; do not infer publication from any other signal.
- Public article with failed Cheat registration: keep `publish.json.status` as `publicly_published`, set the article publish stage to `failed`, and retry root `cheat-on-content` registration without uploading or publishing again.
- Interruption: retain valid artifacts and resume from the nearest valid checkpoint. Apply the change-to-stage map before trusting downstream work.

## Learned style rules

A confirmed edit-learning record is account-level guidance for future articles. Recording, promoting, or decaying such a rule does not modify the current article and therefore does not invalidate its approved artifacts, prediction, visuals, HTML, or publication state. If a user explicitly asks to apply a newly learned rule to the current article, treat that as a requested content edit and invalidate from the earliest stage actually changed under the map above.

## Source import safety

Preview is read-only. Cheat migration modifies a project and therefore requires explicit authorization. Prefer a copied working project when the user wants to preserve the source unchanged. Never modify a source account during recovery unless the user explicitly authorizes the exact migration target.
