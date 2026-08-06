# Phase 1 规则合并记录

> 行号均指 Phase 1 合并前快照。裁决遵循“约束取并集、保留更严格版本”；命令与产物路径可留在 `execution.md`，但规则正文只能留在 owner。

## R1：21:9 单封面与双兜底

- 合并前副本：`SKILL.md:12`、`references/execution.md:222,275-281`、`references/quality-gates.md:134`、`references/skill-routing.md:18,25,98-116`。
- 差异证据：入口摘要只写单图、比例和适配器；执行稿额外限定 `.poster.wide`、拒绝视频并给出命令；路由稿额外要求近完整标题、一个强视觉关系、账号视觉规则优先以及无可用路线时阻塞；门禁稿包含 Guizang/ImageGen 两级兜底和 companion 输出拒绝。
- 裁决：`references/quality-gates.md` 为唯一 owner，合并全部更严格条件；`execution.md` 只保留命令和产物路径，其他位置只链接。
- 冲突：无。各副本是约束子集，不存在相反行为。

## R2：HTML 五件套与复制门禁

- 合并前副本：`references/execution.md:223,296-343,353-358`、`references/quality-gates.md:147-196`、`references/publishing.md:5-7`、`references/skill-routing.md:22,136-138`。
- 差异证据：门禁稿包含五件套、双视口、复制方法、pasted DOM、CTA 与 QC；执行稿独有 section 到五件套的固定映射和脚本命令；发布稿只定义 `html_ready` 的人工交付语义。
- 实质冲突：`quality-gates.md:168` 与 `skill-routing.md:138` 把项目预览归给 `gzh-design`，而 `execution.md:313-331` 与 Phase 0 的 `wrap_preview.py` 把项目预览归给总控。
- 用户裁决：`gzh-design` 负责生成并校验纯 section；总控用 `wrap_preview.py` 生成两份项目预览，再加固 copy preview。
- 裁决：`references/quality-gates.md` 为规则 owner；`execution.md` 保留固定映射与命令；`publishing.md` 只保留状态和人工交付边界。

## R3：八路选题信号

- 合并前副本：`references/execution.md:214,229-239`、`references/skill-routing.md:27-50`、`references/quality-gates.md:18`、`references/topic-signal-registry.md:1-40`。
- 差异证据：registry 已列 lane、适用性、状态和候选字段；执行稿额外写预检、后端、去重、Cheat 分流与确认；路由稿额外写 fan-in 次序和部分失败语义；门禁稿强调信号不是事实证据。
- 实质冲突：registry 与文档排除 `cheat-trends`，但 `dependency_check.py` 的 `topic`、`topic-ai`、`news-card`、`news-card-ai` 仍将其设为必需依赖。
- 用户裁决：从四个预检中删除 `cheat-trends`；八路 registry 是公众号信号唯一 owner，`cheat-trends` 不调用、不注册为 lane。
- 裁决：把完整编排并入 `references/topic-signal-registry.md`，其他位置只链接。

## R4：Ian / Baoyu 正文配图分轨

- 合并前副本：`SKILL.md:12`、`references/execution.md:222,283-294`、`references/quality-gates.md:136-145`、`references/skill-routing.md:19-21,118-134`。
- 差异证据：路由稿的分类最完整，含精确语义优先、无信息任务不出图、profile 规则优先和逐轨预检；门禁稿独有数值证据与 Baoyu 终稿哈希门禁；执行稿独有 adapter 命令。
- 裁决：`references/quality-gates.md` 为唯一 owner，取全部约束并集；执行稿只保留命令。
- 冲突：无。

## R5：Cheat 必须真实调用

- 合并前副本：`SKILL.md:8`、`references/execution.md:227`、`references/skill-routing.md:52-78`、`references/quality-gates.md:3-5`。
- 差异证据：入口稿包含全局禁止模拟、迁移确认和排除路由；执行稿列 12 个公开路由；路由稿补充不得复制或近似公式与协议；门禁稿补充依赖失败时必须停止并报告 runtime 缺口。
- 裁决：`SKILL.md` 核心约束第 1 条为全局 owner，列明全部公开路由并保留最严格禁止项；依赖门禁只保留检查与错误报告，不复述 Cheat 行为。
- 冲突：除 R3 已由用户裁决的 `cheat-trends` 预检矛盾外，无。

