# 质量门禁

## 运行时依赖门禁

每个需要 Cheat 的阶段开始前，都要从已安装的 `SKILL_ROOT` 运行匹配的依赖检查。若退出码为 2 或报告 `ok: false`，立即停止，并按实际情况报告 `missing_required`、`script_runtime.missing_required` 或 `cli_runtime.missing_required`。根调用与禁止模拟的规则只由 `SKILL.md` 核心约束第 1 条定义。

信任任何可恢复项目检查点前，运行：

```text
python <SKILL_ROOT>/scripts/validate_project.py article <PROJECT_ROOT>
```

下游阶段可以依赖状态文件前，验证器必须重新计算每个已登记产物的哈希，并比较每项绑定产物的审批。

## 事实门禁

将主张分为用户提供的个人材料、稳定知识或时效性事实。保留用户材料，不得编造缺失细节。用户材料只能支持用户明确说过、观察过或经历过的内容；它不能作为 AI 模型、产品、公司、市场、政策、基准、价格、发布或其他变化主题之事实主张的外部证据。

每项时效性事实都要联网核验，并优先使用官方文档、原始公告、一手研究和权威数据库。对后果重大的争议主张进行交叉核验。证据包中未登记外部来源的时效性 AI 主张不得（MUST NOT）通过事实门禁：删除无依据断言、明确改写为作者观点，或仅描述为未经证实的报道。把主张标成“未经证实”不会让它变成证据；它不得支撑结论，也不得作为事实数字出现在正文或视觉中。只有措辞不再把无依据主张断言为事实后，事实门禁才可通过。不得把多篇二手文章的重复转述视为独立确认。

选题发现只能执行 [`references/topic-signal-registry.md`](topic-signal-registry.md)。其中信号不是最终证据。把已验证证据记录到 `research/evidence.md`，并把每个外部来源写入 `research/sources.json` 的 `sources` 数组，包含以下必需字段：

| 字段 | 必需内容 |
|---|---|
| `title` | 来源的准确标题 |
| `url` | 直接规范 URL |
| `source_type` | 如 `official_document`、`original_announcement`、`primary_research` 或 `authoritative_database` |
| `access_date` | `YYYY-MM-DD` 格式的访问日期 |
| `supported_claim` | 该来源支持的准确文章主张或主张标识符 |

任何需要核验的外部事实主张缺少可追踪的 `supported_claim` 条目时，不得通过门禁。一个来源只能支持为它登记的主张，不得外推到无关结论。

## 写作门禁

事实门禁通过后、起草前调用 `wechat-content-strategy`。必须具备一个主要增强策略、一个中心判断、职责互异的章节、已登记的证据锚点、文章级写作参数和 2–3 个编辑锚点。每个外部事实锚点必须能解析到 `research/sources.json`；每个个人材料锚点必须留在 `research/evidence.md` 允许的范围内。

中长文提纲开头必须（MUST）包含完整写前卡片，且八个字段缺一不可：真实摩擦、它揭示的机制、读者处境、一句核心判断、主要传播动作（点赞 / 转发 / 收藏，只选一项）、可转发立场、理性段落后的张力恢复点、标题承诺。任何字段缺失时，把缺口返回总控；不得批准提纲或开始起草。

起草前读取 `references/writing-style.md`。`wechat-article-writing` 拥有初稿，账号 `voice.md` 与已验证的 profile 规则定义作者声音。`outline.md` 必须包含完整文风卡：选择相关稳定规则、当篇文笔目标、可选临时实验、可选终稿观察候选、禁用习惯、保留的用户表达、开头动作与结尾回扣。文风卡缺失或泛化时不得起草。

外部写作 Skill 绝不是作者身份。文风卡锁定后，调用 `human-writing` 作为必需的正文主流程。公众号中长文须读取其论坛正文规则；真人、新闻、产品、行业、数据或用户经历须叠加现实题材规则；其改稿规则只能在初稿完成后读取。要求材料充分且可追踪、说话者位置具体、段落逐层推进、中文自然；对长稿运行 `human-writing/scripts/check_prose.py`，清除失败后才可批准。整篇必须由账号声音与 `human-writing` 共同写成并整合；不得调用外部作者文风 Skill。保留用户已确认的立场边界，不得为口语、碎句、反问或金句设置配额。

