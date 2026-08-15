# Audit Checklist · feature-list

每次提交给父级 function-description 前自审。先跑确定性校验器，再逐条过本清单。

## Structural Gate

- [ ] 父文档 `function-description.md` 中存在 `## 功能清单` 章节（支持 `## N. 功能清单` 编号形式）
- [ ] 至少存在一个 `FEA-\d+` 标识，无 `FEA-XXX` 占位 ID 冒充
- [ ] FEA ID 全局唯一、编号连续（FEA-001、FEA-002…），无跳号、无重复
- [ ] 功能清单表头列与契约一致：`ID | 功能名称 | 所属故事 ST | 优先级 | 一句话描述 | 来源`
- [ ] 元数据含 artifact ID、version、status、owner、reviewer、日期或 `待确认` / `TBD`
- [ ] 元数据 status 位于白名单内（draft / needs_user_input / conditional_review / ready_for_human_review 等），**不包含 `confirmed`**
- [ ] `python3 scripts/validate_artifact.py <function-description.md> --json` 返回 `"ok": true`

## Source Coverage Gate

- [ ] 每个承载功能的原始来源（ST-XXX / 范围基线 / 会议纪要 / 邮件）均已登记
- [ ] 每个已确认故事都被 ≥1 个 FEA 覆盖（无缺口）；每个 FEA 都能追到一个故事（无越权）
- [ ] 来源直接声明与 AI 推断可区分（知识状态标签）
- [ ] 冲突保持可见，直到授权人工裁决

## Content Gate（内容门）

- [ ] 每个 P0 ST-XXX 至少有一个 P0 FEA；P1 故事按需覆盖，无遗漏也无空壳占位
- [ ] 每个 FEA 的 `所属故事 ST` 列含 ≥1 个 `ST-XXX`
- [ ] 每个 FEA 的 `优先级` 有 P0/P1/P2 及理由（P0 = 缺它旅程无法完成）
- [ ] 每个 FEA 的 `一句话描述` 写明边界：做什么 + 明确不做什么（in/out）
- [ ] 功能之间无重叠：任一项动作只能归属一个 FEA；重叠则合并或重画边界
- [ ] 功能粒度与故事匹配——故事少而拆出十几条微功能，或故事多而功能稀疏，都是危险信号

## Boundary Gate（边界门）

- [ ] 功能清单不含 UX 词汇（按钮、页面、弹窗、toast、点击、hover、滚动）
- [ ] 未把「用户操作 → 系统响应」写成交互规则（→ interaction-rules `IX-XXX`）
- [ ] 未写页面骨架、页面区域或视觉布局（→ product-ux / page-design）
- [ ] 未写领域业务规则、计算公式、策略（→ business-rules `BR-XXX`）
- [ ] 未写字段格式/长度/必填校验（→ validation-rules `VL-XXX`）
- [ ] 未写状态迁移、副作用（→ state-machine）
- [ ] 未写异常、失败、重试、超时、回滚（→ exception-handling）
- [ ] 未写可测验收用例（→ acceptance-criteria `AC-XXX`）
- [ ] 未引入架构、API、数据库表结构、测试实现细节等实现层内容

## Semantic Gate（语义门）

- [ ] 从上游推断、而非来源明确写明的功能边界，已标注 `AI_INFERENCE`，未冒充 `FACT`
- [ ] 来源确认过的功能标注 `FACT` 或 `DECISION`，并有出处
- [ ] 无法确认的功能边界标注 `UNKNOWN` 并登记到父文档「待确认问题」，不静默编造
- [ ] 每个 FEA 足以支撑下游 `functional-flow` / `business-rules` 消费，无需回头重研故事
- [ ] 功能存在性可反向追溯：每个 FEA 都能回答"它支撑哪个故事/目标"

## Quality Lenses

- 第一性原理：去掉某个功能后，其承载的故事是否仍被满足？
- 系统思考：受影响的上游/下游功能、数据、角色、系统均被考虑。
- 对抗性审查：至少测试了一个功能重叠或覆盖缺口场景。
- 逆向验证：从已确认故事反推，所需功能是否齐全且互不重叠。

## Requirement Quality Gate (ISO/IEC/IEEE 29148)

对每条 material 功能按 29148 单条需求特性核查：

| # | 特性 | 通过判据 |
|---|---|---|
| 1 | Appropriate | 可追溯到 ST-XXX |
| 2 | Complete | 无悬空的缺失信息引用 |
| 3 | Conforming | 模板表头 + ID 规则满足 |
| 4 | Correct | 与来源故事一致 |
| 5 | Feasible | 无已知不可实现阻塞 |
| 6 | Necessary | 去掉后其承载故事仍成立？ |
| 7 | Singular | 单行单功能，不把多条功能塞进一行 |
| 8 | Unambiguous | 功能边界有定义，两读者不会分歧 |
| 9 | Verifiable | 有可判定是否存在/归属的判据 |

`Verifiable` 失败是阻塞项：要么补齐边界，要么标 `needs_user_input` 并给出负责人。

## Human Gate

- [ ] 阻塞性确认项（影响功能集合与边界的关键决策）均已有明确答案，非阻塞项已注明原因
- [ ] 无 `待确认` 残留在已定稿的功能行内；仍有占位的内容已降级为 `UNKNOWN` 并给出负责人
- [ ] 下游子技能（functional-flow / business-rules）可无歧义地消费本产出
- [ ] 与父级编排约定一致（order 1，先于其他功能类子技能产出），无越权写入
- [ ] 本子技能产出已同步回父文档 §功能清单 小节，且未改动其他小节

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
overlap_candidates
downstream_risks
```
