---
name: feature-list
description: 功能清单——从已确认的用户故事（ST-XXX）分解出功能清单（FEA-XXX），每个功能可追溯、边界清晰不重叠、带 P0/P1 优先级。function-description 编排的第一个子 skill。
---

# Feature List · 功能清单

## 目的与边界

把已确认的用户故事（ST-XXX）分解为产品必须交付的完整功能清单（FEA-XXX）——这是下游所有 function-description 子 skill 消费的唯一功能总账。每个 FEA-XXX 必须追溯 ≥1 个已确认的 ST-XXX，必须有清晰、互不重叠的功能边界，必须标注 P0/P1 优先级。

**Do not** 设计功能流程（→ `function-description`/`functional-flow`）、交互规则（→ `product-ux`/`interaction-rules`）、页面骨架或原型（→ `product-ux`/`page-design`）、领域业务规则（→ `business-rules`）、字段校验（→ `validation-rules`）、状态机（→ `state-machine`）、异常与失败处理（→ `exception-handling`）、验收依据（→ `acceptance-criteria`）。功能清单只命名「做什么（WHAT）」；行为细节由其他子 skill 定义。

## 输入与输出

**Input**: 已确认的 `user-journey-and-stories` 故事（ST-XXX）与范围基线，以及影响范围的已确认 `project-background-goal` 事实与目标。**Output**: 父产物 `function-description.md` 的 §功能清单 章节（registry `output_section`: 功能清单），模板由 `src/templates/resolver.py function-description.md` 解析。

分析前加载 `references/thinking-framework.md`（引用 `src/framework/thinking-core.md` §1 必用透镜 + §2 检查透镜）。草拟前加载 `references/output-contract.md`。送审前加载 `references/audit-checklist.md` 与 `references/reviewer-checklist.md`。评审前运行 `scripts/validate_artifact.py <父产物> --json`。

## 思考提示（按阶段）

### 1. Preflight
- "所有上游故事都已确认吗？范围基线（in/out）是什么？"
- 枚举已确认的 ST-XXX、角色与生命周期阶段；发现缺失归属或矛盾故事时，先标 `CONFLICT` 再写任何 FEA。
- **若不存在任何已确认故事**，返回 routing receipt 并 STOP——不要进入 Intake。

### 2. Intake
- "每个已确认故事实际要求系统做什么——而不是我认为它意味着什么？"
- 把每个已确认故事映射到 ≥1 个 FEA；有故事无功能 → 覆盖缺口，有功能无故事 → 范围越权。
- 每个候选都保留 `ST-XXX` 链接；不静默合并不同故事的诉求为一个功能。

### 3. Think (apply thinking-core.md §1 mandatory lenses)
- **First Principles**: "功能必须产出什么可观察的结果？哪些功能其实是伪装成需求的假设？"
- **Systems Thinking**: "哪些功能相互依赖？每个功能需要什么数据或上游能力？"
- **Role Perspective**: "对每个角色——哪些功能服务他们，砍掉某功能他们会失去什么？"
- **Constraint Analysis**: "哪些硬约束（范围、法务、平台、时间线）限定了功能集合？"
- **Adversarial**: "是否会有两个功能重叠到让用户不知道该去哪？哪个功能实际上是冗余的？"
- **Reverse Validation**: "从已确认故事反向推导，必须存在哪些功能，每条故事才能被满足？"

### 4. Clarify
- 先自行调研可发现的事实（现有产品规格、竞品界面、公开数据）。
- 剩余问题批量提交：AI 初步判断、依据、选项、影响、owner、阻断标志。
- 当功能边界或范围决策改变必须构建的内容时，**停在 `needs_user_input`**。
- Limit: 每轮 ≤5 个问题，按影响排序。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
- 填 §功能清单 表。一行一个功能，强制列：ID / 功能名称 / 所属故事 ST / 优先级 / 一句话描述 / 来源。
- Status: 用 `draft`、`needs_user_input` 或 `conditional_review`——**永不 `confirmed`**。

### 6. Audit
- **Traceability**: 每个 FEA-XXX 链接 ≥1 个 ST-XXX；反向检查每个 P0 ST-XXX 有 ≥1 个 FEA。
- **Non-overlap**: 没有两个 FEA 目的相同或边界含糊；每项动作只能归属一个功能。
- **Priority**: 每个 FEA 有 P0/P1/P2 及理由；P0 = 缺它就无法满足某个已确认故事。
- **Consumability**: 每个 FEA 的一句话描述足以让 `functional-flow` / `business-rules` 直接消费，无需回头重研故事。
- 运行 `scripts/validate_artifact.py <父产物> --json`。修复所有 error；warning 在审计记录中说明。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
Present 候选 §功能清单、证据摘要（每条功能由哪个故事支撑）、未知项及其影响、需做的决策、审计结果、变更摘要。
**只有产品负责人 / 业务负责人可以批准。** 批准产生 ReviewRecord（SHA-256）。

### 8. Commit / Reflow
- 只有 `pipeline.py review --decision approve` 可写入 `confirmed`。
- 变更时：记录 delta → 更新受影响 FEA 行 → 重跑 Audit → 返回 Human Gate。
- 后续发现故事/范围矛盾 → 从本 Skill 开头重进（而非下游打补丁）。

## 反模式

| ❌ 不要 | ✅ 要 |
|---|---|
| 一个故事拆成 5 个无新增信息量的微功能 | 一个 FEA 对应一个内聚能力；粒度与故事匹配 |
| 写 "FEA-002: 客户管理" 无边界 | 写 "FEA-002: 客户名单导入" 并明示 in/out |
| 无 ST 链接凭空造功能 | 每个 FEA 追溯 ≥1 个已确认故事 |
| 功能互相重叠（活动创建 vs 活动编辑 vs 活动发布混在一起） | 画清边界，重叠则合并或拆分至互斥 |
| 全部标 P0 | 用 MoSCoW：P0 = 缺它旅程无法完成 |
| 把 UX 文案、页面布局抄进清单 | 清单只写 WHAT；UX/IX/页面属于 product-ux |
| 为 1 行故事写 5 页描述 | 产出密度与输入密度匹配，稀疏时降级 |

## 示例：充分输入 → 充分输出

**Input**: confirmed `user-journey-and-stories`，ST-001..ST-006（客户邀约活动：名单导入、活动创建、邀约发放、客户接受/拒绝、二次催办、效果看板）。
**Output**: §功能清单 FEA-001..FEA-006 —— 每项追溯 ST-XXX、P0/P1 优先级带理由、边界互不重叠、来源可查。

## 示例：稀疏输入 → 降级输出

**Input**: confirmed 一行 "给 VIP 客户发邀请"，无名单来源、无活动配置、无响应流程。
**Output**: Preflight 判定 L1 → Intake 登记单一候选为 `UNKNOWN` → Think 识别缺失：名单从哪来? 邀约如何发放? 客户如何响应? → Clarify 生成 3 个问题 → 停在 `needs_user_input`。不为凑表格而编造 FEA。

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

每个已确认故事都由 ≥1 个 FEA-XXX 表达；每个 FEA 追溯 ≥1 个已确认的 ST-XXX；功能边界清晰且互不重叠；P0/P1 优先级带理由说明；无 UX/规则内容泄漏；功能密度与输入密度匹配；阻断性未知项阻止确认；在启动下游子 skill 前，授权产品/业务负责人批准 §功能清单 基线。
