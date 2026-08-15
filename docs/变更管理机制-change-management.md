# 变更管理机制（Change Management）

> 本文档定义 PM Scaffold 的**变更管理机制**：已 confirmed 产物的不可变原则、受控变更流程、状态跃迁规则、逆向跃迁的留痕与锚点重算要求，以及 change-record 模板。
>
> 本文档覆盖六个变更管理落点：`--decision changes` 静默回退的留痕要求、hash 链外部锚点的自动重算、已确认产物修正的自动化变更路径、改版 / CR 的显式变更落点、不可变性与「修正」流程的协调、变更记录模板。
> 相关概念：状态语义见 `docs/状态语义矩阵.md`；Shared Records 见 `src/framework/contracts.md`；现有变更管理模块见 `src/shared/change-management/`。

---

## 一、文档目的与范围

本文档回答四类问题：

1. **已 confirmed 产物为什么不可变、现状如何保证**（branch_validator 的 hash 校验 + 外部锚点链）。
2. **变更怎么走**：提出变更 → 评估影响（downstream impact）→ 审批（reviewer 角色）→ 记录 change-*.md → 更新下游 → 重新评审。
3. **状态跃迁规则**：`confirmed → draft`（需留痕 + reason）、`confirmed → superseded`（需 superseded_reason）等合法 / 非法跃迁。
4. **逆向跃迁的留痕与锚点重算**：`pipeline.py --decision changes` 留痕、`record_sha256` 锚点、change-record 模板。

> 本文档是**设计文档**，不改变任何代码行为。其中描述的「现状」以现有代码为准；「建议 / 规划」仅作记录，供后续实现排期（自动化变更路径、不可变性与「修正」的协调、变更记录模板的处置为「方案」）。

---

## 二、已 confirmed 产物不可变原则

### 2.1 原则声明

**已 confirmed 产物是不可变基线**：`confirmed` 是唯一正式完成态，其内容与 ReviewRecord 的 `artifact_content_sha256` 绑定。**不可变 ≠ 永不修改**——修改必须走受控变更流程（本文件 §三），而不是直接改文件。

依据：
- 宪法第 6 条：人工关卡不可绕过（Human gates cannot be bypassed）。
- `src/framework/contracts.md` Confirmation Invariant：Machine checks, simulation, fixtures, and non-interactive flags cannot create or preserve formal confirmation。
- `src/framework/governance.md` Change Control：Scope freezes after confirmed product UX. A changed confirmed artifact invalidates affected downstream confirmation until rerun。

### 2.2 现状：branch_validator 的 hash 校验

| 校验层 | 机制 | 代码位置 |
|---|---|---|
| 内容 hash 绑定 | confirmed 产物当前内容 hash 必须与**最新** ReviewRecord（按 `reviewed_at` 排序）的 `artifact_content_sha256` 一致，不一致报 CRITICAL | `src/scripts/branch_validator.py` |
| 有效 reviewer | confirmed 产物必须有有效人工 reviewer（非 AI / 待确认 / simulated） | `src/scripts/branch_validator.py` |
| 记录自指纹 | ReviewRecord 正文（除自身行）的 `record_sha256` 自指纹，篡改任一字段即 CRITICAL | `src/scripts/hash_anchor.py` `record_body_sha256()` |
| 外部锚点链 | `99-review/.hash-anchor.jsonl` append-only 锚点链，防「artifact + ReviewRecord 同步篡改」 | `src/scripts/hash_anchor.py` `record_anchor()` / `verify_anchor_chain()` / `verify_artifact_anchored()` |
| 事件溯源链（Harness 借鉴点一） | `.audit/events.jsonl` append-only + `event_sha256` 自指纹 + `prev_hash` 链 + 单调 `recorded_at` + `payload_sha256` 绑定记录体；`audit_log.verify_chain` 检测任何篡改（删行 / 改字段 / 断链） | `src/scripts/audit_log.py` `append_event()` / `verify_chain()` / `reconstruct_causality()` |
| 投影缓存（Harness 借鉴点二） | `.audit/projection.json` 派生视图：从事件日志折叠 latest status / artifact hash / reviewer / review record；`is_stale` 检测自动重建；`branch_validator` 改读 projection 替代 glob+sort（老案例带 warning fallback） | `src/scripts/projection_cache.py` `build_projection()` / `read_projection()` / `is_stale()` / `latest_review_for()` |

