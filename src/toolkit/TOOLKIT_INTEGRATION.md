# 外部 Skill 工具链集成清单

> 本文档定义 PM Scaffold 脚手架如何调用外部 Claude Code Skill 来增强原型、设计、旅程和战略能力。
> 这些是"可插拔"的外部能力——脚手架注册表不管理它们，但 AI 执行体在特定阶段应主动调用。

## 集成架构

```text
PM Scaffold 脚手架 (注册表驱动，PRD-only)
│
├── Stage 1: 业务需求 ────────────────────────────────────
│   ├── project-background-goal
│   │   └── 🔌 requirements-gathering (干系人发现 + MoSCoW)
│   └── user-journey-and-stories
│       └── 🔌 user-journeys (情感旅程 + 痛点上色 + Playwright 验证)
│
├── Stage 2: 产品需求 ────────────────────────────────────
│   ├── product-ux
│   │   ├── 🔌 flow2demo (流程→交互文档+可视化板)
│   │   ├── 🔌 interactive-demo-factory (可点击原型工厂)
│   │   ├── 🔌 pm-phase-4.5-prototype (确认页面清单→HTML原型)
│   │   ├── 🔌 image2html (截图→HTML重建，高保真模式)
│   │   ├── 🔌 frontend-design (让原型看起来有设计感)
│   │   └── 🔌 impeccable (原型设计审计+打磨)
│   └── function-description
│       └── 🔌 prd-writer (IR/BR 规范 + 分支覆盖)
│
├── Stage 3: PRD 输出 ────────────────────────────────────
│   └── prd-assembly
│       ├── 🔌 theme-factory (PRD HTML 品牌主题)
│       ├── 🔌 impeccable (/typeset + /arrange PRD页面)
│       └── 🔌 dataviz (PRD 内嵌指标图表)
│
└── 跨阶段 ──────────────────────────────────────────────
    ├── 🔌 agile-pm-workflow (整体编排参考——7步对话式工作流)
    ├── 🔌 prd (PRD 质量标杆——模糊语言零容忍标准)
    └── 🔌 product-management (战略工具箱——RICE/ICE/WSJF 优先框架 + PMF 度量)
```

## 各 Skill 调用时机与契约

### `agile-pm-workflow` — 编排参考（不直接调用）
- **借鉴什么**: 7 步对话式工作流、7 维度需求评估、3 轮深度追问、iframe 沙盒切片 PRD 格式
- **脚手架对应**: `AI.md` 启动协议 = 其 Step 1 结构化版；我们的 pipeline 8 步循环 = 其 Step 2-7 注册表化版
- **不直接调用的原因**: 脚手架有自己的注册表驱动编排，但它的 iframe 切片 PRD 格式可直接作为 prd-assembly 的输出参考

### `requirements-gathering` — Stage 1 前置
- **调用时机**: project-background-goal 的 Intake 阶段，当输入材料稀疏或干系人不明确时
- **输入**: 原始需求材料
- **输出**: 干系人清单、MoSCoW 优先级草案、需求验证清单
- **注意**: 其 StakeholderDiscovery 的 7 类干系人可作为 persona profiling 模板

### `user-journeys` — Stage 1 WI2 增强
- **调用时机**: user-journey-and-stories 的 Think Phase C（情感映射）时
- **输入**: 已确认的角色 + 生命周期阶段
- **输出**: 情感弧线、痛点上色、错误恢复路径
- **借鉴**: 其 `critical/common/edge-cases` 三级旅程分类可直接映射到脚手架路径类型覆盖

### `pm-phase-4.5-prototype` — Stage 2 WI1 原型生成
- **调用时机**: product-ux 的 Generate Phase C（页面骨架）完成后
- **输入**: 用户故事文档 + 功能设计文档 (FEA + IX)
- **输出**: 页面清单确认表 → 单一 HTML 交互原型（覆盖主流程+所有分支）
- **脚手架集成点**: 作为 page-design 子 Skill 的高保真输出选项

