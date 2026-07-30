---
name: WeChat Article Execution
description: Detailed execution runbook for dependency checks, project setup, article pipeline, approvals, visuals, HTML upgrades, publishing, and recovery.
---

# WeChat Article Execution

详细执行手册，和 `SKILL.md` 一起阅读。前者保留核心约束和入口判断，这里保留可执行步骤、产物路径和阶段命令。

## 第一步：选择入口

读取 `references/onboarding.md`，判断用户属于：

- 导入已有账号。
- 新建长期账号。
- 临时创作单篇文章。

用户给出目录时先只读检查。用户已经给出明确主题、素材或初稿时保留它们，不强迫回到选题起点。

### 项目工具契约

若已确认 workspace 根包含 `tools/project_ops.py` 与
`docs/PROJECT-GOVERNANCE.md`，先读取项目治理约定，再执行通用流水线。项目命令
只由本总控调用，两个子 Skill 只返回产物与结果，不自行刷新项目状态或 Skill 锁：

- 日常一致性：`python tools/project_ops.py audit`
- 看板刷新：`python tools/project_ops.py status --write`
- 校准诊断：`python tools/project_ops.py calibration --write`
- 热点收件箱：`python tools/project_ops.py trends --write`
- 改稿候选：`python tools/project_ops.py writing-learning --write`
- Skill 经兼容性测试后：`python tools/project_ops.py skill-lock --write`，随后再次
  运行 `audit`

只在对应项目阶段需要时运行带 `--write` 的命令。不得把项目命令分散给
`wechat-content-strategy` 或 `wechat-style-learning`。

## 第二步：检查依赖

将本 Skill 的绝对目录记为 `SKILL_ROOT`。所有 `scripts/` 和 `references/` 路径都相对 `SKILL_ROOT` 解析；执行时必须拼成绝对路径，不得依赖当前工作目录。按当前阶段运行：

```text
python scripts/dependency_check.py --stage account
python scripts/dependency_check.py --stage topic
python scripts/dependency_check.py --stage topic-ai
python scripts/dependency_check.py --stage writing
python scripts/dependency_check.py --stage strategy
python scripts/dependency_check.py --stage editing
python scripts/dependency_check.py --stage learning
python scripts/dependency_check.py --stage cover
python scripts/dependency_check.py --stage visual
python scripts/dependency_check.py --stage visual-ian
python scripts/dependency_check.py --stage visual-structured
python scripts/dependency_check.py --stage html
python scripts/dependency_check.py --stage publish
python scripts/dependency_check.py --stage retro
```

### 依赖缺失处理

检查返回 `ok: false` 时，按 `missing_required` 或 `missing_any` 列表给出具体安装指引，不要只报错。常见缺失与安装命令：

| 缺失 Skill | 安装命令（对用户说） |
|---|---|
| `cheat-on-content` | `帮我安装 https://github.com/XBuilderLAB/cheat-on-content` |
| `khazix-writer` | `帮我安装 https://github.com/KKKKhazix/khazix-skills`（只需 khazix-writer） |
| `humanizer-zh` | `帮我安装 https://github.com/op7418/Humanizer-zh` |
| `wechat-content-strategy` | 源码位于本仓库 `companion-skills/wechat-content-strategy`；修复指向该目录的同级运行时联接 |
| `wechat-style-learning` | 源码位于本仓库 `companion-skills/wechat-style-learning`；修复指向该目录的同级运行时联接 |
| `creator-buddy` | `帮我安装 https://github.com/SpaceZephyr/creator-buddy` |
| `gzh-explosive-content-detector` | `creator-buddy` 的必需公众号分支；重新安装或修复 `creator-buddy` |
| `aihot` | 重新安装或修复本机 `aihot` Skill |
| `guizang-social-card-skill` | `帮我安装 https://github.com/op7418/guizang-social-card-skill` |
| `ian-xiaohei-illustrations` | `帮我安装 https://github.com/helloianneo/ian-xiaohei-illustrations` |
| `baoyu-article-illustrator` | `帮我安装 https://github.com/JimLiu/baoyu-skills`（只需 baoyu-article-illustrator） |
| `gzh-design` | `帮我安装 https://github.com/isjiamu/gzh-design-skill` |
| `imagegen` | 可选的 Codex 图片 Skill；未发现时仅提示，由所选路线继续解析可用图片后端 |

