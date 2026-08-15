---
name: exception-handling
description: 为每个 P0 功能枚举失败模式、重试/回滚/恢复策略与用户可见提示（EX-XXX），使父产物的 §异常与失败处理 完整、可判定、可追溯。function-description 编排的一部分（4/5，在 state-machine 之后）。
bind: function-description (called after state-machine)
---

# Exception Handling 异常与失败处理

## 目的与边界

为范围内每个功能定义可能出错之处与系统如何响应：可判定的触发条件、系统行为（拦截 / 降级 / 回滚 / 阻断）、带边界的恢复路径（重试 / 手动 / 自动 / 终止），以及面向用户的中文提示。每条 `EX-XXX` 行必须能被下游 `acceptance-criteria`（AC-XXX）作为可验证的失败用例消费。

**不得**重新定义校验规则（→ `validation-rules`）、领域业务规则（→ `business-rules`）、状态转移（→ `state-machine`）、UI 呈现或交互反馈（→ `interaction-rules`）、可测的验收用例（→ `acceptance-criteria`），或实现级错误处理（try-catch、异常类型、超时毫秒数、消息队列、幂等键）。

## 输入与输出

输入：按功能组织的区块 `FUN-XXX`，含已确认的状态（`state-machine`）、业务拒绝分支（`business-rules`）、校验拒绝（`validation-rules`）、外部依赖清单与已确认的失败来源。输出：`EX-XXX` 行写入父级 `function-description.md` §2 分功能详述 中每个 FUN 的 `#### 异常与失败处理` 小节，遵循 `src/templates/stage-2-product/function-description.md`。

分析前加载 `references/thinking-framework.md`（其引用 `src/framework/thinking-core.md` §1 强制透镜）。Draft 前加载 `references/output-contract.md`。交接前加载 `references/audit-checklist.md` 与 `references/reviewer-checklist.md`。Review 前运行 `scripts/validate_artifact.py <artifact> --json`。当失败来源稀疏时加载 `references/question-patterns.md`（主动向业务方采集失败场景）。

## 思考提示（按阶段）

### 1. Preflight
- "范围内有哪些 FUN-XXX？每个功能的风险密度如何（金钱、库存、数据、外部依赖）？"
- 确认上游失败来源（state-machine、business-rules、validation-rules）存在，并识别失败来源负责人。
- **若不存在任何功能区块或已确认的失败来源**，返回 routing receipt 并 STOP——不要进入 Intake。
- 评估成熟度：L0（无失败信息）→ L1（单一稀疏失败提及）→ L2（部分失败分支）→ L3（充分明确）→ L4（上游已确认）。

### 2. Intake
- "对这个 FUN，上游实际说了什么会失败——而不是我认为可能失败什么？"
- 先逐字提取失败声明再解读。将每条归类为 `FACT`、`DECISION`、`ASSUMPTION`、`AI_INFERENCE`、`UNKNOWN` 或 `CONFLICT`。
- 用 SRC-ID 登记来源。绝不从沉默中发明失败场景；缺失的失败分支是 `UNKNOWN`，而非不存在。

### 3. Think (apply thinking-core.md §1 mandatory lenses + domain lenses)
- **First Principles**: "系统必须吸收什么可观察的失败？哪些失败被笼统的"系统错误"掩盖？"
- **Systems Thinking**: "此失败发生时，哪些上游/下游系统、数据或角色受影响？"
- **Failure Source Enumeration**: "走一遍六类失败源（校验 / 权限 / 资源 / 业务 / 冲突 / 网络）——对该功能哪些真实可能发生？"
- **Adversarial**: "如果我们在这里什么都不做，什么会静默坏掉？我能否构造一个反例？"
- **Reverse Validation**: "从我们向用户承诺的恢复反向推导，系统行为必须满足什么？"

