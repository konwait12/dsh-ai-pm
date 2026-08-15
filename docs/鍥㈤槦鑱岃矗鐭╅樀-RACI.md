# 团队职责矩阵（RACI）

> 本文档定义 PM Scaffold 脚手架各环节的角色与职责边界，用 RACI 矩阵表达「谁执行 / 谁负责 / 咨询谁 / 知会谁」，并明确「AI 可以做什么 / 必须人审什么」的人机分工。覆盖两个交付物落点：角色与职责的 RACI 表达、人机分工边界（后者与 `docs/变更管理机制-change-management.md` 的改版 / CR 落点衔接）。
> 相关概念：评审角色约束见 `src/framework/contracts.md`（Confirmation Invariant）与 `src/framework/governance.md`（Confirmation）；角色枚举见 `src/framework/workflow-registry.json`（`reviewer_roles` / `support_capabilities[*].responsible_role`）。

---

## 一、文档目的与范围

本文档回答三类问题：

1. **脚手架各环节有哪些角色**：`business_owner` / `product_manager` / `ux_designer` / `tech_lead` / `qa` / `ai_agent` / `reviewer` / `approver` 的定义与在现有机制中的落点。
2. **每个环节谁做什么**：用 RACI 矩阵列出 10 个环节 × 8 个角色。
3. **人机分工边界**：AI 可以做什么、必须人审什么。

> 本文档是**文档**，不改变任何代码行为。RACI 是职责约定，不是校验器输入；但其中「reviewer 必须命中 `authorized-reviewers.json` + `reviewer_roles`」等约束与现有代码一致，是**硬约束**。

---

## 二、角色定义

### 2.1 角色总览

| 角色 | 中文 | 定义 | 现有机制落点 |
|---|---|---|---|
| `business_owner` | 业务负责人 | 拥有业务事实与业务目标，对「业务真相」负责（宪法第 1 条：Business truth remains human-owned）。 | registry `reviewer_roles`（BG / JS / FD / PRD）；frontmatter `business_fact_owner`；`support_capabilities[*].responsible_role` |
| `product_manager` | 产品经理 | 拥有需求内容与目标决策，对 PRD 内容与范围负责。 | registry `reviewer_roles` 中的 `product_owner`（**本文档 `product_manager` 与 registry `product_owner` 同义**）；frontmatter `goal_decision_owner` |
| `ux_designer` | UX 设计师 | 拥有用户旅程 / 页面设计 / 交互规则的设计产出。 | 参与 `user-journey-and-stories` / `product-ux` 环节；不在 registry `reviewer_roles` 内（评审角色由 product_owner 承担） |
| `tech_lead` | 技术负责人 | 拥有功能描述 / 技术可行性视角，是 PRD 的下游消费者（研发）。 | 参与 `function-description` 环节；不在 registry `reviewer_roles` 内 |
| `qa` | 测试 | 拥有验收判据视角，是 PRD 的下游消费者（测试）。 | 参与 `function-description`（AC）/ `tracking-plan` 环节；不在 registry `reviewer_roles` 内 |
| `ai_agent` | AI 智能体 | 脚手架的执行者：起草产物、跑机器校验、登记记录。**永远不能设置 `confirmed`**。 | `src/scripts/pipeline.py`（review 拒绝 AI / 待确认 / simulated 名）；`src/framework/contracts.md`（Confirmation Invariant） |
| `reviewer` | 评审人 | 执行评审、提出意见的人；对产物质量把关。**必须命中 `00-input/authorized-reviewers.json` 且角色在 registry `reviewer_roles` 内**。 | `src/scripts/pipeline.py` `load_authorized_reviewer()`；`src/scripts/branch_validator.py` |
| `approver` | 审批人 | 对确认 / 变更负最终责任的人。当前模型下 reviewer 即 approver（`review --decision approve`）；变更审批由 `business_owner` / `product_owner` 承担。 | `src/shared/change-management/proposal-template.md` §6 审批表 |

