# Question Patterns · Competitive Research

Eight canonical question templates for the one-question-at-a-time Clarify loop. Each entry gives:

- **When to use** — the trigger condition
- **Question shape** — the prompt structure
- **Three examples** — paraphrased real cases (desensitized)
- **Common traps** — typical AI mistakes when asking this kind of question

Use these as reference when generating a new question in a Clarify Session. See `SKILL.md` § Thinking Prompts → Clarify for runtime rules.

---

## 1. 调研目标（Research Goal）

**When to use**: when the research goal is missing — AI does not know whether the analysis is business-level (solution direction) or functional-level (feature design).

**Question shape**:

```
[为什么重要] 竞品调研的层级决定对比维度和产出深度。
请明确: 这次调研是 [业务级]（定产品方向/定位）还是 [功能级]（定具体功能怎么设计）?
它最终要支撑哪个产品决策?
```

**Examples**:

- "这次竞品调研是定整个会员体系的定位，还是只定'积分规则'这一个功能怎么做？"
- "调研结论要支撑哪个决策——要不要做会员等级、还是等级怎么分档？"
- "调研后下一步是 user-journey 还是 product-ux？这决定我把竞品分析写到什么粒度。"

**Common traps**:

- 不问层级直接默认业务级，导致功能级问题被忽略
- 调研目标与已确认的目标脱节
- 让业务方从零定义调研框架（应先给 AI 初步判断）

---

## 2. 竞品范围（Competitor Scope）

**When to use**: when competitor candidates are unknown, or the user named one competitor without confirming it is the right benchmark.

**Question shape**:

```
[为什么重要] 竞品选择决定分析结论的适用面。
当前候选是 [已有列表]。请确认/补充:
1. 直接竞品（同品类）?
2. 间接竞品（不同品类、满足同一需求）?
3. 参照竞品（跨领域、最佳体验）?
```

**Examples**:

- "除了提到的 [竞品A]，是否还有 [竞品B]（同品类）和 [竞品C]（会员体系的跨领域参照，比如航空常旅客）？"
- "这个会员等级功能，建议看 3-5 个竞品。你指定了 [竞品A]，其余 2 个由我按直接/间接补充，可以吗？"
- "[竞品X] 和我们的目标用户差异很大（他们 2B 我们 2C），是否仍作为主要对标？"

**Common traps**:

- 只研究用户指定的竞品，不加判断
- 只列同品类，漏掉真正替代需求的间接竞品
- 超过 5 个竞品稀释分析深度

---

## 3. 对比维度（Comparison Dimensions）

**When to use**: when comparison dimensions are undefined, or the AI's proposed dimensions may not match what the business cares about.

**Question shape**:

```
[为什么重要] 维度选错，分析再深也答不到决策点。
我计划按 [候选维度] 对比。其中哪些是这次决策的关键?
对照已确认目标 [G#]，还需要补哪些维度?
```

**Examples**:

- "针对'缩短客户入驻'这个目标，我计划按 入驻时长、表单字段数、集成深度 对比，是否覆盖了关键点？"
- "价格维度对这次定级重要吗？如果不重要我可以省略，避免干扰。"
- "是否要纳入'运营/客服成本'维度？竞品公开数据可能不全，需要你判断重要性。"

**Common traps**:

- 用通用清单（功能/价格/体验）不映射到目标
- 塞入竞品无公开数据的维度，导致整列 `待确认`
- 维度太多失去焦点

---

## 4. 数据来源（Data Source）

**When to use**: when a material claim lacks a source, or when vendor claims and user reviews conflict.

**Question shape**:

```
[为什么重要] 竞品信息的可靠性决定结论可信度。
当前 [竞品/功能] 的依据来自 [来源]。是否需要:
1. 补充 [独立来源]（应用商店评分 / 用户评测 / 第三方报告）?
2. 或认可现状并标注为 AI_INFERENCE?
```

**Examples**:

- "竞品A的'自动续费'只能从官网 FAQ 确认，应用商店差评里有用户抱怨扣费。两处说法矛盾，哪边可信？还是都保留标 CONFLICT？"
- "竞品B定价只有第三方代理商报价，无官方公开价。是否接受为 AI_INFERENCE？"
- "这条'竞品C 不做 X'——搜索没有找到，是确无还是我没检索到？需要你确认是否值得再挖。"

