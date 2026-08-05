# Quality Gates

## Runtime dependency gate

Before every stage that requires Cheat, run the matching dependency check from the installed `SKILL_ROOT`. If the dependency check exits with code 2 or reports `ok: false`, the orchestrator MUST stop before invoking or simulating Cheat. It must report `missing_required` and may not substitute a guessed score, recommendation, prediction, status, publish record, retro, persona, or rubric change. A passing dependency check proves only that the Skill is installed; the orchestrator must still invoke root `cheat-on-content` and follow its selected workflow.

Before trusting any resumable project checkpoint, run
`python <SKILL_ROOT>/scripts/validate_project.py article <PROJECT_ROOT>`. The
validator must rehash every recorded artifact and compare every artifact-bound
approval before a downstream stage is allowed to rely on the state file.

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

Read `references/writing-style.md` before drafting. `wechat-article-writing` owns the draft, and the account `voice.md` plus validated profile rules define the author voice. Require a complete style card in `outline.md`; it must select the relevant stable rules, article-specific prose goals, optional provisional experiment, optional final-observation candidate, forbidden habits, preserved user expressions, opening action and closing return. Do not start drafting while the card is missing or generic.

External writing Skills are never the author identity. After the style card is locked, call `khazix-writer` as a required bounded craft assistant for structure, scene, analogy, rhythm and self-check suggestions; do not import its persona, slogans, coarse language, punctuation bans, fixed word count, fixed structure, signature or fixed ending. The total draft must be rewritten and integrated by the account voice. Preserve the user's confirmed position boundaries and do not use quotas for colloquial phrases, fragments, rhetorical questions or quotable lines.

After facts and structure stabilize, run the prose, account-voice, AI-pattern and voice-regression passes from `references/writing-style.md`. `humanizer-zh` is optional diagnostic input only: obtain a problem list, apply the smallest compatible edits, and reject any whole-draft rewrite or suggestion that adds facts, numbers, experiences, positions or synthetic personality. Final approval requires all seven prose checks in that reference to pass.

Editing anchors belong in the draft as explicit requests for real user judgment, experience, or emotion. Resolve or remove them before final approval; never fill them with invented material.

### 微信长文排版契约

排版契约的 8 条规则（3 文本级 + 5 视觉级）已抽到独立文档
[`references/wechat-layout-contract.md`](wechat-layout-contract.md)。在
`wechat-article-writing` 调用 `gzh-design` 时，将本节作为不可选的上位约束传入；
主题组件与契约冲突时省略该组件或改用更简洁的兼容组件。

`output/html-qc.md` 的"9 项排版检查"段按契约文档逐项记录复核结果；若只能通过
改动正文文字才能修复，按 `recovery-rules.md` 从 `final` 阶段失效并重新完成审批及
下游流程；不得在已批准正文或已锁定预测之后静默改字。

## Prediction gate

Only an approved final text enters Cheat prediction. The `final` approval MUST be bound to the current final artifact, and `approvals.final.artifact_sha256` MUST equal `artifacts.final.sha256`; otherwise obtain a new user confirmation before prediction. Invoke root `cheat-on-content` for the prediction; do not simulate or approximate it. Do not expose actual performance, retro, audience performance signals, or other prohibited material to the blind scoring route. Never overwrite an immutable prediction.

For the long-essay path, create the Cheat-compatible script through
[`references/cheat-prediction-bridge.md`](cheat-prediction-bridge.md). The
adapter is the only supported copy from `drafts/final.md` into Cheat's
`scripts/` input namespace; a missing or mismatched approval hash must fail
before any snapshot is written. `prediction-input-reference.json` is only an
input receipt and never substitutes for the real `cheat-predict` call.

When the root Cheat route returns a Channel B JSON response, validate it before
the parent route calculates `composite` or writes prediction data:

```text
python <SKILL_ROOT>/scripts/blind_score_adapter.py validate <BLIND_JSON> <RUBRIC_NOTES> --script <CHEAT_PROJECT>/scripts/<id>.md
```

The validator derives `rubric_version` and the exact 7/9 dimension set from the
current rubric, checks every per-dimension field, and optionally recomputes the
12-character script hash prefix. A failure is a prediction gate failure; do not
fill missing dimensions, accept a different rubric version, or calculate a
composite from an unvalidated response. See
[`references/blind-score-contract.md`](blind-score-contract.md).

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