> **外部锚点链的意义**：仅比对 artifact hash 与 ReviewRecord hash 是「闭环校验」，同步篡改可绕过；`record_sha256` 自指纹 + `.hash-anchor.jsonl` 外部锚点提供篡改可检测的外部参照。变更管理必须**自动重算并更新**这些锚点，而不是让用户手动改 hash（人工手动改 hash 会造成不可追溯）。

### 2.3 不可变原则的例外

唯一例外是**受控变更**：通过本文件 §三 的流程，将受影响产物显式置为 `superseded`（或留痕回退 `draft`），再重新走确认。任何直接修改 confirmed 产物内容而不走流程的行为，都会被 `branch_validator` 以 CRITICAL 拦截。

---

## 三、变更流程

### 3.1 变更类型与触发

| 类型 | 触发场景 | 变更管理落点 |
|---|---|---|
| 业务需求变更 | 改版 / CR（在既有版本上增量变更） | 受控变更流程（§三） |
| 缺陷修复 | 下游分析暴露上游缺陷，需修正已 confirmed 产物 | 变更流程 + 留痕 + 锚点重算 |
| 上游输入更新 | 上游材料 / 事实更新，影响已确认基线 | — |
| 范围变更 | `product-ux` confirmed 后新增 / 修改范围 | `governance.md` Change Control |

### 3.2 变更流程总览

```text
① 提出变更（创建 CHG-NNN 提案）
   ↓
② 评估影响（识别最早受影响 work_item + downstream impact 级联失效）
   ↓
③ 审批（reviewer 角色在提案 §6 审批表给出 approved / CONDITIONS）
   ↓
④ 记录（archive.py 生成 change-record-CHG-NNN.md，写入 99-review/）
   ↓
⑤ 更新下游（reflow --apply 将受影响 confirmed 产物翻转 superseded）
   ↓
⑥ 重新评审（从最早受影响 work_item 重跑，重新走 human gate 确认）
```

### 3.3 分步说明

**① 提出变更**
- 在 `99-review/changes/CHG-NNN/` 创建变更提案，使用 `src/shared/change-management/proposal-template.md` 模板。
- `proposed_by` 填真实人名（对应 RACI 中 business_owner 为业务变更提出方）。
- 用 `src/shared/change-management/change-validator.py` 校验提案完整性（必填章节 / 变更内容非空 / 受影响产物在 registry / 下游级联 / 审批角色）。

**② 评估影响（downstream impact）**
- 识别**最早受影响 work_item**（`earliest_affected_work_item`），这是变更回流的起点。
- 列出受影响产物清单（ADDED / MODIFIED / REMOVED）与**下游级联失效**清单。
- 依据：`src/framework/workflow-registry.json` `dependency_policy.cascade_invalidation`（上游 superseded → 下游 confirmed 一并失效）。

**③ 审批（reviewer 角色）**
- 提案 §6 审批表由 `business_owner` / `product_owner`（approver 角色）给出 `approved` / `CONDITIONS`。
- 审批角色必须与受影响 work_item 的 registry `reviewer_roles` 匹配（`change-validator.py` 校验）。
- 未完全批准前，`archive.py` 拒绝归档（`validate_approved()`）。

