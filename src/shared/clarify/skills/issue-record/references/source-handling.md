# 来源处理 · 问题清单（Issue Record · 跨阶段共享）

## 来源登记（Source Register）

issue-record 的来源是阶段产物加上携带问题信号的原始材料。为每个来源分配一个稳定 ID 并记录：

```text
source_id
title_or_description
format                  (background-goal / 范围基线 / journey / UX / function-description / prd / 会议 / 邮件 / 口头)
author_or_speaker
provided_by
created_at
retrieved_at
authority_scope
location_or_link        (产物 § / 章节 / 行号 / 时间戳)
notes
```

使用 `SRC-001`、`SRC-002` 等。每个问题还记录其 `affected_artifact`（它来自哪个上游产物）。

## 提取规则（Extraction Rules）

1. 在问题信号出现时逐条提取：待确认 / UNKNOWN / CONFLICT / 待决决策 / 风险 / 范围外。
2. 对每个信号，保留确切的触发源（引发它的句子或标记）和产物位置——没有可追溯来源的问题无法被核实或关闭。
3. 区分"产物显式标记了这一点"（FACT）与"我注意到一个风险"（AI_INFERENCE）——AI 不得把自己观察到的东西变成业务事实。
4. 记录被排除的信号并附简短理由（重复、已跟踪、超出清单范围）。
5. 绝不把未记录的待确认标记当作已解决——上游映射是一道审计闸门。

## 跨产物查重（Cross-Artifact Dedup）

同一个问题可能在多个阶段产物中出现（例如在 requirement-restate 和 background-goal 中都标记了同一冲突）。规则：

- 登记一个规范化的 ISS-NNN；
- 把其他出现处交叉链接到它；
- 记录每次出现的位置，使问题从每个产物都可找到；
- 不要为每个产物创建重复行。

## 权威性与冲突（Authority And Conflicts）

决策权威是分层的：目标决策 owner / 业务发起人拥有 `accepted` 风险和 closed-out 清单；问题 owner 拥有自己问题的状态和 target_close；验证人确认 `resolved`。

当两个产物对问题是否真实存在意见冲突时（例如一个标为 BLK，另一个展示了变通方案）：

- 保留两条声明及其位置；
- 说明每种解读的影响；
- 把分歧路由给问题 owner 或决策 owner；
- 绝不静默降级问题来清空清单。

## 调研边界（Research Boundary）

仅当外部事实可能解决或缓解某个问题（法规文本、平台能力、厂商合同）且可发现时，才做调研。记录来源、日期、事实/推断状态、置信度、适用性和决策影响。

调研不能接受风险、设置目标关闭或分配 owner——这些是问题 / 决策 owner 的人类决策。

## 混合媒介（Mixed Media）

- 阶段产物：引用待确认 / UNKNOWN / CONFLICT 标记的确切章节（§）和标题。
- 会议：区分已陈述的决策与未解决的讨论；保留时间戳。
- 聊天/工单：保留发送者、线程上下文，以及后一条消息是否取代前一条。
- 口头输入：注明说话者，以及尚未签字。
