<!--
产物模板：PRD 汇总
prd-assembly SKILL.md 驱动 · 只聚合不新增 · 待确认 是唯一占位符。

按需子章节（§5 按需章节下，校验器不要求；材料不含对应内容时标注"本期不适用"）：
  - 5.5 名词解释 / 术语表 — 术语 / 缩略词 → 说明
  - 5.6 涉及团队及职责   — 团队 / 系统 → 职责
-->
---
artifact_id: ""
version: "v0.1"
status: "draft"
owner: ""
business_fact_owner: ""
goal_decision_owner: ""
reviewer: ""
created_at: ""
updated_at: ""
confirmed_at: ""
upstream_artifact_ids: []
---

<!--
🤖 AGENT INSTRUCTION BLOCK (for downstream AI consumers of this PRD):

This PRD is a living source of truth — not a static document. When consuming this file:

1. DO NOT GUESS. If any requirement, rule, or constraint is ambiguous, STOP and ask the human product owner before proceeding.
2. Knowledge states are tagged inline:
   - FACT = verified business truth (do not reinterpret)
   - DECISION = confirmed human decision (binding)
   - ASSUMPTION = unverified premise (may change)
   - AI_INFERENCE = AI-generated, NOT human-confirmed (treat as suggestion)
   - UNKNOWN = explicitly marked gap (ask before acting)
   - CONFLICT = known contradiction (resolve before implementing)
3. The traceability matrix (§需求追溯矩阵) is authoritative — every acceptance criterion traces to a story, which traces to a goal. Do not implement anything without traceability.
4. If you need to change this PRD, create a change proposal (see src/shared/change-management/proposal-template.md) — do not edit confirmed content directly.
5. Version history is in the frontmatter (version / updated_at) and CHANGELOG.md. Always check you're reading the latest version.
-->

# PRD（产品需求文档）

> 上游：本 PRD 基于 REQ-XXX 的 4 个已确认上游产物（版本与评审记录见 99-review/ 与 frontmatter `upstream_artifact_ids`）。

## 1. 项目背景与目标

（从 `project-background-goal` 已确认产物完整引用）

`待确认`

## 2. 业务角色、用户旅程与用户故事

（从 `user-journey-and-stories` 已确认产物完整引用）

`待确认`

## 3. UX：页面设计与交互规则

（从 `product-ux` 已确认产物完整引用）

`待确认`

## 4. 分功能描述

（从 `function-description` 已确认产物完整引用）

`待确认`

## 5. 按需章节

### 5.1 字段规则

（从 `function-description` 的字段定义表引用，如无内容标注"本期不适用"）

### 5.2 埋点需求分析

（从 `tracking-plan` 分支产物引用，如无内容标注"本期不适用"）

### 5.3 依赖与约束

（汇总各工作事项 中的依赖与约束）

### 5.4 未决问题与风险

（汇总各工作事项 中的 UNKNOWN 项和开放风险，引用 issue-record）

### 5.5 名词解释 / 术语表

（从各上游已确认产物中汇总术语 / 缩略词定义，逐条摘录不自造；如无术语可标注"本期不适用"）

| 术语 / 缩略词 | 说明 |
|---|---|
| 待补充 | 待补充 |

### 5.6 涉及团队及职责

（汇总各上游产物中涉及的团队 / 系统职责，只写上游已提及的团队、不推断；如无明确职责划分可标注"本期不适用"）

| 团队 / 系统 | 职责 |
|---|---|
| 待补充 | 待补充 |

## 6. 事实与决定

（汇总各工作事项 的关键事实与人类决定）

`待确认`

## 7. 验收依据

（汇总各工作事项 的验收标准，作为研发/测试的验收基线）

`待确认`

## 需求追溯矩阵

| 目标 (G) | 故事 (ST) | 功能 (FEA) | 功能详述 (FUN) | 验收标准 (AC) | 业务规则 (BR) |
|---|---|---|---|---|---|
| `待确认` | `待确认` | `待确认` | `待确认` | `待确认` | `待确认` |

## 自审记录（Constitution Compliance）

> 评审用附录：AI 的自审证明，非 PRD 正文。正向/反向追溯检查与不一致报告由机器在 gate 时产出、进 99-review 评审记录，不写进 PRD。

| 原则 | 状态 | 证据 / 备注 |
|---|---|---|
| ① 业务事实分离 | 待确认 | |
| ② AI 不替业务决定 | 待确认 | |
| ③ 来源可追溯 | 待确认 | |
| ④ 冲突显式保留并关闭 | 待确认 | |
