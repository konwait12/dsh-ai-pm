# 提问模式 · user-journey-and-stories

Clarify Session 的规范提问模板。每个模板对应一个类别，并指明答案回写到哪里。

## 1. 角色澄清（Role Clarification）

**何时**： The upstream background lists a role but does not describe what it does in the lifecycle.

**模板**：
```
角色「{role_name}」在{lifecycle_stage}阶段的具体职责是什么？
- AI 初步判断：{inferred_role_actions}
- 选项：A. {option_a}  B. {option_b}  C. 其他（请描述）
- 影响：此角色的职责决定了后续用户故事的覆盖范围
- 回写位置：§2 用户旅程图 → {role_name} 列
```

## 2. 生命周期边界（Lifecycle Boundary）

**何时**： It is unclear where one lifecycle stage ends and another begins.

**模板**：
```
{stage_a}和{stage_b}的边界在哪里？
- AI 初步判断：边界是{proposed_boundary}
- 选项：A. {proposed_boundary}  B. 其他（请描述触发事件）
- 影响：边界不清会导致重复覆盖或遗漏
- 回写位置：§1 业务生命周期分解 → {stage_a} / {stage_b}
```

## 3. 路径类型覆盖（Path Type Coverage）

**何时**： The happy path is clear but exception/failure/recovery paths are missing.

**模板**：
```
在{journey_entry_description}这个场景中，{path_type}路径需要考虑吗？
- AI 初步判断：{preliminary_assessment}
- 选项：A. 需要（请描述典型场景）  B. 不需要（本期不做）  C. 不确定
- 影响：缺失此路径可能导致{impact}
- 回写位置：§2 用户旅程图 → {stage} × {role} 单元格 + §5 路径类型覆盖检查
```

## 4. 故事优先级（Story Priority）

**何时**： Multiple stories derive from the same journey entry and need prioritization.

**模板**：
```
从旅程条目{journey_entry_ref}派生的{story_count}个故事中，哪些是第一期必须覆盖的？
- AI 初步判断：必须覆盖 ST-{xxx}, ST-{yyy}（依据：上游目标 G{n}）
- 选项：A. 同意 AI 判断  B. 调整优先级（请说明）
- 影响：优先级决定开发排期和 MVP 范围
- 回写位置：§3 用户故事卡片 → 优先级提示列
```

## 5. 角色交接（Role Interaction）

**何时**： Two roles interact but the handoff protocol is unclear.

**模板**：
```
在{stage}阶段，{role_a}和{role_b}之间的交接规则是什么？
- AI 初步判断：{proposed_handoff}
- 选项：A. {option_a}  B. {option_b}  C. 不需要正式交接
- 影响：交接规则缺失会导致流程断裂
- 回写位置：§2 用户旅程图 → {stage} × {role_a} / {role_b} 单元格 → 交接路径
```

## 6. 范围决策（Scope Decision）

**何时**： A lifecycle stage or role might be out of scope for the current phase.

**模板**：
```
{lifecycle_stage_or_role}是否纳入本期范围？
- AI 初步判断：{preliminary}（依据：{evidence}）
- 选项：A. 纳入  B. 下期  C. 不做
- 影响：{impact_on_coverage}
- 回写位置：§1（如排除，标记为非目标）+ §4 覆盖矩阵（标注排除原因）
```

## 7. 故事格式细化（Story Format Refinement）

**何时**： A story card is too vague or mixes multiple needs.

**模板**：
```
故事 ST-{xxx}「{current_story_text}」是否需要拆分或细化？
- AI 初步判断：{analysis}（可能拆分为 ST-{aaa}, ST-{bbb}）
- 选项：A. 拆分为 {n} 个独立故事  B. 保持现状  C. 细化场景描述
- 影响：模糊的故事无法准确估算和验收
- 回写位置：§3 用户故事卡片 → ST-{xxx}
```

## 8. 缺失生命周期阶段（Missing Lifecycle Stage）

**何时**： A lifecycle stage is logically implied but not mentioned in any source.

**模板**：
```
当前生命周期缺少「{missing_stage}」阶段（常见于{domain}类项目），是否需要补充？
- AI 初步判断：需要（理由：{rationale, e.g. "用户完成核心动作后必然涉及后续跟进"}）
- 选项：A. 需要，请提供典型场景  B. 不需要（本期不做此阶段）  C. 不确定
- 影响：缺失此阶段可能导致{impact}
- 回写位置：§1 业务生命周期分解（新增行或标记为非目标）
```