> **角色映射说明**：registry 使用 `product_owner`（产品负责人），本文档按用户要求使用 `product_manager`（产品经理），两者在本脚手架中同义。`reviewer` 与 `approver` 在「确认」场景下是同一人（reviewer 通过 approve 即完成审批），在「变更」场景下 reviewer 评审提案、approver 批准提案，可分离。

### 2.2 角色与 registry 的绑定

| 角色 | 是否在 `reviewer_roles` 可选项 | 可评审的 work_item |
|---|---|---|
| `business_owner` | ✅ | `project-background-goal` / `user-journey-and-stories` / `function-description` / `prd-assembly` |
| `product_owner`（= `product_manager`） | ✅ | 全部 5 个主 work_item |
| `ux_designer` | ❌（不参与评审确认） | — |
| `tech_lead` | ❌（不参与评审确认） | — |
| `qa` | ❌（不参与评审确认） | — |
| `ai_agent` | ❌（永远不可评审） | — |

> 依据：`src/framework/workflow-registry.json` `work_items[*].reviewer_roles`。评审确认只接受 registry 内角色；`ux_designer` / `tech_lead` / `qa` 通过「被咨询（C）」参与环节，不通过 `pipeline.py review` 确认产物。

---

## 三、RACI 矩阵

### 3.1 RACI 定义

- **R（Responsible）执行者**：实际完成该环节工作的人 / 角色。
- **A（Accountable）负责人**：对该环节结果负最终责任，最终拍板。每个环节有且仅有一个 A。
- **C（Consulted）被咨询**：提供输入 / 意见，决策前需征询。
- **I（Informed）被告知**：结果产生后需知会。

### 3.2 矩阵总表

| 环节 | business_owner | product_manager | ux_designer | tech_lead | qa | ai_agent | reviewer | approver |
|---|---|---|---|---|---|---|---|---|
| 1. 需求澄清 | C | **A** | C | C | I | **R** | I | I |
| 2. 背景目标 | **R** | **A** | C | C | I | **R** | C | I |
| 3. 用户旅程 | C | **A** | **R** | I | C | **R** | C | I |
| 4. UX 设计 | C | **A** | **R** | C | I | **R** | C | I |
| 5. 功能描述 | C | **A** | C | **R** | C | **R** | C | I |
| 6. 追踪计划 | **R** | **A** | I | C | C | **R** | C | I |
| 7. PRD 组装 | C | **A** | C | C | C | **R** | C | I |
| 8. 评审 | C | C | C | C | C | I | **R** | **A** |
| 9. 变更 | **R** | C | C | C | C | **R** | **R** | **A** |
| 10. 发布 | I | **A** | I | I | I | **R** | C | C |

> 说明：
> - 每个内容环节（1-7）的 **A 均为 `product_manager`**（产品经理对需求内容与范围负责），`business_owner` 在「背景目标 / 追踪计划」作为 R（业务事实与埋点需求由业务方提供），在其余环节为 C。
> - 环节 8「评审」：`reviewer` 为 R（执行评审），`approver` 为 A（批准确认）；当前模型下二者可为同一人。
> - 环节 9「变更」：`business_owner` 为 R（业务变更的提出方，`proposed_by`），`ai_agent` 为 R（起草提案与影响评估），`reviewer` 为 R（评审提案），`approver` 为 A（批准变更）。
> - 环节 10「发布」：`product_manager` 为 A（对发布决策负责），`ai_agent` 为 R（执行 `src/scripts/prd_publish.py` 飞书发布脚本，仅发布已确认 PRD）。

### 3.3 各环节职责说明

