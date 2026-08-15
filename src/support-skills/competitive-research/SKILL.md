---
name: competitive-research
description: 当业务方案不清晰且缺少参考时进行竞品分析。使用结构化框架（功能矩阵、定位图、SWOT）为产品决策提供依据。所有发现均为 AI_INFERENCE，直到人工确认。
---

# 竞品调研（Competitive Research）

## 目的与边界

当产品方向缺少参考——"竞品是怎么做的？""是否存在市场标准？""我们如何差异化？"——本 skill 系统性地分析竞品，并综合出可供产品决策采取行动的洞见。产物是 `competitive-analysis.md`，由 `user-journey-and-stories`、`product-ux` 或 `function-description` 消费。

**不要**在不理解竞品语境的情况下照搬竞品功能、把调研发现当作已确认的事实呈现、替代 user-journey 或 product-ux 的工作，或在没有差异化分析的情况下得出"我们应该照做竞品 X 的做法"的结论。竞品在其市场上的成功，若无证据不会自动迁移到我们的市场。

## 输入与输出

输入：已确认的业务基线（`background-goal.md`，含已确认的目标）或范围基线、一个调研目标（业务级 vs 功能级）、以及已登记的竞品来源（官网、应用商店页面、用户评价、公开文档、行业报告）。若没有已确认的背景或调研目标，停止在 `needs_user_input`——不要在真空中调研。

输出：`competitive-analysis.md`，使用 `src/templates/support/competitive-analysis.md` 中的模板。

分析前加载 `references/thinking-framework.md`（其中引用 `src/framework/thinking-core.md` §1 的必用透镜）。Intake 时加载 `references/source-handling.md`。Clarify 时加载 `references/question-patterns.md`。起草前加载 `references/output-contract.md`。Generate 时加载 `references/anti-patterns.md`。移交前加载 `references/audit-checklist.md` 和 `references/reviewer-checklist.md`。评审前运行 `scripts/validate_artifact.py <artifact> --json`。

## 思考提示（按阶段）

### 1. Preflight（预检）
- "本次调研支撑什么决策？调研目标是业务级（方案方向）还是功能级（功能设计）？"
- "应研究哪些竞品——直接竞品（同品类）、间接竞品（同一需求、不同方案）还是参照竞品（其他领域的最佳实践）？"
- 为每个竞品来源登记一个 SRC-ID。识别 research_owner 和 decision_owner。
- **若没有已确认的 background-goal 或调研目标**，返回路由收据并 STOP 在 `needs_user_input`。
- 限制在 3-5 个竞品。评估成熟度：L0（无方向）→ L1（单一模糊问题）→ L2（业务方向清晰）→ L3（范围已定义）→ L4（上游已确认）。

### 2. Intake（输入）
- "每个来源实际上是怎么描述竞品的——而不是我对其产品的假设？"
- 逐字提取竞品陈述（功能集、定价、目标用户、定位）。按 `src/framework/contracts.md` 将每条归类为 `FACT`、`AI_INFERENCE`、`UNKNOWN` 或 `CONFLICT`。
- 保留 SRC-ID 和位置。不要将两个竞品的说法合并到一行。

### 3. Think（思考；应用 thinking-core.md §1 必用透镜 + 竞品领域透镜）
- **First Principles（第一性原理）**："每个功能实际服务于什么用户需求？如果把竞品 X 作为参考移除，我们已确认的目标是否仍然成立？"
- **Systems Thinking（系统思维）**："这项调研会影响哪些细分、用户流和下游决策？"
- **Adversarial（对抗性审查）**："我的假设的反面是否可能成立——竞品 X 实际上不是对标基准？证据是否只来自某一利益方？"
- **Reverse Validation（反向验证）**："从我们想要的差异化倒推，竞品必须在哪些方面做失败？"
- 领域透镜：Positioning Mapping（定位映射）、Differentiation Scan（差异化扫描）、Pattern Extraction（模式提取）、Inference Discipline（推断纪律）（见 `references/thinking-framework.md`）。

### 4. Clarify（澄清）
- 先调研可发现的客观事实（官网、应用商店评论、公开报告）。
- 批量整理剩余问题，附带：AI 初步判断、证据、选项、影响、owner、阻断标记。
- **当答案会改变竞品选择、对比维度或重大结论时，停止在 `needs_user_input`**。
- 限制：每会话 ≤5 个问题。按影响排序。

