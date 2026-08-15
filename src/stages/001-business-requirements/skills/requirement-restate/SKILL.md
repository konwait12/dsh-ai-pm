---
name: requirement-restate
description: 需求重举能力（复述 + 发散收敛，双模式）。模式一「需求复述」（RR-NNN）：用 stakeholder 原话 verbatim 重述确认，冲突路由 issue-record（CLS）、未知路由 Q-XXX（INF）；模式二「发散收敛」（SCN-XXX）：材料稀疏/L0 时按 12 维度发散候选，人工四值处置（include/exclude/defer/research），仅 include 候选写入 project-background-goal 输入包。本 skill 是能力（output_kind=process），产物为过程记录，不进 PRD 正文。Use when stakeholder language is ambiguous, multiple sources use different terms for the same thing, a "do we really agree on what you asked for?" checkpoint is required, or the ask exists only as a thin one-line idea at L0.
---

# Requirement Restate（需求重举 · 复述 + 发散收敛双模式能力）

## 目的与边界（Purpose And Boundary）

本 skill 是**能力（`output_kind=process`）**，不是产物型 skill：它产出的过程记录（RR 重述清单 / SCN 发散候选与人工处置表）**永远不进 prd.md 正文**，只作为「共享理解检查点」与「收敛后输入包」喂给后续工作项。注册表 `workflow-registry.json` 已将其标记为 `output_kind: process`。

按输入成熟度自动选择运行模式：

- **模式一「需求复述」RR-NNN**：原始需求可追溯（L1-L4，至少存在口头或书面来源）时，用 **stakeholder 原话 verbatim** 逐条复述确认，建立共享理解检查点。矛盾标 `CONFLICT` → 路由 `issue-record`（CLS 类别）；未知标 `UNKNOWN` → 路由 `issue-record` Q-XXX（INF 类别）。
- **模式二「发散收敛」SCN-XXX**：材料稀疏 / L0（仅一行想法）时，按 **12 个场景维度**发散候选（lifecycle / roles / normal-alternate-exception-failure-timeout / permission / data condition / handoff / dependency / cancellation / retry / rollback / change-recovery），聚类去重后编号 `SCN-XXX`、全部标注 `AI_INFERENCE`，交人工 **四值处置**（`include` / `exclude` / `defer` / `research`），**仅 `include` 候选**综合成 ≥50 字输入包写入 `project-background-goal` 输入包。

**Do not**（两模式通用）：不发明业务事实、不替 stakeholder / 负责人做处置决定、不把发散候选当已确认需求、不让过程记录本身到达 `confirmed`。模式一不在此解决冲突（只标记并路由到 issue-record）；模式二不把候选直接写回正式产物（只有 `include` 进输入包）。

**PRD 归宿**：❌ **永远不进 PRD 正文**。本 skill 是分析过程（Analysis Process），产物是过程记录。模式一确认通过后：重举通过的需求行进入 `project-background-goal` 和 `user-journey-and-stories` 草案；CONFLICT → `issue-record` ISS-XXX（CLS 类别）；UNKNOWN → `issue-record` Q-XXX（INF 类别）。模式二确认后：仅 `include` 候选综合为输入包进入 `project-background-goal`。`requirement-restate.md` / `brainstorming-output.md` 过程记录本身永远不进入 prd.md 正文。

**本 Skill 属于 Branch**（参见 `src/framework/governance.md` §Human-In-The-Loop Inquiry Contract）。`prd-assembly` 进入 §0 上游清单时会**主动询问**"要不要在 §0 标注 requirement-restate 来源链"——若 stakeholder 显式要求可追溯到 restate，则 §0 加一行 RR-XXX / SCN-XXX 摘要；否则不出现。触发条件：原始需求被多团队/多语言/多源转述、多源术语不一致、误读代价高（合规/法律/昂贵构建）、需要正式的"我们真的同意了吗"检查位、新 stakeholder 加入需重新锚定、材料稀疏到无法进入主干（L0）。

## 输入与输出（Inputs And Outputs）

Inputs:
- Original source materials（meeting minutes, emails, BRD, audio/video transcripts, chat, tickets）——模式一必需；模式二存在时也登记
- L0 原始想法 / 稀疏材料（模式二：仅一行想法即可触发）
- Background artifact（`background-goal.md`，如有）
- 范围基线（journey 的 §范围基线，如有）
- The full chain of prior conversation（chat, ticket, ticket comments）