| 环节 | 对应机制 / Skill | 职责说明 |
|---|---|---|
| 1. 需求澄清 | `intake-routing` / `clarify` / `requirement-restate` | ai_agent 起草澄清问题、登记 Q-/ISS-，product_manager 拍板澄清结果；business_owner 提供业务事实答案。 |
| 2. 背景目标 | `project-background-goal` | business_owner 提供业务事实与目标（`business_fact_owner`），product_manager 拍板目标决策（`goal_decision_owner`），ai_agent 起草 BG 产物。 |
| 3. 用户旅程 | `user-journey-and-stories` | ux_designer 主导旅程 / 场景 / 用户故事设计，product_manager 负责范围基线，ai_agent 起草。 |
| 4. UX 设计 | `product-ux`（page-design + interaction-rules） | ux_designer 主导页面设计与交互规则，product_manager 负责 UX 范围，ai_agent 起草。 |
| 5. 功能描述 | `function-description`（feature-list / functional-flow / business-rules / validation-rules / state-machine / exception-handling / acceptance-criteria） | tech_lead 主导功能与规则（下游研发视角），qa 提供验收判据视角（AC），product_manager 负责，ai_agent 起草。 |
| 6. 追踪计划 | `tracking-plan`（分支） | business_owner 提供埋点 / 数据需求（registry `responsible_role`），qa 提供口径视角，product_manager 负责，ai_agent 起草。 |
| 7. PRD 组装 | `prd-assembly` | ai_agent 聚合已确认上游产物（不得新增需求），product_manager 对最终 PRD 负责。 |
| 8. 评审 | `human-gate` / `pipeline.py review` | reviewer 执行评审（命中 authorized-reviewers.json + reviewer_roles），approver 批准确认；ai_agent 只跑机器校验（`--yes`），不参与确认。 |
| 9. 变更 | `change-management`（CHG-NNN 提案 / reflow） | business_owner 提出业务变更，ai_agent 起草提案与影响评估，reviewer 评审，approver 批准。 |
| 10. 发布 | `src/scripts/prd_publish.py`（飞书发布脚本） | ai_agent 执行发布（仅已确认 PRD），product_manager 对发布决策负责。 |

---

## 四、AI 可以做什么 / 必须人审什么（人机分工）

### 4.1 AI 可以做什么（ai_agent 的权限边界）

| # | 能力 | 依据 |
|---|---|---|
| 1 | 起草所有产物（`draft` / `ready_for_human_review`） | `src/framework/workflow.md`（Machine validation may produce `ready_for_human_review` but never `confirmed`） |
| 2 | 跑机器校验（`machine_gate`：dor_check / branch_validator / traceability_check / property_check） | `src/scripts/pipeline.py` `machine_gate()` |
| 3 | 起草澄清问题、登记 Q-/ISS-/DEC-/SRC- 引用 | `src/shared/clarify/`；`src/framework/governance.md`（Stage Closeout） |
| 4 | 起草变更提案与影响评估（downstream impact） | `src/shared/change-management/proposal-template.md` |
| 5 | 需求重举（发散 / 复述）候选生成 | `src/stages/001-business-requirements/skills/requirement-restate/` |
| 6 | 引用并校准能力片段（capability-fragment） | `src/shared/capability-fragments/README.md` |
| 7 | 执行 `reflow`（机器翻转下游为 `superseded`，语义上代表人工发起的变更） | `src/scripts/pipeline.py`（reflow 动作） |
| 8 | 执行发布（`src/scripts/prd_publish.py` 飞书发布脚本，仅发布已确认 PRD） | `src/scripts/prd_publish.py` |

### 4.2 必须人审什么（AI 不可做）

| # | 禁区 | 依据 |
|---|---|---|
| 1 | **设置 `confirmed` 状态**：仅授权人工 `review --decision approve` 可确认 | `src/framework/contracts.md`（Confirmation Invariant）；`src/scripts/pipeline.py` |
| 2 | **提供 reviewer 身份**：reviewer 必须命中 `authorized-reviewers.json`（id + name + role 全匹配） | `src/scripts/pipeline.py` `load_authorized_reviewer()` |
| 3 | **提供业务事实（FACT）**：事实必须有来源；`business_fact_owner` 复核 | 宪法第 1 条；`src/framework/contracts.md`（Knowledge States） |
| 4 | **做出目标 / 范围决策（DECISION）**：`goal_decision_owner` 拍板 | `src/templates/_frontmatter-schema.md` §1；`src/framework/contracts.md` |
| 5 | **批准变更**：变更提案 §6 审批表由 `business_owner` / `product_owner` 给出 approved | `src/shared/change-management/proposal-template.md`；`archive.py` `validate_approved()` |
| 6 | **绕过 human gate**：`--yes` 只跑机器检查，不产生确认 | `src/scripts/pipeline.py`（`--yes` NOTICE） |
| 7 | **对 `simulated` 产物 approve**：reviewer 名含 simulated / 模拟被拒绝 | `src/scripts/pipeline.py`；`docs/状态语义矩阵.md` §四 |
| 8 | **静默回退已确认产物**：`confirmed → draft` 必须留痕（见变更管理文档） | `docs/变更管理机制-change-management.md`（逆向跃迁留痕要求） |

