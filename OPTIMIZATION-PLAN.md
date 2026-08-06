# wechat-article-writing 瘦身计划（执行文档）

> 交给 Codex 执行。本文件自包含：所有事实均已实测，行号对应执行本计划时的仓库状态。
> 执行完成后本文件可删除。

## 0. 目标与非目标

**目标**：消除同一条规则在多个文件中的重复复述，修复已断裂的引用，让「按需加载 references」重新生效。

**非目标（严禁触碰）**：
- ❌ 不得削弱、放宽或删除任何门禁规则。这是**去重重构**，不是策略变更。规则总量可以减少，规则**约束力**必须一字不减。
- ❌ 不得修改 `scripts/*.py` 的 CLI 签名。特别是 `validate_project.py profile <账号目录>` —— 它是对伴生 Skill 承诺的稳定接口（见 `references/execution.md:87-100`），JSON 形状 `{"ok": bool, "errors": [...]}` 与退出码 0/1 必须保持。
- ❌ 不得 vendoring 或复制第三方 Skill 进本仓库。
- ❌ 不得改变 `article-state.json` / `account.json` 的 schema。

---

## 1. 仓库现状（已实测）

路径：`~/.codex/skills/wechat-article-writing`

| 目录 | 数量 | 体量 |
|---|---|---|
| `SKILL.md` | 1 | 4.6 KB |
| `references/` | 22 个 md | 141 KB |
| `scripts/` | 18 个 py | — |
| `tests/` | 22 个 py | — |
| `companion-skills/` | 2 个子 Skill | 各约 7.5 KB |

references 体量分布高度不均：

- 三个大文件占 45%：`execution.md` 30.2KB、`quality-gates.md` 18.6KB、`skill-routing.md` 14.2KB
- 10 个文件 < 2.1KB：`external-contract-fixtures`(0.9)、`gzh-design-author-cta`(1.1)、`humanizer-diagnostic-contract`(1.2)、`cheat-seed-compatibility`(1.3)、`creator-buddy-wechat-override`(1.4)、`blind-score-contract`(1.6)、`visual-asset-manifest`(1.7)、`cheat-form-contract`(1.8)、`cheat-prediction-bridge`(2.0)、`cheat-status-receipt`(2.0)

---

## 2. 已确认缺陷（必须修复）

### D1 — SKILL.md 有 7 条引用指向不存在的文件

`SKILL.md:43-52` 的「细则索引」共 8 条，其中**只有第 52 行的 `creator-buddy-wechat-override.md` 真实存在**。以下 7 条（第 45-51 行）在 `references/` 中不存在：

| 行号 | 幽灵引用 | 内容实际所在 |
|---|---|---|
| 45 | `references/cheat-routing.md` | `skill-routing.md:30-32,52-78` |
| 46 | `references/signal-orchestration.md` | `skill-routing.md:38-50` + `topic-signal-registry.md` |
| 47 | `references/news-card-flow.md` | `execution.md:158-188` |
| 48 | `references/style-learning.md` | `execution.md:255-260` + `writing-style.md:92-99` |
| 49 | `references/platform-distribution.md` | `skill-routing.md:87-96` |
| 50 | `references/account-directories.md` | `account-profile-schema.md` |
| 51 | `references/visual-routing.md` | `skill-routing.md:98-134` |

### D2 — `scripts/wrap_preview.py` 不存在，但流程强制调用它

`references/execution.md:324-325` 要求执行：

```
python <SKILL_ROOT>/scripts/wrap_preview.py <PROJECT_ROOT>/output/article.html      <PROJECT_ROOT>/output/article-preview.html
python <SKILL_ROOT>/scripts/wrap_preview.py <PROJECT_ROOT>/output/article-copy.html <PROJECT_ROOT>/output/article-copy-preview.html
```

`scripts/` 下没有该文件。这直接阻断 HTML 五件套中的 `article-preview.html` 与 `article-copy-preview.html`，而后者又是 `upgrade_preview_copy.py` 的输入 —— 即 HTML 门禁当前**不可能通过**。

---

## 3. 重复规则地图（Phase 1 的作业清单）

同一条规则在 3–4 个文件中各写一遍。这是臃肿的真实来源：agent 执行任一阶段都得同时读 `execution.md` + `quality-gates.md` + `skill-routing.md`，因为无法判断谁是权威。

