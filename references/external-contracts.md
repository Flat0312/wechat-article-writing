# External Contracts

## Humanizer diagnostic contract

`humanizer-zh` is an optional diagnostic input after facts, structure, and
account voice stabilize. It must return a local issue list, never a replacement
draft:

```json
{
  "schema_version": "1.0",
  "source_skill": "humanizer-zh",
  "mode": "diagnostic",
  "input_sha256": "<SHA256 of the current draft>",
  "issues": [
    {
      "location": "paragraph:3",
      "pattern": "机械连接词",
      "suggestion": "删去连接词并让因果关系承担转场。",
      "scope": "local",
      "adds_facts": false,
      "changes_meaning": false,
      "severity": "medium"
    }
  ]
}
```

Validate the response against the current draft before applying any change:

```text
python <SKILL_ROOT>/scripts/humanizer_diagnostic_adapter.py <DIAGNOSTIC_JSON> --input <DRAFT>
```

The adapter rejects full-text fields, scores used as approval, missing input
hashes, non-local scope, and suggestions that add facts or change meaning. The
total-control Skill applies the smallest compatible local edit, rechecks facts
and account voice, and records any resulting final-artifact hash change. A
missing humanizer is allowed; the built-in AI-pattern pass remains mandatory.

## gzh-design author CTA override（schema 1.0 历史长文）

> **schema 1.1 中长文不调用本节——不调 `gzh-design`、不写 `output/html-qc.md`。** 本节仅 schema 1.0 项目继续执行以保历史回放。

`gzh-design` normally adds an author placeholder and a generic
"点赞、在看、转发" CTA when the source article has no explicit author. That
default is not part of the WeChat total-control output contract.

When the account has not supplied a name, bio, or CTA preference, pass the
following instruction to `gzh-design` and remove any generated default before
the five project files are finalized:

```text
author_cta: disabled
Do not add an author signature, author placeholder, or generic interaction CTA.
```

When the user has explicitly supplied an author block or CTA, pass
`author_cta: explicit` and preserve only that supplied text. In both cases,
write exactly one of these lines into `output/html-qc.md`:

```text
- author_cta: disabled
```

or:

```text
- author_cta: explicit
```

The article validator rejects missing registration. With `disabled`, it also
rejects `{{作者名}}`, `{{简介}}`, and the default three-action CTA in
`article.html` or `article-copy.html`. A placeholder or generic CTA therefore
cannot silently enter the manual-paste artifact.

## Creator-buddy WeChat route override

The total-control Skill owns the evidence policy for WeChat topic discovery.
When it invokes the `creator-buddy-xiaohongshu` lane, it must pass this
route override to the root `creator-buddy` Skill:

```json
{
  "platforms": ["xiaohongshu", "bilibili", "douyin", "zhihu", "weibo", "toutiao"],
  "provider": "global-content-search",
  "route": "agent-reach-opencli->redfox->guaikei->public-api",
  "purpose": "wechat-topic-signal",
  "allow_fallback": true
}
```

For Xiaohongshu keyword heat, the override is mandatory, not a preference.
The route uses Agent Reach's `OpenCLI` first and then the declared fallback
chain. The selected provider/backend must be recorded; no fallback may be
silent. Credentials are never written into a receipt or cache.

The lane receipt must make the selected backend observable:

```json
{
  "lane": "creator-buddy-xiaohongshu",
  "provider": "global-content-search",
  "route": "agent-reach-opencli->redfox->guaikei->public-api",
  "purpose": "wechat-topic-signal",
  "status": "completed",
  "query": "...",
  "captured_at": "2026-08-05T15:00:00+08:00",
  "sources": []
}
```

`status` may be `completed`, `missing`, or `blocked`. A fallback receipt must
name the actual backend and preserve the original URL. If every route is
unavailable, leave the platform lane as `missing` rather than using memory.

## Offline external contract fixtures

`tests/fixtures/external_contracts.json` is an offline normalized boundary
fixture. It does not call a network service or claim that an external Skill
returned these values in production. It models the input, output path receipt,
and status receipt that the total-control Skill accepts at each seam.

The fixture test covers:

- all nine external Skills used by this workflow;
- the eight topic signal lanes, including the local Xiaohongshu override;
- long-essay Cheat prediction, publish, and retro receipt paths;
- the bounded humanizer response;
- news-card 21:9 cover and (schema 1.0 only) the five HTML delivery files. schema 1.1 中长文不进入此 fixture 的 HTML 端。

When an external Skill changes its real output shape, update the external
Skill and this fixture in the same change review. A fixture passing only proves
that the total-control adapter still rejects/accepts the declared boundary; it
does not replace the mandatory real Skill invocation.

## Visual Asset Manifest（schema 1.0 长文 / news-card 路径）

> **schema 1.1 中长文不读本节、不生成 `visuals/assets/manifest.json`、不调用 `scripts/visual_asset_adapter.py`；其交付以 `final.md` + final 审批绑定为准。** news-card 仍走本节；schema 1.0 历史长文回放亦读本节。

`visuals/assets/manifest.json` is the article project's only delivery index for
the cover and body illustrations. External visual Skills may render into a
temporary output directory, but the article pipeline accepts only the files
copied into `visuals/assets/` by `scripts/visual_asset_adapter.py`.

The manifest is UTF-8 JSON with exactly this top-level shape:

```json
{
  "schema_version": "1.0",
  "article_id": "article-1",
  "cover": null,
  "body": []
}
```

Every asset record contains `asset_id`, `role`, `route`, `delivery_path`,
`source_name`, `sha256`, `width`, `height`, and `aspect_ratio`. `delivery_path`
is a POSIX path below `visuals/assets/`; machine absolute paths never enter the
manifest. Body records also contain `anchor_id` and `information_job`; an
optional `provenance_ref` may be a portable reference or an HTTP(S) URL.

The cover record is singular and must have `asset_id=wechat-cover-21x9`,
`aspect_ratio=21:9`, and one of the `guizang` or `imagegen` routes. The adapter
requires the selected route output directory to contain exactly one static
bitmap and rejects square, pair, carousel, Live Photo, and video artifacts.

Body records use `ian` or `baoyu` as the route. The adapter copies both routes
to `visuals/assets/<route>/...`; the external Skill's default `assets/`, `imgs/`,
or `illustrations/` directory is provenance only, not the article delivery
path.

After all selected assets are registered, record the manifest as the article
state `visuals` artifact so its path and SHA256 are part of the resumable
project state:

```text
python <SKILL_ROOT>/scripts/article_state.py record <PROJECT_ROOT> --role visuals --path visuals/assets/manifest.json
```
