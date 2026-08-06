---
name: wechat-style-learning
description: Learn compact, reusable WeChat writing rules from confirmed human-edited draft/final pairs and continuously observe approved final drafts in a standard long-term account profile. Use when the user asks to learn, persist, or continuously evolve writing style; keep final-only observations provisional and preview promotion candidates before changing hard voice rules.
---

# WeChat Style Learning

从人工改稿差异和每篇已批准终稿中提炼可复用规则，写入长期账号的便携式学习账本。
终稿观察可以自动累积，但只能先进入观察层；只有用户确认或满足独立的晋级门槛后，
才进入正式文风规则。

## 强制边界

1. 用户明确要求学习或持续进化后，才启用本 Skill；在该授权持续有效期间，已批准的
   每篇终稿可以自动进入“终稿观察”流程。
2. 正式改稿学习仅接受标准长期账号画像、原始初稿和人工定稿。终稿观察只接受完整、
   已批准的 `final.md`；临时文章和资讯贴图不得创建 long-essay 学习状态。
3. 终稿观察可以自动记录候选，但不得自动写入 `voice.md` 或把观察直接标记为
   `validated`。正式规则晋级前仍需展示候选并取得确认，或满足下文规定的独立样本门槛。
4. 只记录文章 ID、相关 SHA256、观察/确认时间和简短通用规则。不得保存正文、摘录、
   机器绝对路径、凭据或 Cheat 状态。
5. 正式改稿学习只更新 `history/edits/` 和 `content-patterns.md` 的生成区块；终稿观察
   只更新 `history/voice-observations/`。不得修改文章产物、Cheat 状态、当前审批或
   当前文章状态。`voice.md` 只能由总控在用户明确确认后更新。
6. 新规则只影响后续文章。若用户要求应用到当前文章，交还总控并按最早变化阶段
   执行失效传播。
7. 2026-08-01 至 2026-08-31 的资讯贴图试运行样本不得进入 long-essay
   学习账本；以后如需学习，必须使用单独的贴图账本，不得混入现有规则。
8. 学习结果只能描述本账号可复用的声音或技法，不得把对标账号或任何外部
   Skill 的身份、口癖、粗口、固定标点、固定字数、固定结构或固定结尾写入账号规则。
   技法默认按文章选择，不设置每篇强制配额。

## 输入来源与所有权

- 项目的 `reports/writing-learning-candidates.md` 候选报告只用于筛选值得人工比较的
  文件对，不是规则、不构成写入授权，也不能替代本 Skill 的逐篇比较与用户确认。
- 本 Skill 负责两条证据路线：单篇真实初稿与人工定稿的 diff，以及已批准终稿的跨篇观察。
  前者写 `history/edits/` 与 `content-patterns.md` 的 `style-learning:validated`、
  `style-learning:provisional` marker 区块；后者只写 `history/voice-observations/`。
- P1–P6、G1–G6 等跨篇发布后 pattern 归 `cheat-retro` 路径负责，不得伪造为
  draft/final occurrence，不得由 `edit_learning.py` 改写。两路证据重合时只做
  交叉引用，不双写、不重复计数。

## 工作流

### 1. 核查前置条件

确认：

- 账号目录包含有效的 `account.json` 和 `content-patterns.md`。
- 初稿与人工定稿均存在，且不是同一内容。
- 用户明确说明定稿包含其人工判断，而非另一份未经确认的模型输出。
- 完成人工定稿完整性二次检查：实际读取定稿，确认它是完整、可发布的实质正文，
  不是空白、近空、占位提示或截断文件；不得只相信候选报告的 `review` 标签。
- 本动作不针对临时文章或导入预览。

### 2. 提炼候选规则

比较初稿与定稿，但不要把正文写入账本。候选规则必须：

- 可以用于多篇未来文章，而非复述本篇主题。
- 使用稳定的英文 `key`，格式为小写字母、数字、下划线或连字符。
- `type` 只能是 `structure`、`opening`、`closing`、`rhythm`、`tone`、
  `expression` 或 `evidence`。
- `instruction` 是简短、可执行的中文规则，不含原文摘录、事实结论或本机路径。

排除事实纠错、一次性内容增删、平台合规修正和无法从差异中稳定推断的偏好。
如果只从终稿观察到某种结构或幽默，不得把它写成固定人格、固定口癖或机械数量要求。

### 3. 预览并等待确认

逐条展示：

- 规则 key 和类型
- 可执行说明
- 支撑它的“差异类型”概述，不展示或持久化长段正文
- 适用范围和可能误判点

用户可以确认、删除或改写候选规则。未确认时不得执行记录脚本。

### 3.5 每篇终稿自动观察

用户启用持续学习后，在最终稿审批通过、且 `final.md` SHA256 已锁定时：

1. 实际读取完整终稿，提炼 0–5 条跨文章可复用的候选规则；不保存正文片段。
2. 用 `observe-final` 记录 `article_id`、终稿 SHA256、时间和候选规则。该动作幂等，
   不改变文章状态、审批、预测或发布记录。
3. 用 `aggregate-observations` 汇总跨篇出现次数。候选在至少 3 篇不同文章中出现，且
   没有与 `voice.md` 冲突时，标记为 `candidate`；否则保持 `observed`。
4. 下一篇文章的文风执行卡可以把 `candidate` 当作软参考，但不得自动升级为硬约束。
   总控在周期复盘或用户要求时展示晋级候选，用户确认后才写入 `voice.md` 或正式
   `content-patterns.md`。

调用：

```text
python <SKILL_ROOT>/scripts/edit_learning.py observe-final \
  --profile <账号目录> \
  --final <终稿路径> \
  --article-id <文章ID> \
  --rules <终稿观察规则JSON文件>
```

只读查看观察结果：

```text
python <SKILL_ROOT>/scripts/edit_learning.py aggregate-observations \
  --profile <账号目录> \
  [--as-of YYYY-MM-DD]
```

### 4. 记录已确认规则

运行 `record` 前再次确认人工定稿完整性检查已经通过；失败时停止，不执行脚本。

调用：

```text
python <SKILL_ROOT>/scripts/edit_learning.py record \
  --profile <账号目录> \
  --draft <初稿路径> \
  --final <人工定稿路径> \
  --article-id <文章ID> \
  --rules <已确认规则JSON文件> \
  --approved
```

`rules` 文件是 JSON 数组，每项只包含 `key`、`type`、`instruction`。
程序会：

- 对初稿/定稿计算 SHA256，并对同一文件对保持幂等。
- 创建或更新 `history/edits/index.json` 和独立 lesson JSON。
- 聚合同 key 的确认次数。
- 每次确认增加 2 点置信度；距最后一次确认每满 90 天衰减 1 点。
- 置信度达到 6 时进入 `validated`，否则保持 `provisional`。
- 更新 `content-patterns.md` 的已验证与待验证生成区块。

### 5. 验证并报告

运行总控的画像验证器：

```text
python <WECHAT_ARTICLE_ROOT>/scripts/validate_project.py profile <账号目录>
```

报告新增或重复记录、当前出现次数、置信度和状态。不要声称当前文章已经应用这些规则。
终稿观察报告还要报告 `observed` / `candidate` 状态，并明确它们仍是软参考。

## 聚合查看

只读查看当前规则：

```text
python <SKILL_ROOT>/scripts/edit_learning.py aggregate \
  --profile <账号目录> \
  [--as-of YYYY-MM-DD]
```
