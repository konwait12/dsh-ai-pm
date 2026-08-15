# Thinking Framework · feature-list

用这些透镜改进候选内容。不要把完整分析粘贴进产物。

## Common Core（必用）

应用 `src/framework/thinking-core.md` §1 的 **6 个核心透镜**（第一性原理、系统思考、对抗性审查、逆向验证、确认偏误防御、知识边界认知），以及 §2 中与本 work item 相关的校验层透镜（阶段收口前事前验尸、Human Gate 前空杯视角、验收依据前可测试性、写作时结论先行 + 读者视角）。只记录改变候选内容的发现——不要逐字重复核心透镜分析。

## 领域透镜 A：单一职责

- 每个 FEA-XXX 是否是一个开发者能独立命名并构建的内聚能力？
- 哪些候选"功能"其实是更大的功能内部、或属于 product-ux 的 UX 步骤、页面区域或子操作？
- 只有当两个能力有不同用户、不同数据或不同触发路径时才拆分；否则合并。

## 领域透镜 B：边界清晰与互不重叠

- 每个 FEA-XXX 是否有明确的 in/out？没有边界的功能是黑盒。
- FEA-A 与 FEA-B 是否重叠到用户或下游子 skill 无法判断一个在哪里结束、另一个在哪里开始？
- 边界测试：我能否描述一个动作并准确指向一个 FEA？如果两个 FEA 都声称拥有它，则合并或重画。

## 领域透镜 C：可追溯性

- 每个 FEA-XXX 的 `来源` 指向一个已确认的 `ST-XXX`。
- 反向检查：每个 P0 ST-XXX 有 ≥1 个 FEA-XXX 支撑。
- 已确认的功能 → `FACT` / `DECISION`；AI 推导的新增 → `AI_INFERENCE`；无法确认 → `UNKNOWN`。

## 领域透镜 D：优先级纪律

- P0：缺它某个已确认故事无法被满足（无 workaround）——MVP 必须项。
- P1：重要，存在 workaround——应有项。
- P2：锦上添花——可有项。
- 每行都要说明 WHY 这个优先级；推迟 P0 破坏故事，推迟 P1 损失效率。

## 领域透镜 E：下游可消费性

- functional-flow / business-rules 能否不重新调研故事就直接消费这个 FEA？
- 一句话描述是否足够具体，能为后续 §分功能详述 与 §业务规则 提供种子？
- 任何含糊到需要追问才能定义的功能 → 标 `UNKNOWN` 或拆分。

---

## 低密度降级模式

当已确认故事集合只是一句没有任何范围承载内容的话时，上述透镜无法产生有意义的工作。把它们套在不足的信息上会产出冗长但空洞的分析。切换到降级模式：

```text
low-density input → skip domain-lens ideation
                   → do not enter Generate / Audit
                   → output only:
                      a) input sufficiency assessment (what is confirmed, what is missing)
                      b) batched clarifying questions (each: AI preliminary judgment + options + impact + owner)
                   → status = needs_user_input
                   → wait for human to fill in, then re-enter Preflight in sufficient mode
```

降级触发条件（任一即触发）:

- 已确认故事集合不含任何范围承载内容（无清单来源、无边界、无优先级信号）
- 来源只是复述 UX 愿望，没有功能级决策
- 决定 FEA 集合的功能边界无法被任何来源确认

本模式不是失败状态。这是对信息不足的正确响应——省下人工评审时间，产出一批干净的澄清问题，而不是一张满是 `待确认` 行的 §功能清单 表。

## 确认偏误防御（feature-list 特化）

1. 我是否把故事膨胀成了故事从未要求的功能（越权），或静默丢掉了没有明显功能的故事（缺口）？
2. 我是否把每个推断的功能边界标成 `FACT`，还是先检查它是 `ASSUMPTION` / `AI_INFERENCE`？
3. 如果两个故事会推出重叠功能，我是保持重叠可见——还是静默选择了一个边界？

## 知识边界（feature-list 特化）

1. 我是否区分了"故事说功能存在"（`FACT`）、"我从流程推断出边界"（`AI_INFERENCE`）与"还没人决定范围"（`UNKNOWN`）？
2. 我是否把缺失的边界保留在父产物的 待确认问题 登记表中，而不是自己发明？
3. 知识状态标签是写在每个 FEA 行上，还是埋在叙述里？
