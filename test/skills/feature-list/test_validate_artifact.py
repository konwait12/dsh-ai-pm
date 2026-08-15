#!/usr/bin/env python3
"""Unit tests for feature-list validate_artifact.py (sub-skill of function-description)."""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL_SCRIPT = (
    ROOT
    / "src/stages/002-product-requirements/skills/function-description/skills/feature-list/scripts/validate_artifact.py"
)
sys.path.insert(0, str(SKILL_SCRIPT.parent))

import importlib.util

spec = importlib.util.spec_from_file_location("validate_artifact", SKILL_SCRIPT)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)

FIXTURE = Path(__file__).resolve().parent / "fixtures/feature-list-confirmed.md"

POSITIVE_HEADER = """---
artifact_id: FD-TST-001
version: v0.1
status: draft
owner: PM-Office
reviewer: 评审人
created_at: 2026-08-13
updated_at: 2026-08-13
---

# 功能描述

## 1. 功能清单

| ID | 功能名称 | 所属故事 ST | 优先级 | 一句话描述 | 来源 |
|---|---|---|---|---|---|
| FEA-001 | 客户名单导入 | ST-001 | P0 | 描述 | ST-001 (FACT) |

## 2. 分功能详述
"""


def _write_temp(body: str) -> Path:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(body)
        return Path(f.name)


def test_positive_fixture_passes():
    """The confirmed fixture (feature-list-confirmed.md) must pass validation."""
    assert FIXTURE.is_file(), f"Fixture missing: {FIXTURE}"
    result = validate_module.validate(FIXTURE)
    assert result["ok"], f"Fixture should pass: {result.get('errors')}"
    print("✅ test_positive_fixture_passes")


def test_fea_without_st_rejected():
    """Negative: a FEA row with no ST-XXX story traceability must be rejected."""
    body = POSITIVE_HEADER.replace(
        "| FEA-001 | 客户名单导入 | ST-001 | P0 | 描述 | ST-001 (FACT) |",
        "| FEA-001 | 客户名单导入 | ST-001 | P0 | 描述 | ST-001 (FACT) |\n"
        "| FEA-999 | 幽灵功能 | 待确认 | P0 | 无来源功能 | AI_INFERENCE |",
    )
    tmp = _write_temp(body)
    try:
        result = validate_module.validate(tmp)
        assert not result["ok"], "Should fail: FEA row without ST-XXX"
        assert any("without ST-XXX" in e for e in result["errors"]), result["errors"]
        print("✅ test_fea_without_st_rejected")
    finally:
        tmp.unlink()


def test_confirmed_status_rejected():
    """Negative: sub-skill output may never carry status=confirmed."""
    body = POSITIVE_HEADER.replace("status: draft", "status: confirmed\nconfirmed_at: 2026-08-13")
    tmp = _write_temp(body)
    try:
        result = validate_module.validate(tmp)
        assert not result["ok"], "Should fail: status=confirmed is not allowed"
        assert any("confirmed" in e and "not allowed" in e for e in result["errors"]), result["errors"]
        print("✅ test_confirmed_status_rejected")
    finally:
        tmp.unlink()


def test_missing_section_rejected():
    """Negative: parent artifact without a 功能清单 section must be rejected."""
    body = "# 功能描述\n\n## 2. 分功能详述\n\n无功能清单章节。\n"
    tmp = _write_temp(body)
    try:
        result = validate_module.validate(tmp)
        assert not result["ok"], "Should fail: missing 功能清单 section"
        assert any("Missing required section" in e for e in result["errors"]), result["errors"]
        print("✅ test_missing_section_rejected")
    finally:
        tmp.unlink()


if __name__ == "__main__":
    test_positive_fixture_passes()
    test_fea_without_st_rejected()
    test_confirmed_status_rejected()
    test_missing_section_rejected()
    print("\n4 tests passed.")
