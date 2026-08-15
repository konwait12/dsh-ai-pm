# 来源处理 · user-journey-and-stories

本 Skill 主要消费一个上游产物（已确认的 project-background-goal）。因此来源处理比 `project-background-goal` 更轻量，但仍必须严格。

## 主来源（Primary Source）

已确认的 `project-background-goal` 产物是主要且权威的来源。它的 §13 下游交接摘要提供：
- `confirmed_roles`：→ §2 旅程图角色
- `known_lifecycle_clues`：→ §1 生命周期分解
- `goal_summary`：→ §3 故事优先级提示
- `constraints_and_dependencies`：→ 旅程范围的边界条件
- `source_ids`：→ 在 §9 交叉引用

## 次要来源（Secondary Sources）

当上游产物引用了原始材料（SRC-001、SRC-002 等）时，可以在上游产物摘要不足的情况下查阅这些材料以获取关于角色与生命周期的额外上下文。绝不用原始来源的解读覆盖已确认的产物。

## 来源登记（Source Registration）

旅程图与故事卡片中的每条主张必须引用以下之一：
- 上游产物 ID（用于已确认的背景事实）
- 上游产物中的具体 SRC-* ID（用于直接的来源证据）
- AI_INFERENCE 或 ASSUMPTION 标签（用于推导内容）

## 冲突处理（Conflict Handling）

如果旅程条目与上游背景冲突：
1. 在 §7 标记为 CONFLICT。
2. 同时呈现旅程派生的主张与上游背景陈述。
3. 通过 Clarify 请求人工解决。
4. 不要静默选边。

## 多来源交叉验证（Multi-Source Cross-Validation）

当上游背景有 ≥ 3 个来源时，核验：
- 角色描述在来源间一致
- 生命周期阶段有 ≥ 1 个来源支撑
- 旅程图中的痛点可追溯到上游 §4
