## 视觉门禁（schema 1.0 历史长文 / news-card 路径）

> **schema 1.1 中长文不读本节、不执行本节门禁**——1.1 不生成封面、不生成正文配图。news-card 仍按本节执行其 21:9 单图契约，schema 1.0 历史长文回放亦可读本节。

## 视觉门禁

缺少合适照片素材时，ImageGen 可以生成底图，仍由 Guizang 合成排版（素材兜底）。只有 Guizang 本身不可用时，ImageGen 才可端到端生成整张封面（路线兜底）。两种兜底都保持同一单资产契约，并且必须（MUST）在 `visual-plan.md` 和交付说明中标记。把完整路线输出传入 `scripts/visual_asset_adapter.py cover`；它要求恰好一张静态位图，拒绝所有禁用 companion，验证 `21:9`，并且只把 `visuals/assets/cover.<ext>` 复制进交付 manifest。适配器失败会使该路线不可用。没有可用封面路线会阻塞视觉完成；绝不得静默替换成正文或通用图片路线。

调用 Baoyu 前，完成其对图片类型、信息密度、风格、配色和语言的强制确认。快速模式不免除 visual plan 审批或任何视觉门禁。

运行 `visual` 依赖预检，再对每个选中锚点运行 `visual-ian` 或 `visual-structured`。`optional_missing: ["imagegen"]` 只是发现提示；所选路线必须解析到真实图片后端。路线缺失或后端未解析会阻塞该资产，替代方案不得更改其信息任务。每个结果都要经过 `scripts/visual_asset_adapter.py body`；只接受它复制到 `visuals/assets/ian/` 或 `visuals/assets/baoyu/` 下的文件，并要求 manifest 记录路线、锚点、信息任务、尺寸和 SHA256。验证宽高比、中文文字、可读性、一致性、插入位置、来源与文件存在性。

封面或正文配图中出现的每个数字、日期、排名、比例、基准或图表值，都必须（MUST）使用以下证据路径之一：

- 外部事实值可追踪到 `research/sources.json` 的 `sources` 数组条目，且准确的视觉主张由 `supported_claim` 覆盖。
- 用户一手经历或自有记录中的值，可追踪到 `research/evidence.md` 中明确的 `user-material` 条目；该条目记录来源人、来源材料、材料日期和允许表达范围。

不得为用户材料编造 URL。不得把个人或自有记录中的值泛化成市场、群体、产品或其他普遍事实。图片提示词和生成工具不得编造、估算、装饰或静默修改数据。若两条证据路径都无法在允许范围内支持数值标签，删除该标签，或把正文视觉替换为非数据插图。

## HTML 门禁（schema 1.0 历史长文）

> **schema 1.1 中长文不读本节、不执行本节门禁**——1.1 不调 `gzh-design`、不生成 `output/article.html`、不写 `output/html-qc.md`。schema 1.0 项目仍可走本节以保历史回放。

## HTML 门禁

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
python <SKILL_ROOT>/scripts/upgrade_preview_copy.py <文章目录>
```

然后点击已加固预览的复制按钮，把目标正文粘贴到干净的本地 `contenteditable` 区域或微信兼容的富文本沙箱。确认按钮报告 `clipboard-api`；若报告 `legacy-fallback`，记录降级，且不得假定块级层次仍然保留。检查粘贴后的剪贴板 HTML DOM，而不只看预览：验证内容层级、必需行内样式、链接目标、图片节点及来源、内容顺序，并确认不存在预览专用控件或标签。若已有登录的微信编辑器可用，再额外在那里验证粘贴；默认前置条件不得要求微信登录或凭据。标记阶段完成前，报告复制方法、两个检查宽度、粘贴目标，以及每项 DOM 和布局检查结果。

把两个检查宽度、图片加载结果、复制方法、粘贴目标、每项 DOM / 布局结果和全部九项微信长文排版契约结果写入 `output/html-qc.md`。只有五件套存在，且 `gzh-design`、确定性验证、两个浏览器预览检查和 pasted-DOM 检查全部通过后，才可标记 HTML 完成。缺失 `gzh-design` 会阻塞 HTML 完成；任何通用格式化器或手写 HTML 都不得替代此门禁。

`output/html-qc.md` 的结构按 [`assets/article-project-template/output/html-qc.template.md`](../../assets/article-project-template/output/html-qc.template.md)：

- 五件套存在性
- `gzh-design` 调用记录
- 9 项排版契约（3 文本级 + 5 视觉级 + `final.md` SHA256 绑定）
- 浏览器视口检查（≤390 / ≥900）
- 复制方法与粘贴目标
- DOM / 布局检查
