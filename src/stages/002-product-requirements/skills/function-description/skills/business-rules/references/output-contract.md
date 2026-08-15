# Output Contract · business-rules

产出父级 `function-description.md` 产物的 §业务规则 章节（registry `output_section`: 业务规则）。输出格式必须匹配 `src/templates/stage-2-product/function-description.md` 中对应的表格。

## ID 契约

- 每个规则行携带稳定 ID `BR-XXX`（BR-001、BR-002、…），全局唯一、零填充、无空缺、无重复。
- 每条 BR-XXX 恰好挂接在父产物的一个 `FUN-XXX` 区块下——功能区块之外无孤儿规则。
- 每条 BR-XXX 的 `来源` 引用一个已确认的 `ST-XXX` 或 `FEA-XXX`。
- 规则移除后 ID 永不复用（补空会破坏审计历史）。

## 产物状态

| Status | Meaning | Downstream use |
|---|---|---|
| `draft` | 初始候选；Audit 未完成 | No |
| `needs_user_input` | 某关键约束或策略决策阻断确认 | No |
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

对 §业务规则 区块使用 `src/templates/stage-2-product/function-description.md` 中的所有标题（规则索引、分功能详述、规则冲突检查、事实与决定、待确认问题、来源追溯）。若某规则无已确认内容，写 `待确认` 并关联问题或未知 ID；不要删除标题。

> 占位符 `待确认` 保留在中文 PRD 约定中。译者可在纯英文产物中使用 `[NEEDS CLARIFICATION]`，只要校验器识别两种形式。

## 规则行结构

| ID | 规则描述 | 类型 | 触发条件 | 约束/逻辑 | 来源 |
|---|---|---|---|---|---|
| BR-XXX | EARS-style statement | 计算 / 约束 / 条件 / 权限 / 时序 | exact trigger | closed logic + reject behavior | ST-XXX / FEA-XXX |

## 人工职责

- 产品负责人：确认规则行为与策略。
- 业务策略负责人：确认约束与计算（阈值、配额、截止时间、公式）。
- 产品经理：检查完整性、确定性、来源覆盖、下游可用性。
- 最终评审人：授权 §业务规则 基线。一人可兼任多个角色，但决策权必须明确。

## 下游交接

为下游子 skill 输出一份紧凑交接：

```text
confirmed_rules            # BR-XXX 列表
rule_class_per_row         # 计算/约束/条件/权限/时序
input_fields_affected      # 哪些 F-XXX 字段输入到哪条规则
state_triggers_from_rules  # 门控 state-machine 迁移的条件
accepted_assumptions
open_nonblocking_unknowns
source_ids
```

不要在本交接中创建字段校验（→ validation-rules）、状态表（→ state-machine）、异常路径（→ exception-handling）或验收依据（→ acceptance-criteria）。

## 澄清会话契约

每个 Clarify Session 在父产物的 `## Clarifications` 章节记录为一行结构化数据。每个 Session 一行，按 session id 排序：

| Field | Meaning | Example |
|---|---|---|
| `session_id` | 单调递增 `CL-NNN`，零填充 | `CL-004` |
| `category` | 6 类 影响 × 不确定性 之一（scope / data-model / UX / non-functional / integration / compliance） | `data-model` |
| `question` | 本轮提出的唯一问题 | "VIP discount threshold" |
| `ai_preliminary_judgment` | AI 的初步回答及依据 | "Inferred from ST-002: spend ≥ ¥500k/yr; needs confirmation" |
| `options` | 2–5 个互斥选项（或"自由短答"） | A) ¥300k B) ¥500k C) ¥1M |
| `decision_owner` | 回答的策略负责人 | VP of Sales |
| `blocking` | yes / no | `yes` |
| `deferral_risk` | 若推迟会破坏什么 | "Discount tiers remain undecidable" |
| `accepted_answer` | 人工回复后选定的选项 | `B (¥500k)` |
| `reflow_target` | 会被更新的产物章节 | `§业务规则 BR-003` |
| `integrated_at` | 答案写回时的 ISO 时间戳 | `2026-08-13T10:00:00Z` |
| `integrated_by` | AI 或人类执行者 | `AI` |
| `audit_recheck` | 集成后重新审计的结果（`pass` / `fail` / `n/a`） | `pass` |

规则:

- 每个 Session 一行。绝不把多轮 Q+A 合并进一行。
- `accepted_answer` 必须在产物到达 `ready_for_human_review` 前填写。
- `reflow_target` 必须引用已存在的章节标题。
- `audit_recheck` 必须是最后填写的字段；若为 `fail`，将状态切回 `needs_user_input` 并再开一个 Session。
- 运行顺序见 `SKILL.md` § Clarify。
