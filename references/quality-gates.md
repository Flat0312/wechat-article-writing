# Quality Gates

## Runtime dependency gate

Before every stage that requires Cheat, run the matching dependency check from the installed `SKILL_ROOT`. If the dependency check exits with code 2 or reports `ok: false`, the orchestrator MUST stop before invoking or simulating Cheat. It must report `missing_required` and may not substitute a guessed score, recommendation, prediction, status, publish record, retro, persona, or rubric change. A passing dependency check proves only that the Skill is installed; the orchestrator must still invoke root `cheat-on-content` and follow its selected workflow.

## Fact gate

Classify claims as user-provided personal material, stable knowledge, or time-sensitive fact. Preserve user material without inventing missing details. User-provided material supports only what the user said, observed, or experienced; it is not external evidence for a factual claim about an AI model, product, company, market, policy, benchmark, price, release, or other changing subject.

Browse for every time-sensitive factual claim and prefer official documentation, original announcements, primary research, and authoritative databases. Cross-check consequential disputed claims. A time-sensitive AI claim without an external source recorded in the evidence package MUST NOT pass the fact gate. Remove the unsupported assertion, rewrite it explicitly as the author's opinion, or describe it only as an unverified report. Labeling a claim unverified does not turn it into evidence: it may not support a conclusion or appear as a factual number in text or visuals. The fact gate can pass only after the wording no longer asserts that unsupported claim as fact. Do not treat repetition across secondary articles as independent confirmation.

`creator-buddy`, its `gzh-explosive-content-detector` branch, and `aihot` provide topic signals, not final evidence. Before Cheat scoring, normalize their candidates, merge duplicate coverage of the same event, retain every source URL, and record incomplete signal lanes explicitly. Record verified evidence in `research/evidence.md`. Store each external source in the `sources` array in `research/sources.json` with these required fields:

| Field | Required content |
|---|---|
| `title` | Exact source title |
| `url` | Direct canonical URL |
| `source_type` | Such as `official_document`, `original_announcement`, `primary_research`, or `authoritative_database` |
| `access_date` | Access date in `YYYY-MM-DD` form |
| `supported_claim` | The exact article claim or claim identifier supported by the source |

Do not pass the gate while an external factual claim that requires verification lacks a traceable `supported_claim` entry. A source may support only the claim recorded for it; do not stretch it to unrelated conclusions.

## Writing gate

After the fact gate passes, invoke `wechat-content-strategy` before drafting. Require one primary enhancement strategy, one central thesis, distinct section responsibilities, recorded evidence anchors, article-level writing parameters, and 2-3 editing anchors. Every external factual anchor must resolve to `research/sources.json`; every personal anchor must remain within the allowed scope in `research/evidence.md`.

For a long essay, the outline MUST begin with a complete 写前卡片 containing all eight
fields: 真实摩擦、它揭示的机制、读者处境、一句核心判断、主要传播动作（点赞 /
转发 / 收藏，只选一项）、可转发立场、理性段落后的张力恢复点、标题承诺。
If any field is missing, return the gaps to the orchestrator and do not approve the outline or
begin drafting.

Apply `khazix-writer` as the sole author voice to every draft: follow its voice, rhythm, taboo-word list, four-layer self-check, and the article-level parameters in `outline.md`. Parameters may control opening shape, evidence presentation, paragraph cadence, emotional intensity, and closing form; they may not replace the account voice or introduce a separate persona. Preserve the user's confirmed position boundaries. Invoke `humanizer-zh` only after facts and structure stabilize. It may edit wording and rhythm but may not add facts, numbers, experiences, or positions.

Editing anchors belong in the draft as explicit requests for real user judgment, experience, or emotion. Resolve or remove them before final approval; never fill them with invented material.

## Prediction gate

Only an approved final text enters Cheat prediction. The `final` approval MUST be bound to the current final artifact, and `approvals.final.artifact_sha256` MUST equal `artifacts.final.sha256`; otherwise obtain a new user confirmation before prediction. Invoke root `cheat-on-content` for the prediction; do not simulate or approximate it. Do not expose actual performance, retro, audience performance signals, or other prohibited material to the blind scoring route. Never overwrite an immutable prediction.

Before any formal prediction, shadow prediction, or public release, lock exactly one
`primary_action`: `approval`, `forwarding`, `saving`, or `discussion`. The
`prediction-reference.json` receipt MUST record `primary_action`, `locked_at`, and the current
`final_sha256`; its `final_sha256` MUST match the approved final artifact. Missing or inconsistent
fields block prediction and release.

门禁口径：见数据后不改写。
After any post-publication data becomes visible, never backfill or rewrite `primary_action`.
Changing it before publication requires rechecking the outline and final text, then creating a
new immutable prediction version while preserving prior prediction history.

