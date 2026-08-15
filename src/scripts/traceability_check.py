#!/usr/bin/env python3
"""Validate explicit G→ST→FEA→FUN→AC/BR relationships across artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from validation_errors import make_issue
from workflow_registry import find_artifact, work_items

FAMILY = "traceability"

PATTERNS = {
    "goal": r"\bG\d+\b",
    "story": r"\bST-\d+\b",
    "feature": r"\bFEA-\d+\b",
    "function": r"\bFUN-\d+\b",
    "acceptance": r"\bAC-\d+\b",
    "rule": r"\bBR-\d+\b",
}
REQUIRED_EDGES = [
    ("story", "goal"),
    ("feature", "story"),
    ("function", "feature"),
    ("acceptance", "function"),
    ("rule", "function"),
]
CROSS_LEVEL_EDGES = [
    ("acceptance", "goal"),  # G↔AC: each acceptance criterion should reference the goal it validates
]
# Reverse direction: every upstream ID must be referenced by some downstream ID
# (no orphan goals / stories / features / functions that nothing traces to).
REVERSE_EDGES = [
    ("goal", "story"),
    ("story", "feature"),
    ("feature", "function"),
    ("function", "acceptance"),
    ("function", "rule"),
]


def collect(req_dir: Path) -> tuple[dict[str, set[str]], set[tuple[str, str]], dict[str, str]]:
    ids = {kind: set() for kind in PATTERNS}
    edges: set[tuple[str, str]] = set()
    locations = {}
    for item in work_items():
        artifact = find_artifact(req_dir, item)
        if not artifact:
            continue
        for line_no, line in enumerate(artifact.read_text(encoding="utf-8").splitlines(), 1):
            # Table rows: connect IDs across the entire row (columns represent relationships)
            if line.lstrip().startswith("|") and "---" not in line:
                row_ids = {}
                for kind, pattern in PATTERNS.items():
                    found = set(re.findall(pattern, line))
                    row_ids[kind] = found
                    ids[kind].update(found)
                    for identifier in found:
                        locations.setdefault(identifier, f"{artifact.relative_to(req_dir).as_posix()}:{line_no}")
                for downstream, upstream in REQUIRED_EDGES + CROSS_LEVEL_EDGES:
                    for child in row_ids[downstream]:
                        for parent in row_ids[upstream]:
                            edges.add((child, parent))
            else:
                # Non-table lines: connect IDs that appear together
                line_ids = {}
                for kind, pattern in PATTERNS.items():
                    found = set(re.findall(pattern, line))
                    line_ids[kind] = found
                    ids[kind].update(found)
                    for identifier in found:
                        locations.setdefault(identifier, f"{artifact.relative_to(req_dir).as_posix()}:{line_no}")
                for downstream, upstream in REQUIRED_EDGES + CROSS_LEVEL_EDGES:
                    for child in line_ids[downstream]:
                        for parent in line_ids[upstream]:
                            edges.add((child, parent))
    return ids, edges, locations


def validate(req_dir: Path) -> dict:
    ids, edges, locations = collect(req_dir)
    issues: list[dict[str, Any]] = []
    for downstream, upstream in REQUIRED_EDGES:
        upstream_ids = ids[upstream]
        downstream_ids = ids[downstream]
        if not downstream_ids:
            issues.append(make_issue(
                severity="CRITICAL", check_id=f"traceability.required_edges.no_{downstream}",
                family=FAMILY, location=str(req_dir),
                field_path=f"ids.{downstream}",
                message=f"No {downstream} IDs found",
                expected=f"产物中必须出现至少一个 {downstream} ID（{PATTERNS[downstream]}）",
                actual=f"全文未匹配到任何 {downstream} ID",
                repair_hint=f"在对应的产物章节为每个功能/规则补充 {downstream} 编号",
                source_ref="traceability_check §REQUIRED_EDGES",
            ))
            continue
        if not upstream_ids:
            issues.append(make_issue(
                severity="CRITICAL", check_id=f"traceability.required_edges.no_{upstream}",
                family=FAMILY, location=str(req_dir),
                field_path=f"ids.{upstream}",
                message=f"No {upstream} IDs found",
                expected=f"产物中必须出现至少一个 {upstream} ID（{PATTERNS[upstream]}）",
                actual=f"全文未匹配到任何 {upstream} ID",
                repair_hint=f"在对应的产物章节补充 {upstream} 编号（业务背景/用户故事章节）",
                source_ref="traceability_check §REQUIRED_EDGES",
            ))
            continue
        linked_children = {child for child, parent in edges if child in downstream_ids and parent in upstream_ids}
        for orphan in sorted(downstream_ids - linked_children):
            loc = locations.get(orphan) or str(req_dir)
            issues.append(make_issue(
                severity="CRITICAL", check_id="traceability.required_edges.orphan",
                family=FAMILY, location=loc,
                field_path=f"ids.{downstream}.{orphan}",
                message=f"{orphan} has no explicit {upstream} link on the same traceability row or statement",
                expected=f"{downstream} 编号 '{orphan}' 必须与 {upstream} 编号出现在同一行/同一句（显式链路）",
                actual=f"{orphan} 出现在 {loc}，但该行/句无任何 {upstream} 编号",
                repair_hint=f"在 '{orphan}' 出现的表格行或描述句中补充其上游 {upstream} 编号（如 G1/ST-001）",
                source_ref="traceability_check §REQUIRED_EDGES",
            ))
    for downstream, upstream in CROSS_LEVEL_EDGES:
        upstream_ids = ids[upstream]
        downstream_ids = ids[downstream]
        if not downstream_ids or not upstream_ids:
            continue
        linked = {child for child, parent in edges if child in downstream_ids and parent in upstream_ids}
        for orphan in sorted(downstream_ids - linked):
            loc = locations.get(orphan) or str(req_dir)
            issues.append(make_issue(
                severity="HIGH", check_id="traceability.cross_level.orphan",
                family=FAMILY, location=loc,
                field_path=f"ids.{downstream}.{orphan}",
                message=f"{orphan} has no explicit {upstream} link — verify this AC validates the correct business goal",
                expected=f"每条 AC 都应显式引用其验证的业务目标 {upstream}（跨层校验）",
                actual=f"{orphan} 出现在 {loc}，同一行/句未引用任何 {upstream}",
                repair_hint=f"为 '{orphan}' 补充其验证的 {upstream} 编号（如在 AC 表格补充 G1 列引用）",
                source_ref="traceability_check §CROSS_LEVEL_EDGES",
            ))
    # Reverse traceability: every upstream ID must be consumed by some downstream.
    for upstream, downstream in REVERSE_EDGES:
        upstream_ids = ids[upstream]
        downstream_ids = ids[downstream]
        if not upstream_ids:
            continue
        referenced = {parent for child, parent in edges if child in downstream_ids and parent in upstream_ids}
        for orphan in sorted(upstream_ids - referenced):
            loc = locations.get(orphan) or str(req_dir)
            issues.append(make_issue(
                severity="MEDIUM", check_id="traceability.reverse_edges.orphan",
                family=FAMILY, location=loc,
                field_path=f"ids.{upstream}.{orphan}",
                message=f"{orphan} is not referenced by any {downstream} — reverse traceability gap",
                expected=f"每个 {upstream} 编号 '{orphan}' 至少被一个 {downstream} 引用（反向可追溯）",
                actual=f"{orphan} 出现在 {loc}，但没有任何 {downstream} 引用它",
                repair_hint=f"确认 '{orphan}' 是否仍有下游产物引用；若是孤立项（已废弃/未落地），在产物中删除或标注废弃",
                source_ref="traceability_check §REVERSE_EDGES",
                blocking=False,
            ))
    return {
        "ok": not any(issue["severity"] in {"CRITICAL", "HIGH"} for issue in issues),
        "counts": {kind: len(values) for kind, values in ids.items()},
        "edge_count": len(edges),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("req_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.req_dir.is_dir():
        print(f"ERROR: {args.req_dir} is not a directory", file=sys.stderr)
        return 1
    result = validate(args.req_dir)
    if args.json:
        from validation_errors import aggregate_by_check_id
        result = dict(result)
        result["aggregate_by_check_id"] = aggregate_by_check_id([result["issues"]])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        from validation_errors import format_issue
        print(f"Traceability: {'PASS' if result['ok'] else 'FAIL'}")
        print(f"Counts: {result['counts']} edges={result['edge_count']}")
        for issue in result["issues"]:
            print(f"  [{issue['severity']}] {format_issue(issue)}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
