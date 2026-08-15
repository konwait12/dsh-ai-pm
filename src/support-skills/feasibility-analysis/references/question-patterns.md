# Question Patterns · Feasibility Analysis

Eight canonical question templates for the one-question-at-a-time Clarify loop. Each entry gives:

- **When to use** — the trigger condition
- **Question shape** — the prompt structure
- **Three examples** — paraphrased real cases (desensitized)
- **Common traps** — typical AI mistakes when asking this kind of question

Use these as reference when generating a new question in a Clarify Session. See `SKILL.md` § Thinking Prompts → Clarify for runtime rules.

---

## 1. 决策问题（Decision Scope）

**When to use**: when the decision itself is unclear — whether the request is a feasibility question (做不做) or a comparison question (选哪个), or whether it is a product decision at all.

**Question shape**:

```
[为什么重要] 评估对象不清，评估必然跑偏。
请明确: 这次要决策的是 [做/不做]（可行性）还是 [选 A 还是 B]（多方案对比）?
如果方案只差实现细节，是否应交给工程而非产品评估?
```

**Examples**:

- "这是'要不要做订单通知'（可行性），还是'自研还是外采'（多方案）？两者评估框架不同。"
- "方案 A 和 B 只是前端实现方式不同，这种属于工程选型，产品是否仍需介入？"
- "评估要支撑的决策是什么——是否立项，还是立项后选哪条路？"

**Common traps**:

- 分不清主线四维度与 §多方案取舍 章节
- 把工程实现细节当产品方案评估
- 评估目标与真实决策脱节

---

## 2. 候选方案（Candidate Set）

**When to use**: when the candidate solution list may be incomplete, or when the requester named only two options that are not mutually exclusive.

**Question shape**:

```
[为什么重要] 候选集不全，结论就是局部的。
当前候选: [A/B]。是否还有第三个选项，比如 [C]（混合/分阶段/外包+自研）?
这些方案是互斥的吗?是否可以同时进行?
```

**Examples**:

- "自研 vs 外采之外，是否考虑'先用成熟 SaaS 顶上、再逐步自研'的分阶段方案？"
- "方案 A 和 B 互斥吗？如果先 A 后 B 可行，成本矩阵要重新评估。"
- "有没有'什么都不做/维持现状'作为基线方案纳入对比？"

**Common traps**:

- 只对比用户提到的两个选项
- 漏掉"维持现状"这个默认方案
- 不验证方案是否互斥

---

## 3. 评估标准与权重（Criteria & Weights）

**When to use**: when criteria are undefined, or when the AI's proposed weights may bias the outcome.

**Question shape**:

```
[为什么重要] 权重决定结论，且必须在打分前确定。
我计划用 [候选标准] 评估，权重初判为 [W]。请确认:
哪些标准对这次决策最重要?哪些可以去掉?
```

**Examples**:

- "权重初判：业务匹配 5、用户影响 4、成本 4、时间 3、技术风险 3。成本对你更重要吗？需要提到 5？"
- "合规权重应该设多少？如果合规红线一票否决，是否用'否决项'而非权重？"
- "可逆性对这次决策重要吗？如果决策难撤回，权重应提高。"

**Common traps**:

- 打分后再调权重（锚定）
- 权重设定明显偏袒某个方案
- 用否决项冒充权重（合规应一票否决而非加权）

---

## 4. 成本与资源数据（Cost Data）

**When to use**: when material cost/headcount/timeline figures are missing or only guessed.

**Question shape**:

```
[为什么重要] 成本是方案取舍的核心，估算错误会直接误导决策。
当前 [方案] 的成本依据是 [来源/估算]。请确认或补充:
研发成本 [数值]?运维成本?回本预期?来源是报价单/历史项目/估算?
```

**Examples**:

- "自研成本我估 2 人×4 周 ≈ ¥X。这是历史项目经验还是拍脑袋？有真实人天数据吗？"
- "外采报价只有代理商口头 ¥X，能否拿到正式报价单作为 SRC？"
- "运维成本是否计入？（自研的隐性维护成本常被漏掉）"

**Common traps**:

