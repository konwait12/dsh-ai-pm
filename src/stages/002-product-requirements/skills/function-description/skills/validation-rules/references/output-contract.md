# Output Contract · validation-rules

产出父级 `function-description.md` 产物的 §系统校验 章节（registry `output_section`: 系统校验）。输出格式必须匹配 `src/templates/stage-2-product/function-description.md` 中对应的表格。

## ID 契约

- 每个校验行携带稳定 ID `VL-XXX`（VL-001、VL-002、…），全局唯一、零填充、无空缺、无重复，绝不与 `BR-XXX` 混淆。
- 每条 VL-XXX 恰好挂接在父产物的一个 `FUN-XXX` 区块下——功能区块之外无全局堆叠。
- 每条 VL-XXX 的 `来源` 引用一个已确认的 `BR-XXX` / `FEA-XXX` / 字段定义（F-XXX）。
- 检查移除后 ID 永不复用（补空会破坏审计历史）。

## 产物状态

| Status | Meaning | Downstream use |
|---|---|---|
| `draft` | 初始候选；Audit 未完成 | No |
| `needs_user_input` | 某校验边界或错误提示决策阻断确认 | No |
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

对 §系统校验 区块使用 `src/templates/stage-2-product/function-description.md` 中的所有标题（校验索引、分功能详述、校验覆盖检查、事实与决定、待确认问题）。若某检查无已确认内容，写 `待确认` 并关联问题或未知 ID；不要删除标题。

> 占位符 `待确认` 保留在中文 PRD 约定中。译者可在纯英文产物中使用 `[NEEDS CLARIFICATION]`，只要校验器识别两种形式。

## 规则行结构

| ID | 校验内容 | 校验规则 | 触发时机 | 错误提示 | 关联字段 (F) | 关联业务规则 (BR) | 来源 |
|---|---|---|---|---|---|---|---|
| VL-XXX | what is checked | executable value domain | when it fails | Chinese message (≤30 chars) | F-XXX | BR-XXX | FACT/DECISION/... |

## 字段定义表 (Field Definition Table)

按需产出（P1 按需），并入老版「字段规则说明」（字段名称、类型、长度、校验规则、来源）；同域合并到本 Skill。当上游 product-ux 的字段定义需要补充实现级字段契约时，在 §系统校验 内产出 `字段定义表` 小节。字段级校验逻辑由 VL-XXX 承担，本表只登记字段契约，不重复撰写校验表达式。

| 字段 ID | 字段名 | 类型 | 长度/范围 | 必填 | 来源（上游 IX/FUN） | 关联校验 VL-XXX |
|---|---|---|---|---|---|---|
| F-XXX | field name | string/int/... | length or value domain | 是/否 | IX-XXX / FUN-XXX | VL-XXX |

- 每个 `F-XXX` 全局唯一、零填充，不得与 `BR-XXX` / `VL-XXX` 混淆。
- `来源（上游 IX/FUN）` 必须引用上游已确认的 interaction-rules（IX-XXX）或 function-description（FUN-XXX）。
- 每个 F-XXX 至少关联一个 VL-XXX；未定义校验的字段在 `校验覆盖检查` 中标 ⚠️。
- 表头缺「字段名/类型」或字段无来源引用时，`validate_artifact.py` 仅记 warning（不阻塞），由人工评审把关。

## 人工职责

- 产品负责人：确认检查边界与错误提示文案。
- 业务负责人：确认可追溯到业务事实的值域（手机号字符集、金额上限、码表）。
- 产品经理：检查覆盖、可判定性、提示的面向用户质量、下游可用性。
- 最终评审人：授权 §系统校验 基线。一人可兼任多个角色，但决策权必须明确。

## 下游交接

为下游子 skill 输出一份紧凑交接：

```text
confirmed_checks           # VL-XXX 列表
field_coverage_map         # 每个用户输入字段 → 其 VL；缺口被标记
cross_field_dependencies   # 选 B 时 A 必填的关系（供 AC 与测试）
error_message_copy         # 每条 VL 的最终中文文案
accepted_assumptions
open_nonblocking_unknowns
source_ids
```

不要在本交接中创建业务规则（→ business-rules）、状态表（→ state-machine）、异常路径（→ exception-handling）或验收依据（→ acceptance-criteria）。

## 澄清会话契约

每个 Clarify Session 在父产物的 `## Clarifications` 章节记录为一行结构化数据。每个 Session 一行，按 session id 排序：

| Field | Meaning | Example |
|---|---|---|
| `session_id` | 单调递增 `CL-NNN`，零填充 | `CL-007` |
| `category` | 6 类 影响 × 不确定性 之一（scope / data-model / UX / non-functional / integration / compliance） | `data-model` |
| `question` | 本轮提出的唯一问题 | "Mobile number charset" |
| `ai_preliminary_judgment` | AI 的初步回答及依据 | "Inferred from BR-005: mainland CN, ^1[3-9]; needs confirmation" |
| `options` | 2–5 个互斥选项（或"自由短答"） | A) mainland CN B) CN+HK C) global E.164 |
| `decision_owner` | 回答的字段/格式负责人 | Product owner |
| `blocking` | yes / no | `yes` |
| `deferral_risk` | 若推迟会破坏什么 | "Format regex undecidable" |
| `accepted_answer` | 人工回复后选定的选项 | `A (mainland CN)` |
| `reflow_target` | 会被更新的产物章节 | `§系统校验 VL-003` |
| `integrated_at` | 答案写回时的 ISO 时间戳 | `2026-08-13T11:00:00Z` |
| `integrated_by` | AI 或人类执行者 | `AI` |
| `audit_recheck` | 集成后重新审计的结果（`pass` / `fail` / `n/a`） | `pass` |

规则:

- 每个 Session 一行。绝不把多轮 Q+A 合并进一行。
- `accepted_answer` 必须在产物到达 `ready_for_human_review` 前填写。
- `reflow_target` 必须引用已存在的章节标题。
- `audit_recheck` 必须是最后填写的字段；若为 `fail`，将状态切回 `needs_user_input` 并再开一个 Session。
- 运行顺序见 `SKILL.md` § Clarify。
