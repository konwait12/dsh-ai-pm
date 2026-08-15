#!/usr/bin/env python3
"""Unit tests for feasibility-analysis validate_artifact.py — Source Fidelity (SRC-ID / knowledge state)."""

import sys
import tempfile
from pathlib import Path

SKILL_SCRIPT = Path(__file__).resolve().parent.parent.parent.parent / "src/support-skills/feasibility-analysis/scripts/validate_artifact.py"
sys.path.insert(0, str(SKILL_SCRIPT.parent))

import importlib.util
spec = importlib.util.spec_from_file_location("validate_artifact", SKILL_SCRIPT)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)

SRC_WARNING_KEY = "Source Fidelity"


def _mkdoc(roi_cost: str) -> str:
    """A structurally complete feasibility-report artifact (mode detected via 可行性)."""
    return (
        "## 市场空间\n\n"
        "| 指标 | 数据 | 来源 |\n"
        "|---|---|---|\n"
        "| 目标用户量 | 100万 | 行业报告 |\n\n"
        "## 技术可行性\n\n"
        "| 技术挑战 | 状态 | 验证方式 |\n"
        "|---|---|---|\n"
        "| 兼容性 | 已验证 | 原型验证 |\n\n"
        "## 投入产出\n\n"
        "| 项目 | 金额/时间 | 说明 |\n"
        "|---|---|---|\n"
        "| 研发成本 | " + roi_cost + " | 含人力与工具 |\n\n"
        "## 风险评估\n\n"
        "| 风险 | 影响 | 概率 | 应对措施 |\n"
        "|---|---|---|---|\n"
        "| 交付延迟 | 高 | 中 | 预留缓冲 |\n\n"
        "## 结论\n\n"
        "**建议**: 做\n\n"
        "**条件**: 无\n\n"
        "**AI 推荐理由**: 成本可控\n"
    )


def test_confirmed_fixture_passes_with_traceability_warning():
    """Confirmed fixture stays ok; it cites no SRC-ID and no knowledge state, so Source Fidelity warns."""
    fixture = Path(__file__).resolve().parent / "fixtures/feasibility-confirmed.md"
    result = validate_module.validate(fixture)
    assert result["ok"], f"Fixture should pass: {result.get('errors')}"
    assert any(SRC_WARNING_KEY in w for w in result["warnings"]), (
        "Fixture has cost/risk content without SRC-IDs, Source Fidelity must warn"
    )
    print("✅ test_confirmed_fixture_passes_with_traceability_warning")


def test_knowledge_state_label_passes():
    """Cost figures labeled AI_INFERENCE should satisfy Source Fidelity without an SRC-ID."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(_mkdoc("10万（AI_INFERENCE）"))
        tmp = f.name
    try:
        result = validate_module.validate(Path(tmp))
        assert result["ok"], f"Should pass: {result.get('errors')}"
        assert not any(SRC_WARNING_KEY in w for w in result["warnings"]), (
            f"AI_INFERENCE label satisfies traceability; got: {result['warnings']}"
        )
        print("✅ test_knowledge_state_label_passes")
    finally:
        Path(tmp).unlink()


def test_missing_source_warns():
    """Cost/risk content with neither SRC-ID nor knowledge-state label must trigger the warning."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(_mkdoc("10万"))
        tmp = f.name
    try:
        result = validate_module.validate(Path(tmp))
        assert result["ok"], "Missing source traceability is a warning, not a blocker"
        assert any(SRC_WARNING_KEY in w for w in result["warnings"]), (
            f"Should warn about missing source traceability; got: {result['warnings']}"
        )
        print("✅ test_missing_source_warns")
    finally:
        Path(tmp).unlink()


if __name__ == "__main__":
    test_confirmed_fixture_passes_with_traceability_warning()
    test_knowledge_state_label_passes()
    test_missing_source_warns()
    print("\n3 tests passed.")
