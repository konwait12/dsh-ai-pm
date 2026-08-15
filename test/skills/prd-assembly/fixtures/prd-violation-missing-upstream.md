<!--
产物：故意违规样本（缺 UX/FD 两个上游，触发 D5.2）
本文件通过 validate_artifact.py —— 故意制造 error 触发 D5.2。
status: ready_for_human_review（演示用）。
-->
---
artifact_id: PRD-VIOL-001
version: v0.1
status: ready_for_human_review
owner: PM-Office
business_fact_owner: VP of Talent
goal_decision_owner: VP of Talent
reviewer: VP of Talent
created_at: 2026-08-11
updated_at: 2026-08-11
confirmed_at: 待确认
upstream_artifact_ids: ["BG-PDM-001", "JS-PDM-001"]
---

# PRD 汇总

> ⚠️ **违规声明**：本 fixture 故意在 frontmatter `upstream_artifact_ids` 只填 BG/JS，缺 UX/FD 两个上游，以触发 PRD DoD D5.2 强校验。
> 期望 validator 返回 error："PRD DoD D5.2 failed: missing upstream artifact IDs for ['FD', 'UX']"。

## 1. 项目背景与目标

（来自 BG-PDM-001 confirmed v1.0，摘要省略）

## 2. 业务角色、用户旅程与用户故事

（来自 JS-PDM-001 confirmed v1.0，摘要省略）

## 3. UX：页面设计与交互规则

（本应来自 UX-PDM-XXX，本 fixture 故意缺）

## 4. 分功能描述

（本应来自 FD-PDM-XXX，本 fixture 故意缺）

## 5. 按需章节

（本期无 NFR / 字段规则 / 埋点等按需扩展，跳过）

## 6. 事实与决定

| ID | 类型 | 内容 | 来源/决策人 | 状态 |
|---|---|---|---|---|
| — | — | 无上游确认产物可引用 | — | 待确认 |

## 7. 验收依据

（上游缺位，无验收基线）

## 需求追溯矩阵

| 目标 G | 故事 ST | 功能 FEA | 功能详述 FUN | 验收标准 AC | 业务规则 BR |
|---|---|---|---|---|---|
| G1 | ST-001 | ⏸ | ⏸ | ⏸ | ⏸ |
| G2 | ST-002 | ⏸ | ⏸ | ⏸ | ⏸ |

> 故意留 ⏸ 占位以同时命中 RTM P0 链断裂校验。

## 自审记录（Constitution Compliance）

| 原则 | 状态 | 证据 / 备注 |
|---|---|---|
| ① 业务事实分离 | PASS | §6 显式登记 |
| ② AI 不替业务决定 | PASS | 无新需求引入 |
| ③ 来源可追溯 | FAIL | D5.2 缺 UX-/FD- 上游 → validator error |
| ④ 冲突显式保留 | PASS | 无冲突源 |
