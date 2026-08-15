#!/usr/bin/env python3
"""Append-only event-sourcing audit log for traceable artifact lifecycle.

Harness借鉴点一：事件溯源式审计流。把确认/变更/评审做成 append-only 事件日志，
能从事件流重建完整因果链。作为现有评审文档的补充索引，不取代、不重写已确认产物。

Exposes:
  - :func:`append_event` — append one AuditEvent to the session's events.jsonl.
  - :func:`replay_events` — read and return all events for a session in order.
  - :func:`verify_chain` — validate hash chain continuity, monotonic timestamps,
    valid event_type, and referenced record existence + integrity.
  - :func:`reconstruct_causality` — rebuild a session's 认定 → 变更 → 确认 chain
    from the event log, returning a list of causal stages with record paths.

Storage layout (per REQ-NNN-* directory):
    requirements/REQ-NNN-*/
      .audit/
        events.jsonl    # append-only, one canonical JSON per line
        projection.json # (populated by projection_cache.py, not this module)

Design rules (same philosophy as hash_anchor.py):
  * Append-only: ``append_event`` never rewrites prior lines. ``verify_chain``
    treats any deviation from the expected prev_hash as a CRITICAL break.
  * Stable serialization: ``json.dumps(..., sort_keys=True, ensure_ascii=False)``
    so two processes writing equivalent rows byte-for-byte agree.
  * Self-fingerprint: every event carries ``event_sha256`` covering all fields
    *except* event_sha256 itself. Editing any field — including prev_hash,
    payload_sha256, or recorded_at — breaks the fingerprint.
  * Monotonic recorded_at: within a session, each new event must have a
    recorded_at >= the last event's recorded_at (with a 1s fuzz for clock
    skew between subprocess writers).
  * Idempotent on (event_type, payload, payload_sha256): calling append_event
    twice with the same triple does NOT duplicate a row. This matches
    hash_anchor.record_anchor's idempotency contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVENT_TYPE_TOKENS = {"review", "change", "decision", "confirm", "reject", "reflow", "init"}
GENESIS_PREV = "0" * 64
EVENT_SHA256_PLACEHOLDER = "<event_sha256>"


def _audit_dir(req_dir: Path) -> Path:
    return req_dir / ".audit"


def _events_path(req_dir: Path) -> Path:
    return _audit_dir(req_dir) / "events.jsonl"


def _canonical(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _event_body_sha256(event: dict[str, Any]) -> str:
    """SHA-256 of an event covering all fields except event_sha256 itself.

    Mirrors :func:`hash_anchor.record_body_sha256`: remove the self-fingerprint
    line / field so the hash is not self-referential; canonicalize; digest.
    """
    stripped = {k: v for k, v in event.items() if k != "event_sha256"}
    return _sha256_text(_canonical(stripped))


def _read_raw_events(req_dir: Path) -> list[dict[str, Any]]:
    """Read events.jsonl and return rows as parsed dicts.

    Corrupt lines are kept as ``{_corrupt: True, _raw: str, _line_no: int}``
    so verify_chain can surface them. Missing file → empty list (no events
    have been written yet; this is NOT a chain break).
    """
    path = _events_path(req_dir)
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for idx, raw in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not raw.strip():
            continue
        try:
            rows.append(json.loads(raw))
        except json.JSONDecodeError:
            rows.append({"_corrupt": True, "_raw": raw, "_line_no": idx})
    return rows


def _session_id(req_dir: Path) -> str:
    """Session id is the requirement directory name (REQ-NNN-*)."""
    return req_dir.resolve().name


def _last_clean_event(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    for ev in reversed(events):
        if not ev.get("_corrupt"):
            return ev
    return None


def append_event(
    req_dir: Path,
    event_type: str,
    payload: str | dict[str, Any],
    payload_sha256: str | None = None,
    recorded_at: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append one AuditEvent. Returns ``{recorded, event, skipped_dedup}``.

    Parameters
    ----------
    event_type:
        One of EVENT_TYPE_TOKENS. A ValueError is raised for unknown tokens.
    payload:
        Either a *relative path* (from req_dir root) to the referenced record
        (ReviewRecord / ChangeRecord / DecisionRecord .md file), or an inline
        dict for events that don't correspond to a file (e.g. ``init``).
    payload_sha256:
        SHA-256 of the referenced record body (required when payload is a path).
        For inline-dict payloads it is computed automatically from canonical
        serialization, and the caller-supplied value (if any) is ignored.
    recorded_at:
        ISO-8601 UTC timestamp. Defaults to ``datetime.now(timezone.utc)`` with
        microseconds stripped. If ``recorded_at`` is earlier than the last
        event's recorded_at by more than 1s, a ValueError is raised (clock-skew
        guard).
    extra:
        Optional extra fields folded into the event (e.g. work_item, decision,
        reviewer). These are part of the canonical body and therefore covered
        by event_sha256.
    """
    if event_type not in EVENT_TYPE_TOKENS:
        raise ValueError(f"unknown event_type '{event_type}' — allowed: {sorted(EVENT_TYPE_TOKENS)}")

    audit_dir = _audit_dir(req_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)

    session_id = _session_id(req_dir)
    now_iso = recorded_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    # Resolve payload + payload_sha256
    if isinstance(payload, dict):
        payload_canon = _canonical(payload)
        resolved_payload: str | dict[str, Any] = payload
        resolved_payload_sha256 = _sha256_text(payload_canon)
    elif isinstance(payload, str):
        # Treat string payload as a path relative to req_dir
        payload_path = req_dir / payload
        if not payload_path.is_file():
            raise FileNotFoundError(f"payload path not found: {payload_path}")
        if not payload_sha256:
            raise ValueError("payload_sha256 is required when payload references a file path")
        resolved_payload = payload
        resolved_payload_sha256 = payload_sha256
    else:
        raise TypeError("payload must be str (path) or dict (inline)")

    existing = _read_raw_events(req_dir)
    last_clean = _last_clean_event(existing)

    # Monotonic recorded_at check (1s fuzz for subprocess clock skew)
    if last_clean:
        last_ts_iso = last_clean.get("recorded_at", "")
        try:
            last_dt = datetime.fromisoformat(last_ts_iso.replace("Z", "+00:00"))
            cur_dt = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
        except ValueError:
            last_dt = cur_dt = datetime.now(timezone.utc).replace(microsecond=0)
        delta = (cur_dt - last_dt).total_seconds()
        if delta < -1:  # more than 1s clock skew backwards
            raise ValueError(
                f"recorded_at {now_iso} is earlier than last event {last_ts_iso}"
                f" by {abs(delta):.1f}s (monotonic guard)"
            )

    new_event: dict[str, Any] = {
        "event_id": (last_clean["event_id"] + 1) if last_clean else 1,
        "session_id": session_id,
        "event_type": event_type,
        "prev_hash": _sha256_text(_canonical(last_clean)) if last_clean else GENESIS_PREV,
        "payload": resolved_payload,
        "payload_sha256": resolved_payload_sha256,
        "recorded_at": now_iso,
    }
    if extra:
        # Merge extra fields AFTER the required ones so they're covered by the
        # fingerprint; caller-supplied values never overwrite the required
        # fields above.
        for k, v in extra.items():
            if k not in new_event:
                new_event[k] = v

    # Idempotency: if the last clean event shares (event_type, payload,
    # payload_sha256) with the candidate, skip appending and return the
    # existing row. Extra fields are intentionally excluded from the dedup
    # key (they are metadata like reviewer/work_item), so two events that
    # reference the *same physical record* always collapse — matching
    # hash_anchor.record_anchor's behavior.
    if last_clean:
        dedup_keys = ("event_type", "payload", "payload_sha256")
        if all(last_clean.get(k) == new_event.get(k) for k in dedup_keys):
            return {"recorded": False, "event": last_clean, "skipped_dedup": True}

    new_event["event_sha256"] = EVENT_SHA256_PLACEHOLDER
    new_event["event_sha256"] = _event_body_sha256(new_event)

    line = _canonical(new_event)
    with _events_path(req_dir).open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")

    # Harness 借鉴点二闭环：事件写入成功后主动重建投影缓存，保证"事件 ⟺ 模型可见"强一致。
    # 延迟导入避免循环依赖（projection_cache 顶层 import audit_log）。
    # 重建失败只 warn：事件是单一事实来源，投影是派生视图，下次 read_projection(auto_rebuild=True)
    # 会自动重建，所以投影重建失败不应让 append_event 整体失败。
    try:
        from projection_cache import build_projection
        build_projection(req_dir, write=True)
    except Exception as proj_err:  # pragma: no cover - defensive
        print(f"WARN: projection rebuild failed after event append: {proj_err}", file=sys.stderr)

    return {"recorded": True, "event": new_event, "skipped_dedup": False}


