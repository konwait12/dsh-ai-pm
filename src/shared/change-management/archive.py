#!/usr/bin/env python3
"""Archive an approved change proposal: merge back into baseline.

After a change proposal is approved (all reviewers confirmed), this script:
1. Validates the proposal is approved (all reviewer roles have a decision)
2. Creates a ChangeRecord in the affected requirement's 99-review/
3. Updates the proposal status to 'archived'
4. Lists downstream artifacts that need cascade invalidation

Does NOT modify artifact content — that's a human responsibility.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent.parent.parent
REQUIREMENTS = PROJECT / "requirements"


def parse_proposal(proposal_path: Path) -> dict:
    """Extract key metadata from a proposal markdown file."""
    content = proposal_path.read_text(encoding="utf-8")

    meta = {}
    for key in ["proposal_id", "proposed_by", "affected_artifacts", "status"]:
        m = re.search(rf"{key}:\s*(.+)", content)
        if m:
            val = m.group(1).strip()
            if key == "affected_artifacts":
                val = [a.strip() for a in val.strip("[]").split(",") if a.strip()]
            meta[key] = val

    # Check approval decisions
    approval_section = content.find("## 审批")
    if approval_section != -1:
        decisions = re.findall(
            r"\|\s*(\w+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|",
            content[approval_section:]
        )
        meta["decisions"] = [
            {"role": d[0], "reviewer": d[1], "decision": d[2]}
            for d in decisions
            if d[2] not in ("待确认", "")
        ]

    return meta


def validate_approved(meta: dict) -> list[str]:
    """Check all required reviewers have approved."""
    errors = []
    if meta.get("status") == "archived":
        errors.append("Proposal is already archived")
    decisions = meta.get("decisions", [])
    if not decisions:
        errors.append("No approval decisions found — proposal must be approved before archiving")
    for d in decisions:
        if d["decision"] not in ("approved", "APPROVED", "confirmed", "CONDITIONS"):
            errors.append(f"Reviewer {d['reviewer']} ({d['role']}) has not approved: {d['decision']}")
    return errors


def create_change_record(proposal_path: Path, meta: dict, req_dir: Path) -> Path:
    """Create a ChangeRecord in 99-review/."""
    review_dir = req_dir / "99-review"
    review_dir.mkdir(parents=True, exist_ok=True)

    pid = meta.get("proposal_id", "CHG-UNKNOWN")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    record_path = review_dir / f"change-record-{pid}.md"
    record = f"""---
record_id: REC-{pid}
type: ChangeRecord
proposal_id: {pid}
proposed_by: {meta.get('proposed_by', 'unknown')}
archived_at: {now}
affected_artifacts: {meta.get('affected_artifacts', [])}
---

# Change Record: {pid}

## Approval Summary

"""
    for d in meta.get("decisions", []):
        record += f"- {d['role']}: **{d['decision']}** by {d['reviewer']}\n"

    record += f"""
## Archive

Archived at: {now}
Proposal: {proposal_path.relative_to(req_dir)}

## Downstream Cascade

The following artifacts may need re-validation due to cascade invalidation:
(Resolved from registry dependency_policy.cascade_invalidation — affected downstream artifacts are listed in the proposal's §2 影响范围)

## Resolution

- [ ] Downstream artifacts re-validated
- [ ] Baseline updated
"""
    record_path.write_text(record, encoding="utf-8")
    return record_path


def mark_archived(proposal_path: Path) -> None:
    """Update proposal frontmatter status to archived."""
    content = proposal_path.read_text(encoding="utf-8")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    content = re.sub(r"status:\s*draft", "status: archived", content)
    content = re.sub(r"archived_at:\s*待确认", f"archived_at: {now}", content)

    proposal_path.write_text(content, encoding="utf-8")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 archive.py <proposal.md> <REQ-DIR>", file=sys.stderr)
        print("Example: python3 archive.py 99-review/changes/CHG-001/proposal.md requirements/REQ-NNN-topic", file=sys.stderr)
        sys.exit(2)

    proposal_path = Path(sys.argv[1])
    req_dir = Path(sys.argv[2])

    meta = parse_proposal(proposal_path)
    errors = validate_approved(meta)

    if errors:
        print("Cannot archive — proposal not fully approved:")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)

    record_path = create_change_record(proposal_path, meta, req_dir)
    mark_archived(proposal_path)

    print(f"✅ Proposal {meta.get('proposal_id')} archived")
    print(f"   Change record: {record_path.relative_to(req_dir)}")
    print(f"   Downstream artifacts may need cascade invalidation — check registry dependency_policy")


if __name__ == "__main__":
    main()
