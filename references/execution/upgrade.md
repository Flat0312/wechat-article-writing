### 升级已安装的 Skill

用户说「更新所有 skill」「更新依赖」「检查 skill 更新」时：

1. 运行 `python <SKILL_ROOT>/scripts/dependency_check.py --stage account` 拿到已安装 skill 的路径列表（`available` 数组）。
2. `dependency_check.py` 本身不输出路径。改用 `python <SKILL_ROOT>/scripts/dependency_check.py --stage html`，从 `available` 取到 skill 名，再按 Git 搜索逻辑找到每个 skill 的实际目录。更直接的方式：直接搜索各 runtime skills 目录下的 git 仓库。
3. 对每个 skill 目录执行：`git -C <目录> pull --ff-only 2>&1`。用 `--ff-only` 避免合并冲突意外改写本地文件。
4. 汇总报告：

| Skill | 状态 |
|---|---|
| `human-writing` | 已更新 (旧哈希 -> 新哈希) |
| `humanizer-zh` | 已是最新 |
| `gzh-design` | 更新失败：本地有未提交的修改 |

5. 更新完后跑一次全阶段依赖检查，确认没有因更新导致的 schema 不兼容或路由断裂。
6. 若当前 workspace 启用上述项目工具契约，先完成兼容性测试，再运行
   `skill-lock --write` 刷新 Skill 锁，最后运行 `audit`。

搜索目录：`~/.codex/skills/`、`~/.claude/skills/`、`~/.agents/skills/`，以及 `WECHAT_ARTICLE_SKILL_ROOTS` 环境变量中的路径。只更新是 git 仓库的目录（有 `.git`），跳过手动复制的 skill。