**Common traps**:

- 官网营销话术当成功能事实
- 单一利益方证据（竞品自己说好）不交叉验证
- 检索不到就当"竞品没有"，不区分 UNKNOWN

---

## 5. 结论适用性（Insight Applicability）

**When to use**: when an insight is about to be copied but its applicability to our context is unverified.

**Question shape**:

```
[为什么重要] 竞品做得好 ≠ 我们做了就好，语境不同结论可能失效。
竞品X 的 [做法] 在其 [语境] 下有效。它适合我们吗?
前提条件 [列举] 在我们这里成立吗?
```

**Examples**:

- "竞品A 用 5 档会员是因为用户量大、可分层运营。我们当前用户量是它的 1/10，5 档是否过早？建议降到 3 档吗？"
- "竞品B 的免费模式靠广告变现，我们无广告位，免费策略是否仍适用？"
- "竞品C 的'先付费后体验'适合高客单，我们客单价低，是否照搬？"

**Common traps**:

- 把"竞品有"直接当成"我们该有"
- 忽略语境差异直接照搬
- 不问适用前提就写进结论

---

## 6. 差异化优先级（Differentiation Priority）

**When to use**: when multiple differentiation opportunities exist but the decision maker has not prioritized them.

**Question shape**:

```
[为什么重要] 差异化机会很多，投入要聚焦。
当前机会: [A/B/C]。哪个与已确认目标 [G#] 关联最强?
如果资源只够做 1-2 个，先做哪个?
```

**Examples**:

- "差异化机会有：一键迁移（竞品都没有）、更低价格、更深集成。目标 G2 是'降低迁移成本'，是否优先做一键迁移？"
- "竞品都不支持 [X]，但 X 的开发成本高。你判断 X 是真实需求还是自嗨？"
- "如果 [竞品A] 下季度也上线了我们准备差异化的功能，我们还有备选吗？"

**Common traps**:

- 把竞品都不做当作"一定是机会"，不问需求真实性
- 一次推多个差异化不做取舍
- 不预判竞品的跟进

---

## 7. 时间与更新（Recency / Update）

**When to use**: when a material competitor claim is stale, or the competitor recently changed direction.

**Question shape**:

```
[为什么重要] 竞品信息会过期，过期的结论会误导决策。
[竞品/功能] 的资料检索于 [日期]。是否有更新的公开信息?
竞品近期是否有重大改版 / 新定价 / 战略调整?
```

**Examples**:

- "竞品A 的定价页我检索于 3 个月前，是否已改版？需要重新核验吗？"
- "[竞品B] 上月宣布转型，是否会影响它作为对标的价值？要不要换对标？"
- "行业报告是去年的，渗透率数据是否还有参考价值？"

**Common traps**:

- 复用旧分析不重新核验
- 忽略竞品动态变化
- 把历史结论当现状

---

## 8. 范围边界（Scope Boundary）

**When to use**: when research scope creep is high, or the boundary between this research and other ongoing work is unclear.

**Question shape**:

```
[为什么重要] 竞品调研很容易蔓延成完整行业研究。
本期调研 [包含 / 不包含] 哪些?
是否只覆盖 [目标 G#] 相关竞品，不扩展到 [无关领域]?
```

**Examples**:

- "本期只做会员等级的竞品调研，还是连带积分、权益、风控一起调研？如果全做，产出会很大，是否分批？"
- "要不要纳入海外竞品？如果纳入，语言和区域差异如何处理？"
- "竞品定价策略属于本次范围吗？还是留给商务/运营决策？"

**Common traps**:

- 从功能调研蔓延到行业全景研究
- 不写"不做什么"，范围无限膨胀
- 把范围当调研目标

---

## Cross-cutting tips

1. **排序原则**：Clarify 一次只问 1 个，按 Impact × Uncertainty 排序，先问阻断性高的。
2. **不要问 AI 能查的事实**：竞品官网、公开定价、应用商店信息，让 AI 自己查，不要让业务方回答。
3. **每问必带 AI 初步判断**：不要让业务方从零开始想问题。
4. **三选项常驻**：给 2-4 个互斥选项 + 「其他」兜底。
5. **跳过按钮**：非阻断项允许业务方打 ⚠️ 风险标签先跳过。
6. **回写位置必填**：每答一题必须能精确指向竞品分析产物的哪个章节。
