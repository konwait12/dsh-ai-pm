# 运行时工作流

阶段、Work Item、Skill 与产物路径的机器可读来源是 `workflow-registry.json`。

## 主干（Backbone）

```text
001 业务需求阶段
  project-background-goal
  → 人工确认
  user-journey-and-stories
  → 人工确认
002 产品需求阶段
  product-ux
  → 人工确认
  function-description
  → 人工确认
003 PRD 汇总阶段
  prd-assembly
  → 最终人工确认
```

## Work Item 循环（Work-Item Cycle）

```text
Preflight → Intake → Think → Clarify → Generate
→ Audit → Human Gate → Commit / Reflow
```

Clarify（澄清）与 reflow（回流）是当前 Work Item 内部的状态，不是强制性的顶层分支。头脑风暴用于发现候选；由人类决定哪些候选成为需求。

每次经过 `Human Gate` 和 `Commit / Reflow` 的转换，也会以相应的事件类型 `review` / `confirm` / `change` / `reflow`，通过 `audit_log.append_event` 向 `.audit/events.jsonl` 追加一条 `AuditEvent`——事件先于状态变更，因此该循环总能从日志重放。

## 审计层（Audit Layer）

脚手架维护一个三层审计基础（借鉴 Harness）：

1. **`audit_log`**（`src/scripts/audit_log.py`）——只追加（append-only）的 `.audit/events.jsonl` 是 review/change/confirm/reflow/init 生命周期的唯一事实来源。每个事件携带 `prev_hash`（哈希链）+ `event_sha256`（自指纹）+ `payload_sha256`（记录体绑定）+ 单调递增的 `recorded_at`。`verify_chain` 检测任何篡改；`reconstruct_causality` 重建完整因果链。
2. **`projection_cache`**（`src/scripts/projection_cache.py`）——将事件日志折叠进 `.audit/projection.json`，即每个 Work Item 最新状态 / 产物哈希 / 评审人 / 评审记录的物化视图。`is_stale` 触发重建；`latest_review_for` 返回最新评审记录的路径 + 哈希。
3. **`registry_contract_check`**（`src/scripts/registry_contract_check.py`）——注册表 schema + 模板↔校验器字段闭环（E3_drift）。作为 `run_tests_mac.sh` 的第一项检查（Phase 0）运行；任何失败都会中止后续测试（fail loud）。

不变式：**事件 ⟺ 模型可见状态**——任何 review/change 在它出现在 `events.jsonl` 之前都不被视为真实存在。校验器读取投影（projection），绝不直接 glob+sort 扫描 markdown（旧需求回退到 glob+sort 并给出警告）。

## 进入与退出（Entry And Exit）

- 只有当所有已注册的前置条目（predecessors）都为 `confirmed` 时，一个 Work Item 才能开始。
- 稀疏或冲突的输入应路由到 `needs_user_input`，而不是编造输出。
- 机器校验可以产出 `ready_for_human_review`，但永远不能产出 `confirmed`。
- 人工拒绝与跨产物追溯失败会阻断推进并返回失败。
- PRD assembly 只聚合已确认的内容，不得新增需求。
- 校验器从 `projection_cache.read_projection` 读取最新评审记录，仅对旧需求（没有 `.audit/events.jsonl` 的需求）回退到 glob+sort；该回退会发出警告，使迁移面保持可见。

## 条件支持（Conditional Support）

- `competitive-research`：当需要外部证据时，以业务或功能模式运行。
- `feasibility-analysis`：在进入主干之前，评估市场 / 技术 / 成本 / 风险维度的可行性；多方案权衡作为一个章节处理。
- `requirement-restate`：当输入稀疏、来源冲突或 L0 仅停留在想法层面时，提供需求重举能力（复述 + 发散）。
- `tracking-plan`：当某个功能需要度量数据时，提供数据追踪 / 埋点（instrumentation）计划。
- `issue-record`：跨阶段的问题清单；任何 Work Item 送审前必须先完成 B3 收口。

可视化仍是 toolkit 的一项能力。只有 Work Item 契约显式要求流程表示时，才需要它。
