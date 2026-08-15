# 思考框架（Thinking Framework）

用这些透镜改进候选产物。不要把完整分析倾倒进产物。

## 公共核心（Common Core，必用 MANDATORY）

应用 `src/framework/thinking-core.md` §1 的 **6 个核心透镜**（第一性原理 First Principles、系统思维 Systems Thinking、对抗性审视 Adversarial Review、逆向验证 Reverse Validation、确认偏误防御 Confirmation Bias Defense、知识边界 Knowledge Boundary），以及 §2 中与本 work item 相关的检查层透镜（阶段收口前的 Pre-Mortem、Human Gate 前的 Fresh-Eyes、验收标准前的可测试性 Testability、写作时的结论先行 Conclusion First + 读者视角 Reader Perspective）。只记录会改变候选产物的发现——不要逐字重复核心透镜分析。

## 第一性原理（First Principles）

- 需要改变的可观察结果是什么？
- 没有提议的功能时，存在的底层问题是什么？
- 为什么是现在？
- 哪些主张是伪装成需求的假设？
- 如果去掉提议方案，所述目标仍然成立吗？

## 现状（Current State）

- 今天这项工作如何处理：系统、人工流程、变通做法，还是没有流程？
- 哪些角色负责哪些部分？
- 什么证据表明现状不足？
- 造成了什么成本、延迟、风险、错误或错失机会？
- 哪些部分已经有效、不能破坏？

## 目标质量（Goal Quality）

区分：

- 业务结果：对组织或用户改变什么；
- 交付结果：必须存在什么能力；
- 成功判断：什么证据能显示改进；
- 非目标：这项工作不试图解决什么。

当来源无法支撑数值 KPI 时，不要强行套一个。写明临时度量，并请负责人确认基线、目标值与时间窗口。

## 干系人与系统透镜（Stakeholder And System Lens）

只识别背景基线所需的：

- 需求提出者与业务负责人；
- 主要受影响用户与次要受影响角色；
- 目标决策负责人与最终评审人；
- 运营、支持、合规、数据或集成干系人（当实质性时）；
- 相关系统与外部依赖。

把详细角色旅程与权限矩阵留给下游工作。

## 系统思维（Systems Thinking）

检查预期的改变是否影响上游/下游流程、其他角色的工作量、数据归属、外部服务、政策、时间或运营支持。

## 对抗性审视（Adversarial Review）

尝试推翻当前的框定：

- 所述问题是否只是症状？
- 能否通过政策/流程改变解决，而无需产品改动？
- 证据是否只来自一个利益相关方？
- 目标是否在优化一个角色的同时损害另一个？
- 紧迫性是否在没有真实截止日期或后果的情况下被断言？
- 在替代方案被理解之前，提议方案是否已被预定？

只记录影响候选产物或需要确认的发现。

## 逆向验证（Reverse Validation）

从预期结果出发，问成功必须成立什么。用结果揭示缺失的前提、依赖、基线数据、归属与约束。

---

## 低密度降级模式（Low-Density Degradation Mode）

当输入是单条自然语言句子且无附带材料时（闸门见 `SKILL.md` §1.1），上述七个透镜无法做有意义的工作。把透镜用在信息不足上会产生冗长但空洞的分析。切换为降级模式：

```text
low-density input → skip all 7-lens ideation
                   → do not enter Generate / Audit
                   → output only:
                      a) input sufficiency assessment (char count, attachments, business-domain guess)
                      b) batched clarifying questions (each: AI preliminary judgment + options + impact + owner)
                   → status = needs_user_input
                   → wait for human to fill in, then re-enter Preflight in sufficient mode
```

降级触发条件（满足任一即可）：

- 输入长度 < 50 字符且无附件
- 没有业务领域、没有角色提及、没有时间约束
- 用户只提到功能或实现（"加一个按钮"、"实现 X"），且无业务上下文

此模式不是失败状态。它是信息不足时的正确反应——节省人工评审时间，产出一批干净的澄清问题，而不是一份塞满 `待确认` 的 14 章节产物。

## 确认偏误防御（Confirmation Bias Defense，Wave-1 特化）

背景产物是 AI 最容易不加质疑地镜像请求方框定的第一处：

1. 我是否把请求方的方案复述成业务目标？还是把"他们要什么"与"它解决什么问题"分开了？
2. 如果请求方的前提是错误的（例如现状其实没问题），我的产物是让它可见——还是悄悄附和？
3. 我是否把来自来源的每条主张都标为 FACT，还是先检查它其实是 ASSUMPTION / AI_INFERENCE？

## 知识边界（Knowledge Boundary，Wave-1 特化）

1. 我是否区分了"来源说 X"（FACT）、"我推断 X"（AI_INFERENCE）与"还没有人知道 X"（UNKNOWN）？
2. 我是否把临时指标标为需要负责人确认，而不是当作既定的 KPI 呈现？
3. 约束与未知是否单独放进自己的寄存器，还是埋在散文里？
