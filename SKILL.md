---
name: wechat-article-writing
description: Use when users ask to 写公众号文章、创作微信公众号推送、公众号长文改稿、公众号贴图（新闻、资讯、观点梗、截图等）、选题与内容增强、账号初始化或导入、学习人工改稿、沉淀公众号文风、微信公众号21:9头图、微信公众号 HTML 排版、公开发布登记或文章数据复盘, including requests such as "帮我写公众号文章", "做一组贴图", "从零写一篇推送", "学习我的修改", or "导入公众号账号状态".
---

## 核心约束（不可违反）

1. **Cheat 必须真调**：`cheat-init`、`cheat-learn-from`、`cheat-seed`、`cheat-recommend`、`cheat-score`、`cheat-predict`、`cheat-publish`、`cheat-retro`、`cheat-persona`、`cheat-bump`、`cheat-status`、`cheat-migrate` 全部真实调用 `cheat-on-content` 根 Skill，由它选择内部流程。不得模拟、复现、复制或近似其公式与协议，也不得自行排名候选。`cheat-shoot`、`cheat-trends` 不服务公众号场景；`cheat-score-blind` 只由 Cheat 内部调用。账号导入先完成 `cheat-status`；schema 不兼容时取得单独确认后执行迁移，迁移后仍需取得兼容回执并写入 `cheat-status-receipt.json`。
2. **事实优先**：事实与证据的唯一完整规则见 `references/quality-gates.md`；事实、证据、用户明确提供的经历和当篇要求高于任何文风规则。
3. **只读优先**：账号导入、路径和敏感信息边界以 `references/onboarding.md` 为唯一规则；未确认目标前不得写入。
4. **状态持久化**：状态与失效传播以 `references/recovery-rules.md` 为唯一规则；未持久化当前阶段或上游 `stale` 前不得继续下游。
5. **视觉门禁**：封面与正文配图的唯一完整规则见 `references/quality-gates.md`；任何路线或总控适配器失败都不得标记视觉完成。
6. **发布只走人工**：交付与公开状态以 `references/publishing.md` 为唯一规则；不得调用任何发布 API。
7. **门禁不通过 = 没交付**：事实、视觉、HTML 任一强制关卡未通过时，不得声称完整交付。
8. **第三方 Skill 是运行时依赖**：不得 vendoring 或复制到本 Skill。

## 入口判断（按用户场景分流）

按以下顺序判断用户当前请求属于哪条路径，按需加载对应 references：

| 用户场景 | 走哪条 | 关键差异 |
|---|---|---|
| 长期账号创作 | long-essay 路径 | 12 阶段流水线 + cheat 全程 + 可选风格学习 |
| 贴图（新闻/资讯/观点梗/截图） | news-card 轻量路径 | 跳过 12 阶段，不进 long-essay v1 校准池 |
| 临时单篇 | temporary 路径 | 不生成长期账号包，需要 cheat 时复用现有项目 |
| 已有主题/素材/初稿 | 保留输入 | 跳过选题与调研阶段，直接进入下游 |

用户给出明确目录、主题、素材、初稿或角度时保留该输入，不强迫回到任何起点。

持续学习启用后，已批准且 SHA256 锁定的终稿调用 `wechat-style-learning observe-final` 写入软观察账本；不得据此自动晋级硬规则。

## 执行手册（按需加载，不在主流程注入）

| 步骤 | 引用 |
|---|---|
| 入口判断、账号导入、长期账号初始化、临时创作、单篇项目初始化 | `references/onboarding.md` |
| 依赖检查、Skill 更新、状态建立、文章流水线、视觉、HTML、发布、复盘 | `references/execution.md` |
| 路由规则、信号汇聚、Cheat 子路由、风格学习约束与排除能力 | `references/skill-routing.md` |
| 事实、写作、视觉、HTML 检查标准 | `references/quality-gates.md` |
| 微信长文排版契约 | `references/wechat-layout-contract.md` |
| 文风优先级、文风执行卡、起草方法、文笔终检 | `references/writing-style.md` |
| 上游变更失效传播与恢复协议 | `references/recovery-rules.md` |
| 交付、人工发布、复盘边界（含 xhs 二次分发） | `references/publishing.md` |

## 细则索引（按需查阅，不进 system prompt）

- `references/topic-signal-registry.md` — 八路信号编排、状态、去重与 Cheat 决策交接
- `references/skill-routing.md` — 外部 Skill 职责、排除能力与平台分发
- `references/account-profile-schema.md` — 账号 `directories` 字段映射与默认目录约定
- `references/cheat-contracts.md` — Cheat 形态、迁移、预测、seed 兼容与盲评分边界
- `references/external-contracts.md` — Humanizer、CTA、Creator Buddy、fixture 与视觉清单边界
