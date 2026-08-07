## 视觉与 HTML（schema 1.0 历史长文 / news-card 路径）

> **仅 schema 1.0 长文与 news-card 适用。schema 1.1 中长文不再调用本节所述视觉与 HTML 流程——不调 `gzh-design`、不生成 `output/article.html`、不依赖 `ian-xiaohei-illustrations` / `baoyu-article-illustrator` 作为长文主流程。** 历史 schema 1.0 项目回放仍可走本节；新中长文走 `references/execution/pipeline.md` 的九阶段纯文字链路。

视觉规则只见 `references/quality-gates.md` 的视觉门禁。在
`visuals/visual-plan.md` 记录获批计划后，把封面 route 输出交给总控适配器：

```text
python <SKILL_ROOT>/scripts/visual_asset_adapter.py cover <PROJECT_ROOT> --route guizang --source <GUIZANG_OUTPUT>/wechat-21x9-cover.png --route-output-dir <GUIZANG_OUTPUT>
```

每个获批正文锚点都用总控适配器登记：

```text
python <SKILL_ROOT>/scripts/visual_asset_adapter.py body <PROJECT_ROOT> --route ian --source <IAN_OUTPUT>/anchor-emotion.png --anchor-id anchor-emotion --information-job "narrative tension" --provenance-ref <IAN_OUTPUT_REF>
python <SKILL_ROOT>/scripts/visual_asset_adapter.py body <PROJECT_ROOT> --route baoyu --source <BAOYU_OUTPUT>/anchor-flow.png --anchor-id anchor-flow --information-job "ordered steps" --provenance-ref <BAOYU_OUTPUT_REF>
```

完成全部选定资产后，用 `python <SKILL_ROOT>/scripts/article_state.py record <PROJECT_ROOT> --role visuals --path visuals/assets/manifest.json` 把 manifest 纳入文章状态。

选择 Baoyu 轨道时，运行 `python <SKILL_ROOT>/scripts/baoyu_adapter.py prepare <文章目录>`，把生成的 `visuals/assets/baoyu/source.md` 交给根 Skill；结束后运行 `python <SKILL_ROOT>/scripts/baoyu_adapter.py verify <文章目录>`。

封面或正文配图中出现的每个数字、日期、排名、比例、基准或图表值，都必须（MUST）使用以下证据路径之一：

- 外部事实值可追踪到 `research/sources.json` 的 `sources` 数组条目，且准确的视觉主张由 `supported_claim` 覆盖。
- 用户一手经历或自有记录中的值，可追踪到 `research/evidence.md` 中明确的 `user-material` 条目；该条目记录来源人、来源材料、材料日期和允许表达范围。

不得为用户材料编造 URL。不得把个人或自有记录中的值泛化成市场/群体/产品等普遍事实。图片提示词和生成工具不得编造、估算、装饰或静默修改数据。若两条证据路径都无法支持数值标签，删除该标签，或把正文视觉替换为非数据插图。

视觉与 HTML 完成需要以下五个文件均存在、非空：

1. `output/article.html`
2. `output/article-preview.html`
3. `output/article-copy.html`
4. `output/article-copy-preview.html`
5. `output/html-qc.md`

将 `output/article-copy.html` 视为人工粘贴产物，并登记到 `artifacts.html.path`。缺少任一文件都会阻塞 HTML 完成与 `html_ready`。仓库验证器还要求五个文件均含非空白 UTF-8 文本，`article.html` 含一对 `<section>...</section>`，`article-copy-preview.html` 含预期 HTML / 复制控件，`html-qc.md` 含 Markdown 标题、`output/article.html` 引用和验证记录。

在浏览器打开 `output/article-preview.html`，至少检查一个不宽于 390 CSS 像素的窄视口和一个不窄于 900 CSS 像素的常规视口。两个宽度都要验证：图片加载、文字与控件不重叠、内容不裁切、无横向溢出。

根 `gzh-design` 返回并验证 `<section>` 片段后，用 `scripts/wrap_preview.py` 创建两份项目预览，再运行：

```text
python <SKILL_ROOT>/scripts/upgrade_preview_copy.py <文章目录>
```

然后点击已加固预览的复制按钮，把目标正文粘贴到本地 `contenteditable` 区域或微信兼容的富文本沙箱。确认按钮报告 `clipboard-api`；若报告 `legacy-fallback`，记录降级，且不得假定块级层次仍然保留。检查粘贴后的剪贴板 HTML DOM：验证内容层级、必需行内样式、链接目标、图片节点及来源、内容顺序，并确认不存在预览专用控件或标签。若已有登录的微信编辑器可用，再额外验证粘贴；默认不得要求登录或凭据。完成前报告复制方法、检查宽度、粘贴目标，以及每项 DOM 和布局检查结果。

把两个检查宽度、图片加载结果、复制方法、粘贴目标、每项 DOM / 布局结果和全部九项微信长文排版契约结果写入 `output/html-qc.md`。只有五件套存在，且 `gzh-design`、确定性验证、两个浏览器预览检查和 pasted-DOM 检查全部通过后，才可标记 HTML 完成。缺失 `gzh-design` 会阻塞 HTML 完成；任何通用格式化器或手写 HTML 都不得替代此门禁。

`output/html-qc.md` 的结构按 [`assets/article-project-template/output/html-qc.template.md`](../../assets/article-project-template/output/html-qc.template.md)：五件套存在性、`gzh-design` 调用记录、9 项排版契约（3 文本级 + 5 视觉级 + `final.md` SHA256 绑定）、浏览器视口检查（≤390 / ≥900）、复制方法与粘贴目标、DOM / 布局检查。
