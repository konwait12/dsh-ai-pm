# Output Contract · Requirement Restate（双模式能力）

## 目的（Purpose）

本 skill 是**能力（`output_kind=process`）**：产物是过程记录，**不进 PRD 正文**。两条产物线：

- **模式一「需求复述」**：`requirement-restate.md` —— 共享理解检查点（shared-understanding checkpoint），非需求文档。
- **模式二「发散收敛」**：`brainstorming-output.md` —— 发散候选 + 人工处置的过程记录，非正式产物且**永不产 `confirmed`**。

## Artifact States（两模式共用）

| 状态 | 含义 | 下游使用 |
|---|---|---|
| `draft` | 初始收集；Audit 未完成 | 否 |
| `needs_user_input` | CONFLICT / UNKNOWN 阻断，或答案会实质改变候选集/处置选项 | 否 |
| `conditional_review` | 已知晓非阻断未知，可审 | 否 |
| `ready_for_human_review` | 自审通过；待 stakeholder 确认（模式一）/ 待人工四值处置（模式二） | 否 |
| `confirmed` | 模式一：原 stakeholder 显式确认；**模式二：本记录不允许** | 模式一是 |
| `superseded` | 被新 confirmed 版本取代 | 否 |

> 模式二记录永远不产 `confirmed`：人工的 `include` 决策流入 `project-background-goal` 输入包，只有 `pipeline.py review --decision approve` 可确认下游工作项本身。

## 版本规则（Version Rules）

- 起 `v0.1`；人工要求修订时递增 minor。
- 首次 confirmed 为 `v1.0`（仅模式一适用）。
- 跨阶段引用时使用 RR-XXX（模式一）/ SCN-XXX（模式二）；版本变更记录在 `## 版本变更摘要`。

## Knowledge-State Labels（两模式共用）

`FACT` / `DECISION` / `ASSUMPTION` / `AI_INFERENCE` / `UNKNOWN` / `CONFLICT`

- 模式一：每条重述标 6 态之一。
- 模式二：发散候选**唯一允许** `AI_INFERENCE`；未处置前不得升级为 FACT；仅在有 SRC-* 材料时可出现 FACT。

---

## 模式一 · 需求复述（RR-NNN）

### 必需章节（Required Sections）

| § | 标题 | Required |
|---|---|---|
| 1 | 项目元数据 | Yes |
| 2 | 来源清单（SRC-IDs） | Yes |
| 3 | 重述需求清单（RR-XXX） | Yes |
| 4 | 冲突清单（CONFLICT → ISS-XXX） | Yes |
| 5 | 未知清单（UNKNOWN → Q-XXX） | Yes |
| 6 | stakeholder 自查反馈位 | Yes |
| 7 | 来源追溯 | Yes |
| 8 | 待确认问题 | Yes |
| 9 | Constitution Compliance | Yes |

空章节用 `待确认` 占位，不删除标题。

### 重述行 Schema（Restate Row Schema）

| 字段 | 必填 | 说明 |
|---|---|---|
| `RR-NNN` | Yes | 单调递增，本 artifact 内唯一 |
| `restated` | Yes | 用 stakeholder 的话重述（避免翻译损耗） |
| `original_phrase` | Yes | stakeholder 原始措辞（保留方言、口语） |
| `source` | Yes | SRC-ID（具体到段落/时间戳） |
| `knowledge_state` | Yes | 6 态之一 |
| `stakeholder` | Yes | 谁提出 |
| `confidence` | Yes | high / medium / low |
| `solution_leak` | Optional | 标记是否意外夹带方案（要求复审） |

### 模式一 · 内嵌于契约的反模式（Anti-Patterns Embedded In Contract）

- 出现"应该怎么设计"→ invalid，要求改写
- 多需求塞一行 → 拆 RR-NNN
- 解决方案混入 restate → 标记 `solution_leak=true`，需 stakeholder 重新确认

---

## 模式二 · 发散收敛（SCN-XXX）

### Candidate Table Contract（候选表 SCN-XXX）

材料稀疏/L0 时按 12 维度发散（lifecycle / roles / normal-alternate-exception-failure-timeout / permission / data condition / handoff / dependency / cancellation / retry / rollback / change-recovery / constraint），聚类去重后每个独立想法一个稳定 ID `SCN-001`, `SCN-002`, …。

