# Audit Checklist · business-rules

每次提交给父级 function-description 前自审。先跑确定性校验器，再逐条过本清单。

## Structural Gate

- [ ] 父文档 `function-description.md` 中存在 `## 2. 分功能详述` 章节，且业务规则表位于各 `FUN-XXX` 块内的「业务规则」小节
- [ ] 至少存在一条 `BR-\d+` 标识，无「待确认」占位 ID
- [ ] BR ID 全局唯一、编号连续（BR-001、BR-002…），无跳号、无重复
- [ ] 每条 `BR-XXX` 都挂在某个 `FUN-XXX` 之下，没有游离在函数块之外的孤儿规则
- [ ] 规则表头列与模板一致：`ID | 规则描述 | 类型 | 触发条件 | 约束/逻辑 | 来源`
- [ ] 元数据含 artifact ID、version、status、owner、reviewer、日期或 `待确认` / `TBD`
- [ ] `python3 scripts/validate_artifact.py <function-description.md> --json` 返回 `"ok": true`

## Source Coverage Gate

- [ ] 每个承载规则的原始来源（ST-XXX / FEA-XXX / 会议纪要 / 邮件）均已登记
- [ ] 每条 BR 的关键声明有产物落位或排除原因
- [ ] 来源直接声明与 AI 推断可区分（知识状态标签）
- [ ] 冲突保持可见，直到授权人工裁决

## Content Gate（内容门）

- [ ] 每个 P0 `FUN-XXX` 至少有一条 `BR-XXX`；P1 函数按需覆盖，无遗漏也无空壳占位
- [ ] 每条规则能回答"系统必须计算什么 / 强制什么"，是可直接执行的领域逻辑，而非泛泛描述
- [ ] 每条规则的六列字段全部填写，`触发条件` 与 `约束/逻辑` 没有留空或写「待确认」
- [ ] `类型` 已按 计算 / 约束 / 条件 / 权限 / 时序 正确归类，无「其他」「待确认」等模糊分类
- [ ] 计算类规则写明公式、单位、舍入/边界处理；约束类规则写明取值范围与拒绝行为
- [ ] 权限类规则覆盖上游已确认的全部相关角色，不只写主角色
- [ ] 时序/先后依赖规则明确前置与后置事件，可被状态机或编排逻辑消费
- [ ] 规则之间无自相矛盾（例如一条禁止、另一条允许同一场景）；有冲突则进入待确认

## Boundary Gate（边界门）

- [ ] 规则描述不含 UI 词汇（按钮、页面、弹窗、toast、点击、hover、滚动）
- [ ] 未把「用户操作 → 系统响应」写成交互规则（→ interaction-rules `IX-XXX`）
- [ ] 未把字段格式/长度/必填校验写成业务规则（→ validation-rules `VL-XXX`）
- [ ] 未把状态迁移、副作用写成业务规则（→ state-machine）
- [ ] 未把异常、失败、重试、超时、回滚处理写成业务规则（→ exception-handling）
- [ ] 未写可测验收用例（→ acceptance-criteria `AC-XXX`）
- [ ] 未引入架构、API、数据库表结构、测试实现细节等实现层内容
- [ ] 与交互规则 `IX-XXX` 的内容无重复定义，领域策略只落在本子技能

## Semantic Gate（语义门）

- [ ] 从上游推断、而非来源明确写明的规则，已标注 `AI_INFERENCE`，未冒充 `FACT`
- [ ] 来源确认过的规则标注 `FACT` 或 `DECISION`，并有出处
- [ ] 无法确认的约束标注 `UNKNOWN` 并登记到父文档「待确认问题」，不静默编造
- [ ] 触发条件与约束/逻辑足够具体，开发者无需追问即可实现
- [ ] 规则存在性可反向追溯：每条 BR 都能回答"它支撑哪个功能/故事/目标"
- [ ] 规则总量与函数量级匹配——函数多而规则为零，或规则大量冗余重复，都是危险信号

## Quality Lenses

- 第一性原理：去掉该规则依赖的某个功能后，业务目标是否仍成立？
- 系统思考：受影响的上游/下游规则、状态、字段、角色、系统均被考虑。
- 对抗性审查：至少测试了一个合理解释或失败场景（如边界值、配额打满、并发）。
- 逆向验证：从预期业务结果反推，哪些前提必须为真，是否已具备。

## Requirement Quality Gate (ISO/IEC/IEEE 29148)

对每条 material 规则按 29148 单条需求特性核查：

| # | 特性 | 通过判据 |
|---|---|---|
| 1 | Appropriate | 可追溯到 ST-XXX / FEA-XXX |
| 2 | Complete | 无悬空的缺失信息引用 |
| 3 | Conforming | 模板表头 + ID 规则满足 |
| 4 | Correct | 与来源故事/UX 一致 |
| 5 | Feasible | 无已知不可实现阻塞 |
| 6 | Necessary | 去掉后业务仍成立？ |
| 7 | Singular | 单行单声明，不把多条规则塞进一行 |
| 8 | Unambiguous | 术语有定义，两读者不会分歧 |
| 9 | Verifiable | 有可判定通过/拒绝判据；不可判定的词（合理/适当）不得出现 |

`Verifiable` 失败是阻塞项：要么补齐精确边界，要么标 `needs_user_input` 并给出负责人。

## Human Gate

- [ ] 阻塞性确认项（影响规则定义的关键约束）均已有明确答案，非阻塞项已注明原因
- [ ] 无 `待确认` 残留在已确认的规则行内；仍有占位的内容已降级为 `UNKNOWN` 并给出负责人
- [ ] 下游子技能（validation-rules / state-machine / exception-handling）可无歧义地消费本产出
- [ ] 与父级编排约定一致（按 `P0 FUN` 驱动、先于其他规则类子技能产出），无越权写入
- [ ] 本子技能产出已同步回父文档 §业务规则 小节，且未改动其他小节

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