Output（均为**过程记录**，非 PRD 产物）:
- 模式一：`requirement-restate.md`（§1-§9，RR-NNN 重述清单 + CONFLICT→ISS / UNKNOWN→Q 路由），模板 `assets/requirement-restate-template.md`
- 模式二：`brainstorming-output.md`（SCN-XXX 候选表 + 8 列人工处置表 + 收敛后输入包），模板 `src/templates/others/brainstorming-output.md`

Load `references/thinking-framework.md`（Common Core + 领域 lens + 12 维度发散 lens）before analysis. Load `references/output-contract.md`（RR 行契约 + SCN 候选表 / 处置表契约）before drafting. Load `references/audit-checklist.md` and `references/reviewer-checklist.md` before handoff. Load `references/source-handling.md` during Intake when登记 SRC-*。Run `scripts/validate_artifact.py <artifact> --json` before review.

## 思考提示词（按阶段）（Thinking Prompts per stage）

### 1. Preflight
- **选模式**：有可追溯来源（L1+）→ 模式一（RR-NNN）；L0 仅想法 / 材料稀疏 → 模式二（SCN-XXX）；多源歧义 → 模式一（先收敛来源）。若同时材料稀疏且多源歧义，先模式一收敛来源，再由模式二补全未知维度。
- 模式一："stakeholder 实际说了什么，用他们自己的话？""我们依据哪些来源重述？有没有未被转写的音频/视频/聊天？"识别：项目名、项目 ID（REQ-XXX）、stakeholder(s)、来源。为每个来源登记 SRC-ID。评估成熟度：L0（无源）→ L1（单条口头表述）→ L2（单源书面）→ L3（多源一致）→ L4（多源冲突，需消歧）。
- 模式二："Is this L0 (idea only) or thin material? What is the stuck point? What is the evidence boundary?" 确认触发：L0 → 模式二；多源歧义 → 模式一；材料充分 → 直接进入 `project-background-goal`。确认负责处置的人工（business_owner）与证据边界。
- **如果无来源且诉求只是记忆转述（模式一）/ 想法为空或无法识别负责人工（模式二）→ 返回路由回执并在 `needs_user_input` 停下。**

### 2. Intake
- 两模式通用：verbatim 保留原始措辞（方言、口语、术语照抄），不翻译成"我们以为的意思"。
- 模式一："每个来源实际上说了什么——不是我认为它是什么意思？"逐源提取候选需求；跨源合并重复项（同一诉求、不同措辞）并注明；矛盾标 `CONFLICT`（**不解决，只标记**）；每条标知识状态：`FACT` / `DECISION` / `ASSUMPTION` / `AI_INFERENCE` / `UNKNOWN` / `CONFLICT`；登记 SRC-*。
- 模式二：捕获原始想法原文作为证据基础（纯 L0 无源时明示"其余皆为推断"）；若有材料（消息/邮件/纪要）按 `references/source-handling.md` 登记 SRC-*。

### 3. Think (apply thinking-core.md §1 mandatory lenses + 模式专属 lens)
- **First Principles**: "剥离所有提议方案后，这个诉求/想法本身是什么？"
- **Systems Thinking**: "这个诉求/想法是否隐含一个也在推进中的上游/下游系统？涉及哪些角色、数据、流程？"
- **Role Perspective**: "stakeholder 能否在重述里认出他们自己的话？（模式一）/ 对每个可能角色——他们获得什么、失去什么、需要什么？（模式二）"
- **Constraint Analysis**: "stakeholder 在诉求里嵌入的硬约束（时间/预算/平台/合规），我们是否不能静默移除？"
- **Adversarial**: "最糟糕的误读方式是什么？重述/候选是否防御了这种误读？"
- **Reverse Validation**: "如果 stakeholder 只读重述，他们看到的正是他们想说的吗？（模式一）/ 从想要的结果倒推，什么必须先成立？（模式二）"
- 模式二额外：**12 维度发散 lens**（lifecycle/roles/normal-alternate-exception-failure-timeout/permission/data condition/handoff/dependency/cancellation/retry/rollback/change-recovery，见 `references/thinking-framework.md`）→ 聚类去重后每个独立想法得稳定 ID `SCN-XXX`。

