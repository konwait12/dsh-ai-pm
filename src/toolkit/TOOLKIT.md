# PM AI 脚手架 · 内置工具体系

> 本文件是工具注册总表。AI Agent 启动时加载，按需调用。
> 状态：✅ 已内置 | 🔌 可安装 | 🔮 规划中 | 🚫 不适用

---

## 〇、当前环境已有能力（直接可用）

### 内置 Skills（Claude Code 附带）
| Skill | 用途 | PM 场景 |
|---|---|---|
| `frontend-design` | 生产级 HTML/CSS 界面 | 原型生成、交互演示 |
| `canvas-design` | PNG/PDF 静态视觉设计 | 海报、架构图、品牌素材 |
| `dataviz` | 图表、仪表盘、数据可视化 | 竞品数据对比、埋点分析、转化漏斗 |
| `web-artifacts-builder` | React+Tailwind+shadcn 复杂组件 | 交互式 PRD、可点击原型 |
| `webapp-testing` | Playwright 浏览器测试 | 验证原型、截屏对比 |
| `flow2demo` | 页面流程→可交互 HTML Demo | 产品流程演示 |
| `interactive-demo-factory` | ASCII/Mermaid→可点击原型 | 微信小程序/Web 原型 |
| `image2html` | UI 截图→HTML/CSS 复刻 | 参考设计图→原型 |
| `impeccable` | UI 审查、打磨、优化 | 原型质量检查 |
| `theme-factory` | 10 套预设主题 + 自定义 | 品牌化原型、演示配色 |
| `algorithmic-art` | p5.js 生成艺术 | 品牌视觉、数据艺术化 |
| `doc-coauthoring` | 结构化协作文档 | PRD 写作引导 |
| `internal-comms` | 内部沟通文案 | 立项邮件、周报、公告 |

### 内置 MCP（已连接）
| MCP Server | 能力 | PM 场景 |
|---|---|---|
| **Figma Remote** | get_design_context, use_figma, generate_diagram, get_screenshot, search_design_system, download_assets, get_variable_defs, get_libraries, create_new_file, upload_assets | 设计系统搜索、流程图生成、UI 截图对照、设计稿→代码、素材导出 |
| **WebSearch** | 网络搜索 | 竞品调研、行业基线、技术可行性查证 |
| **WebFetch** | URL→Markdown 转换 | 读取外部文档、竞品网站、API 文档 |

### 内置 CLI
| CLI | 用途 | PM 场景 |
|---|---|---|
| **lark-cli** (v1.0.84) | 飞书文档/多维表格/消息/日历/任务 200+ 命令 | 读写飞书文档、同步 PRD、发送通知、管理任务 |
| **Bash** | 完整 Shell | 脚本自动化、文件处理、数据转换 |
| **Git** | 版本控制 | 产物版本管理、变更追溯 |

---

## 一、需求接入层 (Input)

### 邮件
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| Gmail MCP | MCP | 🔌 可安装 | 读取邮件、提取需求、搜索历史往来 |
| Outlook MCP | MCP | 🔌 可安装 | 同上，企业 Microsoft 365 环境 |

### 飞书
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| lark-cli `docs +fetch` | CLI | ✅ 已内置 | 读取飞书文档内容→Markdown |
| lark-cli `im` | CLI | ✅ 已内置 | 读取飞书消息、群聊 |
| lark-cli `sheets` | CLI | ✅ 已内置 | 读取飞书电子表格 |
| lark-cli `base` | CLI | ✅ 已内置 | 读取飞书多维表格 |
| lark-cli `calendar` | CLI | ✅ 已内置 | 读取日历、会议信息 |
| feishu-user-plugin | MCP | 🔌 可安装 | 85 工具，用户身份发消息、读私聊 (GitHub EthanQC) |
| lark-mcp-dm | MCP | 🔌 可安装 | 官方 Lark MCP 快速接入 (GitHub Chranos) |

### 文档
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| PDF 解析 | Skill | 🔮 规划中 | 读取 PDF 中的需求和表格 |
| PPT 解析 | Skill | 🔮 规划中 | 读取 PPT 中的需求描述 |
| Word 解析 | Skill | 🔮 规划中 | 读取 .docx 文档 |
| OCR/图片识别 | MCP | 🔮 规划中 | 白板照片、手写笔记→文字 |
| 音频转文字 | MCP | 🔮 规划中 | 会议录音→逐字稿 |

### 项目管理
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| JIRA MCP | MCP | 🔌 可安装 | 读需求、创建 Story、跟踪状态 |
| Linear MCP | MCP | 🔌 可安装 | 同上，Linear 用户 |
| GitHub Issues MCP | MCP | 🔌 可安装 | Issue 读/写/搜索 |

### 通讯
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| Slack MCP | MCP | 🔌 可安装 | 读消息、搜索历史、发通知 |
| 微信/企微 | MCP | 🔮 规划中 | 国内团队常用 |

