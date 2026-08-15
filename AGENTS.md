# PM Scaffold · 产品 AI 脚手架 — Agent 唯一入口

> 任何 AI 执行体（Claude Code / Codex / Cursor / Copilot / 其他）进入本项目的**第一份必读文件**。
> 读完本文件后，按「启动顺序」依次读框架文件，再开始工作。不要跳过、不要先读别的。

---

## 1. 定位与边界

这是 **PRD-only 产品经理 AI 脚手架**：把原始需求材料（BRD、会议纪要、邮件、PPT、图片）逐步转化为一份**经真实人工确认、可沟通、可实现、可核验的中文 `prd.md`**。

- ✅ 我做：需求采集 → 业务需求 → 产品需求 → PRD 汇总 → 人工确认。
- ❌ 我不做：研发任务拆分、技术架构设计、测试用例、用户手册、API 合约。唯一交付物是 `prd.md`。

三条硬哲学：**业务真相由人类拥有**、**证据与不确定性必须可见**、**AI 不得伪造人工确认**。

---

## 0. 首次接触人类用户（必做）

当人类用户第一次接触本项目（问「这是什么 / 怎么用 / 从哪开始」）时，按顺序：

1. **先打开驾驶舱给他们看**：`open src/toolkit/visualization/scaffold-flow.html`（浏览器打开）——里面是项目流程图、19 Skill 说明书、命令全集、文件架构。
2. **引导点左侧「📖 新手教程 · 从这里开始」**——那是给人类看的协作手册（用什么 Agent、怎么下指令、从零到 PRD 的完整剧本）。这是硬核项目、没有外部生态，这个 HTML 是唯一的入门门面。
3. **本文件是你的工作合同，不要直接甩给用户读**——用户需要的是「怎么用」，不是「你的规则」。等用户看完教程、按他们的指令开始协作后，你按本文件 §2-§8 执行。

---

## 2. 启动顺序（严格按序，共 5 个文件）

| 顺序 | 文件 | 作用 |
|---|---|---|
| 1 | `src/framework/workflow-registry.json` | 阶段 / Skill / 产物的**唯一机器真相源**，一切路径以此为准，不要硬编码 |
| 2 | `src/framework/constitution.md` | 8 条硬宪法，违反任何一条 = 缺陷 |
| 3 | `src/framework/workflow.md` | 每个 Work Item 必走的 8 步循环 |
| 4 | `src/framework/thinking-core.md` | 17 个思考透镜，§1 的 6 个核心透镜每次必用 |
| 5 | `src/framework/contracts.md` | 知识状态标注 + 确认不变式；含 AuditEvent / ProjectionCache / ValidatorIssue / RegistryContract 等扩展 Shared Records 契约（v0.4.0 Harness 借鉴） |

之后读当前需求的 `STAGE.md` 和对应 Skill 的 `SKILL.md`。

---

## 3. 硬红线（违反即缺陷）

1. **`confirmed` 永远不能由 AI 设置**——只有 `pipeline.py review --decision approve`（带真实人名 + 授权清单匹配）才能产生。`--yes` 只能跑机器检查。
2. **上游未 confirmed，下游不启动**——`orchestrator` 会检测越级并阻止。
3. **PRD assembly 只聚合、不发明**——发现缺口路由回最早的 Work Item 重来。
4. **知识状态必须标注**——每条声明标 `FACT / DECISION / ASSUMPTION / AI_INFERENCE / UNKNOWN / CONFLICT`，不得把推断当事实、忽略冲突、漏掉未知。
5. **产物单点存放**——一个 artifact 一个位置，版本演进用 v0.* 快照，不在别处复制。
6. **变更已确认内容使下游失效**——回归到最早受影响的 Work Item 重跑。
7. **注册表是唯一真相源**——不要硬编码路径 / 阶段名 / Skill 名。
8. **事件日志不可篡改 + 校验器统一错误格式**（v0.4.0 硬宪法第 7/8 条）—— `.audit/events.jsonl` 是 append-only 单一事实来源；`prev_hash` 链断 / `event_sha256` 自指纹不符 / `payload_sha256` 不绑定记录体即 CRITICAL，由 `audit_log.verify_chain` 检测；所有校验器必须用 `validation_errors.make_issue` 输出统一错误格式（8+ 字段：severity / blocking / check_id / check_family / location / field_path / message / expectation / actual / repair_hint / source_ref），禁止裸 stack trace。`registry_contract_check.py` 作为 `run_tests_mac.sh` 首项 fail-loud 关卡，任何 skill 新增/修改必须通过。

---

## 4. 执行循环（每个 Work Item 必走一遍）

```text
Preflight → Intake → Think → Clarify → Generate → Audit → Human Gate → Commit / Reflow
```

- **Clarify**（提问澄清）、**Reflow**（回流重做）是当前 Work Item 内部状态，不是独立主干。
- **Human Gate 不可绕过**：机器检查只能产出 `ready_for_human_review`，永远不能产出 `confirmed`。
- 产物状态机：`draft → needs_user_input / conditional_review / ready_for_human_review → confirmed`（`superseded` / `simulated` 为特殊态）。

---

## 5. 需求目录布局

