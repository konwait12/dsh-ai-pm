<!--
变更提案模板 · Change Proposal Template
借鉴 OpenSpec delta-spec 模型 (propose → explore → apply → archive)
每个 change 是一个独立文件夹：99-review/changes/CHG-NNN/
-->
---
proposal_id: CHG-{NNN}
version: v0.1
status: draft
proposed_by: {姓名}
proposed_at: {YYYY-MM-DD}
approved_by: 待确认
approved_at: 待确认
archived_at: 待确认
affected_artifacts: []
---

# 变更提案: {简短标题}

## 1. 动机 (Why)

- 触发原因：（业务需求变更 / 发现缺陷 / 上游输入更新 / 其他）
- 当前基线存在的问题：

## 2. 影响范围

| 受影响的 Artifact | Artifact ID | 当前状态 | 变更后状态 |
|---|---|---|---|
| | | | |

受影响的下游产物（级联失效）：
- 

## 3. 变更内容

### 新增 (ADDED)

| 对象 | 位置 | 内容 | 理由 |
|---|---|---|---|
| | | | |

### 修改 (MODIFIED)

| 对象 | 位置 | 旧内容摘要 | 新内容摘要 | 理由 |
|---|---|---|---|---|
| | | | | |

### 删除 (REMOVED)

| 对象 | 位置 | 内容摘要 | 理由 |
|---|---|---|---|
| | | | | |

## 4. 方案评估

### 方案 A（推荐）: {方案名称}
- 描述：
- 优点：
- 缺点：
- 风险：

### 方案 B（备选）: {方案名称}
- 描述：
- 优点：
- 缺点：
- 风险：

## 5. 回滚计划

如果变更批准后出现问题：
1. 回滚步骤：
2. 受影响的下游如何恢复：
3. 回滚责任人：

## 6. 审批

| 角色 | 审批人 | 决定 | 日期 | 备注 |
|---|---|---|---|---|
| business_owner | | 待确认 | | |
| product_owner | | 待确认 | | |

## 7. 归档记录

- 归档时间：
- 合并到基线的 commit/版本：
- ChangeRecord 引用：REC-CHG-{NNN}
