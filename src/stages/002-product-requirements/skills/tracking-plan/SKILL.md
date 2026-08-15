---
name: tracking-plan
description: 埋点与追踪计划 — 为每个 P0 功能定义事件、属性、触发时机、上报时机、平台、PII 标记与关联指标/目标，产出数据团队与工程团队可直接落地的 `tracking-plan.md`。Use when a function needs data tracking or a PRD-side event contract.
---

# 埋点与追踪计划（Tracking Plan）

## 目的与边界（Purpose And Boundary）

为每个 P0 功能定义 **要追踪什么**，作为 PRD 侧的事件合约：事件、属性、触发时机、上报时机、平台、PII 标记，以及每个事件支撑的指标/目标。输出 `tracking-plan.md` 是数据团队与工程团队用于埋点的唯一事实来源，覆盖矩阵证明每个 P0 功能都有信号。

**不要**写 SQL 查询或分析实现代码、设计数据仓库表或 BI 看板、定义 A/B 测试方法论，或设定具体数值目标（那是上游 background-goal 设定的 G-X 目标）。

**PRD 归宿**：✅ **按需**。当 `prd-assembly` 进入 §5 按需章节时，AI 必须主动询问"要不要把 tracking-plan 的 EV-XXX 事件表聚合为 §5.2 埋点需求"。若业务方 / 数据团队 / 工程团队回答"要"，则 EV-XXX 事件表与属性字典 verbatim 进入 prd.md；若回答"不要"（如本项目无埋点需求），则 prd.md 不出现埋点章节，tracking-plan.md 作为过程证据存档于 `99-review/support/`。

**本 Skill 属于 Branch**（参见 `src/framework/governance.md` §Human-In-The-Loop Inquiry Contract），是 function-description 的子 Skill，在 business-rules / validation-rules / state-machine / exception-handling **confirmed 之后**调用、acceptance-criteria 之前调用。即使上游已 confirmed，仍需在 §5.2 询问是否显式暴露埋点合约。

## 输入与输出（Inputs And Outputs）

输入：
- 已确认的上游：function-description（FUN-XXX）、product-ux（IX-XXX）、business-rules（BR-XXX）、background-goal 目标（G-X）
- 已知平台（web / ios / android / miniprogram / server）

输出：`tracking-plan.md`，含 §1-§8 章节，使用模板 `templates/tracking-plan-output.md`，包括事件表（EV-NNN）、属性字典、覆盖矩阵、指标映射与 PII 寄存器。

分析前加载 `references/thinking-framework.md`（其中引用 `src/framework/thinking-core.md` §1 必用透镜 + 领域 lens）。起草前加载 `references/output-contract.md`。交接前加载 `references/audit-checklist.md` 与 `references/reviewer-checklist.md`。Intake 登记 SRC-* 时加载 `references/source-handling.md`。评审前运行 `scripts/validate_artifact.py <artifact> --json`。

## 思考提示词（按阶段）（Thinking Prompts per stage）

### 1. Preflight
- "上游哪些 P0 功能已确认？上线后哪些目标（G-X）必须可度量？"
- "谁拥有指标？哪些平台必须埋点？"
- **如果 function-description（FUN-XXX）或其上游规则未 confirmed，则 STOP** — 返回"上游未确认"路由收据，不进入 Intake。
- 登记每条上游产物引用。识别 metric_owner 与 data_owner。

### 2. Intake
- "对每个 P0 FUN-XXX——哪些用户动作必须可观测，才能证明功能生效且目标达成？"
- 从 FUN/IX/BR 逐条提取候选事件（page_view / click / submit / exposure / success / error / custom），登记来源引用（FUN-XXX / IX-XXX / BR-XXX）。
- 标知识状态：`FACT`（上游已确认）/'AI_INFERENCE'（由功能推导）/ `UNKNOWN`（触发时机不明）。

### 3. Think（应用 thinking-core.md §1 必用透镜）
- **First Principles**："每个事件能回答哪个业务问题？删掉它，指标是否仍可证明？"
- **Systems Thinking**："事件是否跨系统（server 端埋点 / 第三方上报）？谁负责采集与清洗？"
- **Role Perspective**："数据团队能直接照表埋点吗？工程团队知道何时上报吗？业务方知道指标怎么算吗？"
- **Constraint Analysis**："哪些事件受平台/合规/性能限制？PII 属性如何处理？"
- **Adversarial**："会不会有人用这个事件得出错误结论？漏斗/指标是否被歧义污染？"
- **Reverse Validation**："从 G-X 反推——要验证这个目标，必须有哪些事件和属性？"

### 4. Clarify
- 触发时机、属性口径、上报时机不明确时：批量提问（≤5 per session），带 AI 初判 + 选项 + 影响 + owner。
- 事件是否 `must_track` / `nice_to_track`、是否需要补充埋点——交 metric_owner 判定。
- **当答案会改变覆盖、事件合约或 PII 处理时，停在 `needs_user_input`**。