- 把 AI 估算当 FACT 写死
- 漏掉运维/支持等隐性成本
- 回本周期无依据

---

## 5. 风险与合规（Risk & Compliance）

**When to use**: when a risk or compliance red line is unresolved, or when a risk's impact/probability is uncertain.

**Question shape**:

```
[为什么重要] 合规红线一票否决，风险判断决定方案取舍。
当前风险 [描述] 的影响/概率为 [判断]。请确认:
是否有法务/合规审批?是否存在数据安全红线 [列举]?
该风险由谁负责跟进、何时复核?
```

**Examples**:

- "外采方案涉及客户数据出域，是否需要法务和数据安全审批？周期多久？"
- "供应商锁定风险（外采方案）的影响我估为高概率。你的判断呢？"
- "这个合规风险是硬否决还是可接受？由谁拍板？"

**Common traps**:

- 风险只列不处置（无责任人、无复核点）
- 把合规当加权项而非否决项
- 对风险概率凭感觉填高/中/低

---

## 6. 时间与周期（Timing）

**When to use**: when the deadline is asserted without evidence, or when each solution's time-to-value differs materially.

**Question shape**:

```
[为什么重要] 时间窗口直接决定哪些方案可行。
上线 deadline 是 [具体日期/季度]?是否硬性?
各方案的 [里程碑] 需要精确到周吗?外部依赖确认了吗?
```

**Examples**:

- "deadline 是 Q3 还是具体到 9/30？如果是硬性，自研 4 周是否来不及？"
- "外采上线依赖供应商接口，SLA 确认了吗？对方排期如何？"
- "如果分两期（先用 SaaS 顶上），第一期上线时间能接受吗？"

**Common traps**:

- 用「尽快」代替具体时间
- 漏掉外部依赖（供应商/审批/采购周期）
- 把软 deadline 当硬约束或反之

---

## 7. 决策人（Decision Owner）

**When to use**: when no decision owner is identified, or when the person requesting the assessment is not the person authorized to decide.

**Question shape**:

```
[为什么重要] 评估必须交给有权决策的人，否则白做。
谁对这次 [做不做/选哪个] 有最终决定权?
拍板的是 [角色] 吗?评估结果需要提交给谁评审?
```

**Examples**:

- "自研 vs 外采最终由谁拍板——产品、技术负责人还是 CEO？我需要把评估提交给正确的人。"
- "预算上限的批准人是财务还是业务负责人？"
- "如果决策人本周不在，评估是否可以先出 `conditional_review` 等其确认？"

**Common traps**:

- 找错了决策人，评估无人认领
- 替决策人做判断（AI 或 PM 越权）
- 不确认决策人可否决什么

---

## 8. 回流范围（Reflow Scope）

**When to use**: when a preferred solution changes scope, cost, or confirmed constraints, and the impact boundary is unclear.

**Question shape**:

```
[为什么重要] 方案变更会级联影响已确认的上游。
若选择 [方案]，会影响哪些已确认 Work Item?（范围/成本/约束）
需要回流到 [最早受影响项] 重新确认吗?还是本次一并更新?
```

**Examples**:

- "如果选外采，会员体系的确认范围是否要改？是否影响已确认的 background-goal §8 边界？"
- "自研方案 2 期拆分是否改变已确认的时间约束？需要重走哪些确认？"
- "如果结论是'有条件做'，条件是新增约束，是否要同步到上游 §7 依赖？"

**Common traps**:

- 悄悄改范围不回流
- 只更新评估产物不回写上游
- 漏掉级联影响（下游 PRD 已引用旧边界）

---

## Cross-cutting tips

1. **排序原则**：Clarify 一次只问 1 个，按 Impact × Uncertainty 排序，先问阻断性高的。
2. **不要问 AI 能查的事实**：公开报价、可比案例、行业成本数据，让 AI 自己查。
3. **每问必带 AI 初步判断**：不要让业务方从零开始想问题。
4. **三选项常驻**：给 2-4 个互斥选项 + 「其他」兜底。
5. **跳过按钮**：非阻断项允许业务方打 ⚠️ 风险标签先跳过。
6. **回写位置必填**：每答一题必须能精确指向评估产物的哪个章节。
