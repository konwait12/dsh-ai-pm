---
name: prd-assembly
description: Assemble all confirmed business and product baselines into one traceable PRD without introducing new requirements. Apply structured review taxonomy and traceability audit.
---

# PRD 汇总（PRD Assembly）

## 目的与边界（Purpose And Boundary）

通过组织已确认的上游内容、校验跨产物一致性、应用结构化评审分类法、让未决风险可见，产出唯一的最终 `prd.md`。

**不要**：发明、静默解决、概括删减、润色成改变含义、或添加任何新需求。PRD 汇总 = **聚合 + 审计**，不是设计。

## 输入与输出（Inputs And Outputs）

**输入**：4 个上游 work item 全部已确认（project-background-goal、user-journey-and-stories、product-ux、function-description）。

**输出**：
- `prd.md`：7 正文节 + 需求追溯矩阵（附录）+ 自审记录（附录）
- 正向/反向追溯检查、不一致报告、Review taxonomy 结论 → 进 `99-review/` 评审记录，**不写进 prd.md 正文**（由机器在 gate 时产出）

汇总前加载 `references/thinking-framework.md`（→ `thinking-core.md` §1 必用 + §2 检查 + §3 pre-mortem）。审计前加载 `src/shared/audit/review-taxonomy.md`。若上游 `product-ux` 产出了可点击原型，加载 `references/prototype-embedding.md`（§4 分功能详述可嵌入 iframe 切片 + 版本切换器；可选，文本规则仍权威）。

## 工作流（Workflow）

### 1. Preflight
- "所有 4 个上游产物都由合法的人工评审记录确认了吗？"
- 核验：所有前置产物 `confirmed`，无 simulated/superseded/blocked 基线。
- **只要任一基线缺失或未确认就 STOP**。路由回最早未确认的 Work Item。

### 2. Intake
在不改变知识状态的情况下加载：来源 ID、目标（G1-G5）、角色、生命周期阶段、故事（ST-XXX）、范围基线、功能（FEA-XXX）、UX 流程、页面、交互规则（IX-XXX）、功能描述（FUN-XXX）、业务规则（BR-XXX）、校验（VL-XXX）、状态转移、异常、验收标准（AC-XXX）、决策（DEC-XXX）、假设（AII-XXX）、未知（UNK-XXX）。

### 3. Think（跨产物分析）
- **正向追溯（Forward trace）**：G→ST→FEA→FUN→AC/BR。每条 AC 都追溯到 FUN→FEA→ST→G。无孤儿。
- **反向追溯（Reverse trace）**：AC→FUN→FEA→ST。没有无上游存在理由的元素。
- **一致性检查（Consistency check）**：对比四个产物间的术语、范围、优先级、约束、角色、状态与依赖。标记每个不匹配。
- **Pre-Mortem**（thinking-core §2.7）："如果这份 PRD 上线 3 个月后失败，最可能的原因是什么？" → 列出 3-5 个失败场景 → 检查 PRD 是否应对。

### 4. Clarify
- **不要在本 Skill 回答新的业务问题**。
- 记录带证据的不一致。路由回最早受影响的 Work Item。
- 存在实质性不一致时，阻断最终确认。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
填模板（由 `src/templates/resolver.py prd.md` 解析）。
正文 7 节：项目背景与目标 → 业务角色/旅程/故事 → UX → 分功能描述 → 按需章节 → 事实与决定 → 验收依据；附录 2 节：需求追溯矩阵、自审记录（Constitution Compliance）。
正向/反向追溯检查与不一致报告**不写进正文**——它们在 Audit 阶段由机器产出、进 99-review 评审记录。