| 列 | 内容 | 规则 |
|---|---|---|
| Candidate ID | `SCN-XXX` | 单调递增，去重后编号，不随排序变化 |
| 发散维度 | 12 维度之一（lifecycle / roles / normal-alternate-exception-failure-timeout / permission / data condition / handoff / dependency / cancellation / retry / rollback / change-recovery / constraint） | 主维度 |
| Candidate | 候选内容一句话 | 单一诉求，不塞多条 |
| Evidence | 为什么 AI 这么想 | 引用原始想法原文 / SRC-* / 常识推断；不得为空或占位 |
| Impact | 若纳入会产生什么影响 | 面向后续旅程/功能/范围的影响；不得为空或占位 |
| 知识状态 | `AI_INFERENCE` | 全表统一；未处置前不得升级为 FACT |

> 12 维度列表与发散提问的权威来源：`src/shared/brainstorming/SCENARIO_EXPANSION.md`（仍存在，未随支持目录删除）。

### Disposition Table Contract（人工处置表 · 8 列）

处置表有 **8 列**——在 `src/shared/brainstorming/rediscovery-templates/scenario-disposition.md` 中约定的规范形态：

| Candidate ID | Role-Lifecycle | Candidate | Evidence | Impact | Human Disposition | Reason | Write-back Target |
|---|---|---|---|---|---|---|---|
| `SCN-001` | 维度/阶段 | 候选内容 | 依据 | 影响 | include / exclude / defer / research | 原因 | 写回目标 |

Rules:

- **Human Disposition** 是四值之一：`include` / `exclude` / `defer` / `research`。AI 填其余所有列；**只有负责人工填这一列**。
- `include` → 候选进入正式产物；**必须**给出非占位的 Write-back Target（写回 `project-background-goal` 输入包的哪个段：§生命周期线索 / §角色候选 / §约束候选 …）。
- `exclude` → 排除；Reason 必须说明排除原因。
- `defer` → 暂缓；Reason 给出触发条件或计划周期。
- `research` → 待调研；登记 issue-record / QuestionRecord，不静默搁置。

### 写回契约（Write-back Contract，模式二）

- 只有 `include` 候选被写回，且**只**写回 `project-background-goal` 输入包（综合为 ≥ 50 字的充分输入）。
- 写回包必须是朴素的输入需求（要探索什么），而不是设计好的方案。
- 写回后，work item 在 `project-background-goal` 恢复（registry `resume_work_item`）。

### Human Responsibilities（模式二）

- Business owner：处置每个候选（`include` / `exclude` / `defer` / `research`），确认写回目标。
- Product manager：检查发散覆盖、证据质量、输入包对下游的可用性。

---

## 两模式共用契约

### Clarifications Session 契约（Clarifications Session Contract）

`## Clarifications` 一行一 session，≤5 sessions；`accepted_answer` 在 `ready_for_human_review` 前必填。每次 session：`CL-NNN` 单调编号；AI 初判 + 选项 + 影响 + owner + blocking；≤5 问题/轮；答案回写进候选表/处置表/重述清单对应行。未知答案成为普通 QuestionRecord / issue-record 条目，不额外开分支。

### 下游交接（Downstream Handoff）

restate 通过后产出的合并体进入 issue-record 的 INF/CLS/CONFLICT 区（模式一），以及 `project-background-goal` 输入包（模式二）：

```text
mode                        # rr / scn
trigger_signal              # 多源歧义 / 单源歧义 / L0 仅想法 / 材料稀疏
confirmed_version
rr_count                    # 模式一
scn_count                   # 模式二
divergence_coverage         # 模式二：12 维度扫描摘要
conflict_count              # 模式一
unknown_count               # 模式一
solution_leak_count         # 模式一
included_candidates         # 模式二：仅 include 项
deferred_candidates         # 模式二：defer 项 + 触发条件
research_items              # 模式二：research 项 + issue-record 引用
input_package               # 模式二：≥50 字综合输入（交付 project-background-goal）
stakeholder_signed          # 模式一
source_ids
```

### Anti-Patterns Embedded In Contract（两模式）

- 出现"应该怎么设计"→ invalid，要求改写
- 多需求/多候选塞一行 → 拆 RR-NNN / SCN-XXX
- 解决方案混入 restate → 标记 `solution_leak=true`，需 stakeholder 重新确认
- 模式二记录状态到达 `confirmed` → invalid（过程记录止步 `ready_for_human_review`）
- 处置表缺 Human Disposition 或 `include` 行缺 Write-back Target → invalid
