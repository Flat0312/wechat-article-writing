## 第三步：建立状态

### 导入账号

1. 如果目录已有标准 `account.json`，先验证并直接使用；不得复制出第二份标准 profile。
2. 否则对该目录运行 `profile_adapter.py preview`。
3. 分开展示会复制的 `mapped` 文档与 `live_linked` Cheat 来源。实时链接来源保留在 Cheat 项目中，通过本地 binding 解析；不得复制进便携 profile。
4. 若存在 `.cheat-state.json`，运行 `python <SKILL_ROOT>/scripts/dependency_check.py --stage account`。报告为 `ok: false` 时，必须在 Cheat 状态检查或导入前停止。
5. 依赖检查通过后，调用根 `cheat-on-content` 检查状态，比较 schema 与 migrations registry。未取得兼容的 `cheat-status` 前不得继续 preview/import。
   对 benchmark 或导入证据用 `cheat-learn-from`，限制在已确认样本范围与目标 Cheat 项目。迁移只在单独批准后对源项目或工作副本运行 `cheat-migrate`；再调 `cheat-status` 并按 [`cheat-contracts.md`](../cheat-contracts.md#post-migrate-cheat-status-receipt) 规范化为 `<账号目录>/cheat-status-receipt.json`。迁移回执失败或缺失会阻塞导入。
6. 若 schema 不兼容，停止只读导入；仅可在明确批准后做源项目或工作副本迁移。
7. 展示 `mapped`、`live_linked`、缺失、冲突和排除字段。
8. 仅在批准后运行 `profile_adapter.py import`，只能写入已确认 workspace 的 `<account_profile>/`。
9. 使用结果前先验证。

适配器的 `approved` 标志只授权本地写入，绝不替代强制的根 `cheat-on-content` 状态检查。

绝不得导入 `.auth`、Cookie、API Key、缓存登录状态或秘密文件。preview 和普通 import 期间绝不得更改源目录。

## 创建长期账号

先调用根 `cheat-on-content`，以 `long-essay` 内容形态完成初始化。保留 Cheat 要求的每一项确认。

Cheat 初始化后，只按三个紧凑分组收集公众号专属上下文：1. 账号身份、创作目标与预期受众。2. 内容赛道、作者证据、边界与声音。3. 历史文章、对标、视觉偏好与交付偏好。

汇总完整 profile 草案。只针对矛盾或缺失字段逐次追问一个问题。写入前展示最终 profile；批准后，用已初始化的 Cheat 项目运行 `profile_adapter.py create`，把批准后的回答写入 profile Markdown 文件并验证结果。

初始化空的可选 `history/edits/index.json`，用于将来已确认的改稿学习。初始化期间不得从导入文件推断文风规则；学习需要用户另行明确请求。

## 临时文章

临时模式要求主题明确。schema 1.1 中长文可在没有持久 profile 的情况下运行调研、写作、编辑、终稿落盘与 Cheat 预测阶段。若用户要求 Cheat 打分、预测、发布登记或复盘，必须提供已有 Cheat 项目，或升级为长期账号模式。绝不得模拟这些动作。

## 学习确认

用户明确要求登记学习时，先展示候选规则；写入账号学习账本前，必须取得单独的用户确认。

## 确认节点（按 schema 分档）

schema 1.1 中长文保留前 4 类（账号配置、主题角度、大纲事实边界、最终正文 + 用户明确确认发布）；schema 1.0 / news-card 保留全部 5 类，末类（视觉交付）由该路径独立触发。1. 账号导入预览或新 profile。2. 主题、角度与受众。3. 提纲、核心主张与事实边界。4. 终稿（schema 1.1：`final.md` 落盘 + final 审批绑定 + 用户明确确认；schema 1.0：Cheat 预测和 HTML 生成前的终稿）。5. （仅 schema 1.0 / news-card）视觉交付：生成前确认方案，排版后确认 HTML。

外部 Skill 自己的强制确认仍然有效。schema 1.0 / news-card 视觉确认按 [`../quality-gates.md`](../quality-gates.md) 的唯一规则覆盖单张 `21:9` 微信主封面和入选的正文配图；方形分享卡无需确认。schema 1.1 中长文不走视觉交付节点。

### 贴图轻量项目

当 `content_kind=news-card` 时，用户界面统一称"贴图"；新闻、资讯、观点梗、截图等不再划分子类。贴图不调用 `article_state.py init`，不进入 long-essay 状态（1.1 九阶段或 1.0 十二阶段）、正式 v1 预测或 rubric 变更流程，只在 canonical 工作区建立独立贴图目录。

普通贴图最小产物是 `caption.md` + `cards/` 与 `cards/manifest.json`；公开后才建立或更新 `publish.json` 与 `metrics.json`。仅当需要核验事实/时效/价格等时增加 `research/evidence.md` 与 `research/sources.json`；多卡信息任务时增加 `card-brief.md`、`card-outline.md`。需要多卡信息结构时调用 `wechat-content-strategy` 的 `news-card` 分支生成 `card-outline.md`。所有贴图共用独立贴图发布/表现池，不得按新闻/梗图/截图另建校准池，不得写入 long-essay v1 或修改其 rubric；2026-08-01 至 2026-08-31 试运行期不得把贴图交给 `wechat-style-learning`。

贴图与 long-essay 同级，公开后都登记发布与数据；普通贴图不以缺少大纲或盲预测阻塞人工发布。进入贴图流程前先运行 `python <SKILL_ROOT>/scripts/dependency_check.py --stage news-card`；AI 账号或 AI 主题改用 `--stage news-card-ai`。贴图执行封面门禁，不进入正文配图或 HTML 阶段。

### 单篇项目

运行 `python <SKILL_ROOT>/scripts/article_state.py init <文章目录> --article-id <ID> --mode <full|fast|temporary>` 创建文章目录（默认 schema 1.1；用 `--schema-version 1.0` 显式创建旧项目）。字段、路径和真实来源遵循 `references/account-profile-schema.md` / `references/article-state-schema.md` / `references/recovery-rules.md`。每次记录产物后运行 `python <SKILL_ROOT>/scripts/validate_project.py article <文章目录>`。
