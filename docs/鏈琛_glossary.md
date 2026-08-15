# 术语表（Glossary）

> 本文档是 PM Scaffold 脚手架**核心术语的语义权威参考**：定义、出现位置、相关校验器与示例，全部以现有 framework 文档（`src/framework/*.md`）、注册表（`src/framework/workflow-registry.json`）与真实代码行为（`src/scripts/*.py`）为证据，不臆测。
>
> 本文档覆盖「术语表」这一交付物落点：为脚手架核心术语提供统一、可核验的语义权威参考。
> 相关概念：产物状态语义见 `docs/状态语义矩阵.md`；知识状态标签见 `src/framework/contracts.md`；主干/分支区分见 `src/framework/governance.md`。

---

## 一、文档目的与范围

本术语表回答三类问题：

1. **脚手架核心术语是什么**：`work_item` / `artifact` / `ReviewRecord` / `machine_gate` / `branch` / `simulated` / `confirmed` / `superseded` / `upstream_artifact_ids` / `rule_density` / `capability-fragment` 等，每个术语给出「定义 / 出现位置 / 相关校验器 / 示例」。
2. **术语之间的边界**：哪些是脚手架本体术语（收录），哪些是具体案例词（**不收录**，见 §四）。
3. **使用约定**：写产物、写文档、写校验器时如何保持一致（见 §五）。

> 本术语表是**文档**，不是校验器输入。它不改变任何代码行为；后续如需将术语表落地为产物章节（`prd.md` / `function-description.md` 新增「术语表」章节），以本文档为权威来源。

---

## 二、核心术语表

> 每个术语的「相关校验器」列出的脚本，是该校验器**读取或校验该术语语义**的位置，用于帮助定位实现。

### 2.1 work_item（工作项）

| 项 | 内容 |
|---|---|
| **定义** | 脚手架执行的最小工作单元。每个 work_item 对应一个 Skill、一个产物文件、一组前置依赖（predecessors）与一组评审角色（reviewer_roles）。5 个主 work_item 构成主干：`project-background-goal` → `user-journey-and-stories` → `product-ux` → `function-description` → `prd-assembly`。 |
| **出现位置** | `src/framework/workflow-registry.json` 的 `work_items[]`（权威定义）；`src/framework/workflow.md`（Backbone 与 Work-Item Cycle）；`src/framework/governance.md`（Main Trunk vs. Branch）。 |
| **相关校验器** | `src/scripts/orchestrator.py`（active 态 / workflow_valid / next_work_item 判定）；`src/scripts/pipeline.py`（`--work-item` 参数、`resolve_work_item`）；`src/scripts/workflow_registry.py`（`work_items()` / `resolve_work_item()`）。 |
| **示例** | `project-background-goal`（order=1，predecessors=[]，reviewer_roles=[business_owner, product_owner]）；`prd-assembly`（order=5，predecessors=其余 4 个主 work_item）。 |

### 2.2 artifact（产物）

| 项 | 内容 |
|---|---|
| **定义** | work_item 产出的正式交付文件（Markdown），带 frontmatter 元数据（`artifact_id` / `version` / `status` / `owner` 等）。产物是**状态机的载体**：`draft → … → confirmed` 的状态跃迁都发生在 artifact 的 `status` 字段上。产物不定义架构（宪法第 3 条：artifacts do not define architecture）。 |
| **出现位置** | `src/templates/_frontmatter-schema.md`（frontmatter 字段权威定义）；`src/framework/workflow-registry.json` 的 `artifact_types[]`（产物 ID / 生产者 / PRD 落点 / 依赖）；各 work_item 的 `artifact_dir` / `artifact_file`。 |
| **相关校验器** | `src/stages/*/skills/*/scripts/validate_artifact.py`（结构 + 语义红线）；`src/scripts/property_check.py`（function-description 逻辑完备性）；`src/scripts/branch_validator.py`（confirmed 产物 hash 绑定）。 |
| **示例** | `001-business-requirements/01-background-goal/background-goal.md`（artifact_id=`BG-001`）；`003-prd-output/prd.md`（artifact_id=`PRD-001`）。 |

### 2.3 ReviewRecord（评审记录）

