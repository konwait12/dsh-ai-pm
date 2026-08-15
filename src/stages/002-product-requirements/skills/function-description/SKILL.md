---
name: function-description
description: Specify domain-level business rules, validation, permissions, state transitions, exceptions, and acceptance criteria for each confirmed feature. Interaction rules (IX) are owned by product-ux/interaction-rules — reference only.
---

# 功能描述（Function Description）

## 目的与边界（Purpose And Boundary）

定义范围内每个功能**如何**行为——达到业务方可理解、开发可实现、测试可验证的粒度。本 Skill 拥有功能清单（FEA）、功能流程与领域规则（BR、VL、状态、异常、AC）。交互规则（IX）由 product-ux/interaction-rules 拥有——**引用它们，不要重新定义**。

**不要**：重新设计 UX、添加不可追溯的功能、写测试用例、架构、数据库 schema 或 API 契约。

## 子 Skill（执行顺序）

每个子 skill 产出 function-description 产物的一个章节：
1. `feature-list` → §功能清单（FEA 表：已确认的范围内功能清单）
2. `functional-flow` → §功能流程（每个 FUN 的主/备选/异常/失败路径）
3. `business-rules` → §业务规则（BR 表：领域约束、计算、策略）
4. `validation-rules` → §校验规则与字段定义（VL 表：字段级 + 跨字段校验、错误提示 + 字段定义）
5. `state-machine` → §状态变化（STATE 表：状态 × 事件 → 目标状态）
6. `exception-handling` → §异常与失败处理（EX 表：失败模式 + 用户可见的恢复）
7. `acceptance-criteria` → §验收依据（AC 表：Given/When/Then + 量化阈值）

## 输入与输出（Inputs And Outputs）

**输入**：上游功能清单 FEA（`feature-list` 子 skill 产出）+ 已确认 `product-ux`（IX、页面）+ 已确认业务上游（ST、范围基线）。
**输出**：一个 `function-description.md`，由 7 个子 skill 依次产出 7 个章节：§功能清单 / §功能流程 / §业务规则 / §校验规则与字段定义 / §状态变化 / §异常与失败处理 / §验收依据。字段规则和埋点章节按需出现。

分析前加载 `references/thinking-framework.md`（→ `thinking-core.md` §1 必用 + §2 检查层透镜）。写 BR/VL 规则前加载 `references/ears-syntax.md`（EARS 句式标准）。

## 思考提示词（按阶段）（Thinking Prompts per stage）

### 1. Preflight
- "上游所有 FEA 都确认了吗？总功能数（P0/P1）是多少？"
- 从 product-ux 提取范围：功能清单、IX 引用、页面/状态、角色、依赖。
- 标记：如果某个 P0 FEA 没有 IX 规则 → 警告（UX 对功能设计来说欠定义）。

### 2. Intake
- 为每个 P0 功能创建一个 `FUN-XXX` 块。保留 `FEA-XXX` → `ST-XXX` 链接。
- **写规则之前**：解决任何缺失的归属或矛盾的 UX。如果 product-ux 说"按钮做 X"但 user-journey 说"按钮做 Y"，标为 CONFLICT。

### 3. Think（per function）
对每个 FUN，系统性走一遍以下路径：
- **主路径（Main path）**：从入口到成功的快乐日流程
- **备选路径（Alternate paths）**：用户走不同的合法路径
- **异常路径（Exception paths）**：输入错误、认证失败、状态冲突
- **失败路径（Failure paths）**：网络超时、系统错误、数据不一致
- **超时路径（Timeout paths）**：空闲超时、会话过期
- **权限路径（Permission paths）**：基于角色的访问控制
- **重试路径（Retry paths）**：瞬时失败 → 保留状态重试
- **取消路径（Cancellation paths）**：用户中途中止
- **回滚路径（Rollback paths）**：部分完成 → 清理

每条路径 → 识别：适用哪些 BR？哪些 VL 校验？什么状态变化？什么异常？什么 AC 验证？

### 4. Clarify
批量提问影响以下方面的：用户可见行为、业务策略、权限规则、校验逻辑、状态转移、失败恢复、度量阈值。
当存在实质性可行性或多方案取舍时，触发 `feasibility-analysis`（可行性分析，support skill）。
- 遇到「待确认 / 冲突 / 信息缺口」信号：主动询问是否登记 issue-record（问题清单，见 `src/shared/clarify/skills/issue-record`）；送审前 dor_check 会硬检查收口与引用。

