# 输出契约 · prd-assembly

## 状态机（Status Machine）
与所有 Skill 相同的 6 种状态：draft → needs_user_input → conditional_review → ready_for_human_review → confirmed → superseded。

## 产物章节（Artifact Sections）

正文（7 节，干系人/研发/测试阅读）：
1. **项目背景与目标** (§1): 来自 `project-background-goal` verbatim
2. **业务角色、用户旅程与用户故事** (§2): 来自 `user-journey-and-stories` verbatim
3. **UX：页面设计与交互规则** (§3): 来自 `product-ux` verbatim
4. **分功能描述** (§4): 来自 `function-description` verbatim
5. **按需章节** (§5): 字段规则、埋点、依赖、未决项
6. **事实与决定** (§6): 汇总的关键事实与人工决策
7. **验收依据** (§7): 验收基线

附录（2 节，评审/机器用，非正文）：
- **需求追溯矩阵**: G→ST→FEA→FUN→AC→BR matrix（traceability_check.py 读取此表）
- **自审记录（Constitution Compliance）**: AI 4-principle self-audit（dor_check audit_evidence 读取）

**不在 PRD 内**（由机器在 gate 时产出、进 99-review 评审记录）：
- 上游产物清单 → frontmatter `upstream_artifact_ids`
- 正向/反向追溯检查 → `traceability_check.py` 输出
- 不一致报告 → 评审记录（review taxonomy [Contradiction]/[Gap]/… labels）
- 变更记录 → frontmatter version/updated_at + CHANGELOG

## 聚合规则（Aggregation Rules）
- 逐字复制上游内容，绝不转述
- 保留全部 ID（SRC-*、ST-*、FEA-*、FUN-*、BR-*、AC-*）
- PRD 中无新需求
- 不静默解决不一致
- 条件章节（§5.1、§5.2）仅在上游有非空内容时才落章

## RTM 格式（RTM Format）
| Goal (G) | Story (ST) | Feature (FEA) | Function (FUN) | Acceptance (AC) | Business Rule (BR) |
每行 = 一条完整追溯链。P0 项必须有完整链。
