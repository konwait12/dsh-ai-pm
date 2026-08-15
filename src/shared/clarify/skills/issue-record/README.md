# issue-record（跨阶段共享）

全局问题清单 · 任何阶段遇到"待确认" / UNKNOWN / CONFLICT 时 AI 主动询问是否登记。

## 用途

- 集中维护 BLK / RSK / DEC / INF / CLS / OUT 六类问题
- 跨阶段共享：一个需求从 background-goal 到 PRD 汇总，所有"未决"都在这里
- 给业务方一个权威的"还有什么没解决"清单
- 跟踪 owner、状态、目标关闭日期、缓解措施
- PRD 确认前必经的"问题清零"环节

## 不该用

- 想写需求 / 用户故事 / 设计（用对应 Skill）
- 一次性、不会重复出现的小问题（用单条 `QuestionRecord` 即可）
- 业务方还没提出，自己推测的"风险"（不要 AI 主动写问题清单）

## 强制行为

**AI 必须主动询问**：当用户输入或源材料出现以下任一信号时：
- `待确认` / `我不确定` / `可能` / `也许` / `大概` / `之后再说` / `再看看`
- `?` / `TODO` / `TBD` / `[空]`
- 两个来源对同一事实给出不同表述
- 业务方口头表达但未签字
- 推导结果与某条 FACT 冲突
- 阶段产物生成后仍有 `UNKNOWN` 知识状态遗留

→ AI 必须在给出方案之前询问：

> 我注意到 [引用具体源] 中存在 [BLK/RSK/DEC/INF/CLS/OUT] 信号：[具体描述]。
> 要不要登记到 Issue Record（ISS-NNN）由 [推荐 owner] 处理？
> 1. 登记为 [类别]，[状态]
> 2. 现在口头回答并填入 [目标产物 §X]
> 3. 暂不处理，标记为 [accepted] 由 [owner] 接受

## 章节速查

| § | 标题 | 何时填写 |
|---|---|---|
| 1 | 项目元数据 | 起草时 |
| 2 | 总览（按类别与状态计数） | Generate 后 |
| 3 | Blocker（BLK） | 必有 |
| 4 | Risk（RSK） | 必有 |
| 5 | Decision-in-waiting（DEC） | 必有 |
| 6 | Information gap（INF） | 必有 |
| 7 | Clarification（CLS） | 必有 |
| 8 | Out-of-band（OUT） | 必有 |
| 9 | Closed Issues | 必有 |
| 10 | 来源追溯 | 必有 |
| 11 | 待确认问题 | 必有 |
| 12 | Constitution Compliance | 必有 |

## 与上下游的衔接

- **上游汇聚点**：所有产物（background-goal、scope、journey、UX、function-description、PRD）的"待确认"都应被提升为 ISS-NNN
- **下游关闸**：PRD 确认前，Issue Record 必须有 confirmed 版本
- **同级互补**：scope 定"做什么"，issue-record 列"卡点/风险/待决"
- **与 `clarify/issue-templates/issue-record.md` 共存**：单条问题字段模板 vs. 全局清单

## 审计硬约束

- 所有 open 状态必须有 owner
- BLK / DEC 必须有 target_close
- 30 天以上的 open 状态必须有 escalation 记录
- 与上游产物的"待确认"必须一一对应或有 documented 关闭理由
- 登记问题必须先经用户确认（AI 主动询问）

## 验证

```bash
python3 scripts/validate_artifact.py <产物路径> --json
```

其中 `<产物路径>` 是生成的 `issue-record.md`（如 `requirements/REQ-XXX/99-review/support/issue-record.md`）；空模板见 Skill 目录下的 `assets/issue-record-template.md`。
