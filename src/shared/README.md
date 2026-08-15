# 共享机制

所有 Skill 复用的控制能力，不是独立的业务事项。按功能分类：

| 目录 | 能力 | 说明 |
|---|---|---|
| `audit/` | 审查闸门 | Skill 自审用的 checklist 和 reviewer 人类审查清单 |
| `capability-fragments/` | 通用能力片段库 | 跨案例复用标准 BR/AC/EX 片段（OBS-007 落地） |
| `clarify/` | 提问澄清 + 问题清单 | 澄清问题、issue-record 阶段收口 |
| `change-management/` | 变更回流 | 修改确认和跨 Work Item 选择性回流 |
| `decision-log/` | 决策记录 | 结构化 DEC-XXX 记录模板 |
| `human-gate/` | 人工确认 | 评审决定、驳回和修改记录 |
| `intake-routing/` | 入口判定 | L0-L4 成熟度判定，路由决策模板 |
| `project-init/` | 项目初始化 | 一键创建 REQ-DIR 骨架 |
| `traceability/` | 追溯验证 | 跨产物 G→ST→FEA→FUN→AC→BR 追溯链 |

## 九大子 Skill 索引

| Sub-Skill | 父 Skill | 章节 | README |
|---|---|---|---|
| `feature-list` | function-description | §功能清单 | `stages/002-product-requirements/skills/function-description/skills/feature-list/README.md` |
| `functional-flow` | function-description | §功能流程 | `stages/002-product-requirements/skills/function-description/skills/functional-flow/README.md` |
| `business-rules` | function-description | §BR | `stages/002-product-requirements/skills/function-description/skills/business-rules/README.md` |
| `validation-rules` | function-description | §VL | `stages/002-product-requirements/skills/function-description/skills/validation-rules/README.md` |
| `state-machine` | function-description | §State | `stages/002-product-requirements/skills/function-description/skills/state-machine/README.md` |
| `exception-handling` | function-description | §Exception | `stages/002-product-requirements/skills/function-description/skills/exception-handling/README.md` |
| `acceptance-criteria` | function-description | §AC | `stages/002-product-requirements/skills/function-description/skills/acceptance-criteria/README.md` |
| `page-design` | product-ux | §页面设计 | `stages/002-product-requirements/skills/product-ux/skills/page-design/README.md` |
| `interaction-rules` | product-ux | §交互规则 | `stages/002-product-requirements/skills/product-ux/skills/interaction-rules/README.md` |

## 分支 Skill 索引（4 产物 + 1 能力 · registry `support_capabilities`）

| Skill | 用途 | 触发条件 | 位置 |
|---|---|---|---|
| `competitive-research` | 竞品分析 | 方向不清/缺参考 | `support-skills/competitive-research/` |
| `feasibility-analysis` | 可行性分析（市场/技术/投入产出/风险；多方案取舍为其章节） | 进入主干前评估可行性或方案取舍影响范围/成本/风险 | `support-skills/feasibility-analysis/` |
| `requirement-restate` | 需求重举能力（复述+发散） | 材料稀疏/多源歧义/L0 | `stages/001-business-requirements/skills/requirement-restate/` |
| `tracking-plan` | 埋点与追踪计划 | 需要数据埋点 | `stages/002-product-requirements/skills/tracking-plan/` |
| `issue-record` | 跨阶段问题清单 | 任何阶段需求不明确/冲突 | `shared/clarify/skills/issue-record/` |

## 全局变更日志

| 版本 | 日期 | 主要变更 |
|---|---|---|
| v0.4 | 2026-08-14 | Harness 借鉴基础设施 audit_log / projection_cache / registry_contract_check / validation_errors + 真实案例脱敏 + capability-fragments 能力片段库 |
| v0.2 | 2026-08-13 | 入口收敛为唯一 AGENTS.md；删除归档垃圾；loop 引擎（init + reflow --apply + property_check 入 gate + 双向追溯 + requirements 盲区检查）；registry v5（7 分支 skill）；15 个 skill 补齐到同等丰富度（7 类 references + thinking-core 接线） |
| v0.1 | 2026-08-12 | 新增 sub-skill README/agents；dor_check 六态知识状态硬规则；orchestrator --dry-run；5 个跨 Skill 集成测试 |

共享机制服务于主线三阶段的 L2-L4 层，不独立构成业务阶段。
