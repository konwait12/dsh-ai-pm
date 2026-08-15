<!--
Template for project-background-goal artifacts.

Section headings (需求来源与触发, 项目与需求背景, ...) are mandatory
Chinese forms because the artifact is consumed by Chinese business
stakeholders. English aliases are shown in comments only; do NOT add the
English aliases to the artifact headings themselves — the validator and
downstream consumers match the Chinese strings.

The artifact must include all sections 1–15 below, in order, with the
Constitution Compliance section placed between downstream handoff and
版本变更摘要. Required frontmatter is the same 10-field block used
by validate_artifact.py.

Optional sections (可选章节，校验器不要求，按需启用；材料不含对应内容时整节删除):
  - ## 术语表（按需）            — 仅当输入材料（如 BRD）含「名词解释 / 术语表」时启用
  - ## 涉及团队及职责总结（按需）  — 仅当输入材料含团队 / 职责信息时启用
-->
---
artifact_id: BG-001
version: v0.1
status: draft
owner: 待确认
business_fact_owner: 待确认
goal_decision_owner: 待确认
reviewer: 待确认
created_at: 待确认
updated_at: 待确认
confirmed_at: 待确认
---

# 项目背景与目标

## 0. 预检输入充分度判定
<!-- Preflight Input Sufficiency -->

在起草背景与目标前，先判定输入材料的充分度，并按 L0–L4 标注成熟度。仅当达到 L2 及以上时进入正文撰写；L0–L1 应转入 `intake-routing` 或 `requirement-restate` 模式。

| 维度 | L0（仅想法） | L1（单条稀疏来源） | L2（业务方案已存在） | L3（需求细节明确） | L4（上游已确认） |
|---|---|---|---|---|---|

## 术语表（按需）
<!-- Optional Glossary Section — 仅当输入材料（如 BRD）含「名词解释 / 术语表」时启用本节；否则整节删除，校验器不要求。 -->

仅当 BRD 等输入材料含「名词解释 / 术语表」时启用本节：逐条摘录材料中的术语 / 缩略词定义，不自造、不改写；每条标注来源 SRC 编号。

| 术语 / 缩略词 | 说明 | 来源 |
|---|---|---|
| 待补充 | 待补充 | SRC-001 |

## 1. 需求来源与触发
<!-- Requirement Source And Trigger -->

说明需求由谁、通过什么材料、因为什么事件提出，并引用 `SRC-*`。

## 2. 项目与需求背景
<!-- Project And Requirement Background -->

说明业务环境、需求由来、为什么现在需要处理。

## 3. 当前现状与已有做法
<!-- Current State And Existing Practices -->

说明当前流程、系统、人工方式或替代方案，以及仍然有效的部分。

## 4. 核心问题与证据
<!-- Core Problem And Evidence -->

按"问题 → 影响 → 证据来源"描述，不把预设功能当作问题。

## 5. 目标、未来期望与成功判断
<!-- Goal, Future Expectation And Success Judgment -->

区分业务结果、交付结果和成功判断。无法量化时标记待确认，不编造指标。

> **Fit Criterion（量化判据）提示**：每条目标/成功判断必须能回答"怎么算达成"。格式建议：`基线 → 目标 + 衡量方式 + 时间窗口`（例：邀约转化率 47% → 60%，CRM 数据，12 个月）。无法量化的目标必须显式标 `待确认` 并关联 §11 问题 ID 与 §Clarifications 的 owner（依据 Volere Fit Criterion + ISO/IEC/IEEE 29148 Verifiable 特性）。无判据的目标视为未完成。

## 6. 用户角色与利益相关者
<!-- User Roles And Stakeholders -->

只识别与背景和目标有关的角色、责任和影响；详细旅程留给下一步。

## 涉及团队及职责总结（按需）
<!-- Optional Team & Responsibility Summary — 仅当输入材料含团队 / 职责信息时启用本节；否则整节删除，校验器不要求。 -->

仅当输入材料含团队 / 职责信息时启用本节：从材料与角色关系中提取各团队 / 角色的职责边界与关联环节，不推断材料未提及的团队；每条标注来源 SRC 编号。

