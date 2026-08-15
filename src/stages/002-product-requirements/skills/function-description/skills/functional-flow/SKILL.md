---
name: functional-flow
description: 功能流程（主流程/分支/异常流程）。把已确认的功能清单（FEA）组织为主流程、分支流程、异常流程的可执行流程结构，以 Mermaid 呈现并回溯到已确认故事。Sub-skill of function-description，填充 §功能流程。
---

# Functional Flow · 功能流程

## Purpose And Boundary

为每个已确认功能 `FEA-XXX` 产出**功能流程结构**：从业务起点出发的主流程步骤序列、在决策点的分支流程、以及异常/失败情况下的异常流程与回退目标。功能流程描述的是**业务/功能如何被走通**——谁触发、依次执行哪些业务步骤、在什么条件下分叉、异常时去向哪里——而非页面/交互表达。每个流程必须回溯到已确认的功能（`FEA-XXX`）与故事（`ST-XXX`），使 `business-rules`、`state-machine`、`exception-handling` 等下游子技能能在真实步骤上挂接规则与细节。

**Do not** 设计页面布局（page-design）、写交互规则（`IX-*`）、定义业务规则（`BR`/`VL`/`AC`）、展开状态机明细（`STATE-*`）、或输出异常处理明细表（`EX-*`）。异常流程在本 Skill 只画**结构**（异常分支与回退目标）；异常处理的系统行为/恢复方式/用户提示归 `exception-handling`。一个流程步骤可以标注跨系统交接，但边界决策本身在上游。

## Inputs And Outputs

Inputs: confirmed `user-journey-and-stories` artifact（故事 `ST-XXX`、范围基线、角色、生命周期）与父级 function-description 的功能清单（`FEA-XXX`，含 P0/P1/P2 优先级）。Output: 父级 `function-description.md` 的 **§功能流程** 章节（主流程 / 分支流程 / 异常流程）——不是独立产物。章节布局遵循 `src/templates/stage-2-product/function-description.md`。

Load `references/thinking-framework.md`（引用 `src/framework/thinking-core.md` §1 强制透镜）再分析。Draft 前加载 `references/output-contract.md`。交接前加载 `references/audit-checklist.md` 与 `references/reviewer-checklist.md`。Review 前运行 `scripts/validate_artifact.py <function-description.md> --json`。分支/异常路径模糊时加载 `references/question-patterns.md`。

## Thinking Prompts (per stage)

### 1. Preflight
- "哪些 FEA 是 P0？各对应哪些故事与生命周期阶段？范围基线是否已确认？"
- Verify upstream: 每个流程的 FEA 必须存在于功能清单，且回溯到 ≥1 条已确认 `ST-XXX`。
- **若功能清单或 P0 列表缺失**，返回 routing receipt 并 STOP——不凭空发明流程。
- Assess density: L1（一句话、无流程材料）→ L2（功能清单存在）→ L3（故事 + 角色 + 生命周期）→ L4（上游已确认）。

### 2. Intake
- "上游材料到底怎么描述业务被走通——而不是我脑中想象的流程？"
- 逐字摘取起点、业务步骤、分支条件、异常与出口，再结构化。
- 每条流程声明按 `src/framework/contracts.md` 归类为 `FACT` / `DECISION` / `ASSUMPTION` / `AI_INFERENCE` / `UNKNOWN` / `CONFLICT`。
- 为使流程完整而补的步骤必须标 `AI_INFERENCE`，绝不静默当作已确认。

### 3. Think (apply thinking-core.md §1 mandatory lenses)
- **First Principles**: "用户/系统实际执行的可观察业务步骤是什么？哪些步骤被假设但未陈述？"
- **Systems Thinking**: "此流程是否跨系统/模块边界、另一角色的触点、或外部依赖？"
- **Adversarial**: "是否存在被忽略的替代入口或触发条件？这条分支业务上真的会发生吗？"
- **Reverse Validation**: "从终点/出口反向，每个步骤必须满足什么前置，流程才完整？"
- **Confirmation Bias Defense**: "我是不是只画了需求方口头的主流程，没有独立质疑分支与异常路径？"
- **Knowledge Boundary**: "哪些步骤是已确认事实，哪些是我的结构推断？"

