# 审计清单 · 问题清单（Issue Record · 跨阶段共享）

## 结构闸门（Structural Gate）

- 所有必需标题都存在（§1-§12 + `## Constitution Compliance` + `## 版本变更摘要`）。
- 元数据包含产物 ID、版本、状态、owner、reviewer 以及日期或 `待确认` / `TBD`。
- 每个问题都有稳定 ID（`ISS-NNN`）、类别、状态、标题、描述、owner、知识状态、来源和 raised_at。
- 重大结论引用来源 ID。阻断性问题被显式标记。

## 覆盖闸门（Coverage Gate）

- 每个上游产物的"待确认" / UNKNOWN / CONFLICT 标记都映射到 ISS-NNN，或有文档化的关闭理由（`closed_at_intake`）。
- 没有阶段遗留的未知被静默漏记。
- 问题是项目级的：没有任何问题被孤立在单个阶段产物中而没有登记条目。

## 责任闸门（Ownership Gate）

- 每个 `open` 问题都有 owner（个人或角色，不是"TBD"）。
- 每个 BLK / DEC 都有 `target_close`。
- 每个 RSK 都有 `mitigation`。
- 每个 `resolved` 问题都链接到关闭它的产物变更。
- 每个 `escalated` 问题都有 `escalated_to`（新 owner 或机构）。
- 超过 30 天的问题有升级记录或仍 open 的文档化理由。

## 状态完整性闸门（State Integrity Gate）

- `accepted` 状态只由决策 owner 设置，绝不由 AI 设置。
- `resolved` 由与实现者不同的验证人核实（或注明该事实）。
- 没有问题在无证据的情况下关闭（没有"只为清空清单"式关闭）。
- 类别稳定：BLK 是真阻断，INF 是缺失来源/数据，CLS 是措辞歧义，DEC 有具名决策者，OUT 有路由目标。

## AI 询问合规闸门（AI Inquiry Compliance Gate）

- 每次登记都以 AI 询问"要不要登记为 ISS-NNN"为前提——没有"静默越过待确认标记"。
- AI 没有替用户接受风险。
- 未经用户确认进入的新问题被标记为违规。

## 质量透镜（Quality Lenses）

- 第一性原理：剥离建议方案后问题仍然存在。
- 系统思维：每个 open 问题影响的下游 Work Item 都考虑到了。
- 对抗性审查：至少测试了一个对问题严重性的合理降级/升级。
- 反向验证：从 PRD 确认倒推，"问题清零"清单是完整的，或被显式接受为风险。
- Pre-mortem：前 3-5 个失败原因每个都有 owner 和缓解措施或已接受的风险。

## 人工关卡（Human Gate）

当类别、owner 或阻断状态未解决，或等待中的决策没有目标关闭时，设置 `needs_user_input`。

仅当剩余未知项为非阻断、有 owner、且包含延期风险时，设置 `conditional_review`。

仅当所有其他闸门通过时，设置 `ready_for_human_review`。绝不设置 `confirmed`；只有目标决策 owner / 业务发起人才能批准 closed-out 清单。

## 审计报告形态（Audit Report Shape）

```text
status_recommendation
passed_checks
failed_checks
repairs_applied
open_count
in_progress_count
blocked_count
accepted_count
resolved_count
escalated_count
open_blk_ids
open_dec_ids
critical_top5
blocking_questions
downstream_risks
```
