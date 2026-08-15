# 产品 UX 输出契约（Product UX Output Contract）

单一产物：**一份 `product-ux.md`，内含两个章节**。两个章节都由 `product-ux` 的子 skill 产出，直接写入同一份 `product-ux.md`——每个子 skill 是章节生产者，不是独立的产物。

## 一个产物，两个章节（One Artifact, Two Sections）

| 章节 | 内容 | 产出方 | 在 product-ux.md 中的落位 |
|---|---|---|---|
| §页面设计 | 页面/步骤骨架：入口、前置条件、主要内容、操作、下一状态（非视觉设计） | `page-design` 子 skill | §页面设计（页面与步骤描述 + HTML 原型入口） |
| §交互规则 | IX-XXX 交互规则：触发条件 → 系统响应（正常/错误/空/加载/边界） | `interaction-rules` 子 skill | §交互规则 |

功能清单（feature-list）与功能流程（functional-flow）不在此产物内 —— 归 `function-description`。

## 各章节契约

### §页面设计（由 `page-design` 子 skill 产出）
- 页面/步骤骨架行：入口触发、前置条件、内容区、可用操作、下一状态。
- 不是视觉设计；无像素位置。

### §交互规则（由 `interaction-rules` 子 skill 产出）
- `IX-XXX` 规则：触发 → 系统响应，覆盖正常 + 错误 + 空 + 加载 + 边界状态。
- 属于 product-ux §交互规则（UX 层）。

## 产出顺序与所有权

- 顺序：委托 `page-design` 产 §页面设计（Phase A）→ 委托 `interaction-rules` 产 §交互规则（Phase B）。
- 两个子 skill 只写同一份 `product-ux.md` 的对应章节，各自不产独立产物。
- 本产物不得定义 `BR-XXX`、`VL-XXX` 或 `AC-XXX`，也不得定义功能清单（feature-list）或功能流程（functional-flow）——那些属于 `function-description`。

## 必需章节（Required Sections，校验器检查）

必需章节：输入充分度评估、范围基线、页面/步骤/状态描述（§页面设计）、交互规则（IX-XXX，§交互规则）、知识寄存器、问题、来源、下游交接、审计合规与变更摘要。
