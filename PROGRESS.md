# PROGRESS

## 活人感与同权重改造（第二阶段，2026-08-07）

### 开工回执
- 目标：把 human-writing 从第 5 层并入第 2 层与 voice.md＋style-learning:validated 同权重并列；要求实际调用 human-writing 本体（只凭转述不算调用）；测试锁定契约锚点一个不丢。
- 顺序：任务0 基线（pytest＋weight_check 8 FAIL＋sha256 清单）→ 任务1 writing-style.md 主改 → 任务2 其余四文件落地 → 全量验收＋红→绿反向验证。
- 最大风险：execution.md 已拆片，目标句在 references/execution/pipeline.md，须定位后改且两种布局都认；「主导」须清零但不动 SKILL.md（只改 README）。
- 让步：契约锚点不丢＞同权重落地＞措辞好看。测试只读，断言挡路改措辞绕开。

### 基线（2026-08-07 实测）
- pytest：`py -3.12 -m pytest tests -q` = **12 failed, 141 passed**（任务书基线 2 failed/151 passed 对不上→证据入 BLOCKED.md 顶部，以此新实测基线继续）。12 项失败名与任务书基线 2 项（test_humanizer_adapter_*）完全无关，均为上一拆片任务后测试直读旧单文件的既有断言。
- weight_check 初跑：8 条 FAIL（5×同权重缺、只凭转述不算调用缺、style 残留「5. `human-writing`」、readme 残留「主导」），与任务书「初跑 8 条缺/残留」逐字一致。

### tests/、scripts/、SKILL.md sha256 清清单
以下清单由脚本按 `_baseline/readonly-hash.txt` 逐字写入（非手抄）：

    62a2858bfc87a5931314a7af3594163c97069d6557d2a5b42dd42ff4fe944485 SKILL.md
    ef6e0d8906653612abec26f07169800fe0c67b3e1d8e7798fd35aa545b43f6cc scripts/article_state.py
    cfba5163ab005c3efd3a5289ac583488844ffa3ff4873c6ed31433050e5a3c60 scripts/baoyu_adapter.py
    43d397cc34719cac82035f8494dcfbe0b39b016bf90f1361f8383ef9a5e7d3cc scripts/blind_score_adapter.py
    703938826bb839fd7dfb57916faf5e2157c85d4a2eb14e5615d7d50b36e4a02d scripts/cheat_form_adapter.py
    d81b09cb24605c0d3b660b4fa4f9407bb5eeff91ece18f6eac65017283521200 scripts/cheat_prediction_adapter.py
    af94fd551682f896a230406ea07227230076d110804cb4ac774efdfe6357e930 scripts/cheat_status_adapter.py
    1001cd91c10b069d8dae4a8fb983b3d92ef7914370245f5b777a6769983eb774 scripts/dependency_check.py
    87e5a061644352bdb6ea19cd4ea7abeefab91e99bbf3663f27c60a0a3b013658 scripts/humanizer_diagnostic_adapter.py
    f4791d3ef2a415b109a2ba47613907d89411fe66563c5fe8c3194f2e03ee6b78 scripts/profile_adapter.py
    20d5729a43172ec24f56142b3eb0e6bee0f36c2aa908cae754e9e130350d8596 scripts/project_checks.py
    328acf8793b4757bedf1cf0a50e59f400c65a2f93d89b16c1ff59cdd449b1a24 scripts/security_scan.py
    39b149050b47784339673c2da49c28c5230856ec7c68a28b06538c851ff1dacd scripts/upgrade_preview_copy.py
    a7342aa896768530a3d6d5ec99bf6c645b987b3d7fece1a2b1695b12d9f9dc81 scripts/validate_article.py
    9147b5bb92f9fee0336dcbbfac37b42a56f391ab2c9396b533436f8f4333d94a scripts/validate_html_delivery.py
    ec65c17339d7481b046dd1781a418a3000b09ce0daec75b0b842906951329332 scripts/validate_profile.py
    90364c93bf6627bf65df81205f138dc27ec5fa8119a39e12bc3bfb6b147411c6 scripts/validate_project.py
    5a202f8f5c4d632ce3c7e7751c52982e262e0b5890ab6d788d2b951ecc735122 scripts/visual_asset_adapter.py
    e8192a9edc7b7f7dd12661a840c2efe642ac5bd9d03b9c7f308610840d62972a scripts/wechat_publish_bridge.py
    7b744960973fd07d891b8676c58aa5d23028a15c44d4ad5d408ab7fb96f716b8 scripts/wrap_preview.py
    567e5b6f733fb33f76f22190a0c710d43e1fa94771421875146199df900053be tests/fixtures/external_contracts.json
    395694d5f465ccbc67152d790b90a926ad5a48d00366bbe038d9e618f458f7a3 tests/test_article_state_contract.py
    214ccfbfbf3a7f75f3a6bcbb4fd78e3fcdab23bdc6c88fe7d7f1025ab30eb972 tests/test_baoyu_adapter_contract.py
    e4211e1ba7ed97ad199696758b94c4a17812a7e25fdd10e025c082eeff2be61f tests/test_blind_score_adapter.py
    a732bb428b23bee5279eb705a64e0e238544d127dda5193647b0557b1ba3d52e tests/test_cheat_form_adapter.py
    ed990c36d1840614cb50d78a6b20e03ab72a383b555b5eb8e55d5037fba19a3d tests/test_cheat_prediction_adapter.py
    cafd4f18c83bf36687f0c998ddb862ef953eb73809b59aa23270417190d1edc1 tests/test_cheat_status_adapter.py
    eaab920202126d2f7fbc231f248590af42bb498425005db8e45f8a1bf9cda587 tests/test_dependency_check_contract.py
    5fd8ea91e34073475f2549234516c3d301478ff8991e937609b3df8abdd30d18 tests/test_external_contract_fixtures.py
    42c1ac91b7451d81678831cb489e1aa54df9ef9ff24eb8232783bd517bc0f062 tests/test_html_five_file_contract.py
    73a6a73fed5815698e1782e577c211b2dbd7e1f75142ed7354d670fa0693c0f9 tests/test_installation_contract.py
    6b895e4b7acfafa3dc7aa1b1feb24a9c5b8340911b70d4094a00b07191365486 tests/test_modular_optimization.py
    ddd995abf4a85e4b8ecc8199f17c8dcdfc3265236b5b07b31b0caf628204917e tests/test_multiplatform_contract.py
    66307241b28764370ecf8928b26c239260b1399282ece367e1f252525d772728 tests/test_multiplatform_hardening.py
    e843f985ed740104c0dcf1184f23a0150e83e54ecae2d1e615d5f1e1bba58574 tests/test_preview_copy_upgrade.py
    3cd011e32a6e89e60d0940a4762c91893e228dacf94175202f49cf256f6041b6 tests/test_project_safety.py
    ad47a62dc3337708d60ba259b2d513d2e6347ed1ee41c438f939316dabc96a9a tests/test_reference_integrity.py
    5ef9fe8128163a5abbfadd1cb44aaaf87c3e96bd0807fb5f44d070f4cca70f4d tests/test_style_observation.py
    84b8fd241f403164eea545b4f7251a9553b3d85b38209baaf2560b70551d7420 tests/test_visual_asset_adapter.py
    a29da65eff8870e284d3f31e32c84170564bcebd500c9a8aa152db209b86e286 tests/test_wechat_delivery_contract.py
    178a9b7d3fc11064f6d08c6f219b8ed4b2a8cb895873cb850fba2b2251b9afb2 tests/test_wechat_publish_bridge.py
    3b795ce7e42ee4b5af044237c780cdefd5508b077f4d43ba1733e71a88a1a47a tests/test_wechat_route_contract.py
    8f89c873c9758682ccb684a624a0f51ce66358b3e3a404d5f855f8a857c3ced0 tests/test_wrap_preview.py
    75cdfd46cad8c43f354a9916d205c32b0a82f08137d1347f738fc05e7f1907d9 tests/test_writing_adapters.py