| 团队 / 角色 | 职责 | 关联环节 | 来源 |
|---|---|---|---|
| 待补充 | 待补充 | 待补充 | SRC-001 |

## 7. 时间、约束与依赖
<!-- Timing, Constraints And Dependencies -->

记录已知期限、资源、政策、合规、数据、系统和外部依赖。

## 8. 初步边界与非目标
<!-- Preliminary Boundaries And Non-Goals -->

记录已确认或暂定的边界，明确这不是最终产品范围。

## 9. 事实与决定
<!-- Facts And Decisions -->

| ID | 类型 | 内容 | 来源/决策人 | 状态 |
|---|---|---|---|---|
| FCT-001 | FACT | 待补充 | SRC-001 | 待确认 |

## 10. 假设、AI 推断、未知与冲突
<!-- Assumptions, AI Inferences, Unknowns And Conflicts -->

| ID | 类型 | 内容 | 依据 | 影响 | 责任人 | 处理方式 |
|---|---|---|---|---|---|---|
| UNK-001 | UNKNOWN | 待补充 | - | 待评估 | 待确认 | 待确认 |

## 11. 待确认问题
<!-- Questions To Confirm -->

| ID | 问题 | AI 初步判断与依据 | 选项/影响 | 决策人 | 阻断 | 延后风险 | 回写位置 |
|---|---|---|---|---|---|---|---|
| Q-001 | 待补充 | 待补充 | 待补充 | 待确认 | 是/否 | 待补充 | 待补充 |

> Note: §11 lists the open question register. After the human confirms an answer, the answer is integrated back into the artifact body AND a new Clarify Session row is added to `## Clarifications` below. Open questions on §11 may be closed when their corresponding Session is logged in `## Clarifications`.

## Clarifications

> Logged sessions of the one-question-at-a-time Clarify loop (see `SKILL.md` § Clarify Is Its Own Loop and `references/output-contract.md` § Clarifications Session Contract).
> One row per session. Ordered by `session_id`. Place this section between §11 待确认问题 and §12 来源追溯 so human reviewers can see "what was asked, what was answered, what changed".

| session_id | category | question | ai_preliminary_judgment | options | decision_owner | blocking | deferral_risk | accepted_answer | reflow_target | integrated_at | integrated_by | audit_recheck |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |

Rules:

- Only one Q+A round per row. Never combine multiple sessions.
- `accepted_answer` MUST be filled in before the artifact reaches `ready_for_human_review`.
- `reflow_target` MUST reference an existing section heading.
- `audit_recheck` MUST be the last field filled; if `fail`, status flips back to `needs_user_input`.

## 12. 来源追溯
<!-- Source Traceability -->

| 来源 ID | 材料/位置 | 关键内容 | 本文落位或排除理由 |
|---|---|---|---|
| SRC-001 | 待补充 | 待补充 | 待补充 |

## 13. 下游输入摘要
<!-- Downstream Handoff Summary -->

仅在 `confirmed` 后填写供"用户旅程与用户故事"使用的背景、目标、角色线索、约束、已接受假设和未决风险；不在此处生成旅程或故事。

## 14. Constitution Compliance

> 本节由 `src/framework/constitution.md` 强制要求：每个主干产物模板末尾必须包含本章节，用于显式审计与项目宪法的对齐情况。

| 原则 | 状态（PASS / FAIL / JUSTIFIED） | 证据 / 备注 |
|---|---|---|
| ① <核心原则 1> | PASS | <章节 X 已说明> |
| ② <业务约束 1> | PASS | <章节 X 已说明> |
| ③ <技术约束 1> | PASS | <章节 X 已说明> |
| ④ <治理规则 1> | PASS | <章节 X 已说明> |

- **PASS**：本步骤产物明确符合该原则，无需额外说明
- **FAIL**：本步骤产物违反该原则，禁止提交人工，需回到步骤重新处理
- **JUSTIFIED**：与原则有偏离但有充分理由，必须显式写明"偏离理由 + 影响范围 + 回归计划"

## 15. 版本变更摘要
<!-- Version Change Summary -->

| 版本 | 变更原因 | 主要变化 | 人工确认状态 |
|---|---|---|---|
| v0.1 | 初始候选 | 首次生成 | 待确认 |