---

## 二、分析处理层 (Analysis)

### 调研
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| WebSearch | MCP | ✅ 已内置 | 关键词搜索、竞品查找 |
| WebFetch | MCP | ✅ 已内置 | URL→Markdown，深度阅读网页 |
| Brave Search MCP | MCP | 🔌 可安装 | 更高精度的实时搜索 |
| Firecrawl MCP | MCP | 🔌 可安装 | 深度网页爬取+内容提取 |
| Exa MCP | MCP | 🔌 可安装 | 语义搜索（找相似论点的文章） |
| App Store 评论 | MCP | 🔮 规划中 | 竞品 App 用户反馈分析 |

### 数据处理
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| SQLite MCP | MCP | 🔌 可安装 | 本地数据分析、CSV 导入查询 |
| Python pandas | Script | ✅ 已内置 (Bash+Python) | 数据清洗、统计、透视 |
| Airtable MCP | MCP | 🔌 可安装 | 电子表格+数据库混合 |

### 框架化分析
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| SWOT 分析 | Skill | 🔮 规划中 | 结构化 SWOT 模板 |
| RICE 优先级 | Skill | 🔮 规划中 | Reach/Impact/Confidence/Effort 打分 |
| MoSCoW 分类 | Skill | 🔮 规划中 | Must/Should/Could/Won't 分类 |
| Kano 模型 | Skill | 🔮 规划中 | 功能满意度分析 |
| RACI 矩阵 | Skill | 🔮 规划中 | 角色责任分配 |

---

## 三、可视化层 (Visualization)

### 图表与流程图
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| Figma `generate_diagram` | MCP | ✅ 已内置 | Mermaid→FigJam 流程图/时序图/ERD/甘特图 |
| Figma `use_figma` | MCP | ✅ 已内置 | 在 Figma 中创建任意设计 |
| dataviz Skill | Skill | ✅ 已内置 | 图表/仪表盘/数据可视化 |
| Mermaid (原生) | Markdown | ✅ 已内置 | 流程图、时序图、ERD、甘特图、用户旅程 |

### 原型与UI
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| frontend-design Skill | Skill | ✅ 已内置 | 生产级 HTML/CSS 原型 |
| web-artifacts-builder Skill | Skill | ✅ 已内置 | React 复杂交互原型 |
| interactive-demo-factory Skill | Skill | ✅ 已内置 | 可点击 HTML Demo + 侧边栏 |
| flow2demo Skill | Skill | ✅ 已内置 | 页面流程→交互 Demo |
| image2html Skill | Skill | ✅ 已内置 | UI 截图→HTML/CSS |
| Figma `get_design_context` | MCP | ✅ 已内置 | 设计稿→代码 |
| Figma `get_screenshot` | MCP | ✅ 已内置 | 设计稿截屏 |
| Figma `generate_figma_design` | MCP | ✅ 已内置 | 网页截屏→Figma |
| theme-factory Skill | Skill | ✅ 已内置 | 品牌化主题套用 |
| impeccable Skill | Skill | ✅ 已内置 | UI 审查/打磨 |
| canvas-design Skill | Skill | ✅ 已内置 | 静态视觉设计(海报/品牌) |

### 架构与结构图
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| Figma `generate_diagram` (architecture) | MCP | ✅ 已内置 | 软件架构图、系统拓扑图 |
| feature-list 子 skill | Skill | ✅ 已内置 | FEA 功能清单（功能树状分解） |

---

## 四、输出导出层 (Output)

### 飞书同步
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| lark-cli `docs +create` | CLI | ✅ 已内置 | 创建飞书文档 |
| lark-cli `markdown +create` | CLI | ✅ 已内置 | Markdown→飞书文档 |
| lark-cli `markdown +overwrite` | CLI | ✅ 已内置 | 更新已有飞书文档 |
| lark-cli `drive +import --type docx` | CLI | ✅ 已内置 | MD 文件→Docx 导入飞书 |
| lark-cli `whiteboard-update` | CLI | ✅ 已内置 | Mermaid→飞书画板（流程图渲染） |
| lark-cli `base` | CLI | ✅ 已内置 | 多维表格操作 |
| lark-cli `sheets` | CLI | ✅ 已内置 | 电子表格操作 |
| lark-cli `im` | CLI | ✅ 已内置 | 发送飞书消息 |
| lark-cli `calendar` | CLI | ✅ 已内置 | 日历/会议 |

### PDF 导出
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| mermaid-to-pdf | CLI/MCP | 🔌 可安装 | Mermaid 图表→PDF (GitHub costajohnt) |
| Pandoc | CLI | 🔌 可安装 | Markdown→PDF/Word/PPT |
| canvas-design Skill (PDF) | Skill | ✅ 已内置 | 生成 PDF 文档 |
| headless Chrome print | Script | 🔮 规划中 | HTML 原型→PDF |