### 5. Generate（生成）
- 填模板：§1 竞品列表 → §2 逐品分析 → §3 横向对比 → §4 结论（"So What"）。
- 每条洞见都映射到我们的目标（goal ID）。所有发现标记 `AI_INFERENCE`。
- 状态：使用 `draft`、`needs_user_input` 或 `conditional_review`——**绝不使用 `confirmed`**。

### 6. Audit（审计）
- **完整性（Completeness）**：所有选中的竞品都覆盖了吗？所有重大结论都有来源吗？有"So What"吗？
- **确认偏误（Confirmation Bias）**：我是否主动搜索了反证，还是只挑支持性的证据？
- **来源保真（Source Fidelity）**：每条结论都能追溯到 SRC-ID 吗？`FACT` 和 `AI_INFERENCE` 是否区分清晰？
- **下游可用性（Downstream Usability）**：user-journey-and-stories / product-ux 能否无需重新调研就接上？
- 运行 `scripts/validate_artifact.py <artifact> --json`。修复所有错误。警告 → 记入审计备注。

### 7. Human Gate（人工关卡）
呈现：竞品选择理由（直接/间接/参照）、所用框架的分析、跨竞品模式与分歧、"So What"综合、审计结果。
**只有业务负责人可以确认适用性。** 在此之前所有发现保持 `AI_INFERENCE`。批准会创建带 SHA-256 的 ReviewRecord。

### 8. Commit / Reflow（提交 / 回流）
- 只有 `pipeline.py review --decision approve` 可以写入 `confirmed`。
- 当已确认的 background-goal 发生变化：记录 delta → 更新受影响章节 → 重跑 Audit → 回到 Human Gate。
- 之后出现矛盾（竞品改变方向或出现新竞品）→ 从 Preflight 重新进入本 skill，而非在下游打补丁。

## 反模式

| ❌ 不要 | ✅ 要做 |
|---|---|
| "竞品 X 这么做了，所以我们也该这么做" | 理解他们为什么这么做——是否满足相同用户需求？语境是否一致？映射到我们的目标 |
| 列出 20 个竞品配一行描述 | 限制在 3-5 个并做深度分析 |
| 跳过"So What"综合 | 每次竞品调研都必须回答：我们该拿这些信息做什么？ |
| 把发现当作事实呈现 | 在人工确认前把一切都标为 `AI_INFERENCE` |
| 只看直接竞品 | 纳入间接竞品（不同方案、同一需求）和参照竞品（最佳体验） |
| 不了解功能的目标就评判 | 对照我们已确认的目标 ID 打分每个功能，而不是在真空中打分 |
| 把过时来源当作现状 | 记录检索日期；复用竞品事实前重新核验 |

## 示例：充分输入 → 充分输出

**输入**：已确认的 `background-goal.md`（目标 G1：缩短客户入驻流程）、业务级调研目标、3 个已登记 SRC-ID 的竞品来源（两个直接、一个间接）。
**输出**：完整模板——竞品列表（含选择理由）、逐品分析（用定位图 + 功能矩阵）、横向对比（识别出一个市场标准模式和一个空白点）、结论"So What"（把每条洞见映射到 G1 并标 `AI_INFERENCE`）→ 状态 `ready_for_human_review`。

## 示例：稀疏输入 → 降级输出

**输入**：Slack 消息"看看竞品怎么做会员等级的"。
**输出**：Preflight 发现没有已确认的 background-goal 和调研目标 → Intake 把该消息登记为 SRC-001 → Think 识别缺失项：哪些竞品？什么层级（业务级 vs 功能级）？哪些维度重要？→ Clarify 生成 3 个问题（调研目标、竞品候选列表、本次调研支撑的决策）→ 停止在 `needs_user_input`。

## 加载参考文献

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见反模式（竞品分析特有，写产物时对照规避） | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/output-contract.md` | 产物结构与 ID 契约 | Draft 前 |
| `references/question-patterns.md` | Clarify 提问模板（8 类句式） | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单（Human Gate 用） | Human Gate 前 |
| `references/source-handling.md` | 来源处理规则（SRC-* 登记与引用） | Intake/来源处理时 |
| `references/thinking-framework.md` | 思考透镜（Common Core + 竞品领域 lens，必读） | 每次任务开始（必读） |

## 完成标准

竞品的选择有理由（直接/间接/参照）并限制在 3-5 个；至少应用并分析了一个框架；识别了跨竞品模式与分歧；每条洞见映射回一个已确认的目标；"So What"综合提供了可执行、具体的建议；所有发现都带有显式的知识状态（`AI_INFERENCE`，直到确认）；业务负责人确认或修订洞见。
