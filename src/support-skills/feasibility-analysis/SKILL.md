---
name: feasibility-analysis
description: 评估一个具体的产品级方案在四个维度上是否可行：市场空间 / 技术可行性 / 投入产出 / 风险评估，并产出 做 / 不做 / 有条件做 的推荐，附带显式的 AI 置信度。当同一目标存在 ≥2 个实质不同的方案时，把取舍作为可行性报告内部的 §多方案取舍 章节处理（在打分前定义加权决策矩阵）——绝不作为独立交付物。AI 推荐；人类决策人拍板。
---

# 可行性分析（Feasibility Analysis）

## 目的与边界

当技术、合规、资源或业务约束对某个具体产品级方案的可行性提出疑问时，本 skill 在四个维度上客观框定评估——**市场空间、技术可行性、投入产出、风险评估**——并给出带置信度的 做 / 不做 / 有条件做 推荐——但**绝不做出最终决策**。人类决策人拥有选择权。

当同一目标存在 ≥2 个实质不同的方案时（自研 vs 外购、不同路径、不同范围取舍），对比作为可行性报告内部的 **§多方案取舍** 章节处理，使用在打分前定义好的加权决策矩阵。它是报告的一章——不是独立的交付物。

**不要**做出最终决策、静默修改范围、设计架构，或评估只在实现细节上不同的方案（那些属于工程，不属于产品）。可行性评估要求一个具体的产品级方案已经存在——在 X 具体之前，你无法评估"我们能不能做 X"。

## 输入与输出

输入：一个具体的产品级方案（来自 `product-ux` 或 `function-description`）或显式的可行性决策请求、上游证据（background-goal、成本/约束/合规输入）、以及一个指定的 decision-owner。如果决策会改变已确认的范围、成本、合规或风险姿态，停止在 `needs_user_input`，直到识别出决策 owner。

输出：单一的 `feasibility-report.md`，使用 `src/templates/support/feasibility-report.md` 中的模板——市场空间 / 技术可行性 / 投入产出 / 风险评估 / §多方案取舍（≥2 实质方案时）/ 结论（做/不做/有条件做）。§多方案取舍 章节（若存在）使用 `src/templates/support/solution-comparison.md` 的多方案对比模板作为其章节结构；它嵌入在报告中，绝不作为独立产物产出。

分析前加载 `references/thinking-framework.md`（其中引用 `src/framework/thinking-core.md` §1 必用透镜）。Intake 时加载 `references/source-handling.md`。Clarify 时加载 `references/question-patterns.md`。起草前加载 `references/output-contract.md`。Generate 时加载 `references/anti-patterns.md`。移交前加载 `references/audit-checklist.md` 和 `references/reviewer-checklist.md`。评审前运行 `scripts/validate_artifact.py <artifact> --json`。

## 思考提示（按阶段）

### 1. Preflight（预检）
- "是否存在需要在市场 / 技术 / 投入产出 / 风险维度回答的可行性问题？是否存在具体的产品级方案？"
- "同一目标是否存在 ≥2 个真正不同的方案？如果是，适用 §多方案取舍 章节（报告内部的加权矩阵）。"
- "如果方案只在实现细节上不同，路由给工程，而不是产品。"
- 识别 decision_owner。**如果不存在决策 owner，返回路由收据并 STOP 在 `needs_user_input`。**
- 评估成熟度：L0（无具体方案）→ L1（模糊想法）→ L2（存在产品级方案）→ L3（有成本/约束数据）→ L4（上游已确认）。

