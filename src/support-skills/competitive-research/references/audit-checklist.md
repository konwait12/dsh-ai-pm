# 审计清单 · 竞品调研

## 结构闸门（Structural Gate）

- 在版本变更摘要之前，所有必需标题都存在（`竞品列表`、`逐品分析`、`横向对比`、`结论`）。
- 元数据包含产物 ID、版本、状态、owner、reviewer 以及日期或 `待确认` / `TBD`。
- 重大结论引用来源 ID（SRC-*）。
- 每个竞品都有选择理由（直接 / 间接 / 参照）。
- 调研目标（业务级 / 功能级）已记录。
- 阻断性问题被显式标记。

## 来源覆盖闸门（Source Coverage Gate）

- 每个被研究的竞品都登记了 SRC-ID 和检索日期。
- 重大来源陈述有产物位置或排除理由。
- 官方陈述与 AI 解读（来自截图/评论）可区分。
- 过时来源被标记；厂商声明与用户评论之间的冲突保持可见，直到被授权人解决。

## 语义闸门（Semantic Gate）

- 调研目标已陈述，每个对比维度都能追溯到它（没有泛泛的功能清单）。
- "So What"章节回答：我们应该做什么、差异化做什么、忽略什么、还不知道什么。
- 每条"我们应该做 Y"的建议都映射到已确认的目标 ID，并带 `AI_INFERENCE`。
- 至少识别出一个市场标准信号（竞品一致）和一个分歧点（差异化机会）。
- 已检查确认偏误：主动寻找了反证，而不只是支持性证据。

## 质量透镜（Quality Lenses）

- 第一性原理：每条建议在移除对标竞品后仍然成立。
- 系统思维：受影响的细分、旅程和下游决策都考虑到了。
- 对抗性审查：至少测试了一个"竞品 X 不是正确对标"的反例。
- 反向验证：我们差异化的前提条件已检查。
- 最小充分性：产物包含下一步所需内容，排除完整产品设计。

## 人工关卡（Human Gate）

当未解决项可能改变竞品选择、对比维度或重大建议时，设置 `needs_user_input`。

仅当剩余未知项为非阻断、有 owner、且包含延期风险时，设置 `conditional_review`。

仅当所有其他闸门通过时，设置 `ready_for_human_review`。绝不设置 `confirmed`；只有被授权人才能设置。

## 审计报告形态（Audit Report Shape）

```text
status_recommendation
passed_checks
failed_checks
repairs_applied
blocking_questions
nonblocking_unknowns
decisions_required
traceability_gaps
downstream_risks
```
