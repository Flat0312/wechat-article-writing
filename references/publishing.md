# 发布契约

## 仅人工交付

唯一交付路线是 `html_ready`：交付通过 `quality-gates.md` 的 HTML 包、最终 Markdown 和视觉资产，由用户手工复制到公众号编辑器。人工交付不需要任何账号凭据。

只有 `quality-gates.md` 的完整 HTML 门禁通过后，才可设置 `html_ready`。此状态不表示草稿已经上传，也不表示文章已经公开。

不得调用 `wechat-publisher`、其他草稿适配器、微信公众号 API 或任何自动发布接口。不得请求、检查或存储微信公众号应用凭据、IP 白名单设置、草稿标识符、Cookie 或 Token。若用户要求自动上传草稿，应说明本流程有意只支持人工复制。

## `publish.json` 状态

只允许以下状态：

| 状态 | 含义 |
|---|---|
| `html_ready` | 已验证的 HTML 和预览可供人工复制；不表示草稿已上传或文章已公开。 |
| `publicly_published` | 用户明确确认文章已经公开；已知时记录公开 URL。 |

不得根据 HTML 交付、时间流逝、截图或对人工动作的推测认定 `publicly_published`。只有用户明确确认公开可访问后才可转换状态。

转换为 `publicly_published` 必须（MUST）调用根 `cheat-on-content` 并使用其 `cheat-publish` 路由。不得模拟登记或复现协议；该强制调用成功前，不得把发布流水线阶段标记为 `completed`。

若文章确已公开，但 Cheat 缺失或登记失败，仍应如实保持 `publish.json.status` 为 `publicly_published`，将 `article-state.json.stage_status.publish` 设为 `failed`，报告阻塞，并在恢复时只重试 Cheat 登记。本流程绝不得上传、重新发布或修改公开文章。

根 `cheat-publish` 成功后，将其规范化回执传给
[`references/wechat-publish-bridge.md`](wechat-publish-bridge.md)。该 bridge
写入 `publish.json`，在 `publish-reference.json` 和文章状态的 `publish` 产物中记录其 SHA256，并把公众号复盘输入固定为 `metrics.json`。它不调用任何上传或发布 API。
