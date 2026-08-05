# Skill Routing Contract

## Canonical registry

| Skill | Responsibility | Rule |
|---|---|---|
| `cheat-on-content` | Init, topic decision, score, prediction, publish, retro, persona, rubric, benchmark import, migration | Mandatory whenever the stage involves Cheat |
| `cheat-trends` | Configured trend-adapter collection, deduplication, and rough candidate scoring | Mandatory fifth topic-signal lane; invoke through root `cheat-on-content` |
| `creator-buddy` | WeChat hits, competitors, cross-platform topic signals | Topic signal provider |
| `xiaohongshu-skill` | Xiaohongshu keyword heat via local Playwright login (free, no API key) | Default Xiaohongshu route for topic discovery |
| `gzh-explosive-content-detector` | Recent WeChat viral samples, growth signals, headline patterns, niche terms | Mandatory WeChat branch for topic discovery; invoke through `creator-buddy` and preserve its generic-keyword confirmation rule |
| `aihot` | Current AI news | Invoke for AI accounts or AI topics |
| `x-tweet-fetcher` | X/Twitter tweets, threads, long-form articles, and timeline signals via local CLI (no API key) | Mandatory X lane for topic discovery on both long essays and news cards |
| `wechat-article-writing` | First-party drafting, account voice, prose execution and final style gate | Mandatory owner of article drafting; read `references/writing-style.md` |
| `khazix-writer` | Required craft assistant | Must participate after the style card is locked under [`khazix-craft-contract.md`](khazix-craft-contract.md); never the author voice and never import persona, signature, quota or fixed mannerism |
| `humanizer-zh` | Optional AI-pattern diagnostic | Run only after facts, structure and account voice stabilize under [`humanizer-diagnostic-contract.md`](humanizer-diagnostic-contract.md); accept local suggestions selectively and never replace the whole draft |
| `wechat-content-strategy` | Evidence-bound content enhancement, outline, writing parameters, style card and editing anchors | Mandatory after topic/evidence and before first-party drafting |
| `wechat-style-learning` | Confirmed edit learning for long-term profiles | Invoke only on an explicit learn-from-edits request and persist only after confirmation |
| `guizang-social-card-skill` | One 21:9 WeChat main cover | Preferred cover route; explicitly suppress its default 1:1 pair output; ImageGen fallback allowed under cover routing rules |
| `ian-xiaohei-illustrations` | Metaphor, emotion, identity, cognitive turns | Body illustration rail A |
| `baoyu-article-illustrator` | Process, hierarchy, comparison, matrix, timeline, exact labels, evidence-backed data | Body illustration rail B |
| `imagegen` | Optional Codex image Skill | Sanctioned cover fallback (see cover routing rules); discovery hint for body visuals, where each selected route resolves the actual runtime image backend, so absence does not by itself block `visual` |
| `gzh-design` | WeChat HTML, preview, platform validation | Required for HTML completion; accept alias `gzh-design-skill` |

`guizang-social-card-skill` owns cover composition and typography. This orchestrator overrides its general WeChat pair default: generate only the `21:9` main cover, with no `1:1` sharing card, pair preview, carousel, or Live Photo. When suitable photo material is missing, ImageGen may generate the base photo while guizang still composes the typography (material fallback); only when guizang itself is unavailable may ImageGen produce the entire cover end to end (route fallback). Every fallback must be explicitly flagged in the delivery notes and in `visual-plan.md`. Body illustrations remain a separate Ian/Baoyu pipeline.

The lane names, applicability, statuses and candidate fields below are
single-sourced in [`topic-signal-registry.md`](topic-signal-registry.md).

## Intentionally excluded Cheat routes

Do not invoke `cheat-shoot` or `cheat-score-blind` directly from this orchestrator. `cheat-shoot` only belongs to video shooting registration; `cheat-score-blind` must only be invoked internally by Cheat's score, predict, or bump workflow. Topic discovery must invoke root `cheat-on-content` and let it route to `cheat-trends` as the fifth signal lane. Do not simulate these actions from this Skill.

