---
name: wechat-article-writing
description: 写公众号文章（schema 1.1 中长文纯文字九阶段，不生成 HTML）、创作微信推送、公众号贴图(21:9 头图)、选题/账号初始化、学习文风、发布登记或复盘.
---

## 核心约束

1. **Cheat 必须真调**：`cheat-init/cheat-learn-from/cheat-seed/cheat-recommend/cheat-score/cheat-predict/cheat-publish/cheat-retro/cheat-persona/cheat-bump/cheat-status/cheat-migrate` 真实调用 `cheat-on-content` 根 Skill；不得模拟/近似/自行排名。`cheat-shoot`/`cheat-trends` 排除；`cheat-score-blind` 仅内部。`cheat-learn-from`、`cheat-status`、`cheat-migrate` 属相关子路由；导入须先 `cheat-status`，schema 不兼容经单独确认后迁移，再按 [`references/cheat-contracts.md`](references/cheat-contracts.md#post-migrate-cheat-status-receipt) 写回执 `cheat-status-receipt.json`。
2. 事实优先：事实/证据/经历/当篇要求＞文风；`references/quality-gates.md`。
3. 只读优先：账号导入/路径/敏感边界`references/onboarding.md`；未确认不写。
4. 状态持久化：`references/recovery-rules.md`；未持久化/stale 不继续。
5. 视觉门禁：`references/quality-gates.md`；schema 1.1 中长文不要求视觉/HTML 门禁，news-card 仍走原 21:9 贴图门禁。
6. 发布只走人工：`references/publishing.md`；不得调用发布 API。
7. 门禁不过=没交付：schema 1.1 中长文只看 final 落盘、final 审批绑定、用户明确确认；旧 schema 1.0 保留原 HTML / 视觉关卡。
8. 第三方 Skill 是运行时依赖：不得 vendoring/复制。

## 入口判断

长期账号→long-essay（schema 1.1 纯文字九阶段）；贴图→news-card（独立 21:9 / guizang）；临时单篇→temporary；已有素材→保留输入。持续学习启用后，SHA256 锁终稿调 `wechat-style-learning observe-final` 写软观察。

## 信号路由

选题信号只走 `references/topic-signal-registry.md` 的八路信号。

## 引用索引

references/execution.md、references/execution/upgrade.md、references/execution/state.md、references/execution/pipeline.md、references/quality-gates.md、references/quality-gates/prediction.md、references/onboarding.md、references/publishing.md、references/skill-routing.md、references/topic-signal-registry.md。`references/execution/visuals-html.md` 与 `references/quality-gates/visual-html.md` 仅作 1.0 历史保留。
