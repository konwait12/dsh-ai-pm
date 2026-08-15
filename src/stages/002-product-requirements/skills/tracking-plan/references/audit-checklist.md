# 审计清单 · 埋点与追踪计划（Audit Checklist · Tracking Plan）

## 结构闸门（Structural Gate）

- 所有必需标题存在（§1-§8 + `## Constitution Compliance`）。
- 每个事件都有稳定 ID（`EV-NNN`）、`event_name`、`event_type`、FUN/IX/BR 引用、触发条件、属性、上报时机、平台、指标、目标与优先级。
- 每个事件都链接到某个 FUN-XXX 与某个 G-X——无孤儿事件。
- 实质性主张引用上游产物 ID。阻断性问题被显式标记。

## 覆盖闸门（Coverage Gate）

- 每个 P0 FUN-XXX 至少有一个 `must_track` 事件（覆盖矩阵硬约束）。
- 在 `ready_for_sub_skill_review` 时，覆盖矩阵状态列对 P0 功能不显示 `⚠️ 待补`。
- 每个上线后必须可度量的 G-X 都有验证它所需的事件 + 属性。

## 事件 Schema 闸门（Event Schema Gate）

- `event_name` 是 snake_case verb_noun 且全局唯一；没有不同名称下含义重复的事件。
- `event_type` 属于允许集合之一（`page_view` / `click` / `submit` / `exposure` / `success` / `error` / `custom`）。
- `upload_timing` 属于 `realtime` / `near_realtime` / `batch` / `on_session_end` 之一，且匹配指标的需求。
- `platform` 属于 `web` / `ios` / `android` / `miniprogram` / `server` 之一。

## PII 闸门（PII Gate）

- 每个属性都有 `pii_flag`：`false` / `quasi` / `true` / `sensitive`。
- PII/sensitive 事件在 `notes` 中带有显式的数据保留规则。
- 不在无标记的情况下静默采集标识符、指纹或敏感内容。

## 指标闸门（Metric Gate）

- 每个 `must_track` 事件都映射到某个目标（G-X）与某种指标类型。
- 指标可追溯到 background-goal 的目标；本计划不发明数值目标。

## 质量透镜（Quality Lenses）

- 第一性原理：每个事件都回答真实的业务问题；无"全量追踪"噪声。
- 对抗性审视：至少把一种对事件的合理解读误解测试过。
- 逆向验证：从每个 G-X 倒推，所需的事件/属性都存在。
- 最小充分性：事件清单包含数据/工程所需的内容，排除 SQL/表设计。

## 人工闸门（Human Gate）

当覆盖失败、某个触发/属性有歧义，或某个 PII 决策改变合约时，设置为 `needs_user_input`。

仅当剩余未知项非阻断、有负责人且包含延期风险时，才设置为 `conditional_review`。

仅当所有其他闸门通过时，才设置为 `ready_for_sub_skill_review`。绝不设置 `confirmed`；只有 metric/data owner 加 function-description 父 Skill 可以设置。

## 审计报告形态（Audit Report Shape）

```text
status_recommendation
passed_checks
failed_checks
repairs_applied
must_track_count
nice_to_track_count
pii_event_count
unmapped_events
blocking_questions
downstream_risks
```
