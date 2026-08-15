---
name: project-background-goal
description: Turn raw requirement materials into a sourced, human-confirmed business background and goal baseline before journey or product design begins.
---

# 项目背景与目标（Project Background And Goal）

## 目的与边界（Purpose And Boundary）

确立需求为什么存在、今天发生了什么、什么问题重要、涉及哪些人、预期达成什么结果，以及哪些约束或未知项会影响后续工作。

**不要**设计旅程、功能、页面、字段、API、架构或实现任务。业务方提供的产品方案是需要审视的证据，而不是理解业务需求的替代品。

## 输入与输出（Inputs And Outputs）

输入：已登记的来源材料（会议纪要、邮件、BRD、PPT、图片）以及可识别的业务事实/目标负责人。输出：`background-goal.md`，使用 `src/templates/resolver.py background-goal.md` 解析出的模板。

分析前加载 `references/thinking-framework.md`（其中引用 `src/framework/thinking-core.md` §1 必用透镜）。起草前加载 `references/output-contract.md`。交接前加载 `references/audit-checklist.md` 与 `references/reviewer-checklist.md`。评审前运行 `scripts/validate_artifact.py <artifact> --json`。当来源材料稀疏时加载 `references/elicitation-techniques.md`（访谈/观察主动采集）。

## 思考提示词（按阶段）（Thinking Prompts per stage）

### 1. Preflight
- "我有哪些来源？谁拥有业务事实？信息密度如何？"
- 为每个来源登记 SRC-ID。识别 business_fact_owner（业务事实负责人）与 goal_decision_owner（目标决策负责人）。
- **如果没有可用来源或事实负责人**，返回一张路由回执并 STOP——不要进入 Intake。
- 评估成熟度：L0（无来源）→ L1（单一稀疏来源）→ L2（已有业务方案）→ L3（定义良好）→ L4（上游已确认）。

### 2. Intake
- "每个来源实际说了什么——而不是我认为它是什么意思？"
- 在解读之前先逐字提取来源陈述。按 `src/framework/contracts.md` 将每条分类为 `FACT`、`DECISION`、`ASSUMPTION`、`AI_INFERENCE`、`UNKNOWN` 或 `CONFLICT`。
- 保留来源 ID 与位置。不要把不同来源的主张合并成一条陈述。

### 3. Think（应用 thinking-core.md §1 必用透镜）
- **第一性原理（First Principles）**："我们想改变的可观察结果是什么？哪些假设伪装成了需求？"
- **系统思维（Systems Thinking）**："哪些上游/下游系统、角色与数据会受影响？"
- **角色视角（Role Perspective）**："对每个识别出的角色——他们获得什么、失去什么、需要改变什么？"
- **约束分析（Constraint Analysis）**："硬约束（法律、平台、品牌、时间）有哪些？"
- **对抗性审视（Adversarial）**："任何主张的反面是否可能成立？什么证据能推翻它？"
- **逆向验证（Reverse Validation）**："从期望结果倒推，哪些条件必须成立？"

### 4. Clarify
- 对可发现的客观事实先尝试调研（文档、公开数据、系统日志）。
- 将其余问题批量呈现，附带：AI 初步判断、证据、选项、影响、负责人、是否阻断标记。
- **当某个答案可能改变问题、目标、角色、范围、成本、时间或风险时，停在 `needs_user_input`**。
- 数量限制：每轮 Session 至多 5 个问题，按影响排序。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
- 填充模板。叙述部分放入有来源依据的内容；不确定的内容放进显式寄存器（§6-§8）。
- 状态：使用 `draft`、`needs_user_input` 或 `conditional_review`——**绝不用 `confirmed`**。

### 6. Audit
- **完整性（Completeness）**：所有来源都体现了？所有角色都识别了？所有约束都列出了？
- **第一性原理**：我是否不小心写成了方案而不是问题？
- **来源保真度（Source Fidelity）**：每条主张是否都能追溯到一条来源陈述？
- **下游可用性**：journey-and-stories 能否无需重新调研就直接接续？
- 运行 `scripts/validate_artifact.py <artifact> --json`。修复所有错误。警告 → 记录进 audit notes。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
呈现：候选摘要、证据摘要（每条主张由哪些来源支撑）、未知项及其影响、所需决策、审计结果、变更摘要。
**只有业务事实/目标负责人可以批准。** 批准会创建带 SHA-256 的 ReviewRecord。

### 8. Commit / Reflow
- 只有 `pipeline.py review --decision approve` 可以写入 `confirmed`。
- 发生变更时：记录 delta → 更新受影响的章节 → 重新执行 Audit → 返回 Human Gate。
- 后续出现矛盾 → 从本 Skill 的开头重新进入（不在下游打补丁）。

## 反模式（Anti-Patterns）

| ❌ 不要 | ✅ 要做 |
|---|---|
| 把"我们需要一个 X 应用"当作问题陈述 | 问"如果做了这个，哪些可观察结果会改变？" |
| 列 20 个目标却不设优先级 | 限制为 3-5 个目标，并给出可衡量的基线与目标值 |
| 复制粘贴 BRD 章节却不标注知识状态 | 把每条主张标注为 FACT/DECISION/ASSUMPTION 等 |
| 因为"BRD 只提到用户"就跳过角色 | 从工作流描述推断角色，标注为 AI_INFERENCE |
| 为一段话的来源写 3 页背景 | 按输入密度调整输出规模 |

## 示例：充足输入 → 充足输出（Sufficient Input → Sufficient Output）

**输入**：含业务背景、当前流程、痛点、5 个目标、4 个角色、约束的 BRD。
**输出**：完整模板，含带来源依据的叙述 + 显式寄存器。

## 示例：稀疏输入 → 降级输出（Sparse Input → Degraded Output）

**输入**：Slack 消息"我们需要一个面向 VIP 客户的会议邀约系统。"
**输出**：Intake 登记来源 → Preflight 返回 L1 → Think 识别缺失项：角色有哪些？当前流程是什么？成功指标是什么？→ Clarify 生成 3 个问题 → 停在 `needs_user_input`。

## 加载参考文档（Load References）

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见反模式（写产物时对照规避） | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/elicitation-techniques.md` | 需求采集技法（访谈/观察，材料稀疏时用） | 材料稀疏时 |
| `references/output-contract.md` | 产物结构与 ID 契约 | Draft 前 |
| `references/question-patterns.md` | Clarify 提问模板（8 类句式） | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单（Human Gate 用） | Human Gate 前 |
| `references/source-handling.md` | 来源处理规则（SRC-* 登记与引用） | Intake/来源处理时 |
| `references/thinking-framework.md` | 思考透镜（Common Core + 领域 lens，必读） | 每次任务开始（必读） |

## 完成标准（Completion）

所有承载需求的来源均已体现或被注明排除原因；背景、现状、问题、目标与方案彼此区分；实质性主张可追溯；阻断性未知阻止确认；且获得授权的人类批准了基线。
