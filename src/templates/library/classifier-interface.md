# 模板自动分类器接口契约（预留）

> 本文件定义未来 `classifier.py` 的接口契约，当前为预留，不被任何代码调用。
> 创建于 2026-08-12，配合 `manifest.schema.json` 使用。

## 1. 定位

模板自动分类器（`classifier.py`）是未来模板库的核心组件，负责：

1. 读取请求中的业务关键词（来自 `requirements/REQ-NNN/` 的原始材料摘要）
2. 扫描 `src/templates/extensions/*/manifest.json`
3. 根据 `domain`、`scenario`、`tags` 字段匹配候选模板包
4. 返回最佳匹配的模板包 ID（或 `null` 表示无匹配，回退核心模板）

## 2. 接口签名（未来实现）

```python
# src/templates/library/classifier.py（未来创建）
from pathlib import Path

def classify(
    req_dir: Path,
    extensions_dir: Path | None = None,
    top_k: int = 3,
) -> list[str]:
    """
    根据请求目录中的原始材料，匹配候选模板包。

    Args:
        req_dir: requirements/REQ-NNN-topic/ 目录路径
        extensions_dir: src/templates/extensions/ 目录路径，默认自动推断
        top_k: 返回前 K 个候选模板包 ID

    Returns:
        按匹配度降序排列的 template_package_id 列表。
        空列表表示无匹配，调用方应回退核心模板。

    Raises:
        FileNotFoundError: extensions_dir 不存在时（当前正常情况，返回空列表）
    """
    ...
```

## 3. 匹配规则（未来实现，当前仅定义）

| 优先级 | 匹配维度 | 权重 | 说明 |
|---|---|---|---|
| 1 | `domain` 精确匹配 | 0.5 | 请求摘要中的业务域关键词与 manifest.domain 完全匹配 |
| 2 | `scenario` 精确匹配 | 0.3 | 请求摘要中的场景关键词与 manifest.scenario 完全匹配 |
| 3 | `tags` 关键词匹配 | 0.15 | 请求摘要命中 manifest.tags 中的标签数量 |
| 4 | `domain` 模糊匹配 | 0.05 | 同义词/上位词匹配（如同义词库未来引入） |

- 总分 ≥ 0.6 的模板包进入候选
- 候选数 > 1 时，取 top_k=3 供人工选择
- 候选数 = 0 时，返回空列表，调用方回退核心模板（resolver.py 第 4 层）

## 4. 与 resolver.py 的集成点（未来实施）

当前 `resolver.py` 的第 3 层 extensions 扫描逻辑：

```python
# 当前逻辑（不修改）
if EXTENSIONS_DIR.exists():
    for ext_dir in sorted(EXTENSIONS_DIR.iterdir()):
        if ext_dir.is_dir():
            ext_template = ext_dir / name
            if ext_template.exists():
                return ext_template
```

未来 Phase 3 集成方案（**不本次实施**）：

```python
# 未来逻辑（Phase 3 实施，走变更确认）
if EXTENSIONS_DIR.exists():
    # 新增：调用分类器获取候选模板包
    candidate_packages = classifier.classify(req_dir) if req_dir else []

    # 优先在候选模板包中查找
    for pkg_id in candidate_packages:
        ext_template = EXTENSIONS_DIR / pkg_id / name
        if ext_template.exists():
            return ext_template

    # 兜底：扫描所有 extensions（保持当前逻辑）
    for ext_dir in sorted(EXTENSIONS_DIR.iterdir()):
        if ext_dir.is_dir():
            ext_template = ext_dir / name
            if ext_template.exists():
                return ext_template
```

## 5. 当前不变项

- `resolver.py` **不修改**，仍按当前 extensions 扫描逻辑运行
- `classifier.py` **不创建**，待 Phase 2 实施
- 本接口契约仅用于：
  1. 让未来贡献者了解模板包 `manifest.json` 应包含哪些字段
  2. 让未来 `classifier.py` 实现者有明确的接口约束
  3. 让 `resolver.py` 维护者知道未来集成点在哪里

## 6. 验证标准（未来实施时）

| 测试场景 | 输入 | 期望输出 |
|---|---|---|
| 无 extensions 目录 | `req_dir=REQ-NNN`，`extensions_dir` 不存在 | 返回空列表，resolver 回退核心模板 |
| 无匹配模板包 | `req_dir` 摘要为"内容平台发布"，extensions 中只有 `<domain>-scenario` | 返回空列表 |
| 精确匹配 | `req_dir` 摘要为"电商下单场景"，extensions 有 `<domain>-scenario` | 返回 `["<domain>-scenario"]` |
| 多候选 | `req_dir` 摘要同时命中两个域 | 返回 top_k=3 个候选 ID |
| deprecated 模板包不参与匹配 | extensions 中有 `deprecated` 状态的模板包 | 跳过该模板包 |