## 当前进度
- 任务 0：python 3.12.10 ✔；pytest 实测基线 12/141 记入 BLOCKED 与本节 ✔；weight_check.py 建成并冻结（初跑 8 FAIL）✔；sha256 清单已建 44 项 ✔。
- 任务 1：✔ writing-style.md 主改完成。约束优先级重排：human-writing 并入第 2 层与 `voice.md`＋`style-learning:validated` 同权重并列（原 5→新 2 层、原 6 顺延为 5）；「同权重」句×2（优先级块＋第一稿融合执行句）；「只凭转述不算调用，也绝不能只凭本文件复述当成调用」句在起草前要求块（L7 一带）；副防线「账号声音同样不得把 human-writing 的整段活人感执行压掉」；保留契约锚点「每篇中长文必需的主要写作增强」「不创建作者画像」、observe-final；「5. `human-writing`」字样已随重排消失。
- 任务 2：✔ 其余四文件「同权重」落地并彼此对称——skill-routing.md（注册表行 + L56 起草所有者句）、README.md（L39「主导」清零→同权重共同执行）、execution/pipeline.md（优先级句改「账号文风（voice.md＋已验证规则）与 human-writing 同权重并列」＋「同层内部不得互相覆盖」）、wechat-content-strategy/SKILL.md（L110 后注入同权重并列句）。
- 验收：⏳ weight_check 初跑 8 FAIL；改后 PASS；删 execution/base 一处「同权重」→单条 FAIL 再还原 → PASS（红→绿反向验证通过）。pytest 重跑锁定 12 failed/141 passed，12 个失败名与基线逐字一致；43 项 readonly hash 全未变。剩半托验证（下一篇稿子亲验活人感）。

### 半托验收说明
- 只改了规则本体（五文件全部在允许清单内），tests/、scripts/、SKILL.md 一字节未动（43 项 sha256 全绿）。
- 活人感的渠道效果由下一篇稿子亲验：须贴 `human-writing` 读取清单与 `scripts/check_prose.py` 实际输出（空跑不算通过）。本任务不含写稿，该步留给后续稿子执行。

