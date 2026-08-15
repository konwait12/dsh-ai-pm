<!--
产物：产品 UX · REQ-002 设备预测性维护平台
v1.0 confirmed · 基于上游 JS-PDM-001 (confirmed v1.0)
本文件通过 validate_artifact.py 校验。

⚠️ Fixture 声明：本文件是 product-ux skill 的回归演示样本，非 REQ-002 真实需求产物。
上游引用 JS-PDM-001 在 `requirements/REQ-002-predictive-maintenance/001-business-requirements/02-user-journey-stories/journey-and-stories.md` 中真实落位；
本 fixture 仅用于校验 product-ux validator 的结构与语义红线，不代表 REQ-002 已跑通 `product-ux`。
功能清单（FEA-XXX）与功能流程归 function-description，本产物只引用不重定义。
真实 REQ-002 `product-ux` 需由 product-ux skill 在 `requirements/REQ-002-predictive-maintenance/002-product-requirements/01-product-ux/` 重新生成。
-->
---
artifact_id: UX-PDM-001
version: v1.0
status: confirmed
owner: PM-Office
business_fact_owner: 设备工程部总监 陈工
goal_decision_owner: 生产运营部 郑总
reviewer: 设备工程部 陈工 + IT 周工
created_at: 2026-08-11
updated_at: 2026-08-11
confirmed_at: 2026-08-11
upstream_artifact_id: JS-PDM-001
---

# 产品 UX

## 0. 预检输入充分度判定

- 上游产物：JS-PDM-001（status: confirmed, v1.0）
- 已确认故事卡片数：10（P0: 5, P1: 5）
- 已确认角色数：7
- 判定：**充分模式** → 走完整工作流

## 1. 范围引用（上游）

> 业务范围与功能清单已在 Stage 1 `user-journey-and-stories` 与 `function-description` §功能清单 锁定。本步骤只引用，不重新定义功能。

| 引用 | 内容 |
|---|---|
| 上游范围基线 | JS-PDM-001 §范围基线：苏州压铸厂 26 台压铸机试点（P0 5 个故事 / P1 5 个故事，角色 7 个）；排除项见 JS-PDM-001（常州/无锡推广、自研算法平台、SaaS 云端、模具系统集成、移动 App 均不在本期） |
| 上游功能清单 | function-description §功能清单 FEA-001~FEA-006（设备数据接入 / 实时监控看板 / 故障预警引擎 / 维护工单管理 / 备件分析看板 / 试点效果报告） |

## 2. 页面设计

> 长什么样 + 可用性：信息架构、页面结构、导航逻辑、页面骨架、状态描述。原型是 UX 的落地产物，作为沟通载体不替代文本。

### 2.1 页面与步骤描述

| 页面/步骤 | 所属功能 | 入口 | 前置条件 | 主要内容 | 操作 | 下一状态 |
|---|---|---|---|---|---|---|
| 实时监控看板 | FEA-002 | 主导航 | 数据已接入 | 26台设备卡片（温度/振动/压力/电流实时值）、异常设备红色高亮、历史趋势小图 | 点击设备→设备详情；筛选→按工厂/状态 | 设备详情页 |
| 设备详情页 | FEA-002 | 监控看板点击设备 | 该设备数据在线 | 实时参数曲线、历史趋势、预警记录列表、维护记录列表 | 查看预警详情；查看维护历史 | 预警详情 |
| 预警详情页 | FEA-003 | 设备详情/预警通知 | 预警已触发 | 异常参数对比（当前vs基线）、趋势图、AI建议操作、所需备件清单 | 一键生成工单；标记误报 | 工单创建 / 监控看板 |
| 工单管理列表 | FEA-004 | 主导航 | 有工单数据 | 工单列表（状态/优先级/技师/截止时间/设备）、超时标记 | 新建工单；查看详情；筛选 | 工单详情 |
| 工单执行页(手机端) | FEA-004 | 工单详情/扫码 | 工单已派发 | 设备信息、操作指引、备件清单、扫码录入区 | 扫码记录备件消耗；提交维修结果 | 工单关闭 |
| 管理仪表板 | FEA-002 | 主导航(厂长) | 已登录 | 实时OEE、停机趋势、设备健康度概览 | 切换时间范围；导出 | — |

状态色标约定：实时监控看板设备卡片按参数状态着色——正常（绿）/ 关注（黄）/ 异常（红），见 JS-PDM-001 生命周期线索。

### 2.2 HTML 原型（沟通载体，按需）

- 是否需要原型：是（多角色评审：技师手机端 / 主管端）
- 原型位置：99-review/support/prototype/（评审沟通载体）

## 3. 交互规则

> 用户操作后系统怎么反应：操作反馈、跳转逻辑、弹窗规则、表单交互。仅描述页面层交互，不包含业务规则（属于 function-description）。

