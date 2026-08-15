# lark-cli 飞书集成 · PM 常用命令

> lark-cli v1.0.84 已安装。所有命令需先 `cd` 到目标文件所在目录。

## PM 高频场景

### 1. PRD 同步到飞书云空间
```bash
# 方式A：Markdown 直接创建飞书文档
lark-cli markdown +create --file ./prd.md --title "REQ-NNN PRD"

# 方式B：导入为 Docx（支持 Mermaid 画板渲染）
lark-cli drive +import --type docx --file ./prd.md

# 方式C：覆盖已有文档
lark-cli markdown +overwrite --file-token DocToken --file ./prd.md
```

### 2. Mermaid 流程图渲染到飞书画板
```bash
# 飞书原生 Markdown 不渲染 Mermaid，需转为画板
lark-cli docs +update --command block_replace --file ./flow.md
# 将 <pre lang="Plaintext"> 块替换为 <whiteboard type="mermaid">
```

### 3. 读取飞书文档内容
```bash
# 读取为 Markdown
lark-cli docs +fetch --doc DocToken --doc-format markdown --format pretty

# 读取大纲
lark-cli docs +fetch --doc DocToken --scope outline --format pretty
```

### 4. 发送飞书消息通知
```bash
# 发送文本消息
lark-cli im +send --receive-id-type chat_id --receive-id ChatID --content '{"text":"PRD 已更新"}'

# 发送卡片消息（带按钮）
lark-cli im +send --receive-id-type chat_id --receive-id ChatID --msg-type interactive
```

### 5. 飞书多维表格（需求管理）
```bash
# 读取多维表格
lark-cli base +fetch --app-token BaseToken --table-id TableID

# 新增记录（如新增需求条目）
lark-cli base +record-create --app-token BaseToken --table-id TableID
```

### 6. 日历与任务
```bash
# 查看日程
lark-cli calendar +list --start-time "2026-08-11" --end-time "2026-08-18"

# 创建任务
lark-cli task +create --summary "评审 REQ-NNN PRD" --due-date "2026-08-15"
```

## 踩坑提醒（来自全局复利日志）

- `--file` 参数**只接受相对路径**（不是绝对路径），需先 `cd` 到目标目录
- 飞书 Markdown 文件**不渲染 Mermaid**，需导入为 Docx + 画板方案
- 跨目录操作时：先 `cp` 文件到 cwd，再传 `./filename`
