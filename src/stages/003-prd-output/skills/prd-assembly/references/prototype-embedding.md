# PRD 原型嵌入技法参考（Prototype Embedding）

> 来源吸收：Trae `agile-pm-workflow` skill 的 PRD 内嵌原型技法（iframe 沙盒切片 + focus 沙盒锁定 + 版本切换器），经适配作为 prd-assembly 的可选增强。
> 定位：PRD 是唯一交付物，文本规则是权威；本技法让 PRD 的「分功能详述」章节内嵌可交互原型切片，提升沟通与评审效率。**可选启用**：仅当上游 product-ux 已产出可点击原型（见 page-design 的 `prototype-techniques.md`）时使用。

## 1. 适用条件

- 上游 `product-ux` 已产出可点击 HTML 原型（`prototype/index.html`）。
- PRD 分功能详述（§4）需要向业务/开发/测试直观展示交互。
- 满足其一即建议启用：流程 ≥ 3 页、涉及状态分支、需要多方评审。

## 2. 原型切片与沙盒锁定（核心技法）

### 2.1 单文件原型要求

上游原型必须支持：
1. **Hash 路由定位**：每个页面可通过 URL Hash 直达（如 `index.html#login`）。
2. **Focus 模式参数**：原型解析 `?focus=feature_id` 参数，进入 focus 模式时锁定/遮罩无关交互区域（`pointer-events: none; opacity: 0.5`），仅允许操作对应功能点。

> 若上游原型未实现 focus 模式，PRD 嵌入时降级为整页 iframe，并在 PRD §9 不一致报告标注「原型未实现 focus 沙盒」。

### 2.2 iframe 嵌入规范

每个功能模块（FEA/FUN）的详述区嵌入对应原型切片：

```html
<div class="feature-module">
  <h3>功能：{FUN 名称}</h3>
  <div class="feature-content" style="display:flex; gap:20px;">
    <div class="logic-rules" style="flex:1;">
      <h4>交互流程图</h4>
      <div class="mermaid">flowchart TD ...</div>
      <h4>规则描述</h4>
      <ul><li>触发条件：...</li><li>交互反馈：...</li></ul>
    </div>
    <div class="sandbox-preview">
      <iframe src="../prototype/index.html?focus={feature_id}#{page_hash}"
        style="width:375px; height:812px; border:none; background:transparent;"
        sandbox="allow-scripts allow-same-origin"></iframe>
    </div>
  </div>
</div>
```

尺寸规则：
- 移动端原型：固定宽度（如 `width:375px; height:812px`），必要时 `transform: scale(0.7)` 缩小。
- Web/后台原型：响应式宽度（`width:100%; height:600px`）。
- 去除边框：`border:none; background:transparent`。
- 沙盒隔离：`sandbox="allow-scripts allow-same-origin"`。

## 3. 版本切换器与物理隔离

### 3.1 文件物理隔离

- **绝不覆盖历史版本**：新版本复制 `prd_v1.1.html` + `prototype_v1.1.html`，历史版本原样保留。
- 版本命名 `prd_v{主}.{次}.html` 与 `prototype_v{主}.{次}.html` 一一对应。

### 3.2 PRD 界面内版本切换器

- PRD 页面右上角提供**版本切换下拉菜单**（v1.0 / v1.1 ...）一键跳转。
- 查看历史版本时，页面顶部显示警告横幅：「您正在查看历史版本 v1.0，点击此处前往最新版 v1.1」。

### 3.3 版本强联动

- PRD 中所有 iframe 切片路径必须指向**对应版本**的原型：`../prototype/prototype_v1.1.html`。
- 版本记录表记录本次迭代新增 / 修改 / 下线的功能点（Delta：ADDED/MODIFIED/REMOVED）。

## 4. 嵌入自检清单

- [ ] 上游原型存在且与 PRD 版本一致（路径含版本号）
- [ ] 每个 P0 功能详述区有对应切片（或标注「未生成原型」原因）
- [ ] iframe 带 `sandbox="allow-scripts allow-same-origin"` 与 focus 参数
- [ ] 移动端宽度 375px / Web 端响应式
- [ ] 版本切换器已实现，历史版本有警告横幅
- [ ] 切片路径与原型实际版本一致（版本联动）
- [ ] 文本规则仍是权威——原型切片是增强，不替代 §4 文字详述

## 5. 边界

- 原型嵌入不新增需求、不修改已确认内容（聚合契约不变）。
- 原型缺失时**不静默跳过**：在 §9 不一致报告标注，由人工决定是否补原型。
- focus 模式无法实现时降级整页 iframe 并显式标注，不伪造交互隔离。
