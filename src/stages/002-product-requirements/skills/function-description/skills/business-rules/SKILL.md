---
name: business-rules
description: 从已确认的 UX 与故事中提取领域级业务规则 BR-XXX（约束、计算、策略、权限、时序）。function-description 编排的第一个规则子 skill。
---

# Business Rules · 业务规则

## 目的与边界

确立系统在领域层必须计算、强制与决定什么——独立于任何 UI 如何呈现。每条 BR 必须可追溯到一个已确认的 `ST-XXX` 或 `FEA-XXX`，且必须可执行：开发者能把它转成代码而无需追问。

**不得**描述 UI 行为（→ interaction-rules `IX-XXX`）、编写字段格式/长度/必填检查（→ validation-rules `VL-XXX`）、建模状态迁移（→ state-machine）、定义失败/恢复路径（→ exception-handling）或编写验收测试（→ acceptance-criteria `AC-XXX`）。

## 输入与输出

**输入**: 已确认的 `product-ux`（FEA-XXX + UX 步骤）与已确认的上游故事（`ST-XXX`），以及已确认的范围基线。**输出**: 父级 `function-description.md` 的 §业务规则 章节（registry `output_section`: 业务规则），使用由 `src/templates/resolver.py function-description.md` 解析的模板。

分析前加载 `references/thinking-framework.md`（其引用 `src/framework/thinking-core.md` §1 强制透镜 + §2 检查透镜）。Draft 前加载 `references/output-contract.md`。交接前加载 `references/audit-checklist.md` 与 `references/reviewer-checklist.md`。Review 前运行 `scripts/validate_artifact.py <artifact> --json`。

## 思考提示（按阶段）

### 1. Preflight
- "我将要为其建规则的功能，其所有上游 FEA / ST 都已确认吗？"
- 枚举 P0 功能及其上游故事链接。写任何规则前，将缺失归属或矛盾的 UX 标为 `CONFLICT`。
- **若不存在任何已确认的上游功能**，返回 routing receipt 并 STOP——不要进入 Intake。

### 2. Intake
- "已确认的故事/UX 实际要求系统计算或强制什么——而不是我认为它意味着什么？"
- 先逐字提取候选规则再解读。按 `src/framework/contracts.md` 为每个候选标记知识状态：`FACT` / `DECISION` / `ASSUMPTION` / `AI_INFERENCE` / `UNKNOWN` / `CONFLICT`。
- 在每个候选上保留 `ST-XXX` / `FEA-XXX` 来源。不把不同来源的声明合并为一条规则。

### 3. Think (apply thinking-core.md §1 mandatory lenses)
- **First Principles**: "系统必须保证什么可观察的业务结果？哪些约束伪装成了假设？"
- **Systems Thinking**: "这条规则与哪些其他规则、状态、字段或功能交互？什么已经生效且不能被破坏？"
- **Role Perspective**: "对受此规则约束的每个角色——谁可以、谁不可以、谁依赖该结果？"
- **Constraint Analysis**: "这条规则绝不能违反的硬约束（合规、定价策略、法务）是什么？"
- **Adversarial**: "在某些场景下这条规则的反面是否可能成立？什么证据能证伪它？"
- **Reverse Validation**: "从预期结果反向推导，系统必须计算或强制什么才能达到？"

### 4. Clarify
- 先自行调研可发现的事实（现有定价表、已发布策略、系统日志）。
- 剩余问题批量提交：AI 初步判断、依据、选项、影响、owner、阻断标志。
- 当缺失的约束或策略决策改变规则的结果、范围、成本或风险时，**停在 `needs_user_input`**。
- Limit: 每轮 ≤5 个问题，按影响排序。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
- 填 §业务规则 表。一行一条规则；强制归类：计算 / 约束 / 条件 / 权限 / 时序。
- Status: 用 `draft`、`needs_user_input` 或 `conditional_review`——**永不 `confirmed`**。

