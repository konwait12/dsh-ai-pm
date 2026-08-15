# 运行时契约

## 知识状态（Knowledge States）

`FACT`、`DECISION`、`ASSUMPTION`、`AI_INFERENCE`、`UNKNOWN`、`CONFLICT` 是仅有的知识状态标签。只有有出处的（sourced）事实与已记录的人工决策，才可以被视为已确认的业务真相。

## 产物状态（Artifact States）

`draft`、`needs_user_input`、`conditional_review`、`ready_for_human_review`、`confirmed`、`superseded`、`simulated`。

`confirmed` 需要 `reviewer`、`reviewed_at` 以及一条人工 `ReviewRecord`。自动化可以校验候选，但不能确认它。

## 共享记录（Shared Records）

- `SourceRecord`：id、location、type、provider、captured_at、scope。
- `QuestionRecord`：id、question、initial_judgment、evidence、options、impact、owner、reflow_target。
- `DecisionRecord`：id、decision、alternatives、decider、rationale、decided_at、impact_scope。
- `ReviewRecord`：work_item、artifact_version、artifact_content_sha256、decision、reviewer、reviewer_id、reviewer_role、reviewed_at、record_created_at、record_sha256、comments。
- `ChangeRecord`：change_type、target、reason、source、downstream_impact。
- `TraceabilityLink`：source_id、target_id、relation、evidence_location。
- `AuditEvent`：event_id、session_id、event_type、prev_hash、payload、payload_sha256、recorded_at、event_sha256。
  - event_id：在会话内单调递增，用于哈希链校验。
  - session_id：需求目录名（REQ-NNN-*），按 Work Item 对事件分组。
  - event_type：review | change | decision | confirm | reject | reflow | init。
  - prev_hash：上一条事件规范化 JSON 的 SHA-256；首条事件使用哨兵值（sentinel）。
  - payload：被引用记录（ReviewRecord / ChangeRecord / DecisionRecord）的路径，或内联 dict。
  - payload_sha256：被引用记录体的 SHA-256（同步检测事件与记录两者的篡改）。
  - recorded_at：ISO-8601 UTC 时间戳；在会话内必须单调递增。
  - event_sha256：覆盖除 event_sha256 自身之外所有字段的自指纹（self-fingerprint）。
- `ProjectionCache`：schema_version、session_id、generated_at、event_count_snapshot、audit_chain_ok、work_items、derived_from_events。
  - schema_version：投影格式版本（当前为 1）。
  - session_id：需求目录名，镜像 AuditEvent.session_id。
  - generated_at：最近一次重建的 ISO-8601 UTC 时间戳。
  - event_count_snapshot：已折叠的事件数量；与 `len(replay_events)` 比较以检测是否过期。
  - audit_chain_ok：构建时 `audit_log.verify_chain` 是否干净通过。
  - work_items：按 Work Item 分组的数据桶（见下文）；由 AuditEvent 事件流 + 产物 frontmatter 事实数据折叠而成。
  - derived_from_events：参与生成该投影的 event_id 列表（用于重放的来源追溯）。
  - Work-item 数据桶字段：status、artifact_path、artifact_content_sha256、artifact_version、artifact_id_frontmatter、reviewer、reviewer_id、reviewer_role、reviewed_at、confirmed_at、latest_review_record、latest_review_decision、superseded、superseded_reason、last_change_reason、last_changed_at、_legacy_fallback。
  - `_legacy_fallback: true` 标记一个其 latest_review_record 来自 glob+sort 兜底的 Work Item（audit_log 之前的旧需求）；校验器可据此输出 WARN。
- `ValidatorIssue`：severity、blocking、check_id、check_family、location、field_path、message、expectation、actual、repair_hint、source_ref。
  - severity：`CRITICAL` | `HIGH` | `MEDIUM` | `INFO`（大写标签；绝不用小写）。
  - blocking：布尔值；CRITICAL/HIGH 默认 True，MEDIUM/INFO 默认 False。
  - check_id：稳定的机器可读检查标签（如 `state_machine.no_outgoing`）；跨代码重构保持稳定，便于用户追踪复发。
  - check_family：校验器家族（如 `property_check`、`branch_validator`）；用于测试汇总中的分组。
  - location：产物相对于 req_dir 的路径（或 `<artifact>` 占位符）。
  - field_path：指向违规字段的点分路径（如 `frontmatter.status`、`tables.BR-007.规则内容`、`sections.3`）。
  - message：人类可读的单行说明；省略时自动由 expectation/actual 推导。
  - expectation：校验器期望的内容（wanted state）。
  - actual：校验器实际发现的内容（观察到的状态）。
  - repair_hint：可执行的修复指引（不只是"X 缺失"，而是如何修复）。
  - source_ref：为该检查提供依据的宪法条款 / skill 输出契约章节 / DEC-SRC id。
- `RegistryContract`：由 `registry_contract_check.py` 强制执行的 schema + 闭环不变量。
  - Schema 形状：`workflow-registry.json` 必须声明 `stages[]`（每个含 `id`、`name`、`path`、`work_items`）、`work_items[]`（每个含 `id`、`name`、`order`、`stage`、`skill_path`、`artifact_dir`、`artifact_file`、`artifact_prefix`、`required_outputs`、`predecessors`、`legacy_wave`、`legacy_artifact_dir`、`reviewer_roles`、`human_gate`）以及 `internal_capabilities[]`。
  - 引用完整性：每个 `predecessors` / `depends_on` / `parent_work_item` 都必须解析到已存在的 work_item id。
  - 模板↔校验器闭环：skill 模板中声明的每个 frontmatter 字段，都必须在该 skill 的 `validate_artifact.py` 中被引用（AST 校验）；出现偏离即为 E3_drift。
  - 运行顺序：`registry_contract_check.py` 是 `run_tests_mac.sh` 的第一个阶段；任何失败都会在 consistency_check 运行之前中止。

## 校验器问题格式（Validator Issue Format）

每个校验器都必须通过 `validation_errors.make_issue` 输出问题。原始 Python traceback 绝不展示给用户；意外异常通过 `validation_errors.wrap_unexpected` 包装。每个校验器的 `--json` 输出都必须暴露 `errors`（阻断性问题）、`warnings`（非阻断）与 `info`（诊断信息）数组，每个数组包含 `ValidatorIssue` 字典。`validation_errors.aggregate_by_check_id` 为测试汇总提供跨校验器的聚合。

## 注册表契约（Registry Contract）

`workflow-registry.json` 是三阶段 pipeline 形状的唯一事实来源。`registry_contract_check.py` 在任何其他测试运行之前强制校验 schema 形状、引用完整性以及模板↔校验器闭环。新增一个 skill 需要：(1) 在注册表中声明它；(2) 提供带 frontmatter 字段的模板；(3) 在 `validate_artifact.py` 中引用每一个 frontmatter 字段。任何偏离都会导致 E3_drift 失败并阻断 pipeline。

## 确认不变式（Confirmation Invariant）

机器检查、模拟（simulation）、fixtures 与非交互式标志，在缺少匹配 `00-input/authorized-reviewers.json` 的评审人时，都不能创建或维持正式确认。每一次新评审都会把决策绑定到被评审的版本及其 SHA-256，并在产物的 frontmatter 状态被翻转之前，向 `.audit/events.jsonl` 追加一条 `AuditEvent`——事件先写入、状态后变更，因此日志总能重放该决策。人工关卡或跨产物关卡失败，会使整个命令失败。企业级身份验证仍属于未来 SSO 或飞书适配器的职责。
