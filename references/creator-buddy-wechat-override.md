# Creator-buddy WeChat route override

The total-control Skill owns the evidence policy for WeChat topic discovery.
When it invokes the `creator-buddy-cross-platform` lane, it must pass this
route override to the root `creator-buddy` Skill:

```json
{
  "platform": "xiaohongshu",
  "provider": "xiaohongshu-skill",
  "route": "local-playwright",
  "purpose": "wechat-topic-signal",
  "allow_fallback": false
}
```

For Xiaohongshu keyword heat, the override is mandatory, not a preference.
The route must use the local `xiaohongshu-skill` search flow and preserve the
query, capture time, returned snapshot, and original URLs. Do not use
`skills/xhs-hotnotes`, Agent Reach, `global-content-search`, RedFox,
socialdatax, or Guaikei as a silent fallback for this lane. Those routes may
be used by `creator-buddy` only for a separately declared details, comments,
or creator-history task after the keyword-heat signal is recorded.

The lane receipt must make the selected backend observable:

```json
{
  "lane": "creator-buddy-cross-platform",
  "provider": "xiaohongshu-skill",
  "route": "local-playwright",
  "purpose": "wechat-topic-signal",
  "status": "completed",
  "query": "...",
  "captured_at": "2026-08-05T15:00:00+08:00",
  "sources": []
}
```

`status` may be `completed`, `missing`, or `blocked`. A missing local route
must leave this lane incomplete and must not be presented as a complete
cross-platform signal. A receipt with another provider is not acceptable for
the WeChat topic lane.
