# 输出契约（Output Contract）

## 产物状态（Artifact States）

| 状态 | 含义 | 下游使用 |
|---|---|---|
| `draft` | 初始候选；Audit 未完成 | 否 |
| `needs_user_input` | 某个实质性事实或决策阻断确认 | 否 |
| `conditional_review` | 结构上可评审，含显式的非阻断未知项 | 否 |
| `ready_for_human_review` | 自审通过；等待授权评审 | 否 |
| `confirmed` | 被授权的人类已显式批准此版本 | 是 |
| `superseded` | 更新的已确认基线取代此版本 | 否 |

## 版本规则（Version Rules）

- 候选从 `v0.1` 开始。
- 每次人工要求修订，递增次要候选版本：`v0.2`、`v0.3`。
- 首次确认的基线使用 `v1.0`，除非宿主项目另有政策。
- 已确认基线的改动按影响递增补丁/次要版本。
- 在面向人的版本之间保留一份简明变更摘要。不要保留每次内部自审迭代。

## 知识状态标签（Knowledge-State Labels）

| 标签 | 定义 |
|---|---|
| `FACT` | 来源权威范围内的显式来源陈述 |
| `DECISION` | 被授权人类做出的显式决策 |
| `ASSUMPTION` | 为分析而接受的临时条件，但未经确认 |
| `AI_INFERENCE` | AI 推导的解读，有证据支撑但不是业务事实 |
| `UNKNOWN` | 缺失的信息 |
| `CONFLICT` | 不兼容的来源陈述需要解决 |

## 必需章节（Required Sections）

使用 `src/templates/stage-1-business/background-goal.md` 中的全部标题。如果某个章节没有已确认内容，写入 `待确认` 并链接到某个问题或未知 ID；不要删除标题。

> 占位符 `待确认` 在中文化 PRD 惯例中保留。翻译者在纯英文产物中可使用 `[NEEDS CLARIFICATION]`，前提是校验器能识别这两种形式。

## 人类职责（Human Responsibilities）

- 业务事实负责人：确认现状事实与业务背景。
- 目标决策负责人：确认预期结果、成功判断、时间与可接受风险。
- 产品经理：检查完整性、清晰度、来源覆盖与下游可用性。
- 最终评审人：授权基线供下游使用。一人可兼任多个角色，但决策权必须明确。

## 下游交接（Downstream Handoff）

输出一份紧凑的交接包，包含：

```text
confirmed_version
background_summary
goal_summary
confirmed_roles
known_lifecycle_clues
constraints_and_dependencies
accepted_assumptions
open_nonblocking_unknowns
source_ids
```

不要在本交接包中创建用户旅程或用户故事。

## 澄清 Session 契约（Clarifications Session Contract）

每个 Clarify Session 作为产物内 `## Clarifications` 章节的一行结构化记录（放在 §11 待确认问题之后、§14 Constitution Compliance 之前）。每个 Session 一行，按 session id 排序：

| 字段 | 含义 | 示例 |
|---|---|---|
| `session_id` | 单调递增的 `CL-NNN`，前导补零 | `CL-001` |
| `category` | 6 种影响 × 不确定性类别之一（scope / data-model / UX / non-functional / integration / compliance） | `scope` |
| `question` | 本轮提出的唯一问题（转述） | "邀请范围的 VVIP 阈值" |
| `ai_preliminary_judgment` | AI 的初步答案及证据 | "由 SRC-002 §3 推断：VVIP = 年消费 ≥ ¥500k；需要确认" |
| `options` | 2–5 个互斥选项（或"自由文本短答"） | A) ¥500k B) ¥300k C) ¥1M D) 其他 |
| `decision_owner` | 负责回答的事实负责人或决策负责人 | CRM 副总裁 |
| `blocking` | yes / no | `yes` |
| `deferral_risk` | 延期会造成什么破坏 | "邀请范围仍然无法判定" |
| `accepted_answer` | 人工回复后选择的选项 | `A (¥500k)` |
| `reflow_target` | 会被更新的产物章节 | `§8 初步边界与非目标` |
| `integrated_at` | 答案写回的 ISO 时间戳 | `2026-08-11T10:30:00Z` |
| `integrated_by` | AI 或人类执行者 | `AI` |
| `audit_recheck` | 集成后重新 Audit 的结果（`pass` / `fail` / `n/a`） | `pass` |

规则：

- 每个 Session 一行。绝不要把多轮问答合并成一行。
- 在产物到达 `ready_for_human_review` 之前，`accepted_answer` 必须已填写。
- `reflow_target` 必须引用一个已存在的章节标题。
- `audit_recheck` 必须是最后填写的字段；如果是 `fail`，把状态改回 `needs_user_input` 并运行另一个 Session。
- 运行时顺序见 `SKILL.md` § Clarify 自成一个循环（Clarify Is Its Own Loop）。
