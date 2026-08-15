# Audit Checklist · state-machine

State Machine 产出物：状态定义 + 状态转移表（current state, trigger event, target state, guard conditions, side effects），
写入父产物 function-description.md 的「分功能详述」§状态变化 部分。提交前逐项自检。

## Structural Gate

- [ ] 父产物中存在 `## 2. 分功能详述` 章节，State Machine 产出物已写入「状态变化」子章节，而非散落其他章节
- [ ] 至少存在一条 `STATE-\d+` 标识，无「待确认」占位 ID
- [ ] STATE ID 全局唯一、编号连续（STATE-001、STATE-002…），无重号、无跳号、不与 `BR-\d+` / `ST-\d+` 混淆
- [ ] 每个 STATE-XXX 落在对应的 `FUN-XXX` 块内，无游离转移
- [ ] 表格列齐全且与模板一致：状态定义（ID/名称/FUN/描述/进入条件/退出条件）+ 状态转移表（当前状态/触发事件/目标状态/条件/副作用/来源）
- [ ] 元数据含 artifact ID、version、status、owner、reviewer、日期或 `待确认` / `TBD`
- [ ] `python3 scripts/validate_artifact.py <function-description.md> --json` 返回 `"ok": true`

## Source Coverage Gate

- [ ] 每个承载状态语义的来源（BR-XXX / IX-XXX / 故事 / 会议纪要）均已登记
- [ ] 每条转移的守卫条件与副作用有出处，AI 推断的已标 `AI_INFERENCE`
- [ ] 直接声明与 AI 推断可区分（知识状态标签）
- [ ] 冲突保持可见，直到授权人工裁决

## Content Gate（内容门）

- [ ] 对每个存在状态的实体（P0 功能的 `FUN-XXX`）逐一列出全部合法状态，无遗漏、无杜撰状态
- [ ] 状态集合完备性：起始态、中间态、终态（terminal states）都被识别并显式标注
- [ ] 每个状态对每个可能触发事件都有目标状态定义——无「悬空转移」（有触发器但没写目标态）
- [ ] 每条转移都写明守卫条件（conditions）：条件可判真伪，不写「视情况」「适当时候」这类不可判定措辞
- [ ] 每条转移的副作用都被点名：通知、状态联动、相关实体更新、埋点等；无副作用时显式写「无」
- [ ] 非法/被禁止的转移（如终态不允许回退、未授权状态下不允许推进）被显式排除或标注「不允许」
- [ ] 循环、回退、重试、超时导致的隐式状态转移（如「审核超时自动驳回」）已被覆盖，不只写主成功路径
- [ ] 状态转移表与同一功能块的 `BR` 业务规则、`IX` 交互规则在语义上一致，无矛盾

## Boundary Gate（边界门）

- [ ] 只描述状态与状态转移，未为状态设计 UI 展示（属于交互规则 / 前端设计，非本技能职责）
- [ ] 未定义数据库表结构、字段存储方案、索引、迁移（属于字段规则 / 实现层，非本技能职责）
- [ ] 未写实现代码、伪代码、算法实现细节（属于工程实现，非本技能职责）
- [ ] 未把「如何做」的工程决策（消息队列、缓存、幂等实现）混入产品级状态转移定义
- [ ] 未提前讨论验收标准细节（属于 acceptance-criteria）、未复述异常处理文本（属于 exception-handling）；
      异常/回滚等只作为转移条件或副作用点到为止，重复内容已去重

## Semantic Gate（语义门）

- [ ] 每条状态转移的结论来源清晰：来自业务事实（`FACT`）、用户确认（`DECISION`）、AI 推断（`AI_INFERENCE`）或未知待确认（`UNKNOWN`）
- [ ] `AI_INFERENCE` / `UNKNOWN` 的条目已进入「待确认问题」章节，未在状态表中默默当事实
- [ ] 转移表中的每条 STATE-XXX 均可反追溯到上游 `FUN-XXX` 与来源文档，正向可追踪、反向可溯源
- [ ] 状态命名统一（中英文混用已消除、同义不同名状态已合并），读者不会把「待审核 / 审核中」当成两个状态
- [ ] 终态与取消/终止语义一致：不会出现「取消后还能回到进行中」的语义矛盾
- [ ] 与父产物「事实与决定」「来源追溯」章节的引用一致，无孤儿引用、无悬空链接

## Quality Lenses

- 对抗性审查：对每个转移测试了反例——重复事件、回退尝试、超时、并发触发时行为如何？
- 逆向验证：从每个终态反推，其前置状态链是否完整可达？
- 读者视角：一个不了解上下文的人仅凭状态表能复述完整状态流转，无需口头补充。

## Requirement Quality Gate (ISO/IEC/IEEE 29148)

对每条 material 转移按 29148 单条需求特性核查：

| # | 特性 | 通过判据 |
|---|---|---|
| 1 | Appropriate | 可追溯到 BR-XXX / 故事 |
| 2 | Complete | 无悬空目标态、无未定义事件 |
| 3 | Conforming | 模板表头 + ID 规则满足 |
| 4 | Correct | 与来源状态语义一致 |
| 5 | Feasible | 无已知不可实现阻塞 |
| 6 | Necessary | 去掉后生命周期不完整？ |
| 7 | Singular | 单行单转移 |
| 8 | Unambiguous | 状态命名唯一、守卫可判真伪 |
| 9 | Verifiable | 每条转移有可判定守卫与副作用；无"视情况" |

`Verifiable` 失败是阻塞项：要么补齐可判定守卫，要么标 `needs_user_input` 并给出负责人。

## Human Gate

- [ ] 已自跑 `python3 scripts/validate_artifact.py` 且返回 PASS（或输出的 ERROR 已清零、WARNING 已逐一说明）
- [ ] 存在状态（>1 个状态）的实体全部有转移表，无「只有一个状态所以没表」的遗漏未说明
- [ ] 不确定的状态语义（状态能否回退、终态后能否重开等）已列为待确认问题，未自行拍板
- [ ] 副作用涉及的其他实体/通知已点名到具体对象，不会让下游无从接线
- [ ] 已同步回父文档 §状态变化 小节，未改动其他小节

## Audit Report Shape

```text
status_recommendation
passed_checks
failed_checks
repairs_applied
blocking_questions
nonblocking_unknowns
decisions_required
traceability_gaps
downstream_risks
```
