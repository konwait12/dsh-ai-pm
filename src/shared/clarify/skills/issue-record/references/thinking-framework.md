# 思考框架 · 问题清单（Issue Record）

使用以下透镜改进候选产物。不要把完整分析倾倒进产物。

## 公共核心（Common Core · 必用）

应用 `src/framework/thinking-core.md` §1 的 **6 个核心透镜**（第一性原理、系统思维、对抗性审查、反向验证、确认偏误防御、知识边界），以及 §2 中与本 work item 相关的检查层透镜（阶段收口前的 Pre-Mortem、Human Gate 前的 Fresh-Eyes、写作时的 Conclusion First + Reader Perspective）。只记录会改变候选产物的发现——不要逐字重复核心透镜分析。

## 问题分诊（Triage）

任何信号的第一个决策是类别。按顺序问：

- **BLK（阻断）**：这真的阻断推进吗，还是有变通方案？如果有变通方案，它可能是 RSK，而不是 BLK。
- **RSK（风险）**：这会变成阻断吗？它有缓解措施吗？
- **DEC（待决）**：需要某个具名的人决策吗？谁，什么时候？
- **INF（信息缺口）**：是否缺少来源、数据或权限？
- **CLS（歧义）**：措辞是否模糊，需要 owner 消除歧义？
- **OUT（范围外）**：它被提出来了，但在本项目范围之外？

错误分诊（把 DEC 当作 BLK，把 CLS 当作 INF）会把问题交给错误的 owner，使其停滞。

## 责任归属（Ownership）

- 每个 open 问题都有有权限解决它的 owner 吗？
- owner 是个人或角色，不是"TBD"？（修复：在 Clarify 中询问 owner。）
- 对 `accepted` 风险：只有决策 owner 可以接受。是具名决策 owner 接受的，还是 AI 接受的？

## 时效与升级（Aging And Escalation）

- 每个 BLK / DEC 都带 `target_close` 吗？没有的话，它可能无限期漂移。
- 超过 30 天的问题是否审查过升级？陈旧问题是项目健康信号。
- 每次升级是否路由给有权限行动的新 owner？

## 闭环验证（Closed-Loop Verification）

- `resolved` 问题链接到关闭它的产物变更——还是只是声明已解决？
- 解决是否由与实现者不同的验证人核实？
- 已接受的风险是否携带接受条件和日期，而不只是"accepted"？

## 事前验尸（Pre-Mortem · thinking-core §2 领域 lens）

Issue Record 是失败预演的自然家园。在 PRD 确认前运行它：

- 如果项目按现状发布，最可能失败的是什么？哪个 open 问题会导致它？
- 最可能的 3-5 个失败原因是什么？它们每个都有 owner 和缓解措施（或已接受的风险）吗？

## 对抗性审查（Adversarial Review）

- BLK 真的阻断吗，还是因为让人不舒服而被标为 BLK？
- 风险是否因为跟踪起来不方便而被降级？
- 问题是否在没有证据的情况下被关闭，只为清空清单？

## 确认偏误防御（Confirmation Bias Defense · 问题清单特化）

AI 不得在没有决策的情况下把"待确认"信号静默吸收进产物：

1. 我在继续之前问"要不要登记为 ISS-NNN"了吗，还是默默继续？
2. 我是否为了回避升级而分配了美化故事的类别（用 INF 代替 DEC，用 RSK 代替 BLK）？
3. 我是替用户接受了风险，还是具名决策 owner 接受它？

## 知识边界（Knowledge Boundary · 问题清单特化）

1. 我是否区分了"上游产物显式标记了这一点"（FACT）与"我注意到一个风险"（AI_INFERENCE）？
2. 未知事实是否标为 UNKNOWN，而不是写成假设？
3. 冲突是否保留双方，而不是合并成一方？

---

## 低密度降级模式（Low-Density Degradation Mode）

当不存在问题信号（任何地方都没有待确认 / UNKNOWN / CONFLICT / 风险）时，上述透镜没有可工作的对象。切换到降级模式：

```text
no-issue-signal input → skip lens ideation
                       → do not invent issues
                       → return a routing receipt:
                          "issue-record has no new entries; list may stay as-is"
                       → no status change, no Generate / Audit
```

降级触发条件（任一即可）：

- 所有上游产物都已确认，没有待处理的标记
- 任何地方都没有矛盾、没有等待中的决策、没有风险信号
- 用户只确认现有问题，没有提出新问题

此模式不是失败状态。发明的问题会污染清单、浪费决策 owner 的注意力。一份诚实的空清单胜过一份虚构的满清单。

## Clarify 是独立闭环

每次 Clarify Session 一行一 session（≤5），`accepted_answer` 在 `ready_for_human_review` 前必填；答案回写目标产物章节（`reflow_target`）。登记问题本身必须先经用户确认——这是 issue-record 的独特契约，违反即反模式。
