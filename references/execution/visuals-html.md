## 视觉与 HTML

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

完成全部选定资产后，用
`python <SKILL_ROOT>/scripts/article_state.py record <PROJECT_ROOT> --role visuals --path visuals/assets/manifest.json`
把 manifest 纳入文章状态。

选择 Baoyu 轨道时，运行
`python <SKILL_ROOT>/scripts/baoyu_adapter.py prepare <文章目录>`，把生成的
`visuals/assets/baoyu/source.md` 交给根 Skill；结束后运行
`python <SKILL_ROOT>/scripts/baoyu_adapter.py verify <文章目录>`。

HTML 规则只见 `references/quality-gates.md` 的 HTML 门禁。通过 `gzh-design`
取得并校验纯 section 后，按以下固定映射生成项目产物。

HTML 阶段必须同时保留：

1. `output/article.html`
2. `output/article-preview.html`
3. `output/article-copy.html`
4. `output/article-copy-preview.html`
5. `output/html-qc.md`

`gzh-design` 的默认文件名（`{原文件名}_排版_{主题}.html` 和
`{原文件名}_预览.html`）不属于文章项目 schema。总控必须把它返回的纯
`<section>...</section>` 正文按下面的固定映射落盘；不得把默认命名直接登记为项目产物：

1. 将 `gzh-design` 的干净 section 写入绝对路径
   `<PROJECT_ROOT>/output/article.html`，并运行 `gzh-design` 的 HTML 校验。
2. 原样复制 `output/article.html` 为 `output/article-copy.html`；后者是人工粘贴
   交付物，`artifacts.html.path` 必须指向它。不要把预览外壳复制到该文件。
3. 用总控随附脚本分别生成两个预览壳：

   ```text
   python <SKILL_ROOT>/scripts/wrap_preview.py <PROJECT_ROOT>/output/article.html <PROJECT_ROOT>/output/article-preview.html
   python <SKILL_ROOT>/scripts/wrap_preview.py <PROJECT_ROOT>/output/article-copy.html <PROJECT_ROOT>/output/article-copy-preview.html
   ```

4. 只对 `output/article-copy-preview.html` 运行：

   ```text
   python <SKILL_ROOT>/scripts/upgrade_preview_copy.py <PROJECT_ROOT>/output/article-copy-preview.html
   ```

   复制加固、图片内嵌和 pasted-DOM 验收标准见 HTML 门禁。
5. 按 `assets/article-project-template/output/html-qc.template.md` 生成并填写
   `<PROJECT_ROOT>/output/html-qc.md`，并填写 HTML 门禁要求的全部字段。

每一步都使用实际的绝对 `<SKILL_ROOT>` 与 `<PROJECT_ROOT>`；文件完成前运行
`python <SKILL_ROOT>/scripts/validate_project.py article <PROJECT_ROOT>`。

## 失败与恢复

读取 `references/recovery-rules.md`。上游内容变化时找出最早变更阶段，运行 `python <SKILL_ROOT>/scripts/article_state.py invalidate <文章目录> --stage <阶段>` 并先持久化状态；不要用状态切换代替失效传播，也不要删除有效上游产物。

头图或正文配图失败时保留提示词和错误记录；HTML 失败时停止交付。恢复必须继续到所有受影响的下游 `stale` 项重新生成和验证。

## 发布边界与最终交付

交付包、`html_ready`、`publicly_published`、人工发布边界和失败恢复只按
`references/publishing.md` 执行；本节不复述发布规则。