正文配图至少需要 `ian-xiaohei-illustrations` 或 `baoyu-article-illustrator` 其中一条轨道可用；两条都不可用时阻塞视觉阶段。`optional_missing: ["imagegen"]` 只表示未发现独立的 `imagegen` Skill，不代表当前 runtime 一定没有原生图片工具。由所选路线继续解析真实后端；确实没有可用后端时才阻塞该配图资产。

读取 `references/skill-routing.md` 决定真实调用对象。封面运行 `cover` 预检且只生成 `21:9` 微信头图；正文按认知锚点分别运行对应路线的 `visual-ian` 或 `visual-structured` 预检。缺少 `cheat-on-content` 时阻塞所有相关阶段；缺少 `gzh-design` 时不得标记 HTML 完成。

系统还必须安装 Git。`validate_project.py profile` 使用的 `git init` 和 `git check-ignore` 只能在隔离的临时 Git 仓库中运行，不得写入被验证账号目录。它会在那里验证 `bindings.local.json` 被 `.gitignore` 排除；Git 不可用时账号验证不得通过。

### 升级已安装的 Skill

用户说「更新所有 skill」「更新依赖」「检查 skill 更新」时：

1. 运行 `python scripts/dependency_check.py --stage account` 拿到已安装 skill 的路径列表（`available` 数组）。
2. `dependency_check.py` 本身不输出路径。改用 `python scripts/dependency_check.py --stage html`，从 `available` 取到 skill 名，再按 Git 搜索逻辑找到每个 skill 的实际目录。更直接的方式：直接搜索各 runtime skills 目录下的 git 仓库。
3. 对每个 skill 目录执行：`git -C <目录> pull --ff-only 2>&1`。用 `--ff-only` 避免合并冲突意外改写本地文件。
4. 汇总报告：

| Skill | 状态 |
|---|---|
| `khazix-writer` | 已更新 (旧哈希 -> 新哈希) |
| `humanizer-zh` | 已是最新 |
| `gzh-design` | 更新失败：本地有未提交的修改 |

5. 更新完后跑一次全阶段依赖检查，确认没有因更新导致的 schema 不兼容或路由断裂。
6. 若当前 workspace 启用上述项目工具契约，先完成兼容性测试，再运行
   `skill-lock --write` 刷新 Skill 锁，最后运行 `audit`。

搜索目录：`~/.codex/skills/`、`~/.claude/skills/`、`~/.agents/skills/`，以及 `WECHAT_ARTICLE_SKILL_ROOTS` 环境变量中的路径。只更新是 git 仓库的目录（有 `.git`），跳过手动复制的 skill。

## 第三步：建立状态

### 导入账号

1. 如果目录已有标准 `account.json`，先运行 `python scripts/validate_project.py profile <账号目录>`；验证通过后直接使用，不重新导入。
2. 否则运行 `python scripts/profile_adapter.py preview <源目录>`。
3. 检测到 Cheat 项目时，真实调用 `cheat-on-content` 检查状态和 schema 兼容性。
4. schema 不兼容时停止只读导入，取得授权后才在源项目或工作副本迁移。
5. 展示映射、缺失、冲突和排除项。
6. 用户批准后运行 `python scripts/profile_adapter.py import <源目录> <账号目录> --approved`。
7. 再运行 `validate_project.py profile` 验证结果。

预览必须把会复制的 `mapped` 文档与保持在源项目中的 `live_linked` Cheat 来源分开展示。`.cheat-state.json`、rubric、候选池和预测记录通过本机 binding 实时解析，不复制成会漂移的快照。

