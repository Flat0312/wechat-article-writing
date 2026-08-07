## 第三步：建立状态

### 导入账号

1. 如果目录已有标准 `account.json`，先运行 `python <SKILL_ROOT>/scripts/validate_project.py profile <账号目录>`；验证通过后直接使用，不重新导入。
2. 否则运行 `python <SKILL_ROOT>/scripts/profile_adapter.py preview <源目录>`。
3. 检测到 Cheat 项目时，真实调用 `cheat-on-content` 检查状态和 schema 兼容性。
4. schema 不兼容时停止只读导入，取得授权后才在源项目或工作副本迁移。
5. 若执行了 `cheat-migrate`，再次真实调用根 `cheat-status`，按
   [`references/cheat-contracts.md`](../cheat-contracts.md#post-migrate-cheat-status-receipt) 生成并验证
   `<账号目录>/cheat-status-receipt.json`；回执缺失或失败时停止导入。
6. 展示映射、缺失、冲突和排除项。
7. 用户批准后运行 `python <SKILL_ROOT>/scripts/profile_adapter.py import <源目录> <账号目录> --approved`。
8. 再运行 `python <SKILL_ROOT>/scripts/validate_project.py profile <账号目录>` 验证结果。

预览必须把会复制的 `mapped` 文档与保持在源项目中的 `live_linked` Cheat 来源分开展示。`.cheat-state.json`、rubric、候选池和预测记录通过本机 binding 实时解析，不复制成会漂移的快照。

`--approved` 只授权适配器的本地写入，不能替代 Cheat 状态检查。公开账号包只保存逻辑绑定和相对引用；机器绝对路径只能进入被忽略的 `bindings.local.json`。账号包与单篇文章项目使用 `references/onboarding.md` 的独立 workspace 布局，不得写入导入源目录。

### 新建长期账号

先调用 `cheat-on-content` 初始化 `long-essay` 项目并完成其全部问题。再按 `references/onboarding.md` 分组收集公众号定位、受众、文风、内容边界、对标和视觉偏好，只对缺失或矛盾字段逐项追问。用户确认画像后，运行：

```text
python <SKILL_ROOT>/scripts/profile_adapter.py create <账号目录> --account-id <ID> --cheat-project <Cheat项目> --approved
python <SKILL_ROOT>/scripts/validate_project.py profile <账号目录>
```

把已确认答案写入对应 Markdown，再验证标准账号包。

### 临时创作

用户必须给出明确主题。临时模式不生成长期账号包；一旦请求 Cheat 能力，要求选择现有 Cheat 项目或升级到长期账号。不得模拟 Cheat 输出。

### 贴图轻量项目

当 `content_kind=news-card` 时，用户界面统一称“贴图”；新闻、资讯、观点梗、截图和
其他图片主体内容不再划分子类。`news-card` 仅是兼容机器字段。贴图不调用
`article_state.py init`，不进入 long-essay 的 12 阶段状态、正式 v1 预测或 rubric
变更流程，只在 canonical 工作区建立独立贴图目录。

普通贴图的最小产物是：

- `caption.md`：简短、自然、可直接发布的配文；
- `cards/` 与 `cards/manifest.json`：最终图片、尺寸、SHA256 和可得来源/版权边界；
- 公开后才建立或更新 `publish.json` 与 `metrics.json`，记录阅读、点赞、分享、评论、收藏。

仅当贴图包含需要核验的外部事实、时效新闻、产品、价格、政策或数据时，增加
`research/evidence.md` 与 `research/sources.json`；仅当多张卡需要分配独立信息任务时，
再增加 `card-brief.md`、`card-outline.md`。用户提供的单张图片、观点梗或简单截图不
强制补齐这些文件，也不强制套用“发生了什么 / 为什么值得关注 / 账号一句判断”。

需要多卡信息结构时才调用 `wechat-content-strategy` 的 `news-card` 分支生成
`card-outline.md`。所有贴图共用一个独立贴图发布/表现池，不得按新闻、梗图或截图
另建校准池，也不得写入 long-essay v1 或修改其正式 rubric；2026-08-01 至
2026-08-31 试运行期不得把贴图交给 `wechat-style-learning`。

贴图与 long-essay 同级，公开后都登记发布与数据；但普通贴图不以缺少大纲或盲预测
阻塞人工发布。只有在发布前完成兼容盲预测的贴图，才作为正式预测校准样本；未预测
贴图仍保留在同一贴图类作为发布/表现记录，不得事后补造成盲预测。需要预测时区分
真实 Cheat 调用状态与统一贴图 rubric 的适配状态；缺少适配回执时不得把流程调用
记为可校准预测。进入贴图流程前先运行
`python <SKILL_ROOT>/scripts/dependency_check.py --stage news-card`；AI 账号或
AI 主题改用 `--stage news-card-ai`。贴图卡图执行
`references/quality-gates.md` 的封面门禁，但不进入正文配图或 HTML 阶段。

### 单篇项目

运行 `python <SKILL_ROOT>/scripts/article_state.py init <文章目录> --article-id <ID> --mode <full|fast|temporary>` 创建文章目录。字段、路径和真实来源遵循：

- `references/account-profile-schema.md`
- `references/article-state-schema.md`
- `references/recovery-rules.md`

每次记录产物后运行 `python <SKILL_ROOT>/scripts/validate_project.py article <文章目录>`。

