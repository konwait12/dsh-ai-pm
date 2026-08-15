#!/usr/bin/env python3
"""Unit tests for prd-assembly validate_artifact.py"""

import sys
import tempfile
from pathlib import Path

SKILL_SCRIPT = Path(__file__).resolve().parent.parent.parent.parent / "src/stages/003-prd-output/skills/prd-assembly/scripts/validate_artifact.py"
sys.path.insert(0, str(SKILL_SCRIPT.parent))

import importlib.util
spec = importlib.util.spec_from_file_location("validate_artifact", SKILL_SCRIPT)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)


def test_template_passes():
    """Template file itself should pass structural validation."""
    template = Path(__file__).resolve().parent.parent.parent.parent / "src/templates/stage-3-prd/prd.md"
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


def test_violation_fixture_emits_d52_error():
    """Violation fixture should fail D5.2 (missing upstream UX-/FD-)."""
    fixture = Path(__file__).resolve().parent / "fixtures/prd-violation-missing-upstream.md"
    if not fixture.exists():
        print("⚠️  test_violation_fixture_emits_d52_error: fixture missing, skipped")
        return
    result = validate_module.validate(fixture)
    assert not result["ok"], "Violation fixture should fail D5.2"
    has_d52 = any("D5.2" in e for e in result["errors"])
    assert has_d52, f"Should emit D5.2 error; got: {result['errors']}"
    print("✅ test_violation_fixture_emits_d52_error")


if __name__ == "__main__":
    test_template_passes()
    test_missing_contract_fails()
    test_violation_fixture_emits_d52_error()
    print("\n3 tests passed.")