## Excluded capabilities

Do not register or call `hv-analysis`, `space-chart-image`, `article-batch-illustration`, `article-cover-and-batch-illustration`, `baoyu-slide-deck`, `neat-freak`, or `storage-analyzer`. Let `creator-buddy` route its own platform subskills, except that WeChat topic discovery MUST explicitly request its `gzh-explosive-content-detector` branch.

## Topic signal orchestration

Run topic discovery as a fan-in pipeline. Signal providers never make the final topic decision.

1. Run the `creator-buddy-cross-platform` lane through root `creator-buddy` with the mandatory [`creator-buddy-wechat-override.md`](creator-buddy-wechat-override.md) route override. Xiaohongshu keyword heat MUST use the local `xiaohongshu-skill` route (Playwright, free, no API key); do not silently fall back to `xhs-hotnotes`, `global-content-search`, Agent Reach, RedFox, socialdatax, or Guaikei. Use those other routes only for a separately declared details, comments, or creator-history task after the keyword-heat lane is recorded.
2. In the same `creator-buddy` run, explicitly run the `gzh-explosive-content-detector` lane for recent WeChat viral samples. If it classifies the input as a generic keyword, stop and obtain the required expansion choice before continuing the pipeline.
3. For an AI account or AI-related topic, run the `aihot` lane. For other topics, record `not_applicable`; preserve every original URL and treat generated summaries as discovery aids, not verified evidence.
4. Run the `x-tweet-fetcher` lane for long essays and news cards alike: relevant users' timelines, search results, threads, and long-form articles. Save raw output under `news-cards/<slug>/research/x-raw/` (news cards) or the article research folder (long essays), and register each source in the corresponding `sources.json`.
5. Invoke root `cheat-on-content` and let it route to the `cheat-trends` lane, using the account's enabled adapters to add broad trend signals. Treat adapter overlap with `aihot` or `creator-buddy` as duplicate coverage, not independent confirmation.
6. Normalize and deduplicate all five registered lanes before the final Cheat recommendation. Each candidate MUST retain `title`, `source`, `snapshot_text`, `snapshot_at`, and `url` when available. Merge cross-platform coverage of the same event into one candidate while retaining all source records; repeated coverage is not independent confirmation.
7. Submit the normalized pool to root `cheat-on-content`. Use `cheat-recommend` for a populated candidate pool, `cheat-score` for an existing topic or draft, and `cheat-seed` only when no topic or usable pool exists. Cheat owns scoring and ranking.
8. Show Cheat's scored recommendation, rationale, anchors, risks, retained source provenance and all five lane statuses. The topic stage remains `awaiting_confirmation` until the user confirms the topic angle.

If one signal provider fails, report its missing route or runtime requirement and keep its lane visibly incomplete. Do not fabricate results, silently substitute model memory, or present a partial pool as the full set of applicable signal lanes.

## Cheat routes

- Existing account: status check; migrate only with authorization.
- Schema migration: `cheat-migrate` only with explicit authorization or after migration in a copied working project; then re-run root `cheat-status` and require the total-control post-migrate receipt before continuing.
- Benchmark or imported evidence: `cheat-learn-from` for sample-scoped evidence, then obtain separate user confirmation before migrating or importing the sample scope and target Cheat project.
- New long-term account: initialize as `long-essay`.
- No topic: `cheat-seed`.
- Candidate pool choice: `cheat-recommend`.
- Existing topic or draft: `cheat-score`.
- Approved final text: `cheat-predict`.
- Publicly published article: `cheat-publish`.
- Post-publication data: `cheat-retro`.
- Audience refresh: `cheat-persona`.
- Rubric change: `cheat-bump`.
- Progress: `cheat-status`.

For `content_form=long-essay`, prediction additionally requires the total-control
[`cheat-form-contract.md`](cheat-form-contract.md) receipt. A completed root
Cheat call and a compatible WeChat long-essay rubric are separate statuses;
`cheat-predict` must not proceed with an opinion-video-only rubric.

