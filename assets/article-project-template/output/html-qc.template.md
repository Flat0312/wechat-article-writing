# HTML 验收报告（`output/html-qc.md`）

> **本模板由 `gzh-design` 完成后、`html_ready` 标记前自动生成**。每项必填，结果记录到本文件
> 后才能标记 HTML 完成。所有项目通过才能进入发布阶段；任一失败须回到对应阶段修复。

---

## 一、五件套存在性

| 文件 | 必填 | 实际路径 | 存在 | 大小 / 字节 |
|---|:---:|---|:---:|---:|
| `output/article.html` | ✅ | | ☐ | |
| `output/article-preview.html` | ✅ | | ☐ | |
| `output/article-copy.html` | ✅ | | ☐ | |
| `output/article-copy-preview.html` | ✅ | | ☐ | |
| `output/html-qc.md` | ✅ | （本文件） | ✅ | |

任一缺失 → 阻塞 HTML 完成；不替代剪贴板门禁。

## 二、gzh-design 调用记录

- 调用时间：`<YYYY-MM-DD HH:MM>`
- 入口 Skill：`gzh-design`（不接受其他 HTML 路由）
- 上位约束传入：✅ `references/wechat-layout-contract.md` 8 条规则
- 默认智能处理覆盖：✅ 主题组件与契约冲突时省略该组件

## 三、9 项排版契约复核（`wechat-layout-contract.md`）

### 文本级（3 项）

| # | 规则 | 检查项 | 结果 | 备注 |
|---:|---|---|:---:|---|
| T1 | 段长与拆段 | 窄屏（≤390 CSS px）下无单段超 5-6 行 | ☐ | |
| T2 | 孤立短行 | 无分行后仅剩 2-3 字的孤立短行 | ☐ | |
| T3 | 整句高亮 | 重点内容高亮覆盖整句 + 句末标点，无半句高亮 | ☐ | |

### 视觉级（5 项）

| # | 规则 | 检查项 | 结果 | 备注 |
|---:|---|---|:---:|---|
| V1 | 窄屏首屏 | 窄屏首屏呈现一个完整阅读单元（无装饰切割） | ☐ | |
| V2 | 标题层级 | 大标题/小标题使用明显不同字体颜色；大标题全篇统一格式 | ☐ | |
| V3 | 字色字号 | 浅色主题 14/15 px + `#595757`；深色主题走组件库"正文色"且对比度 ≥ 4.5:1 | ☐ | |
| V4 | 行距段距 | 舒适、疏密适度，无拥挤或过量留白 | ☐ | |
| V5 | 装饰横线 | 默认无装饰横线 / 多余边框；小标题短竖线仅保留必要一种 | ☐ | |

逐项标 ✅ / ❌；❌ 项必须给具体复现路径（行号 / 截图 / 描述）。

## 四、浏览器视口检查

### 窄屏（≤390 CSS px）

- 视口宽度：`<N>` px
- 图片加载：☐ 全部加载 / ☐ 失败 N 张（列路径）
- 文本与控件重叠：☐ 无 / ☐ 有（描述）
- 内容被裁切：☐ 无 / ☐ 有（位置）
- 横向溢出：☐ 无 / ☐ 有（描述）

### 常规宽度（≥900 CSS px）

- 视口宽度：`<N>` px
- 图片加载：☐ 全部加载 / ☐ 失败 N 张
- 文本与控件重叠：☐ 无 / ☐ 有
- 内容被裁切：☐ 无 / ☐ 有
- 横向溢出：☐ 无 / ☐ 有

## 五、复制与粘贴

### 复制加固

- 入口脚本：`python <SKILL_ROOT>/scripts/upgrade_preview_copy.py output/article-copy-preview.html`
- 加固结果：☐ 已注入 `window.gzhCopy` / ☐ 已存在（幂等跳过）
- 本地图片内嵌：☐ 全部 `data:image/...` / ☐ 仍有 `../visuals/...` 路径
- 复制按钮可见：☐ 是 / ☐ 否

### 复制方法

- 实际方法：☐ `clipboard-api`（`navigator.clipboard.write` 成功）/ ☐ `legacy-fallback`（降级）
- 报告字段：`<copy_method>`（来自 `gzhCopy` 函数返回值）

### 粘贴目标

- 目标 A（必做）：本地 `contenteditable` 表面
- 目标 B（可选，已登录时）：微信编辑器实际粘贴
- 是否实际粘贴并检查：☐ 是 / ☐ 否

### pasted DOM 检查

| 检查项 | 目标 A 结果 | 目标 B 结果（如有） |
|---|:---:|:---:|
| 内容层级保留 | ☐ | ☐ |
| 必填内联样式 | ☐ | ☐ |
| 链接 target / href | ☐ | ☐ |
| 图片节点 + src | ☐ | ☐ |
| 内容顺序 | ☐ | ☐ |
| 无 preview-only 控件 | ☐ | ☐ |
| 无 preview-only 标签 | ☐ | ☐ |

任一 ❌ → 阻塞 `html_ready`；如需改 final.md，按 `references/recovery-rules.md` 从 `final` 阶段失效并重走审批 + 预测。

## 六、validate_project 与确定性校验

- `python <SKILL_ROOT>/scripts/validate_project.py article <文章目录>`：☐ 通过 / ☐ 失败（错误列表）
- `gzh-design` mandatory errors：☐ 清空 / ☐ 残留
- 路径安全（无 Windows 绝对路径、无 `..`）：☐ 通过
- 凭据字段扫描：☐ 无 secret-like 字段

## 七、final.md SHA256 绑定

- 当前 `drafts/final.md` SHA256：`<sha256:64>`
- `approvals.final.artifact_sha256`：`<sha256:64>`
- 一致性：☐ 是 / ☐ 否（不一致阻塞 `html_ready`）

## 八、记录

- 检查完成时间：`<YYYY-MM-DD HH:MM>`
- 执行人：`<Claude / 用户>`
- 进入 `html_ready` 决定：☐ 通过 / ☐ 阻塞
- 阻塞原因（如有）：`<具体描述>`
