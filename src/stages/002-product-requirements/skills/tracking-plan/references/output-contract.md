# 输出契约 · 埋点与追踪计划（Output Contract · Tracking Plan）

## 产物状态（Artifact States）

| 状态 | 含义 | 下游使用 |
|---|---|---|
| `draft` | 初始收集 | 否 |
| `ready_for_sub_skill_review` | 覆盖矩阵已通；待 function-description 编排审 | 否 |
| `confirmed` | 由授权人接受（随 function-description 一起） | 是 |

## 版本规则（Version Rules）

- 起 `v0.1`；随 function-description 版本同步。
- 子 Skill 阶段不写 `confirmed`，由 function-description 父 Skill 一起签发。

## 必需章节（Required Sections）

| § | 标题 | 必填 |
|---|---|---|
| 1 | 元数据 | Yes |
| 2 | 事件清单（EV-XXX） | Yes |
| 3 | 事件属性字典 | Yes |
| 4 | 覆盖矩阵（每 FUN-XXX ≥1 must_track） | Yes |
| 5 | 指标映射（event → G-X → metric） | Yes |
| 6 | PII 与数据保留 | Yes |
| 7 | 待确认问题 | Yes |
| 8 | Constitution Compliance | Yes |

## 事件 Schema（Event Schema）

| 字段 | 必填 | 说明 |
|---|---|---|
| `EV-NNN` | Yes | 单调递增 |
| `event_name` | Yes | snake_case，verb_noun 模式 |
| `event_type` | Yes | `page_view` / `click` / `submit` / `exposure` / `success` / `error` / `custom` |
| `fun` | Yes | FUN-XXX |
| `ix` | Optional | IX-XXX |
| `br` | Optional | BR-XXX |
| `trigger_condition` | Yes | 何时触发 |
| `properties` | Yes | 属性列表（key / type / example / pii_flag / required） |
| `upload_timing` | Yes | `realtime` / `near_realtime` / `batch` / `on_session_end` |
| `platform` | Yes | `web` / `ios` / `android` / `miniprogram` / `server` |
| `metric` | Yes | `north_star` / `funnel_step` / `counter` / `latency` / `conversion` / `retention` |
| `goal` | Yes | G-X 引用 |
| `priority` | Yes | `must_track` / `nice_to_track` |
| `notes` | Optional | 采样 / 去重 / 保留期 |

## PII Flag 体系

| Flag | 含义 | 要求 |
|---|---|---|
| `false` | 非 PII | 标准上报 |
| `quasi` | 准标识（IP / 设备 ID / 位置） | 哈希化 + 用户授权后上报 |
| `true` | 直接标识（姓名 / 证件号 / 手机） | 加密 + 明确业务必要性 |
| `sensitive` | 敏感内容（健康 / 财务 / 宗教） | 访问控制 + 最小化 + 明确同意 |

## 覆盖硬约束（Coverage Hard Constraints）

- 每个 P0 FUN-XXX 至少 1 个 `must_track` 事件
- 每个事件都有 FUN-XXX 和 G-X 引用
- 同名事件必须合并（不允许 `click_btn` 和 `button_click` 并存）
- PII 事件必须填 `notes` 写保留期

## 下游交接（Downstream Handoff）

```text
must_track_count
nice_to_track_count
pii_event_count
event_to_goal_coverage
unmapped_events
```
