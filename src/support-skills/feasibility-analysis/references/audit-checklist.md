# 审计清单 · 可行性分析

## 结构闸门（Structural Gate）

- 在版本变更摘要之前，可行性报告的所有必需标题都存在（主线：市场空间 / 技术可行性 / 投入产出 / 风险评估 / 结论；§多方案取舍 章节：候选方案 / 方案对比矩阵 / AI 推荐 / 人工决策，仅在 ≥2 实质方案时出现）。
- 元数据包含产物 ID、版本、状态、owner、decision-owner、reviewer 以及日期或 `待确认` / `TBD`。
- 重大成本/风险数字引用来源 ID（SRC-*），或显式标为 `AI_INFERENCE` / `ASSUMPTION` 并带 owner。
- 已识别决策 owner；存在 `DEC-XXX` 决策记录槽位。
- 阻断性问题被显式标记。

## 方法闸门（§多方案取舍 章节）

- 标准在打分**之前**定义（锚定检查）——有证据表明权重不是从偏好结果逆向工程出来的。
- 每个方案以同等深度描述；没有选项被灌水或饿死。
- 加权得分算术正确（每条标准 权重 × 得分 → 总分）。
- 敏感度分析说明：哪个标准，若其权重 ±1，会翻转推荐。

## 方法闸门（主线四维度）

- 全部 4 个维度（市场 / 技术 / 投入产出 / 风险）都有证据分析。
- 每个技术挑战归结为 已验证 / 待验证 / 不可行。
- 推荐是 做 / 不做 / 有条件做，条件（若有）具体且可衡量。

## 语义闸门（Semantic Gate）

- 评估回答一个真实的决策，而非一段描述（"我们可以做 X 或 Y"不是结论）。
- AI 推荐带置信度（HIGH/MEDIUM/LOW）并列出可能翻转它的假设。
- 无静默范围变更：如果首选方案改变范围，点名受影响的 Work Item。
- 实现细节级的选择被路由给工程，而不是灌进产品对比。

## 质量透镜（Quality Lenses）

- 第一性原理：根决策在移除"显而易见"的方案后仍然成立。
- 系统思维：受影响的角色、流程、系统和运营依赖都考虑到了。
- 对抗性审查：至少测试了一个"推荐选项是陷阱"的反例。
- 反向验证：推荐方案成功的前提条件已检查。
- 最小充分性：产物包含决策所需内容，排除架构设计。

## 人工关卡（Human Gate）

当未解决项可能改变推荐、标准权重或重大成本/风险数字时，设置 `needs_user_input`。

仅当剩余未知项为非阻断、有 owner、且包含延期风险时，设置 `conditional_review`。

仅当所有其他闸门通过时，设置 `ready_for_human_review`。绝不设置 `confirmed`；只有被授权的决策 owner 才能设置。

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