### 4.3 人机分工的校验闭环

```text
ai_agent 起草（draft / ready_for_human_review）
   ↓
machine_gate 机器校验（只能产生候选，不能确认）
   ↓
reviewer 评审（命中 authorized-reviewers.json + reviewer_roles）
   ↓
approver 批准（review --decision approve → confirmed）
   ↓
branch_validator 复核（hash 绑定 + record_sha256 + 锚点）
```

> 任何环节缺失人工确认，`workflow_valid` 不会为 true；任何「AI 直接确认」的尝试都会被 `pipeline.py` / `branch_validator.py` 拒绝。

---

## 五、与现有机制的衔接

1. **评审角色硬约束**：`reviewer` 必须命中 `00-input/authorized-reviewers.json` 且角色在 registry `reviewer_roles` 内（`src/scripts/pipeline.py` / `branch_validator.py`）。RACI 中的「评审」环节只允许 `business_owner` / `product_owner` 作为 reviewer。
2. **frontmatter 角色字段**：`business_fact_owner` / `goal_decision_owner` / `owner` / `reviewer` 与本文档角色一一对应（`src/templates/_frontmatter-schema.md` §1）。
3. **「涉及团队及职责总结」章节的落地方向**（本文档不实现，仅记录）：在 `prd.md` 新增「涉及团队及职责总结」章节（团队 / 系统 / 职责 / 交付物 / 依赖），并扩展 frontmatter 支持多团队字段；本 RACI 矩阵可作为该章节的权威来源。
4. **多团队协作**：真实多系统 PRD（WeCom / CCE / Lion / Apollo）的职责边界由本矩阵的「角色 × 环节」表达；每个团队映射到对应角色（如 CCE 团队 → tech_lead 视角、业务方 → business_owner 视角）。

---

## 六、边界与例外

1. **角色可兼任**：同一人可兼任 `business_owner` 与 `product_manager`，但**评审确认时 reviewer 与产物 owner 不强制分离**（当前模型不要求四眼分离，仅要求 reviewer 命中授权清单）。
2. **`ux_designer` / `tech_lead` / `qa` 不参与确认**：它们通过 C（被咨询）参与环节，不通过 `pipeline.py review` 确认产物；如需它们确认，需扩展 registry `reviewer_roles`（本文档不改变代码）。
3. **变更场景的 reviewer / approver 分离**：变更提案的评审（reviewer）与批准（approver）可分离，由 `change-management` 流程定义（见变更管理文档）。

---

## 七、维护与更新

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.1 | 2026-08-14 | 首版 RACI 矩阵，沉淀自 `src/framework/workflow-registry.json`、`src/framework/contracts.md`、`src/framework/governance.md` 与既有代码行为 |

---

## 附：证据文件索引

| 证据 | 位置 |
|---|---|
| 角色枚举（reviewer_roles / responsible_role） | `src/framework/workflow-registry.json` |
| Confirmation Invariant / Shared Records | `src/framework/contracts.md` |
| Confirmation / Human-In-The-Loop / Stage Closeout | `src/framework/governance.md` |
| 评审 / 机器闸门 / --yes / reflow | `src/scripts/pipeline.py` |
| confirmed 复核（reviewer / hash / 锚点） | `src/scripts/branch_validator.py` |
| frontmatter 角色字段 | `src/templates/_frontmatter-schema.md` §1 |
| 变更审批表 | `src/shared/change-management/proposal-template.md` §6 |