| 项 | 内容 |
|---|---|
| **定义** | 人工评审产物后生成的记录文件，是 `confirmed` 状态的**唯一合法证据**。字段见 `src/framework/contracts.md` Shared Records：`work_item` / `artifact_version` / `artifact_content_sha256` / `decision` / `reviewer` / `reviewer_id` / `reviewer_role` / `reviewed_at` / `record_created_at` / `record_sha256` / `comments`。每条记录带 `record_sha256` 自指纹，并在 `99-review/.hash-anchor.jsonl` 落外部锚点。 |
| **出现位置** | `src/framework/contracts.md`（Shared Records）；`src/scripts/pipeline.py` `review()`（写入逻辑）；`src/scripts/hash_anchor.py`（自指纹 + 锚点）；实际落点 `requirements/REQ-XXX/99-review/review-*.md`。 |
| **相关校验器** | `src/scripts/branch_validator.py`（confirmed 必须有匹配 ReviewRecord + hash 一致 + 锚点校验）；`src/scripts/hash_anchor.py`（`record_body_sha256` / `verify_anchor_chain` / `verify_artifact_anchored`）。 |
| **示例** | `99-review/review-prd-assembly-2026-08-13.md`，含 `- artifact_content_sha256: <64位hex>`、`- reviewer: <授权人名>`、`- record_sha256: <64位hex>`。 |

### 2.4 machine_gate（机器闸门）

| 项 | 内容 |
|---|---|
| **定义** | 由多个机器校验器组合而成的**候选生成闸门**：`dor_check`（DoR/DoD + 知识状态 + 阶段收口）+ `branch_validator`（评审记录 / hash / 锚点）+ `traceability_check`（prd-assembly 的 RTM 正反向追溯）+ `property_check`（function-description 逻辑完备性）。**机器校验只能产生 `ready_for_human_review`，不能产生 `confirmed`**（宪法第 6 条：Human gates cannot be bypassed）。 |
| **出现位置** | `src/framework/contracts.md`（Confirmation Invariant）；`src/framework/governance.md`（Quality Sequence / Confirmation）；`src/scripts/pipeline.py` `machine_gate()`。 |
| **相关校验器** | `src/scripts/dor_check.py`；`src/scripts/branch_validator.py`；`src/scripts/traceability_check.py`；`src/scripts/property_check.py`。 |
| **示例** | `python3 src/scripts/pipeline.py requirements/REQ-XXX gate --work-item function-description` 返回 `{"ok": true/false, ...}`；`ok=true` 只代表「候选可送审」，不代表「已确认」。 |

### 2.5 branch（分支 / 可选能力）

| 项 | 内容 |
|---|---|
| **定义** | 相对**主干（Main Trunk）**的可选 / 条件能力。主干是 5 个主 work_item（必需、无 Inquiry）；分支是其余一切（function-description 的子 Skill、共享机制 clarify / change-management / decision-log / intake-routing / project-init / human-gate / audit / traceability、可选支持能力 competitive-research / feasibility-analysis / tracking-plan / issue-record / requirement-restate 等）。**每个分支入口都触发 Inquiry Gate**（默认行为 vs 覆盖）。 |
| **出现位置** | `src/framework/governance.md`（Main Trunk vs. Branch — Strict Distinction、Default Behaviors By Artifact）；`src/framework/workflow-registry.json` 的 `support_capabilities[]` 与 `internal_capabilities[]`。 |
| **相关校验器** | `src/scripts/pipeline.py`（`branch_skill_signals` / `entry_branch_signals`）；各分支 Skill 的 `scripts/validate_artifact.py`（如 `src/stages/002-product-requirements/skills/tracking-plan/scripts/validate_artifact.py`）。 |
| **示例** | `tracking-plan`（分支，产物落 `99-review/support/tracking-plan.md`）；`requirement-restate`（分支能力，产物落 `99-review/support/`）。 |

### 2.6 simulated（模拟状态）

| 项 | 内容 |
|---|---|
| **定义** | **测试线专用终态**：仅用于跑测 / 演示，产物不进入正式交付，全程**不要求人工确认**。gate 对 simulated 跳过知识状态 / 阶段收口 / trace 强制（`status=simulated (gate not enforced)`）。`pipeline.py review` 拒绝 reviewer 名含 simulated / 模拟。 |
| **出现位置** | `docs/状态语义矩阵.md`（§一 状态全景表 / §四 明确约定）；`src/templates/_frontmatter-schema.md` §2（状态枚举）；`run_tests_mac.sh`（`grep -q '^status: simulated'` 跳过 trace）。 |
| **相关校验器** | `src/scripts/dor_check.py`（simulated 跳过 gate）；`src/scripts/orchestrator.py`（simulated 不在 active 集合 → 不产生越级）；`src/scripts/pipeline.py`（review 拒绝 simulated）。 |
| **示例** | `requirements/REQ-007-insidemp/`、`requirements/REQ-008-bae/` 全流程 `status: simulated`，`workflow_valid=true`（无越级待审卡点）。 |

