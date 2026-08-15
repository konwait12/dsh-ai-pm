# Business Rules · 业务规则

> **Sub-skill of** [`function-description`](../SKILL.md)
> **输出章节**：§BR（domain rules table）
> **执行顺序**：1 / 5（首个执行，建立规则底座）

## 用途

把 `product-ux` 中已确认的 FEA-XXX 翻译为**领域级业务规则**：约束、计算公式、策略。BR 是后续 §VL（字段校验）、§State（状态机）、§Exception（异常）、§AC（验收）的基础。

## 输入

- `product-ux` 的 confirmed artifact（包含 FEA-XXX 与 UX 步骤）
- `project-background-goal` 的事实与决定（提供合规与业务策略上下文）

## 输出

`§BR` 表格，每行一个 BR-XXX：

| 字段 | 说明 |
|---|---|
| ID | BR-001, BR-002, ... |
| 规则描述 | 用 EARS 句式（参见 `references/ears-syntax.md`） |
| 适用功能 | FEA-XXX |
| 适用条件 | 触发场景 |
| 例外路径 | 何时不适用 / 走异常流程 |
| 来源 | upstream artifact + 决议人 |

## 触发判断

- 看到 "业务规则" / "BR" / "领域约束" / "计算公式" / "策略" → 触发
- 看到 "字段校验" / "格式" → **不触发**（走 `validation-rules`）
- 看到 "状态机" / "状态转换" → **不触发**（走 `state-machine`）

## 关键约束

- 每个 BR 必须独立可追溯到 FEA-XXX 和一个上游决议
- 不重复定义字段级校验（交给 `validation-rules`）
- 不写实现细节（数据库表、API）

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/audit-checklist.md` · 审计清单
- `references/output-contract.md` · §BR 输出契约
- `references/thinking-framework.md` · 思考框架
- `scripts/validate_artifact.py` · 产物校验
- `templates/business-rules-output.md` · 输出模板
