## 预测门禁

根 Cheat 路由返回 Channel B JSON 后，父路由计算 `composite` 或写入预测数据前先验证：

```text
python <SKILL_ROOT>/scripts/blind_score_adapter.py validate <BLIND_JSON> <RUBRIC_NOTES> --script <CHEAT_PROJECT>/scripts/<id>.md
```

验证器从当前 rubric 推导 `rubric_version` 和准确的 7/9 维集合，检查每个维度字段，并可重新计算 12 字符脚本哈希前缀。验证失败就是预测门禁失败；不得补填缺失维度、接受不同 rubric 版本，或根据未验证响应计算 composite。详见 [`references/cheat-contracts.md`](../cheat-contracts.md#blind-score-contract)。

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

