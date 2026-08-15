#!/usr/bin/env python3
"""Unit tests for user-journey-and-stories validate_artifact.py"""

import json
import sys
import tempfile
from pathlib import Path

# Add the skill scripts dir to path
SKILL_SCRIPT = Path(__file__).resolve().parent.parent.parent.parent / "src/stages/001-business-requirements/skills/user-journey-and-stories/scripts/validate_artifact.py"
sys.path.insert(0, str(SKILL_SCRIPT.parent))

import importlib.util
spec = importlib.util.spec_from_file_location("validate_artifact", SKILL_SCRIPT)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)


def test_template_passes():
    """Template file itself should pass structural validation (warnings OK)."""
    template = Path(__file__).resolve().parent.parent.parent.parent / "src/templates/stage-1-business/journey-and-stories.md"
    result = validate_module.validate(template)
    assert result["ok"], f"Template should pass: {result.get('errors')}"
    print("✅ test_template_passes")


def test_missing_contract_fails():
    """File with missing frontmatter and headings must fail."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# Just a title\n\nNo frontmatter, no proper structure.\n")
        tmp = f.name
    try:
        result = validate_module.validate(Path(tmp))
        assert not result["ok"], "Should fail: missing frontmatter and headings"
        assert any("Missing frontmatter" in e for e in result["errors"])
        print("✅ test_missing_contract_fails")
    finally:
        Path(tmp).unlink()


def test_confirmed_requires_owners():
    """Confirmed status without proper confirmation fields must error."""
    content = """---
artifact_id: TEST-001
version: v1.0
status: confirmed
owner: PM
business_fact_owner: ""
goal_decision_owner: ""
reviewer: ""
created_at: "2026-01-01"
updated_at: "2026-01-01"
confirmed_at: ""
upstream_artifact_id: ""
---

# 用户旅程与用户故事

## 0. 预检输入充分度判定
test
## 1. 业务生命周期分解
test ST-001
## 2. 用户旅程图
test
## 3. 用户故事卡片
test
## 4. 旅程→故事覆盖矩阵
test
## 5. 路径类型覆盖检查
test
## 6. 事实与决定
test
## 7. 假设、AI 推断、未知与冲突
test
## 8. 待确认问题
test
## 9. 来源追溯
test
## 10. 下游输入摘要
test
## 11. Constitution Compliance
test
## 12. 版本变更摘要
test
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp = f.name
    try:
        result = validate_module.validate(Path(tmp))
        assert not result["ok"], "Should fail: confirmed with empty confirmation fields"
        assert any("unresolved confirmation fields" in e for e in result["errors"])
        print("✅ test_confirmed_requires_owners")
    finally:
        Path(tmp).unlink()


if __name__ == "__main__":
    test_template_passes()
    test_missing_contract_fails()
    test_confirmed_requires_owners()
    print("\nAll 3 tests passed.")