`--approved` 只授权适配器的本地写入，不能替代 Cheat 状态检查。公开账号包只保存逻辑绑定和相对引用；机器绝对路径只能进入被忽略的 `bindings.local.json`。账号包与单篇文章项目使用 `references/onboarding.md` 的独立 workspace 布局，不得写入导入源目录。

### 新建长期账号

先调用 `cheat-on-content` 初始化 `long-essay` 项目并完成其全部问题。再按 `references/onboarding.md` 分组收集公众号定位、受众、文风、内容边界、对标和视觉偏好，只对缺失或矛盾字段逐项追问。用户确认画像后，运行：

```text
python scripts/profile_adapter.py create <账号目录> --account-id <ID> --cheat-project <Cheat项目> --approved
python scripts/validate_project.py profile <账号目录>
```

把已确认答案写入对应 Markdown，再验证标准账号包。

### 临时创作

用户必须给出明确主题。临时模式不生成长期账号包；一旦请求 Cheat 能力，要求选择现有 Cheat 项目或升级到长期账号。不得模拟 Cheat 输出。

### 资讯贴图轻量项目

当 `content_kind=news-card` 时，不调用 `article_state.py init`，不进入 long-essay
的 12 阶段状态、正式 v1 预测或 rubric 变更流程。只在 canonical 工作区建立独立
贴图目录，并保留以下五类产物：

- `card-brief.md`：发生了什么、为什么值得关注、账号一句判断、消息日期、可核查来源；
- `research/sources.json`：每个外部事实的直接来源和 `supported_claim`；
- `card-outline.md`：逐卡信息任务、文字上限、事实锚点和来源标记；
- `cards/`：最终图片；
- `publish.json` 与 `metrics.json`：独立记录发布以及阅读、点赞、分享、评论、收藏。

调用 `wechat-content-strategy` 的 `news-card` 分支生成 `card-outline.md`。资讯贴图
数据不得写入 long-essay v1 校准池，不得据此修改正式 rubric；2026-08-01 至
2026-08-31 试运行期不得把资讯贴图交给 `wechat-style-learning`。

### 单篇项目

运行 `python scripts/article_state.py init <文章目录> --article-id <ID> --mode <full|fast|temporary>` 创建文章目录。字段、路径和真实来源遵循：

- `references/account-profile-schema.md`
- `references/article-state-schema.md`
- `references/recovery-rules.md`

每次记录产物后运行 `python scripts/validate_project.py article <文章目录>`。

## 第四步：执行文章流水线

文章绑定标准长期账号画像时，在进入大纲和初稿前解析画像并读取 `voice.md` 与
`content-patterns.md`。将 `voice.md` 和 `style-learning:validated` 区块作为硬约束，
将 `style-learning:provisional` 区块作为软参考。优先级依次为：用户当次明确要求与
已核验事实/证据/经历/观点、账号文风与已验证规则、当篇策略参数、待验证规则、
`khazix-writer` 默认口吻。不得为套用文风新增素材。

下表只适用于 `content_kind=long-essay`；资讯贴图使用上面的轻量项目，不进入本表。

| 阶段 | 动作 | 产物或真实来源 |
|---|---|---|
| 简报 | 明确主题、受众、观点、材料、字数和时效 | `brief.md` |
| 选题 | `creator-buddy` 跨平台信号 + 显式公众号爆款分支 + AI 主题的 `aihot` -> 候选归一化、去重、保留来源 -> 根 Cheat 评分与决策 -> 用户确认角度 | `topic-brief.md` + Cheat 引用 |
| 调研 | 核查当前事实和原始来源 | `research/evidence.md`、`research/sources.json` |
| 大纲 | 调用 `wechat-content-strategy`，从已核验材料选择一种内容增强策略，确定中心论点、文章级写作参数、结构、证据位置和编辑锚点 | `outline.md` |
| 初稿 | 使用 `khazix-writer` 作为唯一起草引擎，按账号文风、已验证规则和大纲参数生成初稿；不得让其默认口吻覆盖账号规则 | `drafts/draft-v1.md` |
| 审校 | 事实核查、结构、账号适配、`humanizer-zh` 去 AI 痕迹 | `drafts/final.md` |
| 预测 | 最终稿确认后调用 Cheat | Cheat 预测引用 |
| 视觉 | Guizang 生成唯一一张 `21:9` 微信头图；Ian/Baoyu 按认知锚点生成正文配图 | `visuals/visual-plan.md`、`visuals/assets/` |
| 排版 | 调用 `gzh-design` 并清零强制错误 | `output/article.html`、`output/article-preview.html`、`output/article-copy.html`、`output/article-copy-preview.html`、`output/html-qc.md` |
| 发布 | 人工复制已验证 HTML；公开后由用户确认并登记 Cheat | `publish.json` |
| 复盘 | 公开发布后调用 Cheat 回收和演化 | Cheat 复盘引用 |

