# 思考框架 · Requirement Restate（双模式能力）

用这些透镜改进候选产物 / 候选集。不要把完整分析倾倒进产物——只记录会改变重述（模式一）或成为候选（模式二）的发现。

## 公共核心（Common Core，必用 MANDATORY）

应用 `src/framework/thinking-core.md` §1 的 **6 个核心透镜**（第一性原理 First Principles、系统思维 Systems Thinking、对抗性审视 Adversarial Review、逆向验证 Reverse Validation、确认偏误防御 Confirmation Bias Defense、知识边界 Knowledge Boundary），以及 §2 中与本 work item 相关的检查层透镜（阶段收口前的 Pre-Mortem、Human Gate 前的 Fresh-Eyes、写作时的结论先行 Conclusion First + 读者视角 Reader Perspective）。只记录会改变候选产物的发现——不要逐字重复核心透镜分析。

---

## 模式一 · 需求复述（RR-NNN）lens

### Source Fidelity（来源保真度）

如果重述产物不能忠实反映来源，它就是无价值的：

- 每条 RR-NNN 行是否都追溯到具体的 SRC-ID，精确到段落或时间戳？
- `original_phrase`（原始措辞）是否 verbatim 保留（方言、口语都保留）而不是被"清洗"过？
- 重述是否是来源的翻译，而不是在它之上叠加的解读？
- "重述 vs 原话"的差异是否正是重点——而不是被抹平？

### Atomicity（原子性）

- 有没有一行塞进了两个不同的诉求？
- 每行是否都能作为 stakeholder 可以回答"是/否"的单一主张被测试？
- 如果一行需要"并且还要…"才完整，就拆开它。

### No Solution Leak（无方案泄露）

- 有没有一行包含提议的方案、技术或设计（"做一个移动应用"、"用 QR 码"）？
- 来源中提到的方案是否记录为带 `solution_leak=true` 的 *hint*，而不是当作决策？
- 开发者读重述时，是否会在诉求确认之前就开始设计？

### Stakeholder Recognition（stakeholder 认可度）

- stakeholder 能否在每一行里认出他们自己的话？
- 措辞是 stakeholder 的，还是 AI 用自己词汇库做的转述？
- 这份产物能否原样发回给 stakeholder，并读起来是忠实的？

### Confirmation Bias Defense（确认偏误防御，重述特化）

AI 最可能悄悄把 stakeholder 的措辞"改进"或"对齐"成 AI 认为 stakeholder 想表达的意思：

1. 我是否改了他们的词让它更"干净"？（修复：保持 verbatim。）
2. 我是否把两个听起来相似但不同的诉求合并进一行？（修复：保持分开，注明重叠。）
3. 我是否通过选择更方便的措辞解决了一个矛盾？（修复：保留双方，标 CONFLICT。）

### Knowledge Boundary（知识边界，重述特化）

1. 我是否区分了"来源说 X"（FACT）、"我推断他们想表达的意思"（AI_INFERENCE）与"还没人知道"（UNKNOWN）？
2. 冲突是否保留双方措辞，而不是丢了一方？
3. 重述的边界（我们没能转写的、我们猜测的）是否可见？

---

## 模式二 · 发散收敛（SCN-XXX）lens

### First Principles（第一性原理）

- 这个想法想改变什么可观察结果？
- 没有提议的功能时，存在的底层问题是什么？
- 为什么是现在？
- 哪些主张是伪装成需求的假设？

### Divergence Domain Lenses（发散领域 lens）

发散式探索扫过以下 **12 个场景维度**。对每个维度问对应的问题并产出候选想法；一旦某个维度的候选开始重复（饱和），停止该维度：

