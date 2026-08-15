#!/usr/bin/env python3
"""Unit tests for validation_errors.py (Harness 借鉴点四·统一错误格式)."""

import json
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent.parent / "src/scripts"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import validation_errors as ve


class MakeIssueTest(unittest.TestCase):
    def test_blocking_defaults_by_severity(self) -> None:
        # CRITICAL/HIGH block by default; MEDIUM/INFO do not.
        self.assertTrue(ve.make_issue("CRITICAL", "a", "f", "l")["blocking"])
        self.assertTrue(ve.make_issue("HIGH", "a", "f", "l")["blocking"])
        self.assertFalse(ve.make_issue("MEDIUM", "a", "f", "l")["blocking"])
        self.assertFalse(ve.make_issue("INFO", "a", "f", "l")["blocking"])

    def test_explicit_blocking_override(self) -> None:
        self.assertFalse(ve.make_issue("HIGH", "a", "f", "l", blocking=False)["blocking"])
        self.assertTrue(ve.make_issue("MEDIUM", "a", "f", "l", blocking=True)["blocking"])

    def test_invalid_severity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ve.make_issue("blocking", "a", "f", "l")  # lowercase legacy severity

    def test_message_auto_derived_from_expected_actual(self) -> None:
        issue = ve.make_issue("HIGH", "a", "f", "l", expected="E", actual="A")
        self.assertIn("期望: E", issue["message"])
        self.assertIn("实际: A", issue["message"])
        self.assertEqual(issue["expectation"], "E")
        self.assertEqual(issue["actual"], "A")

    def test_all_optional_fields_present(self) -> None:
        issue = ve.make_issue(
            "HIGH", "check.id", "family", "loc.md",
            field_path="tables.BR-001", message="m",
            expected="e", actual="a", repair_hint="r", source_ref="s", blocking=False,
        )
        self.assertEqual(issue["check_id"], "check.id")
        self.assertEqual(issue["check_family"], "family")
        self.assertEqual(issue["field_path"], "tables.BR-001")
        self.assertEqual(issue["repair_hint"], "r")
        self.assertEqual(issue["source_ref"], "s")

    def test_explicit_message_wins(self) -> None:
        issue = ve.make_issue("INFO", "a", "f", "l", message="explicit", expected="E")
        self.assertEqual(issue["message"], "explicit")


class WrapUnexpectedTest(unittest.TestCase):
    def test_no_traceback_leak(self) -> None:
        issue = ve.wrap_unexpected(RuntimeError("boom"), check_id="x", family="f", location="l")
        self.assertEqual(issue["check_id"], "x.unexpected_exception")
        self.assertEqual(issue["severity"], "CRITICAL")
        self.assertIn("RuntimeError", issue["actual"])
        self.assertNotIn("Traceback", json.dumps(issue))


class FormatIssueTest(unittest.TestCase):
    def test_format_contains_expect_actual_repair(self) -> None:
        issue = ve.make_issue(
            "HIGH", "state.no_outgoing", "property_check", "fd.md",
            field_path="sections.states.A", expected="non-terminal must have outgoing",
            actual="0 rows", repair_hint="add a row",
        )
        out = ve.format_issue(issue)
        self.assertIn("state.no_outgoing", out)
        self.assertIn("fd.md", out)
        self.assertIn("期望: non-terminal must have outgoing", out)
        self.assertIn("实际: 0 rows", out)
        self.assertIn("修复: add a row", out)


class AggregateTest(unittest.TestCase):
    def test_grouping_counts_and_samples(self) -> None:
        a = ve.make_issue("HIGH", "c1", "f", "l", message="m1")
        b = ve.make_issue("MEDIUM", "c1", "f", "l", message="m2")
        c = ve.make_issue("INFO", "c2", "f", "l", message="m3")
        agg = ve.aggregate_by_check_id([[a, b], [c]])
        self.assertEqual(agg["c1"]["count"], 2)
        self.assertEqual(agg["c1"]["severities"], {"HIGH": 1, "MEDIUM": 1})
        self.assertEqual(agg["c2"]["count"], 1)
        self.assertEqual(len(agg["c1"]["samples"]), 2)

    def test_samples_capped_at_three(self) -> None:
        issues = [ve.make_issue("HIGH", "c", "f", "l", message=f"m{i}") for i in range(5)]
        agg = ve.aggregate_by_check_id([issues])
        self.assertEqual(len(agg["c"]["samples"]), 3)


if __name__ == "__main__":
    unittest.main()
