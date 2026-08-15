<!-- tracking-plan output · auto-generated from sub-skill -->
<!--
⚠️ Fixture 声明：本文件是回归演示样本，非真实需求产物。所有人物姓名、公司名、城市名、财务数字、业务指标均为通用占位符，仅用于演示产物结构。任何与现实业务的相似性纯属巧合。
-->
---
parent_artifact: FD-INVITE-001
sub_skill: tracking-plan
version: v0.1
status: ready_for_sub_skill_review
upstream_artifact_id: FD-INVITE-001
---

## 埋点需求分析

> 本节由 `tracking-plan` 子 Skill 生成，属于 function-description §3.x 埋点层。
> 上游：function-description (FUN-XXX) + product-ux (IX-XXX) + business-rules (BR-XXX)

### 1. 元数据

- 关联需求：REQ-001
- 关联 function-description：FD-INVITE-001
- 关联上游：FUN-001 / FUN-002 / FUN-003 / IX-101 / IX-102 / IX-201 / IX-301 / BR-101
- 评审版本：v0.1

### 2. 事件清单（EV-XXX）

| EV ID | event_name | event_type | FUN | IX | BR | trigger_condition | upload_timing | platform | metric | goal | priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EV-001 | invite_view | page_view | FUN-001 | IX-101 | — | 客户打开邀请函 H5 页面时触发 | realtime | web | funnel_step | G1 | must_track |
| EV-002 | rsvp_submit | submit | FUN-001 | IX-102 | — | 客户提交参加/不参加选择时触发 | realtime | web | conversion | G1 | must_track |
| EV-003 | checkin_scan | success | FUN-002 | IX-201 | BR-101 | 现场签到扫码成功时触发 | realtime | miniprogram | counter | G2 | must_track |
| EV-004 | report_view | page_view | FUN-003 | IX-301 | — | 业务方打开到场分析报告时触发 | realtime | web | counter | G3 | nice_to_track |

### 3. 事件属性字典

| event_name | 属性 key | 类型 | example | pii_flag | required | 说明 |
|---|---|---|---|---|---|---|
| invite_view | invite_id | string | INV-2026-0001 | false | yes | 邀请函编号 |
| rsvp_submit | attend_choice | string | yes / no | false | yes | 参加选择 |
| rsvp_submit | device_id | string | dv_xxxx | quasi | no | 准标识，哈希化后上报 |
| checkin_scan | guest_phone | string | 138xxxx | true | yes | 直接标识，加密存储 |
| report_view | attend_rate | float | 0.62 | false | no | 到场率数值 |

### 4. 覆盖矩阵（每 FUN-XXX ≥ 1 must_track）

| FUN | must_track 事件数 | nice_to_track 事件数 | 状态 |
|---|---|---|---|
| FUN-001 | 2 | 0 | ✅ |
| FUN-002 | 1 | 0 | ✅ |
| FUN-003 | 0 | 1 | ✅ |

### 5. 指标映射（event → G-X → metric）

| event_name | 关联目标 | 指标类型 | 指标说明 |
|---|---|---|---|
| invite_view | G1 | funnel_step | 邀约触达漏斗第一步 |
| rsvp_submit | G1 | conversion | RSVP 回收率 = 提交数 / 发送数 |
| checkin_scan | G2 | counter | 到场人数与到场率 |
| report_view | G3 | counter | 报告查看次数 |

### 6. PII 与数据保留

| event_name | 涉及属性 | pii_flag | 保留期 | 加密 / 哈希 / 访问控制 |
|---|---|---|---|---|
| invite_view | invite_id | false | 180 天 | 标准上报 |
| rsvp_submit | device_id | quasi | 90 天 | SHA-256 哈希 |
| checkin_scan | guest_phone | true | 活动结束后 30 天 | AES 加密 + 角色访问控制 |
| checkin_scan | diet_restriction | sensitive | 活动结束后 7 天 | 最小化采集 + 明确同意 |

### 7. 待确认问题

| ID | 问题 | 结论 |
|---|---|---|
| Q-001 | RSVP 截止时间 | 待业务方代表A 确认（issue-record ISS-201） |
| Q-002 | 签到二维码发放渠道 | 待业务方代表B 确认（issue-record ISS-301） |

### 8. Constitution Compliance

- 规则先行：✅ 已对齐（依赖 confirmed FUN/IX/BR）
- 六态标注：✅ 已对齐
- 模板符合性：✅ 已对齐
- 反模式自检：✅ 已通过（无孤立事件 / PII 已标记）
- 命名一致：✅ snake_case verb_noun
