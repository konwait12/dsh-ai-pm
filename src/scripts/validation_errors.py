#!/usr/bin/env python3
"""Unified error-format helpers for all validators (Harness借鉴点四).

All validators should use :func:`make_issue` for every issue they emit so the
output shape is consistent across scripts::

    {
        "severity":      "CRITICAL" | "HIGH" | "MEDIUM" | "INFO",  # capital tag
        "blocking":      true,               # false → notice only (not counted in FAIL)
        "check_id":      "minimum_threshold" # stable machine-readable check tag
        "check_family":  "property_check",   # validator family (for grouping)
        "location":      "path/to/file.md"   # artifact path relative to req_dir
        "field_path":    "frontmatter.status"| "table.BR-007.规则内容" | "sections.3",
        "message":       "human-readable one-liner",
        "expectation":   "期望: status 必须是 ready_for_human_review 或 confirmed",
        "actual":        "实际: status='drafted' (unknown state token)",
        "repair_hint":   "修复: 确认产物 frontmatter 的 status 字段拼写正确；若产物刚起草，状态应为 draft",
        "source_ref":    "SRC-003 / DEC-007" | "(来源于 thinking-core.md 宪法 §3)",
    }

Why this shape:
  - ``check_id`` is stable across code refactors so users can track recurrence
    (run_tests 按 check_id 归类便于回归跟踪).
  - ``expectation`` / ``actual`` separate what's wanted from what was found,
    which is the core of a "fail loud, precise" report. No more "something is
    wrong" stack-trace-y messages.
  - ``repair_hint`` is actionable: not just "X is missing" but HOW to fix it.
  - Raw Python traces are NEVER shown to users; every error is wrapped in
    this contract by callers (use :func:`wrap_unexpected` for exceptions).

Usage in validators::

    from validation_errors import make_issue

    issues.append(make_issue(
        severity="HIGH",
        check_id="state_machine.no_outgoing",
        family="property_check",
        location=str(artifact.relative_to(req_dir)),
        field_path=f"sections.状态变化.states.{state_name}",
        message=f"State '{state_name}' has no outgoing transitions",
        expected=f"Non-terminal states must define at least one 触发事件 → 目标状态 row",
        actual=f"{state_name} currently has 0 outgoing rows in 状态变化 table",
        repair=f"在 状态变化 表格中为 '{state_name}' 添加至少一个触发事件（如用户点击提交、超时、审批通过等）",
        source_ref="output-contract: property_check §状态机穷尽性",
    ))
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "INFO"}


def make_issue(
    severity: str,
    check_id: str,
    family: str,
    location: str,
    *,
    field_path: str | None = None,
    message: str | None = None,
    expected: str | None = None,
    actual: str | None = None,
    repair_hint: str | None = None,
    source_ref: str | None = None,
    blocking: bool | None = None,
) -> dict[str, Any]:
    """Build a standard validator issue dict.

    ``severity`` must be one of VALID_SEVERITIES. CRITICAL = never waiveable
    (hard-constitutional defect), HIGH = gate-blocking (unless overridden with
    blocking=False for backward-compat notice), MEDIUM = quality warning
    (non-blocking), INFO = diagnostic.

    If ``blocking`` is None it defaults to True for CRITICAL/HIGH, False for
    MEDIUM/INFO so callers rarely need to set it explicitly.
    """
    if severity not in VALID_SEVERITIES:
        raise ValueError(f"severity '{severity}' not in {sorted(VALID_SEVERITIES)}")
    if blocking is None:
        blocking = severity in {"CRITICAL", "HIGH"}
    # Build human one-liner message if caller supplied only expected+actual.
    if not message:
        parts: list[str] = []
        if expected:
            parts.append(f"期望: {expected}")
        if actual:
            parts.append(f"实际: {actual}")
        message = "；".join(parts) or "未指定详情"
    issue: dict[str, Any] = {
        "severity": severity,
        "blocking": bool(blocking),
        "check_id": check_id,
        "check_family": family,
        "location": location,
        "message": message,
    }
    if field_path is not None:
        issue["field_path"] = field_path
    if expected is not None:
        issue["expectation"] = expected
    if actual is not None:
        issue["actual"] = actual
    if repair_hint is not None:
        issue["repair_hint"] = repair_hint
    if source_ref is not None:
        issue["source_ref"] = source_ref
    return issue


def wrap_unexpected(
    exc: Exception,
    *,
    check_id: str,
    family: str,
    location: str,
    severity: str = "CRITICAL",
) -> dict[str, Any]:
    """Wrap a Python exception into a contract issue — no raw traceback leaks."""
    qualname = f"{type(exc).__module__}.{type(exc).__name__}" if type(exc).__module__ else type(exc).__name__
    return make_issue(
        severity=severity,
        check_id=f"{check_id}.unexpected_exception",
        family=family,
        location=location,
        message=f"校验器执行期间发生未预期异常: {qualname}",
        actual=f"{exc.__class__.__name__}: {exc}",
        repair_hint=(
            "此为校验器代码缺陷（非产物问题），请将该错误连同触发命令与产物样本"
            "反馈给维护者；临时规避可跳过该校验子项（需显式 waiver）"
        ),
        source_ref="validation_errors.wrap_unexpected (契约 §错误不泄漏堆栈)",
    )


def format_issue(issue: dict[str, Any]) -> str:
    """One-line human-readable issue string.

    Format (per 借鉴点四 §5.1):
      ``[check_id] location.field_path: expectation vs actual (repair_hint)``
    """
    prefix = f"[{issue.get('check_id','?')}]"
    loc_bits = [issue.get("location", "?")]
    if issue.get("field_path"):
        loc_bits.append(issue["field_path"])
    loc = ":".join(loc_bits)
    body_parts: list[str] = []
    if issue.get("expectation"):
        body_parts.append(f"期望: {issue['expectation']}")
    if issue.get("actual"):
        body_parts.append(f"实际: {issue['actual']}")
    if not body_parts:
        body_parts.append(issue.get("message", ""))
    body = " vs ".join(body_parts) if len(body_parts) == 2 else "；".join(body_parts)
    suffix = ""
    if issue.get("repair_hint"):
        suffix = f"（修复: {issue['repair_hint']}）"
    sev = issue.get("severity", "?")
    return f"{sev:<8} {prefix} {loc}: {body}{suffix}"


def aggregate_by_check_id(issue_lists: list[list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """Aggregate many issue lists into a per-check_id summary for run_tests 汇总.

    Returns::

        { "<check_id>": {
            "family": "property_check",
            "count": N,
            "severities": {"CRITICAL": 2, "HIGH": 5},
            "samples": [first_message, first_message],  # max 3
          }
        }
    """
    agg: dict[str, dict[str, Any]] = {}
    for lst in issue_lists:
        for issue in lst:
            cid = issue.get("check_id", "<missing>")
            if cid not in agg:
                agg[cid] = {
                    "family": issue.get("check_family", "?"),
                    "count": 0,
                    "severities": {},
                    "samples": [],
                }
            bucket = agg[cid]
            bucket["count"] += 1
            sev = issue.get("severity", "?")
            bucket["severities"][sev] = bucket["severities"].get(sev, 0) + 1
            if len(bucket["samples"]) < 3:
                bucket["samples"].append(issue.get("message", ""))
    return agg


def main() -> int:
    """CLI: read one or more JSON issue files (--issue-json path) → pretty summary."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue-json", action="append", default=[],
                        help="path to a validator's --json output file (may repeat)")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    issue_lists: list[list[dict[str, Any]]] = []
    for p in args.issue_json:
        try:
            blob = json.loads(Path(p).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"WARN cannot read {p}: {e}", file=sys.stderr)
            continue
        # Accept either {errors: [...], warnings: [...]} (property_check style)
        # or {issues: [...]} (branch_validator style) or a raw list.
        if isinstance(blob, list):
            issue_lists.append(blob)
        elif isinstance(blob, dict):
            for key in ("errors", "warnings", "issues"):
                if isinstance(blob.get(key), list):
                    issue_lists.append(blob[key])
    agg = aggregate_by_check_id(issue_lists)

    if args.as_json:
        print(json.dumps(agg, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if not agg:
            print("No issues loaded.")
            return 0
        print(f"Issue summary: {len(agg)} distinct check_ids")
        for cid in sorted(agg.keys(), key=lambda k: agg[k]["count"], reverse=True):
            b = agg[cid]
            sevs = ", ".join(f"{k}×{v}" for k, v in sorted(b["severities"].items()))
            print(f"  ×{b['count']:<3} [{b['family']:<18}] {cid:<40} ({sevs})")
            for sample in b["samples"]:
                print(f"      · {sample}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
