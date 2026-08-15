# 输出契约 · 竞品调研

## 产物状态（Artifact States）

| 状态 | 含义 | 下游使用 |
|---|---|---|
| `draft` | 初始候选；Audit 未完成 | 否 |
| `needs_user_input` | 重大事实或决策阻断确认 | 否 |
| `conditional_review` | 结构上可审，带显式非阻断未知项 | 否 |
| `ready_for_human_review` | 自审通过；等待授权评审 | 否 |
| `confirmed` | 被授权人显式批准本版本的适用性 | 是 |
| `superseded` | 更新的已确认分析取代本版本 | 否 |

## 版本规则（Version Rules）

- 候选从 `v0.1` 开始。
- 每次人工要求修订，递增候选版本 minor：`v0.2`、`v0.3`。
- 首次已确认的分析使用 `v1.0`，除非宿主项目定义了其他策略。
- 已确认变更按影响递增 patch/minor 版本。
- 在人可见的版本之间保留简洁的变更摘要。不要保留每次内部自审迭代。

## 知识状态标签（Knowledge-State Labels）

| 标签 | 定义 |
|---|---|
| `FACT` | 在其权威范围内显式的官方来源陈述（官网、已发布规范、经核实的文档） |
| `DECISION` | 被授权人作出的显式决策 |
| `ASSUMPTION` | 为分析接受的暂定条件，但未确认 |
| `AI_INFERENCE` | AI 基于证据（截图、评论、对比）推导出的解读，但不是已确认的业务事实 |
| `UNKNOWN` | 缺失或无法获取的公开信息 |
| `CONFLICT` | 不相容的来源陈述（如厂商声明 vs 用户评论）需要解决 |

**本 skill 的默认标签是 `AI_INFERENCE`。** 竞品发现只有在业务负责人确认其适用于我们的语境后，才能用于产品决策。

## 必需章节（Required Sections）

使用 `src/templates/support/competitive-analysis.md` 模板中的所有标题：

- `## 竞品列表` — 每个选中的竞品及其选择理由（直接/间接/参照）
- `## 逐品分析` — 使用所选框架对每个竞品深度分析，带 SRC-ID
- `## 横向对比` — 跨竞品模式、分歧和市场标准信号
- `## 结论` — 必须的"So What"：我们应该做什么、差异化做什么、忽略什么、还不知道什么

如果某个章节没有已确认的内容，写 `待确认` 并链接到问题或未知 ID；不要删除标题。

## 人类职责（Human Responsibilities）

- 调研负责人（PM）：定义调研目标和对比维度。
- 业务负责人：确认竞品选择、洞见适用性和建议的行动。
- 最终评审人：授权分析供下游使用。一人可兼任多个角色，但决策权必须显式。

## 下游移交（Downstream Handoff）

输出一个精简的移交信息，包含：

```text
confirmed_version
research_goal (business-level / functional-level)
competitor_scope (SRC-IDs, direct/indirect/aspirational)
market_standard_patterns
differentiation_gaps
so_what_recommendations (mapped to goal IDs)
open_unknowns
```

不要在本移交中创建用户旅程、UX 规则或功能描述。

## 澄清会话契约（Clarifications Session Contract）

每次 Clarify 会话都作为结构化行记录在产物内部的 `## Clarifications` 章节中（位于 `## 结论` 之后、版本变更摘要之前）。每次会话一行，按 session id 排序：

| 字段 | 含义 | 示例 |
|---|---|---|
| `session_id` | 单调递增的 `CL-NNN`，零填充 | `CL-001` |
| `category` | 6 类 Impact × Uncertainty 之一（scope / data-model / UX / non-functional / integration / compliance） | `scope` |
| `question` | 本轮问的单一问题，转述 | "会员等级分几档：直接抄 A 的 3 档还是自研 5 档?" |
| `ai_preliminary_judgment` | AI 的初步答案与证据 | "Inferred from SRC-002 §3: 3 档覆盖主流竞品; need confirmation" |
| `options` | 2-5 个互斥选项（或"自由简短回答"） | A) 3 档 B) 5 档 C) other |
| `decision_owner` | 回答的业务负责人 | VP of CRM |
| `blocking` | yes / no | `yes` |
| `deferral_risk` | 如果延期会破坏什么 | "横向对比维度无法定档" |
| `accepted_answer` | 人工回复后选定的选项 | `A (3 档)` |
| `reflow_target` | 会被更新的产物章节 | `## 横向对比` |
| `integrated_at` | 答案写回时的 ISO 时间戳 | `2026-08-11T10:30:00Z` |
| `integrated_by` | AI 或人工执行者 | `AI` |
| `audit_recheck` | 整合后重新 Audit 的结果（`pass` / `fail` / `n/a`） | `pass` |

规则：

- 每次会话一行。绝不把多轮问答合并成一行。
- `accepted_answer` 必须在产物达到 `ready_for_human_review` 前填好。
- `reflow_target` 必须引用一个已存在的章节标题。
- `audit_recheck` 必须最后填写；若为 `fail`，把状态改回 `needs_user_input` 并再跑一次会话。
