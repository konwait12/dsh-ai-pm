# Interaction Rules · 交互规则

> **Sub-skill of** [`product-ux`](../SKILL.md)
> **输出章节**：父级 `product-ux.md` §3 交互规则 IX-XXX
> **执行顺序**：3 / 3（最后生成，约束前两层）

## 用途

为已确认页面上的每个可交互元素定义「用户操作 → 系统响应」的页面层规则 IX-XXX，覆盖触发条件、反馈时机、状态覆盖（loading/empty/error/disabled/timeout）、弹窗与导航、边界行为。

## 输入

- `functional-flow`（function-description）的 confirmed 功能流程（§2.1 主流程 / §2.2 分支流程 / §2.3 异常流程）
- `page-design` 的 confirmed 页面清单（§2 页面设计，含操作列）

## 产物

`§3` 区块（写作格式遵循 `rule-writing-format.md`）：

| 字段 | 说明 |
|---|---|
| ID | IX-001, IX-002, ...（唯一递增） |
| 规则描述 | 用户状态 + 动作 → 系统响应 |
| 触发条件 | 何时生效 |
| 系统响应 | 跳转/弹窗/toast/状态变化/文案 |
| 适用页面/功能 | PG-XXX / FEA-XXX |
| 来源 | 上游故事/流程/原始 SRC-* |

## 触发判断

- 看到 "交互规则" / "IX" / "输入约束" / "反馈时机" / "可访问性" / "a11y" → 触发
- 看到 "功能流程" → **不触发**（走 `functional-flow`，在 function-description）
- 看到 "页面设计" / "组件" → **不触发**（走 `page-design`）

## 关键约束

- 每条 IX 必须引用具体页面 + FEA；无孤儿规则
- 每条满足「触发条件 → 系统响应」，响应具体可测（无"合理提示"类模糊词）
- 状态覆盖 loading/empty/error/disabled/timeout；反馈明确成功/失败/加载中三态
- 不写数据校验（VL）、业务计算（BR）、权限规则、验收标准（AC）——命中即移交 function-description
- 不写视觉细节（颜色、间距）—— 用 token

## 执行循环

Preflight → Intake → Think → Clarify → Generate → Audit → Human Gate → Commit / Reflow（详见 `SKILL.md`）。**永远不产 `confirmed`**；只有 `pipeline.py review --decision approve` 能写入。

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/anti-patterns.md` · AI 常见反模式
- `references/audit-checklist.md` · 审计清单
- `references/output-contract.md` · §3 输出契约
- `references/question-patterns.md` · Clarify 提问模板
- `references/reviewer-checklist.md` · 人工评审清单
- `references/rule-writing-format.md` · 规则书写格式（必读）
- `references/source-handling.md` · 上游追溯规则
- `references/thinking-framework.md` · 思考框架（必读）
- `scripts/validate_artifact.py` · 产物校验
- `templates/interaction-rules-output.md` · 输出模板
