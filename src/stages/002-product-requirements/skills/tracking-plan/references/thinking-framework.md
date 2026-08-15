# 思考框架 · 埋点与追踪计划（Thinking Framework · Tracking Plan）

用这些透镜改进候选产物。不要把完整分析倾倒进产物。

## 公共核心（Common Core，必用 MANDATORY）

应用 `src/framework/thinking-core.md` §1 的 **6 个核心透镜**（第一性原理 First Principles、系统思维 Systems Thinking、对抗性审视 Adversarial Review、逆向验证 Reverse Validation、确认偏误防御 Confirmation Bias Defense、知识边界 Knowledge Boundary），以及 §2 中与本 work item 相关的检查层透镜（阶段收口前的 Pre-Mortem、Human Gate 前的 Fresh-Eyes、验收标准前的可测试性 Testability、写作时的结论先行 Conclusion First + 读者视角 Reader Perspective）。只记录会改变候选产物的发现——不要逐字重复核心透镜分析。

## 指标追溯（Metric Traceability）

每个事件必须通过支撑一个指标与一个目标来赢得它的位置：

- 这个事件证明或度量哪个 G-X（background-goal）？
- 它喂养哪种指标类型：`north_star` / `funnel_step` / `counter` / `latency` / `conversion` / `retention`？
- 如果某个事件不映射到任何 G-X，它是删除或降为 `nice_to_track` 的候选。
- 从每个 G-X 倒推：上线后验证它所需的 事件与属性 是否齐全？

## 事件粒度（Event Fidelity）

- 事件是一个"用户有意义"的动作，而不是几个动作的捆绑？
- 触发条件是否精确到两个工程师会埋同一个时点？
- 属性集是否完整（每个属性有 key / type / example / pii_flag / required）？
- 事件是否在用户动作序列的正确时点触发（校验前/后、成功前/后）？

## PII 纪律（PII Discipline）

- 哪些属性是个人标识符、行为指纹或敏感内容？
- `false`（非 PII）→ 标准上报；`quasi`（IP / 设备 ID / 位置）→ 哈希 + 用户授权；`true`（姓名 / 证件号 / 手机）→ 加密 + 业务必要性；`sensitive`（健康 / 财务 / 宗教）→ 访问控制 + 最小化 + 显式同意。
- 每个 PII 事件是否在 `notes` 中带有显式的数据保留规则？
- 采集这个属性能否通过数据保护评审？

## 覆盖 vs 噪声（Coverage vs Noise）

- 每个 P0 FUN-XXX 是否至少有一个 `must_track` 事件？
- 有没有孤儿事件（无 FUN-XXX、无 G-X）？
- 事件清单是否免于"全量追踪"噪声——即没有指标、目标或决策用途的事件？
- 重复项是否被合并到一个一致的 `event_name` 下？

## 命名一致性（Naming Consistency）

- 每个 `event_name` 是否 snake_case verb_noun（`checkout_submit_click`）且全局唯一？
- `event_type` 是否属于 `page_view` / `click` / `submit` / `exposure` / `success` / `error` / `custom`？
- 跨功能时，同一动作与同一含义是否复用同一事件（不允许 `click_btn` vs `button_click`）？

## 系统思维（Systems Thinking）

- 事件是否需要服务端埋点（后端事件）、第三方 SDK 或小程序桥？
- 谁采集、清洗并拥有事件流？该责任在计划中是否可见？
- 上报时机（realtime / near_realtime / batch / on_session_end）是否匹配指标的需求？

---

## 低密度降级模式（Low-Density Degradation Mode）

当上游未确认（function-description FUN-XXX 或其规则缺失）或追踪需求只是一句不带资格的单句时，上述透镜无法做有意义的工作。切换为降级模式：

```text
low-density / upstream-not-confirmed input → skip lens ideation
                                             → do not enter Generate / Audit
                                             → output only:
                                                a) input sufficiency assessment (upstream confirmed? which G-X to prove? platforms?)
                                                b) batched clarifying questions (each: AI preliminary judgment + options + impact + owner)
                                             → status = needs_user_input
                                             → wait for upstream confirmation or human input, then re-enter Preflight
```

降级触发条件（满足任一即可）：

- function-description（FUN-XXX）或其上游规则未确认
- 没有要映射事件的目标（G-X）
- 用户只说"为 X 加埋点"，没有指标、平台或触发上下文

此模式不是失败状态。在上游确认之前构建的事件合约会是发明出来的数据——比没有计划更糟。
