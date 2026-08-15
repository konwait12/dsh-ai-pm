# Feature List · 功能清单

> **Sub-skill of** [`function-description`](../../SKILL.md)
> **输出章节**：§功能清单（FEA-XXX 功能总账）
> **执行顺序**：1 / 7（首个执行，建立功能总账）

## 一句话

把已确认的用户故事（ST-XXX）分解为可追溯、边界清晰不重叠、带 P0/P1 优先级的功能清单（FEA-XXX），作为下游所有 function-description 子 skill 消费的功能总账。

## 触发判断

- 看到 "功能清单" / "FEA" / "从故事拆功能" / "功能列表" → 触发
- 看到 "功能流程" / "交互规则" / "页面设计" → **不触发**（走 functional-flow / product-ux 子 skill）
- 看到 "业务规则" / "字段校验" / "状态机" → **不触发**（走对应规则子 skill）

## 输入

- `user-journey-and-stories` 的 confirmed artifact（ST-XXX + 范围基线）
- `project-background-goal` 的事实与目标（提供范围上下文）

## 输出

`§功能清单` 表，每行一个 FEA-XXX：

| 字段 | 说明 |
|---|---|
| ID | FEA-001, FEA-002, ... |
| 功能名称 | 内聚能力名 |
| 所属故事 ST | ≥1 个 ST-XXX |
| 优先级 | P0 / P1 / P2 + 理由 |
| 一句话描述 | 边界：做什么 + 不做什么 |
| 来源 | ST-XXX / 决策 |

## 关键约束

- 每个 FEA 必须追溯 ≥1 个 ST-XXX；功能边界清晰不重叠；P0/P1 优先级标注
- 不写 UX / 交互 / 页面（交给 product-ux）
- 不写业务规则 / 字段校验 / 状态机 / 异常 / 验收（交给对应子 skill）

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/audit-checklist.md` · 审计清单
- `references/output-contract.md` · §功能清单 输出契约
- `references/thinking-framework.md` · 思考框架
- `scripts/validate_artifact.py` · 产物校验