### 2. Intake（输入）
- "每个来源实际上是怎么说成本、约束、合规、依赖和风险的——而不是我假设的？"
- 收集四维度证据：市场空间（目标用户、可比渗透率、理论空间）；技术可行性（每个挑战 → 已验证 / 待验证 / 不可行）；投入产出（研发 + 运维成本、预期收益、回本周期）；风险评估（每个风险 → 影响 + 概率 + 应对）。
- 当适用 §多方案取舍 章节时，对每个候选方案：方案摘要、技术依赖、资源估算（人 + 时间）、关键风险、可逆性。
- 按 `src/framework/contracts.md` 归类知识状态：FACT / DECISION / ASSUMPTION / AI_INFERENCE / UNKNOWN / CONFLICT。保留 SRC-ID。

### 3. Think（思考；应用 thinking-core.md §1 必用透镜 + 评估领域透镜）
- **First Principles（第一性原理）**："要做的可观察决策是什么？哪些成本和风险是伪装成需求的假设？"
- **Systems Thinking（系统思维）**："决策影响哪些上游/下游 work item、角色和依赖？"
- **Adversarial（对抗性审查）**："明显的推荐会不会是陷阱？证据是否片面？没有真实期限却强调紧迫？"
- **Reverse Validation（反向验证）**："从期望的结果倒推，每个方案要成功必须具备什么？"
- 领域透镜（见 `references/thinking-framework.md`）：Occam's Razor（多个方案都能满足目标时选依赖最少者）、Opportunity Cost（选择后放弃什么）、Reversibility（能否撤销错误选择）。

### 4. Clarify（澄清）
- 先调研可发现的客观事实（成本基准、公开定价、过往项目数据）。
- 批量整理剩余问题，附带：AI 初步判断、证据、选项、影响、owner、阻断标记。
- **当答案会改变推荐、标准权重或重大成本/风险数字时，停止在 `needs_user_input`**。
- 限制：每会话 ≤5 个问题。按影响排序。

### 5. Generate（生成）
- 主线四维度：市场空间 → 技术可行性 → 投入产出 → 风险评估 → 结论（做/不做/有条件做，条件须具体可衡量）。
- **§多方案取舍 章节**（仅当存在 ≥2 个实质不同方案时）：候选方案（等深描述）→ 权重在打分前定义 → 方案对比矩阵 → AI 推荐（HIGH/MEDIUM/LOW 置信度）→ 敏感度分析 → 人工决策。该章节用 `src/templates/support/solution-comparison.md` 作为章节结构模板，嵌入 `feasibility-report.md`，不独立产出。
- 状态：使用 `draft`、`needs_user_input` 或 `conditional_review`——**绝不使用 `confirmed`**。

### 6. Audit（审计）
- **锚定检查（Anchoring Check）**：标准是在打分前定义的，还是胜出的方案塑造了权重？
- **对等检查（Parity Check）**：每个候选是否以同等深度描述（没有假对等，没有灌水）？
- **敏感度（Sensitivity）**：哪个标准，若其权重 ±1，会翻转推荐？是否显式说明？
- **来源保真（Source Fidelity）**：每条成本/风险数字是否追溯到来源或显式假设？
- 运行 `scripts/validate_artifact.py <artifact> --json`。修复所有错误。警告 → 记入审计备注。

### 7. Human Gate（人工关卡）
呈现：四维度证据摘要、§多方案取舍 矩阵（若适用）、敏感度分析、带置信度和关键假设的 AI 推荐、审计结果。
**只有决策 owner 可以批准。** 人类的选择被记录为 `DecisionRecord`（DEC-XXX），含所选选项、理由、日期和决策人。批准会创建带 SHA-256 的 ReviewRecord。

### 8. Commit / Reflow（提交 / 回流）
- 只有 `pipeline.py review --decision approve` 可以写入 `confirmed`。
- 如果决策改变范围 → 回流到最早受影响的 Work Item；绝不静默修改范围。
- 当已确认的产物发生变化：记录 delta → 更新受影响章节 → 重跑 Audit → 回到 Human Gate。

## 反模式