### 4. Clarify
- 先从上游消解可发现的事实（多数失败点已由 business-rules / state-machine / validation-rules 确认）。
- 剩余问题批量提交：AI 初步判断、依据、选项、影响、owner、阻断标志。
- 当答案可能改变恢复策略、提示文案或补偿行为时，**停在 `needs_user_input`**。
- Limit: 每轮 ≤5 个问题，按影响排序。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
- 填 `EX-XXX` 行。一行一种失败——触发条件与系统行为分开为独立单元格。
- Status: 用 `draft`、`needs_user_input` 或 `conditional_review`——**永不 `confirmed`**。

### 6. Audit
- **Coverage（覆盖）**: 每个 P0 FUN 有 ≥1 条 EX；每条高风险路径（金钱、库存、外部依赖）都有定义的失败分支。
- **Decidability（可判定性）**: 每个触发条件能被测试/开发无歧义复现。
- **No Silent Failure（无静默失败）**: 每条 EX 有用户可见提示；无笼统的"系统异常，请稍后重试"行。
- **Boundary（边界）**: 无校验规则、状态转移、交互文案或实现细节泄漏进来。
- 运行 `scripts/validate_artifact.py <artifact> --json`。修复所有 error；warning 在审计记录中说明。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
Present：候选 EX 行、证据摘要（哪些来源支撑每个失败场景）、未知项及其影响、需做的决策（恢复策略、提示文案、补偿）、审计结果、变更摘要。
**只有业务/功能负责人可以批准。** 批准产生 ReviewRecord（SHA-256）。

### 8. Commit / Reflow
- 只有 `pipeline.py review --decision approve` 可写入 `confirmed`。
- 变更时：记录 delta → 更新受影响 EX 行 → 重跑 Audit → 返回 Human Gate。
- 后续矛盾 → 从本 Skill 开头重进（而非下游打补丁）。

## 反模式

| ❌ 不要 | ✅ 要 |
|---|---|
| 给每个功能一条笼统的"系统异常，请稍后重试"行 | 枚举该功能六类失败源中哪些真实可能发生 |
| 写「当系统繁忙时」/「视网络情况」这类触发 | 写可判定的触发：「当提交时余额不足导致扣款失败」 |
| 把触发条件与系统行为混进一句话 | 一行一个事实：条件（什么失败）→ 行为（系统做什么） |
| 说「提示用户稍后重试」却不给重试边界 | 明确重试次数/间隔/幂等，或切换为手动/终止 |
| 可恢复与不可恢复失败共用一句提示 | 区分可恢复（重试/自动）与不可恢复（终止 → 人工处理） |
| 处理金钱/库存失败却不给补偿 | 为金钱、库存与影响数据的失败定义回滚/补偿 |
| 让 AI 推断的失败场景伪装成 FACT | 给每条 EX 行标记 FACT/DECISION/AI_INFERENCE/UNKNOWN 并登记未知项 |
| 把实现细节（try-catch、超时 ms、MQ、幂等键）塞进表格 | 只保留产品级行为；实现细节留给工程 |

## 示例：充分输入 → 充分输出

**输入**: FUN-001（活动预约提交）的 `state-machine` + `business-rules` 已确认——BR-005（活动已结束驳回）、已知超时的外部支付依赖、P0 高风险密度。
**输出**: 4 条 `EX-XXX` 行，每条都带可判定触发、系统行为（拦截/降级/回滚）、恢复边界（重试 3× / 30s 间隔 / 幂等）、中文用户提示与 SRC 追溯——如 EX-001 网络超时 → 弹窗"提交失败，请重试" → 重试 3 次幂等提交 (B19)。

## 示例：稀疏输入 → 降级输出

**输入**: "给下单功能加点异常处理"
**输出**: Intake 登记来源 → Preflight 返回 L1 → 六类失败源扫描未发现已确认的失败信息 → Clarify 批量生成 3 个问题（哪些失败已在别处确认？金钱/库存失败是否需要补偿？重试上限是多少？）→ 停在 `needs_user_input`。

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

每个 P0 功能至少有一条带可判定触发的 `EX-XXX`；每条 EX 有带边界的恢复路径与用户可见提示；可恢复与不可恢复失败明确区分；无残留静默失败；对校验/状态/交互/实现的边界被保持；EX 行追溯到 FUN-XXX 与来源 ID；阻断性未知项阻止确认；授权人工批准该基线。
