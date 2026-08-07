# Skill 路由契约

## 规范注册表

| Skill | 职责 | 规则 |
|---|---|---|
| `cheat-on-content` | Cheat 生命周期所有者 | 遵循 `SKILL.md` 核心约束第 1 条 |
| `creator-buddy` | 公众号爆款与跨平台选题信号：小红书 / B站 / 抖音 / 知乎 / 微博 / 头条 | 提供选题信号 |
| `global-content-search` | 小红书、B站、抖音及公开热榜搜索 | 默认内容搜索路线；保留实际后端与明确的缺失状态 |
| `gzh-explosive-content-detector` | 近期公众号爆款样本、增长信号、标题模式、赛道词 | 选题发现必须使用的公众号分支；通过 `creator-buddy` 调用并保留其通用关键词确认规则 |
| `aihot` | 当前 AI 新闻 | AI 账号或 AI 主题必须调用 |
| `wechat-article-writing` | 第一方起草、账号声音、文笔执行和最终文风门禁 | 文章起草的必需所有者；读取 `references/writing-style.md` |
| `human-writing` | 必需的活人感正文主流程 | 文风卡锁定后，必须参与每篇中长文的起草与修订；使用其材料、说话者位置、自然中文和文笔检查流程，但不得让它创建或替代账号声音 |
| `humanizer-zh` | 可选的 AI 痕迹诊断 | 仅在事实、结构和账号声音稳定后，按 [`external-contracts.md`](external-contracts.md#humanizer-diagnostic-contract) 运行；选择性接受局部建议，绝不替换全文 |
| `wechat-content-strategy` | 证据约束的内容增强、提纲、写作参数、文风卡与编辑锚点 | 主题和证据就绪后、第一方起草前必须调用 |
| `wechat-style-learning` | 长期账号的已确认改稿学习 | 仅在用户明确要求从改稿学习时调用，并且只在确认后持久化 |
| `guizang-social-card-skill` | 微信封面合成 | 遵循 `quality-gates.md` 的视觉门禁 |
| `ian-xiaohei-illustrations` | 正文配图路线 | 遵循 `quality-gates.md` 的视觉门禁 |
| `baoyu-article-illustrator` | 正文配图路线 | 遵循 `quality-gates.md` 的视觉门禁 |
| `imagegen` | 可选的 Codex 图片 Skill | 仅可在 `quality-gates.md` 的视觉门禁下使用 |
| `gzh-design` | 微信 `<section>` HTML 与平台校验 | 遵循 `quality-gates.md` 的 HTML 门禁；接受别名 `gzh-design-skill` |
| `space-xhs-buddy` | 已确认内容的小红书原生交接 | 仅在项目启用小红书且用户确认具体改编时使用；应路由到写作、标题、图文专项 Skill，不得复制公众号终稿 |

封面、正文配图和 HTML 规则以 [`quality-gates.md`](quality-gates.md) 为唯一来源。
选题 lane 名称、适用性、状态、候选字段与编排以
[`topic-signal-registry.md`](topic-signal-registry.md) 为唯一来源。

## 明确排除的 Cheat 路由

权威 Cheat 路由清单、根调用规则与排除项位于 `SKILL.md` 核心约束第 1 条。

## 排除能力

不得注册或调用 `hv-analysis`、`space-chart-image`、`article-batch-illustration`、`article-cover-and-batch-illustration`、`baoyu-slide-deck`、`neat-freak` 或 `storage-analyzer`。由 `creator-buddy` 自行路由其平台子 Skill，但公众号选题发现必须（MUST）明确请求其 `gzh-explosive-content-detector` 分支。

## 选题信号编排

执行 [`topic-signal-registry.md`](topic-signal-registry.md)；不得在此复述或覆盖其 lane 流程。

## Cheat 路由

使用 `SKILL.md` 核心约束第 1 条中的权威路由清单和根调用规则。账号导入与迁移确认步骤仍位于 `onboarding.md`。

`cheat-seed` 存在外部通用 `humanizer` 命名不一致。应用
[`cheat-contracts.md`](cheat-contracts.md#cheat-seed-humanizer-compatibility-register)
中的登记规则：总控路线只承认 `humanizer-zh`，绝不安装通用替代项，也绝不把 seed 输出当作编辑诊断。

当 `content_form=long-essay` 时，预测还必须具备
[`cheat-contracts.md`](cheat-contracts.md#cheat-content-form-and-rubric-contract)
规定的回执。根 Cheat 调用完成与公众号中长文 rubric 兼容是两个独立状态；只有观点视频 rubric 时，`cheat-predict` 不得继续。

## 内容策略与学习

- 保持 `wechat-article-writing` 为常规入口，以及前置条件、状态、审批与恢复的所有者。
- 仅在选题与证据包存在后调用 `wechat-content-strategy`。它可以写入 `outline.md` 和当篇文风卡；不得收集未登记事实、起草文章或直接更改文章状态。
- 保护 `wechat-article-writing` 为起草所有者。写作前读取 `references/writing-style.md` 并锁定文风卡。以 `human-writing` 作为材料充分性、说话者位置、段落推进、自然中文和初稿后修订的必需正文主流程，账号 `voice.md` 与已验证的 profile 与它同权重并列作用于起草；任一方都不整段覆盖另一方。起草期间不得调用外部作者文风 Skill。
- 仅在标准长期 profile 下，且用户明确要求学习后调用 `wechat-style-learning`。它可以更新可选的改稿账本和 `content-patterns.md` 中生成的学习块；不得更改 `voice.md`、文章产物、Cheat 状态或当前审批。

## 双平台分发交接

- 将已解析分发目录中的 `platforms.json` 视为平台启用开关，将 `registry.json` 视为跨平台关联记录。
- 公众号仍由本 Skill 所有。小红书启用且用户确认具体改编后，调用 `space-xhs-buddy`，由它路由至原生写作、标题和图文 Skill。
- 只共享已验证事实、源素材与内容核心。不得把公众号终稿复用成小红书终稿，也不得让小红书改动使已批准的公众号产物失效。
- 各平台分别记录生产、公开确认、数据与校准。
- 仅启用平台绝不授权发布，也不授权创建逐内容占位目录。

## 视觉与 HTML 门禁

执行 [`quality-gates.md`](quality-gates.md) 中的视觉与 HTML 门禁；本路由注册表不重复其约束。