### `interactive-demo-factory` — Stage 2 WI1 高保真原型
- **调用时机**: 需要可演示的 clickable demo（含微信小程序模拟）时
- **输入**: 页面清单 + 流程描述 + UI 截图（可选）
- **输出**: 单文件 `demo.html` + `demo.md`，支持 `?page=N` URL 路由
- **独特价值**: CHANEL 品牌 tokens.css、微信胶囊/状态栏模拟、Demo Console 状态切换

### `flow2demo` — Stage 2 WI1 交互文档
- **调用时机**: 需要从流程+截图生成结构化交互文档时
- **输入**: 流程描述 + 页面截图
- **输出**: 交互 Markdown 文档 + 可视化交互板 + HTML demo
- **独特价值**: 多入口点 + 状态依赖页面的"状态确认弹窗"模式

### `image2html` — Stage 2 WI1 截图→HTML
- **调用时机**: 有 UI 截图需要转化为真实 HTML（非整页背景图）时
- **输入**: UI 截图
- **输出**: 结构化 HTML/CSS（真实 DOM，可维护）
- **注意**: flow2demo 和 interactive-demo-factory 高保真模式会主动调用此 skill

### `frontend-design` — Stage 2 WI1 设计质量
- **调用时机**: 原型 HTML 生成后，需要"让它看起来像设计过的"而非 AI slop 时
- **输入**: 裸 HTML 原型
- **输出**: 有设计感的 HTML（字体/颜色/间距/动效）
- **反模式防护**: 明确禁止 Inter/Roboto 字体、紫色渐变、cookie-cutter 布局

### `impeccable` — Stage 3 设计打磨
- **调用时机**: PRD HTML 输出前，需要设计审计和打磨时
- **子命令**: `/typeset` (排版), `/arrange` (布局), `/colorize` (配色), `/audit` (审计)
- **注意**: agile-pm-workflow Step 4.2/6.1 已示范调用方式

### `prd-writer` — Stage 2 WI2 IR/BR 规范
- **调用时机**: function-description 写交互规则和业务规则时
- **输入**: 功能设计文档
- **输出**: 工程就绪的 IR/BR 规范（含 input/output/error codes、分支覆盖、Feishu 同步清单）
- **独特价值**: 其 IR/BR 规范章节可直接作为 function-description 的 detailed-spec 模板

### `dataviz` — Stage 3 图表
- **调用时机**: PRD 包含指标仪表盘或数据可视化时
- **注意**: 内置 Skill（不在磁盘上），需确认目标环境是否可用

### `theme-factory` — Stage 3 品牌
- **调用时机**: PRD HTML 需要统一品牌主题时
- **输出**: 10 个预设主题选一，或按需生成自定义主题

### `product-management` — 跨阶段战略
- **调用时机**: 需要优先框架 (RICE/ICE/WSJF)、路线图、PMF 度量时
- **借鉴**: 其 12+ 模板（OKR、路线图、干系人更新）可作为 references 直接 vendo

## 调用规则

1. **外部 Skill 是增强，不是替代** — 脚手架的核心 pipeline（注册表→SKILL.md→validator→Human Gate）不变。外部 Skill 在特定阶段被调用，但产物仍需通过脚手架的 validator 和 Human Gate。
2. **调用后产物归入对应阶段目录** — 原型 HTML → `02-product-requirements/01-product-ux/`；交互文档 → 同目录
3. **AI_INFERENCE 标记传播** — 外部 Skill 的产出通常标记 AI_INFERENCE，直到人工在 Human Gate 确认
4. **不破坏 confirmed 不变式** — 外部 Skill 不能设置 confirmed 状态

## 已知不可用的 Skill

| Skill | 原因 |
|---|---|
| `pm-skill-prd-to-spec` (目录) | 空目录，无 SKILL.md |
| `pm-skill-prd-to-spec.skill` | 文件不存在 |
| `interactive-demo-factory-workspace` | 空评估工作区，不是可执行 Skill |
