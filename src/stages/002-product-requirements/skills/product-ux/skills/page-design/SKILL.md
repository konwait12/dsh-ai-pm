---
name: page-design
description: 为已确认功能流程中的每一步定义页面骨架——入口触发、前置条件、主要内容区块、可用操作与下一状态——不含视觉设计。Sub-skill of product-ux，填充 product-ux.md 的 §2 页面设计（页面骨架）。
---

# Page Design · 页面设计

## 目的与边界

把已确认功能流程中的每一步转化为具体的页面/步骤骨架：用户如何到达、进入时哪些条件必须已成立、页面承载什么内容、用户可执行哪些操作、每个操作通向何处。产出必须能让 `interaction-rules`（补充 IX 行为）与 function-description（补充 BR/VL/AC）在不做二次解读的情况下直接消费。

**不得**指定视觉设计（颜色、字体、间距、组件样式）、编写交互微细节（动效、悬停、滚动、弹窗外观）、设计数据库模型，或定义业务/校验/权限规则。页面骨架是内容与导航契约，而非高保真原型（mockup）。

## 输入与输出

输入：来自 `functional-flow`（在 function-description 内）的已确认功能流程（§2.1 主流程 / §2.2 分支流程 / §2.3 异常流程）、来自 function-description 的 `feature-list` 功能清单（`FEA-XXX`），以及它们所追溯的已确认故事。输出：父级 `product-ux.md` 的 §2 页面设计（§2.1 页面与步骤描述 表格 + 需要时的 §2.2 HTML 原型 条目），遵循 `src/templates/stage-2-product/product-ux.md`。非独立产物。

分析前加载 `references/thinking-framework.md`（其引用 `src/framework/thinking-core.md` §1 强制透镜）。Draft 前加载 `references/output-contract.md`。交接前加载 `references/audit-checklist.md` 与 `references/reviewer-checklist.md`。Review 前运行 `scripts/validate_artifact.py <product-ux.md> --json`。当流程 ≥3 页或需要利益相关方评审视觉/观感时，加载 `references/prototype-techniques.md`。

## 思考提示（按阶段）

### 1. Preflight
- "从已确认功能流程中产出哪些页面/步骤？每个页面追溯哪个 FEA 与故事？"
- 从功能流程的 §2.1 主流程 / §2.2 分支流程 / §2.3 异常流程提取页面清单。任何未出现在流程中的页面必须被标记，不得静默新增。
- **若功能流程缺失或未确认**，返回 routing receipt 并 STOP——没有步骤可挂接时不能凭空发明页面骨架。

### 2. Intake
- "每个流程步骤对内容、操作与下一状态的真正含义是什么——而不是我认为好页面长什么样？"
- 逐字从流程中摘取：步骤名、入口边、到达该步骤的分支条件、出口边。
- 按 `src/framework/contracts.md` 将页面事实归类为 `FACT` / `DECISION` / `ASSUMPTION` / `AI_INFERENCE` / `UNKNOWN` / `CONFLICT`。
- 为补全而新增的内容区块或操作必须标记 `AI_INFERENCE`。

### 3. Think (apply thinking-core.md §1 mandatory lenses)
- **First Principles**: "用户在这里必须看到什么、做什么才能朝结果推进？哪些元素被假设但并非必需？"
- **Systems Thinking**: "此页面的操作是否链到某个数据源、另一角色的任务或外部服务？"
- **Adversarial**: "前置条件失败时会发生什么？是否存在绕过我所假设前置条件的入口路径？"
- **Reverse Validation**: "从下一状态反向推导，本页必须提供什么内容/操作，下一步才能运行？"
- **Confirmation Bias Defense**: "我是在设计需求方草图的页面，还是流程真正需要的页面？"
- **Knowledge Boundary**: "哪些页面事实已确认，哪些是我的结构推断？"

### 4. Clarify
- 先尝试自行消解可发现的缺口（复查流程分支、故事原文、角色定义）。
- 剩余问题批量提交：AI 初步判断、依据、选项、影响、owner、阻断标志。
- 当答案改变某 P0 页面的入口、前置条件、内容、操作或下一状态时，**停在 `needs_user_input`**。
- Limit: 每轮 ≤5 个问题。不问视觉样式（超出范围）或规则（下游技能）。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
- §2.1 表格中每个页面/步骤占一行：页面/步骤、所属功能、入口、前置条件、主要内容、操作、下一状态。
- 内容保持在"页面上有什么"层面；操作一行一条并带有明确的下一状态（含 停留本页 / 退出流程）。
- Status: 用 `draft`、`needs_user_input` 或 `conditional_review`——**永不 `confirmed`**。

