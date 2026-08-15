#!/usr/bin/env python3
"""Unit tests for product-ux validate_artifact.py"""

import sys
import tempfile
from pathlib import Path

SKILL_SCRIPT = Path(__file__).resolve().parent.parent.parent.parent / "src/stages/002-product-requirements/skills/product-ux/scripts/validate_artifact.py"
sys.path.insert(0, str(SKILL_SCRIPT.parent))

import importlib.util
spec = importlib.util.spec_from_file_location("validate_artifact", SKILL_SCRIPT)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)


def test_template_passes():
    """Template file itself should pass structural validation."""
    template = Path(__file__).resolve().parent.parent.parent.parent / "src/templates/stage-2-product/product-ux.md"
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
        assert any("Missing frontmatter" in e or "Missing required headings" in e for e in result["errors"])
        print("✅ test_missing_contract_fails")
    finally:
        Path(tmp).unlink()


def test_low_density_fixture_passes():
    """Low-density degradation fixture should pass (status=needs_user_input)."""
    fixture = Path(__file__).resolve().parent / "fixtures/ux-low-density-degradation.md"
    if not fixture.exists():
        print("⚠️  test_low_density_fixture_passes: fixture missing, skipped")
        return
    result = validate_module.validate(fixture)
    assert result["ok"], f"Low-density fixture should pass: {result.get('errors')}"
    print("✅ test_low_density_fixture_passes")


if __name__ == "__main__":
    test_template_passes()
    test_missing_contract_fails()
    test_low_density_fixture_passes()
    print("\n3 tests passed.")