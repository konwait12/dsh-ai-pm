#!/usr/bin/env python3
"""issue-record pipeline-gate tests.

issue-record（跨阶段问题清单）是「每个案例必备的稳定产物」：machine_gate()
强制检查 99-review/support/issue-record.md 存在，并运行
src/shared/clarify/skills/issue-record/scripts/validate_artifact.py 校验
（frontmatter + §1-§13），缺失或 ok=False 均 gate 失败。

复用 test_workflow_runtime 的模块级辅助函数
（write_reviewer_registry / write_valid_issue_record / build_gate_req）。
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from test_workflow_runtime import build_gate_req, write_valid_issue_record

import pipeline
import workflow_registry


class IssueRecordGateTest(unittest.TestCase):
    def test_machine_gate_missing_issue_record_fails(self) -> None:
        """缺失 99-review/support/issue-record.md → gate 失败（error）"""
        with tempfile.TemporaryDirectory() as temp:
            req = build_gate_req(Path(temp))
            result = pipeline.machine_gate(
                req, workflow_registry.resolve_work_item("project-background-goal"),
            )
            self.assertFalse(result["ok"])
            self.assertFalse(result["issue_record"]["ok"])
            self.assertIn("不存在", result["issue_record"]["error"])
            self.assertIn("issue-record", result["issue_record"]["error"])

    def test_machine_gate_simplified_issue_record_fails(self) -> None:
        """简化版 issue-record（缺 frontmatter + §1-§13）→ 校验失败 → gate 失败"""
        with tempfile.TemporaryDirectory() as temp:
            req = build_gate_req(Path(temp))
            support = req / "99-review" / "support"
            support.mkdir(parents=True, exist_ok=True)
            (support / "issue-record.md").write_text(
                "# 跨阶段问题清单 (Issue Record)\n\n"
                "## 阶段收口表\n\n"
                "| 阶段 | work item | 收口状态 |\n|---|---|---|\n"
                "| 001-business-requirements | project-background-goal | 收口 |\n",
                encoding="utf-8",
            )
            result = pipeline.machine_gate(
                req, workflow_registry.resolve_work_item("project-background-goal"),
            )
            self.assertFalse(result["ok"])
            self.assertFalse(result["issue_record"]["ok"])
            self.assertTrue(result["issue_record"]["errors"])
            self.assertIn(
                "Missing frontmatter fields",
                result["issue_record"]["errors"][0],
            )

    def test_machine_gate_valid_issue_record_passes(self) -> None:
        """完整版 issue-record（frontmatter + §1-§13 + bg 收口行）→ 校验通过 → gate 通过"""
        with tempfile.TemporaryDirectory() as temp:
            req = build_gate_req(Path(temp))
            write_valid_issue_record(req)
            result = pipeline.machine_gate(
                req, workflow_registry.resolve_work_item("project-background-goal"),
            )
            self.assertTrue(result["issue_record"]["ok"], result["issue_record"])
            self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