### 演示文稿
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| Pandoc → PPTX | CLI | 🔌 可安装 | Markdown→PPT |
| Figma Slides | MCP | ✅ 已内置 | Figma 原生 Slides 创建 |
| HTML 演示 | Skill | ✅ 已内置 | frontend-design 产出可直接演示 |
| reveal.js | Script | 🔮 规划中 | Markdown→Web 演示文稿 |

### 邮件/通知
| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| lark-cli `im` | CLI | ✅ 已内置 | 飞书消息通知 |
| Gmail MCP | MCP | 🔌 可安装 | 发送邮件 |
| lark-cli `mail` | CLI | ✅ 已内置 | 飞书邮件 |

---

## 五、沟通协作层 (Communication)

| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| lark-cli `im` (send) | CLI | ✅ 已内置 | 飞书单聊/群聊消息 |
| lark-cli `calendar` (create) | CLI | ✅ 已内置 | 创建会议、查看忙闲 |
| lark-cli `task` | CLI | ✅ 已内置 | 创建/分配飞书任务 |
| claude-code-feishu-channel | Plugin | 🔌 可安装 | 飞书双向通道 (GitHub whobot-ai) |
| lark-claude-bridge | Plugin | 🔌 可安装 | Claude Code 接入飞书 (GitHub YHAIer) |
| Slack MCP | MCP | 🔌 可安装 | Slack 消息 |

---

## 六、研究调研层 (Research)

| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| WebSearch | MCP | ✅ 已内置 | 实时搜索 |
| WebFetch | MCP | ✅ 已内置 | 深度阅读网页 |
| Brave Search | MCP | 🔌 可安装 | 隐私友好搜索 |
| Firecrawl | MCP | 🔌 可安装 | 结构化网页爬取 |
| Exa | MCP | 🔌 可安装 | 语义搜索 |
| Context7 | MCP | 🔌 可安装 | 实时最新技术文档查询 |
| GitHub API (`gh`) | CLI | ✅ 已内置 | 搜索开源项目、Star 数、Issue |

---

## 七、质量保障层 (Quality)

| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| validate_artifact.py × 5 | Script | ✅ 已内置 | 每个工作事项的结构与语义校验 |
| branch_validator.py | Script | ✅ 已内置 | 人工评审、变更与回流记录校验（文件名为兼容保留） |
| run_tests_mac.sh | Script | ✅ 已内置 | 全量回归测试 |
| webapp-testing Skill | Skill | ✅ 已内置 | 浏览器自动化测试原型 |
| impeccable Skill | Skill | ✅ 已内置 | UI 审查、UX 检查 |
| mermaid-to-pdf (验证渲染) | CLI | 🔌 可安装 | 确保 Mermaid 图正确渲染 |
| 拼写/术语检查 | Script | 🔮 规划中 | 中英文术语一致性 |
| 可访问性检查 | Skill | 🔮 规划中 | a11y 自动检查 |

---

## 八、自动化层 (Automation)

| 工具 | 类型 | 状态 | 说明 |
|---|---|---|---|
| run_tests_mac.sh | Script | ✅ 已内置 | 一键全量回归 |
| lark-cli 文档同步 | Script | 🔮 规划中 | PRD confirmed→自动同步飞书 |
| 日报/周报生成 | Skill | 🔮 规划中 | 基于 Obsidian 日志自动生成 |
| CronCreate | Built-in | ✅ 已内置 | 定时任务（如每日检查 QuestionRecord 老化） |
| Workflow | Built-in | ✅ 已内置 | 多 Agent 并行编排 |
| Make.com/Zapier MCP | MCP | 🔌 可安装 | 跨平台工作流自动化 |

---

## 九、按 PM 工作流场景速查

### "我刚收到一封需求邮件"
→ Gmail MCP 读邮件 → 需求重举（发散） → entry-router 判定起点 → `project-background-goal`

### "我要画用户旅程图给业务方看"
→ `user-journey-and-stories` 产出旅程数据 → Figma generate_diagram (journey map) → lark-cli 同步到飞书

### "我要做竞品分析"
→ WebSearch 搜竞品 → WebFetch 读竞品网站 → dataviz 做对比图表 → markdown +overwrite 同步飞书

### "我要出原型和开发沟通"
→ Figma get_design_context 参考设计系统 → frontend-design 生成原型 → webapp-testing 截屏验证

### "我要出最终 PRD 给领导审批"
→ `prd-assembly` 汇总 → mermaid-to-pdf 导出 PDF → lark-cli drive +import 同步飞书 → lark-cli im 发送审批通知

### "需求改了，要通知所有人"
→ Revision 修改确认 → change-reflow 检测影响范围 → lark-cli im 通知受影响方
