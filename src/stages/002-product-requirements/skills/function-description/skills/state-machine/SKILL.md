---
name: state-machine
description: 定义实体状态迁移 STATE-XXX——合法状态、触发事件、目标状态、守卫条件、副作用。function-description 编排的第三个规则子 skill。
---

# State Machine · 状态变化

## 目的与边界

枚举范围内每个实体的每个合法状态，并为每个 状态 × 事件 组合定义目标状态及其守卫条件与副作用。转移表是生命周期行为的权威来源——而非流程图。

**不得**设计展示状态的 UI（→ interaction-rules `IX-XXX`）、定义数据库 schema 或字段存储（→ validation-rules / 实现）、编写实现代码，或重复异常/恢复文案（→ exception-handling）。

## 输入与输出

**输入**: 门控转移的已确认 §业务规则（`BR-XXX`）、已确认的 `product-ux` 状态定义与流程，以及已确认的范围基线。**输出**: 父级 `function-description.md` 的 §状态变化 章节（registry `output_section`: 状态变化），使用由 `src/templates/resolver.py function-description.md` 解析的模板。

分析前加载 `references/thinking-framework.md`（其引用 `src/framework/thinking-core.md` §1 强制透镜 + §2 检查透镜）。Draft 前加载 `references/output-contract.md`。交接前加载 `references/audit-checklist.md` 与 `references/reviewer-checklist.md`。Review 前运行 `scripts/validate_artifact.py <artifact> --json`。

## 思考提示（按阶段）

### 1. Preflight
- "范围内哪些实体承载多个状态？门控它们的 BR-XXX 已确认吗？"
- 枚举有状态实体及门控其转移的已确认 BR 规则。建模前，把任何没有门控 BR 的有状态 P0 实体标出来。
- **若不存在任何有状态实体或门控规则**，返回 routing receipt 并 STOP——不要进入 Intake。

### 2. Intake
- "已确认的故事/UX 对生命周期实际说了什么——而不是我想象的流程？"
- 列出来源提到的每个状态、暗示的每个事件、陈述的每条约束。按 `src/framework/contracts.md` 为每条标记 `FACT` / `DECISION` / `AI_INFERENCE` / `UNKNOWN` / `CONFLICT`。在每个候选上保留 BR-XXX / FEA-XXX 来源。

### 3. Think (apply thinking-core.md §1 mandatory lenses)
- **First Principles**: "哪些状态是真正独立存在的业务条件？哪些"状态"只是 UI 视图？"
- **Systems Thinking**: "哪些其他实体、字段或流程会响应这次转移？什么不能被破坏？"
- **Role Perspective**: "谁触发每个事件？谁不可以？副作用会通知谁？"
- **Constraint Analysis**: "哪些 BR 规则门控每条转移？适用哪些硬约束（合规、时序）？"
- **Adversarial**: "重复事件、回滚尝试、超时或并发触发时会发生什么？是否有被禁止的转移被静默跳过？"
- **Reverse Validation**: "从每个终态反向推导，实体到达那里必须发生过什么？"

### 4. Clarify
- 先自行调研可发现的事实（既有系统状态机、流程文档、审计日志）。
- 剩余问题批量提交：AI 初步判断、依据、选项、影响、owner、阻断标志。
- 当未定义的转移或守卫条件改变生命周期行为、成本或风险时，**停在 `needs_user_input`**。
- Limit: 每轮 ≤5 个问题，按影响排序。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
- 填 §状态变化 表：状态定义（进入/退出条件）+ 转移表（当前状态 | 触发事件 | 目标状态 | 条件 | 副作用 | 来源）+ Mermaid 状态图。
- 被禁止的转移显式说明（「不允许」），绝不留空。副作用点名或写「无」。
- Status: 用 `draft`、`needs_user_input` 或 `conditional_review`——**永不 `confirmed`**。

### 6. Audit
- **Completeness（完整性）**: 每个状态 × 每个合法事件 → 目标状态；无孤儿状态、无悬空转移。
- **Guard precision（守卫精确性）**: 每个条件可判定；无「视情况」「适当时候」。
- **Side effects（副作用）**: 每个副作用都被点名（通知、相关实体更新、审计、回滚）或写「无」。
- **Consistency（一致性）**: 转移与它们引用的 BR-XXX 规则和 IX 引用一致。
- **Terminal semantics（终态语义）**: 终态/取消态不能回退；无语义矛盾。
- 运行 `scripts/validate_artifact.py <artifact> --json`。修复所有 error；warning 在审计记录中说明。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
Present 候选 §状态变化、证据摘要（每条转移由哪个故事/BR 支撑）、未知项与影响、需做的决策、审计结果、变更摘要。
**只有产品负责人 / 业务负责人可以批准。** 批准产生 ReviewRecord（SHA-256）。

### 8. Commit / Reflow
- 只有 `pipeline.py review --decision approve` 可写入 `confirmed`。
- 变更时：记录 delta → 更新受影响转移 → 重跑 Audit → 返回 Human Gate。
- 上游 BR 或故事变更 → 从本 Skill 开头重进（而非下游打补丁）。

## 反模式

| ❌ 不要 | ✅ 要 |
|---|---|
| 只列状态、不给转移事件 | 每行：当前状态 → 触发事件 → 目标状态 → 条件 → 副作用 |
| 把被禁止的转移留空 | 显式说明：终态回退 → 不允许 |
| 把「当订单异常时」当条件 | 可判定的守卫，如「超时 30 分钟未支付」 |
| 把「通知相关人员」当副作用 | 点名谁 / 什么渠道 / 何时——或写「无」 |
| 只建模主路径 | 覆盖成功、失败、取消、超时、重试、回滚、并发 |
| 把「按钮变灰」写进状态行 | 那是 UI 展示 → interaction-rules；状态行 = 状态 + 转移 |

## 示例：充分输入 → 充分输出

**输入**: 已确认的 FEA-005（订单）+ BR-009（支付超时自动取消）+ 覆盖 待支付/已支付/已取消/已发货/已完成 的 UX。
**输出**: §状态变化 含 STATE-001..STATE-008——带进入/退出条件的状态定义、覆盖超时自动取消、重试、退款回滚与终态的完整转移表，外加 Mermaid 图。

## 示例：稀疏输入 → 降级输出

**输入**: 一行已确认文字 "订单有状态，支付成功才算下单成功"，无状态名、无事件、无转移。
**输出**: Preflight 返回 L1 → Intake 登记单一 `UNKNOWN` 状态集合 → Think 识别缺失：完整状态清单? 每个状态的事件? 超时/取消/回滚? 终态? → Clarify 生成 3 个问题 → 停在 `needs_user_input`。不编造任何转移。

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

每个 P0 FUN-XXX 中的每个有状态实体都有完整的转移表；每个状态有定义的进入/退出事件、无孤儿状态；每条转移有触发、可判定的守卫条件与点名的副作用；被禁止的转移显式说明；终态被识别且不能回退；转移与门控 BR-XXX 一致；阻断性未知项阻止确认；授权人工批准 §状态变化 基线。
