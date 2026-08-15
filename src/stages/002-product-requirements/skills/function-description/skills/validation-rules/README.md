# Validation Rules · 字段校验规则

> **Sub-skill of** [`function-description`](../SKILL.md)
> **输出章节**：§VL（field-level + cross-field checks）
> **执行顺序**：2 / 5

## 用途

把 `business-rules` 的领域策略翻译为**字段级与跨字段校验规则**：必填、格式、范围、错误消息。VL 决定数据能否进入系统。

## 输入

- `business-rules` 的 §BR 表格（已 confirmed）
- `product-ux` 中页面与字段定义

## 输出

`§VL` 表格，每行一个 VL-XXX：

| 字段 | 说明 |
|---|---|
| ID | VL-001, VL-002, ... |
| 适用字段 | 字段名（中文/英文） |
| 校验类型 | 必填 / 格式 / 范围 / 枚举 / 跨字段 |
| 规则表达式 | EARS 句式 |
| 错误消息 | 用户可见的中文错误消息（≤ 30 字） |
| 关联 BR | 引用 BR-XXX |

## 触发判断

- 看到 "字段校验" / "VL" / "字段格式" / "错误消息" / "必填" → 触发
- 看到 "业务策略" / "计算公式" → **不触发**（走 `business-rules`）
- 看到 "状态转换" / "异常处理" → **不触发**（走 `state-machine` / `exception-handling`）

## 关键约束

- 每条 VL 必须关联一条 BR（不能凭空定义校验）
- 错误消息必须中文且 ≤ 30 字
- 跨字段校验明确列出"触发字段"与"受影响字段"
- 校验失败时是否阻塞提交由 `acceptance-criteria` 决定

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/audit-checklist.md` · 审计清单
- `references/output-contract.md` · §VL 输出契约
- `references/thinking-framework.md` · 思考框架
- `scripts/validate_artifact.py` · 产物校验
- `templates/validation-rules-output.md` · 输出模板
