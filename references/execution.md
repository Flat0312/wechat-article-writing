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
python <SKILL_ROOT>/scripts/dependency_check.py --stage account
python <SKILL_ROOT>/scripts/dependency_check.py --stage topic
python <SKILL_ROOT>/scripts/dependency_check.py --stage topic-ai
python <SKILL_ROOT>/scripts/dependency_check.py --stage news-card
python <SKILL_ROOT>/scripts/dependency_check.py --stage news-card-ai
python <SKILL_ROOT>/scripts/dependency_check.py --stage writing
python <SKILL_ROOT>/scripts/dependency_check.py --stage strategy
python <SKILL_ROOT>/scripts/dependency_check.py --stage editing
python <SKILL_ROOT>/scripts/dependency_check.py --stage learning
python <SKILL_ROOT>/scripts/dependency_check.py --stage cover
python <SKILL_ROOT>/scripts/dependency_check.py --stage visual
python <SKILL_ROOT>/scripts/dependency_check.py --stage visual-ian
python <SKILL_ROOT>/scripts/dependency_check.py --stage visual-structured
python <SKILL_ROOT>/scripts/dependency_check.py --stage html
python <SKILL_ROOT>/scripts/dependency_check.py --stage publish
python <SKILL_ROOT>/scripts/dependency_check.py --stage retro
```

### 依赖缺失处理

检查返回 `ok: false` 时，按 `missing_required` 或 `missing_any` 列表给出具体安装指引，不要只报错。常见缺失与安装命令：

| 缺失 Skill | 安装命令（对用户说） |
|---|---|
| `cheat-on-content` | `帮我安装 https://github.com/XBuilderLAB/cheat-on-content` |
| `khazix-writer` | `帮我安装 https://github.com/KKKKhazix/khazix-skills`（只需 khazix-writer；它是必需的技法辅助，不是作者声音） |
| `humanizer-zh` | `帮我安装 https://github.com/op7418/Humanizer-zh`（可选诊断器，缺失时使用本 Skill 的 AI 痕迹门禁） |
| `wechat-content-strategy` | 源码位于本仓库 `companion-skills/wechat-content-strategy`；修复指向该目录的同级运行时联接 |
| `wechat-style-learning` | 源码位于本仓库 `companion-skills/wechat-style-learning`；修复指向该目录的同级运行时联接 |
| `creator-buddy` | `帮我安装 https://github.com/SpaceZephyr/creator-buddy` |
| `gzh-explosive-content-detector` | `creator-buddy` 的必需公众号分支；重新安装或修复 `creator-buddy` |
| `xiaohongshu-skill` | `帮我安装 https://github.com/DeliciousBuding/xiaohongshu-skill`；首次使用需扫码登录（`python -m scripts qrcode --headless=false`） |
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

1. 运行 `python <SKILL_ROOT>/scripts/dependency_check.py --stage account` 拿到已安装 skill 的路径列表（`available` 数组）。
2. `dependency_check.py` 本身不输出路径。改用 `python <SKILL_ROOT>/scripts/dependency_check.py --stage html`，从 `available` 取到 skill 名，再按 Git 搜索逻辑找到每个 skill 的实际目录。更直接的方式：直接搜索各 runtime skills 目录下的 git 仓库。
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

1. 如果目录已有标准 `account.json`，先运行 `python <SKILL_ROOT>/scripts/validate_project.py profile <账号目录>`；验证通过后直接使用，不重新导入。
2. 否则运行 `python <SKILL_ROOT>/scripts/profile_adapter.py preview <源目录>`。
3. 检测到 Cheat 项目时，真实调用 `cheat-on-content` 检查状态和 schema 兼容性。
4. schema 不兼容时停止只读导入，取得授权后才在源项目或工作副本迁移。
5. 若执行了 `cheat-migrate`，再次真实调用根 `cheat-status`，按
   [`references/cheat-status-receipt.md`](cheat-status-receipt.md) 生成并验证
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

运行 `python <SKILL_ROOT>/scripts/article_state.py init <文章目录> --article-id <ID> --mode <full|fast|temporary>` 创建文章目录。字段、路径和真实来源遵循：

- `references/account-profile-schema.md`
- `references/article-state-schema.md`
- `references/recovery-rules.md`

