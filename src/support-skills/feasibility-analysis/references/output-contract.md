# 输出契约 · 可行性分析

## 产物状态（Artifact States）

| 状态 | 含义 | 下游使用 |
|---|---|---|
| `draft` | 初始候选；Audit 未完成 | 否 |
| `needs_user_input` | 重大事实或决策阻断确认 | 否 |
| `conditional_review` | 结构上可审，带显式非阻断未知项 | 否 |
| `ready_for_human_review` | 自审通过；等待授权评审 | 否 |
| `confirmed` | 被授权人显式批准本版本 | 是 |
| `superseded` | 更新的已确认评估取代本版本 | 否 |

## 版本规则（Version Rules）

- 候选从 `v0.1` 开始。
- 每次人工要求修订，递增候选版本 minor：`v0.2`、`v0.3`。
- 首次已确认的评估使用 `v1.0`，除非宿主项目定义了其他策略。
- 已确认变更按影响递增 patch/minor 版本。
- 在人可见的版本之间保留简洁的变更摘要。不要保留每次内部自审迭代。

## 知识状态标签（Knowledge-State Labels）

| 标签 | 定义 |
|---|---|
| `FACT` | 来源权威范围内显式的来源陈述（如厂商报价、已发布价格） |
| `DECISION` | 被授权人作出的显式决策 |
| `ASSUMPTION` | 为分析接受的暂定条件，但未确认（如估算的人力） |
| `AI_INFERENCE` | AI 基于证据推导出的估算或解读，但不是已确认的业务事实 |
| `UNKNOWN` | 缺失的信息 |
| `CONFLICT` | 不相容的来源陈述需要解决 |

**成本/风险数字很少是 FACT。** 估算必须标为 `AI_INFERENCE` 或 `ASSUMPTION` 并指定 owner，直到决策 owner 确认它们。

## 必需章节（Required Sections）

### 主线四维度（feasibility-report.md）

使用 `src/templates/support/feasibility-report.md` 中的所有标题：

- `## 市场空间` — 目标用户、渗透率、理论空间
- `## 技术可行性` — 每个挑战 → 已验证 / 待验证 / 不可行
- `## 投入产出` — 研发成本、运维成本、预期收益、回本周期
- `## 风险评估` — 每个风险 → 影响 + 概率 + 应对
- `## 结论` — 做 / 不做 / 有条件做，条件具体可衡量，含 AI 推荐

### §多方案取舍 章节（≥2 实质方案时，嵌入同一份报告）

使用 `src/templates/support/solution-comparison.md` 的标题作为 `feasibility-report.md` 内部的章节结构：

- `## 候选方案` — 每个方案等深（描述、成本、范围、时间线、风险、优缺点）
- `## 方案对比矩阵` — 加权标准（打分**之前**定义）× 得分 = 排序结果
- `## AI 推荐` — 推荐选项，带置信度（HIGH/MEDIUM/LOW）、接受的 trade-off，以及会改变推荐的条件
- `## 人工决策` — 人类的选择记录为 DEC-XXX，含理由、决策人和日期

§多方案取舍 章节嵌入在单一可行性报告中——绝不作为独立产物产出。

如果某个章节没有已确认的内容，写 `待确认` 并链接到问题或未知 ID；不要删除标题。

## 人类职责（Human Responsibilities）

- 决策 owner：做出最终选择（或 Go/No-Go）并确认重大数字。
- PM：定义标准、检查等深描述、保证推荐的清晰度。
- 最终评审人：授权评估供下游使用。一人可兼任多个角色，但决策权必须显式。

## 下游移交（Downstream Handoff）

输出一个精简的移交信息，包含：

```text
confirmed_version
mode (feasibility | feasibility_with_tradeoffs)
recommendation (with confidence)
human_decision (DEC-XXX)
key_assumptions_that_flip_it
scope_impact (which Work Items to reflow if any)
source_ids
```

不要在本移交中创建新的需求或设计。

## 澄清会话契约（Clarifications Session Contract）

每次 Clarify 会话都作为结构化行记录在产物内部的 `## Clarifications` 章节中（位于最后一个内容章节之后、版本变更摘要之前）。每次会话一行，按 session id 排序：

| 字段 | 含义 | 示例 |
|---|---|---|
| `session_id` | 单调递增的 `CL-NNN`，零填充 | `CL-001` |
| `category` | 6 类 Impact × Uncertainty 之一（scope / data-model / UX / non-functional / integration / compliance） | `scope` |
| `question` | 本轮问的单一问题，转述 | "通知模块自研 vs 外采的预算上限是多少?" |
| `ai_preliminary_judgment` | AI 的初步答案与证据 | "Inferred from SRC-002: 自研 2 人×4 周 ≈ ¥X; need confirmation" |
| `options` | 2-5 个互斥选项（或"自由简短回答"） | A) ≤¥10万 B) ≤¥30万 C) other |
| `decision_owner` | 回答的决策 owner | VP of Engineering |
| `blocking` | yes / no | `yes` |
| `deferral_risk` | 如果延期会破坏什么 | "成本维度无法打分，矩阵无法收敛" |
| `accepted_answer` | 人工回复后选定的选项 | `A (≤¥10万)` |
| `reflow_target` | 会被更新的产物章节 | `## 方案对比矩阵` |
| `integrated_at` | 答案写回时的 ISO 时间戳 | `2026-08-11T10:30:00Z` |
| `integrated_by` | AI 或人工执行者 | `AI` |
| `audit_recheck` | 整合后重新 Audit 的结果（`pass` / `fail` / `n/a`） | `pass` |

规则：

- 每次会话一行。绝不把多轮问答合并成一行。
- `accepted_answer` 必须在产物达到 `ready_for_human_review` 前填好。
- `reflow_target` 必须引用一个已存在的章节标题。
- `audit_recheck` 必须最后填写；若为 `fail`，把状态改回 `needs_user_input` 并再跑一次会话。
