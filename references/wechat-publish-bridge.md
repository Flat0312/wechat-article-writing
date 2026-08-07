# WeChat publish bridge

The public-publication transition has two independent facts: the user
confirmed that a WeChat article is public, and the root Cheat Skill completed
`cheat-publish`. The total-control bridge accepts a normalized successful Cheat
receipt, then writes the local publication records. It never uploads or
publishes to WeChat.

## Preconditions

发布桥按 `article-state.json.schema_version` 分流校验。两条路径都遵守"用户必须明确确认公开"和"prediction 文件哈希与 Cheat 回执一致"两条硬规则；不同之处在于产物 / 完成门禁：

- **schema 1.1 中长文（当前默认）**：`article-state.json.stage_status.final` is `completed`，`final` 审批绑定 `artifact_role=final` 且其 `artifact_sha256` 等于 `artifacts.final.sha256`，`final` 不在 `stale_artifacts`；不要求 `html` 阶段（1.1 项目无 `html` stage）。
- **schema 1.0 历史长文**：`article-state.json.stage_status.html` is `completed` and `html` is not stale。

两条路径的共同前置：

- the user explicitly confirmed the public URL;
- the normalized Cheat receipt has exactly the relevant success facts:
  `status: "published"`, `platform: "wechat"`,
  `prediction_file: "predictions/<id>.md"`, its `prediction_sha256`, and a
  timezone-aware `published_at`.

The bridge verifies the prediction file bytes against the Cheat receipt before
writing any local publication record. A failed or non-WeChat Cheat receipt,
missing prediction, invalid URL, missing confirmation, or schema-specific
stale artifact is a hard failure.

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
