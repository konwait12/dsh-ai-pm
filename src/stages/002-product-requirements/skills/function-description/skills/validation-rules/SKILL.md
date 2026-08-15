---
name: validation-rules
description: 定义系统校验规则 VL-XXX——格式、范围、长度、必填、唯一性、跨字段约束——每条都带用户可见的错误提示。function-description 编排的第二个规则子 skill。
---

# Validation Rules · 系统校验

## 目的与边界

在字段层面精确定义系统接受与拒绝什么数据，以及校验失败时用户看到什么。每条 VL 必须可判定（开发者能实现该检查、测试者能构造通过/失败用例），且必须携带面向用户的中文错误提示。

**不得**定义业务计算或领域策略（→ business-rules `BR-XXX`）、描述错误如何展示（→ interaction-rules `IX-XXX`）、建模状态变化（→ state-machine）或编写验收测试（→ acceptance-criteria `AC-XXX`）。

## 输入与输出

**输入**: 功能集合的已确认 §业务规则（`BR-XXX`）、已确认的 `product-ux` 字段定义（F-XXX）与已确认的范围基线。**输出**: 父级 `function-description.md` 的 §系统校验 章节（registry `output_section`: 系统校验），使用由 `src/templates/resolver.py function-description.md` 解析的模板。

分析前加载 `references/thinking-framework.md`（其引用 `src/framework/thinking-core.md` §1 强制透镜 + §2 检查透镜）。Draft 前加载 `references/output-contract.md`。交接前加载 `references/audit-checklist.md` 与 `references/reviewer-checklist.md`。Review 前运行 `scripts/validate_artifact.py <artifact> --json`。

## 思考提示（按阶段）

### 1. Preflight
- "§业务规则 与字段定义都已确认吗？哪些 FUN-XXX 区块有用户输入？"
- 枚举每个带用户输入字段的功能。写 VL 前，把任何输入未充分定义的功能标出来。
- **若不存在任何已确认的字段定义**，返回 routing receipt 并 STOP——不要进入 Intake。

### 2. Intake
- "已确认的 UX 实际定义的输入面是什么——而不是我认为表单有什么？"
- 列出每条输入路径：表单字段、搜索/筛选参数、上传文件、查询参数、批量粘贴数据，以及隐藏输入（URL 参数、用户可改写的默认值）。
- 按 `src/framework/contracts.md` 为每个 VL 候选标记知识状态：`FACT` / `DECISION` / `AI_INFERENCE` / `UNKNOWN`。在每个候选上保留 BR-XXX / FEA-XXX 来源。

### 3. Think (apply thinking-core.md §1 mandatory lenses)
- **First Principles**: "为安全接受该输入，系统真正需要的最小检查集合是什么？哪些检查是发明出来的装饰？"
- **Systems Thinking**: "该字段的有效性影响哪些其他字段、BR 规则或下游步骤？"
- **Role Perspective**: "谁输入这个数据？真实用户会误输什么？恶意用户会尝试什么？"
- **Constraint Analysis**: "检查必须强制的硬限制（长度、字符集、业务域取值）是什么？"
- **Adversarial**: "某个值是否可能通过所有检查仍破坏下游？某个合法值是否可能被误拒（过度校验）？"
- **Reverse Validation**: "从'合法数据进入系统'反向推导，每个字段的格式、范围与跨字段关系必须满足什么？"

### 4. Clarify
- 先自行调研可发现的事实（既有格式、码表、系统日志）。
- 剩余问题批量提交：AI 初步判断、依据、选项、影响、owner、阻断标志。
- 当校验边界或错误提示措辞改变数据接受、成本或风险时，**停在 `needs_user_input`**。
- Limit: 每轮 ≤5 个问题，按影响排序。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
- 填 §系统校验 表。一行一条检查：字段、检查类型（必填/格式/范围/长度/枚举/跨字段/唯一性）、规则表达式、触发时机、错误提示、来源。
- 每条 VL 携带面向用户的中文错误提示，说明"哪里错了 + 如何修改"——不得使用内部错误码。
- Status: 用 `draft`、`needs_user_input` 或 `conditional_review`——**永不 `confirmed`**。
- 按需产出字段定义表（并入老版字段规则说明：字段名称、类型、长度、校验规则、来源），字段须引用来源（上游 IX/FUN）与关联校验 VL-XXX。