### 2.7 confirmed（已确认状态）

| 项 | 内容 |
|---|---|
| **定义** | **唯一正式完成态**。仅授权人工可设置（`pipeline.py review --decision approve`，且 reviewer 与 `00-input/authorized-reviewers.json` 匹配、角色在 registry `reviewer_roles` 内）。`confirmed` 与 ReviewRecord 的 `artifact_content_sha256` 绑定，内容不可变（改动即 CRITICAL）。 |
| **出现位置** | `src/framework/contracts.md`（Artifact States / Confirmation Invariant）；`src/framework/governance.md`（Confirmation）；`docs/状态语义矩阵.md`（§一 / §四）；`src/templates/_frontmatter-schema.md` §2。 |
| **相关校验器** | `src/scripts/branch_validator.py`（confirmed 必须有效 reviewer + 匹配 ReviewRecord + hash 一致 + 锚点）；`src/scripts/pipeline.py`（approve 前置：`current_status == ready_for_human_review`）。 |
| **示例** | `requirements/REQ-001-rsvp/` 5 个主 work_item 全部 `status: confirmed`，`workflow_valid=true`、`complete=true`。 |

### 2.8 superseded（失效状态）

| 项 | 内容 |
|---|---|
| **定义** | 被更新的确认版本 / 变更回流替代，**必须重新校验**。`superseded` 视为「待重跑」：会成为 `next_work_item`，其下游保持 DoR 阻断直到重新 confirmed。由人工发起（`pipeline.py reflow --apply` 由机器执行，语义上代表人工发起的变更）。 |
| **出现位置** | `docs/状态语义矩阵.md`（§一 / §四）；`src/framework/contracts.md`（Artifact States）；`src/framework/workflow-registry.json`（`dependency_policy.cascade_invalidation`）。 |
| **相关校验器** | `src/scripts/pipeline.py`（reflow 动作）；`src/scripts/orchestrator.py`（superseded 视为待重跑 / next_work_item）。 |
| **示例** | 变更确认后，下游 `product-ux` / `function-description` / `prd-assembly` 被翻转 `status: superseded`，需从最早受影响 work_item 重跑。 |

### 2.9 upstream_artifact_ids（上游产物 ID 列表）

| 项 | 内容 |
|---|---|
| **定义** | `prd.md` frontmatter 的扩展字段，列出 PRD 引用的上游产物 ID，用于 RTM 正反向追溯。**必须使用上游产物 `artifact_id` 的原始格式**（单连字符，如 `BG-001`），不得加版本后缀（统一约定）。 |
| **出现位置** | `src/templates/_frontmatter-schema.md` §3（扩展字段）；`src/stages/003-prd-output/skills/prd-assembly/scripts/validate_artifact.py`（DoR 校验正则）；`src/scripts/consistency_check.py`（`check_upstream_artifact_ids_contract`）。 |
| **相关校验器** | `src/stages/003-prd-output/skills/prd-assembly/scripts/validate_artifact.py`（正则 `(BG|JS|UX|FD)-\d+(?:-\d+)?`）；`src/scripts/consistency_check.py`（模板 ↔ 校验器约定一致性）。 |
| **示例** | `upstream_artifact_ids: ["BG-001", "JS-001", "UX-001", "FD-001"]`。 |

### 2.10 rule_density（规则密度）

| 项 | 内容 |
|---|---|
| **定义** | function-description 的逻辑完备性维度：每个 FUN 必须有足够的 BR + VL + AC 覆盖。阈值：总数 < 3 → HIGH（under-specified）；< 6 → MEDIUM（建议补充）。支持两种布局：`### FUN-XXX` 子标题块、功能清单表格（按「所属 FUN」列聚合）。无 FUN 可定位时输出 MEDIUM「规则密度校验跳过」兜底。 |
| **出现位置** | `src/scripts/property_check.py`（`check_rule_density` / `_table_rule_density` / `_id_fun_pairs`）。 |
| **相关校验器** | `src/scripts/property_check.py`（仅 function-description 触发，见 `pipeline.py machine_gate()`）。 |
| **示例** | `FUN-001 has only 2 rules (BR=1, VL=0, AC=1) — under-specified (minimum 3)`。 |