### 4. Clarify
- 先尝试自行消解可发现的缺口（复查故事原文、角色、生命周期）。
- 剩余问题批量提交：AI 初步判断、依据、选项、影响、owner、阻断标志。
- 当答案改变某 P0 流程的起点、步骤、分支或异常路径时，**停在 `needs_user_input`**。
- Limit: 每轮 ≤5 个问题，按影响排序。不问页面布局或交互细节（下游技能）。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
- 每个 P0 FEA 画一张 Mermaid 图，覆盖 起点 → 主流程步骤 → 分支 → 异常 → 出口/终止。
- 分支流程：每条分支标注具体判定条件，互斥且可穷举。
- 异常流程：异常/失败分支与回退目标显式画出（虚线或标注）。
- 图标题引用 `FEA-XXX` 与 `ST-XXX`。
- Status: 用 `draft`、`needs_user_input` 或 `conditional_review`——**永不 `confirmed`**。

### 6. Audit
- **Completeness**: 每个 P0 FEA ≥1 张主流程图；主/支/异常路径齐全。
- **Branch Soundness**: 分支条件已标注、互斥、穷举。
- **Traceability**: 每个步骤回溯到 FEA/ST；无孤儿步骤。
- **Downstream Usability**: business-rules / state-machine / exception-handling 能否从这些步骤枚举挂接点？
- 运行 `scripts/validate_artifact.py <function-description.md> --json`，修复所有 error；warning 在审计记录中说明。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
Present: 每个 FEA 的主/支/异常流程摘要、已覆盖的路径、分支条件、异常回退目标，以及所有标 `AI_INFERENCE` 的步骤。
**产品负责人确认流程完整性；业务负责人确认分支条件与异常回退。** 批准产生 ReviewRecord（SHA-256）。

### 8. Commit / Reflow
- 只有 `pipeline.py review --decision approve` 可写入 `confirmed`。
- 变更时：记录 delta → 更新受影响流程图 → 重跑 Audit → 返回 Human Gate。
- 起点的改变或分支条件的改变会使下游 business-rules / state-machine / exception-handling 失效 → 从头进入本 Skill 重跑，而不是打补丁。

## Anti-Patterns

| ❌ Don't | ✅ Do |
|---|---|
| 每个 FEA 只画一条 happy path | 覆盖主流程 + 分支流程 + 异常流程 |
| 分支箭头不标条件 | 每条分支标注具体、可测的判定条件 |
| 把"填写并提交"压缩成一个方框 | 把复合动作拆成真实、可执行的业务步骤 |
| 跳过异常路径（"开发自己会处理"） | 画出每条异常分支与回退目标 |
| 加入已确认功能清单之外的步骤 | 每个步骤回溯 FEA-XXX / ST-XXX，否则标 AI_INFERENCE |
| 把跨系统交接画成普通节点 | 标注系统边界与失败回退目标 |
| 在流程图中写页面布局 / IX / BR / STATE / EX 明细 | 流程停在结构层；细节路由到对应子技能 |

## Example: Sufficient Input → Sufficient Output

**Input**: 已确认功能清单 + 故事（如 "场地预约" FEA-001 P0、"查询场地" ST-003），含范围基线与角色。
**Output**: 每个 P0 FEA 一张 Mermaid 功能流程图——主流程（选日期→选时段→填信息→确认提交）、分支流程（名额满→改期/排队、未登录→先登录再回跳）、异常流程（支付失败→重试/取消回退、库存不足→回选时段），分支条件可测、异常回退明确。

## Example: Sparse Input → Degraded Output

**Input**: 一行 Slack "我们想让大家能在线上报名活动，流程还没想好。"
**Output**: Intake 登记来源 → Preflight 判 L1 → Think 列出缺失材料（起点? 步骤? 分支条件? 异常路径? 出口?）→ Clarify 批量 ≤5 个问题（各含 AI 初步判断 + 选项 + owner）→ 停在 `needs_user_input`。不从空白发明任何流程。

## Load References

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见反模式（画功能流程时对照规避） | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/output-contract.md` | §功能流程 产出结构与 ID 契约 | Draft 前 |
| `references/question-patterns.md` | Clarify 提问模板（8 类句式） | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单（Human Gate 用） | Human Gate 前 |
| `references/source-handling.md` | 上游追溯规则（FEA-/ST-/SRC- 引用） | Intake/追溯时 |
| `references/thinking-framework.md` | 思考透镜（Common Core + 功能流程领域 lens，必读） | 每次任务开始（必读） |

## Completion

All P0 FEA 具备覆盖 起点 → 主流程 → 分支流程 → 异常流程 → 出口 的 Mermaid 功能流程图；主/支/异常路径完整；每条分支条件标注且互斥穷举；每个步骤回溯到已确认功能/故事；流程停在结构层，不泄漏布局、交互或业务规则细节；Mermaid 语法可渲染；在下游子技能启动前，授权人工已批准这些功能流程。