### 6. Audit
- **Completeness（完整性）**: 功能流程中的每个页面都有对应行；无孤儿页面；每个页面 ≥1 个操作。
- **Action-NextState Closure（操作-下一状态闭环）**: 每个操作都有明确的下一状态；无悬空箭头。
- **Boundary（边界）**: 无视觉样式、无交互微细节、无 BR/VL/AC。
- **Traceability（可追溯性）**: 每行追溯 FEA-XXX 与一个流程步骤。
- 运行 `scripts/validate_artifact.py <product-ux.md> --json`。修复所有 error；warning 在审计记录中说明。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
Present: 页面清单、每页的入口/前置/操作/下一状态、所有标 `AI_INFERENCE` 的页面，以及任何越界到视觉设计的页面。
**产品负责人确认页面清单与导航；业务负责人确认前置条件与下一状态。** 批准产生 ReviewRecord（SHA-256）。

### 8. Commit / Reflow
- 只有 `pipeline.py review --decision approve` 可写入 `confirmed`。
- 变更时：记录 delta → 更新受影响行 → 重跑 Audit → 返回 Human Gate。
- 功能流程（来自 functional-flow）中某步骤的改变会使挂在其上的页面失效 → 回到受影响的页面，而非下游打补丁。

## 反模式

| ❌ 不要 | ✅ 要 |
|---|---|
| 把内容写成视觉布局（"顶部大按钮、下方蓝色卡片"） | 描述页面呈现哪些信息 |
| 只列操作、不给下一状态 | 每个操作都给出明确的下一状态（成功/失败/停留/退出） |
| 把多个操作揉进一句含糊的句子 | 一行一个操作，每个都有确定结果 |
| 新增功能流程之外的页面 | 每个页面追溯一个流程步骤 + FEA-XXX |
| 只设计主路径页面 | 覆盖正常/备选/错误/超时/取消/恢复等变体 |
| 偷塞交互微细节或规则 | 骨架保持在内容与导航层面 |
| 无理由按"屏幕数"拆页 | 按真实的状态/步骤差异拆分 |

## 示例：充分输入 → 充分输出

**输入**: "场地预约" FEA-001 的已确认功能流程含 4 步（列表→详情→填写→结果），外加已确认故事。
**输出**: §2.1 表格行——场地列表页 (入口: 首页导航; 前置: 已登录; 内容: 场地卡片列表+筛选; 操作: 筛选/查看详情/下拉刷新; 下一状态: 详情页/列表刷新)、场地详情页、填写页、结果页——每行都带有明确的入口/前置/操作/下一状态与知识状态标签。

## 示例：稀疏输入 → 降级输出

**输入**: "给预约流程做个页面吧"，没有任何已确认的流程步骤。
**输出**: Preflight 返回 L1（无流程）→ Intake 记录无页面材料 → Think 列出缺失（页面清单? 前置条件? 操作与下一状态?）→ Clarify 批量生成 ≤5 个问题 → 停在 `needs_user_input`。不从空白凭空发明任何页面行。

## 加载参考

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见反模式（写页面时对照规避） | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/output-contract.md` | §2 产出结构与 ID 契约 | Draft 前 |
| `references/prototype-techniques.md` | 可点击原型技法：先出页面清单经人工确认，再生成单文件 HTML；覆盖主流程与全部分支场景（≥3 页或多方评审时用） | 需原型时（可选） |
| `references/question-patterns.md` | Clarify 提问模板（8 类句式） | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单（Human Gate 用） | Human Gate 前 |
| `references/source-handling.md` | 上游追溯规则（FEA-/ST-/SRC- 引用） | Intake/追溯时 |
| `references/thinking-framework.md` | 思考透镜（Common Core + 页面领域 lens，必读） | 每次任务开始（必读） |

## 完成标准

已确认功能流程中的所有页面/步骤在 §2.1 都有对应行，含入口、前置条件、内容、操作与下一状态；每个页面至少有 1 个操作，每个操作都有明确的下一状态；页面清单与流程一致，无孤儿或凭空发明的页面；内容保持在信息与导航层面，无视觉、交互或规则泄漏；原型（如有）是沟通辅助而非表格的替代；在 interaction-rules 启动前，授权人工已批准页面骨架。
