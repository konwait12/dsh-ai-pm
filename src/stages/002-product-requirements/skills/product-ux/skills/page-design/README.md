# Page Design · 页面设计

> **Sub-skill of** [`product-ux`](../SKILL.md)
> **输出章节**：父级 `product-ux.md` §2 页面设计（§2.1 页面与步骤描述 + §2.2 HTML 原型）
> **执行顺序**：2 / 3

## 用途

为 `functional-flow`（function-description 的功能流程）中的每个页面/步骤指定**入口、前置条件、主要内容、操作、下一状态**的骨架。让 dev 能据此构建 UI 结构，让 interaction-rules 能在其上定义交互反馈。

## 输入

- `functional-flow`（function-description）的 confirmed 功能流程（§2.1 主流程 / §2.2 分支流程 / §2.3 异常流程，含页面/步骤）
- `function-description` 的 `feature-list` 功能清单（FEA-XXX）

## 产物

`§2` 区块：

- **§2.1 页面与步骤描述**（必出）：七列——页面/步骤、所属功能、入口、前置条件、主要内容、操作、下一状态
- **§2.2 HTML 原型**（可选）：≥3 页或多方评审时，生成可点击原型（`99-review/support/prototype/`），仅作沟通载体

## 触发判断

- 看到 "页面设计" / "页面结构" / "页面清单" / "入口/前置条件" → 触发
- 看到 "功能流程" / "流程图" → **不触发**（走 `functional-flow`，在 function-description）
- 看到 "交互规则" → **不触发**（走 `interaction-rules`）

## 关键约束

- 每页一行七列齐全；每个页面 ≥1 个操作；每个操作有显式下一状态
- 页面清单与 `functional-flow` 功能流程对齐，无孤儿页面、无 AI 自造页面（自补须标 `AI_INFERENCE`）
- 不写视觉细节（颜色、字体、间距）、不写交互微细节、不写业务/校验/权限规则
- 原型是沟通辅助，不替代 §2.1 文本；忠于输入，不发明页面与状态

## 执行循环

Preflight → Intake → Think → Clarify → Generate → Audit → Human Gate → Commit / Reflow（详见 `SKILL.md`）。**永远不产 `confirmed`**；只有 `pipeline.py review --decision approve` 能写入。

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/anti-patterns.md` · AI 常见反模式
- `references/audit-checklist.md` · 审计清单
- `references/output-contract.md` · §2 输出契约
- `references/prototype-techniques.md` · 可点击原型技法（可选）
- `references/question-patterns.md` · Clarify 提问模板
- `references/reviewer-checklist.md` · 人工评审清单
- `references/source-handling.md` · 上游追溯规则
- `references/thinking-framework.md` · 思考框架（必读）
- `scripts/validate_artifact.py` · 产物校验
- `templates/page-design-output.md` · 输出模板