### 6. Audit
- **Rule separation（规则分离）**: BR（领域）vs VL（字段格式）vs IX（交互）vs 状态 vs 异常 vs AC——无泄漏。
- **Determinism（确定性）**: 每条规则都有通过/失败判据；无「合理」「适当」「尽快」。
- **Traceability（可追溯性）**: 每条 BR-XXX 链接 ST-XXX / FEA-XXX；每个 P0 FUN 有 ≥1 条 BR。
- **Conflict scan（冲突扫描）**: 无两条 BR 相互矛盾；冲突保持可见，直到授权人工裁决。
- 运行 `scripts/validate_artifact.py <artifact> --json`。修复所有 error；warning 在审计记录中说明。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
Present 候选 §业务规则、证据摘要（每条规则由哪个故事/UX 支撑）、未知项及其影响、需做的决策、审计结果、变更摘要。
**只有产品负责人 / 业务策略负责人可以批准。** 批准产生 ReviewRecord（SHA-256）。

### 8. Commit / Reflow
- 只有 `pipeline.py review --decision approve` 可写入 `confirmed`。
- 变更时：记录 delta → 更新受影响规则 → 重跑 Audit → 返回 Human Gate。
- 后续发现故事/UX 矛盾 → 从本 Skill 开头重进（而非下游打补丁）。

## 反模式

| ❌ 不要 | ✅ 要 |
|---|---|
| 写「系统应校验输入」却不指明规则 | 写「BR-003: 客单价 ≥ ¥500 按 VIP 档计算折扣, 公式 price×0.9, 边界 ¥499.99 不触发」 |
| 定义一条其实是 UI 交互的 BR | 引用 product-ux 的 IX；BR = 领域约束 |
| 写「金额不能太大」却无边界 | 说明精确边界与边界行为（如 单笔 > ¥100k 需审批） |
| 把已确认的 UX 流程逐字照抄成"规则" | 对每个功能问"系统必须计算/强制什么？" |
| 因只提到主角色就跳过权限规则 | 覆盖每个已确认角色；推断出的标 AI_INFERENCE |
| 为 1 行故事写 10 页规则 | 规则密度与输入密度匹配；稀疏时降级 |

## 示例：充分输入 → 充分输出

**输入**: 已确认的 product-ux FEA-002（活动报名）+ ST-002 故事，明确 VVIP 阈值、配额上限与报名截止时间。
**输出**: §业务规则 含 BR-001..BR-004——超额拒绝、VVIP 阈值折扣、截止截断、配额分配顺序——每条都归类（约束/计算/时序）、可追溯到 ST-002 / FEA-002、且写明拒绝行为。

## 示例：稀疏输入 → 降级输出

**输入**: 一行已确认文字 "活动报名要限制人数"，无阈值、无配额、无截止时间。
**输出**: Preflight 返回 L1 → Intake 将单一候选登记为 `UNKNOWN` → Think 识别缺失：配额多少? 每人还是全局? 先到先得还是抽签? 截止时间? → Clarify 生成 3 个问题 → 停在 `needs_user_input`。不为凑表格编造任何 BR。

## 加载参考

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见反模式（写产物时对照规避） | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/output-contract.md` | 产物结构与 ID 契约 | Draft 前 |
| `references/question-patterns.md` | Clarify 提问模板（8 类句式） | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单（Human Gate 用） | Human Gate 前 |
| `references/source-handling.md` | 来源处理规则（SRC-* 登记与引用） | Intake/来源处理时 |
| `references/thinking-framework.md` | 思考透镜（Common Core + 领域 lens，必读） | 每次任务开始（必读） |

## 完成标准

每个 P0 FUN-XXX 有 ≥1 条已归类、确定性的 BR-XXX；每条 BR 可追溯到已确认的 ST-XXX / FEA-XXX；无 UI 词汇泄漏；无两条规则相互矛盾；规则密度与输入密度匹配；阻断性未知项阻止确认；授权产品/策略负责人批准 §业务规则 基线。
