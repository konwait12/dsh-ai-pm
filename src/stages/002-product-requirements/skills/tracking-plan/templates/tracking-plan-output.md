<!-- tracking-plan output · auto-generated from sub-skill -->
---
parent_artifact: FD-{REQ}
sub_skill: tracking-plan
version: v0.1
status: draft
upstream_artifact_id: FD-{REQ}
---

## 埋点需求分析

> 本节由 `tracking-plan` 子 Skill 生成，属于 function-description §3.x 埋点层。
> 上游：function-description (FUN-XXX) + product-ux (IX-XXX) + business-rules (BR-XXX)

### 1. 元数据

- 关联需求：REQ-XXX
- 关联 function-description：FD-{REQ}
- 关联上游：FUN-XXX / IX-XXX / BR-XXX
- 评审版本：v0.1

### 2. 事件清单（EV-XXX）

| EV ID | event_name | event_type | FUN | IX | BR | trigger_condition | upload_timing | platform | metric | goal | priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EV-001 | {verb_noun} | click | FUN-XXX | IX-XXX | — | 用户点击 X 按钮时触发 | realtime | web | funnel_step | G-X | must_track |

### 3. 事件属性字典

| event_name | 属性 key | 类型 | example | pii_flag | required | 说明 |
|---|---|---|---|---|---|---|
| {verb_noun} | {prop_key} | string / int / bool / object | {example} | false / quasi / true / sensitive | yes / no | {说明} |

### 4. 覆盖矩阵（每 FUN-XXX ≥ 1 must_track）

| FUN | must_track 事件数 | nice_to_track 事件数 | 状态 |
|---|---|---|---|
| FUN-001 | 0 | 0 | ⚠️ 待补 |
| FUN-002 | 2 | 1 | ✅ |

### 5. 指标映射（event → G-X → metric）

| event_name | 关联目标 | 指标类型 | 指标说明 |
|---|---|---|---|
| {verb_noun} | G-X | north_star / funnel_step / counter / latency / conversion / retention | {业务侧如何用这个事件} |

### 6. PII 与数据保留

| event_name | 涉及属性 | pii_flag | 保留期 | 加密 / 哈希 / 访问控制 |
|---|---|---|---|---|
| | | false / quasi / true / sensitive | | |

### 7. 待确认问题

| ID | 问题 | 结论 |
|---|---|---|
| Q-001 | | |

### 8. Constitution Compliance

- 规则先行：✅ 已对齐（依赖 confirmed FUN/IX/BR）
- 六态标注：✅ 已对齐
- 模板符合性：✅ 已对齐
- 反模式自检：✅ 已通过（无孤立事件 / PII 已标记）
- 命名一致：✅ snake_case verb_noun
