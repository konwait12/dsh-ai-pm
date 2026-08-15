#!/usr/bin/env python3
"""Report stage/work-item status and the next valid action.

`--dry-run` is a preview mode: instead of running the pipeline, it prints
the ordered list of work items the next valid action will touch (the
work item to run, its predecessors it will gate on, and the artifact
file paths it will read/write).  No file is modified.  This is the
Human-Gate-friendly companion to the live status report — it lets the
PM/AI see what an approval *would do* before committing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from workflow_registry import artifact_status, find_artifact, load_registry, read_frontmatter, work_items


# Statuses that count as "active" (in progress, awaiting human, etc.)
ACTIVE_STATUSES = {"needs_user_input", "conditional_review", "ready_for_human_review"}


def loop_signals(req_dir: Path, statuses: dict) -> list[dict]:
    """一闸门两分支的信号层：B1 熔断 / B3 老化 / 范围冻结。

    全部是提示信号（不自动执行动作）；B1/B3 的硬门禁在 dor_check。
    """
    signals: list[dict] = []
    review_dir = req_dir / "99-review"

    # B1 纠错熔断：同一 work item 连续 changes ≥3 轮
    streak: dict[str, int] = {}
    if review_dir.is_dir():
        for p in sorted(review_dir.glob("review-*.md")):
            text = p.read_text(encoding="utf-8", errors="ignore")
            m_wi = re.search(r"(?m)^- work_item:\s*(\S+)", text)
            m_dec = re.search(r"(?m)^- decision:\s*(\S+)", text)
            if not (m_wi and m_dec):
                continue
            wi = m_wi.group(1)
            if m_dec.group(1) == "changes":
                streak[wi] = streak.get(wi, 0) + 1
            else:
                streak[wi] = 0
        for wi, n in streak.items():
            if n >= 3:
                signals.append({
                    "loop": "B1",
                    "severity": "escalate",
                    "message": f"{wi} 连续 {n} 轮 changes——停下重新评估修改方向（熔断）",
                })

    # B3 问题老化：open/discussing 问题 7 天 flag / 14 天 escalate
    ir = req_dir / "99-review" / "support" / "issue-record.md"
    if ir.is_file():
        today = datetime.now(timezone.utc).date()
        for line in ir.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "ISS-" not in line or ("open" not in line and "discussing" not in line):
                continue
            m = re.search(r"20\d{2}-\d{2}-\d{2}", line)
            if not m:
                continue
            try:
                age = (today - datetime.strptime(m.group(0), "%Y-%m-%d").date()).days
            except ValueError:
                continue
            if age > 14:
                signals.append({"loop": "B3", "severity": "escalate",
                                "message": f"open 问题超过 14 天未关闭，升级处理：{line.strip()[:50]}"})
                break
            if age > 7:
                signals.append({"loop": "B3", "severity": "flag",
                                "message": f"open 问题超过 7 天，请关注：{line.strip()[:50]}"})
                break

    # 范围冻结：product-ux confirmed 后上游 journey 被重新评审
    if statuses.get("product-ux") == "confirmed" and review_dir.is_dir():
        ux_at = js_at = ""
        for p in sorted(review_dir.glob("review-*.md")):
            text = p.read_text(encoding="utf-8", errors="ignore")
            m_wi = re.search(r"(?m)^- work_item:\s*(\S+)", text)
            m_at = re.search(r"(?m)^- reviewed_at:\s*(\S+)", text)
            if not (m_wi and m_at):
                continue
            if m_wi.group(1) == "product-ux":
                ux_at = m_at.group(1)
            elif m_wi.group(1) == "user-journey-and-stories":
                js_at = m_at.group(1)
        if ux_at and js_at and js_at > ux_at:
            signals.append({
                "loop": "change",
                "severity": "flag",
                "message": "范围冻结：product-ux 确认后 journey 又被评审——变更须走 change-mgmt / reflow",
            })
    return signals


def build_status(req_dir: Path) -> dict:
    items = work_items()
    statuses = {item["id"]: artifact_status(req_dir, item) for item in items}

    # Single-active-item check: at most one active work item may exist.
    active_items = [i for i in items if statuses[i["id"]] in ACTIVE_STATUSES]
    active_sorted = sorted(active_items, key=lambda i: i["order"])
    invalid_active = []
    if len(active_items) > 1:
        # Keep the earliest-order active item; later ones are invalid.
        invalid_active = [i["id"] for i in active_sorted[1:]]

    next_item = None
    blockers = []
    workflow_valid = True
    for item in items:
        # confirmed/legacy_unverified are done-for-now; `superseded` means the
        # artifact was invalidated by an upstream reflow and must be re-validated,
        # so it IS the next work item (its downstream remains DoR-blocked until then).
        if statuses[item["id"]] in ("confirmed", "legacy_unverified"):
            continue
        next_item = item["id"]
        for predecessor in item["predecessors"]:
            p_status = statuses.get(predecessor, "not_created")
            if p_status != "confirmed":
                blockers.append(f"{predecessor} is {p_status}")
                workflow_valid = False
        break

    # Downstream ready-for-review is invalid if it skipped predecessors.
    for item in items:
        if statuses[item["id"]] in ACTIVE_STATUSES:
            for predecessor in item["predecessors"]:
                if statuses.get(predecessor) != "confirmed":
                    workflow_valid = False
                    if item["id"] not in invalid_active:
                        invalid_active.append(item["id"])
                    break

    return {
        "requirement": req_dir.name,
        "schema_version": load_registry()["schema_version"],
        "work_items": statuses,
        "active_work_item": active_sorted[0]["id"] if active_items else None,
        "invalid_active_items": invalid_active,
        "workflow_valid": workflow_valid and not invalid_active,
        "next_work_item": next_item,
        "blocked": bool(blockers),
        "blockers": blockers,
        "complete": next_item is None and not invalid_active,
        "signals": loop_signals(req_dir, statuses),
    }


def build_dry_run(req_dir: Path) -> dict:
    """Plan-only: enumerate the work item the pipeline would advance next,
    the predecessors it will check, and the artifact files it would read
    or write.  Nothing on disk is touched.
    """
    registry = load_registry()
    items_by_id = {item["id"]: item for item in registry["work_items"]}
    status_result = build_status(req_dir)
    next_id = status_result["next_work_item"]
    plan = {
        "requirement": req_dir.name,
        "schema_version": registry["schema_version"],
        "mode": "dry-run",
        "next_work_item": next_id,
        "would_modify_files": [],
        "would_check_predecessors": [],
        "blocked": status_result["blocked"],
        "blockers": status_result["blockers"],
        "complete": status_result["complete"],
        "note": "dry-run: no files were modified",
    }
    if not next_id:
        return plan
    target = items_by_id[next_id]
    # Predecessors the next work item depends on (will be checked, not written)
    plan["would_check_predecessors"] = [
        {"id": pid, "status": status_result["work_items"].get(pid, "not_created")}
        for pid in target["predecessors"]
    ]
    # Artifact file the next work item will read/write
    artifact = find_artifact(req_dir, target)
    if artifact:
        plan["would_modify_files"].append({
            "path": str(artifact.relative_to(req_dir)),
            "purpose": "validate + transition status",
        })
    # Also surface any artifact path the work item *would* create if missing
    if artifact is None:
        # Convention: <req_dir>/<stage>/<work-item>/<artifact-base>.md
        stage_id = target["stage"]
        work_id = target["id"]
        candidate = req_dir / stage_id / work_id / f"{work_id}.md"
        plan["would_modify_files"].append({
            "path": str(candidate.relative_to(req_dir)),
            "purpose": "create new artifact (does not exist yet)",
        })
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("req_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview the next action without modifying any file.")
    args = parser.parse_args()
    if not args.req_dir.is_dir():
        print(f"ERROR: {args.req_dir} is not a directory", file=sys.stderr)
        return 1
    if args.dry_run:
        plan = build_dry_run(args.req_dir)
        if args.json:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
        else:
            print(f"[DRY-RUN] Requirement: {plan['requirement']}")
            print(f"[DRY-RUN] Schema: {plan['schema_version']}")
            if plan["complete"]:
                print("[DRY-RUN] Pipeline is complete. Next: publish confirmed PRD.")
            elif plan["blocked"]:
                print(f"[DRY-RUN] Blocked at {plan['next_work_item']}: {', '.join(plan['blockers'])}")
            else:
                print(f"[DRY-RUN] Next work item: {plan['next_work_item']}")
                if plan["would_check_predecessors"]:
                    print("[DRY-RUN] Will check predecessors:")
                    for p in plan["would_check_predecessors"]:
                        print(f"  - {p['id']}: {p['status']}")
                if plan["would_modify_files"]:
                    print("[DRY-RUN] Will read/write files:")
                    for f in plan["would_modify_files"]:
                        print(f"  - {f['path']}  ({f['purpose']})")
                else:
                    print("[DRY-RUN] No artifact files to modify at this step.")
            print(f"[DRY-RUN] {plan['note']}.")
        return 0
    result = build_status(args.req_dir)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Requirement: {result['requirement']}")
        registry = load_registry()
        by_id = {item["id"]: item for item in registry["work_items"]}
        for stage in registry["stages"]:
            print(f"\n{stage['id']} {stage['name']}")
            for item_id in stage["work_items"]:
                print(f"  {item_id}: {result['work_items'][item_id]}")
        if result["complete"]:
            print("\nNext: publish confirmed PRD")
        elif result["blocked"]:
            print(f"\nBlocked at {result['next_work_item']}: {', '.join(result['blockers'])}")
        else:
            print(f"\nNext: {result['next_work_item']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
