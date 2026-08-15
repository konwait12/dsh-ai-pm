# 来源处理 · 可行性分析

## 来源登记（Source Register）

为每个来源分配一个稳定 ID 并记录：

```text
source_id
title_or_description
format (vendor quote / proposal / contract / past-project data / public pricing / compliance doc / internal estimate)
author_or_publisher
provided_by
created_at
retrieved_at
authority_scope (e.g., "official vendor quote — valid 30 days")
location_or_link
notes
```

使用 `SRC-001`、`SRC-002` 等。成本和合规来源是时效敏感的——记录检索日期。

## 提取规则（Extraction Rules）

1. 在规范化之前先提取来源陈述——先引用数字，再解释。
2. 重大结论保留提供方和位置（谁报的价、哪份提案）。
3. 区分显式陈述（书面报价、合规规则）与隐含含义（从类似过往项目得出的估算）。
4. 当相关但超出范围或重复时，用简短理由记录被排除的材料。
5. 绝不把"没有报价"当作"免费"——那是 `UNKNOWN`，不是 `FACT`。
6. 估算不是事实：AI 起草的预算在决策 owner 确认前是 `AI_INFERENCE` 或 `ASSUMPTION`。

## 权威性与冲突（Authority And Conflicts）

使用以下标准评估权威性：

1. 本项目内显式的人工确认；
2. 对特定成本或约束的决策权；
3. 来源的直接程度（书面报价 > 口头估算 > AI 估算）；
4. 时效性——3 个月前的报价可能不反映当前定价；
5. 独立来源的佐证（两家厂商报出相近价格）。

当陈述冲突时（例如厂商报价不同，或财务与产品对预算意见不一）：

- 保留两条陈述和来源 ID；
- 说明每种解读的影响；
- 识别可能的决策 owner；
- 标记为 `CONFLICT`，若它改变重大结论则停止；
- 绝不默默选择更顺手的数字。

## 调研边界（Research Boundary）

评估可以调研公开可得的客观事实（可比产品、行业成本基准、已发布定价），但无法确认：

- 内部预算授权或采购审批；
- 合规或数据安全风险的可接受性；
- 内部资源可用性。

把这些交给负责任的人。依赖未确认数字的推荐保持在 `needs_user_input`。

## 混合媒介（Mixed Media）

- 厂商报价/提案：记录报价日期、有效期窗口，以及包含 vs 排除的内容（隐藏成本）。
- 过往项目数据：记录项目、其与当前项目的相似度，以及外推的可信度。
- 合规文档：记录法规版本及其约束的具体要求。
- 内部估算：区分估算者（AI / PM / 工程）和证据基础。