事实与结构稳定后，按 `references/writing-style.md` 完成 `human-writing` 修订、文笔、账号声音、AI 痕迹与声音回归检查。`humanizer-zh` 只能作为 [`references/external-contracts.md`](external-contracts.md#humanizer-diagnostic-contract) 约束下的可选诊断输入：用 `scripts/humanizer_diagnostic_adapter.py` 验证绑定当前哈希的局部问题清单，只应用最小兼容改动，并拒绝任何全文重写，或新增事实、数字、经历、立场及合成人格的建议。最终批准要求该引用中的七项文笔检查全部通过。

编辑锚点应留在初稿中，明确请求用户提供真实判断、经历或情绪。最终批准前必须解决或删除；绝不得用编造材料填充。

### 微信长文排版契约

排版契约的 8 条规则（3 文本级 + 5 视觉级）已抽到独立文档
[`references/wechat-layout-contract.md`](wechat-layout-contract.md)。在
`wechat-article-writing` 调用 `gzh-design` 时，将本节作为不可选的上位约束传入；
主题组件与契约冲突时省略该组件或改用更简洁的兼容组件。

`output/html-qc.md` 的“9 项排版检查”段按契约文档逐项记录复核结果；若只能通过
改动正文文字才能修复，按 `recovery-rules.md` 从 `final` 阶段失效并重新完成审批及
下游流程；不得在已批准正文或已锁定预测之后静默改字。

## 预测门禁

只有已批准终稿可以进入 Cheat 预测。`final` 审批必须（MUST）绑定当前终稿产物，且 `approvals.final.artifact_sha256` 必须（MUST）等于 `artifacts.final.sha256`；否则预测前重新取得用户确认。对 `content_form=long-essay`，先用 `scripts/cheat_form_adapter.py` 验证 `cheat-form-receipt.json`：`root_call_status=completed` 与 `rubric_status=compatible` 是两个分别必需的事实。默认观点视频 rubric 或 `rubric_form_mismatch=true` 会阻塞预测。调用根 `cheat-on-content` 执行预测；不得模拟或近似。不得向盲评分路线暴露实际表现、复盘、受众表现信号或其他禁用材料。绝不得覆盖不可变预测。

中长文路径通过 [`references/cheat-contracts.md`](cheat-contracts.md#long-essay-cheat-prediction-bridge) 创建 Cheat 兼容脚本。该适配器是把 `drafts/final.md` 复制到 Cheat `scripts/` 输入命名空间的唯一支持方式；审批哈希缺失或不匹配时，必须在写入任何快照前失败。`prediction-input-reference.json` 只是输入回执，绝不替代真实 `cheat-predict` 调用。

根 Cheat 路由返回 Channel B JSON 后，父路由计算 `composite` 或写入预测数据前先验证：

```text
python <SKILL_ROOT>/scripts/blind_score_adapter.py validate <BLIND_JSON> <RUBRIC_NOTES> --script <CHEAT_PROJECT>/scripts/<id>.md
```

验证器从当前 rubric 推导 `rubric_version` 和准确的 7/9 维集合，检查每个维度字段，并可重新计算 12 字符脚本哈希前缀。验证失败就是预测门禁失败；不得补填缺失维度、接受不同 rubric 版本，或根据未验证响应计算 composite。详见 [`references/cheat-contracts.md`](cheat-contracts.md#blind-score-contract)。

任何正式预测、影子预测或公开发布前，必须锁定且只能锁定一个 `primary_action`：`approval`、`forwarding`、`saving` 或 `discussion`。`prediction-reference.json` 回执必须（MUST）记录 `primary_action`、`locked_at` 与当前 `final_sha256`；其中 `final_sha256` 必须（MUST）匹配已批准终稿产物。字段缺失或不一致会阻塞预测与发布。

门禁口径：见数据后不改写。任何发布后数据变得可见后，绝不得回填或重写 `primary_action`。发布前更改它，需要重新检查提纲和终稿，再创建新的不可变预测版本，同时保留此前预测历史。

### v2 影子门禁

启用 v2 影子打分的项目在 v1 预测后、看到实绩前，可以对当前已批准终稿跑一次隔离的 Channel B 影子打分。该打分**只**为 bump 积累 v2 证据，不得替代、修改或触发现役 v1。

**调用入口**：根 `cheat-on-content` 的 `cheat-predict --blind-rescore` 模式。v1.4+ 起该模式支持 `--rubric <path>` 指定替代 rubric 文件。v2 影子必须传：

```text
cheat-predict --blind-rescore \
  --prediction-file <prediction_file> \
  --rubric reports/rubric-v2-candidate-rules.md
```

**Channel B 隔离协议**（与外部 `cheat-on-content/skills/cheat-score-blind/SKILL.md` 一致）：

- **允许读**：`scripts/<id>.md` + `reports/rubric-v2-candidate-rules.md`（v2 候选规则正文）
- **禁止读**：`reports/rubric-v2-candidate.md`（v2 候选证据档，含实绩）、历史 `predictions/*.md` 的复盘段、`rubric-memo.md`、`.cheat-state.json` 历史字段、`videos/*/report.md`、老预测、文章名、发布后评论

**落盘**：sidecar 写到 `.cheat-cache/blind-rescores/<id>.json`（v1.4+ 统一路径），`trigger: "blind_rescore"`，`rubric_version` 标注为 `v2-candidate`。该 sidecar **不**覆盖 v1 retro Phase 5.5 的 `retro_shadow` 触发；若 T+2 retro 尚未运行，新 sidecar 优先级最高。

**边界**：

- **不**替代 v1 预测；
- **不**改 `.cheat-state.json.rubric_version`（仍为 v1）；
- **不**单独触发 rubric bump（bump 须走完整 5 步协议）；
- 缺失 `cheat-on-content` 或 `reports/rubric-v2-candidate-rules.md` 时，阻塞影子步骤并报告缺失路线；**不**用 ad hoc model call 模拟。

**v2 候选证据积累**：`bump --propose` 落地前累计 ≥3 篇同向 v2 shadow 即可作为 bump 候选。v2 shadow 与 v1 retro shadow 的 sidecar 共用 `.cheat-cache/blind-rescores/`，用 `trigger` 字段区分。

## 视觉门禁

先运行 `cover` 依赖预检，再调用根 `guizang-social-card-skill`。使用完整或接近完整的文章标题与一个强视觉关系，只生成一张静态 `21:9` 微信主封面。账号视觉规则优先于自动建议。明确禁止 `.poster.square`、`1:1` 成对输出、成对预览、轮播、Live Photo 和视频。把标题、素材来源、布局意图、输出路径、尺寸与验证结果记录到 `visual-plan.md`。

缺少合适照片素材时，ImageGen 可以生成底图，仍由 Guizang 合成排版（素材兜底）。只有 Guizang 本身不可用时，ImageGen 才可端到端生成整张封面（路线兜底）。两种兜底都保持同一单资产契约，并且必须（MUST）在 `visual-plan.md` 和交付说明中标记。把完整路线输出传入 `scripts/visual_asset_adapter.py cover`；它要求恰好一张静态位图，拒绝所有禁用 companion，验证 `21:9`，并且只把 `visuals/assets/cover.<ext>` 复制进交付 manifest。适配器失败会使该路线不可用。没有可用封面路线会阻塞视觉完成；绝不得静默替换成正文或通用图片路线。

每个正文认知锚点都必须承担一个独立信息任务，并在 `visual-plan.md` 记录路线和理由。无需精确标签或数据时，情绪、观点、身份、叙事转折、张力或原创超现实隐喻选择 Ian；有序步骤、层级、对比、矩阵、架构、时间线、精确标签或有证据支持的数字选择 `baoyu-article-illustrator`。精确语义优先于氛围。独立任务拆成不同锚点；段落没有信息任务就不出图；除非用户明确要求 A/B，否则同一锚点绝不得双路线生成。Profile 视觉规则优先于自动推荐。

调用 Baoyu 前，完成其对图片类型、信息密度、风格、配色和语言的强制确认。快速模式不免除 visual plan 审批或任何视觉门禁。

运行 `visual` 依赖预检，再对每个选中锚点运行 `visual-ian` 或 `visual-structured`。`optional_missing: ["imagegen"]` 只是发现提示；所选路线必须解析到真实图片后端。路线缺失或后端未解析会阻塞该资产，替代方案不得更改其信息任务。每个结果都要经过 `scripts/visual_asset_adapter.py body`；只接受它复制到 `visuals/assets/ian/` 或 `visuals/assets/baoyu/` 下的文件，并要求 manifest 记录路线、锚点、信息任务、尺寸和 SHA256。验证宽高比、中文文字、可读性、一致性、插入位置、来源与文件存在性。

封面或正文配图中出现的每个数字、日期、排名、比例、基准或图表值，都必须（MUST）使用以下证据路径之一：

- 外部事实值可追踪到 `research/sources.json` 的 `sources` 数组条目，且准确的视觉主张由 `supported_claim` 覆盖。
- 用户一手经历或自有记录中的值，可追踪到 `research/evidence.md` 中明确的 `user-material` 条目；该条目记录来源人、来源材料、材料日期和允许表达范围。

不得为用户材料编造 URL。不得把个人或自有记录中的值泛化成市场、群体、产品或其他普遍事实。图片提示词和生成工具不得编造、估算、装饰或静默修改数据。若两条证据路径都无法在允许范围内支持数值标签，删除该标签，或把正文视觉替换为非数据插图。

选择 Baoyu 路线前，终稿必须（MUST）按当前 SHA256 登记并批准。运行 `scripts/baoyu_adapter.py prepare`，只把 `visuals/assets/baoyu/source.md` 传给根 Skill，再运行 `scripts/baoyu_adapter.py verify`。任何终稿哈希不匹配都会阻塞视觉完成。

## HTML 门禁

调用根 `gzh-design` 时，把上述微信长文排版契约作为明确的硬约束，并应用 [`references/external-contracts.md`](external-contracts.md#gzh-design-author-cta-override) 的 CTA 策略。使用微信兼容的行内样式。验证每项图片引用、图片尺寸和必需资产。运行仓库文章验证器并清除每个强制错误，同时清除 `gzh-design` 的每个强制错误。用户未提供作者块或 CTA 偏好时，记录 `author_cta: disabled` 并删除默认署名/CTA；否则记录 `author_cta: explicit`，且只保留用户提供的文字。

HTML 完成要求以下五个文件均存在、非空：

1. `output/article.html`
2. `output/article-preview.html`
3. `output/article-copy.html`
4. `output/article-copy-preview.html`
5. `output/html-qc.md`

将 `output/article-copy.html` 视为人工粘贴产物，并登记到 `artifacts.html.path`。缺少任一文件都会阻塞 HTML 完成与 `html_ready`。仓库验证器还要求五个文件均含非空白 UTF-8 文本，`article.html` 含一对 `<section>...</section>`，`article-copy-preview.html` 含预期 HTML / 复制控件，`html-qc.md` 含 Markdown 标题、`output/article.html` 引用和验证记录。

在浏览器打开 `output/article-preview.html`，至少检查一个不宽于 390 CSS 像素的窄视口和一个不窄于 900 CSS 像素的常规视口。两个宽度都要验证：所有图片加载，文字和控件不重叠，内容不裁切，并且没有意外的横向溢出。

根 `gzh-design` 返回并验证 `<section>` 片段后，用 `scripts/wrap_preview.py` 创建两份项目预览，再运行：

```text
scripts/upgrade_preview_copy.py output/article-copy-preview.html
```

该加固保留原始复制兜底；浏览器支持 Clipboard API 时，把目标片段明确写成 `text/html`，避免 Chromium 在基于选区复制时压平块级层次。加固还必须让本地图片在剪贴板载荷中可移植：复制门禁前，验证 copy preview 中每个本地 `<img>` 来源均已嵌入为 `data:image/...`，或使用另一种已证明能在目标粘贴中存活的资源形式；剪贴板 HTML 中不得残留 `../visuals/...` 路径。缺少或无法识别 `gzhCopy` 函数会阻塞门禁；不得静默声称预览已加固。

然后点击已加固预览的复制按钮，把目标正文粘贴到干净的本地 `contenteditable` 区域或微信兼容的富文本沙箱。确认按钮报告 `clipboard-api`；若报告 `legacy-fallback`，记录降级，且不得假定块级层次仍然保留。检查粘贴后的剪贴板 HTML DOM，而不只看预览：验证内容层级、必需行内样式、链接目标、图片节点及来源、内容顺序，并确认不存在预览专用控件或标签。若已有登录的微信编辑器可用，再额外在那里验证粘贴；默认前置条件不得要求微信登录或凭据。标记阶段完成前，报告复制方法、两个检查宽度、粘贴目标，以及每项 DOM 和布局检查结果。

把两个检查宽度、图片加载结果、复制方法、粘贴目标、每项 DOM / 布局结果和全部九项微信长文排版契约结果写入 `output/html-qc.md`。只有五件套存在，且 `gzh-design`、确定性验证、两个浏览器预览检查和 pasted-DOM 检查全部通过后，才可标记 HTML 完成。缺失 `gzh-design` 会阻塞 HTML 完成；任何通用格式化器或手写 HTML 都不得替代此门禁。

`output/html-qc.md` 的结构按 [`assets/article-project-template/output/html-qc.template.md`](../assets/article-project-template/output/html-qc.template.md)：

- 五件套存在性
- `gzh-design` 调用记录
- 9 项排版契约（3 文本级 + 5 视觉级 + `final.md` SHA256 绑定）
- 浏览器视口检查（≤390 / ≥900）
- 复制与粘贴（`clipboard-api` / `legacy-fallback` + pasted DOM）
- `validate_project` 与确定性校验
- `final.md` SHA256 一致性
- 阻塞原因（如有）

每项标 ✅ / ❌；❌ 项必须给出具体复现路径。
