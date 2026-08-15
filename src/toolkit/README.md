# 工具体系

PM 操作手册和工具集成文档，不是 Skill。AI Agent 不读这里，这是给人看的。

| 目录 | 内容 |
|---|---|
| `input/` | 需求接入工具（邮件/飞书/JIRA/Slack MCP） |
| `analysis/` | 分析处理工具（调研/数据处理/框架化分析） |
| `visualization/` | 可视化工具（Mermaid/Excalidraw/Figma/飞书画板） |
| `output/` | 输出导出工具（飞书同步/PDF/PPT/邮件） |
| `communication/` | 沟通协作工具（lark-cli/飞书消息/日历/任务） |
| `research/` | 研究调研工具（WebSearch/Brave/Firecrawl） |
| `quality/` | 质量保障工具（校验脚本/回归测试） |
| `automation/` | 自动化工具（定时任务/工作流编排） |

核心文件：
- `TOOLKIT.md` — 工具注册总表
- `WORKFLOWS.md` — 10 种 PM 场景 × 工具链速查
- `RECOMMENDED.md` — 推荐安装清单

## 原型自测（可选，不强制）

page-design 生成的可点击 HTML 原型（`prototype/index.html`）交付评审前，可做一次轻量交互冒烟，思路参考 webapp-testing 的 Playwright 冒烟：

- **主流程点击通**：从入口页沿主流程逐页点击，断言关键 CTA 能到达预期目标页——无死链、无空白页。
- **分支态可达**：对状态依赖弹窗逐个选择分支状态，断言对应目标页可达（如「已关注 / 未关注」两条路径都能进）。
- **做法**：静态原型 HTML 可直接以 `file://` 打开跑脚本；动态渲染内容需先等待加载完成（`networkidle`）再取选择器。项目不引入 npm/外部依赖——环境已有 Playwright 则复用，否则以人工点检代替，并用浏览器渲染截图佐证。
- 自测结果是 `render-check.png` 的补充证据，不替代人工评审确认。