### 2.11 capability-fragment（能力片段）

| 项 | 内容 |
|---|---|
| **定义** | 跨案例重复出现的「通用能力 / 组件型功能」标准片段库。生成 `function-description` 时，组件型 / 通用型功能**优先引用片段而非重写**；每个片段可追溯到来源案例。片段自带 ≥3 条标准 BR 兜底（满足规则密度要求）。 |
| **出现位置** | `src/shared/capability-fragments/README.md`（使用约定 / 片段清单）；`src/shared/capability-fragments/{subscription-notice,comment-validation,time-picker}.md`（片段本体）。 |
| **相关校验器** | 无独立校验器（纯 Markdown 知识库）；片段被复制进产物后，产物仍走既有 gate 校验（`validate_artifact.py` / `property_check.py`）。 |
| **示例** | `time-picker.md`（时间/年月选择组件，4 BR / 3 AC / 2 EX，来源 REQ-008-bae FUN-009）。 |

---

## 三、关联术语（次要但常用）

> 以下术语在 framework 文档中高频出现，一并收录以保持术语一致性；详细语义以引用文件为准。

| 术语 | 定义 | 权威位置 |
|---|---|---|
| `knowledge_state`（知识状态） | 六态标签：`FACT` / `DECISION` / `ASSUMPTION` / `AI_INFERENCE` / `UNKNOWN` / `CONFLICT`。只有有来源的事实与已记录的人工决定可视为 confirmed 业务真相。 | `src/framework/contracts.md`（Knowledge States） |
| `SourceRecord`（来源记录） | 来源 ID / 位置 / 类型 / 提供者 / 时间 / 适用范围。 | `src/framework/contracts.md`（Shared Records） |
| `QuestionRecord`（问题记录） | 问题 / AI 初判 / 依据 / 选项 / 影响 / 责任人 / 回流点。 | `src/framework/contracts.md`（Shared Records） |
| `DecisionRecord`（决定记录） | 决定 / 备选项 / 决策人 / 理由 / 时间 / 影响范围。 | `src/framework/contracts.md`（Shared Records） |
| `ChangeRecord`（变更记录） | 变更类型 / 目标 / 原因 / 来源 / 下游影响。 | `src/framework/contracts.md`（Shared Records）；`src/shared/change-management/` |
| `TraceabilityLink`（追溯链接） | 源 ID / 目标 ID / 关系类型 / 证据位置。 | `src/framework/contracts.md`（Shared Records） |
| `authorized-reviewers.json` | 授权评审人清单（id / name / roles），`confirmed` 的唯一合法 reviewer 来源。 | `requirements/REQ-XXX/00-input/authorized-reviewers.json`；`src/scripts/pipeline.py` `load_authorized_reviewer()` |
| `reviewer_roles` | work_item 允许的评审角色集合（registry 定义），reviewer 角色必须命中。 | `src/framework/workflow-registry.json` `work_items[*].reviewer_roles` |
| `active 态` | 集合 `{needs_user_input, conditional_review, ready_for_human_review}`；单 active 约束 + 上游未 confirmed 即越级（越级待审）。 | `docs/状态语义矩阵.md` §2.4；`src/scripts/orchestrator.py` |
| `DoR / DoD` | Definition of Ready / Done：work_item 送审前的硬门禁（材料、知识状态、阶段收口）。 | `src/scripts/dor_check.py`；`src/framework/governance.md`（Stage Closeout） |
| `reflow`（回流） | 变更后从最早受影响 work_item 重跑；`pipeline.py reflow --apply` 将下游 confirmed 翻转 superseded。 | `src/scripts/pipeline.py`；`src/shared/change-management/reflow-templates/reflow-record.md` |
| `Inquiry Gate`（询问闸门） | 每个分支 / 产物的「默认行为 vs 覆盖」询问机制。 | `src/framework/governance.md`（Human-In-The-Loop Inquiry Contract） |
| `stage_closeup`（阶段收口） | `ready_for_human_review` 送审前强制：issue-record 收口行 + 待确认同行引用。 | `src/scripts/dor_check.py`；`src/framework/governance.md`（Stage Closeout） |
| `record_sha256`（记录自指纹） | ReviewRecord 正文（除自身行）的 SHA-256，用于防「artifact + ReviewRecord 同步篡改」。 | `src/scripts/hash_anchor.py` `record_body_sha256()` |
| `.hash-anchor.jsonl`（外部锚点链） | `99-review/` 下的 append-only 锚点链，提供篡改可检测的外部参照。 | `src/scripts/hash_anchor.py` |

