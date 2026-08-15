---
name: acceptance-criteria
description: 为每个 P0 功能以 Given/When/Then 编写原子、可测量的验收依据 AC-XXX，量化阈值可追溯到 Stage 1 目标（G-XXX）。function-description 编排的一部分（5/5，最后被调用以校验前面所有子 skill）。
bind: function-description (called last, validates all previous sub-skills)
---

# Acceptance Criteria 验收依据

## 目的与边界

以开发、QA 与业务都能认可的形式，为每个功能定义"完成"意味着什么：Given/When/Then 形式、原子、可独立测试的 `AC-XXX`，带量化阈值或可观察结果。每条 AC 是产品与验证之间的契约——不是测试用例，不是接口描述。

**不得**编写可执行的测试用例 / 断言脚本（→ QA）、领域业务规则（→ `business-rules`）、字段校验规则（→ `validation-rules`）、UI 呈现或交互（→ `interaction-rules`）、状态转移（→ `state-machine`）、失败恢复流程（→ `exception-handling`），或实现细节（API、schema、框架）。

## 输入与输出

输入：来自前四个子 skill 的已确认 `FUN-XXX` 区块（含 BR/VL/ST/EX），外加来自 `project-background-goal` 的 Stage 1 目标 `G-XXX` 以提供量化阈值。输出：`AC-XXX` 行写入父级 `function-description.md` §2 分功能详述 中每个 FUN 的 `#### 验收依据` 小节，遵循 `src/templates/stage-2-product/function-description.md`。

分析前加载 `references/thinking-framework.md`（其引用 `src/framework/thinking-core.md` §1 强制透镜）。Draft 前加载 `references/output-contract.md`。交接前加载 `references/audit-checklist.md` 与 `references/reviewer-checklist.md`。Review 前运行 `scripts/validate_artifact.py <artifact> --json`。当成功定义或阈值稀疏时加载 `references/question-patterns.md`（主动向业务方确认成功标准）。

## 思考提示（按阶段）

### 1. Preflight
- "范围内有哪些 FUN-XXX？四个规则子 skill（BR/VL/ST/EX）都确认了吗？哪些 G-XXX 目标带可量化阈值？"
- **若某 P0 功能没有已确认的 BR/VL/ST/EX**，发出警告，不要在缺失上游之上编造 AC。
- 评估成熟度：L0（无成功定义）→ L1（单一稀疏提及）→ L2（部分阈值）→ L3（充分明确）→ L4（上游已确认）。

### 2. Intake
- "该功能已确认的成功定义是什么——来自 BR/VL/ST/EX，而非我的假设？"
- 保留 `FUN-XXX` → `G-XXX` / `ST-XXX` 链接。把 AC 隐含行为与上游规则的矛盾标为 `CONFLICT`。

### 3. Think (apply thinking-core.md §1 mandatory lenses + domain lenses)
- **First Principles**: "什么可观察结果能证明该功能可用？用户/操作者会看到什么？"
- **Testability**: "给定一组输入，任何人不看实现能否唯一判定通过或失败？"
- **Reverse Validation**: "从目标结果（G-XXX）反向推导，什么必须为真且可测量？"
- **Adversarial**: "我能否构造一个通过我的 AC 但仍然坏掉的反例？一个应该通过却被我的 AC 拒绝的用例？"
- **Atomicity**: "每条 AC 是否是一个行为，可独立运行、独立失败？"

### 4. Clarify
- 先从已确认的目标/BR/VL/EX 解析阈值；不要问 AI 能从来源推导出的内容。
- 剩余问题批量提交：AI 初步判断、依据、选项、影响、owner、阻断标志。
- 当答案改变成功定义、关键阈值或异常路径范围时，**停在 `needs_user_input`**。
- Limit: 每轮 ≤5 个问题，按影响排序。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
- 填 `AC-XXX` 行。每个 P0 FUN：≥1 条主流程 AC + ≥1 条异常/边界 AC。
- Status: 用 `draft`、`needs_user_input` 或 `conditional_review`——**永不 `confirmed`**。

### 6. Audit
- **Measurability（可测量性）**: 每个可量化结果都有阈值；无"快速"/"流畅"/"合理"。
- **Atomicity（原子性）**: 无捆绑的"并且"检查。
- **Traceability（可追溯性）**: 每个阈值追溯到已确认的 G-XXX；AI 推断的阈值标 `AI_INFERENCE`。
- **No Overlap（无重叠）**: AC 是对 BR/VL/ST/EX 的度量，而非重写；无测试用例或实现细节泄漏。
- 运行 `scripts/validate_artifact.py <artifact> --json`。修复所有 error；warning 在审计记录中说明。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
产品负责人确认完成定义；业务负责人确认阈值与 G-XXX 目标一致；测试评审可验证性（每条 AC 能否由构造的输入判定通过/失败）。
**只有授权人工可以批准。** 批准产生 ReviewRecord（SHA-256）。

### 8. Commit / Reflow
- 只有 `pipeline.py review --decision approve` 可写入 `confirmed`。
- 变更时：记录 delta → 更新受影响 AC 行 → 重跑 Audit → 返回 Human Gate。
- 上游的阈值或成功定义变更 → 回到最早受影响的 work item。

## 反模式

| ❌ 不要 | ✅ 要 |
|---|---|
| 把「系统应正常工作」/「提升体验」写成 AC | Given X, when Y, then 带量化阈值的可观察 Z |
| 用「快速」/「流畅」/「合理」却无基线 | ≤ 2 秒, ≥ 99.9%, 0 元 —— 追溯到 G-XXX |
| 用「并且」把多个检查捆绑进一条 AC | 一条 AC = 一个行为，可独立测试 |
| 写 `then 调用 checkBalance() 接口` | `then` 描述可观察结果，而非内部调用 |
| 描述 UI 而非结果（"弹窗显示…"） | 描述可观察的系统状态/结果 |
| 只为主路径写 AC | 每个 P0 FUN 有主流程 AC + ≥1 条异常/边界 AC |
| 编造与业务目标无关的阈值 | 每个阈值追溯到已确认的 G-XXX；标 AI_INFERENCE/UNKNOWN |
| 起草测试脚本或断言代码 | AC 是契约；测试用例是 QA 的职责 |

## 示例：充分输入 → 充分输出

**输入**: FUN-001（活动预约提交）含 BR-005（活动已结束驳回）、VL-001（姓必填）、EX-001（网络超时重试）、G2（预约成功率 ≥ 99%）。
**输出**: 3 条 `AC-XXX` 行——主流程（Given 已登录客人填写完整信息, when 点即刻预约, then ≤3s 内进入二次确认页, 关联 G2）、异常路径（Given 活动已结束, when 提交, then 展示"活动已结束"页且不创建预约）、边界（Given 姓为空, when 提交, then 姓输入框显示"请输入您的姓氏"）。

## 示例：稀疏输入 → 降级输出

**输入**: "验收标准你看着写"
**输出**: Preflight → 无已确认的成功定义 → Clarify 批量生成 3 个问题（成功定义是什么？关键量化阈值 G-XXX 是多少？异常路径接受哪些失败？）→ 只写有直接支撑的 AC 行，其余标 `UNKNOWN`，停在 `needs_user_input`。

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

每个 P0 功能至少有一条主流程 `AC-XXX` 与一条异常/边界 `AC-XXX`；每条 AC 是原子的且为 Given/When/Then；每个可量化结果都有追溯到已确认 G-XXX 的阈值；无测试用例或实现细节泄漏；AC 触发条件与预期结果与 BR/VL/EX 一致；阻断性未知项阻止确认；授权人工批准该基线。
