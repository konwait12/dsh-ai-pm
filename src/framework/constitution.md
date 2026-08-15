# PRD Scaffold 宪法

1. **业务真相始终由人类拥有。** AI 可以进行推断、调研与建议，但只有被授权的人类才能确认事实、范围、选择与最终交付。
2. **证据与不确定性必须可见。** 事实、决策、假设、AI 推断、未知与冲突，绝不被压缩成虚假的确定性。
3. **工作遵循三阶段注册表。** 阶段提供上下文；五个 Work Item Skill 执行实际工作；产物不定义架构。注册表在任何 pipeline 运行前必须通过 `registry_contract_check`（schema + 模板↔校验器闭环）。
4. **可追溯性必须是显式的。** 下游功能与规则链接到上游故事与目标；变更从最早受影响的条目开始回流（reflow）。
5. **强制 PRD-only 范围。** 调研、图表、原型与分析均为 PRD 服务。开发规划、测试套件与手册保持在下游。
6. **人工关卡不可绕过。** 机器检查产出候选，而非批准。拒绝与追溯失败会阻断推进。
7. **事件溯源不可篡改。** 审计事件（`.audit/events.jsonl`）是 review/change/confirm/reflow 生命周期的唯一事实来源。篡改 `prev_hash`、`event_sha256` 或单调递增的 `recorded_at` 属于 CRITICAL 级破坏；`projection_cache` 是派生视图，必须能够仅凭事件日志重建。
8. **校验器只讲一种错误语言。** 每个校验器都通过 `validation_errors.make_issue` 输出问题（severity / check_id / expectation / actual / repair_hint）。原始 Python traceback 绝不展示给用户；意外异常通过 `wrap_unexpected` 包装。
