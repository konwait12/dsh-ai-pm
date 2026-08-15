# 提问模式 · 埋点与追踪计划（Question Patterns · Tracking Plan）

一次性一问 Clarify 循环的 8 个规范提问模板。每条包含：

- **何时使用** — 触发条件
- **问题句式** — 提示结构
- **三个示例** — 转述过的真实案例（已脱敏）
- **常见陷阱** — AI 问这类问题时最典型的错误

在 Clarify Session 中生成新问题时以此为参考。运行时规则见 `SKILL.md` § Clarify（≤5 sessions、按影响排序、每个问题都带 AI 初步判断）。

---

## 1. 事件必要性（Event Necessity）

**何时使用**： when an event's purpose is unclear or it is a candidate for "track everything" noise.

**问题句式**：

```
[为什么重要] 没有指标/目标支撑的事件会白白增加采集与清洗成本。
候选事件 [event_name] 想验证什么?它支撑 [哪个 G-X]?是 must_track 还是 nice_to_track?
```

**示例**：

- "`coupon_banner_view` 想验证曝光到点击的转化,还是只是好奇?若无指标可降为 nice_to_track。"
- "`help_icon_hover` 没有对应 G-X。是否删除,还是你想建立'帮助自助率'指标?"
- "每个页面都上报 view 是必要的,但页面内部的小曝光是否需要逐个上报?"

**常见陷阱**：

- 默认全部 must_track
- 替业务方编造指标
- 不解释事件与目标的关系

---

## 2. 触发时机（Trigger Condition）

**何时使用**： when `trigger_condition` is ambiguous or two engineers would fire the event differently.

**问题句式**：

```
[为什么重要] 触发时机不一致,同一事件会产生两套口径。
事件 [event_name] 的触发时点是 [建议时点]。请确认: 在 [校验通过后 / 点击后立即 / 接口成功返回后] 触发?
```

**示例**：

- "`order_submit_success` 是前端收到成功响应时触发,还是后端落库成功后触发?"
- "`coupon_apply_click` 在点击按钮时触发,还是校验通过后才触发?"
- "提交失败的事件,是否按失败类型拆成多个 error 事件,还是一个带 error_code 属性?"

**常见陷阱**：

- 用"点击时"这种模糊描述
- 不区分前端/后端触发
- 忽略失败/异常路径的触发

---

## 3. 属性口径（Property Semantics）

**何时使用**： when a property's meaning or domain is unclear and would pollute analytics.

**问题句式**：

```
[为什么重要] 属性口径不一致,指标无法跨事件/跨周期对齐。
属性 [prop_key] 的口径是 [建议口径]?请确认值域与含义,示例: [example]。
```

**示例**：

- "`channel` 属性是'用户来源渠道'(直客/代理),还是'当前访问渠道'(SEO/信息流)?两者不能混。"
- "`amount` 单位是元还是分?含税还是不含税?"
- "`sku_count` 是购物车行数还是不同商品数?"

**常见陷阱**：

- 属性值域不写清楚
- 同一属性在不同事件里口径不同
- 不提供示例值

---

## 4. PII 处理（PII Handling）

**何时使用**： when a property contains identifiers, fingerprints, or sensitive content.

**问题句式**：

```
[为什么重要] PII 处理决定合规与采集链路。
属性 [prop_key] 含 [个人信息]。请确认 pii_flag: [false / quasi / true / sensitive],保留期与处理方式(加密/哈希/访问控制)?
```

**示例**：

- "`user_phone` 是否真的需要上报?能否只用哈希后的 ID?"
- "`device_id` 属于 quasi,确认用哈希 + 用户授权后上报?"
- "`order_medical_category` 属于 sensitive,确认访问控制 + 最小化?"

**常见陷阱**：

- 默认 pii_flag=false
- 不写保留期
- 上报不必要的完整标识符

---

## 5. 上报时机（Upload Timing）

