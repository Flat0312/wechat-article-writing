---
name: wechat-article-writing
description: Use when users ask to 写公众号文章、创作微信公众号推送、公众号长文改稿、AI/科技新闻资讯贴图、选题与内容增强、账号初始化或导入、学习人工改稿、沉淀公众号文风、微信公众号21:9头图、微信公众号 HTML 排版、公开发布登记或文章数据复盘, including requests such as "帮我写公众号文章", "做一组资讯贴图", "从零写一篇推送", "学习我的修改", or "导入公众号账号状态".
---

## 核心规则

1. 涉及账号初始化、对标学习、选题决策、评分、预测、发布登记、复盘、画像、rubric 或 Cheat schema 迁移时，必须真实调用 `cheat-on-content` 根 Skill。不得模拟其子流程或复制其公式。
相关子路由包括 `cheat-learn-from`、`cheat-status`、`cheat-migrate`；账号导入必须先完成 `cheat-status`，schema 不兼容时取得单独确认后再执行迁移，迁移后仍需取得兼容的 `cheat-status` 结果并按 [`references/cheat-status-receipt.md`](references/cheat-status-receipt.md) 写入 `cheat-status-receipt.json` 回执。
 `cheat-seed` 内部若出现泛名 `humanizer`，按 [`references/cheat-seed-compatibility.md`](references/cheat-seed-compatibility.md) 登记外部不一致；不得安装或模拟该泛名 Skill。
2. 先核查事实，再编辑文风；不得新增用户未提供的经历、数字、案例或立场。
3. 导入账号先预览，默认只读；不得读取或复制认证目录、Cookie、密钥和缓存。
4. 每个阶段更新 `article-state.json`。上游产物变化时先按恢复协议传播 `stale` 并持久化，再继续下游。
5. 微信封面只生成一张 `21:9` 头图，不生成 `1:1` 分享卡。封面合成与文字排版走 `guizang-social-card-skill`；照片素材缺失时允许 ImageGen 生成底图、仍由 guizang 合成文字（素材兜底）；仅当 guizang 本身不可用时，才允许 ImageGen 端到端生成整张封面（路由兜底）。两种兜底都必须显式标注。正文配图按单个认知锚点选择单一路线：隐喻、情绪、叙事转折和身份表达走 Ian；有序步骤、层级、对比、矩阵、时间线、精确标签和证据数值走 `baoyu-article-illustrator`。同一锚点不得默认双轨生成，除非用户明确要求 A/B。所有视觉成品必须经 `scripts/visual_asset_adapter.py` 收回 `visuals/assets/` 并登记 `visuals/assets/manifest.json`；外部默认输出目录只作 provenance。HTML 排版走 `gzh-design` 时必须把 [`references/wechat-layout-contract.md`](references/wechat-layout-contract.md) 的 8 条契约（3 文本级 + 5 视觉级）作为不可选的上位约束传入；主题组件与契约冲突时省略该组件或改用更简洁的兼容组件。
6. 发布只采用人工复制已验证 HTML 的路线；不得调用 `wechat-publisher`、其他草稿箱上传适配器或自动发布接口。
7. 未通过事实、视觉或 HTML 强制关卡时，不得声称完整交付。
8. 第三方 Skill 是运行时依赖；不得把它们复制或 vendoring 到本 Skill。
9. 选题与事实调研完成后，调用 `wechat-content-strategy` 完成内容增强和大纲；它不得自行补造证据或替代 Cheat 决策。
10. 只有长期账号且用户明确要求学习改稿或持续进化时，才调用 `wechat-style-learning`。持续学习启用后，每篇已批准终稿自动写入 `history/voice-observations/` 作为软观察；正式 draft/final 学习和硬规则晋级仍须遵守候选预览与确认边界，并且只影响后续文章。
11. 中长文与资讯贴图的选题统一按 [`references/topic-signal-registry.md`](references/topic-signal-registry.md) 汇聚五路信号（五个已登记 lane）：`creator-buddy-cross-platform`、`gzh-explosive-content-detector`、AI 主题条件路由 `aihot`、`x-tweet-fetcher` 和 `cheat-trends`。小红书关键词热度走本机 `xiaohongshu-skill`；公众号分支若判定为通用关键词，必须先取得用户确认的扩展选择。非 AI 主题把 `aihot` 记为 `not_applicable`，不得用模型记忆补位。五路候选归一化、去重并保留来源后，必须交给根 `cheat-on-content` 评分和决策，再由用户确认选题角度。
12. Cheat 子路由按公众号场景裁剪：`cheat-shoot` 只服务视频拍摄登记，不调用；`cheat-trends` 只负责补充、去重和粗筛热点候选，不替代 `creator-buddy`、公众号爆款或 `aihot`，也不替代最终的 Cheat 推荐；`cheat-score-blind` 只能由 Cheat 的 score、predict 或 bump 流程内部调用。
13. 文章绑定标准长期账号画像时，在大纲和初稿前读取 `voice.md` 与 `content-patterns.md`。将 `voice.md` 和已验证规则作为作者声音的硬约束，将待验证规则作为可选实验；事实、证据、用户明确提供的经历、观点和当篇要求高于任何文风规则，不得为套用文风新增素材。先按 `outline.md` 的“文风执行卡”锁定你的声音，再按 [`references/khazix-craft-contract.md`](references/khazix-craft-contract.md) 调用 `khazix-writer` 作为必需的技法辅助并通过 `craft_only_adapter.py`，最后由本 Skill 完成融合起草与审校。卡兹克只能提供结构、节奏、场景、类比和自检建议，不得带入其作者身份、口癖、粗口、固定标点、固定结构或固定结尾。
14. `content_kind=news-card` 的资讯贴图与 long-essay 同级：同样进入发布登记、盲预测与复盘闭环；但走独立轻量建档分支，不进入 long-essay 的 12 阶段 `article-state.json`，也不参与 long-essay v1 正式预测或 rubric 变更流程。发布与数据单独记录；校准使用独立的 news-card 池，不得与 long-essay v1 校准池混池，试运行期不得进入 `wechat-style-learning`。进入贴图流程前先运行 `python <SKILL_ROOT>/scripts/dependency_check.py --stage news-card`；AI 账号或 AI 主题改用 `--stage news-card-ai`。贴图卡图走 guizang 合成（首选）或 imagegen 端到端兜底（与 long-essay 头图相同的 `21:9` 单图契约），不进入 long-essay 的 Ian/Baoyu 正文配图轨道，也不要求 `gzh-design` HTML 门禁（贴图直接交付图片）。预测前同样区分真实 Cheat 调用状态与对应 `content_form` 的 rubric 适配状态；缺少适配回执时不得把流程调用记为可校准预测。
15. 资讯贴图素材抓取使用本机 `x-tweet-fetcher`（`C:\Users\33158\.codex\tools\x-tweet-fetcher`，虚拟环境 `\.venv\Scripts\xtf.exe`）：
    - `--url <推文链接>`：抓单条推文（含推文内嵌长文全文），零依赖，无需登录。
    - `--article <文章链接或ID>`：抓 X 长文，需要浏览器后端（Playwright/Camofox）；未登录时只能拿到标题与公开预览（`is_partial: true`）。
    - `--user <用户名>` / `--search <关键词>`：抓时间线或搜索，需要自建 Nitter 实例（`XTF_NITTER`）。
    抓取结果以 JSON/Markdown 存入 `news-cards/<slug>/research/x-raw/`，来源逐条登记进 `research/sources.json`。抓取内容只作素材与事实核查依据，不得直接作为发布正文；贴图仍须满足“发生了什么 / 为什么值得关注 / 账号一句判断”三要素并标注来源。
