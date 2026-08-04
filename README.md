# WeChat Article Writing

<p align="center">
  <b>面向 Codex 的微信公众号长文 + 资讯贴图总控 Skill</b><br>
  把账号上下文、选题、事实核查、内容策略、写作、审校、配图、公众号 HTML 排版、
  发布登记与复盘，组织成一条可验证的工作流。
</p>

<p align="center">
  <img alt="Skill" src="https://img.shields.io/badge/Skill-Codex-blueviolet?style=flat-square">
  <img alt="License" src="https://img.shields.io/github/license/Flat0312/wechat-article-writing?style=flat-square">
  <img alt="Platform" src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square">
</p>

## 为什么用这个 Skill

微信公众号创作不只是"写一篇文章"。它是一整条需要留痕的流水线：

| 阶段 | 谁负责 | 产物 |
|---|---|---|
| 选题 | 五路信号汇聚 + Cheat 评分 | `candidates.md` |
| 事实核查 | 来源登记 + 交叉验证 | `research/evidence.md` |
| 策略与大纲 | `wechat-content-strategy` | `outline.md` |
| 初稿 | 账号文风执行卡 + `khazix-writer` 技法辅助 + 融合审校 | `drafts/draft-v1.md` |
| 审校 | 事实、结构、去 AI 痕迹 | `drafts/final.md` |
| 预测 | Cheat 盲预测（immutable） | `predictions/` |
| 视觉 | 21:9 头图 + Ian/Baoyu 配图 | `visuals/` |
| 排版 | `gzh-design` + 九项排版契约 | `output/article.html` |
| 发布 | 人工复制，公开后登记 | `publish.json` |
| 复盘 | Cheat T+2 数据回收 | retro 段 |

每一步都有明确的状态、审批和失效传播，绿测试不等于已交付——发布前的浏览器粘贴
验证和发布后的数据复盘都不可省略。

## 核心特点

- **可验证**：用 `article-state.json` 跟踪阶段、审批和失效传播；审计命令一键检查。
- **先事实后文风**：不新增用户未提供的经历、数字、案例或立场。
- **文风可进化**：账号声音由 `voice.md` 主导，卡兹克提供受边界约束的技法辅助；启用持续学习后，每篇批准终稿都会进入软观察层。
- **五路选题信号**：公众号爆款 + 小红书（本机 Playwright）+ AI HOT + X/Twitter + 综合热榜。
- **两种内容形态**：原创长文与 AI/科技资讯贴图，同级但独立校准。
- **微信排版契约**：21:9 头图、窄屏断行、字号字色、九项排版检查全部可执行。
- **发布边界清晰**：只走人工复制已验证 HTML，不碰草稿箱 API；公开后才允许登记与复盘。

## 安装

### 1. 克隆到 Codex skills 目录

```powershell
git clone https://github.com/Flat0312/wechat-article-writing.git "$env:USERPROFILE\.codex\skills\wechat-article-writing"
```

### 2. 创建伴生 Skill 联接

本仓库同时版本化两个第一方伴生 Skill。首次克隆后，在 Codex skills 目录创建同级
目录联接，让运行时继续按独立 Skill 名称发现它们：

```powershell
$repo = "$env:USERPROFILE\.codex\skills\wechat-article-writing"
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.codex\skills\wechat-content-strategy" `
  -Target "$repo\companion-skills\wechat-content-strategy"
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.codex\skills\wechat-style-learning" `
  -Target "$repo\companion-skills\wechat-style-learning"
```

如果同名路径已存在，先确认它是否是旧副本；不要直接覆盖或删除。

### 3. 开始使用

重新启动 Codex 后，可以这样调用：

```text
使用 $wechat-article-writing 帮我写一篇公众号文章
使用 $wechat-article-writing 做一组资讯贴图
```

## 依赖

本仓库包含总控 Skill，以及 `wechat-content-strategy`、`wechat-style-learning`
两个第一方伴生 Skill；不复制第三方 Skill。不同阶段会使用以下依赖：

- `cheat-on-content` — 评分、预测、发布登记、复盘、rubric
- `khazix-writer` — 必需的技法辅助，不代替账号作者声音
- `humanizer-zh` — 可选的 AI 痕迹诊断器；最终改写受账号文风门禁约束
- `creator-buddy`（含 `gzh-explosive-content-detector`）— 跨平台与公众号爆款信号
- `xiaohongshu-skill` — 小红书热点（本机 Playwright，免费）
- `x-tweet-fetcher` — X/Twitter 推文与长文信号
- `aihot` — AI 主题信号
- `guizang-social-card-skill` — 21:9 头图合成
- `ian-xiaohei-illustrations` / `baoyu-article-illustrator` — 正文配图
- `gzh-design` — 公众号 HTML 排版
- `imagegen`（可选）— 封面照片素材兜底或路由兜底

完整的阶段依赖和安装提示见 [references/execution.md](references/execution.md)。
系统还需要 Git 和 Python 3。

## 验证

```powershell
python -m unittest discover -s tests -v
python scripts/dependency_check.py --stage account
```

依赖检查反映本机安装状态；未安装可选或阶段依赖时，检查会明确列出缺失项。

## 安全与发布边界

- 导入账号默认只读，不复制认证目录、Cookie、密钥、缓存或机器绝对路径。
- 不调用微信公众号草稿箱上传接口或自动发布接口。
- `html_ready` 只表示 HTML 已可供人工复制，不代表文章已经上传或公开发布。
- 第三方 Skill 是运行时依赖，许可证和使用条款以各自项目为准。

## 项目结构

```text
agents/            Codex 界面元数据
assets/            账号与文章项目模板
companion-skills/  第一方内容策略与文风学习 Skill
references/        状态、路由、质量门禁和发布契约
scripts/           依赖检查、状态管理与项目验证脚本
tests/             回归测试
SKILL.md           Skill 主入口
```

## License

[MIT](LICENSE)
