# 推荐安装清单

> 当前环境已内置的工具在上面 TOOLKIT.md 中标为 ✅。
> 以下为推荐额外安装的工具，按优先级排列。

## Tier 1 — 立即安装（显著提升 PM 效率）

### Gmail MCP（读需求邮件）
```bash
claude mcp add gmail -- npx @anthropic/mcp-gmail
```
场景：客户/业务方通过邮件发需求 → AI 自动提取结构化为 background-goal

### JIRA MCP 或 Linear MCP（需求跟踪）
```bash
# JIRA
claude mcp add jira -- npx @anthropic/mcp-jira

# Linear
claude mcp add linear -- npx @anthropic/mcp-linear
```
场景：AI 产出 Story Card → 自动创建 JIRA/Linear Ticket → 跟踪开发进度

### feishu-user-plugin（飞书深度集成）
```bash
# GitHub: EthanQC/feishu-user-plugin (MIT, 85 tools)
claude plugin install @ethanqc/feishu-user-plugin
```
场景：以用户身份发飞书消息、读私聊、操作文档/日历/任务/OKR
比 lark-cli 更深度：支持读私聊、用户身份发消息、实时事件 WebSocket

### mermaid-to-pdf（Mermaid 图表→PDF 导出）
```bash
npm install -g mermaid-to-pdf
```
场景：PRD 中的 Mermaid 图导出为 PDF 中的矢量图

## Tier 2 — 按需安装（特定场景使用）

### Brave Search（更精准的实时搜索）
```bash
claude mcp add brave-search -- npx @anthropic/mcp-brave-search
```
场景：竞品深度调研、行业最新动态

### Firecrawl（网页深度爬取）
```bash
claude mcp add firecrawl -- npx @anthropic/mcp-firecrawl
```
场景：批量爬取竞品网站页面结构、提取产品功能清单

### Pandoc（Markdown→PDF/Word/PPT 万能转换）
```bash
brew install pandoc
```
场景：PRD→PDF 交付、Markdown→PPT 演示、PRD→Word 审批

### lark-claude-bridge（飞书双向 Claude Code 通道）
```bash
# GitHub: YHAIer/lark-claude-bridge
```
场景：在飞书群里 @Claude 让它跑 PRD 流程，非技术人员也能用

### Slack MCP（Slack 集成）
```bash
claude mcp add slack -- npx @anthropic/mcp-slack
```
场景：Slack 团队的消息读取、通知发送

## Tier 3 — 未来评估

### OCR/图像识别
场景：白板照片→结构化需求、手写笔记→文字

### 音频转文字
场景：会议录音→逐字稿→自动提炼需求

### Notion MCP
场景：Notion 文档读写、需求数据库同步

### App Store 评论分析
场景：竞品 App 用户反馈→需求洞察

### 微信/企微 MCP
场景：国内团队即时通讯集成
