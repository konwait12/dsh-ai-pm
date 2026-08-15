# Output Contract · exception-handling

## Position In Parent

Produces the `#### 异常与失败处理` subsection of each `FUN-XXX` block in the parent `function-description.md` §2 分功能详述.
Output format must match the table in `src/templates/stage-2-product/function-description.md`（在模板列基础上增加 ID 与来源列以保证追溯）。

## EX-XXX Row Contract

| 列 | 要求 |
|---|---|
| ID | `EX-XXX`，全局唯一、编号连续（EX-001…），挂在所属 `FUN-XXX` 下，不与 BR-/VL-/ST-/AC-/IX- 混淆 |
| 场景 | 该失败的短名（网络超时 / 余额不足 / 并发冲突…），与该函数真实职责一致 |
| 触发条件 | 可判真伪，能写进自动化测试分支；一行一个事实，不与系统行为混写 |
| 系统行为 | 失败发生后系统做什么（拦截 / 降级 / 回滚 / 阻断）；禁止空白 |
| 恢复方式 | 重试 / 手动 / 自动 / 终止 之一，并标注边界（次数、间隔、幂等、是否需人工介入） |
| 用户提示 | 面向用户的中文自然语言，说明「哪里失败 + 用户能怎么办」，不是错误码或「请联系管理员」 |
| 来源 | SRC-* 来源 ID + 知识状态标签（FACT / DECISION / AI_INFERENCE / UNKNOWN） |

## ID And Prefix Rules

- 保持 `EX-` 前缀；不与 `BR-` / `VL-` / `ST-` / `AC-` / `IX-` 混淆。
- 每条 `EX-XXX` 必须挂在某个 `FUN-XXX` 下，无游离孤儿异常。
- 与已确认的 `BR` 异常分支 / `ST` 异常路径建立关联（关联 BR / 关联状态迁移），下游 `AC` 才能覆盖验证。
- 无跳号、无重复；一条 EX 只描述一种失败，多个失败拆成多行。

## Knowledge-State Labels

| Label | Meaning (exception domain) |
|---|---|
| `FACT` | 来源文档明确描述的失败场景 |
| `DECISION` | 业务方对恢复策略 / 提示文案的明确决定 |
| `ASSUMPTION` | 暂定接受、未确认的失败假设 |
| `AI_INFERENCE` | AI 依据上游推断出的失败分支，未经业务确认 |
| `UNKNOWN` | 缺失的恢复策略 / 提示文案 |
| `CONFLICT` | 两个来源对失败处理说法矛盾，需裁决 |

## Version / Status / Placeholder Rules

- 状态机：`draft → needs_user_input / conditional_review → ready_for_human_review → confirmed`；`confirmed` 只能由 `pipeline.py review --decision approve` 产生，AI 不得设置。
- 起始候选 `v0.1`；人工要求修订则 `v0.2`、`v0.3`；首个确认基线 `v1.0`。
- 无确认内容写 `待确认` 并链接到问题/未知 ID，不删除列。
- 可恢复与不可恢复失败必须显式区分，不得共用一条提示。

## Downstream Handoff

按函数输出紧凑 handoff：

```text
confirmed_function_ids
exception_id_list
unrecoverable_exceptions      # 需人工处理 / 终止的失败
recovery_policy_summary       # 重试边界、补偿、幂等
open_unknowns                 # 未确认的恢复策略 / 文案
source_ids
```

## Human Responsibilities

- 业务/功能 owner：确认失败场景的真实性、恢复策略与提示文案。
- 产品经理：检查覆盖度、可判定性、边界保持与下游可用性。
- 最终评审人：授权异常处理基线进入下游。一人可兼任多角色，但决策权必须明确。
