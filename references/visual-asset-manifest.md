# Visual Asset Manifest

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
