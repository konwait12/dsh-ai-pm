---
name: product-ux
description: Define page skeletons and interaction rules (IX) from confirmed journey and stories. Pure UX — page design (§页面设计) + interaction rules (§交互规则). Feature lists and functional flows belong to function-description.
---

# 产品 UX（Product UX）

## 目的与边界（Purpose And Boundary）

把已确认的旅程与故事转化为页面骨架（WHERE 内容放在哪）与交互规则（IX，HOW 用户如何交互）——达到业务方可评审、function-description 无需重新解读即可使用的粒度。

本 Skill 只拥有 **UX 层**：页面骨架（§页面设计，由 `page-design` 产出）与交互规则（§交互规则，由 `interaction-rules` 产出）。**不要做 功能清单（feature lists）或 功能流程（functional flows）**——那些属于 `function-description`。业务规则（BR）、校验（VL）与验收标准（AC）也属于 function-description——**不要在这里泄出**。

**不要**：设计视觉 UI（颜色/字体）、写业务规则、定义验收标准、产出功能清单或功能流程、发明未追溯到已确认故事的新页面，或用原型代替书面规则。

## UX 层模型（UX Layer Model）

```
页面设计 (§页面设计)  → 页面骨架：WHERE 内容放在哪，入口→内容→操作→下一状态
交互规则 (§交互规则)  → IX-XXX：HOW 用户如何交互，触发 → 系统响应（正常/错误/空/加载/边界）
```

这模仿资深 PM 排定 UX 定义顺序的方式：先页面（内容的结构/布局），再管辖每个页面的交互规则。

## PM 专属交付物（PM-Specific Deliverables）

- **页面骨架**：入口触发 + 前置条件 + 内容区 + 可用操作 + 下一状态——不是视觉设计
- **IX 规则**：触发 → 系统响应，覆盖正常 + 错误 + 空 + 加载 + 边界状态
- **故事可追溯**：每个页面与规则都追溯到 ≥1 个已确认 ST——无孤儿页面/规则
- **原型作为沟通辅助**：可点击 HTML 可以伴随规格，但绝不替代书面规则

## 输入与输出（Inputs And Outputs）

**输入**：已确认的 `user-journey-and-stories`（故事、范围基线、角色、生命周期）。
**输出**：单一 `product-ux.md`，含**两个章节**——§页面设计（页面骨架，`page-design` 子 skill）、§交互规则（IX 规则，`interaction-rules` 子 skill）。

分析前加载 `references/thinking-framework.md`（→ `thinking-core.md` §1 必用）。

## 思考提示词（按阶段）（Thinking Prompts per stage）

### 1. Preflight
- "所有故事都确认了吗？范围基线（in/out）是什么？"
- 核验上游。提取：已确认故事（ST-XXX）、范围基线、角色、生命周期阶段、开放的非阻断项。
- 如果范围基线缺失 → 标记并返回上游。

### 2. Intake
- "已确认的故事隐含哪些页面？哪些交互元素需要规则？"
- 从已确认故事派生候选页面。有故事无页面 → 缺口。有页面无故事追溯 → 越界。

### 3. Think

**阶段 A — 页面设计（page skeletons）**
- "存在哪些页面？用户在每个页面能做什么？接下来发生什么？"
- 页面骨架：入口 → 前置条件 → 内容 → 操作 → 下一状态。不是视觉设计。

**阶段 B — 交互规则（IX）**
对每个页面的交互元素，设计：
- 正常：快乐日触发 → 响应
- 备选流程：不同的合法路径
- 错误状态：失败时用户看到什么
- 空状态：没有数据时显示什么
- 加载状态：等待时显示什么
- 边界情况：边界条件

### 4. Clarify
- 批量提问关于：页面边界、交互行为、对用户可见的状态转移。
- 不要问业务规则（属于 function-description）。
- 页面/交互设计缺少参考时，触发 `competitive-research`（竞品调研）。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
按 2 个有序阶段（A→B）填模板。单一产物 `product-ux.md` 含两个章节，两章节都委托给子 skill，它们把各自的章节写进同一个文件：
- §页面设计 —— 委托 `page-design` 子 skill 产出（页面骨架：入口/前置条件/内容/操作/下一状态）
- §交互规则 —— 委托 `interaction-rules` 子 skill 产出（IX-XXX 规则表）

功能清单（feature-list）与功能流程（functional-flow）不在此产出，归 `function-description`。

原型（HTML）可以伴随规格作为沟通辅助，但书面规则仍然权威。若生成原型，参考 `skills/pm-scaffold/` 工具链集成清单中的原型 skill pipeline。

### 6. Audit
- **IX 密度**：存在交互元素时 IX 规则 ≥3 条（过度欠定义时校验器会警告）。
- **状态完整性**：每个页面都覆盖正常 + 错误 + 空 + 加载 + 边界。
- **故事可追溯**：每个页面与规则都追溯到 ≥1 个已确认 ST。
- **无 BR/VL/AC 泄露**：扫描业务规则关键词（format/regex/formula/permission/only-admin-can）。
- **无功能清单/流程泄露**：功能清单与功能流程归 function-description，不在 product-ux 产出。
- 运行校验器。修复所有错误。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
呈现：页面骨架、IX 规则、覆盖缺口。
**产品负责人确认**范围与交互行为。业务负责人确认与范围基线一致。

### 8. Commit / Reflow
批准后 → 确认基线。交接给 `function-description`：页面骨架、IX 规则、开放的非阻断项。
范围变化 → 返回 user-journey-and-stories。页面/规则变化 → 重新进入本 Skill。

## 反模式（Anti-Patterns）

| ❌ 不要 | ✅ 要做 |
|---|---|
| 在 product-ux 产出 功能清单/功能流程 | 路由到 function-description；UX 只覆盖页面 + IX 规则 |
| 在 UX 规格里定义 BR（"字段必须 ≤30 字符"） | 路由 BR 到 function-description；UX 只定义 IX |
| 跳过错误/空/加载状态（"开发者会想出来的"） | 定义每个状态——这正是 PM 增值最多的地方 |
| 把原型当规格 | 书面 IX + 页面骨架是权威；原型只是沟通辅助 |
| 把页面设计成视觉布局 | 页面骨架 = 入口/前置条件/内容/操作/下一状态——不是像素位置 |

## 示例：规范交互规则（Example: Well-Formed Interaction Rule）

```markdown
| IX-011 | I11 | 用户点场次选择器 | 进入日期+时间选择页；默认选中最近可用日期；名额满的置灰 | 无可用场次→提示"所有场次已满" | BRD I11 |
```

## 加载参考文档（Load References）

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见反模式 | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/output-contract.md` | 产物结构与 ID 契约（一个产物 2 章节：§页面设计→`page-design`，§交互规则→`interaction-rules`） | Draft 前 |
| `references/question-patterns.md` | Clarify 提问模板 | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单 | Human Gate 前 |
| `references/source-handling.md` | 来源处理规则 | Intake 时 |
| `references/thinking-framework.md` | 思考透镜 (Common Core + 领域 lens) | 每次任务开始 |

## 完成标准（Completion）

所有已确认故事都由 ≥1 个页面骨架 + 覆盖每个交互元素的 IX 规则代表；每个 P0 页面有 ≥3 条 IX 规则 + 错误/空/加载/边界状态；页面骨架覆盖所有交互触点；无功能清单/流程/BR/VL/AC 泄露；原型（若生成）只是沟通辅助而非规则替代；且获得授权的人类批准基线。
