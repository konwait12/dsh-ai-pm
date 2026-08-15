# Functional Flow · 功能流程

> **Sub-skill of** [`function-description`](../SKILL.md)
> **输出章节**：父级 `function-description.md` §功能流程（主流程 / 分支流程 / 异常流程）
> **执行顺序**：2 / 7（在功能清单之后、业务规则之前生成流程结构）

## 用途

把已确认的功能清单（FEA）组织为**可执行的功能流程**：主流程（业务步骤序列）、分支流程（决策点分叉）、异常流程（失败/超时/取消/恢复与回退目标）。是后续 §业务规则（BR）、§状态变化（STATE）、§异常与失败处理（EX）的结构骨架。

## 输入

- `user-journey-and-stories` 的 confirmed artifact（含 ST-XXX 用户故事、范围基线）
- 父级 `function-description` §1 功能规格概览（FEA-XXX 与 P0/P1/P2 优先级）

## 产物

`§功能流程` 区块：

- **Mermaid flowchart**（必出）：起点 → 主流程步骤 → 分支流程 → 异常流程 → 出口；异常路径用虚线或标注
- **分支流程**（补充说明）：每个决策点的判定条件，互斥、可穷举
- **异常流程**（补充说明）：异常/失败/超时/取消/恢复路径与回退目标

## 触发判断

- 看到 "功能流程" / "业务流程图" / "主流程 分支 异常" / "流程步骤" / "流程图" → 触发
- 看到 "页面设计" / "组件" → **不触发**（走 `product-ux` 下的 `page-design`）
- 看到 "交互规则" / "输入约束" → **不触发**（走 `interaction-rules`）
- 看到 "业务规则" / "校验" / "状态机" / "异常处理明细" → **不触发**（走对应子技能）

## 关键约束

- 每个功能流程必须包含：起点、主流程步骤、≥1 分支流程、≥1 异常回退、出口/终止状态
- 每条分支必须有条件标签（互斥、穷举）；每个 P0 FEA ≥1 张图，且每张图覆盖主/支/异常路径
- 每个步骤可回溯 `ST-XXX` / `FEA-XXX`；AI 补的步骤标 `AI_INFERENCE`
- 不画视觉细节、不写交互规则、不写业务规则/状态机/异常处理明细

## 执行循环

Preflight → Intake → Think → Clarify → Generate → Audit → Human Gate → Commit / Reflow（详见 `SKILL.md`）。**永远不产 `confirmed`**；只有 `pipeline.py review --decision approve` 能写入。

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/anti-patterns.md` · AI 常见反模式
- `references/audit-checklist.md` · 审计清单
- `references/output-contract.md` · §功能流程 输出契约
- `references/question-patterns.md` · Clarify 提问模板
- `references/reviewer-checklist.md` · 人工评审清单
- `references/source-handling.md` · 上游追溯规则
- `references/thinking-framework.md` · 思考框架（必读）
- `scripts/validate_artifact.py` · 产物校验
- `templates/functional-flow-output.md` · 输出模板
