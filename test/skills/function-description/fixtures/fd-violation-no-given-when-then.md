<!--
产物：故意违规样本（无 Given/When/Then 格式）
本文件通过 validate_artifact.py —— 结构合规但 D4.4 触发 error。
status: ready_for_human_review（模拟演示用）。
-->
---
artifact_id: FD-VIOL-001
version: v0.1
status: ready_for_human_review
owner: PM-Office
business_fact_owner: VP of Talent
goal_decision_owner: VP of Talent
reviewer: VP of Talent
created_at: 2026-08-11
updated_at: 2026-08-11
confirmed_at: 待确认
upstream_artifact_id: UX-HIRE-002
---

# 功能描述

## 0. 预检输入充分度判定

- 上游产物：UX-HIRE-002（status: confirmed，v1.0）
- 已确认 FEA 数：3（候选人列表、简历筛选、漏斗看板）
- 判定：**充分模式**（上游 confirmed）→ 走完整工作流

## 1. 功能清单

| ID | 功能名称 | 描述 | 所属故事 ST | 优先级 | 知识状态 |
|---|---|---|---|---|---|
| FEA-001 | 候选人列表 | 招聘专员后台查询候选人，支持筛选/分页/排序 | ST-101 | P0 | FACT |
| FEA-002 | 简历筛选打标 | 对候选人简历打标（待面试/已面试/不合适） | ST-102 | P0 | FACT |
| FEA-003 | 招聘漏斗看板 | 按周/月聚合投递→筛选→面试→录用漏斗 | ST-103 | P1 | AI_INFERENCE |

功能（FUN）拆分映射：FUN-001（FEA-001，P0）、FUN-002（FEA-002，P0）、FUN-003（FEA-003，P1）。

## 2. 功能流程

> 主流程描述，交互细节引用上游 product-ux（IX-XXX）。

### 2.1 主流程（P0）

- **FUN-001 候选人列表查询**：入口招聘专员后台 "候选人" 导航 → 系统读取候选人列表 → 招聘专员筛选/分页/排序（交互参考 IX-001：调整筛选条件后列表刷新并保留当前条件）
- **FUN-002 简历筛选打标**：入口候选人详情 "打标" 按钮 → 招聘专员选择标签（如"待面试/已面试/不合适"）→ 系统保存（交互参考 IX-002：提交标签后显示保存结果；失败时保留当前选择）
- **FUN-003 招聘漏斗看板**：入口导航 "数据看板" → 系统按周/月聚合投递→筛选→面试→录用漏斗（交互参考 IX-003：切换周/月粒度后刷新看板并保持筛选范围）

### 2.2 分支流程

| 决策点 | 判定条件 | 去向 | 条件是否互斥/穷举 |
|---|---|---|---|
| 分页 | 越界分页 | 提示"无更多" | 是 |
| 打标 | 提交成功 / 网络中断 | 成功显示结果 / 本地缓存 | 是 |

## 3. 业务规则

- **BR-001**：列表按更新时间倒序（具体口径待确认）
- **BR-002**：每次打标写入审计日志
- **BR-003**：漏斗阶段定义按现有 CRM

## 4. 校验规则与字段定义

（本期不涉及新字段，跳过）

## 5. 状态变化

| STATE | 状态名称 | 触发事件 | 目标状态 | 条件 | 所属 FUN |
|---|---|---|---|---|---|
| STATE-001 | 列表加载 | 查询条件变化 | 列表刷新 | 无 | FUN-001 |
| STATE-002 | 打标中 | 选择标签并提交 | 已保存 | 网络可用 | FUN-002 |
| STATE-003 | 漏斗渲染 | 切换周/月粒度 | 看板刷新 | 数据存在 | FUN-003 |

## 6. 异常与失败处理