### 5. Generate
- 填模板。每个事件：ID（`EV-NNN`）、`event_name`（snake_case verb_noun，全局唯一）、event_type、FUN/IX/BR 引用、trigger_condition、properties（key/type/example/pii_flag/required）、upload_timing、platform、metric、goal、priority。
- 覆盖矩阵：每个 P0 FUN-XXX ≥ 1 个 `must_track`。
- 状态：使用 `draft`、`needs_user_input` 或 `conditional_review`——**绝不用 `confirmed`**（由 function-description 父 Skill 一并签发）。

### 6. Audit
- **Coverage**：每个 P0 FUN-XXX 至少 1 个 must_track 事件。
- **No Orphans**：每个事件都链接到 FUN-XXX 与 G-X；无孤立事件。
- **Naming Consistency**：同名事件已合并（不允许 `click_btn` 与 `button_click` 并存）；命名 snake_case verb_noun。
- **PII Discipline**：PII/sensitive 属性已标记并带保留期。
- 运行 `scripts/validate_artifact.py <artifact> --json`。修复所有错误。警告 → 记录进 audit notes。

### 7. Human Gate
呈现：must_track/nice_to_track 计数、覆盖矩阵、PII 事件清单、未映射事件、audit 结果。
**只有 metric_owner / data_owner + function-description 父 Skill 负责人可以批准。** 批准会创建带 SHA-256 的 ReviewRecord。

### 8. Commit / Reflow
- 只有 `pipeline.py review --decision approve` 可以写入 `confirmed`（通常随 function-description 一起签发）。
- 发生变更时：记录 delta → 重新 Audit → 重新校验 → 返回 Human Gate。
- 上游功能变更导致事件失效 → 回归最早受影响的 Work Item 重跑，不在事件表打补丁。

## 反模式（Anti-Patterns）

| ❌ 不要 | ✅ 要做 |
|---|---|
| 自动记录每个点击 | 只列能映射到指标/目标的事件 |
| 用 `click1` 这类无意义事件名 | 用 snake_case verb_noun：`checkout_submit_click` |
| 把多个动作塞进一个事件 | 一个用户有意义动作 = 一个事件 |
| 跳过 upload_timing | 明确 realtime / batch / session_end |
| 忘掉 G-X 链接 | 每个事件必须支撑一个业务目标 |
| 把 PII 当普通属性 | 明确 pii_flag 四档与保留期 |
| 在事件表里写 SQL/表结构 | 事件表只定义"报什么"，实现交给数据团队 |

## 示例：充足输入 → 充足输出（Sufficient Input → Sufficient Output）

**输入**：confirmed function-description 含 FUN-001「提交订单」、FUN-002「优惠券核销」+ G2「订单转化率」、G4「优惠券核销率」+ 各平台清单。
**输出**：完整 tracking-plan.md——
- FUN-001 的事件：`EV-001 order_submit_click`（click, IX-007, must_track, funnel_step, G2）、`EV-002 order_submit_success`（success, FUN-001, must_track, conversion, G2）、`EV-003 order_submit_error_invalid_coupon`（error, BR-012, must_track, counter, G2）、`EV-004 coupon_field_hover`（exposure, IX-007, nice_to_track, counter, G4）。
- 覆盖矩阵：FUN-001 / FUN-002 各有 ≥1 must_track；属性字典含 PII 标记（如手机号 `pii_flag=true` + 保留期）。

## 示例：稀疏输入 → 降级输出（Sparse Input → Degraded Output）

**输入**：一个 P0 功能描述但上游 business-rules / validation-rules 均未 confirmed（只有功能名）。
**输出**：Preflight 判定"上游未确认"→ 返回路由收据（需要先确认 FUN-XXX 及其规则）→ 不进入 Generate/Audit。若上游已确认但数据需求稀疏，则 Clarify 批量产出：要验证哪些 G-X？需要哪些事件与属性？哪些平台？PII 如何处理？→ status = `needs_user_input`。

## 加载参考文档（Load References）

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见埋点反模式（写产物时对照规避） | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/output-contract.md` | 产物结构与 ID 契约（EV-NNN） | Draft 前 |
| `references/question-patterns.md` | Clarify 提问模板（8 类句式） | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单（Human Gate 用） | Human Gate 前 |
| `references/source-handling.md` | 来源处理规则（SRC-* 登记与引用） | Intake/来源处理时 |
| `references/thinking-framework.md` | 思考透镜（Common Core + 领域 lens，必读） | 每次任务开始（必读） |

## 完成标准（Completion）

每个 P0 FUN-XXX 至少 1 个 must_track 事件；每个事件都链接到 FUN-XXX 与 G-X，无孤立事件；PII/sensitive 属性已显式标记并带保留期；命名一致（snake_case verb_noun）；数据团队与工程团队无需再澄清即可照表埋点。
