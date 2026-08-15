# Excalidraw 本地白板 · 飞书画板开源等价物

> 107K GitHub Stars | MIT License | 手绘风无限画布 | AI 可编程操作
> MCP Server: `mcp-excalidraw-server` (26 tools) + `@kamiazya/whiteboard-mcp` (协作版)

## 何时用白板（使用原则）

本地白板用于**可视化用户旅程、UX 流程、状态模型或追溯关系**，当评审方要求一块**可编辑画布**时使用。它是**可选的渲染工具**：
- **不是 Skill**，**不是工作流停点**——用不用它都不阻塞交付流程。
- 节点标签**绑定产物 ID**（ST-XXX / FEA-XXX / FUN-XXX），保持可追溯。
- **源 Markdown / 源表格是权威**，白板只是它的可视化呈现。
- 只有**确认画布渲染正确**后，才导出或同步（到飞书/团队）。

## 和飞书画板的对比

| 能力 | 飞书画板 | Excalidraw (开源) |
|---|---|---|
| 画布类型 | 飞书云文档内嵌 | 浏览器本地 http://127.0.0.1:3000 |
| 编辑方式 | 飞书客户端 | 浏览器 + AI 编程 |
| 协作 | 飞书多人 | WebSocket 实时同步 |
| 导出格式 | 飞书专有 | SVG / PNG / JSON / Mermaid |
| MCP 集成 | lark-cli whiteboard-update | 26 MCP tools (CRUD+布局+截图+导出) |
| 离线可用 | ❌ | ✅ 完全本地 |
| 开源 | ❌ | ✅ MIT |

## 安装 (已完成)

```bash
# MCP Server
claude mcp add excalidraw --scope user -- npx -y mcp-excalidraw-server

# 启动画布
npx -y mcp-excalidraw-server start
# → http://127.0.0.1:3000

# 停止
npx -y mcp-excalidraw-server stop
```

## AI Agent 可用的 26 个工具

| 类别 | 工具 | 说明 |
|---|---|---|
| 元素 CRUD | create_element, update_element, delete_element | 创建/修改/删除矩形/菱形/箭头/文字等 |
| 布局 | align, distribute, group, ungroup | 对齐/分布/编组 |
| 场景感知 | describe (AI 可读文本描述), screenshot | 告诉 AI 画布上有什么 |
| 文件 | export (.excalidraw JSON), import, mermaid_to_canvas | JSON 导入导出 |
| 状态 | snapshot, restore | 快照回滚 |

## 特殊能力: Mermaid → Excalidraw

AI 可以先画 Mermaid 图（文本），然后一键转 Excalidraw 白板：
```
mermaid_to_canvas("graph TD\n  A-->B-->C")
```
→ 白板上出现可编辑的手绘风图

## 和现有工具的分工

| 场景 | 用什么 |
|---|---|
| VS Code 本地预览 | Mermaid (Cmd+Shift+V) |
| 团队实时协作编辑 | Excalidraw (http://127.0.0.1:3000) |
| 飞书云文档同步 | lark-cli whiteboard-update |
| Figma 设计评审 | Figma MCP generate_diagram |
| 零依赖浏览器渲染 | render_mermaid_local.html |
| 批量 Markdown→图 | mermaid-cli (mmdc) |
| Agent 编程操作白板 | Excalidraw MCP (26 tools) |

## 其他开源白板 (备选)

| 工具 | 特点 | 安装 |
|---|---|---|
| **draw.io** | 正式技术图 (UML/网络/架构)，Docker 自托管 | `docker run -p 8080:8080 jgraph/drawio` |
| **tldraw** | 现代几何风白板，42K Stars | `npx tldraw` |
| **@kamiazya/whiteboard** | Excalidraw + 版本控制 + 分支合并 | `npx -y @kamiazya/whiteboard-mcp` |
