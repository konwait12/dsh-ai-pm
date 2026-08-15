---
artifact_id: BG-EX-001
version: v0.1
status: ready_for_human_review
owner: PM-Office
business_fact_owner: VP of CRM
goal_decision_owner: VP of Marketing
reviewer: 待确认
created_at: 2026-08-11
updated_at: 2026-08-11
confirmed_at: 待确认
---

<!--
Example artifact 1: Sufficient-mode run (generic business scenario, desensitized).
This file passes validate_artifact.py — it is a COMPLETE artifact, not a guide.
See guides/guide-1-example-sufficient.md for the pedagogical walkthrough.
-->

# 项目背景与目标

## 1. 需求来源与触发

- SRC-001（会议纪要，2026-08-08）：产品周会上业务方提出，需要为 2026 春季电商大促活动搭建客户端下单与履约能力。
- SRC-002（业务方邮件，2026-08-09）：邮件标题"Re: 2026 春季电商大促活动 PRD 需求"，明确活动日期 2026-03-20，目标客户为 VVIP 与普通客户。
- SRC-003（客群分级 PPT，2026-08-10）：客户分级权益定义。

## 2. 项目与需求背景

- 业务环境：电商平台，春季大促活动是全年最大获客节点。
- 需求由来：2025 年大促活动使用 Excel + 人工下单，转化率低（NNN%）、履约错误率高（NNN%），业务方希望数字化。
- 为什么现在：2026 春季活动 2026-03-20 上线，立项到上线仅 NNN 天。

## 3. 当前现状与已有做法

- 下单：运营手动从 CRM 导出客户名单，群发邀请，无渠道追踪。
- 履约：线下手工履约，错误率 NNN%（CRM 2025 数据）。
- 仍然有效：现有 CRM 客户分级（VVIP / 普通）字段可用；运营与客户已建立信任。

## 4. 核心问题与证据

| 问题 | 影响 | 证据来源 |
|---|---|---|
| 下单无渠道追踪 | 转化率 NNN% 无法定位原因 | SRC-002 |
| 手工履约错误率高 | NNN% 错误率造成客诉 | CRM 2025 数据（SRC-001 引用） |
| VVIP 与普通客户体验无差异 | VVIP 复购率同比下降 NNNpp | SRC-003 |

## 5. 目标、未来期望与成功判断

- 业务结果：大促活动下单转化率从 NNN% 提升至 NNN%（12 个月窗口）。
- 交付结果：客户端下单 + 履约能力上线。
- 成功判断：转化率 ≥ NNN%、履约错误率 ≤ NNN%、VVIP 复购率回正。
- 非目标：不做积分体系（下一版本）；不做外部投放。

## 6. 用户角色与利益相关者

- 需求提出方：业务方（VP of Marketing）
- 主要用户：运营（客户端下单）、客户（小程序下单）
- 受影响角色：门店店长（履约审核）、运营（活动配置）、客服（履约异常处理）
- 决策 owner：VP of CRM（数据与阈值）、VP of Marketing（活动与预算）

## 7. 时间、约束与依赖

- 上线：2026-03-20（硬约束）
- 依赖：CRM 客户分级字段（已就绪）、企微渠道接入（需确认）、小程序认证（需 NNN 周）

## 8. 初步边界与非目标

- 包含：客户端下单、小程序履约、运营端客户列表。
- 不包含：积分体系、礼品发放、回访、外部投放。

## 9. 事实与决定

| ID | 类型 | 内容 | 来源/决策人 | 状态 |
|---|---|---|---|---|
| FCT-001 | FACT | 活动日期 2026-03-20 | SRC-002 | 确认 |
| FCT-002 | FACT | 2025 转化率 NNN% | SRC-002 | 确认 |
| FCT-003 | FACT | VVIP 定义 = 年消费 ≥ ¥NNN 万 | SRC-003 + CL-001 | 确认 |
| DEC-001 | DECISION | 积分机制不在本期 | VP of Marketing | 确认 |

## 10. 假设、AI 推断、未知与冲突

| ID | 类型 | 内容 | 依据 | 影响 | 责任人 | 处理方式 |
|---|---|---|---|---|---|---|
| AI-001 | AI_INFERENCE | 转化率低主因是下单无渠道追踪 | SRC-002 定性描述 | 方案设计方向 | VP of CRM | 待确认 |
| UNK-001 | UNKNOWN | 企微渠道接口成本与周期 | - | 排期 | 产研 | 待调研 |
| CNF-001 | CONFLICT | SRC-002 说 VVIP 邀约 NNN 人/NNN 店，SRC-003 说重点场次 NNN+ 人 | 两者密度不一致 | 邀约规模 | VP of CRM | 待裁决 |

## 11. 待确认问题

| ID | 问题 | AI 初步判断与依据 | 选项/影响 | 决策人 | 阻断 | 延后风险 | 回写位置 |
|---|---|---|---|---|---|---|---|
| Q-001 | VVIP 阈值 | 推断 = ¥NNN 万（SRC-003） | A ¥NNN 万 / B ¥NNN 万 / C ¥NNN 万 | VP of CRM | 是 | 邀约范围无法定 | §8 |
| Q-002 | 企微渠道是否本期接入 | 推断 = 是（SRC-002 提到企微发邀请） | A 是 / B 否 | 产研 | 否 | 排期延迟 | §7 |

## Clarifications

| session_id | category | question | ai_preliminary_judgment | options | decision_owner | blocking | deferral_risk | accepted_answer | reflow_target | integrated_at | integrated_by | audit_recheck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL-001 | scope | VVIP 邀约阈值 | 推断 ¥NNN 万（SRC-003 §3） | A) ¥NNN 万 B) ¥NNN 万 C) ¥NNN 万 D) 其他 | VP of CRM | yes | 邀约范围无法定夺 | A (¥NNN 万) | §8 初步边界与非目标 | 2026-08-11T10:30:00Z | AI | pass |
| CL-002 | integration | 企微渠道本期接入？ | 推断是（SRC-002 提到企微发邀请） | A) 是 B) 否 C) 延后一期 | 产研 | no | 排期延迟 NNN 周 | A (是) | §7 时间、约束与依赖 | 2026-08-11T10:35:00Z | AI | pass |

## 12. 来源追溯

| 来源 ID | 材料/位置 | 关键内容 | 本文落位或排除理由 |
|---|---|---|---|
| SRC-001 | 会议纪要 | 活动数字化诉求 | §1、§3、§4 |
| SRC-002 | 业务方邮件 | 活动日期 / 转化率 / 企微邀约 | §1、§2、§4、§8 |
| SRC-003 | 客群分级 PPT | VVIP 定义 / 复购率 | §1、§4、§5 |

## 13. 下游输入摘要

待 `confirmed` 后填写（当前 ready_for_human_review）。

## 14. Constitution Compliance

| 原则 | 状态 | 证据 / 备注 |
|---|---|---|
| ① 业务事实分离 | PASS | §9 六类标签齐全，FACT 均带 SRC |
| ② AI 不替业务决定 | PASS | Q-001/Q-002 均带 AI 初步判断 + 选项 + 责任人 |
| ③ 来源可追溯 | PASS | §12 三源全部登记 |
| ④ 冲突显式保留 | PASS | CNF-001 未静默选边，提交 VP of CRM 裁决 |

## 15. 版本变更摘要

| 版本 | 变更原因 | 主要变化 | 人工确认状态 |
|---|---|---|---|
| v0.1 | 初始候选 | 首次生成（示例产物） | 待确认 |
