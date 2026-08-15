#!/usr/bin/env python3
"""Unit tests for function-description validate_artifact.py"""

import sys
import tempfile
from pathlib import Path

SKILL_SCRIPT = Path(__file__).resolve().parent.parent.parent.parent / "src/stages/002-product-requirements/skills/function-description/scripts/validate_artifact.py"
sys.path.insert(0, str(SKILL_SCRIPT.parent))

import importlib.util
spec = importlib.util.spec_from_file_location("validate_artifact", SKILL_SCRIPT)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)


def test_template_passes():
    """Template file itself should pass structural validation."""
    template = Path(__file__).resolve().parent.parent.parent.parent / "src/templates/stage-2-product/function-description.md"
    result = validate_module.validate(template)
    assert result["ok"], f"Template should pass: {result.get('errors')}"
    print("✅ test_template_passes")


def test_missing_contract_fails():
    """File with missing frontmatter must fail."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# Just a title\n\nNo frontmatter.\n")
        tmp = f.name
    try:
        result = validate_module.validate(Path(tmp))
        assert not result["ok"], "Should fail: missing frontmatter"
        assert any("Missing frontmatter" in e for e in result["errors"])
        print("✅ test_missing_contract_fails")
    finally:
        Path(tmp).unlink()


def test_violation_fixture_rejected():
    """Violation fixture must be rejected with the D4.4 Given/When/Then error."""
    fixture = Path(__file__).resolve().parent / "fixtures/fd-violation-no-given-when-then.md"
    if not fixture.exists():
        print("⚠️  test_violation_fixture_rejected: fixture missing, skipped")
        return
    result = validate_module.validate(fixture)
    assert not result["ok"], "Violation fixture must be rejected"
    has_d44 = any("D4.4" in e for e in result["errors"])
    assert has_d44, f"Should emit D4.4 error; got: {result['errors']}"
    print("✅ test_violation_fixture_rejected")


if __name__ == "__main__":
    test_template_passes()
    test_missing_contract_fails()
    test_violation_fixture_rejected()
    print("\n3 tests passed.")