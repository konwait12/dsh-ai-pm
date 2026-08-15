# 输出契约 · 问题清单（Issue Record · 跨阶段共享）

## 产物状态（Artifact States）

| 状态 | 含义 | 下游使用 |
|---|---|---|
| `draft` | 初始收集；Audit 未完成 | No |
| `needs_user_input` | 阻断 / 待决；需要先回答 | No |
| `conditional_review` | 已知晓非阻断未知，可审 | No |
| `ready_for_human_review` | 自审通过；待授权审 | No |
| `confirmed` | 授权人显式接受 closed-out 列表 | Yes |
| `superseded` | 被新 confirmed 版本取代 | No |

## 版本规则（Version Rules）

- 起 `v0.1`，人工要求修订时递增 minor。
- 首次 confirmed 为 `v1.0`。
- 新问题随时可加；状态变更走 Audit。

## 知识状态标签（Knowledge-State Labels）

`FACT` / `DECISION` / `ASSUMPTION` / `AI_INFERENCE` / `UNKNOWN` / `CONFLICT`

## 必需章节（Required Sections）

| § | 标题 | Required |
|---|---|---|
| 1 | 项目元数据 | Yes |
| 2 | 总览（按类别与状态计数） | Yes |
| 3 | Blocker（BLK） | Yes |
| 4 | Risk（RSK） | Yes |
| 5 | Decision-in-waiting（DEC） | Yes |
| 6 | Information gap（INF） | Yes |
| 7 | Clarification（CLS） | Yes |
| 8 | Out-of-band（OUT） | Yes |
| 9 | Closed Issues（accepted / resolved / escalated） | Yes |
| 10 | 来源追溯 | Yes |
| 11 | 待确认问题 | Yes |
| 12 | Constitution Compliance | Yes |

空章节用 `待确认` 占位，不删除标题。

## 问题结构（Issue Schema）

| 字段 | 必填 | 说明 |
|---|---|---|
| `ISS-NNN` | Yes | 单调递增，限定本 artifact |
| `category` | Yes | `BLK` / `RSK` / `DEC` / `INF` / `CLS` / `OUT` |
| `state` | Yes | `open` / `in_progress` / `blocked` / `accepted` / `resolved` / `escalated` |
| `title` | Yes | 一句话、具体 |
| `description` | Yes | 上下文 / 影响 / "完成" 的定义 |
| `owner` | Yes | 个人或角色 |
| `knowledge_state` | Yes | 6 态之一 |
| `source` | Yes | SRC-ID |
| `affected_artifact` | Optional | 来自哪个上游产物 |
| `raised_at` | Yes | 提单日期 |
| `target_close` | Required for BLK/DEC | 目标解决日期 |
| `mitigation` | Required for RSK | 缓解措施 |
| `resolution` | Required for resolved | 解决内容与引用变更 |
| `escalated_to` | Required for escalated | 新 Owner 或机构 |
| `notes` | Optional | 边缘情况 / 依赖 |

## 审计钩子（Audit Hooks）

- 上游产物每个"待确认"必须有 ISS-NNN 引用或 `closed_at_intake` 理由
- 每个 open 都有 Owner
- BLK / DEC 都有 target_close
- 30 天以上 open 都有 escalation 记录

## 人类职责（Human Responsibilities）

- 决策 Owner：接受 `accepted` 状态，签发 closed-out 列表
- 问题 Owner：维护状态、Owner、target_close
- 最终 Reviewer：授权 issue list 用于 PRD 确认

## 下游移交（Downstream Handoff）

```text
confirmed_version
open_count
in_progress_count
blocked_count
accepted_count
resolved_count
escalated_count
open_blk_ids
open_dec_ids
critical_top5
source_ids
```

## 澄清会话契约（Clarifications Session Contract）

`## Clarifications` 一行一 session，≤5 sessions，`accepted_answer` 在 `ready_for_human_review` 前必填。