### 4. Clarify
- 模式一：每个 `CONFLICT`：列出双方措辞，路由给 stakeholder 选择（含 AI 初判 + 选项 + 影响 + owner）。每个 `UNKNOWN`：请 stakeholder 补全。Batch questions：≤5 per session，按影响排序。
- 模式二：批量提问带 AI 初判 + 证据 + 选项 + 影响 + owner + blocking flag；答案会实质改变候选集或处置选项时 **STOP at `needs_user_input`**。Limit ≤5 questions per session，按影响排序。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 `issue-record`（问题清单）并更新 §13 收口表；送审前 dor_check 会硬检查收口与引用。
- **当冲突或未知会改变诉求本身 / 当答案会实质改变候选集或处置选项时，停在 `needs_user_input`**。

### 5. Generate
- 模式一：填模板 `assets/requirement-restate-template.md`。每条重述需求：ID（`RR-NNN`）、重述（stakeholder 的话）、原始措辞（verbatim）、来源、知识状态、提出方、confidence。发现"方案泄露"（重述夹带方案）→ 标 `solution_leak=true`，需 stakeholder 重新确认。状态：使用 `draft`、`needs_user_input` 或 `conditional_review`——**绝不用 `confirmed`**。
- 模式二：填 SCN 候选表（全 `AI_INFERENCE`，每条含 Evidence 与 Impact）→ 8 列人工处置表（Disposition 留给人工）→ Include 项写回 → 收敛后输入包（≥50 字）。状态：使用 `draft`、`needs_user_input` 或 `conditional_review`——记录本身**永不** `confirmed`。

### 6. Audit
- **Source Coverage**（模式一）：每条 Intake 登记的 SRC-ID 都反映在重述清单中。
- **Atomicity**（两模式）：没有一行塞两个诉求 / 两条候选。
- **No Solution Leak**（模式一）：没有一行含方案/技术/设计。
- **Conflict Visibility**（模式一）：所有冲突被标记，未被解决。
- **Stakeholder Recognition**（模式一）：重述可原样发回给 stakeholder 且读起来忠实。
- **Completeness**（模式二）：12 维度全部扫过或显式跳过；每条候选带 Evidence + Impact。
- **Inference Discipline**（模式二）：每条候选标 `AI_INFERENCE`；无任何内容被当成事实。
- **Disposition Readiness**（模式二）：处置表就绪；每个 `include` 候选命名写回目标。
- 运行 `scripts/validate_artifact.py <artifact> --json`。修复所有错误。警告 → 记录进 audit notes。
- **B3 收口**（两模式）：确认 issue-record 的 §13 收口表已更新本 skill 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
- 模式一：Present 重述条数、冲突条数、未知条数、来源覆盖、audit 结果。**原 stakeholder（或其指定代理）必须确认重述。** 批准会创建带 SHA-256 的 ReviewRecord。
- 模式二：Present 发散覆盖摘要（哪些维度产出什么）、候选表（证据+影响）、每条候选的推荐处置、deferral risks。**只有负责人工（business_owner）可以处置**每个候选（`include` / `exclude` / `defer` / `research`）。写回批准会创建带 SHA-256 的 ReviewRecord。

### 8. Commit / Reflow
- 模式一：只有 `pipeline.py review --decision approve` 可以写入 `confirmed`。发生变更时：记录 delta → 重新 Audit → 重新校验 → 返回 Human Gate。这里浮现的冲突必须升级到 `issue-record.md` 解决，不在本 skill 内解决。
- 模式二：Write back **only `include` candidates** 综合为 ≥50 字充分输入，写入 `project-background-goal` 输入包，然后返回当前 Work Item。处置不完整或出现实质新想法 → 从 Preflight 重新进入本 skill，不补丁下游；写回后出现矛盾 → 重新进入而非静默修订目标产物。
- 两模式：过程记录本身最高 `ready_for_human_review`；只有 `pipeline.py review` 可确认下游工作项。

## 反模式（Anti-Patterns）

