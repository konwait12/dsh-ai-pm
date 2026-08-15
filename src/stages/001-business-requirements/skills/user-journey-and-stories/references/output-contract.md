# 输出契约 · user-journey-and-stories

定义本 Skill 产出产物的结构、字段语义与状态转移。所有 AI 实现都必须符合本契约。

## 状态机（Status Machine）

与 project-background-goal Skill 相同的 6 种状态：

| 状态 | 含义 | 谁设置 |
|---|---|---|
| `draft` | AI 仍在工作中；尚未可评审 | AI |
| `needs_user_input` | 阻塞于人工回答；无法推进 | AI |
| `conditional_review` | 可评审，带有非阻断注意事项 | AI |
| `ready_for_human_review` | AI 工作完成；等待人工确认 | AI |
| `confirmed` | 人工已显式批准 | 仅人工 |
| `superseded` | 被更新的已确认版本取代 | 人工或 AI |

合法转移：
- `draft` → `needs_user_input` | `conditional_review` | `ready_for_human_review`
- `needs_user_input` → `draft` | `conditional_review` | `ready_for_human_review`
- `conditional_review` → `needs_user_input` | `ready_for_human_review` | `draft`
- `ready_for_human_review` → `confirmed` | `draft` | `superseded`
- `confirmed` → `superseded`
- `superseded` → (终止)

## 知识状态标签（Knowledge State Tags）

| 标签 | 含义 |
|---|---|
| `FACT` | 带来源证据的可验证陈述 |
| `DECISION` | 人工做出的选择，如实记录 |
| `ASSUMPTION` | 工作假设，尚未确认 |
| `AI_INFERENCE` | 由证据推导，需要人工核查 |
| `UNKNOWN` | 确实未知；需要调研 |
| `CONFLICT` | 两个或多个来源说法不一致 |

## 产物章节（Artifact Sections）

1. **预检输入充分度判定** (§0): 上游产物核验 + 模式分类
2. **业务生命周期分解** (§1): 业务生命周期阶段 × 角色
3. **用户旅程图** (§2): 按阶段（行）× 角色（列）的旅程图
4. **用户故事卡片** (§3): 派生的故事卡片，含规范格式 + 按角色分组列表
5. **旅程→故事覆盖矩阵** (§4): 从旅程条目到故事卡片的可追溯性
6. **路径类型覆盖检查** (§5): normal/alt/exception/failure/handoff/recovery 覆盖
7. **事实与决定** (§6): FACT/DECISION 寄存器
8. **假设、AI 推断、未知与冲突** (§7): ASSUMPTION/AI_INFERENCE/UNKNOWN/CONFLICT 寄存器
9. **待确认问题** (§8): 带结论的待决问题
10. **Clarifications**: Session 日志（见 Clarifications Session Contract）
11. **范围基线（In/Out/Deferred/Conditional 四分类）** (§10): In/Out/Deferred/Conditional 范围项 + 验收依据 + 来源追溯（见 Scope Baseline Section Format）
12. **来源追溯** (§11): 来源可追溯
13. **下游输入摘要** (§12): 给 product-ux 的交接摘要
14. **Constitution Compliance** (§13): 4 原则合规检查
15. **版本变更摘要** (§14): 版本历史

## 故事卡片格式（Story Card Format，规范）

```
在〈前提/场景〉下，作为〈角色〉，我希望〈动作〉，以便〈目标/价值〉
```

字段：
- `前提/场景`: 需求产生的情境或上下文
- `角色`: 具体角色（来自已确认背景 §6）
- `动作`: 角色想做什么
- `目标/价值`: 他们为什么想做——结果或价值

## 旅程条目格式（Journey Entry Format）

每个（阶段 × 角色）单元格必须包含：
- `触发`（trigger）: 什么事件为该角色启动此阶段
- `动作`（actions）: 角色做什么
- `触点`（touchpoints）: 交互发生在哪里
- `痛点`（pain points）: 背景 §4 中已知的问题
- `期望`（expected outcome）: 成功看起来什么样
- `类型`（path type）: normal / alternative / exception / failure / handoff / recovery
- `来源`（source）: 来自上游背景的 SRC-* 引用
- `知识状态`（knowledge state）: FACT / DECISION / ASSUMPTION / AI_INFERENCE / UNKNOWN / CONFLICT