**④ 记录（change-*.md）**
- 批准后，`src/shared/change-management/archive.py` 生成 `99-review/change-record-CHG-NNN.md`（ChangeRecord），含审批摘要 / 归档时间 / 下游级联 / 解决清单。
- 同时登记 `DecisionRecord`（DEC-NNN，decider 必须是人）。
- 本文件 §六 提供统一的 change-record 模板（from_status / to_status / reason / changed_at / changed_by / downstream_impact）。
- 同时通过 `audit_log.append_event` 写入 `change` 类型事件到 `requirements/REQ-NNN-*/.audit/events.jsonl`，`payload` 指向 ChangeRecord 路径，`payload_sha256` 绑定 ChangeRecord 正文（任何对 ChangeRecord 的事后篡改都会在 `audit_log.verify_chain` 时被检测到）。

**⑤ 更新下游**
- 用 `pipeline.py reflow --apply` 将受影响下游 confirmed 产物翻转 `superseded`，并生成 `change-record-reflow-*.md`。
- 对需回退重写的产物，按 §四 状态跃迁规则留痕回退 `draft`。

**⑥ 重新评审**
- 从最早受影响 work_item 重跑（`reflow-record.md` 记录 rerun_order）。
- 重新走机器闸门 + 人工确认（`review --decision approve`），直至 `workflow_valid=true`、`complete=true`。

---

## 四、状态跃迁规则

### 4.1 合法 / 非法跃迁表

| from_status | to_status | 合法性 | 条件 / 留痕要求 |
|---|---|---|---|
| `draft` | `ready_for_human_review` | ✅ | AI 完成起草，机器闸门通过 |
| `ready_for_human_review` | `confirmed` | ✅ | reviewer 命中授权清单 + 角色匹配 + 机器闸门通过 |
| `confirmed` | `draft` | ⚠️ **受控** | **必须留痕 + reason**（禁止静默回退） |
| `confirmed` | `superseded` | ⚠️ **受控** | **必须 superseded_reason**（reflow 时记录） |
| `superseded` | `ready_for_human_review` | ✅ | 重跑后重新送审 |
| `simulated` | `ready_for_human_review` | ✅ | 测试线转正式候选（`docs/状态语义矩阵.md` §四 路径） |
| `simulated` | `confirmed` | ❌ | 不存在此路径（`pipeline.py review` 拒绝 simulated） |

### 4.2 关键规则

1. **`confirmed → draft` 必须留痕 + reason**：现状 `pipeline.py --decision changes` 仅对 approve 路径校验 `current_status`，对 revert 路径无审批 / 留痕要求，已 confirmed 产物可被静默回退为 draft。**变更管理要求**：所有 `* → draft` 逆向跃迁必须记录 `modification-record.md`（`src/shared/human-gate/revision-templates/modification-record.md`）或 ChangeRecord，含 reason / changed_by / changed_at。
2. **`confirmed → superseded` 必须 superseded_reason**：reflow 翻转时在 `change-record-reflow-*.md` 记录触发原因与受影响清单。
3. **不可变基线保护**：任何对 confirmed 产物的内容修改，若未先走变更流程（未先置 superseded / 留痕回退 draft），`branch_validator` 报 CRITICAL 阻断。
4. **事件先于状态**（Harness 借鉴点一·事件溯源）：每次状态跃迁必须**先** `audit_log.append_event` 落事件（type ∈ `{change, confirm, reject, reflow}`，`payload` 指向对应 ChangeRecord / ReviewRecord 路径，`payload_sha256` 绑定记录体），**再**改写 frontmatter `status` 字段。事件日志先于状态变更，保证 `.audit/events.jsonl` 始终可 replay 出完整因果链；若顺序倒置（先改状态后落事件），中途崩溃会留下「状态已变但无事件」的不可追溯窗口。`projection_cache` 随后折叠派生 `.audit/projection.json` 作为下游 validator 的统一读取入口。

### 4.3 逆向跃迁留痕与锚点重算要求

