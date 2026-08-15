# Source Handling · interaction-rules

本子 Skill 消费的是**已确认的上游产物**而非原始材料。因此"来源"指：上游 `page-design` 页面清单（§2 页面设计）、`functional-flow`（function-description）功能流程（§2.1 主流程 / §2.2 分支流程 / §2.3 异常流程）、`feature-list`（function-description）功能清单，以及更早的 `SRC-*` 原始来源。

## Upstream Register

进入 Generate 前登记上游引用：

```text
rule_id            # IX-XXX，本子 Skill 生成的规则 ID
applicable_page    # PG-XXX，来自 page-design §2 页面设计
feature_id         # FEA-XXX，来自 function-description 的 feature-list
flow_step          # 来自 functional-flow 功能流程的步骤（规则对应的流程节点）
upstream_version   # page-design / functional-flow 的 confirmed 版本
source_ids         # 透传上游引用的原始 SRC-*
```

每条规则必须可回溯到 `applicable_page` + `feature_id`。透传 `SRC-*`，不新建重复的来源登记。

## Rule-Claim Extraction Rules

1. 先从页面清单的"操作"列与流程的分支条件逐字摘取交互事实，再写规则。
2. 规则中的术语（页面名、操作名、状态名）与 §2 页面设计、functional-flow 功能流程一致，不自造。
3. 为补全而增加的响应/状态：分离"上游写了"（FACT）与"我推测该有"（AI_INFERENCE）。
4. 排除的上游交互点要写理由（重复 / 出范围 / 已被更新），不静默丢弃。
5. 上游未提的反馈（错误文案、超时行为）**不视为确认不存在**——标 `UNKNOWN` 交人工。

## Authority And Conflicts

当上游页面/流程与规则表达冲突时：

- 保留双方：保留上游原文与规则的选择，都标 ID。
- 解释影响：不同反馈会怎样影响用户体验与下游验收。
- 标 `CONFLICT-XXX` 并停止：若该冲突改变 P0 交互或反馈行为，交给产品负责人裁决。
- **绝不静默选择更方便的响应。**

上游产物的版本关系：`page-design` / `functional-flow` 为 `confirmed` 才有权作为规则输入；`superseded` 版本的页面/流程不采用，除非确认的变更记录明确沿用。

## Research Boundary

- 可自行调研：平台通用交互惯例、WCAG/ARIA 标准、常见反馈模式（toast、skeleton、snackbar）——这些是可发现的事实，标记来源。
- 不可自行确认：具体错误文案、反馈取舍、是否采用某交互模式——交人工。
- 外部调研结论一律先标 `AI_INFERENCE`，需人工确认后才能当决策依据。

## Mixed Media

- 从旧原型/录屏反推交互行为时，先转写可见的触发与响应，标注转写不确定性。
- 从 PRD 旧版交互描述，区分"确认过的行为"与"讨论中的行为"。
- 从竞品交互对照时，明确标注来源与"仅参考、非本产品决定"。

## Traceability Table（父产物 §9）

每条规则的落位填入父产物 `## 9. 来源追溯`：来源 ID、材料/位置、关键内容、本文落位或排除理由。规则与来源的对应关系要在 §9 中可查。