## 范围基线章节格式（Scope Baseline Section Format，§范围基线 · In/Out/Deferred/Conditional 四分类）

产物必须包含 **范围基线** 章节——`journey-and-stories.md` 产物三大章节之一（范围基线 / 旅程 / 故事）。它把每个干系人期望或候选归入 **四类之一**，每类都由可验证的验收依据、知识状态标签与来源或决策支撑：

| 子标题 | 含义 | 判定 |
|---|---|---|
| 范围总览 | In/Out/Deferred/Conditional 四分类计数 | 先给计数，再列明细 |
| In-Scope | **In · 本期做**（已确认纳入本期） | 必须有可验证验收依据，模糊项不得列入 |
| Out-of-Scope | **Out · 本期不做**（已确认排除 + 原因） | 原因 = 约束 / 决议 / 未来工作，不得静默丢弃 |
| Deferred | **Deferred · 延后**（暂缓做 + 触发/重开条件） | 记录触发条件；低成本高不确定项优先延后 |
| Conditional | **Conditional · 条件触发**（条件成立则纳入） | 如"预算通过则…"/"法务签字则…"，是真实范围，必须显式列出 |

若某类无已确认内容，写 `待确认` 并链接到 §8 待确认问题 或 §7 UNKNOWN ID，不得删除该子标题。

### 范围项 Schema（Scope Item Schema，S-NNN）

每个范围项必须具备：

| 字段 | 必填 | 描述 |
|---|---|---|
| `S-NNN` (ID) | 是 | 本产物内单调递增 |
| `description` | 是 | 一句可测试的描述 |
| `knowledge_state` | 是 | FACT / DECISION / ASSUMPTION / AI_INFERENCE / UNKNOWN / CONFLICT |
| `source_or_decision` | 是 | SRC-* 或 DEC-*（可追溯） |
| `acceptance_criterion` | 是 (In) / 可选 (Out/Deferred/Conditional) | 如何判定完成或排除 |
| `stakeholder` | 可选 | 提出/负责该范围项的干系人 |
| `notes` | 可选 | 边界情况、依赖 |

**互斥性（Mutual Exclusivity）**: 一项不得同时 In 且 Out，也不得同时 In 且 Deferred。争议边界必须显式路由到决策者（goal decision owner / business sponsor），AI 不得自行裁决。

**下游交接（Downstream Handoff）**: confirmed 后，范围基线随 `journey-and-stories.md` 交接 product-ux：`in_count / out_count / deferred_count / conditional_count` + 范围项清单（S-NNN）+ 开放非阻断未知。

## Clarifications Session 契约（Clarifications Session Contract）

与 project-background-goal 相同格式：

| 字段 | 必填 | 描述 |
|---|---|---|
| `session_id` | 是 | CL-XXX，顺序递增 |
| `category` | 是 | scope / roles / lifecycle / coverage / priority |
| `question` | 是 | 提出的唯一问题 |
| `ai_preliminary_judgment` | 是 | 人工回答前 AI 的最佳猜测 |
| `options` | 是 | 适用时的 A/B/C 选项 |
| `decision_owner` | 是 | 谁必须回答 |
| `blocking` | 是 | yes/no——是否阻断确认？ |
| `deferral_risk` | 是 | 若延期会发生什么 |
| `accepted_answer` | 否 | 人工回答后填写 |
| `reflow_target` | 是 | 哪个章节接收答案 |
| `integrated_at` | 否 | ISO 时间戳 |
| `integrated_by` | 否 | AI / 人工 |
| `audit_recheck` | 否 | pass / fail |

每次调用本 Skill 至多 5 个 Session。若需要更多，设置 `needs_user_input`。

## 覆盖要求（Coverage Requirements）

旅程 + 故事的组合必须覆盖：

1. **上游背景中所有已确认角色**
2. **业务领域隐含的所有生命周期阶段**
3. **适用的六种路径类型**：normal、alternative、exception、failure、handoff、recovery
4. **旅程 → 故事覆盖矩阵中无无解释的缺口**