| ❌ 不要 | ✅ 要做 |
|---|---|
| 评估没有具体方案对象的"可行性"（"我们想做邀请系统——可行"） | 评估前要求具体的产品级方案 |
| AI 替业务方做最终决定（"分析清楚表明…"） | AI 推荐并给置信度；人拍板 |
| 打分后才定权重 | 权重先于打分定义，防锚定 |
| 给偏爱的方案更多篇幅 | 每个候选等深描述 |
| 把明显劣质的选项包装成可比 | 如实呈现差距，让矩阵暴露差距 |
| 推荐不带置信度 | 总是说明：HIGH/MEDIUM/LOW 置信度 + 关键假设 |
| 跳过敏感度分析 | 识别哪个假设变化会翻转推荐 |
| 成本/风险估算当事实写死 | 标 `AI_INFERENCE`/`ASSUMPTION` + 责任人 + SRC-* |
| 只有单个方案也硬凑对比 | 单一方案时只做四维度可行性，不加 §多方案取舍 章节 |
| 把实现细节当产品方案评估 | 把细节级选择路由给工程 |

## 示例：充分输入 → 充分输出

**输入**：具体产品方案已存在（`function-description`）、成本/约束输入已登记、决策 owner 已指定。决策：订单通知模块自研 vs 外购（带多方案取舍的可行性）。
**输出**：完整 `feasibility-report.md`——市场空间（目标用户量 100 万，可比渗透率 30%，理论空间）→ 技术可行性（微信模板消息已验证兼容）→ 投入产出（自研 2 人×4 周 ≈ ¥X vs 外采年费 ¥Y，回本周期）→ 风险评估（供应商锁定：高/中 → 应对：退出条款）→ §多方案取舍（权重在打分前定义：业务匹配 5、用户影响 4、成本 4、时间 3、技术风险 3、可逆性 2；自研 86 vs 外采 65；AI 推荐 自研，MEDIUM 置信度；敏感度：时间权重 3→5 翻转）→ 结论：有条件做（自研，条件：2 周内确认技术栈）; 人工决策记录 DEC-001 → 状态 `ready_for_human_review`.

## 示例：稀疏输入 → 降级输出

**输入**：Slack 消息"帮我评估一下自研还是外采这个功能"。
**输出**：Preflight 发现没有具体的产品级方案和决策 owner → Intake 登记 SRC-001 → Think 识别缺失项：哪些方案选项？哪些标准？谁决定？成本数据是什么？→ Clarify 生成 3 个问题（方案候选、决策 owner、决策日期/范围）→ 停止在 `needs_user_input`。

## 加载参考文献

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/thinking-framework.md` | 思考透镜（Common Core + 可行性领域 lens，必读） | 每次任务开始（必读） |
| `references/feasibility.md` | 可行性四维度主线模式细节 | 主线评估时 |
| `references/multi-solution.md` | §多方案取舍 章节细节（加权矩阵 + 决策记录） | 存在 ≥2 实质方案时 |
| `references/output-contract.md` | 产物结构与 ID 契约 | Draft 前 |
| `references/question-patterns.md` | Clarify 提问模板（8 类句式） | Clarify 提问时 |
| `references/source-handling.md` | 来源处理规则（SRC-* 登记与引用） | Intake/来源处理时 |
| `references/anti-patterns.md` | AI 常见反模式（可行性分析特有，写产物时对照规避） | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/reviewer-checklist.md` | 人工评审清单（Human Gate 用） | Human Gate 前 |

## 完成标准

四个维度（市场空间 / 技术可行性 / 投入产出 / 风险评估）都有证据支撑的分析；当存在 ≥2 个实质不同方案时，§多方案取舍 章节以等深方式记录每个方案，标准在打分前定义并加权；敏感度分析识别出哪个假设变化可能翻转推荐；结论是清晰的 做 / 不做 / 有条件做，条件具体可衡量；AI 推荐带显式置信度；人类决策者的选择被记录为 `DecisionRecord`。如果决策改变范围，回流最早受影响的 Work Item。