Every init, seed, recommend, score, predict, publish, retro, persona, bump, learn-from, migrate, or status stage MUST invoke the root `cheat-on-content` Skill and let it select its internal workflow. Do not invoke `cheat-score-blind` directly. Do not simulate these actions or reproduce, copy, or approximate its formulas and protocols.

## Content strategy and learning

- Keep `wechat-article-writing` as the ordinary entrypoint and owner of preconditions, state, approvals, and recovery.
- Invoke `wechat-content-strategy` only after the selected topic and evidence package exist. It may write `outline.md` and the article's style card; it may not collect untracked facts, draft the article, or change article state directly.
- Keep `wechat-article-writing` as the drafting owner. Read `references/writing-style.md` before writing, lock the style card, then call `khazix-writer` for bounded craft assistance. Account `voice.md` and validated profile rules define the author voice; article-level parameters refine execution. The assistant must never introduce its own identity, slogans, coarse language, fixed punctuation, fixed word count or fixed ending.
- Invoke `wechat-style-learning` only for a standard long-term profile after the user explicitly requests learning. It may update the optional edit ledger and generated learning blocks in `content-patterns.md`; it may not change `voice.md`, article artifacts, Cheat state, or current approvals.

## WeChat cover routing

Run `python <SKILL_ROOT>/scripts/dependency_check.py --stage cover`, then invoke root `guizang-social-card-skill` with an explicit one-asset contract:

- Produce exactly one static `21:9` WeChat main cover.
- Use the full or near-full article title and one strong visual relationship.
- Do not produce a `1:1` square cover, pair preview, carousel, or Live Photo from the cover route.
- Record title, material source, layout intent, output path, dimensions, and verification result in `visual-plan.md`.
- Account visual rules outrank automatic style suggestions.

After the external route returns, the total Skill must run
`scripts/visual_asset_adapter.py cover` with the route output directory. Only its
`visuals/assets/cover.<ext>` copy and the shared `visuals/assets/manifest.json` are
deliverables; a square/pair/Live Photo companion or a non-`21:9` source fails the
cover route.

Fallback: when suitable photo material is missing, ImageGen may generate the base photo while guizang still composes the typography (material fallback). Only when guizang itself is unavailable may ImageGen produce the entire cover end to end (route fallback). The same one-asset contract applies in both cases, and the fallback must be explicitly flagged in `visual-plan.md` and the delivery notes.

Having no available cover route blocks visual completion. Do not silently replace it with a body-illustration or generic image route, and do not silently fall back without flagging it.

## Dual-rail body illustration routing

For every body cognitive anchor, record route and reason in `visual-plan.md`.

- Choose Ian when the information job is emotion, viewpoint, identity, narrative turn, tension, or an original surreal metaphor and the image does not need exact labels or data.
- Choose `baoyu-article-illustrator` for ordered steps, hierarchy, comparison, matrix, architecture, timeline, exact labels, or evidence-backed numbers.
- Exact semantics outrank mood when readers must recover named relations or values from the image.
- If both jobs matter independently, split them into two anchors. Do not generate both routes for one anchor unless the user explicitly requests A/B.
- If a passage has no independent information job, create no body image for it.
- Profile visual rules outrank automatic recommendations.

After Ian or Baoyu returns, run `scripts/visual_asset_adapter.py body` for every
selected anchor. The adapter is the only accepted copy into
`visuals/assets/ian/` or `visuals/assets/baoyu/`, and its manifest record must
include the route, anchor, information job, dimensions, and SHA256.

Run `python <SKILL_ROOT>/scripts/dependency_check.py --stage visual` before planning. Then run the matching route preflight for each selected anchor: `visual-ian` for Ian, `visual-structured` for Baoyu. Treat `optional_missing: ["imagegen"]` as an informational hint and let the selected route resolve the actual runtime image backend. A missing route Skill or a route that cannot resolve any backend blocks that asset; do not silently substitute a route that changes the information job.

## HTML completion gate

HTML is not complete until root `gzh-design` has produced and validated the WeChat HTML and preview. An alias may resolve the installed Skill name, but it does not weaken this gate.
