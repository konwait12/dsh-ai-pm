# Thinking Framework · business-rules

用这些透镜改进候选内容。不要把完整分析粘贴进产物。

## Common Core（必用）

应用 `src/framework/thinking-core.md` §1 的 **6 个核心透镜**（第一性原理、系统思考、对抗性审查、逆向验证、确认偏误防御、知识边界认知），以及 §2 中与本 work item 相关的校验层透镜（阶段收口前事前验尸、Human Gate 前空杯视角、验收依据前可测试性、写作时结论先行 + 读者视角）。只记录改变候选内容的发现——不要逐字重复核心透镜分析。

## 领域透镜 A：领域策略提取

- 为了让该功能成立，系统必须计算、校验与强制什么——而不是 UI 显示什么？
- 哪些已确认的故事/UX 声明隐藏了系统必须强制但未被明说的隐含约束？
- 哪些候选"规则"其实是屏幕流程叙述（按钮顺序、跳转、toast）而属于 interaction-rules？

## 领域透镜 B：规则归类

对每个候选规则，强制恰好一个类别：

- 计算 Calculation: 派生值（金额、数量、分数、截止时间）——写公式 + 单位 + 舍入/边界处理
- 约束 Constraint: 允许范围、唯一性、业务禁止——写拒绝行为
- 条件 Condition: 决定某个状态/场景是否成立的判断
- 权限 Permission: 谁可以 / 谁不可以，按角色或数据范围
- 时序 Timing: 顺序、依赖、允许/禁止的先后

不要用「待确认」填类别列——未归类的规则无法被下游 validation-rules 或 state-machine 消费。

## 领域透镜 C：确定性

- 开发者能否不追问就把这条规则转成代码？
- 触发是否精确、逻辑是否封闭（同一输入 → 同一输出）？
- 边界与拒绝路径是否写全？
- 任何像「合理」「适当」「尽快」「视情况」这样的词 → 规则没想清楚；拆分它或标 `UNKNOWN`。

## 领域透镜 D：可追溯性

- 每条 BR-XXX 的 `来源` 指向 `ST-XXX` 或 `FEA-XXX`。
- 反向检查：每个 P0 FUN-XXX 有 ≥1 条 BR-XXX 支撑。
- 已确认的规则 → `FACT` / `DECISION`；AI 推导的新增 → `AI_INFERENCE`；无法确认 → `UNKNOWN`。

## 领域透镜 E：边界纪律

| 内容特征 | 归属 |
|---|---|
| 用户操作 → 系统响应、页面行为 | interaction-rules `IX-XXX` |
| 字段格式、长度、必填、正则 | validation-rules `VL-XXX` |
| 状态迁移、触发事件、副作用 | state-machine |
| 失败、超时、重试、回滚、恢复 | exception-handling |
| 可验证的验收条件 | acceptance-criteria `AC-XXX` |
| 系统必须在领域层计算/强制 | **本子 skill `BR-XXX`** |

---

## 低密度降级模式

当某 P0 功能已确认的故事/UX 只是一句没有规则承载内容的话时，上述透镜无法产生有意义的工作。把它们套在不足的信息上会产出冗长但空洞的分析。切换到降级模式：

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

- 某功能的故事/UX 不含任何规则承载内容（无阈值、无策略、无计算）
- 已确认来源只是复述 UI 流程，没有领域逻辑
- 决定规则结果的约束无法被任何来源确认

本模式不是失败状态。这是对信息不足的正确响应——省下人工评审时间，产出一批干净的澄清问题，而不是一张满是 `待确认` 行的 §业务规则 表。

## 确认偏误防御（business-rules 特化）

1. 我是否把已确认的 UX 流程复述成"规则"，而没有把领域逻辑从屏幕叙述中分离出来？
2. 我是否把每个推断的约束标成 `FACT`，还是先检查它是 `ASSUMPTION` / `AI_INFERENCE`？
3. 如果两条规则会矛盾（一条允许、一条禁止同一情况），我是保持冲突可见——还是静默选了一个？

## 知识边界（business-rules 特化）

1. 我是否区分了"故事说阈值是 X"（`FACT`）、"我从流程推断出 X"（`AI_INFERENCE`）与"还没人决定 X"（`UNKNOWN`）？
2. 我是否把缺失的约束保留在父产物的 待确认问题 登记表中，而不是自己发明数值？
3. 知识状态标签是写在每条规则行上，还是埋在叙述里？
