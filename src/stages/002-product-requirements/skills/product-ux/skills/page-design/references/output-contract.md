# Output Contract · page-design

本子 Skill 产出父级 `product-ux.md` 的 **§2 页面设计**（§2.1 页面与步骤描述 + §2.2 HTML 原型）。不产出独立产物；所有内容直接写入父产物对应章节。

## ID 契约

| ID 类型 | 格式 | 规则 |
|---|---|---|
| 页面/步骤 | `PG-XXX` | 每个页面一行；命名与 `functional-flow` 功能流程步骤、上游故事一致；不凭空新增 |
| 功能 | `FEA-XXX` | 每行"所属功能"必须引用 function-description 的 feature-list 已登记的 FEA |
| 操作 | `ACT-XXX`（可选） | 页面内操作可编号，便于交互规则 `IX-*` 引用触发元素 |
| 冲突 | `CONFLICT-XXX` | 页面清单与流程/范围矛盾时显式保留，交人工裁决 |

## Artifact States

| Status | Meaning | Downstream use |
|---|---|---|
| `draft` | 初始候选；Audit 未完成 | No |
| `needs_user_input` | 某页面的入口/前置/内容/操作/下一状态的事实或决定阻断确认 | No |
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
| `FACT` | 上游流程/故事/已确认范围中显式的页面内容或行为 |
| `DECISION` | 授权人工关于页面归属、操作、下一状态的明确决定 |
| `ASSUMPTION` | 为补全页面而接受但未确认的临时条件 |
| `AI_INFERENCE` | AI 为使页面完整而补的结构推断（有证据但非业务事实） |
| `UNKNOWN` | 缺失信息（如空态/权限态的页面去向尚未确认） |
| `CONFLICT` | 上游来源与页面表达不一致，需人工裁决 |

## Required Section Content

父产物 `## 2. 页面设计` 下：

- `### 2.1 页面与步骤描述`：每行七列——页面/步骤、所属功能、入口、前置条件、主要内容、操作、下一状态。所有 `functional-flow` 功能流程步骤都有行；无孤儿页面。
- `### 2.2 HTML 原型`：仅当需要沟通载体时勾选并填原型位置（`99-review/support/prototype/`）。**原型是沟通辅助，不替代 §2.1 文本。**

若某页面内容未确认，写 `待确认` 并关联问题/未知 ID；**不删除行、不跳过流程步骤**。

## Downstream Handoff

向 interaction-rules 与 function-description 传递：

```text
confirmed_version
page_inventory            # 页面清单（PG-XXX 与对应步骤）
per_page_contract         # 每页：入口 / 前置 / 内容 / 操作 / 下一状态
action_to_next_state      # 操作→下一状态映射（供 IX 定义反馈）
precondition_inventory    # 前置条件涉及的权限 / 数据前提（供 BR/VL）
ai_inferred_rows          # 所有 AI_INFERENCE 页面/字段清单
open_nonblocking_unknowns
source_ids                # FEA-XXX / ST-XXX / SRC-*
```

不要在本 Handoff 中创建交互规则或业务规则。

## Clarifications Session Contract

沿用父产物 `## Clarifications` 表，一行一个 Session（`CL-NNN`），字段与父级一致。`reflow_target` 必须指向本子 Skill 影响的章节（`§2.1` / `§2.2`）。`audit_recheck` 为最后填写字段；若 `fail`，状态回退 `needs_user_input` 并开新一轮 Session。