每次记录产物后运行 `python <SKILL_ROOT>/scripts/validate_project.py article <文章目录>`。

## 第四步：执行文章流水线

文章绑定标准长期账号画像时，在进入大纲和初稿前解析画像并读取 `voice.md`、
`content-patterns.md` 和 `references/writing-style.md`。将 `voice.md` 和
`style-learning:validated` 区块作为作者声音的硬约束，将 `style-learning:provisional`
区块作为主动选择的实验。优先级依次为：用户当次明确要求与已核验事实/证据/经历/观点、
账号文风与已验证规则、文风执行卡、卡兹克返回的兼容技法建议、未选中的通用建议。
不得为套用任何文风新增素材。

下表只适用于 `content_kind=long-essay`；资讯贴图使用上面的轻量项目，不进入本表。

| 阶段 | 动作 | 产物或真实来源 |
|---|---|---|
| 简报 | 明确主题、受众、观点、材料、字数和时效 | `brief.md` |
| 选题 | 按 [`references/topic-signal-registry.md`](topic-signal-registry.md) 执行五个信号 lane（`aihot` 按适用性标记） -> 候选归一化、去重、保留来源 -> 根 Cheat 评分与决策 -> 用户确认角度 | `topic-brief.md` + Cheat 引用 |
| 调研 | 核查当前事实和原始来源 | `research/evidence.md`、`research/sources.json` |
| 大纲 | 调用 `wechat-content-strategy`，从已核验材料选择一种内容增强策略，确定中心论点、文章级写作参数、文风执行卡、结构、证据位置和编辑锚点 | `outline.md` |
| 技法辅助 | 在文风执行卡锁定后按 [`references/khazix-craft-contract.md`](khazix-craft-contract.md) 调用 `khazix-writer`，只获取结构、场景、类比、节奏和自检建议，并运行 `craft_only_adapter.py` | 辅助结果，不直接作为正文 |
| 初稿 | 由本 Skill 按文风执行卡融合用户声音与兼容技法，生成初稿；不得让卡兹克默认人格覆盖账号规则 | `drafts/draft-v1.md` |
| 审校 | 事实核查、结构、账号适配、文笔终检；按 [`references/humanizer-diagnostic-contract.md`](humanizer-diagnostic-contract.md) 将 `humanizer-zh` 限制为可选 AI 痕迹诊断 | `drafts/final.md` |
| 终稿观察 | 持续学习启用时，终稿批准并锁定 SHA256 后提炼 0–5 条跨篇候选，写入观察账本；不改变正文、审批或预测 | `account-profile/history/voice-observations/` |
| 预测 | 先验证 `cheat-form-receipt.json`：根 Cheat 调用完成且当前内容形态 rubric 已适配；再运行 `scripts/cheat_prediction_adapter.py` 生成哈希绑定的只读 Cheat 输入，最后调用根 Cheat 的 predict | `cheat-form-receipt.json` + `prediction-input-reference.json` + Cheat 预测引用 |
| 视觉 | Guizang 合成唯一一张 `21:9` 微信头图（素材缺失时 ImageGen 出底图、guizang 仍合成文字；仅 guizang 不可用时 ImageGen 端到端兜底，兜底显式标注）；Ian/Baoyu 按认知锚点生成正文配图，并由总控适配器统一收回 | `visuals/visual-plan.md`、`visuals/assets/manifest.json`、`visuals/assets/` |
| 排版 | 调用 `gzh-design` 并清零强制错误 | `output/article.html`、`output/article-preview.html`、`output/article-copy.html`、`output/article-copy-preview.html`、`output/html-qc.md` |
| 发布 | 人工复制已验证 HTML；用户确认公开后先真实调用 Cheat publish，再运行总控发布桥写入回执 | `publish.json` + `publish-reference.json` |
| 复盘 | 公开发布后把人工 WeChat 数据写入 `metrics.json`，再调用 Cheat 回收和演化 | `metrics.json` + Cheat 复盘引用 |

