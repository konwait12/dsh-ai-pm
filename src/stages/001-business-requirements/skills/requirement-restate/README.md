# requirement-restate

需求重举 · 用 stakeholder 自己的话重述需求、形成可逐条确认的清单。

## 性质

这是**分析过程**，**不是 PRD 产物**。

它的输出是 stakeholder 看到重述后说"是的，就是这个"或"不是，你漏了 X"的检查位。**重举通过后**，结论进入 `issue-record.md`：
- CONFLICT → `ISS-XXX`（CLS 类别）
- UNKNOWN → `Q-XXX`（INF 类别）
- 重举通过的需求行才进入下游 `project-background-goal`

## 用途

- 原始需求被多团队 / 多语言 / 多源转述
- 多源对同一事实给出不同表述
- 高误读代价（合规、法律、昂贵构建）
- 治理需要正式的"我们真的同意这件事了吗"检查位
- 新 stakeholder 加入，需要重新锚定

## 不该用

- 需求已经清楚（"修这一个 typo"）
- 已经通过 restate 闸门，stakeholder 已签
- 需求本身就是设计（"给我做一个含 4 个图表的 dashboard"——这是方案，不是需求）

## 重举原则

| 原则 | 原因 |
|---|---|
| **用 stakeholder 自己的话** | 避免翻译损耗 |
| **一行一个需求** | 强制原子性 |
| **每个行都有源** | 防止凭空捏造；可回流 |
| **保留原始措辞** | "说了什么"和"我们怎么理解"的差异就是价值 |
| **标记冲突但不解决** | restate 阶段只 flag，resolution 走 issue-record / scope |
| **零方案** | 方案掺入的瞬间 restate 闸门就失效了 |

## 章节速查

| § | 标题 | 何时填写 |
|---|---|---|
| 1 | 项目元数据 | 起草时 |
| 2 | 来源清单（SRC-IDs） | 起草时 |
| 3 | 重述需求清单（RR-XXX） | Generate 后 |
| 4 | 冲突清单（CONFLICT → ISS-XXX） | Intake 时 |
| 5 | 未知清单（UNKNOWN → Q-XXX） | Intake 时 |
| 6 | stakeholder 自查反馈位 | Human Gate |
| 7 | 来源追溯 | Generate 后 |
| 8 | 待确认问题 | Audit 前 |
| 9 | Constitution Compliance | Audit 前 |

## 上下游衔接

- **上游**：源材料（会议记录 / 邮件 / BRD / 工单 / 已有文档）
- **下游（成功路径）**：重举通过 → 进 `issue-record.md`（CONFLICT / UNKNOWN）+ `project-background-goal`（已确认需求）
- **下游（失败路径）**：stakeholder 否认重举 → 修订重述 → 重新走流程

## 验证

```bash
python3 scripts/validate_artifact.py <产物路径> --json
```

其中 `<产物路径>` 是生成的 `requirement-restate.md`（如 `requirements/REQ-XXX/99-review/support/requirement-restate.md`）；空模板见 Skill 目录下的 `assets/requirement-restate-template.md`。
