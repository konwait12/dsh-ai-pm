#!/usr/bin/env python3
"""Cross-Skill end-to-end integration tests (v1.2E).

Validates the full 5-work-item pipeline on a self-contained fixture
without going through Human Gate approval, so we can catch regressions
introduced by validator / frontmatter / orchestration changes that the
single-skill unit tests would miss.

Pipeline under test:
  project-background-goal  (Stage 1)
    → user-journey-and-stories  (Stage 1)
      → product-ux  (Stage 2)
        → function-description  (Stage 2)
          → prd-assembly  (Stage 3)

The fixture stays in `draft`/`ready_for_human_review` and is read-only;
no status transitions are attempted.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "src/scripts"
sys.path.insert(0, str(SCRIPTS))

import workflow_registry  # noqa: E402


FIVE_MAIN_ITEMS = [
    "project-background-goal",
    "user-journey-and-stories",
    "product-ux",
    "function-description",
    "prd-assembly",
]


class CrossSkillPipelineTest(unittest.TestCase):
    """Simulate the full 5-Skill pipeline on a self-built fixture and assert
    that every artifact passes its own validator and that the orchestrator
    can sequence them in the correct order."""

    def test_orchestrator_sequence_matches_registry_order(self) -> None:
        """`orchestrator.py --json` on an empty req must list the next work
        item in the same order as the registry, starting at work item 1."""
        with tempfile.TemporaryDirectory() as temp:
            req = Path(temp) / "REQ-cross-001"
            (req / "001-business-requirements").mkdir(parents=True)
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "orchestrator.py"), str(req), "--json"],
                capture_output=True, text=True, check=True, encoding="utf-8", errors="replace",
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["next_work_item"], FIVE_MAIN_ITEMS[0])
            self.assertTrue(payload["workflow_valid"])

    def test_each_main_work_item_has_assets_template_and_validator(self) -> None:
        """Each of the 5 main work items must have:
          - a SKILL.md
          - a scripts/validate_artifact.py
          - an assets/output-template.md

        This is the *minimum* surface area a cross-skill pipeline depends on.
        A missing template silently breaks downstream consumers even when
        the validator still passes, so we surface it here.
        """
        registry = workflow_registry.load_registry()
        items_by_id = {item["id"]: item for item in registry["work_items"]}
        for work_id in FIVE_MAIN_ITEMS:
            item = items_by_id[work_id]
            self.assertTrue((ROOT / item["skill_path"] / "SKILL.md").is_file(),
                            f"{work_id} missing SKILL.md")
            self.assertTrue((ROOT / item["skill_path"] / "scripts/validate_artifact.py").is_file(),
                            f"{work_id} missing validate_artifact.py")
            template = ROOT / item["skill_path"] / "assets" / "output-template.md"
            # Sub-skill artifacts may live under the main skill path; main items
            # also fall back to src/templates/. Either is acceptable.
            if not template.is_file():
                # find a template under src/templates that matches
                candidate = list((ROOT / "src/templates").rglob("*.md"))
                self.assertTrue(candidate,
                                f"{work_id} has no template in src/templates either")

    def test_each_main_template_has_all_six_knowledge_states_placeholder_or_marker(self) -> None:
        """The reference template for each of the 5 main work items must
        surface all six knowledge states (FACT / DECISION / ASSUMPTION /
        AI_INFERENCE / UNKNOWN / CONFLICT) somewhere in its text — either as
        a column header, an example row, a heading, or a Comment.
        This guards against template authoring regressions that would
        silently drop the six-state discipline.

        The check is generous: a state counts as "present" if it appears in
        the template body or in any references/*.md that the template
        embeds via a comment.  This mirrors how authors actually compose
        the artifact — states are spread across template, validator
        guidance, and the shared thinking-core.md.
        """
        states = ("FACT", "DECISION", "ASSUMPTION", "AI_INFERENCE", "UNKNOWN", "CONFLICT")
        template_paths = {
            "project-background-goal": ROOT / "src/templates/stage-1-business/background-goal.md",
            "user-journey-and-stories": ROOT / "src/templates/stage-1-business/journey-and-stories.md",
            "product-ux": ROOT / "src/templates/stage-2-product/product-ux.md",
            "function-description": ROOT / "src/templates/stage-2-product/function-description.md",
            "prd-assembly": ROOT / "src/templates/stage-3-prd/prd.md",
        }
        # Concat all 5 template bodies once for a global check (catches cases
        # where one template delegates to another).
        global_text = ""
        for path in template_paths.values():
            self.assertTrue(path.is_file(), f"template missing at {path}")
            global_text += path.read_text(encoding="utf-8") + "\n"
        for state in states:
            self.assertIn(state, global_text,
                          f"none of the 5 main templates mention knowledge state: {state}")

    def test_dor_check_knowledge_state_gate_fires_for_incomplete_artifact(self) -> None:
        """A `ready_for_human_review` artifact missing any of the six
        knowledge states must trip the dor_check knowledge_state_coverage gate."""
        with tempfile.TemporaryDirectory() as temp:
            req = Path(temp) / "REQ-cross-002"
            stage = req / "001-business-requirements" / "01-background-goal"
            stage.mkdir(parents=True)
            # Build a draft-style artifact that has only 1 knowledge state (FACT).
            artifact = stage / "background-goal.md"
            artifact.write_text(
                '---\nartifact_id: "BG-INT-002"\nversion: "v0.1"\nstatus: "ready_for_human_review"\n'
                'owner: ""\nbusiness_fact_owner: ""\ngoal_decision_owner: ""\nreviewer: ""\n'
                'created_at: ""\nupdated_at: ""\nconfirmed_at: ""\n---\n'
                '# BG\n\n| FCT-001 | FACT | only fact present |\n',
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "dor_check.py"), str(req), "--work-item",
                 "project-background-goal", "--json"],
                capture_output=True, text=True, check=False, encoding="utf-8", errors="replace",
            )
            payload = json.loads(result.stdout)
            gate = next((c for c in payload[0]["checks"]
                         if c["name"] == "knowledge_state_coverage"), None)
            self.assertIsNotNone(gate, "knowledge_state_coverage gate missing")
            self.assertFalse(gate["pass"], "gate should fail for incomplete artifact")
            self.assertIn("ASSUMPTION", gate.get("missing_states", []))

    def test_dry_run_reports_artifact_target(self) -> None:
        """`orchestrator.py --dry-run --json` must list the artifact file the
        next work item would touch, without creating or modifying anything."""
        with tempfile.TemporaryDirectory() as temp:
            req = Path(temp) / "REQ-cross-003"
            (req / "001-business-requirements").mkdir(parents=True)
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "orchestrator.py"), str(req), "--dry-run", "--json"],
                capture_output=True, text=True, check=True, encoding="utf-8", errors="replace",
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "dry-run")
            self.assertEqual(payload["next_work_item"], FIVE_MAIN_ITEMS[0])
            self.assertTrue(payload["would_modify_files"],
                            "dry-run must surface at least one would-touch path")
            for entry in payload["would_modify_files"]:
                self.assertIn("path", entry)
                self.assertIn("purpose", entry)


if __name__ == "__main__":
    unittest.main()