16. 小红书一切数据（热点搜索、笔记详情、评论、长文抓取）一律使用本机 `xiaohongshu-skill`（`C:\Users\33158\.codex\skills\xiaohongshu-skill`，Playwright 驱动，二维码登录）：
    - 搜索热点：`python -m scripts search "<关键词>" --sort-by=最多点赞 --note-type=图文 --limit=10`（在 skill 目录下执行）。
    - 读取帖子详情与评论（含长文正文）：`python -m scripts feed <feed_id> <xsec_token> --load-comments`。
    - 不使用红狐 key（REDFOX_API_KEY），也不把 RedFox/socialdatax/怪壳当作默认路线；这些外部 Key 未配置或余额不足时不得报错终止，直接改用本技能。
    抓取结果以 JSON/Markdown 存入 `news-cards/<slug>/research/`，链接必须原样保留 `xsec_token`，来源逐条登记进 `research/sources.json`。
17. 长文起草与审校必须读取 `references/writing-style.md`。先完成事实与结构，再做文笔、账号文风和去 AI 痕迹检查；`humanizer-zh` 只可按 [`references/humanizer-diagnostic-contract.md`](references/humanizer-diagnostic-contract.md) 作为可选诊断参考并通过 `humanizer_diagnostic_adapter.py`，其输出不得整篇覆盖正文、注入未经用户提供的个性细节，或削弱已确认的账号声音。持续学习启用时，最终正文批准且 SHA256 锁定后，调用 `wechat-style-learning` 的 `observe-final` 记录跨篇候选。

## 执行手册

- 入口判断、账号导入、长期账号初始化、临时创作和单篇项目初始化见 `references/onboarding.md`。
- 运行时依赖、缺失安装指引、Skill 更新流程和各阶段命令见 `references/execution.md`。
- 路由规则、信号汇聚、学习约束和排除能力见 `references/skill-routing.md`。
- 事实、写作、视觉和 HTML 检查标准见 `references/quality-gates.md`；微信长文排版契约见 `references/wechat-layout-contract.md`。
- 文风优先级、文风执行卡、起草方法和文笔终检见 `references/writing-style.md`。
- 上游变更失效传播和恢复协议见 `references/recovery-rules.md`。
- 交付、人工发布和复盘边界见 `references/publishing.md`。
