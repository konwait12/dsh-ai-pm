# 需求重举（Requirement Restate）

> ⚠️ 模板占位：本文件为空白模板，由 `requirement-restate` Skill 在 Generate 阶段填充。
> 这是**分析过程**，不是 PRD 产物；其结论进入 Issue Record。

---
artifact_id: RR-REQ-XXX
version: v0.1
status: draft
owner: 产品经理（待 stakeholder 确认时填入）
stakeholder: （待确认：原始需求提出方）
stakeholder_delegate: （待确认：stakeholder 指定的代理）
reviewer: 原始 stakeholder + 产品经理
created_at: （待填写）
updated_at: （待填写）
confirmed_at: （授权 stakeholder 确认后填写）
---

## 1. 项目元数据

- 项目 ID：REQ-XXX
- 项目名称：（待确认）
- 关联上游：（待确认：源材料 / 邮件 / 会议记录 / 已有 BRD）
- 关联下游：issue-record.md §3-§8（CONFIRMED 后登记）
- 评审版本：v0.1

## 2. 来源清单（SRC-IDs）

| SRC-ID | 类型 | 提供者 | 时间 | 位置 | 适用阶段 |
|---|---|---|---|---|---|
| SRC-001 | （待确认：邮件/会议/文档/聊天/工单） | （待确认） | （待确认） | §（待确认） | （待确认） |

## 3. 重述需求清单（RR-XXX）

| ID | 重述（用 stakeholder 的话） | 原始措辞 | 来源 | 知识状态 | 提出方 | 信心 | 方案泄露 |
|---|---|---|---|---|---|---|---|
| RR-001 | （待确认） | （待确认） | SRC-XXX | FACT | （待确认） | high | false |

## 4. 冲突清单（CONFLICT → ISS-XXX）

| ID | 冲突描述 | 来源 A | 来源 B | 推荐处理 | Issue 链接 |
|---|---|---|---|---|---|
| CON-001 | （待确认） | SRC-XXX | SRC-YYY | （待确认：让 stakeholder 选择） | ISS-XXX |

## 5. 未知清单（UNKNOWN → Q-XXX）

| ID | 未知描述 | 阻塞？ | 建议提问 | 关联源 |
|---|---|---|---|---|
| UNK-001 | （待确认） | yes / no | （待确认） | SRC-XXX |

## 6. stakeholder 自查反馈位

> stakeholder 看到重述后勾选：
> - [ ] 是的，这就是我说的
> - [ ] 部分不是，需要补充（请在备注中写明）
> - [ ] 不是，请重新理解（请描述真实意图）

**stakeholder 备注**：（待确认）

**签名位置**：（待确认：stakeholder 姓名 / 角色 / 日期）

## 7. 来源追溯

| SRC-ID | 来源 | 关键陈述 | 知识状态 |
|---|---|---|---|
| SRC-001 | （待确认） | （待确认） | FACT |

## 8. 待确认问题

- Q-001: （待确认）

## 9. Constitution Compliance

- 规则先行：✅ 已对齐
- 六态标注：✅ 已对齐
- 模板符合性：✅ 已对齐
- 反模式自检：✅ 已通过（无方案泄露 / 无多需求合并）
- 冲突已升级：✅ 已登记到 issue-record（CONFLICT → ISS-XXX）
- 未知已路由：✅ 已记入 Q-XXX 或 issue-record

## 版本变更摘要

- v0.1: 初稿
