#!/usr/bin/env python3
"""Unit tests for registry_contract_check.py (Harness 借鉴点三·注册表契约硬化)."""

import json
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent.parent / "src/scripts"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import registry_contract_check as rcc


def _good_registry() -> dict:
    return {
        "schema_version": 1,
        "stages": [{"id": "S1", "name": "One", "path": "src/stages/001", "work_items": ["WI1"]}],
        "work_items": [{
            "id": "WI1", "name": "Item", "order": 1, "stage": "S1",
            "skill_path": "src/stages/001/skills/wi1", "artifact_dir": "001", "artifact_file": "a.md",
            "artifact_prefix": "A-", "required_outputs": ["AT1"], "predecessors": [], "reviewer_roles": ["business_owner"],
        }],
        "internal_capabilities": [{"id": "SUB1", "parent_work_item": "WI1", "order": 1, "skill_path": "src/stages/001/skills/wi1/skills/sub1"}],
        "artifact_types": [{"id": "AT1", "name": "Art", "producer": "WI1", "artifact_file": "a.md", "depends_on": []}],
        "support_capabilities": [{"id": "SUP1", "skill_path": "src/shared/sup1", "trigger": "x", "applicable_stages": ["S1"], "output_location": "99-review"}],
    }


class SchemaValidationTest(unittest.TestCase):
    def test_clean_registry_has_no_issues(self) -> None:
        self.assertEqual(rcc.validate_schema(_good_registry()), [])

    def test_missing_required_field(self) -> None:
        reg = _good_registry()
        del reg["work_items"][0]["order"]
        issues = rcc.validate_schema(reg)
        self.assertTrue(any(i["check_id"] == "registry.schema.missing_required" for i in issues))
        self.assertEqual(issues[0]["severity"], "CRITICAL")

    def test_unknown_field_detected(self) -> None:
        reg = _good_registry()
        reg["work_items"][0]["artifact_fiLe"] = "typo.md"  # note capital L
        issues = rcc.validate_schema(reg)
        self.assertTrue(any(i["check_id"] == "registry.schema.unknown_field" for i in issues))

    def test_wrong_type_rejected(self) -> None:
        reg = _good_registry()
        reg["work_items"][0]["order"] = "one"  # str instead of int
        issues = rcc.validate_schema(reg)
        self.assertTrue(any(i["check_id"] == "registry.schema.wrong_type" for i in issues))

    def test_cross_ref_predecessor_unknown(self) -> None:
        reg = _good_registry()
        reg["work_items"][0]["predecessors"] = ["NOPE"]
        issues = rcc.validate_schema(reg)
        self.assertTrue(any(i["check_id"] == "registry.schema.cross_ref" and "predecessor" in i["message"] for i in issues))

    def test_cross_ref_stage_unknown(self) -> None:
        reg = _good_registry()
        reg["work_items"][0]["stage"] = "S9"
        issues = rcc.validate_schema(reg)
        self.assertTrue(any(i["check_id"] == "registry.schema.cross_ref" for i in issues))

    def test_issues_are_standardized(self) -> None:
        reg = _good_registry()
        del reg["work_items"][0]["order"]
        issues = rcc.validate_schema(reg)
        self.assertIn("field_path", issues[0])
        self.assertIn("expectation", issues[0])
        self.assertIn("repair_hint", issues[0])
        self.assertEqual(issues[0]["check_family"], "registry_contract")


class ClosureValidationTest(unittest.TestCase):
    def test_parse_frontmatter_fields(self) -> None:
        text = "---\nartifact_id: BG-001\nstatus: draft\nfoo: true\n---\n# Body"
        self.assertEqual(rcc._parse_frontmatter_fields(text), {"artifact_id", "status", "foo"})

    def test_string_literals_in_py(self) -> None:
        src = 'fm = {"artifact_id": "x"}\nprint(fm.get("status"))\n'
        self.assertTrue("artifact_id" in rcc._string_literals_in_py(src))
        self.assertTrue("status" in rcc._string_literals_in_py(src))

    def test_clean_closure_no_issues(self) -> None:
        # No templates shipped → closure trivially passes
        reg = _good_registry()
        self.assertEqual(rcc.validate_template_validator_closure(reg), [])

    def test_e3_drift_flagged(self) -> None:
        # Skill ships a template whose field never appears in the validator.
        # locate_skill_dirs resolves skill_path against rcc.PROJECT, so patch
        # PROJECT to a temp root and register the skill relative to it.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            old_project = rcc.PROJECT
            rcc.PROJECT = Path(tmp)
            try:
                skill = Path(tmp) / "skills" / "wi1"
                (skill / "scripts").mkdir(parents=True)
                (skill / "templates").mkdir()
                (skill / "templates" / "a.md").write_text("---\ndrift_field_alpha_42: 1\n---\n", encoding="utf-8")
                (skill / "scripts" / "validate_artifact.py").write_text(
                    'print("ok")\n', encoding="utf-8")
                reg = _good_registry()
                reg["work_items"][0]["skill_path"] = "skills/wi1"
                issues = rcc.validate_template_validator_closure(reg)
                self.assertTrue(any(
                    i["check_id"] == "registry.closure.e3_drift" and "drift_field_alpha_42" in i["message"]
                    for i in issues))
            finally:
                rcc.PROJECT = old_project


class RealRegistryTest(unittest.TestCase):
    def test_real_registry_passes(self) -> None:
        reg = json.loads(rcc.REGISTRY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(rcc.validate_schema(reg), [])
        self.assertEqual(rcc.validate_template_validator_closure(reg), [])


if __name__ == "__main__":
    unittest.main()
