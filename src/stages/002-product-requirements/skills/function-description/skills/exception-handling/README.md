# Exception Handling · 异常处理

> **Sub-skill of** [`function-description`](../SKILL.md)
> **输出章节**：§Exception（failure modes + user-visible recovery）
> **执行顺序**：4 / 5

## 用途

枚举每个功能的**失败模式与用户可见的恢复路径**：系统失败、业务驳回、外部依赖超时、降级策略、补偿事务。

## 输入

- `state-machine` 的 §State（提供状态迁移中的失败点）
- `business-rules` 的 §BR（提供业务驳回规则）
- 外部系统依赖清单

## 输出

`§Exception` 表格，每行一个 EX-XXX：

| 字段 | 说明 |
|---|---|
| 触发场景 | 何时进入该异常 |
| 系统响应 | 服务端动作（重试 / 补偿 / 告警） |
| 用户可见动作 | 错误提示、跳转、回退 |
| 重试策略 | 次数 / 间隔 / 退避 |
| 数据补偿 | 是否回写 / 回写哪些字段 |
| 关联 AC | 由 acceptance-criteria 覆盖 |

## 触发判断

- 看到 "异常处理" / "失败模式" / "重试" / "回滚" / "降级" → 触发
- 看到 "业务规则" / "字段校验" → **不触发**（走 `business-rules` / `validation-rules`）
- 看到 "状态机" → **不触发**（走 `state-machine`）

## 关键约束

- 每条 EX 必须有用户可见动作（不允许"沉默失败"）
- 重试策略必须明确次数与上限
- 涉及金钱/库存的失败必须有补偿事务
- 所有 EX 必须在 AC 中可被验证

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/anti-patterns.md` · AI 常见反模式
- `references/audit-checklist.md` · 审计清单
- `references/output-contract.md` · §Exception 输出契约
- `references/question-patterns.md` · Clarify 提问模板
- `references/reviewer-checklist.md` · 人工评审清单
- `references/source-handling.md` · 来源处理规则
- `references/thinking-framework.md` · 思考框架
- `scripts/validate_artifact.py` · 产物校验
- `templates/exception-handling-output.md` · 输出模板
