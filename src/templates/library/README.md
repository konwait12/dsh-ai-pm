# 模板库预留接口（Template Library Reservation）

> 本目录为**未来模板自动分类库**的预留接口，当前不包含任何可执行逻辑，不影响项目本体。
> 创建于 2026-08-12，响应"业务场景模板应独立成库"的规划诉求。

## 1. 定位

当前项目模板分散在三处：

| 位置 | 用途 | 示例 |
|---|---|---|
| `src/templates/{stage-1-business,stage-2-product,stage-3-prd}/` | 核心产物模板（按阶段组织） | `background-goal.md`、`prd.md` |
| `src/stages/*/skills/*/examples/{artifacts,guides}/` | Skill 示例产物与教学指南 | `artifact-1-example-sufficient.md` |
| `src/stages/*/skills/*/skills/*/templates/` | 子 Skill 输出模板 | `acceptance-criteria-output.md` |

**未来模板库**的目标：把"业务场景模板"（如活动邀约、内容平台发布、电商退款流程等）从核心模板中抽离，按业务域自动分类，形成可独立加载、可按需切换的模板生态。

## 2. 与现有 resolver.py 的关系

`src/templates/resolver.py` 已内置 4 层优先级栈：

```
1. Project-level overrides:  requirements/REQ-NNN/.templates/<name>
2. Active preset:            src/templates/presets/<preset>/<name>
3. Extensions (future):      src/templates/extensions/<ext>/<name>   ← 模板库将挂载于此
4. Core (default):           src/templates/**/<name>
```

**预留挂载点**：未来模板库通过 `src/templates/extensions/<domain>/` 目录接入 resolver，无需修改 `resolver.py` 逻辑。例如：

```
src/templates/extensions/
├── <domain>-scenario/           # 业务场景模板包（<domain> 为业务域占位）
│   ├── manifest.json
│   ├── background-goal.md       # 场景化背景模板
│   ├── journey-and-stories.md
│   └── ...
├── content-platform/           # 内容平台场景模板包
└── ecommerce-refund/           # 电商退款场景模板包
```

调用方使用 `--preset <domain>-scenario` 或在 `manifest.json` 中声明 `auto_classify: true`，由未来的分类器自动匹配。

## 3. 本目录文件清单

| 文件 | 用途 | 当前状态 |
|---|---|---|
| `README.md` | 本文件，说明模板库规划与接入点 | 已创建（预留） |
| `manifest.schema.json` | 模板清单 schema，定义自动分类所需元数据 | 已创建（预留） |
| `classifier-interface.md` | 自动分类器接口契约，定义输入/输出/调用时机 | 已创建（预留） |

## 4. 未来实施路线（不本次执行）

| 阶段 | 工作内容 | 是否影响本体 |
|---|---|---|
| Phase 1 | 在 `src/templates/extensions/` 下创建第一个业务模板包（如 `<domain>-scenario/`），迁移 `examples/artifacts/artifact-1-example-sufficient.md` | 否（新增目录，不动核心） |
| Phase 2 | 实现 `classifier.py`，读取 `manifest.json` 的 `domain`/`scenario`/`tags` 字段，自动匹配请求中的业务关键词 | 否（独立脚本，resolver 不变） |
| Phase 3 | 在 `resolver.py` 的 extensions 扫描逻辑中加入 classifier 调用（当 `auto_classify=true` 时） | 是（需改 resolver，走变更确认） |
| Phase 4 | 建立"模板贡献指南"，允许外部提交业务模板包 | 否（文档工作） |

## 5. 当前不变项

- `resolver.py` 逻辑**不修改**
- 核心模板（`stage-1-business/`、`stage-2-product/`、`stage-3-prd/`）**不迁移**
- Skill 示例（`examples/artifacts/`、`examples/guides/`）**不迁移**
- 校验脚本（`validate_artifact.py`）**不修改**

模板库建设完全在 `src/templates/library/` 和未来的 `src/templates/extensions/` 下进行，与本项目核心能力解耦。