## NEEDS-REVIEW

无。两项实质冲突均已取得用户明确裁决。

## 反向抽查

- R1：通过。`quality-gates.md` 可反向找到单图、`21:9`、近完整标题、Guizang、素材/路线双兜底、adapter 与无路线阻塞；其他运行文档仅保留链接或命令。
- R2：通过。`quality-gates.md` 与 `execution.md` 可反向找到五件套、section 固定映射、双视口、`wrap_preview.py`、复制加固、pasted DOM、CTA 与 QC；`publishing.md` 只保留人工交付状态边界。
- R3：通过。`topic-signal-registry.md` 可反向找到八 lane、状态、适用性、后端、去重、根 Cheat 分流与用户确认；四个依赖 stage 已移除 `cheat-trends`。
- R4：通过。`quality-gates.md` 可反向找到 Ian/Baoyu 分类、逐轨预检、adapter、manifest、数值证据与 Baoyu 终稿哈希；`execution.md` 仅保留产物命令。
- R5：通过。`SKILL.md` 核心约束第 1 条可反向找到 12 个公开路由、根调用、禁止模拟/复现/复制/近似、内部与排除路由及迁移回执；依赖门禁仅报告 runtime 缺口。

## Phase 2 契约归并

- Cheat 五份小契约归并为 `references/cheat-contracts.md`，各契约保留为独立 H2。
- 外部五份小契约归并为 `references/external-contracts.md`，各契约保留为独立 H2。
- 所有仓库内旧文件路径已迁移到新文件及对应锚点；四份指定运行文档已中文化，并保留 `MUST` / `MUST NOT` 强度标记。

## Phase 3 端到端加载抽查

从 `SKILL.md` 选择 long-essay 后，按下表模拟标准路径。每个阶段直接加载 1–2 份 reference；`execution.md` 只在需要阶段命令或产物映射时作为其中一份，不再承载 owner 规则。

| 阶段 | 直接加载 | 抽查结果 |
|---|---|---|
| 入口与账号 | `onboarding.md`；需要 profile 字段时再加 `account-profile-schema.md` | 1–2 份，可确定目录、导入与确认边界 |
| 依赖与项目状态 | `execution.md` + `article-state-schema.md` | 2 份，可运行预检并建立状态 |
| 选题与调研 | `topic-signal-registry.md` + `quality-gates.md` | 2 份，可完成信号汇聚和事实门禁 |
| 大纲、起草与审校 | `quality-gates.md` + `writing-style.md` | 2 份，可完成策略调用、文风卡、正文与终检 |
| 预测 | `quality-gates.md` + `cheat-contracts.md` | 2 份，可完成哈希、形态、盲评分与不可变预测门禁 |
| 视觉 | `quality-gates.md` + `execution.md` | 2 份，前者给 owner 规则，后者只给 adapter 命令 |
| HTML | `quality-gates.md` + `execution.md` | 2 份，前者给五件套与复制验收，后者给固定映射命令 |
| 发布与复盘 | `publishing.md` + `wechat-publish-bridge.md` | 2 份，可区分人工交付、公开确认与 Cheat 回执 |
| 失败恢复 | `recovery-rules.md` + `article-state-schema.md` | 2 份，可传播 `stale` 并恢复下游 |

`external-contracts.md` 仅在检查具体外部响应边界、CTA 或 manifest schema 时按需替换同阶段的运行手册，不作为标准阶段的第三份常驻文档。

伴生 Skill 抽查通过：`wechat-content-strategy` 未引用本轮移动路径；`wechat-style-learning` 只引用自身 `scripts/edit_learning.py` 与主 Skill 的稳定 `scripts/validate_project.py profile` 接口。本轮删除的 10 个旧契约文件名在源码与文档中均无残留。
