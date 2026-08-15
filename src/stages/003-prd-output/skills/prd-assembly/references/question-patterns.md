# 提问模式 · prd-assembly

PRD 汇总步骤的 Clarify Session 聚焦于解决聚合期间发现的不一致与追溯缺口。

## 1. 追溯缺口（Traceability Gap）

**何时**： A forward or backward traceability check finds a broken link.

**模板**：
```
追溯链中发现断裂：{element_a}（{artifact}）→ {element_b}（{artifact}）无对应落位。
- 断裂描述：{what_is_missing}
- AI 初步判断：可能原因是 {possible_reason}
- 选项：A. 回到上游步骤补充（走变更回流） B. 在当前 PRD 中标注为已知缺口并接受风险 C. 不需要此追溯链（说明理由）
- 影响：断裂的追溯链意味着 {impact_on_quality}
- 回写位置：§7 正向追溯检查 / §8 反向追溯检查 → 处理决策
```

## 2. 跨产物矛盾（Cross-Artifact Contradiction）

**何时**： Two confirmed artifacts describe the same thing differently.

**模板**：
```
发现跨产物矛盾：{artifact_a} 中描述 {element} 为「{description_a}」，但 {artifact_b} 中描述为「{description_b}」。
- AI 初步判断：应以 {preferred_version} 为准，理由：{rationale}
- 选项：A. 以 {artifact_a} 为准，更新 {artifact_b}（走变更回流） B. 以 {artifact_b} 为准，更新 {artifact_a} C. 两者保留，标注为已知不一致
- 影响：不一致会导致 {downstream_impact}
- 回写位置：§9 不一致报告
```

## 3. 孤儿元素（Orphan Element）

**何时**： An element exists in an upstream artifact but has no downstream chain.

**模板**：
```
发现孤儿元素：{element_id}「{element_description}」（位于 {artifact}）在 PRD 中没有下游落位。
- AI 初步判断：应为 {preliminary_disposition}（P0 必覆盖 / P1 标注缺口 / 已废弃）
- 选项：A. 回到上游步骤补下游链（走变更回流） B. 在 PRD 中标注为已规划但未实施 C. 该元素已废弃，不进入 PRD
- 影响：孤儿元素意味着 {impact}
- 回写位置：§8 反向追溯检查
```

## 4. 优先级降级检测（Priority Downgrade Detection）

**何时**： A P0 story has become a P1 feature or a P1 function.

**模板**：
```
优先级降级检测：ST-{xxx}（P0）→ FEA-{xxx}（P1）。确认是否有意降级？
- AI 初步判断：可能原因 = {possible_reason}
- 选项：A. 有意降级（业务决策） B. 遗漏（应恢复 P0） C. 该故事已被拆分为多个功能，P0 部分在 FEA-{yyy}
- 影响：优先级不一致意味着 {impact}
- 回写位置：§9 不一致报告
```

## 5. 缺失 NFR（Missing NFR）

**何时**： A function clearly needs NFR but none is documented.

**模板**：
```
功能 FUN-{xxx}「{function_name}」缺少非功能性需求。该功能涉及 {concern}（如个人信息处理/实时性要求），建议补充 NFR-{category}。
- AI 初步判断：至少需要 {minimum_nfr}
- 选项：A. 回到 `function-description` 补充 NFR（走变更回流） B. 在 PRD 中标注为已知缺口 C. 不需要（说明理由）
- 影响：缺少 NFR 可能导致 {impact}
- 回写位置：§9 不一致报告
```
