# PRD 结构参考（聚合视图）

> 吸收外部 PRD 写作 skill 的结构骨架精华，为 prd-assembly 提供「章节怎么组织」的呈现方法论。

---

## 0. 边界声明（必读）

**本文仅为结构参考。** prd-assembly 只聚合已确认上游产物、不得新增需求——本文件的章节建议**不得成为发明新需求的入口**。

- 本文件只解决「已有内容怎么摆、怎么裁」；**不解决「缺什么内容」**——缺内容时不得自行补齐。
- 缺内容 → 路由回最早受影响的 work item（Preflight/Clarify 已覆盖），或标 `待确认`（UNK-XXX / Q- 引用）。
- 外部 skill 的「直接访谈用户 → 直接写 PRD」行为（discovery 提问、起草 schema、生成草稿）**不属于本项目**：本项目的访谈与生成发生在上游 4 个 work item，prd-assembly 只做聚合 + 审计。

---

## 1. 结构方法论来源（只读吸收）

| 来源 | 吸收的骨架 | 不吸收的 |
|---|---|---|
| `prd` skill（5 节 Strict Schema） | Executive Summary（问题/方案/成功标准三段式）、User Stories + Acceptance Criteria + Non-Goals 分组、Technical Specifications（架构/集成点/安全）、Risks & Roadmap（分阶段+技术风险） | 主动向用户访谈（Phase 1-2）、直接起草 schema 内容 |
| `prd-writer` skill（5 节框架 + IR/BR 规范） | Problem Statement（现状/痛点/业务影响）、Requirements 三分法（功能/技术/设计）、Implementation（依赖/时间线/资源）、Risks and Mitigations、IR/BR 编号与分支覆盖自检 | 编写新 IR/BR（那是 function-description 的职责） |

吸收原则：**结构可借鉴，内容零发明**。外部 skill 的每个章节在本项目中都必须能指出「上游产物哪一段提供」，指不出来的章节就是空壳，宁缺勿造。

---

## 2. 关键章节的组织方法论（改写为聚合视图）

### 2.1 Executive Summary（高管版核心）
外部写法骨架：Problem Statement（1-2 句痛点）→ Proposed Solution（1-2 句方案）→ Success Criteria（3-5 条**可量化** KPI）。

**聚合视图**：
- 问题陈述 ← `§1 项目背景与目标`（project-background-goal 原文）中的痛点表述；1-2 句摘引，不重写。
- 方案陈述 ← 上游 Goals（G1-G5）与 scope baseline 的聚合摘要。
- 成功标准 ← 上游已确认的可量化表述（如 goals/决策 DEC-XXX 中的指标、FUN/AC 中的可测验收）。**上游没有量化 KPI → 写「待确认」，禁止编造指标**（外部 skill 的「3-5 条 KPI」是写法建议，不是内容清单）。
- 高管版裁剪：只取 §0 清单 + §1 背景目标 + §6 追溯矩阵摘要 + §9 风险敞口，其余章节省略。

### 2.2 用户故事呈现
外部写法：`As a [user], I want to [action] so that [benefit].` 句式 + 每条故事附 Acceptance Criteria 清单。

**聚合视图**：
- 用户故事 ← `§2 业务角色、用户旅程与用户故事`（user-journey-and-stories）**verbatim**，保留 ST-XXX 编号。
- 句式不做「统一改写」：上游已确认的句式是业务事实，prd-assembly 只搬不改；如需统一风格属上游 work item 的 reflow，不在此处做。
- 验收标准 ← AC-XXX（function-description / acceptance-criteria 子 skill 产物）verbatim 挂到对应 ST。

### 2.3 技术规格段（工程师版核心）
外部写法：Architecture Overview → Integration Points → Security & Privacy（或功能/技术/设计三分法）。

**聚合视图（本项目只聚合、不设计）**：
- 本脚手架交付物是 `prd.md`，**不产出技术架构设计**。技术规格段只能呈现**上游已确认的技术约束**：
  - 技术依赖 / 集成约束 ← function-description 的 FUN-* 描述与 DEC-XXX 决定中的技术内容；
  - 安全与隐私 ← 上游已明确的合规约束（如有），无则留空或待确认，不自行添加；
  - 禁止写「建议采用 XX 架构 / 推荐 XX 数据库」——那属于 Overreach（review-taxonomy 标签）。
