# Topic signal registry

This is the single source of truth for the WeChat topic-signal lanes and their
orchestration. It applies to both `long-essay` and `news-card`. A single
`creator-buddy` call may fill several platform lanes and its explicit WeChat
branch, but every lane record stays separate so coverage and missing data
remain visible.

There are eight registered lanes. `aihot` is an AI-only lane: for a non-AI
account or topic, record `not_applicable` rather than pretending it ran or
silently replacing it with model memory. Each platform lane records its actual
backend and may be `missing` when the public route or local read-only CLI is
unavailable.

| Lane ID | Provider and scope | Applicability | Required route and output |
|---|---|---|---|
| `creator-buddy-xiaohongshu` | Root `creator-buddy` → `global-content-search`; OpenCLI first, then declared RedFox/Guaikei fallback. | Every topic | Preserve provider, actual backend, query, capture time, snapshot and original URL. |
| `gzh-explosive-content-detector` | `creator-buddy`'s explicit WeChat branch; viral samples, growth signals and headline patterns. | Every WeChat topic | If the input is classified as a generic keyword, stop for the required expansion choice before continuing. Preserve the branch result and source URL. |
| `aihot` | Root `aihot`; current AI news and product signals. | AI account or AI-related topic only | Preserve the original URL. A summary is discovery input, not verified evidence. |
| `creator-buddy-bilibili` | Root `creator-buddy` → `global-content-search`; bili-cli, OpenCLI or B站 public API. | Every topic | Preserve actual backend and original video URL; public API limitations are `missing` when applicable. |
| `creator-buddy-douyin` | Root `creator-buddy` → `global-content-search`; OpenCLI `douyin search`, then configured `DOUYIN_COMMAND`. | Every topic | Preserve actual backend and original video URL; login/risk-control failures are `missing`. |
| `creator-buddy-zhihu` | Root `creator-buddy` → `global-content-search`; OpenCLI `zhihu search`, then declared public route. | Every topic | Preserve backend, auth status and original URL; missing Zhihu login is `missing`. |
| `creator-buddy-weibo` | Root `creator-buddy` → `global-content-search`; OpenCLI search, then read-only hot-search filtering. | Every topic | Filter to the account topic, preserve actual backend and source URL; access failures are `missing`. |
| `creator-buddy-toutiao` | Root `creator-buddy` → Toutiao public hot-board API. | Every topic | Preserve hot-board URL, capture time and source item URL. |

`cheat-trends` is not a WeChat topic-signal lane and is not a required WeChat
topic preflight dependency. Do not invoke or register it from this Skill.

## Orchestration

1. Run `python <SKILL_ROOT>/scripts/dependency_check.py --stage topic`; use
   `topic-ai` for an AI account or AI-related topic.
2. Run every applicable lane in the table. Apply
   [`external-contracts.md`](external-contracts.md#creator-buddy-wechat-route-override) to
   creator-buddy routes and record the actual backend. If the WeChat branch
   classifies a generic keyword, set that
   lane to `blocked` and wait for the required expansion choice.
3. Record non-AI `aihot` as `not_applicable`. Record unavailable runtimes or
   provider failures as `missing`; continue the remaining lanes and never
   replace a missing result with model memory.
4. Normalize and deduplicate the candidate pool. Merge coverage of the same
   event while retaining every source record; repeated coverage is not
   independent confirmation. Topic signals are discovery input, not verified
   factual evidence.
5. Submit the normalized pool to root `cheat-on-content`: use
   `cheat-recommend` for a populated pool, `cheat-score` for an existing topic
   or draft, and `cheat-seed` only when neither a topic nor a usable pool
   exists. Signal providers and this Skill never score or rank in Cheat's
   place.
6. Write all lane statuses, normalized candidates, duplicate merges, Cheat
   receipt, rationale, anchors and risks to `topic-brief.md`. Keep the topic
   stage `awaiting_confirmation` until the user confirms the angle; never
   present a partial pool as complete coverage.

### Xiaohongshu route commands

Use `creator-buddy` → `global-content-search` under the mandatory override.
Run `agent-reach doctor --json` and, when the workspace provides it,
`python tools/topic_signal_sources.py doctor`; preserve the actual backend and
auth state. From the `global-content-search` directory:

```text
node src/xiaohongshu/search-cli.js --platform xiaohongshu --keyword "<关键词>" --limit 10
node src/xiaohongshu/detail-cli.js --platform xiaohongshu --url "<完整小红书链接>" --limit 100
```

Store JSON or Markdown under `<wechat_image_posts>/<slug>/research/`, preserve
the full link including `xsec_token`, and register sources in
`research/sources.json`.



## Lane status

Each `topic-brief.md` records one row for every lane with exactly one of these
statuses: `pending`, `completed`, `missing`, `not_applicable`, or `blocked`.
`missing` records an unavailable runtime or provider failure. `blocked` is
reserved for a provider rule such as the generic-keyword confirmation. The
candidate pool must retain the lane status, source records, and duplicate
merges before it is sent to Cheat.

Every candidate retains `title`, `source`, `snapshot_text`, `snapshot_at`, and
`url` when available. Cross-lane coverage of the same event is one candidate
with multiple source records, not independent confirmation. Signal lanes find
and shape candidates; root `cheat-on-content` owns scoring, ranking and the
final topic decision.
