---
name: WeChat Article Execution
description: Detailed execution runbook for dependency checks, project setup, schema 1.1 long-essay, news-card, publishing, and recovery.
---

# WeChat Article Execution

详细执行手册，和 `SKILL.md` 一起阅读。前者保留核心约束和入口判断，这里保留可执行步骤、产物路径和阶段命令。schema 1.1 中长文是默认入口，schema 1.0 路径（HTML 五件套）仅作历史兼容。

## 第一步：选择入口

读取 `references/onboarding.md`，判断用户属于：

- 导入已有账号。
- 新建长期账号。
- 临时创作单篇文章。

用户给出目录时先只读检查；已给出明确主题、素材或初稿时保留它们，不强迫回到选题起点。

### 项目工具契约

若 workspace 根含 `tools/project_ops.py` 与 `docs/PROJECT-GOVERNANCE.md`，先读治理约定；项目命令只由总控按需调用 `audit`、`status --write`、`calibration --write`、`trends --write`、`writing-learning --write`、`skill-lock --write`。

## 第二步：检查依赖

将本 Skill 的绝对目录记为 `SKILL_ROOT`。所有 `scripts/` 和 `references/` 路径都相对 `SKILL_ROOT` 解析；执行时必须拼成绝对路径，不得依赖当前工作目录。以脚本帮助为 stage 清单的唯一来源，再运行当前阶段：

```text
python <SKILL_ROOT>/scripts/dependency_check.py --help
python <SKILL_ROOT>/scripts/dependency_check.py --stage <STAGE>
```

### 依赖缺失处理

`ok: false` 时按四个 `missing` 列表给安装指引，并保留 `skill_presence`、`script_runtime`、`cli_runtime` 三类回执；目录发现不能覆盖 runtime 失败。常见缺失与安装命令：

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
| `gzh-design` | `帮我安装 https://github.com/isjiamu/gzh-design-skill`（仅 1.0 长文） |
| `imagegen` | 可选 Codex 图片 Skill；未发现时仅提示，由所选路线继续解析可用后端 |

正文配图至少需要 `ian-xiaohei-illustrations` 或 `baoyu-article-illustrator` 之一可用；两条都不可用时阻塞视觉阶段。**schema 1.1 长文不要求正文配图轨道**——只有 1.0 长文和 news-card 触发该检查。

读取 `references/skill-routing.md` 决定真实调用对象，并按 `references/quality-gates.md` 执行门禁；schema 1.1 中长文以 `text-only-long-essay` 作为 dependency_check 入口（cheat-on-content、wechat-content-strategy、human-writing，不要求 gzh-design）。

Git 必须可用；`validate_project.py profile` 的 Git 操作只能在隔离临时仓库，不能写入账号目录。

### 跨 Skill 稳定验证接口

对伴生 Skill 承诺稳定的验证接口只有 `python <WECHAT_ARTICLE_ROOT>/scripts/validate_project.py profile <账号目录>`，输出 `{"ok": bool, "errors": [...]}`，退出码 0/1。`article` 子命令和验证器内部模块（`validate_profile.py`、`validate_article.py`、`validate_html_delivery.py`、`security_scan.py`、`project_checks.py`）属于本 Skill 内部实现，不向伴生 Skill 承诺稳定。

## 第三步：建立状态

账号迁移后先完成 `cheat-status`；schema 不兼容时取得授权后再迁移。执行 `cheat-migrate` 后按 [`references/cheat-contracts.md`](cheat-contracts.md#post-migrate-cheat-status-receipt) 生成并验证 `<账号目录>/cheat-status-receipt.json`；缺失或失败时停止导入。

## 第四步：执行文章流水线

选题：执行 [`references/topic-signal-registry.md`](topic-signal-registry.md) 并确认角度 → `topic-brief.md`。
预测：先验证 `cheat-form-receipt.json`，再运行 `scripts/cheat_prediction_adapter.py` 生成哈希绑定的只读 Cheat 输入，调用根 Cheat predict。
发布：用户确认公开后先真实调用根 Cheat publish，再运行总控发布桥写入 `publish-reference.json`。Cheat 公开路由与排除规则只见 `SKILL.md` 核心约束第 1 条。