### 6. Audit（应用评审分类法）
按顺序运行：
1. `scripts/validate_artifact.py <prd> --json` → 结构校验
2. `src/scripts/traceability_check.py <REQ-DIR> --json` → 显式边审计
3. `src/scripts/branch_validator.py <REQ-DIR> --json` → 共享记录校验
4. **评审分类法扫描**（应用 `src/shared/audit/review-taxonomy.md`）：
   - 扫描 [Contradiction]：跨章节逻辑冲突
   - 扫描 [Gap]：缺失关键信息
   - 扫描 [Fallacy]：错误前提
   - 扫描 [Redundancy]：重复内容
   - 扫描 [Dangling]：断裂的引用
   - 扫描 [Overreach]：范围外的实现细节
   - 扫描 [Unowned]：未分配的责任
   - 对每条发现 → 裁定：APPROVED / CONDITIONS / REVISION
   - **发现进 99-review 评审记录，不写进 prd.md 正文**
5. 对抗性审视（thinking-core §1.3）："我能构造一个让这份 PRD 导向错误产品的场景吗？"
6. **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

任何断裂的关系、未经批准的添加或 REVISION 级发现 → 闸门失败。

### 7. Human Gate
呈现给授权的最终批准人：
- PRD
- 追溯报告（正向 + 反向、边计数、孤儿检测）
- 不一致报告（带 [Contradiction]/[Gap] 等标签）
- 未决风险（已变得实质性的 UNK-XXX）
- 上游 delta（自上次汇总以来的变更）
- 评审分类法发现与裁定

**禁止自动批准与模拟批准。** 只有来自 `00-input/authorized-reviewers.json` 的授权人工评审人可以批准。

### 8. Commit / Reflow
- 批准时 → `prd.md` 变为 `confirmed`，带 SHA-256 绑定。
- 拒绝时 → 写 reflow 记录 → 返回最早受影响的 Work Item → 重建 PRD。
- CONDITIONS 时 → 带条件清单批准 → 下游标记为 `conditional_review`。

## 评审分类法速查（Review Taxonomy Quick Reference）

来自 `src/shared/audit/review-taxonomy.md`：

| 标签 | 在 PRD 中找什么 |
|---|---|
| [Contradiction] | 两个章节说相反的事 |
| [Gap] | 缺失阻断实现的信息 |
| [Fallacy] | 基于错误假设的主张 |
| [Redundancy] | 同一信息在 >1 处出现，可能漂移 |
| [Dangling] | 引用不存在的 ST/FEA/BR |
| [Overreach] | PRD 指定实现细节 |
| [Unowned] | 某个决策无人类负责人 |

## 反模式（Anti-Patterns）

| ❌ 不要 | ✅ 要做 |
|---|---|
| 在汇总阶段添加一个"锦上添花"功能 | 把想法路由回 project-background-goal |
| 静默修复不一致的术语 | 在评审记录中标为 [Redundancy] 或 [Contradiction] |
| 因为"很明显"就跳过追溯 | 运行 traceability_check.py——它能找出不明显的孤儿 |
| 带着未决的 CRITICAL [Gap] 批准 | 用 REVISION 裁定阻断 |
| 不运行 traceability_check 就生成 PRD | 始终运行显式边审计 |

## 加载参考文档（Load References）

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见反模式（写产物时对照规避） | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/output-contract.md` | 产物结构与 ID 契约 | Draft 前 |
| `references/prd-structure-reference.md` | PRD 结构参考（章节组织方法论） | Generate 前 |
| `references/prototype-embedding.md` | PRD 原型嵌入技法（上游有原型时用） | 上游有原型时 |
| `references/question-patterns.md` | Clarify 提问模板（8 类句式） | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单（Human Gate 用） | Human Gate 前 |
| `references/source-handling.md` | 来源处理规则（SRC-* 登记与引用） | Intake/来源处理时 |
| `references/thinking-framework.md` | 思考透镜（Common Core + 领域 lens，必读） | 每次任务开始（必读） |

## 完成标准（Completion）

所有上游基线合法且已确认；每条必需的 G→ST→FEA→FUN→AC/BR 关系显式；没有引入新需求；评审分类法发现已带裁定记录；风险与冲突可见；机器检查（校验器 + 追溯 + branch）通过；且授权的人类显式批准 `prd.md`。
