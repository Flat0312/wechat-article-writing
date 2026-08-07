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