公众号适用 Cheat 路由共 12 条：`cheat-init`、`cheat-learn-from`、`cheat-seed`、`cheat-recommend`、`cheat-score`、`cheat-predict`、`cheat-publish`、`cheat-retro`、`cheat-persona`、`cheat-bump`、`cheat-status`、`cheat-migrate`。每次都调用根 `cheat-on-content`，由它选择内部流程；`cheat-shoot`、`cheat-trends` 和 `cheat-score-blind` 仍按路由契约排除或仅内部使用。

### 选题信号汇聚

进入选题阶段时先运行 `python <SKILL_ROOT>/scripts/dependency_check.py --stage topic`；AI 账号或 AI 主题改用 `python <SKILL_ROOT>/scripts/dependency_check.py --stage topic-ai`。随后严格按 [`references/topic-signal-registry.md`](topic-signal-registry.md) 和 `references/skill-routing.md` 的 topic signal orchestration 执行：

1. 按 registry 运行 `creator-buddy-cross-platform` 和显式的 `gzh-explosive-content-detector` lane；调用 creator-buddy 时必须附带 [`references/creator-buddy-wechat-override.md`](creator-buddy-wechat-override.md) 的 route override。小红书关键词热度必须走本机 `xiaohongshu-skill`（Playwright 扫码登录、免费、无需 API Key），不得静默降级到 xhs-hotnotes、Agent Reach、global-content-search、RedFox、socialdatax 或 Guaikei；只有已登记关键词热度后，详情、评论或博主作品分析才走 creator-buddy 的其他路线。
2. AI 账号或 AI 主题运行 `aihot` lane，其他主题把该 lane 记为 `not_applicable`；保留原文 URL，摘要只用于发现候选，不能替代事实核查。
3. 运行 `x-tweet-fetcher` lane，按 registry 保存原始输出和来源登记。
4. 调用根 `cheat-on-content` 路由到 `cheat-trends` lane，按账号启用的热点适配器补充综合热榜信号；它负责补充、去重和粗筛，不替代其他信号或最终 Cheat 推荐。
5. 把五个已登记 lane 的结果和状态归一化为候选池。每条至少记录标题、来源、可打分的内容快照、抓取时间和可用的原始链接；同一事件跨平台重复出现时合并为一个候选，并保留全部来源，不把重复转述当成多份独立证据。
6. 将候选池交给根 `cheat-on-content`：已有候选池走 recommend，已有主题或初稿走 score，没有主题且没有可用候选才走 seed。不得由信号 Skill 或本 Skill 自行替代 Cheat 排名。
7. 在 `topic-brief.md` 展示五个 lane 的数据源状态、归一化候选、去重说明、Cheat 评分引用与推荐理由；用户确认选题角度前，topic 阶段保持 `awaiting_confirmation`。

`gzh-explosive-content-detector` 识别到泛词时，必须遵守它的强制等待规则：先让用户选择拓展或不拓展，再继续抓取、汇聚和 Cheat 决策。任一信号源不可用时如实标记该 lane 缺失，不得用模型记忆补造，也不得把不完整候选池描述为完整适用信号集合。

### 内容策略与改稿学习路由

- 普通端到端创作始终由本 Skill 总控；在证据关卡通过后内部调用 `wechat-content-strategy`。
- 用户明确只要选题深化、内容增强或大纲时，仍先由本 Skill 补齐 Cheat 决策和事实前置，再允许直接进入 `wechat-content-strategy`。
- 用户明确说“学习我的修改”“沉淀文风”时，检查长期账号、初稿和人工定稿，再调用 `wechat-style-learning`。先展示候选规则，用户确认后才写入账号学习账本。
- 用户明确启用“持续学习”后，每篇已批准终稿都调用 `wechat-style-learning observe-final`；观察结果只进入软观察层，至少 3 篇不同文章重复且无冲突后标记为 `candidate`，晋级硬规则前仍展示并取得确认。
- 学习动作不改变当前文章内容、审批、预测或状态，也不触发当前文章的 stale 传播；新规则从下一篇文章开始生效。

执行事实、写作、视觉和 HTML 检查时读取 `references/quality-gates.md` 与
`references/writing-style.md`。进入交付或外部写入时读取 `references/publishing.md`。

## 预测与审批

保留五类总控确认：账号配置、选题角度、大纲事实边界、最终正文、视觉交付。视觉交付包含出图前的视觉计划确认和排版后的 HTML 确认。

