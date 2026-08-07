# BLOCKED

## 第二任务（活人感同权重）基线核对异常（2026-08-07，证据）
- 任务书基线：`py -3.12 -m pytest tests -q` = 2 failed/151 passed，失败为 test_humanizer_adapter_binds_a_local_diagnostic_to_current_draft 与 test_humanizer_adapter_rejects_rewrite_and_stale_or_fact_changing_advice。
- 实测：**12 failed, 141 passed in 5.11s**（完整输出已贴会话）。与任务书基线对不上→按任务书「对不上就停，证据写 BLOCKED.md 最上面，用新实测基线继续」执行，本任务以 12 failed/141 passed 为基线。
- 12 项失败名：test_modular_optimization.py::DeliveryContractTests::test_cover_is_21_9_only_while_body_illustrations_remain_enabled；test_reference_integrity.py::ReferenceIntegrityTests::test_all_local_path_references_exist；test_wechat_delivery_contract.py 四项目（cover 21:9、gzh_design_author_cta、long_essay_prediction_bridge、wechat_publish_bridge）；test_wechat_route_contract.py 六项目（benchmark_learning_and_migration、long_essay_prediction_separates、migration_requires_post_status_receipt、skill_lists_all_public_routes、topic_signal_registry_eight_lane、video_route_excluded）。
- 归因：均为上一「省 token 改造」任务把 references/execution.md 与 quality-gates.md 拆成 execution/pipeline.md、execution/upgrade.md、execution/state.md、execution/visuals-html.md、quality-gates/prediction.md、quality-gates/visual-html.md 等分片，而 tests/ 断言直读旧单文件（execution.md、quality-gates.md），锚点字符串（如「SKILL.md` 核心约束第 1 条」「publish-reference.json」「输入回执」「单独确认」「cheat-status-receipt.json」在 SKILL.md、八路信号）被移动或压缩后不再命中。tests/ 只读，本任务不允许改，也不允许顺手修——留待裁决（建议：后续任务可在允许清单纳入 tests 契约文件或恢复锚点措辞）。
- 注：任务硬指标 1 原要求「py -3.12 -m pytest tests -q 仍为 2 failed/151 passed」；因基线对不上，本任务按新实测基线验收（12 failed/141 passed），并将最终 pytest 结果如实贴出。

## 第一段（省 token 改造）遗留
- 观察（非本任务改动，待裁决）：git status 显示 MERGE-LOG.md、OPTIMIZATION-PLAN.md 在会话开始前已从工作区删除（本会话未执行任何删除命令；首次 glob 时这两文件已不存在）；.workbuddy/、tests/_adapter-draft-fixture.md 为既有未跟踪文件。均不在本任务允许改动清单内，未处理。
- 其余无阻塞；任务 0/1/2 全部完成，硬指标验收通过（见 PROGRESS.md）。

## 第二任务交付回执（2026-08-07）
- 无新增阻塞。任务 1/2、weight_check 红→绿反向验证、基线复跑、readonly hash 全绿均完成；证据见 PROGRESS.md「当前进度」。
- 待裁决遗留（沿用上面可裁：拆片后 tests 直读旧单文件 12 项失败）依旧成立，本任务重跑后失败名逐字一致，均与本任务改动无关。
- 半托：活人感渠道效果由下一篇稿子亲验（human-writing 读取清单＋check_prose.py 输出），本任务期间无稿子实例，故不判成败，留待后续。