### 6. Audit
- **Decidability（可判定性）**: 每条 VL 有可执行的值域；无缺格式的"校验手机号格式"。
- **Error message（错误提示）**: 每条 VL 有面向用户的提示；无英文/内部码。
- **Coverage（覆盖）**: 每个用户输入字段有 ≥1 条 VL；无隐藏输入缺口；不在只读/系统字段上做校验（永不触发的规则）。
- **Cross-field（跨字段）**: 选 B 时 A 必填的依赖与引用的 BR/UX 一致。
- **字段定义表（按需）**：如产出，表头含「字段名/类型」，每个 F-XXX 有来源引用与关联 VL；缺失仅记 warning，记入审计说明。
- 运行 `scripts/validate_artifact.py <artifact> --json`。修复所有 error；warning 在审计记录中说明。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
Present 候选 §系统校验、证据摘要（每条 VL 由哪个字段/BR 支撑）、未知项与影响、需做的决策、审计结果、变更摘要。
**只有产品负责人 / 业务负责人可以批准。** 批准产生 ReviewRecord（SHA-256）。

### 8. Commit / Reflow
- 只有 `pipeline.py review --decision approve` 可写入 `confirmed`。
- 变更时：记录 delta → 更新受影响 VL → 重跑 Audit → 返回 Human Gate。
- 上游字段或 BR 变更 → 从本 Skill 开头重进（而非下游打补丁）。

## 反模式

| ❌ 不要 | ✅ 要 |
|---|---|
| 写「系统应校验手机号格式」 | 写「VL-003: 手机号格式 ^1[3-9]\d{9}$, 错误提示: '请输入有效的 11 位手机号'」 |
| 错误提示写 "Invalid input" / 错误码 E002 | 面向用户的中文：「邮箱格式不正确，示例: name@domain.com」 |
| 编造「密码必须 8 位」却无来源 | 说明来源（BR / 安全策略）；否则标 UNKNOWN 并提问 |
| 只校验可见表单框 | 也枚举隐藏输入（URL 参数、可被改写的默认字段） |
| 所有失败共用一条通用提示 | 区分 必填缺失 / 格式错误 / 超出范围 / 已存在冲突 |
| 校验系统自动生成的字段 | 跳过只读/系统字段——永不触发的规则是噪音 |

## 示例：充分输入 → 充分输出

**输入**: 已确认的 FEA-003（注册），含 BR-005（密码策略）与字段定义（手机号、邮箱、密码、确认密码）。
**输出**: §系统校验 含 VL-001..VL-005——手机号格式、邮箱格式、密码长度 + 字符集、确认密码一致（跨字段）——每条都带中文错误提示与可追溯来源。

## 示例：稀疏输入 → 降级输出

**输入**: 一行已确认文字 "注册要校验手机号和密码"，无格式、无长度、无规则。
**输出**: Preflight 返回 L1 → Intake 将两个字段枚举为 `UNKNOWN` → Think 识别缺失：手机号字符集/国家? 密码长度? 确认密码行为? → Clarify 生成 3 个问题 → 停在 `needs_user_input`。不用猜测值编造任何 VL。

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

每个 P0 FUN-XXX 的每个用户输入字段有 ≥1 条可判定的 VL-XXX，带面向用户的中文错误提示；每条 VL 可追溯到 BR-XXX / FEA-XXX / 字段定义；无隐藏输入缺口、无永不触发的规则；跨字段约束与上游一致；阻断性未知项阻止确认；授权人工批准 §系统校验 基线。
