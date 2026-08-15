<!--
产物：用户旅程与用户故事 · 边界测试：多角色+多路径类型
测试 validator 对 full-coverage 场景（含 exception/failure/handoff/recovery）的处理
-->
---
artifact_id: JS-TEST-EDGE
version: v0.1
status: ready_for_human_review
owner: PM-Office
business_fact_owner: Test Owner
goal_decision_owner: Test Owner
reviewer: Test Reviewer
created_at: 2026-08-12
updated_at: 2026-08-12
confirmed_at: 待确认
upstream_artifact_id: BG-TEST-001
---

# 用户旅程与用户故事

## 0. 预检输入充分度判定

- 上游产物：BG-TEST-001 (confirmed v1.0)
- 已确认角色数：3（管理员、操作员、审计员）
- 判定：**充分模式**

## 1. 业务生命周期分解

| 阶段 | 描述 | 触发事件 | 涉及角色 | 来源 |
|---|---|---|---|---|
| 1. 创建 | 管理员创建任务 | 业务需求 | 管理员 | BG §2 |
| 2. 执行 | 操作员执行任务 | 任务创建完成 | 操作员 | BG §2 |
| 3. 审核 | 审计员审核结果 | 任务执行完成 | 审计员 | BG §2 |
| 4. 归档 | 系统自动归档 | 审核完成 | 系统 | BG §2 |

## 2. 用户旅程图

| 阶段 | 管理员 | 操作员 | 审计员 |
|---|---|---|---|
| 1.创建 | 触发：业务需求<br>动作：创建任务<br>触点：管理后台<br>类型：normal<br>来源：BG §2 | — | — |
| 2.执行 | — | 触发：任务分配<br>动作：执行任务<br>触点：工作台<br>类型：normal<br>来源：BG §2 | — |
| 3.审核 | — | — | 触发：任务完成<br>动作：审核结果<br>触点：审核面板<br>类型：normal<br>来源：BG §2 |

## 3. 用户故事卡片

| ID | 来源 | 角色 | 故事 | 路径类型 | 优先级 | 知识状态 |
|---|---|---|---|---|---|---|
| ST-001 (G1) | 1.创建×管理员 | 管理员 | 创建任务 | normal | P0 | FACT |
| ST-002 (G2) | 2.执行×操作员 | 操作员 | 执行任务 | normal | P0 | FACT |
| ST-003 (G2) | 2.执行×操作员 | 操作员 | 执行遇到网络异常时重试 | exception | P1 | AI_INFERENCE |
| ST-004 (G3) | 3.审核×审计员 | 审计员 | 审核结果 | normal | P0 | FACT |
| ST-005 (G2) | 2.执行×操作员 | 操作员 | 执行失败后恢复 | recovery | P1 | AI_INFERENCE |

## 4. 旅程→故事覆盖矩阵

| 旅程条目 | 故事 ID | 状态 |
|---|---|---|
| 1.创建×管理员 | ST-001 (G1) | ✅ |
| 2.执行×操作员 | ST-002 (G2), ST-003 (G2), ST-005 (G2) | ✅ |
| 3.审核×审计员 | ST-004 (G3) | ✅ |

## 5. 路径类型覆盖检查

| 类型 | 覆盖 | 证据 |
|---|---|---|
| normal | ✅ | ST-001,002,004 |
| exception | ✅ | ST-003 |
| failure | 未覆盖 | — |
| handoff | 未覆盖 | — |
| recovery | ✅ | ST-005 |

## 10. 项目范围基线

| 类别 | 内容 |
|---|---|
| 本期包含 | 创建+执行+审核 |
| 假设与依赖 | 系统稳定 |

## 6. 事实与决定

| ID | 类型 | 内容 | 来源 |
|---|---|---|---|
| FCT-001 | FACT | 三角色流程包含创建→执行→审核→归档 4 阶段 | BG §2 |

## 7. 假设、AI 推断、未知与冲突

| ID | 类型 | 内容 | 处理 |
|---|---|---|---|
| AII-001 | AI_INFERENCE | 网络异常+恢复路径基于常见场景推断 | 待人工确认 |

## 8. 待确认问题

| ID | 问题 | 结论 |
|---|---|---|
| Q-001 | 是否需要 handoff 路径？ | 待确认 |

## Clarifications

无

## 11. 来源追溯

| 来源 | 关键内容 | 本文落位 |
|---|---|---|
| BG-TEST-001 | 3角色，4阶段 | §1-§3 |

## 12. 下游输入摘要

```text
confirmed_version: v0.1
journey_summary: 4阶段×3角色×5 stories
```

## 13. Constitution Compliance

| 原则 | 状态 |
|---|---|
| ① 业务事实分离 | PASS |

## 14. 版本变更摘要

| 版本 | 变更 | 状态 |
|---|---|---|
| v0.1 | 初始 | 待确认 |
