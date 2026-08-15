<!--
产物模板：产品 UX（纯 UX：页面设计 + 交互规则）
product-ux SKILL.md 驱动 · 待确认 是唯一占位符。
功能清单与功能流程归 function-description，不在此处。
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
upstream_artifact_id: ""
---

# 产品 UX

## 0. 预检输入充分度判定

- 上游产物：`待确认`
- 已确认故事卡片数：`待确认`
- 已确认角色数：`待确认`
- 判定：`待确认`

## 1. 范围引用（上游）

> 业务范围与功能清单已在 Stage 1 `user-journey-and-stories` 与 `function-description` §功能清单 锁定。本步骤只引用，不重新定义功能。

| 引用 | 内容 |
|---|---|
| 上游范围基线 | `待确认`（引用 JS-XXX §范围基线） |
| 上游功能清单 | `待确认`（引用 function-description FEA-XXX） |

## 2. 页面设计（page-design 子 skill 产出）

> 长什么样 + 可用性：信息架构、页面结构、导航逻辑、页面骨架、状态描述。原型是 UX 的落地产物，作为沟通载体不替代文本。

### 2.1 页面与步骤描述

| 页面/步骤 | 所属功能 | 入口 | 前置条件 | 主要内容 | 操作 | 下一状态 |
|---|---|---|---|---|---|---|
| `待确认` | `待确认` | `待确认` | `待确认` | `待确认` | `待确认` | `待确认` |

### 2.2 HTML 原型（沟通载体，按需）

- [ ] 是否需要原型：`待确认`（多方案沟通 / 多角色评审时生成）
- 原型位置：`待确认`（保存到 99-review/support/prototype/）

## 3. 交互规则（interaction-rules 子 skill 产出）

> 用户操作后系统怎么反应：操作反馈、跳转逻辑、弹窗规则、表单交互。仅描述页面层交互，不包含业务规则（属于 function-description）。

| ID | 规则描述 | 触发条件 | 系统响应 | 适用页面/功能 | 来源 |
|---|---|---|---|---|---|
| IX-001 | `待确认` | `待确认` | `待确认` | `待确认` | `待确认` |

## 4. 事实与决定

| ID | 类型 | 内容 | 来源/决策人 | 状态 |
|---|---|---|---|---|
| 待确认 | 待确认 | 待确认 | 待确认 | 待确认 |

## 5. 假设、AI 推断、未知与冲突

| ID | 类型 | 内容 | 依据 | 影响 | 责任人 | 处理方式 |
|---|---|---|---|---|---|---|
| 待确认 | 待确认 | 待确认 | 待确认 | 待确认 | 待确认 | 待确认 |

## 6. 待确认问题

| ID | 问题 | 结论 |
|---|---|---|
| 待确认 | 待确认 | 待确认 |

## Clarifications

| session_id | category | question | ai_preliminary_judgment | options | decision_owner | blocking | deferral_risk | accepted_answer | reflow_target | integrated_at | integrated_by | audit_recheck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |

## 7. 下游传导摘要

承接上游 `journey-and-stories.md` 的 §下游输入摘要与 §项目范围基线，向下传递给 `function-description` 的关键交接：

- 确认的 `ST-XXX` 列表（已通过 MoSCoW 排序）
- 确认的 `FEA-XXX` 草案（来自 §2 页面设计倒推）
- 全部 `IX-XXX` 列表（来自 §3 交互规则）
- 已锁定的页面/状态枚举（来自 §2）
- 范围基线 In/Out/Deferred/Conditional（无变更入口——发现越界需回流 user-journey-and-stories）

## 8. FUN 移交清单（给 function-description 的衔接）

每个已确认的 `IX-XXX` 至少映射到 1 个 `FEA-XXX`；每个 `FEA-XXX` 至少映射到 1 个 `ST-XXX`。

| FEA | IX 触发器 | 涉及 ST | 优先级 |
|---|---|---|---|
| FEA-XXX | IX-XXX / 页面状态 | ST-XXX | P0/P1/P2 |

## 9. 来源追溯

| 来源 ID | 材料/位置 | 关键内容 | 本文落位或排除理由 |
|---|---|---|---|
| 待确认 | 待确认 | 待确认 | 待确认 |

## 10. 下游输入摘要

```text
confirmed_version: 待确认
page_summary: 待确认
interaction_rule_count: 待确认
open_nonblocking_unknowns: 待确认
source_ids: 待确认
```

## 11. Constitution Compliance

| 原则 | 状态 | 证据 / 备注 |
|---|---|---|
| ① 业务事实分离 | 待确认 | |
| ② AI 不替业务决定 | 待确认 | |
| ③ 来源可追溯 | 待确认 | |
| ④ 冲突显式保留并关闭 | 待确认 | |

## 12. 版本变更摘要

| 版本 | 变更原因 | 主要变化 | 人工确认状态 |
|---|---|---|---|
| v0.1 | 初始候选 | 待确认 | 待确认 |