最终正文确认必须绑定当前 `final` 产物 SHA256。预测前确认 `approvals.final.artifact_sha256 == artifacts.final.sha256`；缺失或不匹配时重新展示当前全文并取得确认。预测版本只能由真实 Cheat 调用产生，旧版本不可覆盖。long-essay 还必须先通过 `references/cheat-form-contract.md` 的调用状态与 rubric 适配状态双门禁。根 Cheat 返回 blind JSON 后，先按 `references/blind-score-contract.md` 运行总控适配器校验 rubric 版本、7/9 维集合、字段和 script hash，再允许根路由计算 composite；失败时停止，不补维度、不猜版本。

外部 Skill 的硬性确认继续有效。选择 `baoyu-article-illustrator` 后，按其流程确认图片类型、密度、风格、配色和语言。快速模式也不得跳过事实关卡、Cheat 协议、头图与正文配图计划确认或 HTML 校验。

## 视觉与 HTML

在 `visuals/visual-plan.md` 分开记录封面与正文配图计划。封面调用根 `guizang-social-card-skill`，显式覆盖其默认封面对输出：只生成 `.poster.wide` 对应的 `21:9` 主头图，不创建 `.poster.square`、`1:1` 分享卡或封面对预览。照片素材缺失时允许 ImageGen 生成底图、仍由 guizang 合成文字（素材兜底）；仅当 guizang 本身不可用时，才允许 ImageGen 端到端生成整张封面（路由兜底）。两种兜底适用同一单图契约，并必须在 `visual-plan.md` 和交付说明中显式标注。生成后先把外部 route 输出目录和选定源文件交给总控适配器：

```text
python <SKILL_ROOT>/scripts/visual_asset_adapter.py cover <PROJECT_ROOT> --route guizang --source <GUIZANG_OUTPUT>/wechat-21x9-cover.png --route-output-dir <GUIZANG_OUTPUT>
```

适配器要求 route 目录恰好有一个静态位图，检查精确 `21:9`，并拒绝 square、pair、carousel、Live Photo 和视频文件；失败即判 Guizang 路线不可用，按上面规则切换到标注过的 ImageGen 路由，不能静默丢弃外部产物。适配成功后交付文件固定在 `visuals/assets/cover.<ext>`，并写入 `visuals/assets/manifest.json`。

正文每个认知锚点只选一条轨道：情绪、观点、身份、叙事转折或原创隐喻走 Ian；流程、层级、对比、矩阵、架构、时间线、精确标签或有证据的数据走 `baoyu-article-illustrator`。无独立信息任务的段落不配图。同一锚点除非用户明确要求 A/B，不重复生成两套。外部成品不能直接作为文章交付路径；每个选定锚点都要用总控适配器登记：

```text
python <SKILL_ROOT>/scripts/visual_asset_adapter.py body <PROJECT_ROOT> --route ian --source <IAN_OUTPUT>/anchor-emotion.png --anchor-id anchor-emotion --information-job "narrative tension" --provenance-ref <IAN_OUTPUT_REF>
python <SKILL_ROOT>/scripts/visual_asset_adapter.py body <PROJECT_ROOT> --route baoyu --source <BAOYU_OUTPUT>/anchor-flow.png --anchor-id anchor-flow --information-job "ordered steps" --provenance-ref <BAOYU_OUTPUT_REF>
```

适配器把两条路线统一收回 `visuals/assets/ian/` 或 `visuals/assets/baoyu/`，并在同一个 `visuals/assets/manifest.json` 中记录路线、锚点、信息任务、尺寸、SHA256 和可选 provenance。完成全部选定资产后，用
`python <SKILL_ROOT>/scripts/article_state.py record <PROJECT_ROOT> --role visuals --path visuals/assets/manifest.json`
把 manifest 纳入文章状态。

选择 Baoyu 轨道时，先运行 `python <SKILL_ROOT>/scripts/baoyu_adapter.py prepare <文章目录>`，只把 `visuals/assets/baoyu/source.md` 交给根 Skill；结束后运行 `python <SKILL_ROOT>/scripts/baoyu_adapter.py verify <文章目录>`，确保已批准的 `drafts/final.md` 没有被改写。