- 工程师版裁剪：聚焦 §2 故事 + §4 分功能 + 全部 AC/BR/IX + §6 追溯矩阵，省略高管叙述与背景渲染。

### 2.4 风险分析段
外部写法：Phased Rollout（MVP → v1.1 → v2.0）+ Technical Risks（延迟/成本/依赖失败）+ Mitigations。

**聚合视图**：
- 风险来源只能是三处：`§9 不一致报告`（含 [Contradiction]/[Gap] 等标签）、UNK-XXX 未知项、pre-mortem（thinking-core §2.7）发现的**未被 PRD 覆盖的失败场景**。
- Mitigations 若上游已有（如决策记录），verbatim 呈现；若上游无对策，写风险本身 + 标待确认，**禁止替业务想对策**。
- 分阶段路线 ← 上游 scope baseline / DEC 中的分期信息；无则「待确认」，不发明 MVP/v1.1/v2.0 规划。

### 2.5 验收清单
外部写法：每条用户故事的「Done 定义」bulleted list；要求具体可测，避免「快/易用/现代」等含糊词。

**聚合视图**：
- 验收清单 = AC-XXX 集合，verbatim，逐条可追溯到 FUN→FEA→ST→G。
- 若上游 AC 出现含糊表述（如「搜索要快」），prd-assembly **不得代写具体阈值**（如「200ms」）：标 [Gap] 或待确认，路由回 function-description。可量化是上游的写作标准，不是 assembly 的改写权。

---

## 3. 上游产物 → PRD 章节映射表

| PRD 章节（output-contract §0-§12） | 内容来源 | 外部 skill 对应章节 |
|---|---|---|
| §1 项目背景与目标 | project-background-goal verbatim | Problem Statement |
| §2 角色、旅程与故事 | user-journey-and-stories verbatim | User Stories + Acceptance Criteria |
| §3 UX 范围/流程/状态 | product-ux verbatim | User Experience & Functionality |
| §4 分功能描述（FUN/BR/IX/VL/AC） | function-description verbatim | Requirements + IR/BR 规范 |
| §5 按需章节（字段/埋点/依赖/未决） | 上游非空才落章 | Implementation（依赖部分） |
| §6 追溯矩阵 G→ST→FEA→FUN→AC/BR | 机器生成（traceability_check） | — |
| §7/§8 正反向追溯检查 | 机器生成 | — |
| §9 不一致报告 | 交叉审计 + review-taxonomy 标签 | Risk Analysis（冲突侧） |
| §10 事实与决定 | 各 work item 汇总（FACT/DECISION/ASSUMPTION） | Risks & Roadmap / Decision Log |
| §11 Constitution Compliance | 6 条硬宪法检查 | — |
| §12 验收依据与变更记录 | AC 基线 + 版本历史 | Acceptance Criteria |

---

## 4. 呈现质量技法（只影响写法，不影响内容）

- 含糊词信号：读到「快速 / 易用 / 现代 / 直观」且非上游原文引用的场景 → 不得展开成具体指标；记 [Gap] / 待确认。
- IR/BR 一致性自检（源自 prd-writer 的评审 checklist，作审计视角复用）：IX 是否覆盖 BR 的全部错误码？异常/边界是否齐全（快速重复操作、网络异常、多端登录）？加载/空/错误三态是否有明确设计？→ 只用于 `§9 不一致报告` 打标，不用于补写。
- 编号纪律：SRC-/ST-/FEA-/FUN-/BR-/IX-/VL-/AC-/DEC-/UNK- 全部保留原文，杜绝漂移（[Dangling] 即缺陷）。
- 待定项统一挂 `UNK-XXX` / Q- 引用，不写裸 TBD（外部 skill 的 "label as TBD" 在本项目落地为 UNK 体系）。

---

## 5. 边界红线复查（写完后对照）

- [ ] 每章都能指出上游出处；无法指出的章节未落笔
- [ ] 未编造成功指标 / 技术方案 / 风险对策 / 分阶段规划
- [ ] 未改写任何上游 verbatim 内容
- [ ] 缺内容时按「路由回最早 work item 或标待确认」处理，而非自答