| ID | 场景 | 触发条件 | 系统行为 | 恢复方式 | 用户提示 | 所属 FUN |
|---|---|---|---|---|---|---|
| EX-001 | 分页越界 | 请求页码超出范围 | 显示"无更多" | 回退到上一页 | 无更多数据 | FUN-001 |
| EX-002 | 打标网络中断 | 提交时网络不可用 | 本地缓存待重试 | 网络恢复后自动重试 | 保存失败，稍后重试 | FUN-002 |
| EX-003 | 看板数据缺失 | 无投递/筛选数据 | 显示空态 | 等待数据接入 | 暂无数据 | FUN-003 |

## 7. 验收依据

（⚠️ 故意不采用 Given/When/Then 格式，触发 D4.4 error）

- **AC-001**：列表展示正常候选人，越界分页给出空提示。
- **AC-002**：点击候选人姓名进入详情页。
- **AC-003**：标签保存后页面立即反映新状态。
- **AC-004**：看板渲染按周/月两种粒度可切换。

## 8. 事实与决定

| ID | 类型 | 内容 | 来源/决策人 | 状态 |
|---|---|---|---|---|
| FCT-601 | FACT | 招聘漏斗阶段定义见 CRM 系统 | UX-HIRE-002 §3 | 确认 |

## 9. 假设、AI 推断、未知与冲突

| ID | 类型 | 内容 | 依据 | 影响 | 责任人 | 处理方式 |
|---|---|---|---|---|---|---|
| ASM-701 | ASSUMPTION | 列表分页大小 = 20/页 | 行业默认 | UX 体感 | PM-Office | 待确认 |

## 10. 待确认问题

| ID | 问题 | 结论 |
|---|---|---|
| Q-801 | AC 是否使用 Given/When/Then 格式？ | 故意未采用，触发 D4.4 error |
| Q-802 | 是否需要 NFR 章节引用 Volere 10-17？ | 故意缺失 |

## Clarifications

| session_id | category | question | ai_preliminary_judgment | options | decision_owner | blocking | deferral_risk | accepted_answer | reflow_target | integrated_at | integrated_by | audit_recheck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | 待补充 | — | 待填写 | AI | n/a |

## 11. 来源追溯

| 来源 ID | 材料/位置 | 关键内容 | 本文落位或排除理由 |
|---|---|---|---|
| UX-HIRE-002 | 上游 UX 产物 | 3 个 FEA 定义 | §1 / §2 / §3 |

## 12. 下游输入摘要

```text
confirmed_version: v0.1 (ready_for_human_review)
feature_count: 3 个 FEA（候选人列表/筛选打标/漏斗看板）
function_count: 3 个 FUN（FUN-001 / FUN-002 / FUN-003）
business_rule_count: 3 个 BR
acceptance_criteria_count: 4 个 AC（故意不含 Given/When/Then）
open_nonblocking_unknowns: Q-801/Q-802（已登记待业务方补全）
source_ids: UX-HIRE-002
```

## 13. Constitution Compliance

| 原则 | 状态 | 证据 / 备注 |
|---|---|---|
| ① 业务事实分离 | PASS | §8 FACT 带 SRC；§9 ASSUMPTION 显式登记 |
| ② AI 不替业务决定 | PASS | §10 两个 Q 全部阻断待业务方 |
| ③ 来源可追溯 | PASS | §11 上游唯一 |
| ④ 冲突显式保留 | PASS | 无冲突源 |

## 14. 版本变更摘要

| 版本 | 变更原因 | 主要变化 | 人工确认状态 |
|---|---|---|---|
| v0.1 | 故意违规（演示 D4.4 error） | 缺 AC Given/When/Then | 待评审 |

> ⚠️ **违规声明**：本 fixture 故意不满足 D4.4（AC Given/When/Then）。
> 期望 validator 返回：≥1 error（结构章节合规，但 "Semantic (D4.4): AC-XXX lacks Given/When/Then format" 命中）。
> 用途：作为 function-description validator 的回归对照，证明 validator 能命中 D4.4 而非被"缺标题"掩盖。