Cheat 路由包括 init、seed、recommend、score、predict、publish、retro、persona、bump 和 status；每次都调用根 `cheat-on-content`，由它选择内部流程。

### 选题信号汇聚

进入选题阶段时先运行 `dependency_check.py --stage topic`；AI 账号或 AI 主题改用 `--stage topic-ai`。随后严格按 `references/skill-routing.md` 的 topic signal orchestration 执行：

1. 根 `creator-buddy` 收集跨平台信号，并在公众号选题中显式路由 `gzh-explosive-content-detector`；小红书关键词热度优先走 `xiaohongshu-search`，只有详情、评论或博主作品分析才走 Agent Reach 路线。
2. AI 账号或 AI 主题同时调用根 `aihot`，保留原文 URL；它的摘要只用于发现候选，不能替代事实核查。
3. 调用根 `cheat-on-content` 路由到 `cheat-trends`，按账号启用的热点适配器补充综合热榜信号；它负责补充、去重和粗筛，不替代前三路。
4. 把四路结果归一化为候选池。每条至少记录标题、来源、可打分的内容快照、抓取时间和可用的原始链接；同一事件跨平台重复出现时合并为一个候选，并保留全部来源，不把重复转述当成多份独立证据。
5. 将候选池交给根 `cheat-on-content`：已有候选池走 recommend，已有主题或初稿走 score，没有主题且没有可用候选才走 seed。不得由信号 Skill 或本 Skill 自行替代 Cheat 排名。
6. 在 `topic-brief.md` 展示数据源状态、归一化候选、去重说明、Cheat 评分引用与推荐理由；用户确认选题角度前，topic 阶段保持 `awaiting_confirmation`。

`gzh-explosive-content-detector` 识别到泛词时，必须遵守它的强制等待规则：先让用户选择拓展或不拓展，再继续抓取、汇聚和 Cheat 决策。任一信号源不可用时如实标记该路缺失，不得用模型记忆补造，也不得把不完整候选池描述为完整四路扫描。

### 内容策略与改稿学习路由

- 普通端到端创作始终由本 Skill 总控；在证据关卡通过后内部调用 `wechat-content-strategy`。
- 用户明确只要选题深化、内容增强或大纲时，仍先由本 Skill 补齐 Cheat 决策和事实前置，再允许直接进入 `wechat-content-strategy`。
- 用户明确说“学习我的修改”“沉淀文风”时，检查长期账号、初稿和人工定稿，再调用 `wechat-style-learning`。先展示候选规则，用户确认后才写入账号学习账本。
- 学习动作不改变当前文章内容、审批、预测或状态，也不触发当前文章的 stale 传播；新规则从下一篇文章开始生效。

执行事实、写作、视觉和 HTML 检查时读取 `references/quality-gates.md`。进入交付或外部写入时读取 `references/publishing.md`。

## 预测与审批

保留五类总控确认：账号配置、选题角度、大纲事实边界、最终正文、视觉交付。视觉交付包含出图前的视觉计划确认和排版后的 HTML 确认。

