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

