#!/usr/bin/env python3
"""Validate a change proposal before it can be submitted for approval.

Checks:
1. Proposal has all required sections (动机/影响范围/变更内容/回滚计划/审批)
2. Affected artifacts exist in registry
3. ADDED/MODIFIED/REMOVED sections are non-empty (at least one change)
4. Downstream cascade impact is explicitly listed
5. Reviewers match registry reviewer_roles for affected work items
6. Proposal ID format is valid (CHG-NNN)

Exit 0 = valid, 1 = invalid.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
REGISTRY = PROJECT / "src/framework/workflow-registry.json"

REQUIRED_SECTIONS = [
    "动机",
    "影响范围",
    "变更内容",
    "回滚计划",
    "审批",
]

CHANGE_TYPES = ["ADDED", "MODIFIED", "REMOVED"]


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def validate_proposal(proposal_path: Path, registry: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not proposal_path.exists():
        errors.append(f"Proposal file not found: {proposal_path}")
        return errors, warnings

    content = proposal_path.read_text(encoding="utf-8")

    # Check required sections (flexible: match "## 1. 动机 (Why)", "## 动机", "# 动机", etc.)
    for section in REQUIRED_SECTIONS:
        found = False
        for line in content.split("\n"):
            stripped = line.strip()
            # Strip markdown heading markers and common numbering patterns
            if stripped.startswith("#"):
                # Remove ##, ###, numbering like "1.", "1. ", "(1)", and parenthetical suffixes like "(Why)"
                import re as re2
                heading_text = re2.sub(r'^#+\s*', '', stripped)
                heading_text = re2.sub(r'^\d+[\.\、\)]\s*', '', heading_text)
                heading_text = re2.sub(r'\s*\([^)]*\)$', '', heading_text).strip()
                if section in heading_text:
                    found = True
                    break
        if not found:
            errors.append(f"Missing required section: {section}")

    # Check proposal ID (accept placeholders like CHG-{NNN} as template; warn not error)
    pid_match = re.search(r"proposal_id:\s*(CHG[-\{]\S+)", content)
    if not pid_match:
        errors.append("Missing or invalid proposal_id (expected CHG-NNN)")
    else:
        pid = pid_match.group(1)
        if "{" in pid:
            warnings.append(f"proposal_id contains placeholder: {pid} (template — fill in before submission)")
        elif not re.match(r"^CHG-\d{3,}$", pid):
            errors.append(f"Invalid proposal_id format: {pid} (expected CHG-NNN)")

    # Check at least one change section has content
    has_change = False
    for ct in CHANGE_TYPES:
        section_start = content.find(f"### {ct}")
        if section_start == -1:
            continue
        # Find the table rows after this section
        next_section = min(
            [content.find(f"### {c}", section_start + 1) for c in CHANGE_TYPES if content.find(f"### {c}", section_start + 1) != -1]
            + [content.find("## ", section_start + 1) if content.find("## ", section_start + 1) != -1 else len(content)]
        )
        section_text = content[section_start:next_section]
        # Count table rows (lines starting with | that aren't headers/separators)
        rows = [l for l in section_text.split("\n") if l.strip().startswith("|") and "---" not in l and l.strip() != "|"]
        if len(rows) > 0:
            has_change = True
            break

    if not has_change:
        errors.append("No change entries found in ADDED/MODIFIED/REMOVED sections")

    # Check affected artifacts exist in registry
    artifact_ids = {at["id"] for at in registry.get("artifact_types", [])}
    affected = re.findall(r"Artifact ID.*?\|\s*([A-Z]+-\S+)", content)
    for aid in affected:
        if aid not in artifact_ids:
            warnings.append(f"Affected artifact '{aid}' not found in registry artifact_types")

    # Check downstream cascade
    if "级联失效" not in content and "cascade" not in content.lower():
        warnings.append("No downstream cascade impact listed — confirm this change has no downstream effects")

    # Check reviewer roles
    work_item_ids = {wi["id"] for wi in registry.get("work_items", [])}
    reviewer_section = content.find("## 审批")
    if reviewer_section != -1:
        for wi_id in work_item_ids:
            if wi_id in content[reviewer_section:]:
                wi = next((w for w in registry["work_items"] if w["id"] == wi_id), None)
                if wi:
                    roles = wi.get("reviewer_roles", [])
                    for role in roles:
                        if role not in content[reviewer_section:]:
                            warnings.append(f"Reviewer role '{role}' (required for {wi_id}) not found in approval section")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 change-validator.py <proposal.md> [--json]", file=sys.stderr)
        sys.exit(2)

    proposal_path = Path(sys.argv[1])
    use_json = "--json" in sys.argv

    registry = load_registry()
    errors, warnings = validate_proposal(proposal_path, registry)

    if use_json:
        import json as j
        print(j.dumps({"ok": len(errors) == 0, "errors": errors, "warnings": warnings}, ensure_ascii=False))
    else:
        for e in errors:
            print(f"ERROR: {e}")
        for w in warnings:
            print(f"WARNING: {w}")
        if not errors:
            print("Proposal is valid.")

    sys.exit(0 if len(errors) == 0 else 1)


if __name__ == "__main__":
    main()