---

## 四、不在术语表内的边界

以下内容**明确不收录**进本术语表，避免脚手架被具体案例污染（对应「案例污染」问题）：

1. **具体案例词**：RSVP、FSN、WeCom、WFJ、OAB、showmp、insidemp、bae、service-account、香奈儿、CCE、Lion、Apollo、TKU、By Session 等——它们是三份飞书文档中的真实项目词，不是脚手架核心术语。
2. **具体案例 ID**：`REQ-001`~`REQ-008`、`BG-RSV-2026S`、`FUN-005`、`BR-018`、`SRC-001` 等具体编号——它们是案例数据，随案例变化，不进入脚手架本体术语表。
3. **下游交付物术语**：开发计划、测试用例、运维手册等——宪法第 5 条 PRD-only scope 明确这些属于下游，不在脚手架术语范围。
4. **外部产品 / 工具名**：Figma、飞书、Mermaid、lark-cli 等——它们是脚手架调用的外部工具，不是脚手架自身概念（如需可另建「外部依赖清单」文档）。

> 判断标准：**凡是不理解该词就无法理解脚手架自身机制**的，收录；**凡是某个具体需求案例才出现的词**，不收录。本术语表只收录脚手架本体概念。

---

## 五、术语使用约定

1. **产物正文**：写 `prd.md` / `function-description.md` 等产物时，核心术语（work_item / artifact / confirmed / superseded / branch 等）按本文档定义使用，不得自造同义词。
2. **文档引用**：framework 文档与本文档互相引用时使用相对路径（如 `src/framework/contracts.md`），与现有文档风格一致。
3. **校验器命名**：术语对应的校验器命名（`branch_validator` / `property_check` / `dor_check` / `orchestrator` / `traceability_check` / `hash_anchor`）与本文档一致，不引入别名。
4. **新增术语**：新增核心术语时，先在本文档登记（定义 / 出现位置 / 相关校验器 / 示例），再在 framework 文档与代码中落地，避免术语漂移（遵循「状态枚举单源」精神）。
5. **案例词隔离**：任何示例一律使用占位符（`REQ-NNN-<topic>` / `<example>` / 通用业务词），不直接套用具体案例词（避免案例污染）。

---

## 六、维护与更新

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.1 | 2026-08-14 | 首版术语表，沉淀自 `src/framework/*.md`、`src/framework/workflow-registry.json`、`docs/状态语义矩阵.md` 与既有代码行为 |

---

## 附：证据文件索引

| 证据 | 位置 |
|---|---|
| 宪法六条 | `src/framework/constitution.md` |
| 知识状态 / 产物状态 / Shared Records / Confirmation Invariant | `src/framework/contracts.md` |
| Quality Sequence / Confirmation / Inquiry Contract / 主干分支 / Stage Closeout | `src/framework/governance.md` |
| Backbone / Work-Item Cycle / Entry And Exit | `src/framework/workflow.md` |
| 状态语义矩阵（simulated / confirmed / superseded 等） | `docs/状态语义矩阵.md` |
| work_item / artifact / reviewer_roles / support_capabilities | `src/framework/workflow-registry.json` |
| frontmatter 字段 / 状态枚举 / upstream_artifact_ids | `src/templates/_frontmatter-schema.md` |
| machine_gate / review / reflow / --decision | `src/scripts/pipeline.py` |
| confirmed hash 绑定 / 锚点校验 | `src/scripts/branch_validator.py` |
| rule_density / 逻辑完备性 | `src/scripts/property_check.py` |
| record_sha256 / .hash-anchor.jsonl | `src/scripts/hash_anchor.py` |
| 能力片段库 | `src/shared/capability-fragments/README.md` |