| 关注点 | 现状 | 变更管理衔接 |
|---|---|---|
| **`--decision changes` 静默回退** | `pipeline.py:204` 对 revert 路径无留痕要求 | 变更管理要求所有逆向跃迁留痕（modification-record / ChangeRecord + reason）；建议 `pipeline.py` 的 `changes` 决策补充留痕校验 |
| **hash 链外部锚点** | `record_sha256` 自指纹 + `.hash-anchor.jsonl` 锚点链 | 变更后必须**自动重算**受影响产物的 `artifact_content_sha256` 并更新对应 ReviewRecord 与锚点（`change-validator.py --apply` 模式），杜绝人工改 hash 造成不可追溯 |
| **自动化变更管理路径** | `src/shared/change-management/` 有 proposal-template / change-validator / archive，但缺「已确认产物修正 → 自动重算并更新 ReviewRecord hash」闭环 | 建议新增 `change-validator.py --apply` 模式：接受变更提案 → 校验 → 重算目标产物 hash → 自动更新对应 ReviewRecord 并留痕（写入 modification-record） |

---

## 五、与现有 change-management 模块的衔接

| 现有模块 | 位置 | 在变更流程中的角色 |
|---|---|---|
| `proposal-template.md` | `src/shared/change-management/proposal-template.md` | 变更提案模板（CHG-NNN） |
| `change-validator.py` | `src/shared/change-management/change-validator.py` | 提案提交前校验（必填章节 / 变更内容 / 受影响产物 / 级联 / 审批角色） |
| `archive.py` | `src/shared/change-management/archive.py` | 批准后归档：生成 ChangeRecord + 标记 archived |
| `reflow-record.md` | `src/shared/change-management/reflow-templates/reflow-record.md` | 选择性回流记录（earliest_affected_work_item / rerun_order） |
| `modification-record.md` | `src/shared/human-gate/revision-templates/modification-record.md` | 修正记录（ADDED / MODIFIED / REMOVED + 下游影响） |
| `README.md` | `src/shared/change-management/README.md` | 变更与选择性回流的原则声明 |

> **改版 / CR 的衔接**：改版 / CR 场景（baseline + delta 建模）通过本变更流程表达——既有版本为 baseline（已 confirmed），改版 / CR 为 delta（CHG-NNN 提案 + 受影响产物 superseded + 重新确认）。发布节奏与改版 / CR 的关系在提案 §1 动机中登记，不再只能靠 Q-001 挂起待确认。

---

## 六、change-record 模板

> 统一变更记录模板，字段覆盖状态跃迁与下游影响。落点：`99-review/change-record-CHG-NNN.md`（归档生成）或 `99-review/change-record-reflow-*.md`（reflow 生成）。

```markdown
---
record_id: REC-CHG-{NNN}
type: ChangeRecord
proposal_id: CHG-{NNN}
from_status: {confirmed | ready_for_human_review | ...}
to_status: {draft | superseded | ...}
reason: {变更原因摘要}
changed_at: {YYYY-MM-DDTHH:MM:SSZ}
changed_by: {真实人名}
downstream_impact: [{受影响下游产物 ID 列表}]
---

# Change Record: CHG-{NNN}

## 1. 状态跃迁

| 字段 | 值 |
|---|---|
| from_status | {变更前状态} |
| to_status | {变更后状态} |
| reason | {变更原因，必须填写} |
| changed_at | {变更时间} |
| changed_by | {变更发起人 / 审批人} |

## 2. 变更内容

| Change | Target | Before | After | Reason/Source |
|---|---|---|---|---|
| ADDED / MODIFIED / REMOVED | {产物 / 章节 / 字段} | {旧内容摘要} | {新内容摘要} | {来源 / 理由} |

## 3. 下游影响（downstream impact）

| 受影响产物 | 当前状态 | 变更后状态 | 需重跑 |
|---|---|---|---|
| {下游 artifact} | confirmed | superseded | ✅ |
| ... | ... | ... | ... |

## 4. 审批摘要

- business_owner: **approved** by {人名} at {时间}
- product_owner: **approved** by {人名} at {时间}

## 5. 解决清单

- [ ] 受影响产物已置 superseded / 留痕回退 draft
- [ ] ReviewRecord hash 与锚点已自动重算更新（`change-validator.py --apply`）
- [ ] 从最早受影响 work_item 重跑并重新确认
- [ ] 重新评审后 workflow_valid=true、complete=true
```

