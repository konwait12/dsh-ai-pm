<!--
产物：功能描述 · 客户邀约活动（虚构演示样本）
feature-list 子 skill 输出章节：§功能清单（FEA-XXX）
本文件为 feature-list 校验器的正例 fixture，非真实需求产物。
章节内容即功能清单定稿，但产物状态为 ready_for_human_review——
子 skill 永远不能把状态写成 confirmed，只有 pipeline.py review --decision approve 可以。
-->
---
artifact_id: FD-CIA-001
version: v0.1
status: ready_for_human_review
owner: PM-Office
business_fact_owner: 市场部 王经理
goal_decision_owner: 市场部 王经理
reviewer: 产品负责人 李总
created_at: 2026-08-13
updated_at: 2026-08-13
confirmed_at:
upstream_artifact_id: JS-CIA-001
---

# 功能描述

## 0. 预检输入充分度判定

- 上游产物：JS-CIA-001（user-journey-and-stories, status: confirmed, v1.0）
- 已确认故事数：ST-001 ~ ST-006（P0 4 个 / P1 2 个）
- 判定：**充分模式**

## 1. 功能清单

| ID | 功能名称 | 所属故事 ST | 优先级 | 一句话描述 | 来源 |
|---|---|---|---|---|---|
| FEA-001 | 客户名单导入 | ST-001, ST-002 | P0 | 支持从 CRM/CSV/Excel 批量导入目标客户名单，去重与格式校验后入库；不含自动客群圈选 | ST-001 (FACT), ST-002 (DECISION) |
| FEA-002 | 邀约活动创建 | ST-001, ST-003 | P0 | 创建邀约活动并配置名称、时间窗与名额上限；不含模板库 | ST-003 (DECISION) |
| FEA-003 | 邀约发放与送达 | ST-002, ST-004 | P0 | 按名单批量发放邀约，追踪送达/失败状态并支持重发；不含催办 | ST-004 (DECISION) |
| FEA-004 | 客户接受/拒绝邀约 | ST-005 | P0 | 客户接受或拒绝邀约，系统记录决定并实时更新名额占用；不含改期 | ST-005 (FACT) |
| FEA-005 | 邀约效果看板 | ST-006 | P1 | 展示接受率、转化漏斗与未响应名单，供运营复盘；不含导出 | ST-006 (AI_INFERENCE) |
| FEA-006 | 二次催办提醒 | ST-006 | P1 | 对未响应客户自动发送二次提醒并可配置间隔；依赖 FEA-003 送达记录 | ST-006 (DECISION) |

## 2. 分功能详述

### FUN-001: 客户名单导入（示意，由 function-description 其他子 skill 细化）

- **来源功能**：FEA-001
- **来源故事**：ST-001, ST-002
- **业务规则 / 校验 / 状态 / 异常 / 验收**：由 business-rules / validation-rules / state-machine / exception-handling / acceptance-criteria 子 skill 产出
