# Figma MCP 集成 · PM 常用能力

> Figma Remote MCP 已连接。覆盖设计系统搜索、流程图生成、UI 截图、设计稿→代码。

## PM 高频场景

### 1. 画流程图/架构图 → FigJam
```
使用 generate_diagram：
- 用户旅程图 (journey map)
- 业务流程图 (flowchart)
- 系统架构图 (architecture diagram)
- 时序图 (sequence diagram)
- ER 图 (entity relationship)
- 甘特图 (gantt chart)
- 状态图 (state diagram)
```
直接用 Mermaid 语法描述，自动生成到 FigJam。

### 2. 搜索设计系统组件
```
使用 search_design_system：
在已订阅的 Figma 设计库中搜索 Button/Form/Table/Card 等组件，
获取组件变体、属性、样式 token。
```
用于：原型设计时复用已有组件，避免从零画。

### 3. 设计稿→代码参考
```
使用 get_design_context：
输入 Figma 节点 ID，获取：
- HTML/CSS 参考代码
- 设计变量（颜色、间距、字号）
- 截图
```
用于：开发拿到设计稿后，快速提取设计参数。

### 4. 网页截屏→Figma（竞品分析）
```
使用 generate_figma_design：
输入网页 URL → 自动截屏并转为 Figma 画板。
```
用于：竞品页面布局参考、设计灵感收集。

### 5. 获取设计变量 (Design Tokens)
```
使用 get_variable_defs：
获取 Figma 节点的颜色/间距/字体等变量定义。
```
用于：品牌色提取、设计规范对齐。

### 6. 导出素材
```
使用 download_assets：
导出 Figma 节点的 PNG/SVG 渲染图。
```
用于：PRD 中嵌入设计稿截屏。

## Skill 加载规则

使用 Figma 工具前，需先加载对应 Skill（按需）：
- `/figma-use` — 写 Figma 前
- `/figma-generate-design` — 网页→Figma
- `/figma-generate-library` — 构建设计系统
- 或直接读 MCP 资源 `skill://figma/figma-use/SKILL.md`