### 6.1 字段说明

| 字段 | 必填 | 说明 |
|---|---|---|
| `from_status` | ✅ | 变更前状态（如 `confirmed`） |
| `to_status` | ✅ | 变更后状态（如 `draft` / `superseded`） |
| `reason` | ✅ | 变更原因，**禁止为空**（留痕要求） |
| `changed_at` | ✅ | 变更时间（ISO 时间戳） |
| `changed_by` | ✅ | 变更发起人 / 审批人（真实人名，非 AI） |
| `downstream_impact` | ✅ | 下游级联失效清单（`branch_validator` 对 change/reflow 记录强制检查「downstream/下游/影响」关键词） |

---

## 七、边界与例外

1. **变更 ≠ 直接改文件**：任何对 confirmed 产物的内容修改，必须先走变更流程（§三），否则 `branch_validator` CRITICAL 阻断。
2. **`--decision changes` 的现状缺口**：当前 `pipeline.py` 的 `changes` 决策可静默回退 confirmed → draft，本文档要求该路径补留痕；在实现落地前，人工应通过变更流程（提案 + 记录）执行回退。
3. **历史记录兼容**：`record_sha256` 与外部锚点引入后，旧 ReviewRecord 缺 `record_created_at` / `record_sha256` 仅报非阻断 HIGH，不阻断 gate；变更管理对旧记录不强制补锚点，但新变更必须走完整锚点流程。
4. **测试线不受影响**：`simulated` 产物不进入正式交付，不适用变更管理；测试线转正式按 `docs/状态语义矩阵.md` §四 路径。

---

## 八、维护与更新

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.1 | 2026-08-14 | 首版变更管理机制，沉淀自 `src/shared/change-management/`、`docs/状态语义矩阵.md` 与既有代码行为 |

---

## 附：证据文件索引

| 证据 | 位置 |
|---|---|
| 不可变原则 / Confirmation Invariant | `src/framework/contracts.md` |
| Change Control / 范围冻结 | `src/framework/governance.md` |
| 状态语义（confirmed / superseded / simulated） | `docs/状态语义矩阵.md` |
| 变更提案模板 | `src/shared/change-management/proposal-template.md` |
| 提案校验 | `src/shared/change-management/change-validator.py` |
| 归档 / ChangeRecord 生成 | `src/shared/change-management/archive.py` |
| 回流记录模板 | `src/shared/change-management/reflow-templates/reflow-record.md` |
| 修正记录模板 | `src/shared/human-gate/revision-templates/modification-record.md` |
| reflow / --decision changes / review | `src/scripts/pipeline.py` |
| confirmed hash 校验 / 锚点校验 | `src/scripts/branch_validator.py` |
| record_sha256 / .hash-anchor.jsonl | `src/scripts/hash_anchor.py` |
| 事件溯源链（change/confirm/reflow 生命周期单一事实来源） | `src/scripts/audit_log.py`（`.audit/events.jsonl` append-only + prev_hash 链 + event_sha256 自指纹 + payload_sha256 绑定记录体） |
| 投影缓存（latest status / hash 派生视图，validators 统一读取入口） | `src/scripts/projection_cache.py`（`.audit/projection.json`，自动重建，老案例带 warning fallback） |
| 注册表契约硬化（schema + 模板↔校验器闭环，防契约漂移，变更后必跑） | `src/scripts/registry_contract_check.py`（`run_tests_mac.sh` Phase 0 首项 fail-loud） |
| 校验器统一错误格式（make_issue 8+ 字段，变更校验结果统一形态） | `src/scripts/validation_errors.py` |
