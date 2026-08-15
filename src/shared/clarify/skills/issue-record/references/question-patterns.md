# Question Patterns · Issue Record

Eight canonical question templates for the one-question-at-a-time Clarify loop. Each entry gives:

- **When to use** — the trigger condition
- **Question shape** — the prompt structure
- **Three examples** — paraphrased real cases (desensitized)
- **Common traps** — typical AI mistakes when asking this kind of question

Use these as reference when generating a new question in a Clarify Session, especially for the **AI 主动询问契约**（先问"要不要登记为 ISS-NNN"再继续生成）。See `SKILL.md` § Clarify for runtime rules (≤5 sessions, ordered by impact, every question carries an AI preliminary judgment).

---

## 1. 类别分诊（Category Triage）

**When to use**: when a signal's BLK / RSK / DEC / INF / CLS / OUT category is unclear.

**Question shape**:

```
[为什么重要] 类别决定谁处理、何时处理。
「[具体信号]」我初判为 [建议类别]。请确认: 它是 [BLK 阻断 / RSK 风险 / DEC 待决 / INF 缺信息 / CLS 歧义 / OUT 范围外]?
```

**Examples**:

- "‘上线范围待定’是 DEC（等业务方拍板）还是 RSK（可能变风险）?"
- "‘缺客户分级数据’是 INF（缺数据源）还是 CLS（分级定义不清）?"
- "这个合规问题已经确定存在,是 BLK 还是 RSK?有缓解路径吗?"

**Common traps**:

- 默认 BLK 制造紧迫感
- 用 INF 掩盖 DEC(等决策却写成缺信息)
- 不解释类别对下游的影响

---

## 2. 阻断判定（Blocking Determination）

**When to use**: when it is unclear whether an issue truly blocks progress.

**Question shape**:

```
[为什么重要] BLK 会冻结流程;误标 BLK 会造成无谓停滞。
「[具体问题]」真的阻断吗?有没有变通路径(换方案/分阶段/人工补)可以把 BLK 降为 RSK?
```

**Examples**:

- "缺少支付能力,能否先用人工收款变通,把 BLK 降为 RSK?"
- "法务未签字,是所有功能都停,还是仅跨境模块停?"
- "如果这个 BLK 一周内不解决,最坏影响是什么?有 fallback 吗?"

**Common traps**:

- 有变通路径仍标 BLK
- 不评估"不解决会怎样"
- 让 AI 替业务方决定阻断等级

---

## 3. 责任归属（Owner Assignment）

**When to use**: when an issue has no owner, or the current owner lacks authority.

**Question shape**:

```
[为什么重要] 无 owner 的问题无人推进,会烂在清单里。
「[具体问题]」的 owner 是谁?他有权做 [这个决定/提供这份数据/解除这个阻断] 吗?
```

**Examples**:

- "VIP 阈值的裁决人是 VP CRM 还是产品总监?"
- "数据缺口谁补?数据团队能单独补,还是需要业务方先给口径?"
- "该 owner 目前无权限,是否需要升级到更高权威?"

**Common traps**:

- owner 写"待定"就结束
- 给无权限的人分配问题
- 不记录 owner 的授权边界

---

## 4. 目标关闭日期（Target Close）

**When to use**: when a BLK / DEC lacks a `target_close`.

**Question shape**:

```
[为什么重要] 无期限的 BLK/DEC 会无限拖延,无法倒排。
「[具体问题]」的目标关闭日期是?倒排的依据是 [PRD 确认日 / 上线日 / 外部依赖时点]?
```

**Examples**:

- "该 DEC 要在 PRD 确认前关闭吗?倒排到几月几号?"
- "法务 review 的周期是 2 周,目标关闭日期定在 9/15 可行吗?"
- "这个 BLK 依赖第三方 SDK 版本,目标关闭能否随依赖交付?"

**Common traps**:

- 用"尽快"当期限
- 期限与外部依赖不同步
- 逾期问题不重排、不升级

---

## 5. 风险缓解（Risk Mitigation）

**When to use**: when a RSK lacks a mitigation, or the mitigation is vague.

**Question shape**:

```
[为什么重要] 无缓解措施的 RSK 只是被推迟的 BLK。
「[具体风险]」的缓解措施是?触发升级的阈值/条件是什么?由谁监控?
```

**Examples**:

- "跨境数据风险的缓解是‘法务 review + 分阶段放开’,触发全量放开的条件是什么?"
- "该 RSK 的监控 owner 是谁?多久复盘一次?"
- "如果缓解措施失效,是否自动升级为 BLK?"

**Common traps**:

- 缓解措施写成"注意一下"
- 不设触发升级的阈值
- 无监控 owner

---

## 6. 升级路由（Escalation）

**When to use**: when an issue is stuck, ownerless, or beyond current authority.

**Question shape**:

```
[为什么重要] 升级是把问题交给有权限的人,不是甩锅。
「[具体问题]」升级到谁?新 owner 有权限吗?升级原因是什么(超期/无权限/僵持)?
```

**Examples**:

- "该争议已僵持两周,升级到项目 PMO 还是业务负责人?"
- "DEC 超期未决,是否升级到更高决策层?"
- "新 owner 接手后,原 owner 的职责如何交接?"

**Common traps**:

- 升级不指定新 owner
- 把升级当"解决"了(升级后问题仍 open)
- 不记录升级原因与时间

---

## 7. 风险接受（Risk Acceptance）

**When to use**: when an issue is a candidate for `accepted` state.

**Question shape**:

```
[为什么重要] accepted = 决策者接受风险不再行动,只有决策者能设。
「[具体风险]」接受为不再行动,可以吗?接受条件与日期?由 [决策 Owner] 确认?
```

**Examples**:

- "该风险接受后,如果发生,影响面是什么?谁能接受这个影响?"
- "确认接受为 accepted,不再投入缓解资源?"
- "接受后是否需要在 PRD §9 风险摘要中体现?"

**Common traps**:

- AI 替决策者设 accepted
- 接受不记录条件与日期
- 把"不处理"当"接受"写死

---

## 8. 关闭验证（Close Verification）

**When to use**: when an issue claims `resolved` but lacks linked evidence.

**Question shape**:

```
[为什么重要] resolved 必须链接到关闭它的产物变更,否则无法复核。
「[具体问题]」的解决方案是?关闭它改动了哪个产物、哪一节?验证人是谁?
```

**Examples**:

- "该 CLS 通过背景 §8 边界修订解决了吗?修订后是否重新审过?"
- "resolved 的验证人是原 owner 还是独立复核人?"
- "关闭后,下游哪些产物需要重跑 Audit?"

**Common traps**:

- 嘴上说解决就关
- resolved 不链接产物变更
- 验证人与实现人是同一人且未注明

---

## Cross-cutting tips

1. **先问后登记（强制）**: 任何"待确认/冲突/风险"信号,先问"要不要登记为 ISS-NNN",确认后再登记。
2. **排序原则**: Clarify 一次只问 1 个,按 Impact × Uncertainty 排序,先问阻断性高的。
3. **每问必带 AI 初步判断**: 给出建议类别/owner/期限,让决策者确认而非从零想。
4. **三选项常驻**: 给 2-4 个互斥选项 + 「其他」兜底。
5. **回写位置必填**: 每答一题必须能精确指向 issue-record.md 的哪个 ISS-NNN。
