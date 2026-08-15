# 问题清单（Issue Record · 跨阶段共享）

> ⚠️ 模板占位：本文件为空白模板，由 `issue-record` Skill 在 Generate 阶段填充。
> 任何阶段登记问题时，复制本表对应章节并新增行。

---
artifact_id: IR-REQ-XXX
version: v0.1
status: draft
owner: 产品经理（待业务方 review 时确认）
goal_decision_owner: 业务方负责人（待人工 review 时确认）
business_sponsor: 业务方（待人工 review 时确认）
reviewer: 业务方负责人 + 项目 PMO
created_at: （待填写）
updated_at: （待填写）
confirmed_at: （授权人工 review 后填写）
---

## 1. 项目元数据

- 项目 ID：REQ-XXX
- 项目名称：（待确认）
- 关联背景：background-goal.md §（待确认）
- 关联范围：范围基线.md §（待确认）
- 评审版本：v0.1

## 2. 总览（按类别与状态计数）

| 类别 | open | in_progress | blocked | accepted | resolved | escalated |
|---|---|---|---|---|---|---|
| Blocker（BLK） | （待确认） | — | — | — | — | — |
| Risk（RSK） | （待确认） | — | — | — | — | — |
| Decision（DEC） | （待确认） | — | — | — | — | — |
| Information（INF） | （待确认） | — | — | — | — | — |
| Clarification（CLS） | （待确认） | — | — | — | — | — |
| Out-of-band（OUT） | （待确认） | — | — | — | — | — |

## 3. Blocker（BLK）

| ID | 标题 | 描述 | 状态 | Owner | 知识状态 | 来源 | 目标关闭 | 备注 |
|---|---|---|---|---|---|---|---|---|
| ISS-001 | （待确认） | （待确认） | open | （待确认） | UNKNOWN | SRC-XXX | （待确认） | — |

## 4. Risk（RSK）

| ID | 标题 | 描述 | 状态 | Owner | 知识状态 | 来源 | 缓解措施 | 备注 |
|---|---|---|---|---|---|---|---|---|
| ISS-101 | （待确认） | （待确认） | open | （待确认） | ASSUMPTION | SRC-XXX | （待确认） | — |

## 5. Decision-in-waiting（DEC）

| ID | 标题 | 描述 | 状态 | Owner | 知识状态 | 来源 | 目标关闭 | 备注 |
|---|---|---|---|---|---|---|---|---|
| ISS-201 | （待确认） | （待确认） | open | （待确认） | UNKNOWN | SRC-XXX | （待确认） | — |

## 6. Information gap（INF）

| ID | 标题 | 描述 | 状态 | Owner | 知识状态 | 来源 | 备注 |
|---|---|---|---|---|---|---|---|
| ISS-301 | （待确认） | （待确认） | open | （待确认） | UNKNOWN | SRC-XXX | — |

## 7. Clarification（CLS）

| ID | 标题 | 描述 | 状态 | Owner | 知识状态 | 来源 | 备注 |
|---|---|---|---|---|---|---|---|
| ISS-401 | （待确认） | （待确认） | open | （待确认） | AI_INFERENCE | SRC-XXX | — |

## 8. Out-of-band（OUT）

| ID | 标题 | 描述 | 状态 | Owner | 知识状态 | 来源 | 路由至 | 备注 |
|---|---|---|---|---|---|---|---|---|
| ISS-501 | （待确认） | （待确认） | open | （待确认） | UNKNOWN | SRC-XXX | （待确认） | — |

## 9. Closed Issues

### 9.1 Accepted（决策者接受的风险 / 不再行动）

| ID | 标题 | 接受者 | 接受日期 | 接受条件 | 备注 |
|---|---|---|---|---|---|
| ISS-A01 | （待确认） | （待确认） | （待确认） | （待确认） | — |

### 9.2 Resolved（已解决）

| ID | 标题 | 解决方案 | 关闭日期 | 引用变更 | 备注 |
|---|---|---|---|---|---|
| ISS-R01 | （待确认） | （待确认） | （待确认） | artifact §（待确认） | — |

### 9.3 Escalated（已升级）

| ID | 标题 | 升级至 | 升级日期 | 新 Owner | 备注 |
|---|---|---|---|---|---|
| ISS-E01 | （待确认） | （待确认） | （待确认） | （待确认） | — |

## 10. 来源追溯

| SRC-ID | 来源 | 关键陈述 | 知识状态 |
|---|---|---|---|
| SRC-001 | （待确认） | （待确认） | FACT |

## 11. 待确认问题

- Q-001: （待确认）

## 12. Constitution Compliance

- 规则先行：✅ 已对齐
- 六态标注：✅ 已对齐
- 模板符合性：✅ 已对齐
- 反模式自检：✅ 已通过
- 跨阶段对齐：✅ 已对齐（待确认 / UNKNOWN / CONFLICT 均已收录或记录关闭理由）
- AI 主动询问：✅ 已对齐（所有登记都先经用户确认）

## 13. 阶段收口表（每个 work item 送审前必填 · 空阶段=审计证据）

> B3 强制语义：每个 work item 的产物在 `ready_for_human_review` 送审前，必须在本表落收口行（空阶段也落行，问题数=0 即审计证据）。

| 阶段 | Work Item | 问题数 | 收口日期 | 状态 |
|---|---|---|---|---|
| 001-business-requirements | project-background-goal | 0 | 待填写 | open |
| 001-business-requirements | user-journey-and-stories | 0 | 待填写 | open |
| 002-product-requirements | product-ux | 0 | 待填写 | open |
| 002-product-requirements | function-description | 0 | 待填写 | open |
| 003-prd-output | prd-assembly | 0 | 待填写 | open |

## 版本变更摘要

- v0.1: 初稿
