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

将本 Skill 的绝对目录记为 `SKILL_ROOT`。所有 `scripts/` 和 `references/` 路径都相对 `SKILL_ROOT` 解析；执行时必须拼成绝对路径，不得依赖当前工作目录。以脚本帮助为 stage 清单的唯一来源，再运行当前阶段：

```text
python <SKILL_ROOT>/scripts/dependency_check.py --help
python <SKILL_ROOT>/scripts/dependency_check.py --stage <STAGE>
```

### 依赖缺失处理

检查返回 `ok: false` 时，按 `missing_required`、`missing_any`、`script_runtime.missing_required` 或 `cli_runtime.missing_required` 列表给出具体安装指引，不要只报错。`skill_presence` 只说明 frontmatter Skill 是否被发现；`script_runtime` 单独说明脚本入口、语法和 Python import/version；`cli_runtime` 单独说明外部命令及其解析路径。三类结果都要保留在阶段回执中，不能用 Skill 目录存在覆盖 runtime 失败。常见缺失与安装命令：

| 缺失 Skill | 安装命令（对用户说） |
|---|---|
| `cheat-on-content` | `帮我安装 https://github.com/XBuilderLAB/cheat-on-content` |
| `human-writing` | `帮我安装 https://github.com/KKKKhazix/human-writing`（每篇中长文必需的活人感写作与改稿主流程，不代替账号声音） |
| `humanizer-zh` | `帮我安装 https://github.com/op7418/Humanizer-zh`（可选诊断器，缺失时使用本 Skill 的 AI 痕迹门禁） |
| `wechat-content-strategy` | 源码位于本仓库 `companion-skills/wechat-content-strategy`；修复指向该目录的同级运行时联接 |
| `wechat-style-learning` | 源码位于本仓库 `companion-skills/wechat-style-learning`；修复指向该目录的同级运行时联接 |
| `creator-buddy` | `帮我安装 https://github.com/SpaceZephyr/creator-buddy` |
| `gzh-explosive-content-detector` | `creator-buddy` 的必需公众号分支；重新安装或修复 `creator-buddy` |
| `global-content-search` | `creator-buddy` 的子 Skill；安装 Agent Reach 与 OpenCLI，并连接用户明确控制的 Chrome 会话 |
| `aihot` | 重新安装或修复本机 `aihot` Skill |
| `guizang-social-card-skill` | `帮我安装 https://github.com/op7418/guizang-social-card-skill` |
| `ian-xiaohei-illustrations` | `帮我安装 https://github.com/helloianneo/ian-xiaohei-illustrations` |
| `baoyu-article-illustrator` | `帮我安装 https://github.com/JimLiu/baoyu-skills`（只需 baoyu-article-illustrator） |
| `gzh-design` | `帮我安装 https://github.com/isjiamu/gzh-design-skill` |
| `imagegen` | 可选的 Codex 图片 Skill；未发现时仅提示，由所选路线继续解析可用图片后端 |

正文配图至少需要 `ian-xiaohei-illustrations` 或 `baoyu-article-illustrator` 其中一条轨道可用；两条都不可用时阻塞视觉阶段。`optional_missing: ["imagegen"]` 只表示未发现独立的 `imagegen` Skill，不代表当前 runtime 一定没有原生图片工具。由所选路线继续解析真实后端；确实没有可用后端时才阻塞该配图资产。

读取 `references/skill-routing.md` 决定真实调用对象，并按 `references/quality-gates.md` 执行对应门禁；本节不复述视觉、HTML 或 Cheat 的 owner 规则。

系统还必须安装 Git。`validate_project.py profile` 使用的 `git init` 和 `git check-ignore` 只能在隔离的临时 Git 仓库中运行，不得写入被验证账号目录。它会在那里验证 `bindings.local.json` 被 `.gitignore` 排除；Git 不可用时账号验证不得通过。

### 跨 Skill 稳定验证接口

对伴生 Skill（如 `wechat-style-learning`）承诺稳定的验证接口只有一个：

```text
python <WECHAT_ARTICLE_ROOT>/scripts/validate_project.py profile <账号目录>
```

稳定承诺范围：`profile` 子命令存在、JSON 输出形状
`{"ok": bool, "errors": [...]}` 以及退出码（0 通过 / 1 失败）。`article`
子命令和验证器内部模块（`validate_profile.py`、`validate_article.py`、
`validate_html_delivery.py`、`security_scan.py`、`project_checks.py`）属于
本 Skill 内部实现，不向伴生 Skill 承诺稳定；伴生 Skill 不得直接 import
这些模块，只能调用上面的 CLI。

### 升级已安装的 Skill

用户说「更新所有 skill」「更新依赖」「检查 skill 更新」时：

