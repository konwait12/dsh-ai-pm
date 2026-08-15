# Thinking Framework · interaction-rules

> **Common Core（必用）**：先应用 `src/framework/thinking-core.md` §1 的 6 个通用 lens（第一性原理 / 系统思考 / 对抗性审查 / 逆向验证 / 确认偏误防御 / 知识边界认知），再应用本文件领域透镜；Audit 前应用 `thinking-core.md` §2 校验层（事前验尸 / 空杯视角 / 可测试性 / 结论先行 / 读者视角）。只记录改变候选内容的发现，不重复粘贴分析。

从 page-design 的页面出发，逐元素推导页面层交互规则（IX-*）的思考透镜。保持页面层：只写「用户操作 → 系统响应」，业务逻辑一律下沉到 function-description。

## Lens 1：触发-响应（Trigger-Response）

**问题**：用户在这个页面的每一个可操作元素上做了什么，系统会给出一条可观察、可描述的响应？

逐元素列出：按钮、输入框、列表项、Tab、链接、弹窗。为每个元素写清楚「什么操作（触发条件）」与「什么反馈（系统响应）」的对子。

**反模式**：只写功能句而不写系统响应（「点击按钮进入下一步」却没有说明界面如何变化），或只写系统动作而丢失触发上下文（「系统打开弹窗」却不说明用户点了什么）。

## Lens 2：状态机（State Lens）

**问题**：这个交互元素从开始到结束会经历哪些状态（初始 / 加载 / 空态 / 成功 / 失败 / 禁用 / 超时），状态之间如何迁移？

对每个可交互元素穷举其状态集合，至少覆盖：操作前可用态、操作中 loading、成功反馈、失败反馈、空数据态、超时与重试。状态迁移要给出迁移条件。

**反模式**：只描述成功路径，把 loading、空态、失败、超时等中间/异常状态当作「没必要写」，导致下游开发只能靠猜。

## Lens 3：边界门（Boundary Gate）

**问题**：这条规则是「页面层交互」，还是「业务逻辑 / 数据校验 / 权限 / 计算」？

逐条自问是否属于以下下沉项，命中即移交给 function-description：
- 数据校验（格式/正则/唯一/范围）→ `VL-*`
- 业务计算（合计/均值/折扣/状态判定依据）→ `BR-*`
- 权限规则（如「仅管理员可操作」）→ function-description
- 验收标准 → `AC-*`

**反模式**：把「密码必须 8 位以上」「库存不足时不允许下单」「仅 VIP 可见」这类领域规则揉进 IX 规则，造成页面层与业务层边界污染。

## Lens 4：可实现与可测试（Implementability）

**问题**：一个开发者只读这一条 IX 规则能否直接实现该交互？一个测试者能否据此写出可复现的用例？

判断标准：规则描述中没有「合理提示」「适当反馈」「视情况而定」等模糊措辞；系统响应必须是具体的动作或确定的界面状态。

**反模式**：用模糊形容词代替确定响应（「提交后给出合理提示」），使规则不可实现、不可测试。

## Lens 5：追溯性（Traceability）

**问题**：每一条 IX 规则能否追溯到 page-design 的某个页面，并对应到 functional-flow 功能流程中的某个流程步骤？

核对反向覆盖：functional-flow 功能流程中出现的每个页面在交互规则中都有 IX；没有对应的页面不得凭空产生孤儿规则。「来源」列必须写明适用的页面/功能。

**反模式**：产生与页面清单无对应关系的孤儿 IX（如凭空写「全局刷新」），或漏掉 functional-flow 功能流程中已存在的关键页面交互。

---

## Low-Density Degradation Mode

当上游 page-design / functional-flow 页面不完整、交互点不清晰时（见 `SKILL.md` §1 Preflight 判定），五个领域透镜无法产生有效工作。

```text
low-density input → skip 5-lens ideation
                   → do not enter Generate / Audit
                   → output only:
                      a) input sufficiency assessment（可交互元素 / 触发响应 / 异常反馈的缺失清单）
                      b) batched clarifying questions（每条：AI 初步判断 + 选项 + 影响 + owner）
                   → status = needs_user_input
                   → wait for human to fill in, then re-enter Preflight in sufficient mode
```

Degradation triggers（任一即触发）:

- 只有一句"给 X 加些交互规则"，没有任何页面或操作
- 上游 page-design 未 confirmed 或页面清单为空
- 页面存在但可交互元素、触发条件完全未提及

这不是失败状态，而是信息不足时的正确响应——省下人工评审时间，产出一批干净的澄清问题，而不是一批没有页面依托的孤儿 IX 规则。

---

## Confirmation Bias Defense（Wave-1 特化）

1. 我是不是在照着需求方"就是弹个提示"的假设写响应，而没有推导流程真正需要的反馈？
2. 需求方描述的交互是否隐藏了 loading、失败、超时等必须定义的状态？
3. 我补的每条响应，是来自页面/流程证据，还是来自"常见交互是这样"的猜测？

## Knowledge Boundary（Wave-1 特化）

1. "页面操作存在"（FACT）与"反馈内容我推测"（AI_INFERENCE）是否可区分？
2. 错误提示文案、超时行为这些尚未确认的响应，标 `UNKNOWN` 交人工了吗？
3. 命中校验/计算/权限的内容，是否已移交而不是揉进 IX？

---

## 表达层技法（可选加载）

产出 IX-XXX 规则时，加载 `references/rule-writing-format.md`（使用标准交互规则书写格式），使用**段落式表达**（用户状态 + 动作 → 系统响应，IF/ELSE 分支，异常与边界）而非表格分列。**IR 呈现 BR 的结果、BR 定义 IR 的依据**；命中数据校验/计算/权限即移交 function-description。
