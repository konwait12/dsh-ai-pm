# 审计清单（Audit Checklist）

## 结构闸门（Structural Gate）

- 所有必需标题都存在，包括位于 `## 版本变更摘要`（`## Version Change Summary`）之前的 `## Constitution Compliance`。
- 元数据包含产物 ID、版本、状态、负责人、评审人，以及日期或 `待确认` / `TBD`。
- 实质性主张引用了来源 ID。
- 所有知识状态寄存器使用稳定的 ID。
- 阻断性问题被显式标记。
- `Constitution Compliance` 章节：每一行的 `status` 字段非空，且没有行是 `FAIL`。如需偏离，状态必须是带理由的 `JUSTIFIED`。

## 来源覆盖闸门（Source Coverage Gate）

- 所有承载需求的来源均已登记。
- 实质性来源陈述有产物位置或排除原因。
- 直接陈述与 AI 解读可区分。
- 冲突在获得授权的人类解决之前保持可见。

## 语义闸门（Semantic Gate）

- 背景解释了需求为什么存在、为什么是现在。
- 现状描述的是实际工作或变通做法，而不只是抱怨。
- 核心问题与提议方案彼此分离。
- 目标描述的是预期的改变，而不只是功能交付。
- 成功判断有证据、临时度量或显式的问题。
- 角色与干系人的粒度足以支撑下一步工作流，而不至于演变成完整旅程。
- 时间、约束、依赖与非目标已处理或标记为未知。

## 质量透镜（Quality Lenses）

- 第一性原理：去掉提议方案后，根问题依然存在。
- 系统思维：受影响的角色、流程、系统与依赖都被考虑过。
- 对抗性审视：至少测试过一个合理的反例或失效假设。
- 逆向验证：成功的前提条件被检查过。
- 最小充分性：产物包含下一步所需的内容，排除下游设计。

## 需求质量闸门（Requirement Quality Gate，ISO/IEC/IEEE 29148）

产物中的每条实质性主张或目标都应对照九项单条需求特性（ISO/IEC/IEEE 29148:2018 §5.2.5）进行核查：

| # | 特性 | 核查问题 | 通过标准 |
|---|---|---|---|
| 1 | 适当（Appropriate） | 与该项目相关吗？ | 是，能追溯到来源或决策 |
| 2 | 完整（Complete） | 是否包含所有必要条件？ | 没有指向缺失信息的悬空引用 |
| 3 | 合规（Conforming） | 是否符合模板与来源规则？ | 标题与 SRC-* 规则已满足 |
| 4 | 正确（Correct） | 与来源相比准确吗？ | 与 SRC-* 陈述一致 |
| 5 | 可行（Feasible） | 在约束内能交付吗？ | 无已知阻断 |
| 6 | 必要（Necessary） | 去掉它目标还成立吗？ | 是 |
| 7 | 单一（Singular） | 是一条陈述而非多条吗？ | 每行一个主张 |
| 8 | 无歧义（Unambiguous） | 两个读者会理解不一致吗？ | 不会，术语已定义 |
| 9 | 可验证（Verifiable） | 有可衡量的适配判据吗？ | 数值基线 + 目标，或带负责人的显式 `待确认` |

推荐的句式：`The [system] shall [verb] [object] [constraint] [condition]`（29148 §5.2.5）。在中文化产物惯例中，保留叙述，但确保每条实质性主张单一、可追溯、可验证。

实质性目标在"可验证"上出现 `FAIL` 是阻断项：要么量化（基线 + 目标 + 时间窗口），要么设为带明确负责人的 `needs_user_input`。

## 人工闸门（Human Gate）

当存在未决项可能改变问题、目标、成功判断、关键角色、时间、边界、成本或实质性风险时，设置为 `needs_user_input`。

仅当剩余未知项非阻断、有负责人且包含延期风险时，才设置为 `conditional_review`。

仅当所有其他闸门通过时，才设置为 `ready_for_human_review`。绝不设置 `confirmed`；只有被授权的人类才能设置。

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
