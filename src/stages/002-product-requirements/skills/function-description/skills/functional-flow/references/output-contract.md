# Output Contract · functional-flow

本子 Skill 产出父级 `function-description.md` 的 **§功能流程** 章节（主流程 / 分支流程 / 异常流程）。不产出独立产物；所有内容直接写入父产物对应章节。

## ID 契约

| ID 类型 | 格式 | 规则 |
|---|---|---|
| 功能 | `FEA-XXX` | 每个流程必须归属父级功能清单已登记的 FEA；不得引入清单之外的孤儿功能 |
| 故事 | `ST-XXX` | 流程的每个步骤必须可回溯到已确认的用户故事；无法回溯的步骤标 `AI_INFERENCE` |
| 步骤 | `FL-XXX`（图内节点） | 图内业务步骤/状态节点可编号，命名与功能清单、故事原文一致，不自造术语 |
| 冲突 | `CONFLICT-XXX` | 上游范围与流程表达矛盾时显式保留，交人工裁决 |

## Artifact States

| Status | Meaning | Downstream use |
|---|---|---|
| `draft` | 初始候选；Audit 未完成 | No |
| `needs_user_input` | 某起点/步骤/分支/异常路径的事实或决定阻断确认 | No |
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
| `FACT` | 上游故事/已确认功能清单中的显式步骤或分支 |
| `DECISION` | 授权人工关于起点/分支/出口/异常回退的明确决定 |
| `ASSUMPTION` | 为画流程接受但未确认的临时条件 |
| `AI_INFERENCE` | AI 为使流程完整而补的结构推断（有证据但非业务事实） |
| `UNKNOWN` | 缺失信息（如某异常路径的行为尚未确认） |
| `CONFLICT` | 上游来源与流程表达不一致，需人工裁决 |

## Required Section Content

父产物 `## 功能流程` 下，按功能组织：

- **主流程**：每个 P0 FEA ≥1 张 Mermaid 图，覆盖 起点 → 业务步骤序列 → 决策 → 出口/终止。
- **分支流程**：以文本/表列出每个决策点的分支条件，条件须标注、互斥、可穷举。
- **异常流程**：异常/失败分支、回退目标显式列出（error / 失败 / 超时 / 取消 / 恢复），与主流程自洽。

流程结构契约（每个流程至少包含）：

```text
start_condition      # 流程在什么业务起点/触发条件下启动
steps                # 主流程的原子业务步骤序列（FL-XXX）
branch_points        # 决策点：判定条件、互斥、穷举
exception_paths      # 异常/失败路径与回退目标
exit_states          # 出口/终止状态与后续去向
source_ids           # FEA-XXX / ST-XXX / SRC-*
```

若某 FEA 无确认流程内容，写 `待确认` 并关联问题/未知 ID；**不删除标题、不跳过 FEA**。

## Downstream Handoff

向 business-rules / state-machine / exception-handling 等下游子技能传递：

```text
confirmed_version
per_fea_flow_summary      # 每 FEA：主流程、分支流程、异常流程
branch_conditions         # 每个决策点的判定条件
exception_paths           # 异常路径与回退目标
handoff_points            # 跨系统交接与失败回退
ai_inferred_steps         # 所有 AI_INFERENCE 步骤清单
open_nonblocking_unknowns
source_ids                # ST-XXX / FEA-XXX / SRC-*
```

不要在本 Handoff 中创建业务规则、状态机明细或异常处理明细表。

## Clarifications Session Contract

沿用父产物 `## Clarifications` 表，一行一个 Session（`CL-NNN`），字段与父级一致。`reflow_target` 必须指向本子 Skill 影响的章节（`§功能流程`）。`audit_recheck` 为最后填写字段；若 `fail`，状态回退 `needs_user_input` 并开新一轮 Session。