`gzh-design` 是 HTML 完成的必经路线。调用时必须把
`references/wechat-layout-contract.md` 的 8 条契约（3 文本级 + 5 视觉级）作为
高于主题配方和默认智能处理的硬约束传入。还要运行文章
验证器。HTML 预览必须分别在 <=390 CSS px 和 >=900 CSS px 两种视口检查。还要把
正文实际粘贴到干净的 `contenteditable` 或微信兼容沙箱检查 DOM，并把九项排版检查
结果逐项写入 `output/html-qc.md`。全部通过后才可标记 HTML 完成。

HTML 阶段必须同时保留：

1. `output/article.html`
2. `output/article-preview.html`
3. `output/article-copy.html`
4. `output/article-copy-preview.html`
5. `output/html-qc.md`

`gzh-design` 的默认文件名（`{原文件名}_排版_{主题}.html` 和
`{原文件名}_预览.html`）不属于文章项目 schema。总控必须把它返回的纯
`<section>...</section>` 正文按下面的固定映射落盘；不得把默认命名直接登记为项目产物：

1. 将 `gzh-design` 的干净 section 写入绝对路径
   `<PROJECT_ROOT>/output/article.html`，并运行 `gzh-design` 的 HTML 校验。
2. 原样复制 `output/article.html` 为 `output/article-copy.html`；后者是人工粘贴
   交付物，`artifacts.html.path` 必须指向它。不要把预览外壳复制到该文件。
3. 用总控随附脚本分别生成两个预览壳：

   ```text
   python <SKILL_ROOT>/scripts/wrap_preview.py <PROJECT_ROOT>/output/article.html <PROJECT_ROOT>/output/article-preview.html
   python <SKILL_ROOT>/scripts/wrap_preview.py <PROJECT_ROOT>/output/article-copy.html <PROJECT_ROOT>/output/article-copy-preview.html
   ```

4. 只对 `output/article-copy-preview.html` 运行：

   ```text
   python <SKILL_ROOT>/scripts/upgrade_preview_copy.py <PROJECT_ROOT>/output/article-copy-preview.html
   ```

   该步骤把复制按钮加固为显式 `text/html` 剪贴板写入并保留旧式复制作为回退，
   同时把本地图片内嵌到复制载荷。随后必须静态确认复制 HTML 中没有
   `../visuals/...` 图片路径，再实际点击该按钮并粘贴检查；只检查干净 HTML 文件
   不能替代剪贴板门禁。
5. 按 `assets/article-project-template/output/html-qc.template.md` 生成并填写
   `<PROJECT_ROOT>/output/html-qc.md`。它必须记录五件套、gzh-design 调用、窄/宽
   视口、图片加载、复制方法、粘贴目标、pasted DOM 和九项排版检查结果。

每一步都使用实际的绝对 `<SKILL_ROOT>` 与 `<PROJECT_ROOT>`；文件完成前运行
`python <SKILL_ROOT>/scripts/validate_project.py article <PROJECT_ROOT>`。

## 失败与恢复

读取 `references/recovery-rules.md`。上游内容变化时找出最早变更阶段，运行 `python <SKILL_ROOT>/scripts/article_state.py invalidate <文章目录> --stage <阶段>` 并先持久化状态；不要用状态切换代替失效传播，也不要删除有效上游产物。

头图或正文配图失败时保留提示词和错误记录；HTML 失败时停止交付。恢复必须继续到所有受影响的下游 `stale` 项重新生成和验证。

## 发布边界与最终交付

默认交付经过浏览器检查的 HTML 五件套：`output/article.html`、
`output/article-preview.html`、`output/article-copy.html`、
`output/article-copy-preview.html`、`output/html-qc.md`，以及最终 Markdown、唯一
一张 `21:9` 微信头图、正文配图和图片资产清单，并将 `publish.json.status` 设为
`html_ready`。这只表示可由用户人工复制到公众号编辑器，不表示已上传草稿或公开
发布。本 Skill 不调用任何草稿箱上传或自动发布适配器。

只有用户明确确认文章公开可访问后，才记录 `publicly_published`，并必须真实调用 `cheat-on-content` 的 publish 路由。Cheat 登记失败时保留真实公开状态，但将文章 publish 阶段标为失败；恢复时只重试登记，不重复上传或发布。
