# Source Handling · business-rules

业务规则产出的来源处理：从上游 `product-ux`（FEA-XXX + UX 步骤）与 `user-journey-and-stories`（ST-XXX）中提取规则时，如何登记、引用、裁决来源。

## Source Register

为每条规则登记来源，并在父文档「来源追溯」中维护：

```text
source_id
source_kind          # ST-XXX / FEA-XXX / 会议纪要 / 邮件 / 决策记录
title_or_description
author_or_speaker
provided_by
created_at
retrieved_at
authority_scope      # 该来源对哪些业务事实/规则有决定权
location_or_link
notes
```

使用 `SRC-001`, `SRC-002`, … 作为材料来源 ID；规则行内的 `来源` 列填其支撑的 `ST-XXX` / `FEA-XXX`。对会议记录，区分原始转录与 AI 生成的纪要。

## Extraction Rules

1. 在规范化之前先提取源声明（原文优先），再解释含义。
2. 关键规则的声明保留说话人/作者与位置。
3. 区分明确声明与隐含含义——隐含约束必须标注 `AI_INFERENCE` 再登记待确认。
4. 承载规则但超出范围或重复的材料，记录排除原因。
5. 缺失的规则（来源没提）不等于"规则不存在"——应标 `UNKNOWN` 而不是跳过。

## Authority And Conflicts

不定义普适的来源优先级。用以下标准评估权威性：

1. 本项目是否有明确的人工确认；
2. 对该特定业务规则是否有决策权（政策 owner）；
3. 来源的直接程度；
4. 时效性与后续声明是否显式覆盖早期声明；
5. 独立来源的相互佐证。

当规则冲突时：

- 同时保留两条规则与其来源 ID；
- 说明每种解读的影响；
- 识别可能的事实/政策 owner；
- 若改变关键规则结论，标记 `CONFLICT` 并停止；
- 绝不静默选择更顺手的版本。

## Research Boundary

只有当外部事实能实质性影响规则口径且可获取时才做调研（公开定价政策、行业惯例、合规要求）。记录来源、日期、事实/推断状态、置信度、适用性与决策影响。

调研不能确认内部业务策略、项目范围、业务归属或风险可接受度——这些必须提交给负责人。

## Mixed Media

- 对故事/UX 文档：保留段落/章节位置。
- 对图片：转录可见的规则相关文字并标注不确定性。
- 对会议记录：区分发言者声明、决定、建议与未决讨论。
- 对邮件线程：保留发件人、收件上下文、日期，以及后一封是否覆盖前一封。

## Mapping To BR Rows

- 规则行的 `来源` 列填 `ST-XXX` / `FEA-XXX`（上游确认的 artifact），不是材料 SRC-ID。
- 材料 SRC-ID 走父文档「来源追溯」表，保证材料 → 故事/UX → 规则三级链路可查。
- 规则内容被上游改动后，同步检查所有引用该来源的 BR-XXX 是否需要回流。