### 5. Generate
填模板（由 `src/templates/resolver.py function-description.md` 解析）。7 个子 skill 各自产出对应章节：
- `feature-list` → §功能清单（FEA-*）
- `functional-flow` → §功能流程（每个 FUN 的流程）
- `business-rules` → §业务规则（BR-*：领域约束、计算、状态策略——每行一条规则，链接到来源 BRD）
- `validation-rules` → §校验规则与字段定义（VL-*：字段级校验，带精确的错误提示文本 + 字段定义）
- `state-machine` → §状态变化（STATE-*：所有状态 × 所有事件 → 目标状态，检查完整性）
- `exception-handling` → §异常与失败处理（EX-*：触发 → 系统行为 → 用户看到 → 恢复 → 关联 BR）
- `acceptance-criteria` → §验收依据（AC-*：Given/When/Then + 量化阈值（≤3s、>95% 等）+ 链接到 G-X 目标）

规则密度护栏：每个 FUN 必须有 ≥3 条 BR+VL+AC（过度欠定义时校验器会警告）。

### 6. Audit
- **规则分离**：BR（领域）、VL（格式）、AC（验证）是不同类别。没有"其实是 VL 的 BR"。
- **IX 引用保真**：每个被引用的 IX 都在 product-ux 中以匹配的 ID 存在。
- **状态完整性**：每个状态都有定义的进入/退出事件。无孤儿状态。
- **异常覆盖**：每条 BR 的异常分支都有定义的恢复路径。
- **AC 可度量**：每条 AC 都有量化阈值或可观察结果。
运行 `scripts/validate_artifact.py <artifact> --json`。修复所有错误。
- **B3 收口**：确认 issue-record 的 §13 阶段收口表已更新本 work item 行（问题数 / 收口日期 / 状态；空阶段也落行）。

### 7. Human Gate
产品负责人确认行为与策略。业务负责人确认规则与范围一致。开发评审可实现性。测试评审可验证性（AC 完整性）。

### 8. Commit / Reflow
批准后 → 把 FUN/BR/VL/AC ID 交接给 PRD assembly。
范围或功能变化 → 返回 product-ux。故事/目标冲突 → 继续返回上游。

## 反模式（Anti-Patterns）

| ❌ 不要 | ✅ 要做 |
|---|---|
| 写"系统校验输入"却不指定规则 | 写"VL-003：手机号格式校验 1xx-xxxx-xxxx，错误提示：'请使用+86手机号'" |
| 定义其实是 UI 交互的 BR | 从 product-ux 引用 IX；BR = 领域约束 |
| 只列状态不写转移事件 | 每个状态行：当前 → 事件 → 目标 → 条件 |
| 把 AC 写成"系统应正常工作" | Given X, when Y, then Z——带阈值 |
| 对"快乐日"功能跳过异常路径 | 每个功能至少包含：超时、认证失败、系统错误 |

## 示例：规范功能块（Example: Well-Specified Function Block）

```markdown
### FUN-001: 活动预约提交
- **BR-001**: 活动已结束+已签到→"感谢出席"页; 已结束+未签到→"活动已结束"页 (B05)
- **VL-001**: 姓为空→红色提示"请输入您的姓氏" (F03)
- **ST-001**: 未预约→点场次选择器→选场次中 (I11)
- **EX-001**: 网络超时→弹窗"请重新提交"→点重试重新提交 (B19)
- **AC-001** (G2): Given 已登录客人填写完整信息, when 点即刻预约, then ≤3s内弹二次确认 (≤3s P95)
```

## 加载参考文档（Load References）

| 文件 | 用途 | 何时加载 |
|---|---|---|
| `references/anti-patterns.md` | AI 常见反模式（写产物时对照规避） | Generate 时对照 |
| `references/audit-checklist.md` | Audit 自审清单 | Audit 前 |
| `references/ears-syntax.md` | EARS 句式标准（BR/VL 规则表述） | 写 BR/VL 规则时 |
| `references/nfr-catalog.md` | NFR 分类目录（Volere 10-17） | 涉及非功能需求时 |
| `references/output-contract.md` | 产物结构与 ID 契约 | Draft 前 |
| `references/question-patterns.md` | Clarify 提问模板（8 类句式） | Clarify 提问时 |
| `references/reviewer-checklist.md` | 人工评审清单（Human Gate 用） | Human Gate 前 |
| `references/source-handling.md` | 来源处理规则（SRC-* 登记与引用） | Intake/来源处理时 |
| `references/thinking-framework.md` | 思考透镜（Common Core + 领域 lens，必读） | 每次任务开始（必读） |

## 完成标准（Completion）

每个 P0 功能都有完整的功能块；IX 与 BR 是不同类别；权限、校验、状态、异常与恢复显式；AC 可度量并带量化阈值；且获得授权的人类批准基线。
