---
name: wechat-article-writing
description: Use when users ask to 写公众号文章、创作微信公众号推送、公众号长文改稿、选题与内容增强、账号初始化或导入、学习人工改稿、沉淀公众号文风、微信公众号21:9头图、微信公众号 HTML 排版、公开发布登记或文章数据复盘, including requests such as "帮我写公众号文章", "从零写一篇推送", "学习我的修改", or "导入公众号账号状态".
---

## 核心规则

1. 涉及账号初始化、对标学习、选题决策、评分、预测、发布登记、复盘、画像、rubric 或 Cheat schema 迁移时，必须真实调用 `cheat-on-content` 根 Skill。不得模拟其子流程或复制其公式。
  相关子路由包括 `cheat-learn-from`、`cheat-status`、`cheat-migrate`；账号导入必须先完成 `cheat-status`，schema 不兼容时取得单独确认后再执行迁移，迁移后仍需取得兼容的 `cheat-status` 结果。
2. 先核查事实，再编辑文风；不得新增用户未提供的经历、数字、案例或立场。
3. 导入账号先预览，默认只读；不得读取或复制认证目录、Cookie、密钥和缓存。
4. 每个阶段更新 `article-state.json`。上游产物变化时先按恢复协议传播 `stale` 并持久化，再继续下游。
5. 微信封面只生成一张 `21:9` 头图，并且只走 `guizang-social-card-skill`；不生成 `1:1` 分享卡。正文配图按单个认知锚点选择单一路线：隐喻、情绪、叙事转折和身份表达走 Ian；有序步骤、层级、对比、矩阵、时间线、精确标签和证据数值走 `baoyu-article-illustrator`。同一锚点不得默认双轨生成，除非用户明确要求 A/B。
6. 发布只采用人工复制已验证 HTML 的路线；不得调用 `wechat-publisher`、其他草稿箱上传适配器或自动发布接口。
7. 未通过事实、视觉或 HTML 强制关卡时，不得声称完整交付。
8. 第三方 Skill 是运行时依赖；不得把它们复制或 vendoring 到本 Skill。
9. 选题与事实调研完成后，调用 `wechat-content-strategy` 完成内容增强和大纲；它不得自行补造证据或替代 Cheat 决策。
10. 只有长期账号且用户明确要求学习改稿时，才调用 `wechat-style-learning`；候选规则经用户确认后才能持久化，并且只影响后续文章。
11. 选题采用三路信号汇聚：`creator-buddy` 提供跨平台信号，并显式路由 `gzh-explosive-content-detector` 提供公众号爆款数据；若被分类为通用关键词，必须先取得用户确认的扩展选择后再继续。AI 账号或 AI 主题再调用 `aihot`。三路候选归一化、去重并保留来源后，必须交给根 `cheat-on-content` 评分和决策，再由用户确认选题角度。
12. Cheat 子路由按公众号场景裁剪：`cheat-shoot` 只服务视频拍摄登记，不调用；热点采集由上述三路信号负责，不调用 `cheat-trends`；`cheat-score-blind` 只能由 Cheat 的 score、predict 或 bump 流程内部调用。

## 执行手册

- 入口判断、账号导入、长期账号初始化、临时创作和单篇项目初始化见 `references/onboarding.md`。
- 运行时依赖、缺失安装指引、Skill 更新流程和各阶段命令见 `references/execution.md`。
- 路由规则、信号汇聚、学习约束和排除能力见 `references/skill-routing.md`。
- 事实、写作、视觉和 HTML 检查标准见 `references/quality-gates.md`。
- 上游变更失效传播和恢复协议见 `references/recovery-rules.md`。
- 交付、人工发布和复盘边界见 `references/publishing.md`。
