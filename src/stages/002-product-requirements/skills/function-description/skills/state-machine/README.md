# State Machine · 状态机

> **Sub-skill of** [`function-description`](../SKILL.md)
> **输出章节**：§State（states × events → target states + guards）
> **执行顺序**：3 / 5

## 用途

枚举每个领域实体的**状态、事件、目标状态与守卫条件**。状态机是后续 §Exception（异常处理）与 §AC（验收）的关键依据。

## 输入

- `business-rules` 的 §BR（提供状态迁移的业务约束）
- `product-ux` 的状态定义与页面流

## 输出

`§State` 表格 + 状态机 Mermaid 图：

| 字段 | 说明 |
|---|---|
| 实体 | 实体名（如 Order / Candidate / Article） |
| 当前状态 | State-A, State-B, ... |
| 事件 | event-1, event-2, ... |
| 目标状态 | next state |
| 守卫条件 | EARS 句式 |
| 副作用 | 写哪些字段、发哪些通知 |

## 触发判断

- 看到 "状态机" / "状态转换" / "生命周期" / "state" → 触发
- 看到 "字段校验" / "格式" → **不触发**（走 `validation-rules`）
- 看到 "异常处理" / "失败重试" → **不触发**（走 `exception-handling`）

## 关键约束

- 初始状态、终止状态必须显式定义
- 非法状态转换必须定义"被拒"行为
- 守卫条件不能与 BR 冲突

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/audit-checklist.md` · 审计清单
- `references/output-contract.md` · §State 输出契约
- `references/thinking-framework.md` · 思考框架
- `scripts/validate_artifact.py` · 产物校验
- `templates/state-machine-output.md` · 输出模板