| # | 维度 Dimension | 发散提问 |
|---|---|---|
| 1 | lifecycle 生命周期 | 这件事从开始到结束有哪些阶段？当前停留在哪个阶段？ |
| 2 | roles 角色 | 谁会发起、执行、受益、受扰？每类角色的动机与顾虑？ |
| 3 | normal / alternate / exception / failure / timeout 正常·备选·异常·失败·超时 | 主路径是什么？备选路径？系统失败与超时怎么处理？ |
| 4 | permission 权限 | 谁有权限做什么？不同角色看到的范围是否不同？ |
| 5 | data condition 数据条件 | 哪些数据必须存在才能继续？数据缺失/脏数据怎么办？ |
| 6 | handoff 交接 | 哪个节点从一个人/系统交接到另一个人/系统？ |
| 7 | dependency 依赖 | 依赖哪些内部系统、外部供应商、审批或时间窗口？ |
| 8 | cancellation 取消 | 事情中途取消的触发条件与善后是什么？ |
| 9 | retry 重试 | 哪些步骤需要重试？重试上限与策略？ |
| 10 | rollback 回滚 | 已生效的结果能否回滚？回滚的代价与边界？ |
| 11 | change-recovery 变更恢复 | 需求或方案变更后，如何恢复到一致状态？ |
| 12 | constraint 约束扫描 | 时间、预算、技术、合规四类约束的候选边界？ |

### Clustering And Deduplication（聚类与去重）

- 合并用不同措辞表达同一独立想法的候选；保留最清晰的措辞。
- 跨越两个维度的候选留在它的主维度；在 Candidate 单元格中交叉引用另一个维度。
- 饱和规则：当一个维度连续两轮产不出新的独立想法时，停止该维度。

### Adversarial Review（对抗性审视）

- 所述想法是否只是某个未明说问题的症状？
- 政策/流程改变能否在没有任何产品改动的情况下满足它？
- 某个候选的证据是否只来自一个利益相关方？
- 如果想法被反方向重写，哪个候选能存活下来？

### Reverse Validation（逆向验证）

从预期结果出发，问成功必须成立什么；用结果揭示缺失的前提、依赖、基线数据与约束，作为新候选。

### Knowledge Boundary（知识边界，发散特化）

- 每个候选在人工标记 `include` 之前都是 `AI_INFERENCE`；发散集合里没有任何东西是业务事实。
- 证据必须说明 *AI 为什么这么想*（来自原始想法、已登记来源或常识惯例）——绝不要把推断当作观察呈现。
- `research` 处置意味着"现在无法判定"：登记到 issue-record / 一个 QuestionRecord，而不是让它静默搁置。

---

## 两模式通用 · Sparse Degradation Mode（稀疏降级）

**模式一**（单句无材料，见 `SKILL.md` § Preflight L1 gate）——lens 无法做有意义工作，切降级模式：

```text
low-density input → skip lens ideation
                   → do not enter Generate / Audit
                   → output only:
                      a) input sufficiency assessment (char count, attachments, domain guess)
                      b) batched clarifying questions (each: AI preliminary judgment + options + impact + owner)
                   → status = needs_user_input
                   → wait for human to fill in, then re-enter Preflight in sufficient mode
```

**模式二**（单句无材料，且负责人不可得 / 首批问题未答）——发散仍可进行但输出降级：

```text
sparse input → diverge into candidate skeletons (short evidence: "AI 推断，无书面来源")
             → do not force complete Evidence/Impact
             → batch ≤5 clarifying questions (each: AI preliminary judgment + options + impact + owner)
             → status = needs_user_input
             → wait for human answers, then re-enter Generate in sufficient mode
```

降级触发条件（满足任一即可）：

- 输入长度 < 50 字符且无附件
- 无来源材料，只有记忆转述（模式一）/ 没有业务领域、没有角色提及、没有时间约束（模式二）
- 用户只提到功能或实现，背后没有可验证的诉求（"做一个打卡功能"）

此模式不是失败状态。它产出一批干净的澄清问题，而不是一份塞满 `待确认` 的臃肿重述/候选表——从无到有构建的重述只会是 AI 自己的猜测，却被当作 stakeholder 的话呈现。
