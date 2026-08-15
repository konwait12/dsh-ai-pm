# 功能描述思考框架（Function Description Thinking Framework）

## 公共核心（Common Core，必用 MANDATORY）

应用 `src/framework/thinking-core.md` §1 的 **6 个核心透镜**（第一性原理 First Principles、系统思维 Systems Thinking、对抗性审视 Adversarial Review、逆向验证 Reverse Validation、确认偏误防御 Confirmation Bias Defense、知识边界 Knowledge Boundary），以及 §2 中与本 work item 相关的检查层透镜（阶段收口前的 Pre-Mortem、Human Gate 前的 Fresh-Eyes、验收标准前的可测试性 Testability、写作时的结论先行 Conclusion First + 读者视角 Reader Perspective）。只记录会改变候选产物的发现——不要逐字重复核心透镜分析。

对每个功能检查：

1. 目的与上游价值；
2. 执行者、权限与前置条件；
3. 用户动作与系统响应（`IX`）；
4. 领域策略、计算与状态约束（`BR`）；
5. 输入、跨字段与跨系统校验（`VL`）；
6. 正常、备选、异常、失败、超时、重复、取消、重试、回滚与恢复路径；
7. 状态转移与副作用；
8. 可度量的验收（`AC`）；
9. 仅在相关时的安全、性能、可用性、无障碍与合规；
10. 逆向追溯到功能、故事与目标。

交互规则与业务规则在功能块中共存，但绝不能被合并成一条含糊的句子。
