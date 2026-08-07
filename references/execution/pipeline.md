## 第四步：执行文章流水线

文章绑定标准长期账号画像时，在进入大纲和初稿前解析画像并读取 `voice.md`、`content-patterns.md` 和 `references/writing-style.md`。将 `voice.md` 和 `style-learning:validated` 区块作为作者声音的硬约束，将 `style-learning:provisional` 区块作为主动选择的实验。优先级依次为：用户当次明确要求与已核验事实/证据/经历/观点、账号文风（`voice.md`＋已验证规则）与 `human-writing` 同权重并列、文风执行卡、未选中的通用建议。同层内部不得互相覆盖，账号文风不得整段压掉 `human-writing` 的活人感执行。不得为套用任何文风新增素材。

下表只适用于 `content_kind=long-essay`；贴图使用上面的轻量项目，不进入本表。

| 阶段 | 动作 | 产物或真实来源 |
|---|---|---|
| 简报 | 明确主题、受众、观点、材料、字数和时效 | `brief.md` |
| 选题 | 执行 [`references/topic-signal-registry.md`](../topic-signal-registry.md) 并等待用户确认角度 | `topic-brief.md` + Cheat 引用 |
| 调研 | 核查当前事实和原始来源 | `research/evidence.md`、`research/sources.json` |
| 大纲 | 调用 `wechat-content-strategy`，从已核验材料选择一种内容增强策略，确定中心论点、文章级写作参数、文风执行卡、结构、证据位置和编辑锚点 | `outline.md` |
| 活人感主执行 | 调用 `human-writing`，按公众号长文与现实题材规则检查材料、说话位置、段落推进和自然中文；材料不足时先补研究、补问或缩短 | 写作约束，不直接替代账号声音 |
| 初稿 | 由本 Skill 按"账号声音 + human-writing"融合起草；不得调用外部作者文风 Skill 或让通用规则覆盖账号声音 | `drafts/draft-v1.md` |
| 审校 | 初稿后读取 `human-writing` 改稿规则并运行 `check_prose.py`，再按 `references/quality-gates.md` 做事实、结构、账号适配和文笔终检；`humanizer-zh` 仅作该门禁允许的可选诊断 | `drafts/final.md` |
| 终稿观察 | 持续学习启用时，终稿批准并锁定 SHA256 后提炼 0–5 条跨篇候选，写入观察账本 | `<account_profile>/history/voice-observations/` |
| 预测 | 先验证 `cheat-form-receipt.json`：根 Cheat 调用完成且当前内容形态 rubric 已适配；再运行 `scripts/cheat_prediction_adapter.py` 生成哈希绑定的只读 Cheat 输入，最后调用根 Cheat 的 predict | `cheat-form-receipt.json` + `prediction-input-reference.json` + Cheat 预测引用 |
| 视觉 | schema 1.0 长文 / news-card 才走：`references/quality-gates.md` 的视觉门禁 | `visuals/visual-plan.md`、`visuals/assets/manifest.json` |
| 排版 | schema 1.0 长文才走：`references/quality-gates.md` 的 HTML 门禁 | `output/article.html`、`output/article-preview.html`、`output/article-copy.html`、`output/article-copy-preview.html`、`output/html-qc.md` |
| 发布 | 人工复制已验证 final.md（1.1）或 article-copy.html（1.0）；用户确认公开后先真实调用 Cheat publish，再运行总控发布桥按 schema 分流校验 | `publish.json` + `publish-reference.json` |
| 复盘 | 公开发布后把人工 WeChat 数据写入 `metrics.json`，再调用 Cheat 回收和演化 | `metrics.json` + Cheat 复盘引用 |

Cheat 的公开路由、根调用与排除规则只见 `SKILL.md` 核心约束第 1 条。

### 选题信号汇聚

完整 lane、后端、状态、去重、Cheat 交接和用户确认流程只见 [`references/topic-signal-registry.md`](../topic-signal-registry.md)。执行后写入 `topic-brief.md`，再进入调研。

### 内容策略与改稿学习路由

- 普通端到端创作始终由本 Skill 总控；在证据关卡通过后内部调用 `wechat-content-strategy`。
- 用户明确只要选题深化、内容增强或大纲时，仍先由本 Skill 补齐 Cheat 决策和事实前置，再允许直接进入 `wechat-content-strategy`。
- 用户明确说"学习我的修改""沉淀文风"时，检查长期账号、初稿和人工定稿，再调用 `wechat-style-learning`。先展示候选规则，用户确认后才写入账号学习账本。
- 用户明确启用"持续学习"后，每篇已批准终稿都调用 `wechat-style-learning observe-final`；观察结果只进入软观察层，至少 3 篇不同文章重复且无冲突后标记为 `candidate`，晋级硬规则前仍展示并取得确认。
- 学习动作不改变当前文章内容、审批、预测或状态，也不触发当前文章的 stale 传播。

调研与事实、预测阶段读取 `references/quality-gates.md`；大纲、起草与审校阶段再配合 `references/writing-style.md`。交付时读取 `references/publishing.md`。schema 1.1 中长文不再读取视觉 / HTML 门禁（不调 `gzh-design`、不生成 `output/article.html`）；schema 1.0 项目仍按 `references/quality-gates.md` 的视觉 / HTML 段执行以保历史回放。

## 预测与审批

总控确认节点按 schema 区分：schema 1.1 中长文保留四类（账号配置、选题角度、大纲事实边界、最终正文 + 用户明确确认发布）；schema 1.0 / news-card 保留五类（再加视觉交付）。schema 1.1 的"最终正文"= `final.md` 落盘 + final 审批绑定；schema 1.0 / news-card 的"视觉交付"包含出图前的视觉计划确认和排版后的 HTML 确认。

预测的终稿哈希、内容形态、盲评分与不可变记录门禁只按 `references/quality-gates.md` 和 `references/cheat-contracts.md` 执行；本节不复述规则。

外部 Skill 的硬性确认和快速模式边界见对应 owner 门禁；本节只保留命令与产物路径。
