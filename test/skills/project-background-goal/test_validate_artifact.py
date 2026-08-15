from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = PROJECT_ROOT / "src" / "stages" / "001-business-requirements" / "skills" / "project-background-goal"
SCRIPT_PATH = SKILL_ROOT / "scripts" / "validate_artifact.py"
TEMPLATE_PATH = PROJECT_ROOT / "src" / "templates" / "stage-1-business" / "background-goal.md"

SPEC = importlib.util.spec_from_file_location("validate_artifact", SCRIPT_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ValidateArtifactTest(unittest.TestCase):
    def test_template_passes(self) -> None:
        result = VALIDATOR.validate(TEMPLATE_PATH)
        self.assertTrue(result["ok"], result)

    def test_missing_contract_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact = Path(temp_dir) / "invalid.md"
            artifact.write_text("# 项目背景与目标\n\n没有契约结构。\n", encoding="utf-8")
            result = VALIDATOR.validate(artifact)

        self.assertFalse(result["ok"])
        self.assertTrue(any("frontmatter" in error for error in result["errors"]))
        self.assertTrue(any("headings" in error for error in result["errors"]))

    def test_confirmed_artifact_requires_confirmation_owners(self) -> None:
        text = TEMPLATE_PATH.read_text(encoding="utf-8").replace("status: draft", "status: confirmed")
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact = Path(temp_dir) / "confirmed-without-reviewer.md"
            artifact.write_text(text, encoding="utf-8")
            result = VALIDATOR.validate(artifact)

        self.assertFalse(result["ok"])
        self.assertTrue(any("confirmation fields" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
