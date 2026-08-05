# WeChat publish bridge

The public-publication transition has two independent facts: the user
confirmed that a WeChat article is public, and the root Cheat Skill completed
`cheat-publish`. The total-control bridge accepts a normalized successful Cheat
receipt, then writes the local publication records. It never uploads or
publishes to WeChat.

## Preconditions

- `article-state.json.stage_status.html` is `completed` and `html` is not
  stale;
- the user explicitly confirmed the public URL;
- the normalized Cheat receipt has exactly the relevant success facts:
  `status: "published"`, `platform: "wechat"`,
  `prediction_file: "predictions/<id>.md"`, its `prediction_sha256`, and a
  timezone-aware `published_at`.

The bridge verifies the prediction file bytes against the Cheat receipt before
writing any local publication record. A failed or non-WeChat Cheat receipt,
missing prediction, invalid URL, missing confirmation, or stale HTML is a hard
failure.

## Records and schema

Run the total-control script after the real Cheat call:

```text
python <SKILL_ROOT>/scripts/wechat_publish_bridge.py <ARTICLE_DIR> --cheat-project <CHEAT_PROJECT> --cheat-receipt <CHEAT_RECEIPT.json> --public-url <URL> --published-at <ISO_TIME> --confirmed
```

The script writes `publish.json` with `status: "publicly_published"` and
these bridge fields:

| Field | Meaning |
|---|---|
| `article_dir` | Canonical-workspace-relative article directory |
| `platform` | Always `wechat` |
| `public_url` | Confirmed `https://mp.weixin.qq.com/s/...` URL |
| `published_at` | Public availability time |
| `cheat_prediction_file` | Relative path in the Cheat project |
| `cheat_prediction_sha256` | Hash of that prediction file |
| `cheat_published_at` | Time returned by Cheat publish |
| `metrics_path` | Always `metrics.json` at the article directory root |

It also writes `publish-reference.json`, whose receipt schema adds
`publish_json_sha256` to bind the written `publish.json` bytes. The article
state records the same hash under `artifacts.publish`; no absolute local path
is placed in either portable record.

## WeChat retro input

After publication, manually collected WeChat metrics belong at
`<ARTICLE_DIR>/metrics.json`. The file is the only input location for the
WeChat retro adapter and must preserve the platform as `wechat`, the public URL,
the collection timestamp, and separate reading, likes, shares, comments, and
favorites fields. The publish bridge only records `metrics_path`; it never
invents or copies performance data.