| # | 规则 | 出现位置 |
|---|---|---|
| R1 | 21:9 单封面契约 + guizang override + ImageGen 素材/路由双兜底 | `SKILL.md:12`、`execution.md:275-281`、`quality-gates.md:134`、`skill-routing.md:25` **和** `skill-routing.md:98-116` |
| R2 | HTML 五件套 + gzh-design 必经 + 剪贴板门禁 | `execution.md:305-343`、`execution.md:353-358`、`quality-gates.md:147-196`、`publishing.md:5-7`、`skill-routing.md:136-138` |
| R3 | 八路选题信号 lane + `missing`/`not_applicable` 处理 | `execution.md:231-239`、`skill-routing.md:38-50`、`quality-gates.md:18`、`topic-signal-registry.md`（自称 single source） |
| R4 | Ian / Baoyu 认知锚点分轨 + adapter 收回 | `execution.md:283-292`、`quality-gates.md:136`、`skill-routing.md:118-134` |
| R5 | 「cheat 必须真调、不得模拟/复制公式」 | `SKILL.md:8`、`execution.md:227`、`skill-routing.md:78`、`quality-gates.md:5` |
| R6 | 依赖检查 stage 清单（16 行穷举） | `execution.md:41-58` —— 属于脚本自身 CLI，不应占用 prompt |

**语言不一致**：`SKILL.md` / `execution.md` / `writing-style.md` 为中文；`quality-gates.md` / `skill-routing.md` / `onboarding.md` / `publishing.md` 为英文。同一规则两种语言各写一遍，已经产生措辞漂移。

---

## 4. 执行前必做：建立基线

```
# 1. 确认测试入口后运行全量测试，保存输出
python -m pytest tests/ -q > /tmp/baseline-tests.txt 2>&1

# 2. 确认工作区干净
git -C . status --short
git -C . rev-parse HEAD
```

**若基线测试本身有失败项，先记录清单，不要在本次重构中顺手修**。基线的用途是证明重构零行为变化。

---

## 5. Phase 0 — 止血（低风险，可独立交付）

### T0.1 修复 D1

删除 `SKILL.md:45-51` 这 7 行。保留第 52 行（`creator-buddy-wechat-override.md` 真实存在）。

若判断这些主题确实需要在索引中可见，**不要新建空文件**——改为指向真实 owner，例如：
```
- `references/skill-routing.md` — Cheat 子路由裁剪、八路信号编排、视觉路线选择、平台分发
```

### T0.2 修复 D2

先读以下文件推导 preview 外壳的确切契约，再实现：

- `scripts/upgrade_preview_copy.py` —— 它对 `article-copy-preview.html` 做加固，会查找 `gzhCopy` 函数；外壳必须满足它的假设
- `scripts/validate_html_delivery.py` —— 五件套的确定性校验规则
- `tests/test_preview_copy_upgrade.py`、`tests/test_html_five_file_contract.py`
- `assets/article-project-template/output/html-qc.template.md`

实现 `scripts/wrap_preview.py`，接口按 `execution.md:324-325` 已声明的形式：

```
python scripts/wrap_preview.py <输入 html> <输出 preview html>
```

要求：把 `gzh-design` 返回的纯 `<section>...</section>` 正文包进可在浏览器打开的预览外壳，产出物需能通过 `validate_html_delivery.py`，且 `article-copy-preview.html` 经 `upgrade_preview_copy.py` 加固后 `gzhCopy` 可用。

⚠️ 备选方案（若实现成本过高）：改写 `execution.md`，改用 `gzh-design` 自身的 `{原文件名}_预览.html` 产物（见 `execution.md:313-315`）。**但注意流程需要两份预览而 gzh-design 只产出一份**，因此优先实现脚本。

配套新增 `tests/test_wrap_preview.py`。

### T0.3 加防再发测试

新增 `tests/test_reference_integrity.py`：

扫描 `SKILL.md`、`references/**/*.md`、`companion-skills/**/SKILL.md` 中出现的所有 `references/*.md`、`scripts/*.py`、`assets/**` 路径引用（含 Markdown 链接语法与行内 code），断言每个被引用的文件真实存在。

这条测试是本次重构最重要的长期资产 —— D1 和 D2 都是它能拦住的。

**Phase 0 验收**：全量测试通过且与基线一致（除新增测试外）；`test_reference_integrity.py` 绿。

---

## 6. Phase 1 — 消重（主要收益，主要风险）

**核心原则：每条规则只有一个 owner 文件。其他文件只能链接，不能复述。**

### 强制工作方法

对第 3 节的 R1–R5，逐条执行：

