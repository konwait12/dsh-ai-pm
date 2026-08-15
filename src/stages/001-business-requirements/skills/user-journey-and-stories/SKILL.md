---
name: user-journey-and-stories
description: Build a lifecycle-by-role user journey with emotional mapping, derive traceable user story cards, and establish scope baseline from a confirmed background and goal baseline.
---

# 用户旅程与用户故事（User Journey And Stories）

## 目的与边界（Purpose And Boundary）

说明业务事件如何跨角色推进——不仅要捕捉动作，还要捕捉每个触点上的情绪、痛点与机会。把选定的旅程需求转化为带有清晰优先级（MoSCoW）的用户故事。产出一份 product-ux 可直接使用的范围基线。

**不要**：按页面组织旅程、设计 UX/UI、定义功能或规则（BR/VL/AC），或在未经业务选择的情况下确认头脑风暴候选。

## PM 专属交付物（PM-Specific Deliverables）

这是阶段 1 中最有 PM 原汁原味的交付物。它产出：
- **按角色×生命周期的旅程**——不是按页面、不是按功能。展示业务事件如何跨人员与系统流动。
- **情绪映射（Emotional Mapping）**——在每个阶段，每个角色感受如何？（沮丧 frustrated、困惑 confused、自信 confident、愉悦 delighted）——这是把功能规格变成以人为本产品的关键。
- **痛点 → 机会（Pain Points → Opportunities）**——对每个痛点，识别一个具体机会。这是从"现状已破损"到"我们可以改进这里"的桥梁。
- **故事卡片（Story Cards）**——使用规范中文句式 `在〈前提/场景〉下，作为〈角色〉，我希望〈动作〉，以便〈目标/价值〉`
- **范围基线（Scope Baseline）**——显式的纳入/排除决策，下游工作项不得静默扩张。

## 角色画像快速建档（Persona Quick-Profiling）

在构建旅程之前，为 background-goal 中识别的每个角色创建轻量画像卡：

| 维度 | 要捕捉什么 |
|---|---|
| 角色名 | 例如 FA（时尚顾问）、客人（主客）、客人（携伴） |
| 首要目标 | 他们需要从这个系统获得什么结果？ |
| 当前痛点 | 他们当前工作流中哪里坏了？ |
| 情境 | 何时/何地/多久交互一次？ |
| 技术熟悉度 | 新手 / 熟练 / 专家（影响交互复杂度） |
| 决策权 | 他们能批准，还是只能建议？ |

## 输入与输出（Inputs And Outputs）

**输入**：已确认的 `project-background-goal`（目标 G1-G5、角色、约束、来源）。
**输出**：单一 `journey-and-stories.md`，含生命周期模型、带画像的角色矩阵、旅程图（情绪 + 痛点 + 机会）、故事卡片（MoSCoW 优先级）、旅程→故事覆盖矩阵、范围基线。

分析前加载 `references/thinking-framework.md`（→ `thinking-core.md` §1 必用 + §2 MECE 场景枚举）。

## 思考提示词（按阶段）（Thinking Prompts per stage）

### 1. Preflight
- "所有目标与角色都确认了吗？背景中存在哪些生命周期线索？"
- 核验上游确认状态。提取目标（G1-G5）、角色、生命周期线索、约束、来源。
- 如果背景未确认，返回上游。

### 2. Intake
- "每个来源如何描述业务事件跨角色展开？"
- 把已确认的角色/场景事实与假设、未知项分开。
- 在展开之前登记每条生命周期线索、干系人交接与情绪信号。
- 为每个角色构建轻量画像卡。

### 3. Think

**阶段 A — 生命周期优先（Lifecycle First，业务生命周期）**
- "业务事件的生命周期是什么——与任何产品无关？"
- 阶段必须以业务事件命名，而不是产品功能。示例："活动创建"而不是"后台表单页面"；"客人接收邀请"而不是"H5过渡页"。

**阶段 B — 角色矩阵（Role Matrix，角色矩阵）**
对每个生命周期阶段 × 每个角色：
- 执行者：谁在做这个动作？
- 知情者：谁需要知道？
- 审批者：谁拍板？
- 协作者：谁帮忙？
- 支撑：什么系统/工具提供辅助？

**阶段 C — 情绪映射（Emotional Mapping，情感旅程）** 🔑 新增
- 在每个触点，角色感受如何？（😤 沮丧 / 😰 焦虑 / 😐 中性 / 🙂 满意 / 😍 愉悦）
- 整个旅程的情绪弧线是什么？（结束时是否比开始时更好？）
- 情绪最低点在哪里？→ 这通常是最需要产品介入的地方。

**阶段 D — 痛点 → 机会**
- 对每个痛点："怎样会更好？" → 具体机会
- 机会是用户故事的原材料
- 把 AI 生成的机会标注为 `AI_INFERENCE`

