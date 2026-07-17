# WeChat Article Writing

一个面向 Codex 的微信公众号长文总控 Skill。它把账号上下文、选题、事实核查、内容策略、写作、审校、配图、公众号 HTML 排版、发布登记和复盘组织为一条可验证的工作流。

## 特点

- 用 `article-state.json` 跟踪阶段、审批和失效传播。
- 先核查事实，再进行写作和文风编辑。
- 支持长期账号、已有账号导入和临时单篇创作。
- 微信封面固定为单张 21:9 头图，正文配图按内容类型路由。
- 交付经过验证、可手动粘贴到公众号编辑器的 HTML。
- 发布登记与内容复盘通过 `cheat-on-content` 形成校准闭环。

## 安装

将仓库克隆到 Codex skills 目录：

```powershell
git clone https://github.com/Flat0312/wechat-article-writing.git "$env:USERPROFILE\.codex\skills\wechat-article-writing"
```

重新启动 Codex 后，可以这样调用：

```text
使用 $wechat-article-writing 帮我写一篇公众号文章
```

## 依赖

本仓库只包含总控 Skill，不复制第三方 Skill。不同阶段会使用以下依赖：

- `cheat-on-content`
- `khazix-writer`
- `humanizer-zh`
- `wechat-content-strategy`
- `wechat-style-learning`
- `creator-buddy`（含 `gzh-explosive-content-detector`）
- `aihot`（AI 主题）
- `guizang-social-card-skill`
- `ian-xiaohei-illustrations` 或 `baoyu-article-illustrator`
- `gzh-design`
- `imagegen`

完整的阶段依赖和安装提示见 [SKILL.md](SKILL.md)。系统还需要 Git 和 Python 3。

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
agents/       Codex 界面元数据
assets/       账号与文章项目模板
references/   状态、路由、质量门禁和发布契约
scripts/      依赖检查、状态管理与项目验证脚本
tests/        回归测试
SKILL.md      Skill 主入口
```

## License

[MIT](LICENSE)
