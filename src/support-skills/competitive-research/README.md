# 竞品调研 Skill

> **Support Skill** · 位于 `src/support-skills/competitive-research/`
> **执行时机**：业务方案方向不清、或具体功能设计缺乏参考时触发（支持分支，非主干必做）

## 用途

用结构化框架（功能对比矩阵 / 定位图 / SWOT）系统分析竞品，产出「对我们意味着什么」的可落地产物 `competitive-analysis.md`，为产品方向、功能优先级、差异化策略提供证据基础。所有结论在人工确认前一律标记 `AI_INFERENCE`。

## 输入

- 已 `confirmed` 的 `background-goal.md`（提供锚定的目标 G#）或范围基线
- 明确的调研目标：业务级（定产品方向）或功能级（定功能设计）
- 竞品来源：官网 / 应用商店 / 用户评测 / 公开文档 / 行业报告

> 缺少已确认背景或调研目标时，停在实际业务需求不清的 `needs_user_input`，不空对空调研。

## 输出

`competitive-analysis.md`，结构见 `src/templates/support/competitive-analysis.md`：

- `## 竞品列表` — 竞品选择与理由（直接/间接/参照）
- `## 逐品分析` — 基于所选框架的深度分析，带 SRC-*
- `## 横向对比` — 竞品共识（市场标准）与分歧（差异化机会）
- `## 结论` — 强制「So What」：该做 / 差异化做 / 忽略 / 还不知道

## 触发判断

- 看到 "竞品分析 / 竞品调研 / 市场调研 / competitive analysis" → 触发
- 看到 "我不确定这个功能怎么做，看看别人怎么做的"（且已有业务背景）→ 触发
- 没有已确认目标或只有一句话需求 → **先走低密度降级**（输出充分性评估 + 分批澄清问题）

## 关键约束

- 竞品 3-5 个，多了稀释洞察质量
- 每条结论映射到已确认目标 G#，不无目标自嗨
- 所有发现默认 `AI_INFERENCE`，**绝不**由 AI 设为 `confirmed`，人工确认适用性后生效
- 必须落到「So What」，只罗列发现不算完成
- 竞品信息带检索日期，material 事实用前重新核验

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/` · 思考透镜 / 产物契约 / 审计与评审清单 / 提问模板 / 来源处理 / 反模式
- `src/templates/support/competitive-analysis.md` · 竞品分析模板
- `scripts/validate_artifact.py` · 校验脚本