```text
requirements/REQ-NNN-topic/
├── README.md
├── 00-input/                      # 原始材料 + authorized-reviewers.json
├── 001-business-requirements/
│   ├── 01-background-goal/
│   └── 02-user-journey-stories/
├── 002-product-requirements/
│   ├── 01-product-ux/
│   └── 02-function-description/
├── 003-prd-output/prd.md          # 唯一最终交付物
└── 99-review/                     # 评审记录 + support/issue-record.md（B3 收口）
```

一个 artifact 原地演进；快照与评审/变更记录保存历史，不创建竞争的「最终版」副本。

**入口探索序列**（进入 project-background-goal 前）：`entry` 判定 L0-L4（内容六信号）→ L0 先 `requirement-restate`（需求重举·发散模式）→ 多源/歧义时（需求重举·复述模式）→ 主干 bg（DoR 硬检查 ≥1 个 SRC 材料）。

**B3 每阶段强制收口**：任何 work item 送审 `ready_for_human_review` 前，`99-review/support/issue-record.md` 必须存在且 §13 收口表含该 work item 行（空阶段也落行）；产物每个「待确认」必须带 Q-/ISS-/DEC-/SRC- 引用。dor_check 硬检查，缺失即阻断送审。

---

## 6. 常用命令

```bash
# 1. 创建新需求骨架
python3 src/scripts/pipeline.py init REQ-005-topic-name

# 2. 把输入材料放进 requirements/REQ-005-topic-name/00-input/

# 3. 查状态（active_work_item / next_work_item / 越级检测）
python3 src/scripts/pipeline.py requirements/REQ-005-topic-name status

# 4. 跑机器闸门（不改状态，只校验）
python3 src/scripts/pipeline.py requirements/REQ-005-topic-name gate \
  --work-item project-background-goal

# 5. 人工确认（只有人，带真实姓名 + 角色；--reviewer-id 需与 00-input/authorized-reviewers.json 一致）
python3 src/scripts/pipeline.py requirements/REQ-005-topic-name review \
  --work-item project-background-goal --decision approve \
  --reviewer "评审人姓名" --reviewer-id "飞书或组织稳定用户ID" \
  --reviewer-role "business_owner"

# 6. 变更回流预览 / 应用级联失效
python3 src/scripts/pipeline.py requirements/REQ-005-topic-name reflow --work-item project-background-goal
python3 src/scripts/pipeline.py requirements/REQ-005-topic-name reflow --work-item project-background-goal --apply

# 7. 全量自检
bash run_tests_mac.sh
python3 src/scripts/consistency_check.py
```

人工批准前需在 `00-input/authorized-reviewers.json` 登记 reviewer 的 id、姓名与允许角色；本地校验不替代未来的飞书/SSO 身份认证。

---

## 7. Skill 全景（5 主 + 9 子 + 4 分支 + 1 能力 = 19）

**主 skill（5，主干必做，永不询问）**
`project-background-goal` → `user-journey-and-stories` → `product-ux` → `function-description` → `prd-assembly`

**子 skill（9，挂到父 skill 的产物章节）**
`product-ux` 内：`page-design` / `interaction-rules`
`function-description` 内：`feature-list` / `functional-flow` / `business-rules` / `validation-rules` / `state-machine` / `exception-handling` / `acceptance-criteria`

**分支/条件 skill（4 产物 + 1 能力，触发才跑）**
`competitive-research`（竞品调研）、`feasibility-analysis`（可行性分析）、`tracking-plan`（埋点计划）、`issue-record`（问题清单）——另 `requirement-restate`（需求重举能力：复述+发散，过程记录）

每个 skill 的权威行为见各自的 `SKILL.md`（含 8 步 Thinking Prompts、Anti-Patterns、示例、Load References、Completion 清单）。

---

## 8. 需要停下来问人（不要自己猜）

- 信息不足无法合理判断 → 标 `needs_user_input`，列出缺失信息。
- 两个来源说法矛盾 → 标 `CONFLICT`，列出冲突点。
- 业务决策（非技术选择）→ 标 `DECISION`，给出选项与推荐。
- 不确定声明是事实还是假设 → 标 `AI_INFERENCE`。

---

## 9. 关键目录地图

```text
src/framework/       宪法、契约、思考核心、注册表（先读这里）
src/stages/          3 阶段 × 5 主 skill + 9 子 skill
src/shared/          9 个共享机制（审计/澄清/变更/闸门/追溯等）
src/support-skills/  5 support capabilities：competitive-research / feasibility-analysis 在此；requirement-restate / tracking-plan 在 stages；issue-record 在 shared/clarify
src/scripts/         pipeline / orchestrator / dor_check / branch_validator / audit_log / projection_cache / registry_contract_check / validation_errors（后四项为 v0.4.0 Harness 借鉴基础设施）
src/templates/       18 个产物模板 + resolver
src/toolkit/         工具使用指南（Figma / Mermaid / lark-cli）
test/                回归测试（fixtures + 单元/集成测试）
requirements/        需求实例（运行时生成，gitignore）
```

更多：人类视角读 `README.md`；打包安装读 `skills/pm-scaffold/SKILL.md`。