最终正文确认必须绑定当前 `final` 产物 SHA256。预测前确认 `approvals.final.artifact_sha256 == artifacts.final.sha256`；缺失或不匹配时重新展示当前全文并取得确认。预测版本只能由真实 Cheat 调用产生，旧版本不可覆盖。

外部 Skill 的硬性确认继续有效。选择 `baoyu-article-illustrator` 后，按其流程确认图片类型、密度、风格、配色和语言。快速模式也不得跳过事实关卡、Cheat 协议、头图与正文配图计划确认或 HTML 校验。

## 视觉与 HTML

在 `visuals/visual-plan.md` 分开记录封面与正文配图计划。封面调用根 `guizang-social-card-skill`，显式覆盖其默认封面对输出：只生成 `.poster.wide` 对应的 `21:9` 主头图，不创建 `.poster.square`、`1:1` 分享卡或封面对预览。生成后验证尺寸、标题可读性、主体裁切、素材来源和文件存在性。

正文每个认知锚点只选一条轨道：情绪、观点、身份、叙事转折或原创隐喻走 Ian；流程、层级、对比、矩阵、架构、时间线、精确标签或有证据的数据走 `baoyu-article-illustrator`。无独立信息任务的段落不配图。同一锚点除非用户明确要求 A/B，不重复生成两套。

选择 Baoyu 轨道时，先运行 `python scripts/baoyu_adapter.py prepare <文章目录>`，只把 `visuals/assets/baoyu/source.md` 交给根 Skill；结束后运行 `python scripts/baoyu_adapter.py verify <文章目录>`，确保已批准的 `drafts/final.md` 没有被改写。

`gzh-design` 是 HTML 完成的必经路线。还要运行文章验证器。HTML 预览必须分别在 <=390 CSS px 和 >=900 CSS px 两种视口检查。还要把正文实际粘贴到干净的 `contenteditable` 或微信兼容沙箱检查 DOM。四项都通过后才可标记 HTML 完成。

HTML 阶段必须同时保留：

1. `output/article.html`
2. `output/article-preview.html`
3. `output/article-copy.html`
4. `output/article-copy-preview.html`
5. `output/html-qc.md`

其中 `article-copy.html` 是人工粘贴交付物，`artifacts.html.path` 必须指向它。
`gzh-design` 生成预览页后，运行
`python scripts/upgrade_preview_copy.py <output/article-copy-preview.html>`，把复制按钮
加固为显式 `text/html` 剪贴板写入并保留旧式复制作为回退。随后必须实际点击该按钮
再粘贴检查；只检查干净 HTML 文件不能替代剪贴板门禁。把窄/宽视口、图片加载、
复制方法、粘贴目标和 pasted DOM 结果写入 `output/html-qc.md`。

## 失败与恢复

读取 `references/recovery-rules.md`。上游内容变化时找出最早变更阶段，运行 `python scripts/article_state.py invalidate <文章目录> --stage <阶段>` 并先持久化状态；不要用状态切换代替失效传播，也不要删除有效上游产物。

头图或正文配图失败时保留提示词和错误记录；HTML 失败时停止交付。恢复必须继续到所有受影响的下游 `stale` 项重新生成和验证。

## 发布边界与最终交付

默认交付经过浏览器检查的 HTML 五件套：`output/article.html`、
`output/article-preview.html`、`output/article-copy.html`、
`output/article-copy-preview.html`、`output/html-qc.md`，以及最终 Markdown、唯一
一张 `21:9` 微信头图、正文配图和图片资产清单，并将 `publish.json.status` 设为
`html_ready`。这只表示可由用户人工复制到公众号编辑器，不表示已上传草稿或公开
发布。本 Skill 不调用任何草稿箱上传或自动发布适配器。

只有用户明确确认文章公开可访问后，才记录 `publicly_published`，并必须真实调用 `cheat-on-content` 的 publish 路由。Cheat 登记失败时保留真实公开状态，但将文章 publish 阶段标为失败；恢复时只重试登记，不重复上传或发布。
