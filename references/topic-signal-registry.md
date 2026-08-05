# Topic signal registry

This is the single source of truth for the WeChat topic-signal lanes. It
applies to both `long-essay` and `news-card`. A single `creator-buddy` call may
fill both its cross-platform lane and its explicit WeChat branch, but the two
lane records stay separate so coverage and missing data remain visible.

There are five registered lanes. `aihot` is an AI-only lane: for a non-AI
account or topic, record `not_applicable` rather than pretending it ran or
silently replacing it with model memory.

| Lane ID | Provider and scope | Applicability | Required route and output |
|---|---|---|---|
| `creator-buddy-cross-platform` | Root `creator-buddy`; cross-platform signals. Xiaohongshu keyword heat uses the local `xiaohongshu-skill` route. | Every topic | Preserve the provider, query scope, capture time, snapshot and original URL. |
| `gzh-explosive-content-detector` | `creator-buddy`'s explicit WeChat branch; viral samples, growth signals and headline patterns. | Every WeChat topic | If the input is classified as a generic keyword, stop for the required expansion choice before continuing. Preserve the branch result and source URL. |
| `aihot` | Root `aihot`; current AI news and product signals. | AI account or AI-related topic only | Preserve the original URL. A summary is discovery input, not verified evidence. |
| `x-tweet-fetcher` | Local X/Twitter CLI; tweets, threads, long-form articles and timeline/search signals. | Every topic | Store raw output under the article research folder or `news-cards/<slug>/research/x-raw/`; register each source in `sources.json`. |
| `cheat-trends` | Root `cheat-on-content` routing to the configured trend adapters. | Every topic | Fifth signal lane for broad trend coverage, deduplication and rough screening; it never replaces the other lanes or final Cheat ranking. |

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