| ID | 规则描述 | 触发条件 | 系统响应 | 适用页面/功能 | 来源 |
|---|---|---|---|---|---|
| IX-001 | 实时高亮与置顶 | 设备参数偏离基线 | 设备卡片变黄/变红并置顶 | 实时监控看板 / FEA-002 | JS-PDM-001 |
| IX-002 | 预警通知推送 | 预警引擎触发预警 | 站内通知推送给技师与主管 | 预警通知 / FEA-003 | JS-PDM-001 |
| IX-003 | 一键生成工单 | 主管在预警详情点击“生成工单” | 创建关联工单并跳转工单详情 | 预警详情页 / FEA-004 | CL-001 |
| IX-004 | 扫码记录备件消耗 | 技师在工单执行页扫码 | 记录备件消耗并更新清单 | 工单执行页 / FEA-004 | JS-PDM-001 |
| IX-005 | 工单超时告警 | 工单超过截止时间未处理 | 列表标记超时并置顶提醒 | 工单管理列表 / FEA-004 | JS-PDM-001 |
| IX-006 | 误报标记确认 | 主管/IT 点击“标记误报” | 弹出原因确认框，确认后更新状态 | 预警详情页 / FEA-003 | JS-PDM-001 |

## 4. 事实与决定

| ID | 类型 | 内容 | 来源/决策人 | 状态 |
|---|---|---|---|---|
| FCT-001 | FACT | 6 个功能模块覆盖 P0+P1 故事 | JS-PDM-001 §3 | 确认 |
| DEC-001 | DECISION | 手机端扫描采用浏览器 WebRTC API（不开发独立 App） | IT 周工 | 确认 |

## 5. 假设、AI 推断、未知与冲突

| ID | 类型 | 内容 | 依据 | 影响 | 责任人 | 处理方式 |
|---|---|---|---|---|---|---|
| AII-001 | AI_INFERENCE | 监控看板布局参考工业 SCADA 模式（设备卡片+趋势图） | 行业常见模式 | 低 | UX 设计师 | 人工确认后转为原型参考 |
| UNK-001 | UNKNOWN | 算法供应商提供的预警 UI 组件是否可嵌入我方平台 | — | 中——影响预警详情页设计 | IT 周工 | 供应商选型后确认 |

## 6. 待确认问题

| ID | 问题 | 结论 |
|---|---|---|
| Q-001 | 监控看板刷新频率（实时 vs 5秒间隔）？ | 评审确认：5 秒轮询 |
| Q-002 | 手机端操作是否需要离线支持？ | 评审确认：不做离线，弱网提示重试 |

## Clarifications

| session_id | category | question | ai_preliminary_judgment | options | decision_owner | blocking | deferral_risk | accepted_answer | reflow_target | integrated_at | integrated_by | audit_recheck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL-001 | ux_pattern | 监控看板采用设备卡片还是列表形式？ | 推断设备卡片（26台适合卡片+状态色标） | A. 设备卡片 B. 列表 C. 混合 | 设备主管 | no | 信息密度不足 | A（设备卡片+状态色标） | §2 页面与步骤描述 | 2026-08-11T18:00:00Z | AI | pass |

## 9. 来源追溯

| 来源 ID | 材料/位置 | 关键内容 | 本文落位或排除理由 |
|---|---|---|---|
| JS-PDM-001 | 上游 confirmed §10 | story_summary / confirmed_roles / lifecycle_clues | §0 / §1 / §2 / §3 |
| SRC-002 | 评审会纪要（IT 预算/本地化） | IT 周工确认传感器方案 | §1 范围引用 / DEC-001 |

## 10. 下游输入摘要

```text
confirmed_version: v1.0
page_summary: 6 个页面（监控看板/设备详情/预警详情/工单列表/手机端执行/管理仪表板）
interaction_rule_count: 6 个 IX（实时高亮/通知推送/一键工单/扫码记录/超时告警/误报标记）
open_nonblocking_unknowns: 算法供应商 UI 组件兼容性（UNK-001）
source_ids: JS-PDM-001, SRC-002
```

## 11. Constitution Compliance

| 原则 | 状态 | 证据 / 备注 |
|---|---|---|
| ① 业务事实分离 | PASS | §4 区分 FACT/DECISION；§5 区分 AI_INFERENCE/UNKNOWN |
| ② AI 不替业务决定 | PASS | CL-001 由设备主管裁决；Q-001/Q-002 已评审确认 |
| ③ 来源可追溯 | PASS | §9 可追溯到上游 JS-PDM-001 和原始 SRC |
| ④ 冲突显式保留并关闭 | PASS | 无冲突 |

## 12. 版本变更摘要

| 版本 | 变更原因 | 主要变化 | 人工确认状态 |
|---|---|---|---|
| v0.1 | 初始候选（基于 JS-PDM-001） | 6 页面 + 6 交互规则 + 状态色标约定 | 已升级 v1.0 |
| v1.0 | 人工评审确认 | CL-001 设备卡片模式确认；§10 下游交接填写 | **已确认** |
