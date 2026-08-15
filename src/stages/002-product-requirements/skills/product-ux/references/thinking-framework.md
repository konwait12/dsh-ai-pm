# 产品 UX 思考框架（Product UX Thinking Framework）

## 公共核心（Common Core，必用 MANDATORY）

应用 `src/framework/thinking-core.md` §1 的 **6 个核心透镜**（第一性原理 First Principles、系统思维 Systems Thinking、对抗性审视 Adversarial Review、逆向验证 Reverse Validation、确认偏误防御 Confirmation Bias Defense、知识边界 Knowledge Boundary），以及 §2 中与本 work item 相关的检查层透镜（阶段收口前的 Pre-Mortem、Human Gate 前的 Fresh-Eyes、验收标准前的可测试性 Testability、写作时的结论先行 Conclusion First + 读者视角 Reader Perspective）。只记录会改变候选产物的发现——不要逐字重复核心透镜分析。

1. **范围透镜（Scope lens）**：in、out、假设、依赖、系统归属与发布边界。
2. **故事→功能透镜（Story-to-feature lens）**：按用户能力与业务结果分组，而不是按 CRUD 界面。
3. **系统透镜（System lens）**：模块、外部系统、交接与归属缺口。
4. **流程透镜（Flow lens）**：入口、步骤、决策、主/备选/失败路径、取消与恢复。
5. **状态透镜（State lens）**：空、加载、部分、成功、失败、超时、权限不匹配与过期数据。
6. **角色/渠道透镜（Role/channel lens）**：角色专属访问路径与实质性的桌面/移动/渠道差异。
7. **第一性原理透镜（First-principles lens）**：删除不为已确认故事或目标贡献的功能。
8. **对抗/逆向透镜（Adversarial/reverse lens）**：尝试打断流程，然后逐功能逆向核验到某个故事。

停在结构性产品模型。详细的反馈、校验、权限、业务策略与验收属于下游。