| ❌ 不要 | ✅ 要做 |
|---|---|
| 用自己的话重述诉求（模式一） | 用 stakeholder 的话；能引用就引用原文 |
| 隐藏来源（"业务方说要…"） | 始终引用 SRC-ID，具体到段落/时间戳 |
| 在重述阶段解决冲突（模式一） | 标 `CONFLICT` 并路由到 issue-record |
| 把 AI 推断当 stakeholder 原话（模式一） | 重述只含来源支持的内容，推断标 AI_INFERENCE |
| 把一行想法变成"事实"（模式二） | 保持全 `AI_INFERENCE` 直到人工处置 |
| 只在一个维度发散，如只看角色（模式二） | 扫全 12 维度（lifecycle/roles/normal-alternate-exception-failure-timeout/permission/data condition/handoff/dependency/cancellation/retry/rollback/change-recovery） |
| 出 40 条近似重复候选（模式二） | 聚类去重；一个独立想法一个 `SCN-XXX` |
| 替人工决定 include/exclude/defer/research（模式二） | 展示处置表；只有人工标记处置 |
| 让 `research` 静默搁置（模式二） | `research` 成为 issue-record 条目 / QuestionRecord 并被跟进 |
| 把 excluded 候选也写回（模式二） | 仅 `include` 候选进入输入包 |
| 让过程记录以 `confirmed` 交付 | 记录最高 `ready_for_human_review`；仅 `pipeline.py review` 可确认下游工作项 |

## Example: 模式一 · Sufficient Input → Sufficient Output

**输入**：3 个来源——一份会议纪要、一封跟进邮件、一条工单评论——都在描述同一个诉求。
**Output**: 完整 requirement-restate.md——
- 7 条重述需求（RR-001…RR-007），每条链接到来源。
- 1 个 CONFLICT：会议说"所有角色"，邮件说"仅经理" → 路由给 stakeholder 选择。
- 2 个 UNKNOWN：deadline 未指定、成功指标未指定 → 路由给 stakeholder 补全。
- 0 个方案：尽管会议提到"dashboard"，重述仅记为 hint，不当作决议。

## Example: 模式二 · Sparse Input → Divergence + Disposition

**Input**: L0 想法——"做客户邀约活动，名单约 500 人，预算 10 万，希望月底前上线"（无书面材料）。
**Output**: 12 维度发散 → 聚类去重到 5 个候选 → SCN 候选表（证据+影响，全 AI_INFERENCE）→ 8 列处置表（3 include / 1 defer / 1 research）→ include 写回输入包 ≥50 字 → `ready_for_human_review` → 输入包交给 `project-background-goal`。

## Example: Degraded Output（两模式通用稀疏降级）

**Input（模式一）**: 聊天消息 "make it faster for our VIPs"（无附件、无来源）。
**Output**: Preflight 判定 L1（单条口头表述，无源）→ 不进入 Generate/Audit → Clarify 批量产出：这是指哪个流程更快？VIP 的定义？"更快"的成功判据？当前耗时基线？——每条带 AI 初判 + 选项 + 影响 + owner → status = `needs_user_input`。

**Input（模式二）**: 消息 "想做客户邀约活动"（无更多信息）。
**Output**: Intake 登记消息为证据基础 → L0 判定 → 候选骨架（稀疏证据："AI 推断，无书面来源"）→ 3 个 Clarify 问题（活动目标 / 邀约对象范围 / 期望时间）→ 停于 `needs_user_input`，处置表待人工补齐。

## 加载参考文档（Load References）

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见反模式（重述 + 发散收敛） | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/output-contract.md` | 产物契约：RR-NNN 行 + SCN-XXX 候选表 + 8 列处置表 | Draft 前 |
| `references/question-patterns.md` | Clarify 提问模板（8 类句式） | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单（Human Gate 用） | Human Gate 前 |
| `references/source-handling.md` | 来源处理规则（SRC-* 登记与引用） | Intake/来源处理时 |
| `references/thinking-framework.md` | 思考透镜（Common Core + 领域 lens + 12 维度发散 lens，必读） | 每次任务开始（必读） |

## 完成标准（Completion）

- 模式一：每条来源里的诉求都用 stakeholder 的话重述；每行都有来源绑定与原始措辞；冲突全部标记并路由到 issue-record；未知全部路由给 stakeholder；原 stakeholder（或其指定代理）确认"是的，这就是我说的"。
- 模式二：L0/稀疏触发确认且证据边界明确；12 维度全部扫过或显式跳过；候选已聚类去重并拥有稳定 `SCN-XXX` ID；每条候选带 Evidence、Impact 与 `AI_INFERENCE` 标注；处置表可供人工四值处置（或已处置）；仅 `include` 候选综合为 ≥50 字输入包写入 `project-background-goal`。
- 两模式：issue-record §13 收口表已更新本 skill 行；过程记录从不进入 prd.md 正文；项目可进入 scope / journey / PRD 工作。
