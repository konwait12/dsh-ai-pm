# Audit Checklist · validation-rules

每次提交给父级 function-description 前自审。先跑确定性校验器，再逐条过本清单。

## Structural Gate

- [ ] 父文档存在 `## 2. 分功能详述` 章节，且每个 `FUN-XXX` 块内都有「#### 系统校验」子标题
- [ ] 至少存在一条 `VL-\d+` 标识，无「待确认」占位 ID
- [ ] VL ID 全局唯一、编号连续（VL-001、VL-002…），无跳号、无重复、不与 `BR-\d+` 混淆
- [ ] 每个 `VL-XXX` 落在对应的 `FUN-XXX` 块内，不堆到全局段落
- [ ] 表头列与模板一致：`ID | 校验内容 | 校验规则 | 触发时机 | 错误提示 | 关联字段 (F) | 关联业务规则 (BR) | 来源`
- [ ] 元数据含 artifact ID、version、status、owner、reviewer、日期或 `待确认` / `TBD`
- [ ] `python3 scripts/validate_artifact.py <function-description.md> --json` 返回 `"ok": true`

## Source Coverage Gate

- [ ] 每个承载校验口径的来源（字段定义、BR-XXX、UX、素材）均已登记
- [ ] 每条 VL 的取值口径（手机号段、金额上限、码表）有出处，未凭空捏造
- [ ] 直接声明与 AI 推断可区分（知识状态标签）
- [ ] 冲突保持可见，直到授权人工裁决

## Content Gate（内容门）

- [ ] 该 `FUN-XXX` 下所有需要用户输入的字段都被枚举，无遗漏必填/可选输入项
- [ ] 每条 `VL-XXX` 都覆盖一个**可判定**的校验点：格式、范围、长度、必填、唯一性、跨字段或引用完整性，且描述具体到值域（如 `8-16 位`、`yyyy-MM-dd`、`0 < x ≤ 100`）
- [ ] 每条 `VL-XXX` 都写明**触发条件**：什么输入下会失败（非法值、边界值、冲突值、缺失值）
- [ ] 每条 `VL-XXX` 都附有面向用户的中文自然语言错误提示，说明「哪里错了 + 应该改成什么」，不是内部错误码
- [ ] 校验规则与 `FUN-XXX` 功能目的一致：该功能确有此输入与校验需求，而非凭空发明字段
- [ ] 未对只读/系统自动生成字段写校验（永远不会触发的规则是噪音）
- [ ] 存在不确定的校验边界时，已在「事实与决定 / 待确认问题」显式列出，未用猜测值伪装成定论

## Boundary Gate（边界门）

- [ ] 只写「系统接受什么数据、拒绝什么数据」，未描述错误提示的 UI 呈现方式（→ interaction-rules）
- [ ] 未定义业务计算、领域约束逻辑或状态策略（→ business-rules）
- [ ] 未描述状态流转、触发事件与副作用（→ state-machine）
- [ ] 未写异常/失败场景的系统行为与恢复方式（→ exception-handling）
- [ ] 未写可度量的验收标准 Given/When/Then（→ acceptance-criteria）
- [ ] 只引用上游已确认的 `IX-XXX`，未在本节重新定义交互内容

## Semantic Gate（语义门）

- [ ] 每个 `VL-XXX` 都标注来源：`FUN-XXX` → `FEA-XXX`/`ST-XXX`/`BR-XXX`，能一路追溯到已确认事实或决策
- [ ] 校验规则内容区分知识状态：FACT / DECISION / AI_INFERENCE / UNKNOWN，未将 AI 推断标记为事实
- [ ] 跨字段约束（A 必填当且仅当 B 被选择）与被引用字段/BR 保持一致，无自相矛盾
- [ ] 错误提示与错误处理目标一致：避免校验通过但后续仍报错的"漏校验"，也避免校验过严堵死合法业务（"过度校验"）

## Quality Lenses

- 第一性原理：这项校验是数据安全/业务正确性所需，还是为了凑覆盖率的装饰？
- 对抗性审查：是否存在能通过全部校验却破坏下游的输入？是否存在被误拒的合法值？
- 逆向验证：从"合法数据进入系统"反推，每个字段的格式、范围、跨字段关系是否都已定义。
- 读者视角：开发能不问问题就实现每条 VL？测试能构造通过/失败样例？

## Requirement Quality Gate (ISO/IEC/IEEE 29148)

对每条 material 校验按 29148 单条需求特性核查：

| # | 特性 | 通过判据 |
|---|---|---|
| 1 | Appropriate | 可追溯到字段定义 / BR-XXX |
| 2 | Complete | 无悬空缺失信息引用 |
| 3 | Conforming | 模板表头 + ID 规则满足 |
| 4 | Correct | 取值口径与来源一致 |
| 5 | Feasible | 无已知不可实现阻塞 |
| 6 | Necessary | 去掉后数据完整性受损？ |
| 7 | Singular | 单行单校验点 |
| 8 | Unambiguous | 值域明确，两读者不会分歧 |
| 9 | Verifiable | 有可执行值域与错误提示；无"校验格式"这类空话 |

`Verifiable` 失败是阻塞项：要么补齐精确值域，要么标 `needs_user_input` 并给出负责人。

## Human Gate

- [ ] 产品与业务方已确认校验边界与错误提示文案（涉及业务事实，未经确认不得自动通过）
- [ ] 开发侧确认校验规则可实现（值域、正则、跨字段约束有明确技术表达）
- [ ] 测试侧确认每条 VL 有可构造的通过/失败输入样例
- [ ] 遗留的未定校验边界已进入待确认问题清单，标注 `blocking` / 责任人，未混入正式正文
- [ ] 已同步回父文档 §系统校验 小节，未改动其他小节

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
