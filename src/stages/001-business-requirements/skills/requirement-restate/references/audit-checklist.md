# 审计清单 · Requirement Restate

## 结构闸门（Structural Gate）

- 所有必需标题存在（§1-§9 + `## Constitution Compliance` + `## 版本变更摘要`）。
- 元数据包含产物 ID、版本、状态、负责人、stakeholder、评审人，以及日期或 `待确认` / `TBD`。
- 每条重述需求都有稳定 ID（`RR-NNN`）、重述措辞、原始措辞、来源、知识状态、stakeholder 与 confidence。
- 实质性主张引用了来源 ID。阻断性问题被显式标记。

## 来源覆盖闸门（Source Coverage Gate）

- 所有承载需求的来源都已登记为 SRC-*。
- Intake 中提到的每个 SRC-ID 都反映在重述中。
- 每条 RR-NNN 行都追溯到来源位置（段落 / 时间戳）。
- 原始措辞 verbatim 保留——无静默清洗。

## 语义闸门（Semantic Gate）

- **原子性（Atomicity）**：没有一行塞进两个诉求；每行都是单一可测试主张。
- **无方案泄露（No Solution Leak）**：没有一行包含提议的方案、技术或设计。来源提到的方案是带 `solution_leak=true` 的 hint，不是决策。
- **stakeholder 之声（Stakeholder Voice）**：重述读起来是 stakeholder 的话，不是 AI 的话。
- **冲突可见性（Conflict Visibility）**：所有冲突都被标记，没有一个被解决。
- **未知已路由（Unknowns Routed）**：每个 UNKNOWN 都链接到一个问题或 issue-record 条目。

## 质量透镜（Quality Lenses）

- 第一性原理：去掉任何提议方案后，诉求依然成立。
- 对抗性审视：至少把一种合理的误读对照重述测试过。
- 逆向验证：stakeholder 只读重述时看到的正是他们想表达的意思。
- 确认偏误防御：没有措辞被 AI"改进"或"对齐"。

## 人工闸门（Human Gate）

当冲突或未知会改变诉求本身，或重述无法原样发回时，设置为 `needs_user_input`。

仅当剩余未知项非阻断、有负责人且包含延期风险时，才设置为 `conditional_review`。

仅当所有其他闸门通过时，才设置为 `ready_for_human_review`。绝不设置 `confirmed`；只有原 stakeholder（或其指定代理）可以设置。

## 审计报告形态（Audit Report Shape）

```text
status_recommendation
passed_checks
failed_checks
repairs_applied
blocking_questions
conflict_count
unknown_count
solution_leak_count
traceability_gaps
downstream_risks
```
