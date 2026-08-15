# Thinking Core · 通用思想引导核心层

> 本文件是所有 Work Item Skill（5 个主 Skill + 9 个子 Skill）**共享的通用思想引导层**。
> 各 Skill 的 `references/thinking-framework.md` 必须引用本文件并遵守本文件的使用协议。
> 与 `src/framework/workflow.md`（通用执行循环）一致；本文件是 AI 运行时权威。
> 变更顺序：先改本文件 → 再同步 `src/framework/workflow.md` → 再同步各 Skill 的 `thinking-framework.md` 引用。

## 使用协议（AI 必读，违反即工作流缺陷）

1. **循环强制（最高优先级）**：每个 Work Item（含 5 个主项与 9 个子项）都必须完整走一遍 `Preflight → Intake → Think → Clarify → Generate → Audit → Human Gate → Commit / Reflow`（见 `src/framework/workflow.md`）。**没有任何产物可以绕过人工确认进入下游**——PRD 汇总产物同样必须人工确认后才能交付。机器校验只能产生 `ready_for_human_review`，不能产生 `confirmed`。
2. **三件套**：每个 lens 必须按"触发时机 → 核心问题（≤3 个）→ 产出落点"使用，禁止只读不产出。
3. **分层使用**：通用核心层（本文件 §1）每个 Work Item 必用；校验层（§2）在 Audit / Human Gate 前用；发散与决策层（§3）由各 Skill 按需挑用。
4. **单次上限**：一次产出最多应用 8-10 个 lens，宁缺毋滥。不把本文件全文塞进产物。
5. **防空转**：稀疏或冲突输入不进入发散，直接路由 `needs_user_input`（见 `src/framework/workflow.md` Entry And Exit）。

---

## §1 通用核心层（每个 Work Item 必用 · 6 个）

### 1. 第一性原理 / First Principles

- 触发时机：`Think` 阶段开始
- 核心问题：
  1. 需要改变的可观测结果是什么？根本问题是什么？
  2. 哪些声明是伪装成需求的假设？
  3. 如果去掉提议方案，目标是否仍然成立？
- 产出落点：产物目标章节（用词必须指向可观测结果，不从模板字段倒推需求）

### 2. 系统思考 / Systems Thinking

- 触发时机：旅程、功能、规则分析（Stage 1-2 全程）
- 核心问题：
  1. 这个变化影响上游/下游 Work Item、其他角色、数据归属、外部系统或依赖吗？
  2. 哪些已经有效、不能破坏？
- 产出落点：假设与依赖章节（显式列出受影响面）

### 3. 对抗性审查 / Adversarial Review

- 触发时机：`Audit` 阶段
- 核心问题：
  1. 前提不成立会怎样？我能否构造反例推翻当前方案？
  2. 证据是否只来自一个利益方？方案是否优化一方而伤害另一方？
  3. 是否在理解备选方案前就预设了解决方案？
- 产出落点：Audit 结果（只记录影响候选版本或需人工确认的发现，不灌水）

### 4. 逆向验证 / Reverse Validation

- 触发时机：`Audit` 阶段末 / Commit 前
- 核心问题：
  1. 从预期结果反推，哪些前提必须为真？
  2. 缺失哪些前置条件、依赖、基线数据、归属与约束？
- 产出落点：DoD 检查 / 下游输入摘要

### 5. 确认偏误防御 / Confirmation Bias Defense

- 触发时机：每步产出后（尤其 Intake → Generate 之间）
- 核心问题：
  1. 我是不是顺着用户/上游的方案在写？有没有独立质疑过它本身？
  2. 如果我把 AI_INFERENCE 当 FACT 写进去，后果是什么？
- 产出落点：知识状态标签（FACT / DECISION / ASSUMPTION / AI_INFERENCE / UNKNOWN / CONFLICT 必须逐条核实，见 `src/framework/contracts.md`）

### 6. 知识边界认知 / Knowledge Boundary

- 触发时机：全流程
- 核心问题：
  1. 已知 / 未知 / 自以为知道——三者分清了没？
  2. 没有证据支撑的推断标 AI_INFERENCE 了没？不确定的标 UNKNOWN 了没？冲突标 CONFLICT 了没？
- 产出落点：`Intake` 知识状态登记 + QuestionRecord 问题清单

---

## §2 校验层（Audit / Human Gate 前 · 按需触发）

### 7. 事前验尸 / Pre-Mortem

- 触发时机：阶段收口 / B3 问题收口（`Audit` 阶段）
- 核心问题：假设这个需求做出来失败了，最可能的原因是什么？（逐条列出 3-5 条）
- 产出落点：问题清单 / 风险条目（每条失败原因 → 风险 + 责任人）

### 8. 空杯视角 / Fresh-Eyes Review

