# Acceptance Criteria · 验收标准

> **Sub-skill of** [`function-description`](../SKILL.md)
> **输出章节**：§AC（Given/When/Then + 量化阈值）
> **执行顺序**：5 / 5（**最后执行**，覆盖前 4 个 sub-skill）

## 用途

为每个 P0 功能写出**可独立测试的验收标准**。AC 是 dev → QA → 业务的"完成定义"统一语言。

## 输入

- 前 4 个 sub-skill 的全部章节（BR / VL / State / Exception）
- `project-background-goal` 中的 G-X 目标（用于量化阈值）

## 输出

`§AC` 表格，每行一个 AC-XXX：

| 字段 | 说明 |
|---|---|
| ID | AC-001, AC-002, ... |
| 适用功能 | FUN-XXX |
| Given | 前置条件（EARS） |
| When | 触发动作（EARS） |
| Then | 期望结果（含量化阈值） |
| 关联 G-X | 引用的 Stage 1 目标 ID |
| 异常路径 | 可选：覆盖一条异常分支 |

## 触发判断

- 看到 "验收标准" / "AC" / "Given When Then" / "完成定义" → 触发
- 看到 "测试用例" / "测试脚本" → **不触发**（AC 是契约，测试用例由 QA 编写）
- 看到 "字段校验" / "状态机" → **不触发**（走前 4 个 sub-skill）

## 关键约束

- 每个 AC 必须**可独立测试**（不依赖其他 AC）
- 阈值必须量化（不允许"快"/"好"/"响应及时"等模糊词）
- 主流程与至少一条异常路径各写一个 AC
- 关联 G-X 失败 → 触发 reflow

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/anti-patterns.md` · AI 常见反模式
- `references/audit-checklist.md` · 审计清单
- `references/output-contract.md` · §AC 输出契约
- `references/question-patterns.md` · Clarify 提问模板
- `references/reviewer-checklist.md` · 人工评审清单
- `references/source-handling.md` · 来源处理规则
- `references/thinking-framework.md` · 思考框架
- `scripts/validate_artifact.py` · 产物校验
- `templates/acceptance-criteria-output.md` · 输出模板