def replay_events(req_dir: Path) -> list[dict[str, Any]]:
    """Return all clean (non-corrupt) events in chronological order.

    Missing file → empty list (callers should treat "no events yet" as
    distinct from "chain invalid"; use :func:`verify_chain` for validation).
    """
    return [ev for ev in _read_raw_events(req_dir) if not ev.get("_corrupt")]


def verify_chain(req_dir: Path) -> dict[str, Any]:
    """Validate the event log hash chain, monotonic timestamps, and records.

    Returns a dict with:
      - ok: bool — True if no CRITICAL issues
      - count: int — number of events (corrupt rows counted separately)
      - corrupt_count: int — rows that failed JSON parsing
      - break_at: int | None — 0-based index of first chain break, or None
      - issues: list[{severity, check, message, event_index?}] — every issue
        surfaced, ordered by event index
    """
    raw = _read_raw_events(req_dir)
    if not raw:
        return {
            "ok": True,
            "count": 0,
            "corrupt_count": 0,
            "break_at": None,
            "issues": [],
            "empty": True,
        }

    issues: list[dict[str, Any]] = []
    break_at: int | None = None
    corrupt_count = 0
    expected_prev = GENESIS_PREV
    last_recorded_at: datetime | None = None

    for idx, ev in enumerate(raw):
        if ev.get("_corrupt"):
            corrupt_count += 1
            issues.append({
                "severity": "CRITICAL",
                "check": "audit_chain.corrupt_row",
                "message": f"event line {ev.get('_line_no', idx)}: corrupt JSON",
                "event_index": idx,
            })
            break_at = break_at if break_at is not None else idx
            expected_prev = ""  # chain beyond a corrupt row is unknowable
            last_recorded_at = None
            continue

        # (1) prev_hash chain continuity
        actual_prev = ev.get("prev_hash", "")
        if actual_prev != expected_prev:
            msg = (
                f"hash chain broken at event {idx} (event_id={ev.get('event_id')}): "
                f"expected prev_hash={expected_prev[:12]}… got {actual_prev[:12]}…"
            )
            issues.append({
                "severity": "CRITICAL",
                "check": "audit_chain.prev_hash_mismatch",
                "message": msg,
                "event_index": idx,
            })
            if break_at is None:
                break_at = idx

        # (2) event_type is a known token
        et = ev.get("event_type", "")
        if et not in EVENT_TYPE_TOKENS:
            issues.append({
                "severity": "HIGH",
                "check": "audit_chain.invalid_event_type",
                "message": f"event {idx}: event_type '{et}' not in {sorted(EVENT_TYPE_TOKENS)}",
                "event_index": idx,
            })

        # (3) self-fingerprint integrity — event_sha256 matches the body
        declared_fingerprint = ev.get("event_sha256", "")
        computed_fingerprint = _event_body_sha256(ev)
        if declared_fingerprint != computed_fingerprint:
            issues.append({
                "severity": "CRITICAL",
                "check": "audit_chain.event_sha256_mismatch",
                "message": (
                    f"event {idx} (event_id={ev.get('event_id')}): self-fingerprint broken "
                    f"(declared={declared_fingerprint[:12]}… computed={computed_fingerprint[:12]}…)"
                ),
                "event_index": idx,
            })

        # (4) recorded_at monotonic (with 1s fuzz)
        ts_raw = ev.get("recorded_at", "")
        try:
            cur_dt = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except ValueError:
            cur_dt = None
            issues.append({
                "severity": "HIGH",
                "check": "audit_chain.bad_timestamp",
                "message": f"event {idx}: recorded_at '{ts_raw}' is not valid ISO-8601",
                "event_index": idx,
            })
        if cur_dt and last_recorded_at is not None:
            delta = (cur_dt - last_recorded_at).total_seconds()
            if delta < -1:
                issues.append({
                    "severity": "HIGH",
                    "check": "audit_chain.non_monotonic_ts",
                    "message": f"event {idx}: recorded_at went backwards by {abs(delta):.1f}s",
                    "event_index": idx,
                })
        if cur_dt:
            last_recorded_at = cur_dt

        # (5) payload reference exists (if payload is a path string) and
        #     payload_sha256 matches the current body on disk.
        payload = ev.get("payload")
        declared_payload_hash = ev.get("payload_sha256", "")
        if isinstance(payload, str) and not isinstance(payload, dict):
            # It's a relative path.
            record_path = req_dir / payload
            if not record_path.is_file():
                issues.append({
                    "severity": "HIGH",
                    "check": "audit_chain.payload_missing",
                    "message": f"event {idx}: payload record missing at {payload}",
                    "event_index": idx,
                })
            elif declared_payload_hash:
                actual_hash = _sha256_text(record_path.read_text(encoding="utf-8"))
                if actual_hash != declared_payload_hash:
                    # This is the key "event + record 同步篡改" defense:
                    # if someone edits both the ReviewRecord AND rewrites the
                    # event log row to match, the event_sha256 self-fingerprint
                    # (check 3) breaks first *or* the prev_hash chain (check 1)
                    # breaks first because the prior row's hash was committed.
                    # If both somehow survived, this check is the final tripwire.
                    issues.append({
                        "severity": "CRITICAL",
                        "check": "audit_chain.payload_hash_mismatch",
                        "message": (
                            f"event {idx}: payload {payload}'s current SHA-256 does not match "
                            f"the event's declared payload_sha256 (record was tampered after event was written)"
                        ),
                        "event_index": idx,
                    })

        # Advance chain-link to the current row (regardless of issues) so a
        # single break doesn't cascade into "everything after is broken".
        expected_prev = _sha256_text(_canonical(ev))

    clean_count = len(raw) - corrupt_count
    ok = not any(i["severity"] in ("CRITICAL", "HIGH") for i in issues)
    return {
        "ok": ok,
        "count": clean_count,
        "corrupt_count": corrupt_count,
        "break_at": break_at,
        "issues": issues,
        "empty": False,
    }


