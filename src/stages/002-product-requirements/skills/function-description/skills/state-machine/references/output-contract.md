# Output Contract · state-machine

产出父级 `function-description.md` 产物的 §状态变化 章节（registry `output_section`: 状态变化）。输出格式必须匹配 `src/templates/stage-2-product/function-description.md` 中对应的表格。

## ID 契约

- 每个状态定义行与每条转移行都携带稳定 ID `STATE-XXX`（STATE-001、STATE-002、…），全局唯一、零填充、无空缺、无重复，绝不与 `BR-XXX`（业务规则）或 `ST-XXX`（用户故事）混淆。
- 每个 STATE-XXX 恰好挂接在父产物的一个 `FUN-XXX` 区块下——无孤儿转移。
- 每条转移行的 `来源` 引用一个已确认的 `BR-XXX` / `IX-XXX` / 故事声明。
- 状态或转移移除后 ID 永不复用（补空会破坏审计历史）。

## 产物状态

| Status | Meaning | Downstream use |
|---|---|---|
| `draft` | 初始候选；Audit 未完成 | No |
| `needs_user_input` | 某未定义的转移或守卫决策阻断确认 | No |
| `conditional_review` | 结构可评审，显式非阻断未知项 | No |
| `ready_for_human_review` | 自审通过，等待授权评审 | No |
| `confirmed` | 授权人工明确批准此版本 | Yes |
| `superseded` | 更新的已确认基线替代本版本 | No |

## 版本规则

- 起始候选 `v0.1`。
- 每次人工要求修订递增小版本：`v0.2`、`v0.3`。
- 首次确认基线用 `v1.0`，除非宿主项目定义了其他策略。
- 保留人工可见版本之间的简明变更摘要，不保留每次内部自审迭代。

## 知识状态标签

| Label | Definition |
|---|---|
| `FACT` | 来源授权范围内显式的来源声明 |
| `DECISION` | 授权人工的显式决定 |
| `ASSUMPTION` | 为分析而接受但未确认的临时条件 |
| `AI_INFERENCE` | AI 推导的解读，有证据但非业务事实 |
| `UNKNOWN` | 缺失信息 |
| `CONFLICT` | 来源声明互不兼容，需裁决 |

## 必需章节

对 §状态变化 区块使用 `src/templates/stage-2-product/function-description.md` 中的所有标题（状态定义、状态转移表、状态机图 Mermaid、状态完备性检查、事实与决定、待确认问题）。若某状态或转移无已确认内容，写 `待确认` 并关联问题或未知 ID；不要删除标题。

> 占位符 `待确认` 保留在中文 PRD 约定中。译者可在纯英文产物中使用 `[NEEDS CLARIFICATION]`，只要校验器识别两种形式。

## 状态定义行结构

| 状态 ID | 状态名称 | 所属功能 (FUN) | 描述 | 进入条件 | 退出条件 |
|---|---|---|---|---|---|
| STATE-XXX | unique, consistent name | FUN-XXX | one-line meaning | decidable condition | decidable condition |

## 转移行结构

| 当前状态 | 触发事件 | 目标状态 | 条件 | 副作用 | 来源 (BR/IX) |
|---|---|---|---|---|---|
| State-A | event | State-B | decidable guard | named effects or 「无」 | BR-XXX / IX-XXX |

被禁止的转移列出时目标为「不允许」并说明理由；绝不留空。

## 人工职责

- 产品负责人：确认生命周期行为与转移策略。
- 业务负责人：确认根植于业务规则的守卫条件与副作用触发。
- 产品经理：检查完整性、守卫精确性、来源覆盖、下游可用性。
- 最终评审人：授权 §状态变化 基线。一人可兼任多个角色，但决策权必须明确。

## 下游交接

为下游子 skill 输出一份紧凑交接：

```text
confirmed_states            # STATE-XXX 列表（按实体）
transition_matrix           # 状态 × 事件 → 目标 + 守卫 + 副作用
terminal_states             # 无合法出边转移的状态
illegal_transitions         # 显式的被禁止转移矩阵
state_triggers_for_events   # 哪些事件映射到异常/恢复路径
accepted_assumptions
open_nonblocking_unknowns
source_ids
```

不要在本交接中创建异常/恢复叙述（→ exception-handling）或验收依据（→ acceptance-criteria）；只把它们作为触发引用。

## 澄清会话契约

每个 Clarify Session 在父产物的 `## Clarifications` 章节记录为一行结构化数据。每个 Session 一行，按 session id 排序：

| Field | Meaning | Example |
|---|---|---|
| `session_id` | 单调递增 `CL-NNN`，零填充 | `CL-010` |
| `category` | 6 类 影响 × 不确定性 之一（scope / data-model / UX / non-functional / integration / compliance） | `data-model` |
| `question` | 本轮提出的唯一问题 | "Timeout auto-cancel interval" |
| `ai_preliminary_judgment` | AI 的初步回答及依据 | "Inferred from BR-009: 30 min unpaid → auto-cancel; needs confirmation" |
| `options` | 2–5 个互斥选项（或"自由短答"） | A) 15min B) 30min C) 24h |
| `decision_owner` | 回答的业务负责人 | Ops lead |
| `blocking` | yes / no | `yes` |
| `deferral_risk` | 若推迟会破坏什么 | "Timeout transition undecidable" |
| `accepted_answer` | 人工回复后选定的选项 | `B (30min)` |
| `reflow_target` | 会被更新的产物章节 | `§状态变化 STATE-004` |
| `integrated_at` | 答案写回时的 ISO 时间戳 | `2026-08-13T12:00:00Z` |
| `integrated_by` | AI 或人类执行者 | `AI` |
| `audit_recheck` | 集成后重新审计的结果（`pass` / `fail` / `n/a`） | `pass` |

规则:

- 每个 Session 一行。绝不把多轮 Q+A 合并进一行。
- `accepted_answer` 必须在产物到达 `ready_for_human_review` 前填写。
- `reflow_target` 必须引用已存在的章节标题。
- `audit_recheck` 必须是最后填写的字段；若为 `fail`，将状态切回 `needs_user_input` 并再开一个 Session。
- 运行顺序见 `SKILL.md` § Clarify。
