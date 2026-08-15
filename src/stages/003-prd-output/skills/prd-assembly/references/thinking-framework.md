# 思考框架 · prd-assembly

把 4 个已确认产物聚合为单份 PRD 并做追溯核验的透镜。

本 Skill 与前四个工作事项不同：它**不生成新内容**。它聚合、核验并报告。

## 公共核心（Common Core，必用 MANDATORY）

应用 `src/framework/thinking-core.md` §1 的 **6 个核心透镜**（第一性原理 First Principles、系统思维 Systems Thinking、对抗性审视 Adversarial Review、逆向验证 Reverse Validation、确认偏误防御 Confirmation Bias Defense、知识边界 Knowledge Boundary），以及 §2 中与本 work item 相关的检查层透镜（阶段收口前的 Pre-Mortem、Human Gate 前的 Fresh-Eyes、验收标准前的可测试性 Testability、写作时的结论先行 Conclusion First + 读者视角 Reader Perspective）。只记录会改变候选产物的发现——不要逐字重复核心透镜分析。

## 透镜 1：聚合完整性（Aggregation Integrity）

把上游产物的内容拉进 PRD 时：

1. **逐字复制**，不要转述。"润色" = 未经授权的修改。已确认文本经过人工评审——你没有权限改它。
2. **保留全部来源 ID**。每个 SRC-*、ST-*、FEA-*、FUN-*、BR-*、AC-* 都必须原样保留。
3. **如果你在已确认内容里发现错误**：不要静默修。在 §9 不一致报告里记录并标记供人工关注。

**反模式**："`project-background-goal` 里这段有点啰嗦，所以我概括了一下。"——这违反了聚合契约。

## 透镜 2：正向追溯（Forward Traceability）

从目标到验收标准走一遍链：

```
G-X (background §5) → ST-XXX (journey §3) → FEA-XXX (UX §2.2) → FUN-XXX (function §1) → AC-XXX (function §2) → BR-XXX (function §2)
```

对每条链接核验：
1. **G→ST**：每个已确认目标是否有 ≥ 1 个故事应对它？
2. **ST→FEA**：每个 P0 故事是否映射到 ≥ 1 个功能？
3. **FEA→FUN**：每个 P0 功能是否映射到 ≥ 1 个功能描述？
4. **FUN→AC**：每个 P0 功能是否有 ≥ 1 条验收标准？
5. **AC→BR**：每条引用业务规则的 AC 是否都引用了它？

在 §7 正向追溯检查中记录断裂链接。

## 透镜 3：反向追溯（Backward Traceability）

反向走一遍链：

```
BR-XXX → AC-XXX → FUN-XXX → FEA-XXX → ST-XXX → G-X
```

对每个元素核验：
1. **BR→AC**：每条业务规则是否有对应的 AC 测试它？
2. **AC→FUN**：每条验收标准是否属于某个功能？
3. **FUN→FEA**：每个功能是否追溯到某个功能清单项？
4. **FEA→ST**：每个功能清单项是否追溯到 ≥ 1 个故事？
5. **无孤儿**：有没有任何元素没有上游连接？

在 §8 反向追溯检查中记录孤儿。

## 透镜 4：跨产物一致性（Cross-Artifact Consistency）

扫描跨产物矛盾：

| 检查 | 找什么 |
|---|---|
| **角色一致性** | 4 个产物中同一角色名、同一描述 |
| **术语一致性** | 同一术语处处同义（例如 `user-journey-and-stories` 中的"候选人状态"应与 `function-description` 中的"候选人状态管理"一致） |
| **约束一致性** | 背景 §7 的约束在 `function-description` 功能描述中仍被尊重？ |
| **范围一致性** | 背景 §8 的非目标——有没有被意外作为功能纳入 `product-ux`？ |
| **优先级一致性** | `user-journey-and-stories` 的 P0 故事 → `product-ux` 的 P0 功能 → `function-description` 的 P0 功能？没有静默降级？ |

**反模式**：发现矛盾然后自己修。记录到 §9，让人类决定。

## 透镜 5：缺口检测（Gap Detection）

识别本应存在但缺失的内容：

1. **未覆盖目标**：完全没有下游链的 G-X。
2. **缺失功能描述**：没有功能描述（FUN-XXX）的 P0 功能清单项（FEA-XXX）。
3. **未被测试的验收标准**：没有可度量阈值的 AC-XXX。
4. **缺失 NFR 覆盖**：明显需要 NFR（例如处理个人数据）却没有 NFR 章节的功能。

## 透镜 6：RTM 构建（RTM Construction）

构建需求追溯矩阵（§6）：

| G | ST | FEA | FUN | AC | BR |
|---|---|---|---|---|---|
| G1 | ST-001, ST-002 | FEA-001 | FUN-001, FUN-002 | AC-001, AC-002 | BR-001, BR-002 |

规则：
- 每行代表一条完整追溯链。
- 单个 G 可能跨多行（每个下游分支一行）。
- P2 元素允许空单元格，但必须注明。
- RTM 通过阅读全部 4 个产物构建，不是靠猜测。

## 透镜 7：完整性终审（Completeness Final Review）

提交人工评审前，问：

1. 一个新开发者读这份 PRD 能否在不问 PM 的情况下理解要构建什么？
2. 一个测试者读这份 PRD 能否无歧义地写测试用例？
3. 一个业务干系人读 §1-§2 能否确认"是的，这就是我们要的"？
4. 有没有哪些章节读起来像 AI 内部笔记而不是交付文档？

## 透镜 8：Pre-Mortem（PRD 交付后失败预演）

PRD 是交给开发的契约。最终批准前，做一次失败演练：

1. 这份 PRD 最可能以什么方式被误读或误实现？（歧义术语、埋没的约束、矛盾规则）
2. 这份 PRD 交付后最可能发生什么范围蔓延？（业务方会要求的近-IN 功能、已声明但未冻结的假设）
3. 针对这份 PRD 的前 3 个 bug 报告会是什么样？AC 覆盖了吗？
4. 评审人会因为什么拒绝这份 PRD？（缺失验收依据、不可追溯的需求、不清晰的归属）

在 §9 不一致报告 / 风险章节中记录每个失败模式并带负责人——不要静默修复已确认内容。

---

## 表达层技法（可选加载）

当上游 product-ux 已产出可点击原型时，加载 `references/prototype-embedding.md`（吸收自 agile-pm-workflow），在 PRD §4 分功能详述区嵌入原型 iframe 切片（focus 沙盒锁定 + 版本切换器）。**文本规则仍是权威，切片是增强；原型缺失不静默跳过，在 §9 不一致报告标注。**
