# 人类审查清单 · 埋点与追踪计划（Tracking Plan）

> 本清单给 **数据团队 / 工程团队 / 业务方（metric_owner）** 在审查 AI 产出的 `tracking-plan.md` 时使用。
> 不是给 AI 看的（AI 看 `audit-checklist.md`）。
> 每条 = "是 / 否 / 不适用"，有"否"则进入 Revision 修改确认。

## 可落地性（数据/工程视角）
- [ ] 每个事件的 `trigger_condition` 是否精确到"哪个动作的哪个时点"？两个工程师照表埋点会不会埋出不同结果？
- [ ] `event_name` 是否 snake_case verb_noun 且全局唯一？是否与团队已有事件命名冲突？
- [ ] `upload_timing` / `platform` 是否与你们的采集链路一致？有没有无法落地的组合？
- [ ] 属性字典里每个属性的 key / type / example 是否清楚？`required` 是否明确？

## 覆盖完整性（业务视角）
- [ ] 每个 P0 功能是否都有 ≥1 个 `must_track` 事件？有没有 P0 功能没有任何信号？
- [ ] 每个事件是否都支撑了某个 G-X 目标？有没有"不知道验证什么"的孤立事件？
- [ ] 从 G-X 反推：要验证"订单转化率/核销率"，事件和属性够吗？缺不缺关键一环？

## PII 与合规
- [ ] 涉及手机号/证件号/设备 ID/位置/健康/财务等属性，`pii_flag` 是否正确（quasi/true/sensitive）？
- [ ] PII 事件是否都有保留期？是否明确加密/哈希/访问控制要求？
- [ ] 这份事件合约能否通过你们的安全/隐私 review？

## 命名与去重
- [ ] 有没有"同一动作、两个事件名"的重复？（`click_btn` 与 `button_click` 并存）
- [ ] `event_type` 是否都属允许集合（page_view/click/submit/exposure/success/error/custom）？

## 最终判断
1. **数据/工程团队能直接照这张表开始埋点吗？** 可以，哪些字段最清楚？不行，卡在哪？
2. **业务方确认这些事件能支撑目标的验证吗？** 认同，有没有必须补的 must_track？不认同，缺什么？
