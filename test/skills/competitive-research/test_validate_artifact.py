#!/usr/bin/env python3
"""Unit tests for competitive-research validate_artifact.py — Source Fidelity (SRC-ID)."""

import sys
import tempfile
from pathlib import Path

SKILL_SCRIPT = Path(__file__).resolve().parent.parent.parent.parent / "src/support-skills/competitive-research/scripts/validate_artifact.py"
sys.path.insert(0, str(SKILL_SCRIPT.parent))

import importlib.util
spec = importlib.util.spec_from_file_location("validate_artifact", SKILL_SCRIPT)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)

SRC_WARNING_KEY = "Source Fidelity"


def _mkdoc(analysis_body: str) -> str:
    """A structurally complete competitive-analysis artifact."""
    return (
        "## 竞品列表\n\n"
        "| 竞品名称 | 产品类型 | 目标用户 | 核心功能 |\n"
        "|---|---|---|---|\n"
        "| 竞品A | SaaS | 企业 | 功能1 |\n\n"
        "## 逐品分析\n\n"
        "### 竞品A\n" + analysis_body + "\n"
        "## 横向对比\n\n"
        "| 维度 | 竞品A |\n"
        "|---|---|\n"
        "| 功能 | 高 |\n\n"
        "## 结论\n\n"
        "- 关键发现：AI_INFERENCE — 待人工确认\n"
    )


def test_confirmed_fixture_passes_with_traceability_warning():
    """Confirmed fixture stays ok; it cites no SRC-ID, so Source Fidelity warns."""
    fixture = Path(__file__).resolve().parent / "fixtures/competitive-confirmed.md"
    result = validate_module.validate(fixture)
    assert result["ok"], f"Fixture should pass: {result.get('errors')}"
    assert any(SRC_WARNING_KEY in w for w in result["warnings"]), (
        "Fixture has analysis claims without SRC-IDs, Source Fidelity must warn"
    )
    print("✅ test_confirmed_fixture_passes_with_traceability_warning")


def test_src_id_cited_passes():
    """Analysis entries that cite SRC-IDs should not trigger the Source Fidelity warning."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(_mkdoc("- 功能分析：描述（SRC-001）\n- 用户体验：描述（SRC-001）"))
        tmp = f.name
    try:
        result = validate_module.validate(Path(tmp))
        assert result["ok"], f"Should pass: {result.get('errors')}"
        assert not any(SRC_WARNING_KEY in w for w in result["warnings"]), (
            f"SRC-IDs cited, should have no Source Fidelity warning; got: {result['warnings']}"
        )
        print("✅ test_src_id_cited_passes")
    finally:
        Path(tmp).unlink()


def test_missing_src_warns():
    """Analysis content without any SRC-ID must trigger the Source Fidelity warning."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(_mkdoc("- 功能分析：描述\n- 用户体验：描述"))
        tmp = f.name
    try:
        result = validate_module.validate(Path(tmp))
        assert result["ok"], "Missing SRC-ID is a warning, not a blocker"
        assert any(SRC_WARNING_KEY in w for w in result["warnings"]), (
            f"Should warn about missing SRC-ID; got: {result['warnings']}"
        )
        print("✅ test_missing_src_warns")
    finally:
        Path(tmp).unlink()


if __name__ == "__main__":
    test_confirmed_fixture_passes_with_traceability_warning()
    test_src_id_cited_passes()
    test_missing_src_warns()
    print("\n3 tests passed.")
