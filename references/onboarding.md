# 初始化协议

## 入口分流

让用户选择或根据上下文判断一条路径：导入账号、创建长期账号或创建临时文章。在路径和目标目录明确前，不得创建文件。

使用以下触发示例与判断规则：

- “从零写一篇公众号文章，主题是……”：用户未要求保留长期账号状态时，视为临时文章。
- “从零初始化一个长期运营的公众号账号”：创建长期账号并调用 Cheat 初始化。
- “导入这个已有账号目录：……”：预览并导入已有账号。
- “继续处理这份 draft：……”：保留用户提供的初稿；若同时给出 profile，则使用该 profile，否则视为临时文章。不得强制退回选题发现阶段。

## Workspace 布局

写入前确认唯一 workspace。便携账号 profile 与单篇文章项目必须分开：

```text
<workspace>/<account_profile>/
<workspace>/<wechat_articles>/<YYYY-MM-DD-slug>/
```

### 规范 workspace 防护

写入前，如果所选 workspace 存在 `START-HERE.md` 和项目治理文件，先读取它们。若项目声明规范根目录和只读备份：

- 所有新 profile、文章状态、预测、发布记录与生成产物只能写入规范根目录；
- 只读备份只能作为恢复或迁移检查的输入；
- 绝不得把备份选作输出目录、向其中写入状态、双向同步或清理它；
- 在 Windows 上，授权写入前先解析绝对路径，并按不区分大小写的方式比较。

只把已经确认位于规范根目录内的目标传给 `wechat-content-strategy` 或 `wechat-style-learning`。

对于导入源，建议使用 `<source-name>-articles` 之类的同级 workspace，但由用户选择。输出不得是导入源、其祖先或其子目录。账号包与文章项目不得写入导入源目录。

## 导入账号

1. 若所给目录已经包含 `account.json`，先验证并直接使用；不得复制出第二份标准 profile。
2. 否则对该目录运行 `profile_adapter.py preview`。
3. 分开展示会复制的 `mapped` 文档与 `live_linked` Cheat 来源。实时链接来源保留在 Cheat 项目中，通过本地 binding 解析；不得复制进便携 profile。
4. 若存在 `.cheat-state.json`，运行 `python <SKILL_ROOT>/scripts/dependency_check.py --stage account`。报告为 `ok: false` 时，必须在 Cheat 状态检查或导入前停止，并报告缺失依赖。
5. 依赖检查通过后，调用根 `cheat-on-content` Skill 检查状态，并把观察到的 schema 与其 migrations registry 比较。未取得兼容的 `cheat-status` 结果前，不得继续 preview 或 import。
   对 benchmark 或导入证据，使用明确的 `cheat-learn-from` 路由，并将其限制在已确认的样本范围与目标 Cheat 项目。需要迁移时，只能在取得单独明确批准后对源项目运行 `cheat-migrate`，或在复制的工作项目中运行；随后再次调用根 `cheat-status`，并按 [`references/cheat-contracts.md`](cheat-contracts.md#post-migrate-cheat-status-receipt) 将结果规范化为 `<账号目录>/cheat-status-receipt.json`。迁移后回执失败或缺失会阻塞导入。
6. 若 schema 不兼容，停止只读导入。仅可在明确批准后提供源项目迁移，或提供工作副本迁移。
7. 展示 `mapped`、`live_linked`、缺失、冲突和排除字段。
8. 仅在批准后运行 `profile_adapter.py import`，且只能写入已确认 workspace 中解析后的 `<account_profile>/` 目录。
9. 使用结果前先验证。

适配器的 `approved` 标志只授权本地写入，绝不替代强制的根 `cheat-on-content` 状态检查，也不能证明 schema 兼容。

绝不得导入 `.auth`、Cookie、API Key、缓存登录状态或秘密文件。preview 和普通 import 期间绝不得更改源目录。

## 创建长期账号

先调用根 `cheat-on-content`，以 `long-essay` 内容形态完成初始化。保留 Cheat 要求的每一项确认。

Cheat 初始化后，只按三个紧凑分组收集公众号专属上下文：

1. 账号身份、创作目标与预期受众。
2. 内容赛道、作者证据、边界与声音。
3. 历史文章、对标、视觉偏好与交付偏好。

汇总完整 profile 草案。只针对矛盾或缺失字段逐次追问一个问题。写入前展示最终 profile；批准后，用已初始化的 Cheat 项目运行 `profile_adapter.py create`，把批准后的回答写入 profile Markdown 文件并验证结果。

初始化空的可选 `history/edits/index.json`，用于将来已确认的改稿学习。初始化期间不得从导入文件推断文风规则；学习需要用户另行明确请求。

## 临时文章

临时模式要求主题明确。它可以在没有持久 profile 的情况下运行调研、写作、编辑、视觉和 HTML 阶段。若用户要求 Cheat 打分、预测、发布登记或复盘，必须提供已有 Cheat 项目，或升级为长期账号模式。绝不得模拟这些动作。

## 学习确认

用户明确要求登记学习时，先展示候选规则；写入账号学习账本前，必须取得单独的用户确认。

## 五类确认

1. 账号导入预览或新 profile。
2. 主题、角度与受众。
3. 提纲、核心主张与事实边界。
4. Cheat 预测和视觉生产前的终稿。
5. 视觉交付：生成前确认方案，排版后确认 HTML。

外部 Skill 自己的强制确认仍然有效。视觉确认按 [`quality-gates.md`](quality-gates.md) 的唯一规则覆盖单张 `21:9` 微信主封面和入选的正文配图方案；本流程明确禁止生成的方形分享卡无需确认。
