# Output Contract · feature-list

产出父级 `function-description.md` 产物的 §功能清单 章节（registry `output_section`: 功能清单）。输出格式必须匹配 `src/templates/stage-2-product/function-description.md` 中对应的表格。

## ID 契约

- 每个功能行携带稳定 ID `FEA-XXX`（FEA-001、FEA-002、…），全局唯一、零填充、无空缺、无重复。
- 每个 FEA-XXX 在 `所属故事 ST` 列追溯 ≥1 个已确认 `ST-XXX`——无孤儿功能。
- 每个 FEA-XXX 边界与其他所有 FEA 互不重叠。
- 功能移除后 ID 永不复用（补空会破坏审计历史）。

## FEA 行结构

| ID | 功能名称 | 所属故事 ST | 优先级 | 一句话描述 | 来源 |
|---|---|---|---|---|---|
| FEA-XXX | name | ST-XXX (comma-separated) | P0 / P1 / P2 | one-line scope + in/out | ST-XXX / decision |

- `所属故事 ST`: 该功能满足的已确认故事；必须包含 ≥1 个 `ST-XXX`。
- `优先级`: P0（核心，无 workaround）/ P1（重要，存在 workaround）/ P2（锦上添花），并记录理由。
- `一句话描述`: 说明边界——功能做什么、明确不做什么。
- `来源`: 确立该功能的 ST-XXX / 决策。

## 产物状态

| Status | Meaning | Downstream use |
|---|---|---|
| `draft` | 初始候选；Audit 未完成 | No |
| `needs_user_input` | 某关键范围/边界决策阻断确认 | No |
| `conditional_review` | 结构可评审，显式非阻断未知项 | No |
| `ready_for_human_review` | 自审通过，等待授权评审 | No |
| `confirmed` | 授权人工明确批准此版本 | Yes |
| `superseded` | 更新的已确认基线替代本版本 | No |

> 子 skill 永远不能向父产物写入 `confirmed`。只有 `pipeline.py review --decision approve` 可以。因此校验器的状态白名单排除 `confirmed`。

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

对 §功能清单 区块使用 `src/templates/stage-2-product/function-description.md` 中的所有标题（功能规格概览、功能清单、待确认问题、来源追溯）。若某功能无已确认内容，写 `待确认` 并关联问题或未知 ID；不要删除标题。

> 占位符 `待确认` 保留在中文 PRD 约定中。译者可在纯英文产物中使用 `[NEEDS CLARIFICATION]`，只要校验器识别两种形式。

## 人工职责

- 产品负责人：确认功能范围与边界。
- 业务负责人：确认功能集合与范围基线一致。
- 产品经理：检查完整性、互不重叠、优先级理由、下游可用性。
- 最终评审人：授权 §功能清单 基线。一人可兼任多个角色，但决策权必须明确。

## 下游交接

为下游子 skill 输出一份紧凑交接：

```text
confirmed_features          # FEA-XXX list
feature_boundaries          # in/out per FEA
feature_priority            # P0/P1/P2 per FEA
story_traceability          # FEA-XXX → ST-XXX map
open_nonblocking_unknowns
source_ids
```

不要在本交接中创建 UX 流程（→ `function-description`/`functional-flow`）、交互规则（→ `interaction-rules`）、页面骨架（→ `page-design`）、业务规则（→ `business-rules`）、字段校验（→ `validation-rules`）、状态表（→ `state-machine`）、异常路径（→ `exception-handling`）或验收依据（→ `acceptance-criteria`）。

## 澄清会话契约

每个 Clarify Session 在父产物的 `## Clarifications` 章节记录为一行结构化数据。每个 Session 一行，按 session id 排序：

| Field | Meaning | Example |
|---|---|---|
| `session_id` | 单调递增 `CL-NNN`，零填充 | `CL-004` |
| `category` | 6 类 影响 × 不确定性 之一（scope / data-model / UX / non-functional / integration / compliance） | `scope` |
| `question` | 本轮提出的唯一问题 | "名单来源" |
| `ai_preliminary_judgment` | AI 的初步回答及依据 | "Inferred from ST-002: CRM 导出 CSV; needs confirmation" |
| `options` | 2–5 个互斥选项（或"自由短答"） | A) CRM 导出 B) Excel 上传 C) 两者都支持 |
| `decision_owner` | 回答的范围负责人 | 市场部 王经理 |
| `blocking` | yes / no | `yes` |
| `deferral_risk` | 若推迟会破坏什么 | "名单导入功能边界无法确定" |
| `accepted_answer` | 人工回复后选定的选项 | `C` |
| `reflow_target` | 会被更新的产物章节 | `§功能清单 FEA-001` |
| `integrated_at` | 答案写回时的 ISO 时间戳 | `2026-08-13T10:00:00Z` |
| `integrated_by` | AI 或人类执行者 | `AI` |
| `audit_recheck` | 集成后重新审计的结果（`pass` / `fail` / `n/a`） | `pass` |

规则:

- 每个 Session 一行。绝不把多轮 Q+A 合并进一行。
- `accepted_answer` 必须在产物到达 `ready_for_human_review` 前填写。
- `reflow_target` 必须引用已存在的章节标题。
- `audit_recheck` 必须是最后填写的字段；若为 `fail`，将状态切回 `needs_user_input` 并再开一个 Session。
- 运行顺序见 `SKILL.md` § Clarify。