def reconstruct_causality(req_dir: Path) -> dict[str, Any]:
    """Rebuild a session's 认定 → 变更 → 确认 causal chain from the event log.

    Returns a dict suitable for machine and human consumption:
      - session_id, event_count
      - stages: list[{phase, work_item, decision, reviewer, recorded_at, record_path}]
        ordered chronologically. phase is one of: init →认定 (review/decision)
        → 变更 (change/reflow) → 确认 (confirm).
      - chain_ok: result of verify_chain().ok
      - chain_issues: verify_chain().issues (empty list if none)
    """
    chain = verify_chain(req_dir)
    events = replay_events(req_dir)
    stages: list[dict[str, Any]] = []
    for ev in events:
        et = ev["event_type"]
        if et == "init":
            phase = "init"
        elif et in ("review", "decision"):
            phase = "认定"
        elif et in ("change", "reflow"):
            phase = "变更"
        elif et == "confirm":
            phase = "确认"
        elif et == "reject":
            phase = "驳回"
        else:
            phase = et
        stages.append({
            "phase": phase,
            "event_type": et,
            "event_id": ev.get("event_id"),
            "work_item": ev.get("work_item"),
            "decision": ev.get("decision"),
            "reviewer": ev.get("reviewer"),
            "recorded_at": ev.get("recorded_at"),
            "record_path": ev.get("payload") if isinstance(ev.get("payload"), str) else None,
        })
    return {
        "session_id": _session_id(req_dir),
        "event_count": len(events),
        "stages": stages,
        "chain_ok": chain["ok"],
        "chain_issues": chain["issues"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("req_dir", type=Path)
    parser.add_argument(
        "action",
        nargs="?",
        choices=["verify", "replay", "causality"],
        default="verify",
        help="verify=check chain, replay=list events, causality=rebuild causal stages (default: verify)",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    if not args.req_dir.is_dir():
        print(f"ERROR: {args.req_dir} is not a directory", file=sys.stderr)
        return 1

    if args.action == "verify":
        result = verify_chain(args.req_dir)
    elif args.action == "replay":
        result = {"events": replay_events(args.req_dir)}
    else:  # causality
        result = reconstruct_causality(args.req_dir)

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.action == "verify":
            label = "PASS" if result["ok"] else "FAIL"
            print(f"Audit chain: {label} (events={result['count']}, corrupt={result['corrupt_count']})")
            for issue in result.get("issues", []):
                print(f"  [{issue['severity']}/{issue['check']}] {issue['message']}")
        elif args.action == "replay":
            for ev in result["events"]:
                print(f"  #{ev.get('event_id'):>3} {ev.get('event_type'):<8} @ {ev.get('recorded_at')} — {ev.get('payload')}")
        else:  # causality
            print(f"Causal chain for {result['session_id']} ({result['event_count']} events):")
            print(f"  Chain integrity: {'PASS' if result['chain_ok'] else 'FAIL'}")
            for s in result["stages"]:
                bits = [f"#{s['event_id'] or '?':>3}", s["phase"], s["event_type"]]
                if s["work_item"]:
                    bits.append(f"wi={s['work_item']}")
                if s["decision"]:
                    bits.append(f"decision={s['decision']}")
                if s["reviewer"]:
                    bits.append(f"by={s['reviewer']}")
                bits.append(f"@ {s['recorded_at']}")
                print("  " + " ".join(bits))
    return 0 if (args.action != "verify" or result.get("ok")) else 1


if __name__ == "__main__":
    sys.exit(main())