- 触发时机：产物提交 Human Gate 前
- 核心问题：假设我是刚入职的开发或业务方，只看这份产物，能直接理解并执行吗？缺了什么信息？
- 产出落点：Audit 清单（补充缺失信息，不靠对话记忆补全）
- 具体技法（PR-FAQ，吸收自 product-management / Amazon Working Backwards）：在空杯视角自检前，先写一份"假装产品已发布"的新闻稿（PR）+ 常见问题（FAQ）——用客观、数据详实的语言描述目标用户、痛点与解决方案，并加一个假想发布日期。若新闻稿无法打动读者或 FAQ 答不出关键问题，说明价值尚未想清楚。新闻稿/FAQ 是内部思考工具，不进入正式产物。


### 9. 可测试性校验 / Testability Check

- 触发时机：功能描述 / PRD 汇总
- 核心问题：每条需求/规则能写出可量化的验收判据吗？没有判据的标记为未完成
- 产出落点：AC-XXX 验收依据（每条款必须有明确判据，见 `contracts.md` Knowledge States）

### 10. 结论先行 / Conclusion First

- 触发时机：每个产物开头
- 核心问题：第一屏能否让读者做出判断？细节是否都放到了后面？
- 产出落点：产物开头结论段（不改变内容，只改变顺序）

### 11. 读者视角 / Reader Perspective

- 触发时机：写作全程
- 核心问题：业务方看决策、研发看实现、测试看判据——各自能在这份产物里读到吗？
- 产出落点：产物结构（按读者分组组织，不混写）

---

## §3 发散与决策层（领域层 · 各 Skill 挑用）

| lens | 触发时机 | 核心问题 | 主要使用 Skill |
|---|---|---|---|
| 同理心视角 / Empathy | 旅程/UX/功能分析 | 换到每个角色身上，他的场景、挫败点、期望是什么？ | user-journey-and-stories, product-ux |
| MECE 穷举 / MECE Enumeration | 场景发散、功能清单 | 按角色×生命周期×路径类型切矩阵，先切分再填充，禁止直接列清单 | user-journey-and-stories（B2 场景发散） |
| 边界扫描 / Boundary Scan | 范围基线、UX Scope | 哪些是本期不做但相邻的？边界在哪、谁负责交界处？ | product-ux（Scope 层） |
| 奥卡姆剃刀 / Occam's Razor | 多方案取舍 | 两个方案都能达标时，哪个依赖最少、下游影响最小？ | feasibility-analysis |
| 机会成本视角 / Opportunity Cost | 范围收口 | 做这个的代价是放弃什么？值得吗？ | product-ux, prd-assembly |
| 一致性校验 / Consistency Check | PRD 汇总 | 正向：每个产物都有章节；反向：每节都能追溯；有无自相矛盾？ | prd-assembly |

---

## §4 与注册表 / 契约的绑定关系

| 本文件条目 | 绑定对象 | 校验方式 |
|---|---|---|
| §1 通用核心层 | `workflow-registry.json` work_items[*].required_outputs | `validate_artifact.py`（结构 + 语义红线） |
| §1.5 确认偏误 / §1.6 知识边界 | `contracts.md` Knowledge States（6 标签） | `validate_artifact.py`（ready/confirmed 必须含非 FACT 标签） |
| §2.7 事前验尸 | B3 问题收口（IssueRecord） | `branch_validator.py`（B3 记录完整性） |
| §2.9 可测试性 | AC-XXX 验收依据 | `validate_artifact.py`（AC 量化判据检查） |
| §3 发散决策 | support-skills（feasibility-analysis 等） | 人工触发，不设全局闸门 |


---

## §5 表达层技法注册（按需触发 · 不设全局闸门）

以下技法来自 Trae 生态 skill 的适配吸收，注册到对应子 Skill 的 `references/`，由 SKILL.md 按需加载。它们不新增业务阶段，只在需要原型/规则表达时增强产物质量。

| 技法 | 来源 | 注册位置 | 触发条件 | 产物 |
|---|---|---|---|---|
| 可点击原型技法 | interactive-demo-factory + flow2demo | `product-ux/skills/page-design/references/prototype-techniques.md` | P0 流程 ≥ 3 页 / 状态分支 / 需多方评审 | prototype/index.html + demo-flow.md |
| 规则写作规范 | 交互规则书写格式 | `product-ux/skills/interaction-rules/references/rule-writing-format.md` | 任何 IX-XXX 交互规则产出 | 段落式 IX 规则（含异常/边界） |
| PRD 原型嵌入 | agile-pm-workflow | `prd-assembly/references/prototype-embedding.md` | 上游已有可点击原型 | PRD §4 内嵌 iframe 切片 + 版本切换器 |

使用规则：
1. **文本规则是权威，技法产物是增强**：原型/切片不替代 page-design §4、interaction-rules §5、function-description 的文字详述。
2. **按需触发，不设全局闸门**：与「图表不设必须先询问的全局闸门」原则一致（见 `src/framework/governance.md`）。
3. **忠于输入**：原型不发明页面、不静默补状态；缺失信息标记 `待确认` 交人工。
4. **版本联动**：PRD 内嵌切片路径必须与原型版本一一对应，绝不覆盖历史版本。
