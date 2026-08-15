# Source Handling · page-design

本子 Skill 消费的是**已确认的上游产物**而非原始材料。因此"来源"指：上游 `functional-flow`（function-description）功能流程（§2.1 主流程 / §2.2 分支流程 / §2.3 异常流程）、`feature-list`（function-description）功能清单、`user-journey-and-stories` 故事，以及更早的 `SRC-*` 原始来源。

## Upstream Register

进入 Generate 前登记上游引用：

```text
page_id            # PG-XXX，本子 Skill 生成的页面行 ID
flow_step          # 来自 functional-flow（function-description）功能流程的步骤（页面挂在哪个步骤上）
feature_id         # FEA-XXX，来自 function-description 的 feature-list
story_id           # ST-XXX，页面追溯的故事
upstream_version   # functional-flow / 上游产物的 confirmed 版本
source_ids         # 透传上游故事引用的原始 SRC-*
```

每个页面行必须可回溯到 `flow_step` + `feature_id`。透传 `SRC-*`，不新建重复的来源登记。

## Page-Claim Extraction Rules

1. 先逐字摘取流程中每步对页面/内容/去向的陈述，再填七列。
2. 页面命名与流程步骤名一致；七列内容不使用流程之外的术语。
3. 为补全页面而增加的内容/操作：分离"流程里有"（FACT）与"我推测页面该有"（AI_INFERENCE）。
4. 排除的流程步骤要写理由（重复 / 出范围 / 已被更新），不静默丢弃。
5. 上游未提的页面状态（空态、失败态、权限态）**不视为确认不存在**——标 `UNKNOWN` 交人工。

## Authority And Conflicts

当上游流程与页面表达冲突时：

- 保留双方：保留流程步骤原文与页面的选择，都标 ID。
- 解释影响：不同取舍会怎样影响交互规则与功能描述。
- 标 `CONFLICT-XXX` 并停止：若该冲突改变 P0 页面清单或主路径，交给产品负责人裁决。
- **绝不静默选择更方便的方案。**

上游产物的版本关系：`functional-flow` 功能流程为 `confirmed` 才有权作为页面输入；`superseded` 版本的流程不采用，除非确认的变更记录明确沿用。

## Research Boundary

- 可自行调研：平台通用页面模式（列表页结构、表单页字段惯例、空态引导）——这些是可发现的事实，标记来源。
- 不可自行确认：页面的取舍、是否包含某操作、某前置条件是否必须——交人工。
- 外部调研结论一律先标 `AI_INFERENCE`，需人工确认后才能当决策依据。

## Mixed Media

- 从旧原型/截图反推页面结构时，先转写可见的信息区块与操作，标注转写不确定性。
- 从会议纪要中的页面描述，区分"确认过的页面"与"讨论中的页面"。
- 从多版本设计稿提取页面时，保留版本与页次，注明后版是否覆盖前版。

## Traceability Table（父产物 §9）

每个页面的落位填入父产物 `## 9. 来源追溯`：来源 ID、材料/位置、关键内容、本文落位或排除理由。七列中的内容与来源的对应关系要在 §9 中可查。