**阶段 E — 路径多样性（Path Diversity，路径类型覆盖）**
在适用的每个生命周期阶段遍历全部 11 种路径类型：normal（正常）、alternative（备选）、exception（异常）、failure（失败）、timeout（超时）、permission-mismatch（权限不匹配）、handoff（交接）、cancellation（取消）、retry（重试）、rollback（回滚）、recovery（恢复）。

### 4. Clarify
- 先创建旅程骨架。批量提出会实质性影响以下方面的问题：角色归属、生命周期边界、必需事件、业务范围、候选选择。
- 保持 AI 新增场景为 `AI_INFERENCE`，直到业务负责人选择它们。
- 数量限制：每轮 Session 至多 5 个问题，按旅程影响排序。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate

**故事卡片格式**（规范中文）：
```
在〈前提/场景〉下，作为〈角色〉，我希望〈动作〉，以便〈目标/价值〉
```

**优先级**（MoSCoW）：
- **P0（必须有，Must have）**：没有它，旅程无法完成。核心价值交付。
- **P1（应该有，Should have）**：重要，但存在变通方案。可行时纳入。
- **P2（可以有，Could have）**：锦上添花。除非微不足道，否则延后。
- **P3（本期不做，Won't have this time）**：显式排除并注明原因。

构建带情绪标注的按角色×生命周期旅程 → 从选定条目派生故事卡片 → 构建覆盖矩阵 → 建立范围基线。

在有用时，Mermaid 视图可以伴随权威矩阵出现，但不设单独的图示闸门。

### 6. Audit
- **角色覆盖**：每个已确认角色至少出现在一个旅程阶段中。
- **生命周期覆盖**：每个阶段至少有一个角色在行动。
- **路径多样性**：normal + 至少 2 种其他路径类型存在。
- **情绪完整性**：每个角色在关键触点上都有情绪标注。
- **故事卡片质量**：每条故事都使用规范格式 + MoSCoW 优先级 + 知识状态。
- **双向链接**：每条故事引用一个旅程条目；未覆盖的条目有原因。
运行校验器。修复非业务缺陷。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
呈现：旅程图（含情绪 + 痛点）、画像卡、故事卡片（含 MoSCoW 优先级）、覆盖缺口、未被选中的候选（是被排除的证据，不是需求）。
**只有业务负责人可以确认**——旅程边界、角色归属、优先级决策。

### 8. Commit / Reflow
批准后 → 确认基线。交接给 `product-ux`：角色、选定的故事、生命周期结构、范围基线、依赖、开放的非阻断项。
后续旅程出现缺口 → 重新进入本 Skill。

## 反模式（Anti-Patterns）

| ❌ 不要 | ✅ 要做 |
|---|---|
| 按页面组织旅程（"首页→详情页→提交页"） | 按业务生命周期阶段组织（"活动创建→邀请发送→客人接收"） |
| 跳过情绪映射（"情绪太主观"） | 捕捉情绪状态——它们揭示产品必须介入的地方 |
| 把所有东西都标成 P0 | 用 MoSCoW：如果一切都是 P0，就没有 P0 |
| 把故事写成"系统应支持 X 功能" | 用规范格式：在〈场景〉下，作为〈角色〉，我希望〈动作〉，以便〈价值〉 |
| 未经评审就确认 AI 生成的旅程条目 | 标为 AI_INFERENCE，直到业务负责人选择 |

## 示例：规范旅程条目（Example: Well-Formed Journey Entry）

| 阶段 | FA (时尚顾问) | 客人 (主客) | 情感 (FA) | 情感 (客人) | 痛点 | 机会 |
|---|---|---|---|---|---|---|
| 4.活动预约 | — | 选择场次→确认信息→点"即刻预约"→二次确认→提交 | — | 😐→🙂 (选好场次) → 😰 (担心填错) → 😍 (预约成功) | 信息填写多，需授权手机号；网络异常时信息可能丢失 | 已注册用户自动填充；异常时信息保留+重试 |

## 加载参考文档（Load References）

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见反模式 | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/output-contract.md` | 产物结构与 ID 契约 | Draft 前 |
| `references/question-patterns.md` | Clarify 提问模板 | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单 | Human Gate 前 |
| `references/source-handling.md` | 来源处理规则 | Intake 时 |
| `references/thinking-framework.md` | 思考透镜 (Common Core + MECE scenario enumeration) | 每次任务开始 |

## 完成标准（Completion）

所有已确认角色与生命周期阶段都得到体现；情绪映射揭示产品必须介入之处；痛点有对应的机会；故事卡片使用规范格式与 MoSCoW 优先级；旅程↔故事双向链接完整；没有候选被静默确认；范围基线显式；且获得授权的人类批准这两项必需输出。
