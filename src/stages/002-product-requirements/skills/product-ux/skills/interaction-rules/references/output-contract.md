# Output Contract · interaction-rules

本子 Skill 产出父级 `product-ux.md` 的 **§3 交互规则 IX-XXX**（隶属 `## 3. 交互规则`）。不产出独立产物；所有内容直接写入父产物对应章节。

## ID 契约

| ID 类型 | 格式 | 规则 |
|---|---|---|
| 交互规则 | `IX-XXX` | 全局唯一，按 `IX-001`、`IX-002` 递增；一条规则一个交互行为；无跳号、无重复 |
| 适用页面 | `PG-XXX` | 每条规则必须引用 `page-design` §2 页面设计存在的页面行；无孤儿规则 |
| 功能 | `FEA-XXX` | 每条规则可回溯到 function-description 的 feature-list 功能清单的 FEA；不引入清单之外的功能 |
| 冲突 | `CONFLICT-XXX` | 规则与页面/流程矛盾时显式保留，交人工裁决 |

规则类别可含：入口与身份、核心操作、反馈与异常、导航、a11y。类别不产生新的 ID 前缀；统一用 `IX-XXX`。

## Artifact States

| Status | Meaning | Downstream use |
|---|---|---|
| `draft` | 初始候选；Audit 未完成 | No |
| `needs_user_input` | 某条规则的触发/响应/反馈的事实或决定阻断确认 | No |
| `conditional_review` | 结构可评审，剩余未知非阻断且有责任人 | No |
| `ready_for_human_review` | 自审通过，等待授权评审 | No |
| `confirmed` | 授权人工明确批准此版本 | Yes |
| `superseded` | 更新的已确认基线替代本版本 | No |

## Version Rules

- 起始候选 `v0.1`；人工要求修订递增小版本 `v0.2`、`v0.3`。
- 首次确认基线用 `v1.0`；已确认基线变更按影响递增 patch/minor。
- 保留人工可见版本之间的简明变更摘要，不保留每次内部自审迭代。

## Knowledge-State Labels

| Label | Definition |
|---|---|
| `FACT` | 页面/流程/已确认范围中显式的交互行为 |
| `DECISION` | 授权人工关于反馈时机、状态处理的明确决定 |
| `ASSUMPTION` | 为写规则而接受但未确认的临时条件 |
| `AI_INFERENCE` | AI 为使交互完整而补的响应推断（有证据但非业务事实） |
| `UNKNOWN` | 缺失信息（如错误提示文案、超时行为尚未确认） |
| `CONFLICT` | 上游来源与规则表达不一致，需人工裁决 |

## Required Section Content

父产物 `## 3. 交互规则` 下：

- 表格六列：ID、规则描述、触发条件、系统响应、适用页面/功能、来源。
- 每条规则满足「触发条件 → 系统响应」结构；系统响应为确定动作或界面状态，无「合理提示」类模糊措辞。
- 写作格式遵循 `references/rule-writing-format.md`（段落式：用户状态 + 动作 → 系统响应，IF/ELSE、异常、边界）。

若某规则内容未确认，写 `待确认` 并关联问题/未知 ID；**不删除行、不跳过已确认页面的关键交互**。

## Downstream Handoff

向 function-description 与 PRD 汇总传递：

```text
confirmed_version
ix_inventory               # 规则清单（IX-XXX → 类别 → 适用页面）
per_rule_contract          # 每条：触发条件 / 系统响应 / 状态覆盖 / 来源
boundary_handoffs          # 已移交的校验/计算/权限提示（VL/BR 线索，不代写）
ai_inferred_rules          # 所有 AI_INFERENCE 规则清单
open_nonblocking_unknowns
source_ids                 # FEA-XXX / PG-XXX / SRC-*
```

不要在本 Handoff 中代写 `BR-*` / `VL-*` / `AC-*` 规则。

## Clarifications Session Contract

沿用父产物 `## Clarifications` 表，一行一个 Session（`CL-NNN`），字段与父级一致。`reflow_target` 必须指向本子 Skill 影响的章节（`§3`）。`audit_recheck` 为最后填写字段；若 `fail`，状态回退 `needs_user_input` 并开新一轮 Session。
