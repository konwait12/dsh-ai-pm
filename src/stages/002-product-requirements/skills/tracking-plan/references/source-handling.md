# 来源处理 · 埋点与追踪计划（Source Handling · Tracking Plan）

## 来源登记（Source Register）

Tracking-plan 的来源主要是**上游已确认产物**，而不是原始会议纪要。为每个来源分配一个稳定 ID 并记录：

```text
source_id
title_or_description
format                  (function-description / product-ux / business-rules / background-goal / 口头补充)
author_or_speaker
provided_by
created_at
retrieved_at
authority_scope
location_or_link        (artifact § / 章节 / 行号)
notes
```

使用 `SRC-001`、`SRC-002` 等。此外，每个事件必须携带它派生的上游功能引用：`FUN-XXX` / `IX-XXX` / `BR-XXX` 以及目标 `G-X`。

## 提取规则（Extraction Rules）

1. 从已确认的上游功能与规则中提取候选事件——不要发明超出已确认功能所隐含范围的事件。
2. 对每个事件，记录哪个上游引用支撑它（FUN-XXX 支撑动作、IX-XXX 支撑交互、BR-XXX 支撑触发错误/边界事件的规则）。
3. 区分"上游说这个动作会发生"（FACT，已确认）与"我推断这需要追踪"（AI_INFERENCE）。
4. 当被排除的事件看似可追踪但属于范围外或重复时，记录一条简短原因。
5. 绝不把"缺失事件"当作不需要埋点的证据——覆盖缺口是阻断性发现，不是假设。

## 权威性（Authority）与冲突

上游已确认产物（function-description、product-ux、business-rules、background-goal 目标）是"某动作是否存在"的权威来源。指标与平台覆盖由 metric_owner / data_owner 拥有。

当上游产物冲突时（例如 BR-XXX 说某动作被禁止而 FUN-XXX 列出了它）：

- 保留双方引用；
- 说明对事件合约的影响；
- 如果它改变覆盖或 PII 处理，标记 `CONFLICT` 并停下；
- 绝不要静默丢弃冲突——路由到父 function-description Skill。

## 调研边界（Research Boundary）

仅当外部事实能改进合约（平台 SDK 事件约定、行业事件命名、数据保护规则）且可发现时，才做调研。记录来源、日期、事实/推断状态、置信度、适用性与决策影响。

调研不能确认某功能是否需要埋点、业务方想要哪个指标，或本产品可接受的 PII 处理方式——把这些提交给 metric_owner / data_owner。

## 混合媒体 / 上游产物处理（Mixed Media / Upstream Artifact Handling）

- 对于 function-description，注明事件派生的具体 FUN-XXX 与章节。
- 对于 product-ux，注明 IX-XXX 交互规则与流程中的页面/步骤。
- 对于 business-rules，注明 BR-XXX 规则与产生 error 事件的失败条件。
- 对于 background-goal，注明事件必须帮助验证的 G-X 目标。