**何时使用**： when the metric needs timeliness that the upload timing cannot support.

**问题句式**：

```
[为什么重要] 上报时机决定指标延迟与实时性。
事件 [event_name] 用 [建议 timing] 上报。请确认: 指标需要实时还是可批量?`realtime / near_realtime / batch / on_session_end`?
```

**示例**：

- "转化漏斗需要近实时,但 `batch` 每天凌晨汇总。确认事件用 near_realtime?"
- "`on_session_end` 会丢断线用户。这个事件能否接受丢失?"
- "批量上报的量级,你们的管道能扛住吗?需要采样吗?"

**常见陷阱**：

- 一律 realtime(成本高)
- 忽视 on_session_end 的丢失风险
- 上报时机与指标延迟不匹配

---

## 6. 平台覆盖（Platform Coverage）

**何时使用**： when the same function exists on multiple platforms and event coverage differs.

**问题句式**：

```
[为什么重要] 平台不一致,漏斗会缺链。
事件 [event_name] 覆盖 [web / ios / android / miniprogram / server] 哪些平台?各平台触发时机是否一致?
```

**示例**：

- "小程序端没有支付回调,`order_pay_success` 怎么触发?能否用后端事件补齐?"
- "web 与 iOS 的 `page_view` 定义是否一致(首屏曝光 vs 可见时间)?"
- "server 端事件(`order_paid`)与客户端事件如何关联(user_id / order_id 关联键)?"

**常见陷阱**：

- 只列 web 忘了移动端
- 跨平台事件口径不一致
- 缺 server 端事件补齐客户端盲区

---

## 7. 指标映射（Metric Mapping）

**何时使用**： when the metric type for an event is unclear or mislabeled.

**问题句式**：

```
[为什么重要] 指标类型决定下游怎么用这个事件。
事件 [event_name] 的指标类型是 [north_star / funnel_step / counter / latency / conversion / retention]?请确认它支撑 [G-X]。
```

**示例**：

- "`order_submit_success` 是 conversion 还是 counter?它是转化漏斗的一步吗?"
- "`api_latency` 是 latency 指标,关联到哪个 G-X?有没有性能目标?"
- "`dau` 事件是 north_star,还是 funnel_step?确认它在指标树中的位置。"

**常见陷阱**：

- 指标类型随手填
- 事件与 G-X 错配
- 不说明指标在业务里的用途

---

## 8. 覆盖缺口（Coverage Gap）

**何时使用**： when a P0 function has no must_track event, or a G-X cannot be verified.

**问题句式**：

```
[为什么重要] P0 无信号 = 上线后无法证明功能是否生效。
FUN-XXX 目前没有 must_track 事件。要验证它,需要哪些事件与属性?请圈定,或确认该功能本期不需要埋点。
```

**示例**：

- "FUN-002 优惠券核销没有事件。核销成功/失败分别上报吗?失败原因用什么属性?"
- "G2 订单转化率需要'提交成功'与'支付成功'两个事件,目前只有前者。是否补后者?"
- "该功能是后台配置项,无用户行为。确认排除出覆盖矩阵?"

**常见陷阱**：

- 掩盖覆盖缺口
- 用"反正没人看"跳过 P0
- 不补关键漏斗链路

---

## 跨主题提示（Cross-cutting tips）

1. **排序原则**: Clarify 一次只问 1 个,按 Impact × Uncertainty 排序,先问阻断覆盖/合规的。
2. **不要问 AI 能查的事实**: 平台能力、SDK 埋点约定,让 AI 自查。
3. **每问必带 AI 初步判断**: 给出建议的事件名/触发时机/属性,让业务方确认而非从零想。
4. **回写位置必填**: 每答一题必须能精确指向 tracking-plan.md 的哪个事件/属性。
5. **上游优先**: 依赖上游 FUN/IX/BR 的问题,先确认上游,再谈事件。