启用 v2 影子打分的项目在 v1 预测后、看到实绩前，可以对当前已批准终稿跑一次隔离的
Channel B 影子打分。该打分**只**为 bump 积累 v2 证据，不得替代、修改或触发现役 v1。

**调用入口**：根 `cheat-on-content` 的 `cheat-predict --blind-rescore` 模式。
v1.4+ 起该模式支持 `--rubric <path>` 指定替代 rubric 文件。v2 影子必须传：

```
cheat-predict --blind-rescore \
  --prediction-file <prediction_file> \
  --rubric reports/rubric-v2-candidate-rules.md
```

**Channel B 隔离协议**（与 [cheat-score-blind](../cheat-on-content/../skills/cheat-on-content/skills/cheat-score-blind/SKILL.md) 一致）：

- **允许读**：`scripts/<id>.md` + `reports/rubric-v2-candidate-rules.md`（v2 候选规则正文）
- **禁止读**：`reports/rubric-v2-candidate.md`（v2 候选证据档，含实绩）、历史
  `predictions/*.md` 的复盘段、`rubric-memo.md`、`.cheat-state.json` 历史字段、
  `videos/*/report.md`、老预测、文章名、发布后评论

**落盘**：sidecar 写到 `.cheat-cache/blind-rescores/<id>.json`（v1.4+ 统一路径），
`trigger: "blind_rescore"`，`rubric_version` 标注为 `v2-candidate`。该 sidecar **不**
覆盖 v1 retro Phase 5.5 的 `retro_shadow` 触发（若 T+2 retro 尚未跑，新 sidecar
优先级最高）。

**边界**：
- **不**替代 v1 预测
- **不**改 `.cheat-state.json.rubric_version`（仍为 v1）
- **不**单独触发 rubric bump（bump 须走完整 5 步协议）
- 缺失 `cheat-on-content` 或缺失 `reports/rubric-v2-candidate-rules.md` → 阻塞影子
  步骤并报告缺失路由；**不**用 ad hoc model call 模拟

**v2 候选证据积累**：`bump --propose` 落地前累计 ≥3 篇同向 v2 shadow 即可作为 bump
候选。v2 shadow 与 v1 retro shadow 的 sidecar 共用 `.cheat-cache/blind-rescores/`，
`trigger` 字段区分。

## Visual gate

The cover route produces exactly one static `21:9` WeChat main cover through root `guizang-social-card-skill`. Explicitly suppress its default `1:1` pair output, pair preview, carousel, and Live Photo. When suitable photo material is missing, ImageGen may generate the base photo while guizang still composes the typography (material fallback); only when guizang itself is unavailable may ImageGen produce the entire cover end to end under the same one-asset contract (route fallback). Every fallback must be explicitly flagged in `visual-plan.md` and the delivery notes. Pass the external route output through `scripts/visual_asset_adapter.py cover`; it rejects any forbidden companion output, requires exactly one static bitmap, and verifies the `21:9` ratio before copying to `visuals/assets/cover.<ext>`. A route that fails this adapter is unavailable for the article and cannot be silently treated as a successful single-cover run.

Body illustrations remain enabled. Give each body image one independent information job and route each cognitive anchor to Ian or `baoyu-article-illustrator` according to `skill-routing.md`. After generation, run `scripts/visual_asset_adapter.py body` and accept only the copied file under `visuals/assets/ian/` or `visuals/assets/baoyu/`; the shared `visuals/assets/manifest.json` is the delivery index. Validate aspect ratio, Chinese text, readability, visual consistency, insertion position, source provenance, and file existence. Do not create decorative filler or generate both routes for the same anchor unless the user explicitly requests A/B.

Every number, date, ranking, ratio, benchmark, or chart value shown on the cover or in a body illustration MUST use one of these evidence paths:

- An external factual value traces to an entry in the `sources` array in `research/sources.json`, with the exact visual claim covered by `supported_claim`.
- A value from the user's firsthand experience or owned records traces to an explicit `user-material` entry in `research/evidence.md` that records the source person, source material, material date, and the allowed expression scope.

