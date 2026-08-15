---
artifact_id: frontmatter-schema
version: v0.1
status: confirmed
created_at: 2026-08-12
updated_at: 2026-08-12
confirmed_at: 2026-08-12
---

# Artifact Frontmatter Schema · 产物元数据规范

> **目的**：统一所有 `src/templates/` 下产物模板的 frontmatter 字段，让 `validate_artifact.py` 可稳定解析，让多 Skill 产物可被 `prd-assembly` 无缝组装。
> **适用**：所有在 `src/templates/stage-1-business/`、`stage-2-product/`、`stage-3-prd/` 下的产物模板，以及对应的实际产物文件。

---

## 1. 核心 10 字段（主产物必填）

下表是 `validate_artifact.py` 当前识别的标准字段。任何 `status: confirmed` 的产物必须全部填写；`status: draft` 等中间态可保留空字符串，但字段名必须存在。

| # | 字段 | 类型 | 必填（confirmed） | 用途 | 示例 |
|---|---|---|---|---|---|
| 1 | `artifact_id` | string | ✅ | 全局唯一产物 ID | `BG-<example>-v1` |
| 2 | `version` | semver | ✅ | 语义化版本 | `v0.1` |
| 3 | `status` | enum | ✅ | 见 §2 状态枚举 | `draft` |
| 4 | `owner` | string | ✅ | 产物负责人 | `产品经理姓名` |
| 5 | `business_fact_owner` | string | ✅ | 业务事实负责人 | `业务方代表 A` |
| 6 | `goal_decision_owner` | string | ✅ | 目标/决策负责人 | `业务方负责人 B` |
| 7 | `reviewer` | string | ✅ | 授权人工 review 人 | `项目 PMO` |
| 8 | `created_at` | ISO date | ✅ | 首次创建日期 | `2026-08-12` |
| 9 | `updated_at` | ISO date | ✅ | 最后更新日期 | `2026-08-12` |
| 10 | `confirmed_at` | ISO date | ✅（仅 confirmed） | 人工确认日期 | `2026-08-12` |

**校验位置**：`src/stages/*/skills/*/scripts/validate_artifact.py` 的 `REQUIRED_FRONTMATTER` 常量。

---

## 2. status 字段枚举

按"由松到严"排列，AI 不得跨越中间态直接设为 `confirmed`：

| 状态 | 含义 | 谁可设置 |
|---|---|---|
| `draft` | AI 起草中 | AI |
| `needs_user_input` | 缺失关键信息，需用户补充 | AI |
| `conditional_review` | 有条件地可被审阅 | AI |
| `ready_for_human_review` | 形成候选，等待人工 review | AI |
| `confirmed` | 人工已确认 | **仅人工** |
| `superseded` | 被新版本替代 | 人工 |
| `legacy_unverified` | 旧版本未重新校验 | 人工 |
| `simulated` | 用于测试或演示的模拟产物 | 人工（仅测试） |

**关键约束**：`confirmed` 状态只能由人工设置，AI 必须停留在 `ready_for_human_review`。

---

## 3. 扩展字段（按产物类型可选）

| 字段 | 适用产物 | 用途 |
|---|---|---|
| `upstream_artifact_ids` | `prd.md` | 上游产物 ID 列表，用于 RTM 追溯 |
| `variant` | `prd-executive.md` / `prd-technical.md` | 变体类型，取值 `executive` / `technical` |
| `source_prd` | `prd-executive.md` / `prd-technical.md` | 源标准 PRD 的 artifact_id |

---

## 4. frontmatter 在文档中的位置

- 必须位于 Markdown 文件最顶端
- 紧跟在 HTML 注释（`<!-- -->`）之后
- 字段顺序按 §1 表格顺序排列
- 数组字段用 YAML 列表语法：`upstream_artifact_ids: ["BG-XXX", "JS-XXX"]`
- 字符串字段值建议加双引号：`artifact_id: "BG-<example>-v1"`

**示例**：
```yaml
---
artifact_id: "BG-<example>-v1"
version: "v0.1"
status: "ready_for_human_review"
owner: "产品经理姓名"
business_fact_owner: "业务方代表 A"
goal_decision_owner: "业务方负责人 B"
reviewer: "项目 PMO"
created_at: "2026-08-12"
updated_at: "2026-08-12"
confirmed_at: ""
---
```

---

## 5. 与下游消费者的接口

- **`validate_artifact.py`**：按 `REQUIRED_FRONTMATTER` 严格校验，缺字段直接 fail
- **`orchestrator.py`**：读 `status` 字段决定是否进入下一阶段
- **`prd-assembly`**：读 `upstream_artifact_ids` 拼装 RTM
- **`branch_validator.py`**：读 `owner` / `reviewer` 决定分支门禁
- **人工 review**：`confirmed_at` 是唯一可信信号，AI 不得伪造

---

## 6. 修改记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.1 | 2026-08-12 | 首版规范，沉淀自 5 主 Skill + 1 PRD 的实际 frontmatter 实践 |
