<!--
产物：低密度退化模式运行（"画一下首页"）
本文件通过 validate_artifact.py —— 完整（退化的）产物。
status: needs_user_input（不进入完整流程）。
-->
---
artifact_id: UX-LOW-001
version: v0.1
status: needs_user_input
owner: 待确认
business_fact_owner: 待确认
goal_decision_owner: 待确认
reviewer: 待确认
created_at: 2026-08-11
updated_at: 2026-08-11
confirmed_at: 待确认
upstream_artifact_id: 待确认
---

# 产品 UX

## 0. 预检输入充分度判定

- 输入原文：`画一下首页`
- 输入长度：5 字（< 50）
- 附件：无
- 上游产物：无
- 判定：**低密度退化模式**（`SKILL.md` §1.1）→ 不进入完整流程，仅输出充分度评估 + 批量澄清问题

## 1. 范围引用（上游）

**信息不足**。无项目背景、需求由来、当前做法、业务问题陈述（待 Q-001/Q-002 补充）。

| 引用 | 内容 |
|---|---|
| 上游范围基线 | 待 Q-002 补充后填写 |
| 上游功能清单 | 待 Q-003 补充后填写 |

## 2. 页面设计

**信息不足**。没有可拆解的页面/步骤。（待 Q-003/Q-004 补充"首页"场景）

### 2.1 页面与步骤描述

**信息不足**。无上游用户旅程可拆解。

### 2.2 HTML 原型（沟通载体，按需）

- 是否需要原型：待 Q-004 补充"首页"具体场景后判定

## 3. 交互规则

**信息不足**。没有页面交互可描述。（待 Q-004/Q-005 补充）

## 4. 事实与决定

| ID | 类型 | 内容 | 来源/决策人 | 状态 |
|---|---|---|---|---|
| — | — | 无上游 confirmed 产物 | — | 待确认 |

## 5. 假设、AI 推断、未知与冲突

| ID | 类型 | 内容 | 依据 | 影响 | 责任人 | 处理方式 |
|---|---|---|---|---|---|---|
| UNK-701 | UNKNOWN | "首页"指 Web 端还是移动端？ | 输入未指定 | 全部 UX 方向 | 待确认 | 待 Q-004 补充 |
| UNK-702 | UNKNOWN | "首页"指哪个产品的哪个场景？ | 输入未指定 | 入口/角色/边界 | 待确认 | 待 Q-005 补充 |

## 6. 待确认问题

| ID | 问题 | AI 初步判断与依据 | 选项/影响 | 决策人 | 阻断 | 延后风险 | 回写位置 |
|---|---|---|---|---|---|---|---|
| Q-001 | 请提供上游 `user-journey-and-stories` confirmed 产物（至少 ST-XXX） | product-ux 必须基于已确认旅程生成 UX | A 提供 BG/JS 产物 B 重启 `project-background-goal` C 跳过（不可行） | PM-Office | 是 | 全部 UX 工作无法启动 | §1 |
| Q-002 | "画一下首页"是哪个产品的首页？ | 输入无产品/项目标识 | A 提供项目名 B 重启 `project-background-goal` C 退回上游 | PM-Office | 是 | 范围与角色无法确认 | §0 / §1 |
| Q-003 | 当前在哪个工作事项 / 哪个步骤？ | 输入不携带上下文 | A 关联 REQ-NNN B 新建 REQ-DIR | PM-Office | 是 | orchestrator 无法路由 | §0 |
| Q-004 | "首页"具体指什么场景？（登录页/列表页/详情页？） | UX 必须有具体入口 | A 登录页 B 列表页 D 详情页 E 自由补充 | 业务方 | 是 | 流程入口与角色动作不明确 | §2 / §3 |
| Q-005 | 涉及哪些角色？ | UX 必须以角色为入口 | A 待补充 | 业务方 | 是 | 用户旅程无法对齐 | §1 / §2 |

## Clarifications

| session_id | category | question | ai_preliminary_judgment | options | decision_owner | blocking | deferral_risk | accepted_answer | reflow_target | integrated_at | integrated_by | audit_recheck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | 待确认 | §0 / §6 Q-001~Q-005 | 待填写 | AI | n/a |

> 状态说明：本产物在 5 个 Session 内未获得任一答案前，保持 `needs_user_input` 不进入完整流程；超过 5 个 Session 也保持当前状态，等人工补齐信息后由 orchestrator 重启。

## 9. 来源追溯

| 来源 ID | 材料/位置 | 关键内容 | 本文落位或排除理由 |
|---|---|---|---|
| SRC-001 | 用户单句自然语言 | "画一下首页" | §0 输入原文 |

## 10. 下游输入摘要

```text
confirmed_version: 不适用（needs_user_input 状态）
page_summary: 待 Q-003/Q-004 补充后填写
interaction_rule_count: 待 Q-004/Q-005 补充后填写
open_nonblocking_unknowns: 5 个 Q 全部为 blocking
source_ids: SRC-001
```

## 11. Constitution Compliance

| 原则 | 状态 | 证据 / 备注 |
|---|---|---|
| ① 业务事实分离 | PASS | §9 仅 SRC-001；§5 UNK-701/702 显式登记未知项 |
| ② AI 不替业务决定 | PASS | §6 五个 Q 全部 blocking，未自设任何边界/范围 |
| ③ 来源可追溯 | PASS | §9 仅一条 SRC；§0 完整记录输入原文 |
| ④ 冲突显式保留 | PASS | 本产物无冲突源（输入仅 1 句） |

## 12. 版本变更摘要

| 版本 | 变更原因 | 主要变化 | 人工确认状态 |
|---|---|---|---|
| v0.1 | 低密度退化（5 字 + 无附件） | 完整章节框架；§5/§6 显式登记 5 个 blocking Q；status=needs_user_input | 待人工补齐 |