Do not fabricate a URL for user material. Do not generalize a personal or owned-record value into a market, population, product, or other universal fact. Image prompts and generation tools may not invent, estimate, decorate with, or silently alter data. If neither evidence path supports a numeric label within its allowed scope, remove it or replace the body visual with a non-data illustration.

Before selecting the Baoyu route, the final text MUST be recorded and approved against its current SHA256. Run `scripts/baoyu_adapter.py prepare`, pass only `visuals/assets/baoyu/source.md` to the root Skill, then run `scripts/baoyu_adapter.py verify`. Any final-text hash mismatch blocks visual completion.

## HTML gate

Invoke root `gzh-design` with the 微信长文排版契约 above as an explicit hard constraint. Use WeChat-compatible inline styles. Verify every image reference, image dimension, and required asset. Run the repository article validator and clear every mandatory validator error; also clear every mandatory `gzh-design` error.

HTML completion requires all five non-empty files:

1. `output/article.html`
2. `output/article-preview.html`
3. `output/article-copy.html`
4. `output/article-copy-preview.html`
5. `output/html-qc.md`

Treat `output/article-copy.html` as the manual-paste artifact recorded by
`artifacts.html.path`. Missing any file blocks HTML completion and `html_ready`.
The repository validator also requires all five files to contain non-whitespace UTF-8
text, a `<section>...</section>` pair in `article.html`, the expected HTML/copy controls
in `article-copy-preview.html`, and a Markdown heading, `output/article.html` reference,
and validation record in `html-qc.md`.

Open `output/article-preview.html` in a browser and inspect at least one narrow viewport no wider than 390 CSS pixels and one regular-width viewport at least 900 CSS pixels wide. At both widths, verify that all images load, text and controls do not overlap, no content is clipped, and there is no unintended horizontal overflow.

After root `gzh-design` creates the copy preview, run
`scripts/upgrade_preview_copy.py output/article-copy-preview.html`. This preserves the original
copy fallback but writes the intended fragment as explicit `text/html` when the browser supports
the Clipboard API, preventing Chromium from flattening block hierarchy during selection-based
copy. The upgrade must also make local images portable in the clipboard payload: before the
copy gate, verify that every local `<img>` source in the copy preview is embedded as
`data:image/...` (or another resource form proven to survive the target paste) and that no
`../visuals/...` path remains in the clipboard HTML. A missing or unrecognized `gzhCopy`
function blocks the gate; do not silently claim that the preview was upgraded.

Then click the upgraded preview copy button and paste the intended article body into a clean local `contenteditable` surface or a WeChat-compatible rich-text sandbox. Confirm that the button reports `clipboard-api`; if it reports `legacy-fallback`, record that downgrade and do not assume block hierarchy survived. Inspect the pasted clipboard HTML DOM, not only the preview: verify content hierarchy, required inline styles, link targets, image nodes and sources, content order, and the absence of preview-only controls or labels. If an already-authenticated WeChat editor is available, additionally validate the paste there; do not require a WeChat login or credentials as the default prerequisite. Report the copy method, the two checked widths, the paste target, and the result of each DOM and layout check before marking the stage complete.

Write the two checked widths, image-loading results, copy method, paste target, each DOM/layout
result, and all nine 微信长文排版契约 results to `output/html-qc.md`. Do not mark HTML complete unless all five files exist,
`gzh-design`, deterministic validation, both browser preview checks, and the pasted-DOM inspection
have all passed. Missing `gzh-design` blocks HTML completion; no generic formatter or hand-written
HTML substitutes for this gate.

`output/html-qc.md` 的结构按 [`assets/article-project-template/output/html-qc.template.md`](../assets/article-project-template/output/html-qc.template.md)：
- 五件套存在性
- gzh-design 调用记录
- 9 项排版契约（3 文本级 + 5 视觉级 + final.md SHA256 绑定）
- 浏览器视口检查（≤390 / ≥900）
- 复制与粘贴（`clipboard-api` / `legacy-fallback` + pasted DOM）
- validate_project 与确定性校验
- final.md SHA256 一致性
- 阻塞原因（如有）

每项标 ✅ / ❌；❌ 项必须给具体复现路径。
