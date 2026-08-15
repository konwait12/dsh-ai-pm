# Audit Checklist · interaction-rules

每次交付人工评审前进行自审。先运行确定性校验器 `scripts/validate_artifact.py`，再逐项核对本清单。

## 1. Structural Gate

- [ ] 父工件 `product-ux.md` 存在且为 `confirmed` 版本（或处于本 Skill 可写的候选阶段）
- [ ] 父工件中存在 §3 交互规则 章节
- [ ] 章节内至少存在一个 `IX-` 标识符
- [ ] IX 编号连续且唯一（IX-001、IX-002、…），无跳号或重复
- [ ] 表格表头与模板一致：ID、规则描述、触发条件、系统响应、适用页面/功能、来源
- [ ] 每一行规则都有 IX-* ID，无空 ID 行

## 2. Content Gate

- [ ] 每个 P0 页面/功能的关键可交互元素（按钮、输入框、列表项、Tab、链接）都有对应 IX 规则
- [ ] 每条规则都满足「触发条件 → 系统响应」结构，二者缺一不可
- [ ] 状态变化完整：按钮禁用/启用、loading、空态、成功、失败、超时均已覆盖
- [ ] 弹窗/对话框行为明确：打开、关闭、遮罩点击、取消、确认后动作
- [ ] 导航触发规则覆盖：页面跳转、Tab 切换、返回、关闭
- [ ] 异常与失败反馈已定义：错误提示内容、重试动作、超时处理
- [ ] 规则描述足够具体，开发者可仅凭该条实现，测试者可据此编写用例
- [ ] 每条 IX 的「来源」列都标注了适用的页面/功能

## 3. Boundary Gate

- [ ] 不含数据校验逻辑（格式/正则/唯一/范围）——此类归 function-description `VL-*`
- [ ] 不含业务计算（公式/合计/均值/折扣）——此类归 function-description `BR-*`
- [ ] 不含权限规则（如「仅管理员可操作」）——此类归 function-description
- [ ] 不含验收标准（`AC-*`）
- [ ] 不含架构、API、数据库、测试用例等实现细节
- [ ] 不重复/不替换 functional-flow 功能流程的跨页面流程描述
- [ ] 不涉及页面布局、视觉样式等 page-design 内容
- [ ] 全文扫描无数据校验关键词（format/regex/unique/range）、计算关键词（formula/sum/average）、权限关键词（only admin can）

## 4. Semantic Gate

- [ ] 业务事实（FACT）均有来源证据
- [ ] AI 推断（AI_INFERENCE）明确标注，不冒充 FACT
- [ ] 未知项（UNKNOWN）标明了责任人
- [ ] 冲突（CONFLICT）显式保留双方观点，不静默解决
- [ ] 每条 IX 可追溯至 page-design 的对应页面与 functional-flow 功能流程的对应流程
- [ ] IX 覆盖范围与 functional-flow 功能流程中出现的页面一致，无孤儿规则、无缺失页面
- [ ] 对真实业务事实使用知识状态标签，而非仅停留在「待确认」

## 5. Quality Lenses

- 第一性原理：删掉某条规则后，用户是否仍能得到必要的可观察反馈？该规则是否只是"看起来完整"？
- 系统思考：异步结果（支付、通知、回调）是否被表示为等待/成功/失败状态？是否依赖外部系统的行为？
- 对抗性审查：为每条关键规则构造反例——双击、超时、断网、陈旧页，验证反馈已定义。
- 逆向验证：从"用户顺利完成任务"反推，缺了哪些必须存在的反馈？
- 最小充分：规则覆盖页面交互所需，且不包含业务判定、视觉与实现细节。

## 6. Requirement Quality Gate（29148 特化）

每条 IX 按单条需求的九特征抽查：可验证（响应可写判据）、无歧义（触发唯一）、单一（一条一个交互）、必要（删掉丢反馈）、一致（适用页面存在于 §2 页面设计）。"响应模糊"（如"给出合理提示"）为阻断项：要么改为具体动作/状态，要么 `needs_user_input`。

## 7. Human Gate

- [ ] `python3 scripts/validate_artifact.py <product-ux.md> --json` 返回 `"ok": true`
- [ ] 所有阻塞性待确认问题均已澄清
- [ ] 剩余「待确认」项均为有意的非阻塞项，并注明责任人
- [ ] 无 AI 替业务方做决定的内容（优先级、取舍均来自上游确认）
- [ ] 规则边界清晰，下游 function-description 可无障碍消费
- [ ] 产物可独立用于产品方案评审，无需 AI 现场解释

## Audit Report Shape

```text
status_recommendation
passed_checks
failed_checks
repairs_applied
blocking_questions
nonblocking_unknowns
decisions_required
traceability_gaps        # 无适用页面的孤儿规则
downstream_risks         # 对 function-description / PRD 汇总的影响
```
