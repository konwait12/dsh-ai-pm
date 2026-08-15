# 可行性分析 Skill

> **Support Skill** · 位于 `src/support-skills/feasibility-analysis/`
> **执行时机**：进入主干前评估可行性（市场/技术/投入产出/风险），或多方案取舍会影响范围、成本、合规或风险时触发（支持分支，非主干必做）

## 用途

以**四维度可行性分析**为主线（市场空间 / 技术可行性 / 投入产出 / 风险评估），客观呈现评估证据并给出带置信度的 AI 推荐；当存在 ≥2 个实质不同方案时，多方案取舍作为其中的 **§多方案取舍** 章节处理（加权决策矩阵）。**AI 永远不做最终决策**——决策人做出选择并记录为 `DecisionRecord`（DEC-XXX）。

## 主线与章节

| 结构 | 产出 | 触发 |
|---|---|---|
| **主线四维度** | `feasibility-report.md`（做 / 不做 / 有条件做） | 技术/合规/资源约束对可行性存疑 |
| **§多方案取舍 章节** | 嵌入 `feasibility-report.md`（用 `solution-comparison.md` 模板作章节结构，不独立产出） | ≥2 个实质不同方案需要取舍 |

## 输入

- 已 `confirmed` 的具体产品级方案（`product-ux` / `function-description`）或明确的可行性评估请求
- 上游证据：background-goal、成本 / 约束 / 合规输入
- 明确命名的决策人（decision-owner）

> 缺少具体方案对象或决策人时，停在 `needs_user_input`，不空对空评估。

## 输出

- 单一产物 `feasibility-report.md` — 见 `src/templates/support/feasibility-report.md`（市场空间 / 技术可行性 / 投入产出 / 风险评估 / §多方案取舍（若适用）/ 结论）
- §多方案取舍 章节结构 — 见 `src/templates/support/solution-comparison.md`（候选方案 / 方案对比矩阵 / AI 推荐 / 人工决策）

## 触发判断

- 看到 "方案评估 / 方案对比 / 可行性分析 / build vs buy / 自研还是外采" → 触发
- 方案只在实现细节上不同 → **不触发**（属工程选型）
- 只有模糊想法、无具体方案、无决策人 → **先走低密度降级**（充分性评估 + 分批澄清）

## 关键约束

- 权重必须在打分**前**定义（防锚定），并做敏感度分析
- 每个方案等深描述（防假对等）
- AI 推荐必须带置信度（高/中/低）与"什么假设会翻转结论"
- AI **绝不**设置 `confirmed`；决策人拍板并记录 `DEC-XXX`
- 若决策改变范围 → 回流最早受影响的 Work Item，绝不静默改范围
- 成本/风险估算标 `AI_INFERENCE`，未经确认不得写死

## 配套资源

- `agents/openai.yaml` · OpenAI / Anthropic Agent 路由元数据
- `references/` · 思考透镜 / 主线与 §多方案取舍 指南 / 产物契约 / 审计与评审清单 / 提问模板 / 来源处理 / 反模式
- `src/templates/support/feasibility-report.md` · 可行性主线模板
- `src/templates/support/solution-comparison.md` · §多方案取舍 章节模板
- `scripts/validate_artifact.py` · 校验脚本