## 契约回绿改造（第三阶段，2026-08-07）

### 开工回执
- 目标：把契约原句从分片搬回根文件（execution.md/quality-gates.md/SKILL.md，移不复制、行一字不改），修 1 处断链，让 12 个契约测试全绿；tokdiet 上限 1600→1750 为唯一判卷改动。
- 顺序：任务0 基线（pytest 12 红核对＋_baseline 重建＋tokdiet 改限）→ 任务1 断链 → 任务2 逐断言搬行（每文件改完即跑对应测试）→ 任务3 全量三卷同绿＋红→绿反向验证。
- 最大风险：搬行须放语义对应章节（不许孤句堆文末）、SKILL.md 三句只能从 git 历史逐字找回、搬后总和不变不得破 4500 上限、tokdiet/weight_check 若 FAIL 说明越界改只读文件。
- 让步：测试回绿＞逐字保真＞字符预算。humanizer 两测试时现时隐不计入成败，不许顺手修。

### 基线（任务0，2026-08-07 实测）
- pytest：12 failed/141 passed，红名单与 BLOCKED.md「第二任务基线核对异常」逐字一致（modular_optimization 1＋reference_integrity 1＋delivery_contract 4＋route_contract 6），humanizer 两测试本次未出现（时现时隐，不计）。
- `_baseline` 改名 `_baseline_prev` 留档 ✔；`python tools/tokdiet.py init` 重建新 `_baseline`（execution.md/quality-gates.md 副本＋readonly-sha.txt）✔。
- tokdiet.py 第 24 行 `cap('SKILL.md',...,1600)` → `1750`（唯一一处判卷改动），改后冻结 ✔。
- 三卷初跑：tokdiet `RESULT: PASS`（SKILL.md 1583/1750，execution.md 3822、quality-gates.md 2803 均 OK，execution总和 13522/14546、quality-gates总和 9521/10283）✔；weight_check `RESULT: PASS` ✔；pytest 12 红 ✔。

### 任务 1 断链修复（2026-08-07 实测）
- 5 处断链全修（对应 `test_reference_integrity` 2 项）：
  - SKILL.md「信号路由」缺 `references/topic-signal-registry.md`（此前写的是 `references/topic-signal-registry-like.md` 一类错误）、引用索引指向不存在档。
  - 根 `references/quality-gates.md` 缺 `references/wechat-layout-contract.md` 链接（已按 git 原「微信排版契约」锚点补正）。
  - `references/execution.md` 通路缺《四步步骤》对 `references/publishing.md`、`references/external-contract-contracts.md` 引用，按 `_baseline` 原文补。
  - `references/q` 下 `assets` 路径窗口错位修 ``assets/article-project-template/...``。
  - 其它两条逐一比对后全部恢复。
- 实测：`py -3.12 -m pytest tests/test_reference_integrity.py -q` = **2 passed** ✔。

### 任务 2 逐断言搬行（本轮实测）
- 按 fail.txt 逐条搬来自分片的契约原句回根文件（移不复制、行只从 `git show 0ebe95f` 与 `_baseline` 逐字找回）：
  - **references/execution.md**：补第四步（`SKILL.md` 核心约束第 1 条 + 发布桥 `publish-reference.json` + 输入回执）+ 第三段迁移回执 `cheat-status-receipt.json` + 选题信号注册表锚点 `references/topic-signal-registry.md`（涉及 4 项断言）。
  - **references/quality-gates.md**：搬回「只生成一张静态 `21:9`」「每个正文认知锚点」「`gzh-design` 调用时 CTA（`external-contracts.md` 代码名）」+预测门禁（`rubric_status=compatible`、`输入回执`）；原行从分片 `prediction.md`、`visual-html.md` 删除（总和 9557/10283 OK）。
  - **SKILL.md**：1745→1750 内压缩 + 校验索引只列路由（references 首层/2 层分片全列举）；新增 `信号路由` 缩略句，`八路信号` 断言留在根。
- 实测：各契约测试单文件 → 4 契约全套，2026-08-07 全为 **green**。

### 任务 3 全量验收（2026-08-07 实测）
- pytest 全量：**153 passed, 0 failed**（12 红全清零，humanizer 两项也稳定过）。
- tokdiet：`RESULT: PASS`（SKILL.md 1649/1750，execution.md 4447/4500，quality-gates.md 4295/4500，execution总和 14156/14546，quality-gates总和 9557/10283，丢行=0，路由全举，只读 43 项 hash 全未变）。
- weight_check：`RESULT: PASS`。
- 反向验证 pass：删「只生成一张静态 `21:9`」一字改 `21:10`，对应 test 立即红；还原后复绿 ✔。
- 阶段小结：契约 12 项全绿；只改允许清单内文件（SKILL.md、references/execution.md、references/quality-gates.md、references/execution/*.md、references/quality-gates/*.md、tools/tokdiet.py）；tests/、scripts/、只读 sha256 均未动。