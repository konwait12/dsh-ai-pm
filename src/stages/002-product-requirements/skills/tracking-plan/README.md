# tracking-plan（埋点需求分析）

002 阶段 · function-description 的子 Skill · 列出每个 P0 功能的事件、属性、触发时机、上报时机、平台与关联指标。

## 用途

- 数据团队和工程团队的"事件合约"
- 每个 P0 功能至少 1 个 `must_track` 事件
- 每个事件都映射到 G-X 目标与具体指标（north_star / funnel_step / counter / latency / conversion / retention）
- PII 事件明确标记与保留期

## 不该用

- 想写 SQL 或数据仓库表设计（用数据团队自己的 Skill）
- 想做 A/B 测试方法学（不是本 Skill 范围）
- 设定具体数值目标（那是上游 G-X）
- 在 business-rules / validation-rules / state-machine / exception-handling 还没 confirmed 之前用

## 调用顺序

```
business-rules (BR)
→ validation-rules (VL)
→ state-machine
→ exception-handling
→ tracking-plan  ← 当前
→ acceptance-criteria
```

## 章节速查

| § | 标题 | 何时填写 |
|---|---|---|
| 1 | 元数据 | 起草时 |
| 2 | 事件清单（EV-XXX） | Generate 后 |
| 3 | 事件属性字典 | Generate 后 |
| 4 | 覆盖矩阵（每 FUN-XXX ≥1 must_track） | Audit 前 |
| 5 | 指标映射（event → G-X → metric） | Generate 后 |
| 6 | PII 与数据保留 | Generate 后 |
| 7 | 待确认问题 | Audit 前 |
| 8 | Constitution Compliance | Audit 前 |

## 关键约束

- `event_name` 强制 snake_case verb_noun（如 `checkout_submit_click`）
- `priority` 二选一：`must_track` / `nice_to_track`
- `pii_flag` 四档：`false` / `quasi` / `true` / `sensitive`
- 每个 P0 FUN-XXX 至少 1 个 `must_track`（覆盖矩阵硬约束）

## 验证

```bash
python3 scripts/validate_artifact.py <产物路径> --json
```

其中 `<产物路径>` 是生成的 `tracking-plan.md`（如 `requirements/REQ-XXX/99-review/support/tracking-plan.md`）；空模板见 Skill 目录下的 `templates/tracking-plan-output.md`。