1. 运行 `python <SKILL_ROOT>/scripts/dependency_check.py --stage account` 拿到已安装 skill 的路径列表（`available` 数组）。
2. `dependency_check.py` 本身不输出路径。改用 `python <SKILL_ROOT>/scripts/dependency_check.py --stage html`，从 `available` 取到 skill 名，再按 Git 搜索逻辑找到每个 skill 的实际目录。更直接的方式：直接搜索各 runtime skills 目录下的 git 仓库。
3. 对每个 skill 目录执行：`git -C <目录> pull --ff-only 2>&1`。用 `--ff-only` 避免合并冲突意外改写本地文件。
4. 汇总报告：

| Skill | 状态 |
|---|---|
| `human-writing` | 已更新 (旧哈希 -> 新哈希) |
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
   [`references/cheat-contracts.md`](cheat-contracts.md#post-migrate-cheat-status-receipt) 生成并验证
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

## 第四步：执行文章流水线

文章绑定标准长期账号画像时，在进入大纲和初稿前解析画像并读取 `voice.md`、
`content-patterns.md` 和 `references/writing-style.md`。将 `voice.md` 和
`style-learning:validated` 区块作为作者声音的硬约束，将 `style-learning:provisional`
区块作为主动选择的实验。优先级依次为：用户当次明确要求与已核验事实/证据/经历/观点、
账号文风与已验证规则、文风执行卡、`human-writing` 的材料与自然中文规则、未选中的通用建议。
不得为套用任何文风新增素材。

下表只适用于 `content_kind=long-essay`；贴图使用上面的轻量项目，不进入本表。

| 阶段 | 动作 | 产物或真实来源 |
|---|---|---|
| 简报 | 明确主题、受众、观点、材料、字数和时效 | `brief.md` |
| 选题 | 执行 [`references/topic-signal-registry.md`](topic-signal-registry.md) 并等待用户确认角度 | `topic-brief.md` + Cheat 引用 |
| 调研 | 核查当前事实和原始来源 | `research/evidence.md`、`research/sources.json` |
| 大纲 | 调用 `wechat-content-strategy`，从已核验材料选择一种内容增强策略，确定中心论点、文章级写作参数、文风执行卡、结构、证据位置和编辑锚点 | `outline.md` |
| 活人感主执行 | 调用 `human-writing`，按公众号长文与现实题材规则检查材料、说话位置、段落推进和自然中文；材料不足时先补研究、补问或缩短 | 写作约束，不直接替代账号声音 |
| 初稿 | 由本 Skill 按“账号声音 + human-writing”融合起草；不得调用外部作者文风 Skill 或让通用规则覆盖账号声音 | `drafts/draft-v1.md` |
| 审校 | 初稿后读取 `human-writing` 改稿规则并运行 `check_prose.py`，再按 `references/quality-gates.md` 做事实、结构、账号适配和文笔终检；`humanizer-zh` 仅作该门禁允许的可选诊断 | `drafts/final.md` |
| 终稿观察 | 持续学习启用时，终稿批准并锁定 SHA256 后提炼 0–5 条跨篇候选，写入观察账本；只学习用户最终保留的选择，不把第三方 Skill 通用规则自动写成个人文风 | `<account_profile>/history/voice-observations/` |
| 预测 | 先验证 `cheat-form-receipt.json`：根 Cheat 调用完成且当前内容形态 rubric 已适配；再运行 `scripts/cheat_prediction_adapter.py` 生成哈希绑定的只读 Cheat 输入，最后调用根 Cheat 的 predict | `cheat-form-receipt.json` + `prediction-input-reference.json` + Cheat 预测引用 |
| 视觉 | 执行 `references/quality-gates.md` 的视觉门禁和下方适配命令 | `visuals/visual-plan.md`、`visuals/assets/manifest.json`、`visuals/assets/` |
| 排版 | 执行 `references/quality-gates.md` 的 HTML 门禁和下方固定映射 | `output/article.html`、`output/article-preview.html`、`output/article-copy.html`、`output/article-copy-preview.html`、`output/html-qc.md` |
| 发布 | 人工复制已验证 HTML；用户确认公开后先真实调用 Cheat publish，再运行总控发布桥写入回执 | `publish.json` + `publish-reference.json` |
| 复盘 | 公开发布后把人工 WeChat 数据写入 `metrics.json`，再调用 Cheat 回收和演化 | `metrics.json` + Cheat 复盘引用 |

Cheat 的公开路由、根调用与排除规则只见 `SKILL.md` 核心约束第 1 条。

### 选题信号汇聚

完整 lane、后端、状态、去重、Cheat 交接和用户确认流程只见
[`references/topic-signal-registry.md`](topic-signal-registry.md)。执行后写入
`topic-brief.md`，再进入调研。

### 内容策略与改稿学习路由

- 普通端到端创作始终由本 Skill 总控；在证据关卡通过后内部调用 `wechat-content-strategy`。
- 用户明确只要选题深化、内容增强或大纲时，仍先由本 Skill 补齐 Cheat 决策和事实前置，再允许直接进入 `wechat-content-strategy`。
- 用户明确说“学习我的修改”“沉淀文风”时，检查长期账号、初稿和人工定稿，再调用 `wechat-style-learning`。先展示候选规则，用户确认后才写入账号学习账本。
- 用户明确启用“持续学习”后，每篇已批准终稿都调用 `wechat-style-learning observe-final`；观察结果只进入软观察层，至少 3 篇不同文章重复且无冲突后标记为 `candidate`，晋级硬规则前仍展示并取得确认。
- 学习动作不改变当前文章内容、审批、预测或状态，也不触发当前文章的 stale 传播；新规则从下一篇文章开始生效。

调研与事实、预测、视觉和 HTML 阶段读取 `references/quality-gates.md`；大纲、起草与
审校阶段再配合 `references/writing-style.md`。进入交付或外部写入时读取
`references/publishing.md`。

## 预测与审批

保留五类总控确认：账号配置、选题角度、大纲事实边界、最终正文、视觉交付。视觉交付包含出图前的视觉计划确认和排版后的 HTML 确认。

预测的终稿哈希、内容形态、盲评分与不可变记录门禁只按
`references/quality-gates.md` 和 `references/cheat-contracts.md` 执行；本节不复述规则。

外部 Skill 的硬性确认和快速模式边界见对应 owner 门禁；本节只保留命令与产物路径。

## 视觉与 HTML

视觉规则只见 `references/quality-gates.md` 的视觉门禁。在
`visuals/visual-plan.md` 记录获批计划后，把封面 route 输出交给总控适配器：

```text
python <SKILL_ROOT>/scripts/visual_asset_adapter.py cover <PROJECT_ROOT> --route guizang --source <GUIZANG_OUTPUT>/wechat-21x9-cover.png --route-output-dir <GUIZANG_OUTPUT>
```

每个获批正文锚点都用总控适配器登记：

```text
python <SKILL_ROOT>/scripts/visual_asset_adapter.py body <PROJECT_ROOT> --route ian --source <IAN_OUTPUT>/anchor-emotion.png --anchor-id anchor-emotion --information-job "narrative tension" --provenance-ref <IAN_OUTPUT_REF>
python <SKILL_ROOT>/scripts/visual_asset_adapter.py body <PROJECT_ROOT> --route baoyu --source <BAOYU_OUTPUT>/anchor-flow.png --anchor-id anchor-flow --information-job "ordered steps" --provenance-ref <BAOYU_OUTPUT_REF>
```

完成全部选定资产后，用
`python <SKILL_ROOT>/scripts/article_state.py record <PROJECT_ROOT> --role visuals --path visuals/assets/manifest.json`
把 manifest 纳入文章状态。

选择 Baoyu 轨道时，运行
`python <SKILL_ROOT>/scripts/baoyu_adapter.py prepare <文章目录>`，把生成的
`visuals/assets/baoyu/source.md` 交给根 Skill；结束后运行
`python <SKILL_ROOT>/scripts/baoyu_adapter.py verify <文章目录>`。

HTML 规则只见 `references/quality-gates.md` 的 HTML 门禁。通过 `gzh-design`
取得并校验纯 section 后，按以下固定映射生成项目产物。

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

   复制加固、图片内嵌和 pasted-DOM 验收标准见 HTML 门禁。
5. 按 `assets/article-project-template/output/html-qc.template.md` 生成并填写
   `<PROJECT_ROOT>/output/html-qc.md`，并填写 HTML 门禁要求的全部字段。

每一步都使用实际的绝对 `<SKILL_ROOT>` 与 `<PROJECT_ROOT>`；文件完成前运行
`python <SKILL_ROOT>/scripts/validate_project.py article <PROJECT_ROOT>`。

## 失败与恢复

读取 `references/recovery-rules.md`。上游内容变化时找出最早变更阶段，运行 `python <SKILL_ROOT>/scripts/article_state.py invalidate <文章目录> --stage <阶段>` 并先持久化状态；不要用状态切换代替失效传播，也不要删除有效上游产物。

头图或正文配图失败时保留提示词和错误记录；HTML 失败时停止交付。恢复必须继续到所有受影响的下游 `stale` 项重新生成和验证。

## 发布边界与最终交付

交付包、`html_ready`、`publicly_published`、人工发布边界和失败恢复只按
`references/publishing.md` 执行；本节不复述发布规则。