### v2 shadow gate

After the official v1 prediction, a project that explicitly enables v2 shadow may create an
isolated Channel B. Channel B may read only the current approved final and
`reports/rubric-v2-candidate-rules.md`. It MUST NOT read `reports/rubric-v2-candidate.md`,
historical performance, retro, rubric memo, old predictions, article names, or post-publication
feedback.

Lock the shadow result as an independent immutable sidecar before publication data appears. It
must not replace the official v1 prediction, update `.cheat-state.json.rubric_version`, or trigger
a rubric bump by itself. If the project lacks an approved shadow runner or route, block the shadow
step and report the missing route; do not simulate it with an ad hoc model call.

## Visual gate

The cover route produces exactly one static `21:9` WeChat main cover through root `guizang-social-card-skill`. Explicitly suppress its default `1:1` pair output, pair preview, carousel, and Live Photo. Validate exact aspect ratio, Chinese title readability, visual consistency, subject crop, source provenance, and file existence.

Body illustrations remain enabled. Give each body image one independent information job and route each cognitive anchor to Ian or `baoyu-article-illustrator` according to `skill-routing.md`. Validate aspect ratio, Chinese text, readability, visual consistency, insertion position, source provenance, and file existence. Do not create decorative filler or generate both routes for the same anchor unless the user explicitly requests A/B.

Every number, date, ranking, ratio, benchmark, or chart value shown on the cover or in a body illustration MUST use one of these evidence paths:

- An external factual value traces to an entry in the `sources` array in `research/sources.json`, with the exact visual claim covered by `supported_claim`.
- A value from the user's firsthand experience or owned records traces to an explicit `user-material` entry in `research/evidence.md` that records the source person, source material, material date, and the allowed expression scope.

Do not fabricate a URL for user material. Do not generalize a personal or owned-record value into a market, population, product, or other universal fact. Image prompts and generation tools may not invent, estimate, decorate with, or silently alter data. If neither evidence path supports a numeric label within its allowed scope, remove it or replace the body visual with a non-data illustration.

Before selecting the Baoyu route, the final text MUST be recorded and approved against its current SHA256. Run `scripts/baoyu_adapter.py prepare`, pass only `visuals/assets/baoyu/source.md` to the root Skill, then run `scripts/baoyu_adapter.py verify`. Any final-text hash mismatch blocks visual completion.

## HTML gate

Invoke root `gzh-design`. Use WeChat-compatible inline styles. Verify every image reference, image dimension, and required asset. Run the repository article validator and clear every mandatory validator error; also clear every mandatory `gzh-design` error.

HTML completion requires all five non-empty files:

1. `output/article.html`
2. `output/article-preview.html`
3. `output/article-copy.html`
4. `output/article-copy-preview.html`
5. `output/html-qc.md`

Treat `output/article-copy.html` as the manual-paste artifact recorded by
`artifacts.html.path`. Missing any file blocks HTML completion and `html_ready`.

Open `output/article-preview.html` in a browser and inspect at least one narrow viewport no wider than 390 CSS pixels and one regular-width viewport at least 900 CSS pixels wide. At both widths, verify that all images load, text and controls do not overlap, no content is clipped, and there is no unintended horizontal overflow.

After root `gzh-design` creates the copy preview, run
`scripts/upgrade_preview_copy.py output/article-copy-preview.html`. This preserves the original
copy fallback but writes the intended fragment as explicit `text/html` when the browser supports
the Clipboard API, preventing Chromium from flattening block hierarchy during selection-based
copy. A missing or unrecognized `gzhCopy` function blocks the gate; do not silently claim that
the preview was upgraded.

Then click the upgraded preview copy button and paste the intended article body into a clean local `contenteditable` surface or a WeChat-compatible rich-text sandbox. Confirm that the button reports `clipboard-api`; if it reports `legacy-fallback`, record that downgrade and do not assume block hierarchy survived. Inspect the pasted clipboard HTML DOM, not only the preview: verify content hierarchy, required inline styles, link targets, image nodes and sources, content order, and the absence of preview-only controls or labels. If an already-authenticated WeChat editor is available, additionally validate the paste there; do not require a WeChat login or credentials as the default prerequisite. Report the copy method, the two checked widths, the paste target, and the result of each DOM and layout check before marking the stage complete.

Write the two checked widths, image-loading results, copy method, paste target, and each DOM/layout
result to `output/html-qc.md`. Do not mark HTML complete unless all five files exist,
`gzh-design`, deterministic validation, both browser preview checks, and the pasted-DOM inspection
have all passed. Missing `gzh-design` blocks HTML completion; no generic formatter or hand-written
HTML substitutes for this gate.
