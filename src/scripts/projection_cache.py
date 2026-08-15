#!/usr/bin/env python3
"""Projection cache (materialized view) folded from the event log.

Harness借鉴点二：投影缓存。从事件日志/评审记录折叠出每个 Work Item 的最新
状态：confirmed 决定、版本、产物 hash、reviewed_at。输出到
``requirements/REQ-NNN-*/.audit/projection.json``；缓存失效检测到新事件时重建，
重建幂等。

Why this matters:
  * ``branch_validator`` used to glob ``99-review/review-*.md`` and sort by
    ``reviewed_at`` — but glob order is NOT guaranteed to be chronological
    (the B7 pitfall), and each validator independently performed this scan
    which could drift.
  * The projection is the single source of truth for "what's the latest
    review record for work_item X?" produced once, read by any validator.

Projection schema (JSON):
  {
    "session_id": "REQ-NNN-xxx",
    "generated_at": ISO-8601,
    "event_count_snapshot": N,           # compare vs len(replay_events) to detect staleness
    "audit_chain_ok": bool,              # whether chain verified cleanly at build time
    "work_items": {
      "<work_item_id>": {
        "status": "confirmed|draft|ready_for_human_review|superseded|...",
        "artifact_path": "00X-xxx/artifact.md",           # relative to req_dir
        "artifact_content_sha256": "<64 hex>" | null,
        "artifact_version": "vX.Y" | "unknown",
        "artifact_id_frontmatter": "<BG-001|...>" | null,
        "reviewer": "<name>" | null,
        "reviewer_id": "<stable id>" | null,
        "reviewer_role": "<role>" | null,
        "reviewed_at": "<ISO-8601>" | null,
        "confirmed_at": "<ISO-8601>" | null,
        "latest_review_record": "99-review/review-xxx.md" | null,  # relative path
        "latest_review_decision": "approve|changes" | null,
        "superseded": bool,
        "superseded_reason": str | null,
        "last_change_reason": str | null,
        "last_changed_at": ISO-8601 | null,
      }
    },
    "derived_from_events": [event_id_1, event_id_2, ...]  # every event_id that folded in
  }

Public API:
  - :func:`build_projection` — fold audit log + file-system observations
    into a projection dict and optionally write it to disk.
  - :func:`read_projection` — load projection.json, rebuilding on stale/missing.
  - :func:`is_stale` — quick check whether projection is out of date.
  - :func:`latest_review_for` — helper: return latest review record path + hash
    for a given work_item, consulting projection first, falling back to legacy
    glob+sort (with a warning) so old requirements keep working.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import audit_log
from workflow_registry import artifact_content_hash, find_artifact, read_frontmatter, work_items


PROJECTION_FILENAME = "projection.json"


def _projection_path(req_dir: Path) -> Path:
    return req_dir / ".audit" / PROJECTION_FILENAME


def _artifact_status_fields(req_dir: Path, item: dict[str, Any]) -> dict[str, Any]:
    """Read the artifact's current frontmatter + content hash.

    Returns empty-ish dict if artifact has not been created yet. This is the
    *current filesystem state* (ground truth) while the review events track
    *decisions made*. A confirmed status is only trustworthy when the
    ReviewRecord hash matches (branch_validator owns that assertion).
    """
    artifact = find_artifact(req_dir, item)
    if not artifact:
        return {
            "status": "not_created",
            "artifact_path": None,
            "artifact_content_sha256": None,
            "artifact_version": "unknown",
            "artifact_id_frontmatter": None,
            # Keep the full key set stable so the event-fold loop can always
            # read bucket["reviewer"] / bucket["reviewed_at"] / ... even when
            # the artifact has never been created (review events may still
            # reference a work item whose artifact was later deleted).
            "reviewer": None,
            "reviewed_at": None,
            "confirmed_at": None,
        }
    fm = read_frontmatter(artifact)
    try:
        content_hash = artifact_content_hash(artifact.read_text(encoding="utf-8"))
    except OSError:
        content_hash = None
    return {
        "status": fm.get("status") or "draft",
        "artifact_path": str(artifact.relative_to(req_dir)),
        "artifact_content_sha256": content_hash,
        "artifact_version": fm.get("version") or "unknown",
        "artifact_id_frontmatter": fm.get("artifact_id"),
        "reviewer": fm.get("reviewer"),
        "reviewed_at": fm.get("reviewed_at"),
        "confirmed_at": fm.get("confirmed_at"),
    }


def _reviewed_at_from_text(text: str) -> str:
    m = re.search(r"(?m)^\s*-\s*reviewed_at:\s*(.+)$", text)
    return m.group(1).strip() if m else ""


def _latest_review_legacy(req_dir: Path, work_item_id: str) -> tuple[str | None, dict[str, Any] | None]:
    """Legacy fallback when projection/events don't exist yet.

    Globs 99-review/review-*.md, filters those whose body mentions the
    work_item_id, sorts by reviewed_at ascending, returns (path, newest_row_extract).
    Returns (None, None) if no match. This is the SAME glob-then-sort logic
    that branch_validator used before the projection; it's kept as a fallback
    so requirements created *before* audit_log was adopted keep working.
    """
    review_dir = req_dir / "99-review"
    if not review_dir.is_dir():
        return None, None
    records = []
    for p in sorted(review_dir.glob("review-*.md")):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if f"work_item: {work_item_id}" not in text:
            continue
        records.append((p, text, _reviewed_at_from_text(text)))
    if not records:
        return None, None
    records.sort(key=lambda t: t[2])
    newest_path, newest_text = records[-1][0], records[-1][1]
    decision = re.search(r"(?m)^\s*-\s*decision:\s*(\S+)", newest_text)
    reviewer = re.search(r"(?m)^\s*-\s*reviewer:\s*(.+)$", newest_text)
    reviewer_id = re.search(r"(?m)^\s*-\s*reviewer_id:\s*(.+)$", newest_text)
    reviewer_role = re.search(r"(?m)^\s*-\s*reviewer_role:\s*(.+)$", newest_text)
    ahash = re.search(r"(?m)^\s*-\s*artifact_content_sha256:\s*([0-9a-f]{64})", newest_text)
    aversion = re.search(r"(?m)^\s*-\s*artifact_version:\s*(\S+)", newest_text)
    extract = {
        "latest_review_record": str(newest_path.relative_to(req_dir)),
        "latest_review_decision": decision.group(1) if decision else None,
        "reviewer": reviewer.group(1).strip() if reviewer else None,
        "reviewer_id": reviewer_id.group(1).strip() if reviewer_id else None,
        "reviewer_role": reviewer_role.group(1).strip() if reviewer_role else None,
        "reviewed_at": records[-1][2] or None,
        "artifact_content_sha256": ahash.group(1) if ahash else None,
        "artifact_version": aversion.group(1) if aversion else "unknown",
    }
    return extract["latest_review_record"], extract


def build_projection(req_dir: Path, write: bool = True) -> dict[str, Any]:
    """Build (and optionally persist) the projection for ``req_dir``.

    Steps:
      1. Read artifact frontmatter / content hashes for every registered work item.
      2. Fold audit events (review / change / reflow) on top, per work_item.
      3. For work_items with no audit events (legacy requirements), call the
         legacy glob-then-sort fallback so branch_validator still sees a
         latest_review_record for confirmed artifacts.
      4. Emit projection dict; write .audit/projection.json if ``write=True``.

    Always rebuilds from scratch (idempotent). Callers can use :func:`is_stale`
    first to avoid unnecessary work.
    """
    req_dir = req_dir.resolve()
    session_id = req_dir.name

    events = audit_log.replay_events(req_dir)
    chain_status = audit_log.verify_chain(req_dir)
    wi_out: dict[str, dict[str, Any]] = {}

    # (1) Filesystem ground-truth per work item
    for item in work_items():
        wi_id = item["id"]
        wi_out[wi_id] = {
            "work_item": wi_id,
            "work_item_order": item.get("order", 0),
            **_artifact_status_fields(req_dir, item),
            # Review-decision fields populated later from events or legacy fallback
            "reviewer_id": None,
            "reviewer_role": None,
            "latest_review_record": None,
            "latest_review_decision": None,
            "superseded": False,
            "superseded_reason": None,
            "last_change_reason": None,
            "last_changed_at": None,
        }

    # (2) Fold events: each review / change / reflow augments the WI dict.
    #     "Latest wins" on a per-field basis because events are chronological.
    derived_ids: list[int] = []
    for ev in events:
        ev_id = ev.get("event_id")
        if isinstance(ev_id, int):
            derived_ids.append(ev_id)
        et = ev.get("event_type")
        wi_id = ev.get("work_item")
        if not wi_id or wi_id not in wi_out:
            # Events like "init" or "reflow" that have no work_item fall through;
            # reflow events carry the trigger WI plus superseded list separately.
            if et == "reflow":
                # Mark every superseded WI's superseded flag
                for swi in ev.get("superseded") or []:
                    if swi in wi_out:
                        wi_out[swi]["superseded"] = True
                        wi_out[swi]["superseded_reason"] = ev.get("reason") or wi_out[swi]["superseded_reason"]
            continue
        bucket = wi_out[wi_id]
        if et == "review":
            bucket["latest_review_record"] = ev["payload"] if isinstance(ev.get("payload"), str) else bucket["latest_review_record"]
            bucket["latest_review_decision"] = ev.get("decision") or bucket["latest_review_decision"]
            bucket["reviewer"] = ev.get("reviewer") or bucket["reviewer"]
            bucket["reviewer_id"] = ev.get("reviewer_id") or bucket["reviewer_id"]
            bucket["reviewer_role"] = ev.get("reviewer_role") or bucket["reviewer_role"]
            # reviewed_at comes either from the event or from the artifact frontmatter
            # (frontmatter is authoritative for *current* artifact stamp, but the
            #  event's record-creation timestamp is not directly stored; the record's
            #  reviewed_at field is what branch_validator has always used.)
            if ev.get("recorded_at"):
                bucket["reviewed_at"] = bucket["reviewed_at"] or ev["recorded_at"]
            if ev.get("artifact_content_sha256"):
                bucket["artifact_content_sha256"] = ev["artifact_content_sha256"]
            if ev.get("artifact_version"):
                bucket["artifact_version"] = ev["artifact_version"]
        elif et == "change":
            bucket["last_change_reason"] = ev.get("reason")
            bucket["last_changed_at"] = ev.get("recorded_at") or bucket["last_changed_at"]
            # After a change (→draft) the artifact is no longer decision-approved
            if ev.get("to_status") == "draft":
                bucket["latest_review_decision"] = "changes"
        elif et == "confirm":
            bucket["confirmed_at"] = ev.get("recorded_at") or bucket["confirmed_at"]
        elif et == "reject":
            bucket["latest_review_decision"] = "changes"

    # (3) Legacy fallback: any WI whose latest_review_record is still None but
    #     whose artifact says "confirmed" → use the glob fallback. This keeps
    #     requirements created *before* audit_log adoption passing branch_validator
    #     without forcing migration. We annotate with ``_legacy_fallback: true``
    #     so callers can surface a WARN (future work).
    for wi_id, bucket in wi_out.items():
        if bucket["latest_review_record"] is None and bucket.get("status") == "confirmed":
            _, legacy_extract = _latest_review_legacy(req_dir, wi_id)
            if legacy_extract:
                bucket["latest_review_record"] = legacy_extract["latest_review_record"]
                bucket["latest_review_decision"] = legacy_extract["latest_review_decision"] or bucket["latest_review_decision"]
                bucket["reviewer"] = legacy_extract["reviewer"] or bucket["reviewer"]
                bucket["reviewer_id"] = legacy_extract["reviewer_id"] or bucket["reviewer_id"]
                bucket["reviewer_role"] = legacy_extract["reviewer_role"] or bucket["reviewer_role"]
                bucket["reviewed_at"] = legacy_extract["reviewed_at"] or bucket["reviewed_at"]
                if legacy_extract.get("artifact_content_sha256"):
                    bucket["artifact_content_sha256"] = legacy_extract["artifact_content_sha256"]
                bucket["_legacy_fallback"] = True
        else:
            bucket["_legacy_fallback"] = False

    projection = {
        "schema_version": 1,
        "session_id": session_id,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "event_count_snapshot": len(events),
        "audit_chain_ok": chain_status["ok"],
        "work_items": wi_out,
        "derived_from_events": derived_ids,
    }

    if write:
        (req_dir / ".audit").mkdir(parents=True, exist_ok=True)
        _projection_path(req_dir).write_text(
            json.dumps(projection, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return projection


def is_stale(req_dir: Path) -> bool:
    """True if projection needs rebuild (missing, unparseable, or event count mismatch)."""
    path = _projection_path(req_dir)
    if not path.is_file():
        return True
    try:
        proj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True
    current_event_count = len(audit_log.replay_events(req_dir))
    return int(proj.get("event_count_snapshot", -1)) != current_event_count


def read_projection(req_dir: Path, auto_rebuild: bool = True) -> dict[str, Any] | None:
    """Load projection.json. If stale and auto_rebuild, rebuild then return.

    Returns None only if auto_rebuild=False and file is missing/unparseable.
    """
    if auto_rebuild and is_stale(req_dir):
        return build_projection(req_dir, write=True)
    path = _projection_path(req_dir)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        if auto_rebuild:
            return build_projection(req_dir, write=True)
        return None


def latest_review_for(req_dir: Path, work_item_id: str) -> dict[str, Any] | None:
    """Return projection bucket for a single work_item (builds cache lazily).

    Equivalent legacy behavior: find the newest review record by glob+sort.
    Consumers (branch_validator, traceability_check, …) should use this helper
    instead of scanning 99-review directly so everyone agrees on "latest".
    """
    proj = read_projection(req_dir, auto_rebuild=True)
    if proj is None:
        _, fallback = _latest_review_legacy(req_dir, work_item_id)
        return fallback
    wi = proj["work_items"].get(work_item_id)
    if wi is None:
        _, fallback = _latest_review_legacy(req_dir, work_item_id)
        return fallback
    return wi


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("req_dir", type=Path)
    parser.add_argument(
        "action",
        nargs="?",
        choices=["build", "status", "stale"],
        default="build",
        help="build=(re)build and write, status=print summary, stale=exit 1 if stale",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    if not args.req_dir.is_dir():
        print(f"ERROR: {args.req_dir} is not a directory", file=sys.stderr)
        return 1

    if args.action == "stale":
        stale = is_stale(args.req_dir)
        if args.as_json:
            print(json.dumps({"stale": stale}))
        else:
            print("STALE" if stale else "FRESH")
        return 1 if stale else 0

    if args.action == "build":
        proj = build_projection(args.req_dir, write=True)
    else:  # status
        proj = read_projection(args.req_dir, auto_rebuild=True)
        assert proj is not None

    if args.as_json:
        print(json.dumps(proj, ensure_ascii=False, indent=2))
    else:
        print(f"Projection for {proj['session_id']} (event_count={proj['event_count_snapshot']})")
        print(f"  Chain ok: {proj['audit_chain_ok']}")
        for wi_id, bucket in sorted(proj["work_items"].items(), key=lambda kv: kv[1].get("work_item_order", 0)):
            status = bucket.get("status", "?")
            lrr = bucket.get("latest_review_record") or "(none)"
            lrd = bucket.get("latest_review_decision") or "(none)"
            legacy = " [legacy]" if bucket.get("_legacy_fallback") else ""
            print(f"  {wi_id:<30} status={status:<28} review={lrd:<8} @ {lrr}{legacy}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
