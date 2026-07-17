# Publishing Contract

## Manual delivery only

The only delivery route is `html_ready`: deliver verified HTML, a browser preview, the final Markdown, and the single verified `21:9` WeChat main cover for the user to copy into the WeChat editor manually. Manual delivery requires no account credentials.

Set `html_ready` only after the complete HTML gate in `quality-gates.md` passes. This status does not mean that a draft was uploaded or that the article is public.

Do not invoke `wechat-publisher`, another draft adapter, the WeChat Official Account API, or any automatic publishing interface. Do not request, inspect, or store WeChat application credentials, IP allowlist settings, draft identifiers, cookies, or tokens. If the user asks for automatic draft upload, explain that this workflow intentionally supports manual copy only.

## `publish.json` states

Only these statuses are valid:

| Status | Meaning |
|---|---|
| `html_ready` | Verified HTML and preview are ready for manual copy. No draft upload or public publication is implied. |
| `publicly_published` | The user explicitly confirmed that the article is publicly available. Record the public URL when known. |

Do not infer `publicly_published` from HTML delivery, elapsed time, a screenshot, or an assumed manual action. Transition only after the user explicitly confirms public availability.

The transition to `publicly_published` MUST invoke root `cheat-on-content` and use its `cheat-publish` route. Do not simulate registration or reproduce the protocol. Do not mark the publish workflow stage `completed` until that mandatory call succeeds.

If the article is already public but Cheat is missing or registration fails, keep `publish.json.status` truthfully set to `publicly_published`, set `article-state.json.stage_status.publish` to `failed`, report the blocker, and retry only the Cheat registration during recovery. Never upload, republish, or modify the public article from this workflow.