1. **先取证**：把该规则的 N 份副本并排提取，逐句 diff
2. **记录差异**：副本之间**几乎一定存在措辞差异**（触发条件、兜底顺序、必填字段范围）。每处差异必须在 `MERGE-LOG.md` 中记录，并明确裁决：哪份为准、为什么
3. **保守合并**：差异无法判断时，**合并为更严格的那一版**，并在 MERGE-LOG 中标记 `NEEDS-REVIEW` 提请人工确认
4. **再删除**：确认 owner 版本完整覆盖全部语义后，才把其余 N-1 处改为单行链接

> 🚫 严禁「看起来一样就删」。这是本 Phase 唯一的失败模式。

### owner 归属方案

| 规则 | owner | 其余位置改为 |
|---|---|---|
| R1 封面 | 视觉门禁文件 | 一行链接 |
| R2 HTML | HTML 门禁文件 | 一行链接 |
| R3 八路信号 | `topic-signal-registry.md`（它已自称 single source，让它名副其实） | 一行链接 |
| R4 Ian/Baoyu | 视觉门禁文件（与 R1 同一份） | 一行链接 |
| R5 cheat 真调 | `SKILL.md` 核心约束第 1 条（这是全局铁律，适合留在常驻入口） | 一行链接 |

`execution.md` 瘦身为**纯流程骨架**：每个阶段只写「做什么 / 产物落在哪 / 下一步是谁 / 规则见哪个文件」，所有规则正文外链。

删除 `execution.md:41-58` 的 16 行 stage 穷举，替换为一行说明 + 指向 `dependency_check.py --help`。

**Phase 1 验收**：
- 全量测试对齐基线
- `MERGE-LOG.md` 中每条合并都有 diff 证据与裁决记录
- 对 R1–R5 各做一次反向抽查：从 owner 文件出发，能否复原原先 3–4 处的全部约束语义

---

## 7. Phase 2 — 合并碎契约 + 统一语言

### T2.1 合并小文件

10 个 <2.1KB 的契约文件合并为 2 份（各契约作为二级标题小节，内容不改写）：

- `references/cheat-contracts.md` ← `cheat-form-contract` + `cheat-prediction-bridge` + `cheat-status-receipt` + `cheat-seed-compatibility` + `blind-score-contract`
- `references/external-contracts.md` ← `humanizer-diagnostic-contract` + `gzh-design-author-cta` + `creator-buddy-wechat-override` + `external-contract-fixtures` + `visual-asset-manifest`

同步更新所有指向旧路径的引用（`SKILL.md`、其余 references、`scripts/`、`tests/`）。`test_reference_integrity.py` 会兜底捕获遗漏。

### T2.2 统一语言为中文

`quality-gates.md`、`skill-routing.md`、`onboarding.md`、`publishing.md` 目前为英文。翻译时**逐条保持约束语义**，MUST / MUST NOT 等强制语气必须以同等强度的中文表达（「必须」「不得」），不得软化为「建议」「尽量」。

### 目标结构

`references/` 从 22 个收敛到约 12 个。

---

## 8. Phase 3 — 收尾校验

1. 全量测试对齐基线
2. `SKILL.md` 复核：核心约束 8 条中，凡是可从下游 owner 文件推导的，压缩为指针；保留真正的全局铁律
3. 端到端抽查：模拟一次 long-essay 流程，确认从 `SKILL.md` 出发，每个阶段只需加载 1–2 个 references 即可执行
4. 复核 `companion-skills/` 两个子 Skill 是否引用了被移动的路径

---

## 9. 交付物

| 文件 | 内容 |
|---|---|
| `MERGE-LOG.md` | Phase 1 每条规则的 diff 证据、裁决理由、`NEEDS-REVIEW` 清单 |
| `scripts/wrap_preview.py` | 新增 |
| `tests/test_reference_integrity.py` | 新增 |
| `tests/test_wrap_preview.py` | 新增 |
| git 提交 | 按 Phase 分开提交，便于单独回滚 |

---

## 10. 需人工决策（遇到时停下来问，不要自行决定）

- **DQ1**：Phase 1 中若发现某条规则的多份副本存在**实质冲突**（不是措辞差异，而是行为不同），停止合并，列出冲突并等待裁决。
- **DQ2**：若 `wrap_preview.py` 的契约无法从现有脚本与测试中确定推导，停止实现，报告缺口。
- **DQ3**：Phase 0 基线测试若存在既有失败项，报告清单后等待指示，不要顺手修。

---

## 11. 建议执行顺序

Phase 0 风险极低且独立可交付，先做完并提交。Phase 1 是真重构，建议单独开一轮，带着 Phase 0 的 `test_reference_integrity.py` 做安全网。
