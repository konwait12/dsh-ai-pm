#!/usr/bin/env python3
"""Append-only external hash anchor for confirmed artifacts (B13 / P0).

The chain hash on its own is closed-loop: an attacker who can edit both the
artifact and its ReviewRecord can swap them in lockstep. This module writes a
tamper-evident external anchor — a JSONL file under ``99-review/.hash-anchor.jsonl``
— and exposes:

  - :func:`record_anchor` — append one anchor line for a confirmed artifact.
  - :func:`verify_anchor_chain` — re-walk the chain and check each line's
    ``prev_anchor_sha256`` matches the SHA-256 of the previous line.
  - :func:`verify_artifact_anchored` — check that a specific artifact has at
    least one anchor row whose ``sha256`` and ``reviewer`` match the current
    artifact and its newest ReviewRecord.

Backward compatibility: the anchor file is OPTIONAL. Existing requirements
that have never recorded an anchor will simply pass the anchor check (so the
77 baseline fixtures stay green). New approvals write one line per call.

Design rules enforced here:

  * Idempotent: dedup key is ``(artifact_id, review_record, sha256)`` — calling
    ``record_anchor`` twice with the same triple does NOT add a second row.
  * Chain integrity: each line's ``prev_anchor_sha256`` equals the SHA-256 of
    the previous line (the line itself, the JSON content). The first row uses
    the sentinel ``"0" * 64``.
  * Stable serialization: ``json.dumps(..., sort_keys=True, ensure_ascii=False)``.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ANCHOR_FILENAME = ".hash-anchor.jsonl"
ANCHOR_GENESIS_PREV = "0" * 64

# Placeholder used by the ReviewRecord writer (pipeline.py) before the real
# record_sha256 value is substituted in. It must never appear in a real record
# body, so record_body_sha256() can be called on the draft text.
RECORD_SHA256_PLACEHOLDER = "<record_sha256>"


def _anchor_path(req_dir: Path) -> Path:
    return req_dir / "99-review" / ANCHOR_FILENAME


def _canonical_line(row: dict) -> str:
    """Stable JSON serialization for a row (sorted keys, no ASCII escaping)."""
    return json.dumps(row, sort_keys=True, ensure_ascii=False)


def _line_sha256(line_text: str) -> str:
    """SHA-256 of a canonicalized line, ignoring the trailing newline."""
    return hashlib.sha256(line_text.encode("utf-8")).hexdigest()


def record_body_sha256(text: str) -> str:
    """SHA-256 of a ReviewRecord's body, excluding its own ``record_sha256`` line.

    ``record_sha256`` is a self-fingerprint of the record: it covers the whole
    record body *except* the ``record_sha256`` line itself (which would be
    self-referential). This is the B13 defense against "artifact + ReviewRecord
    hash 同步篡改": editing any field of the record (e.g. ``artifact_content_sha256``
    to match a rewritten artifact) changes the body, so the declared
    ``record_sha256`` no longer matches and the validator can flag it.

    The writer (``pipeline.py``) and the validator (``branch_validator.py``) must
    both use this exact normalization so a record written by the pipeline
    validates cleanly:

      * the ``record_sha256`` line is removed (the value may be a placeholder
        or a real hash — only the line itself is excluded);
      * trailing newlines are stripped before hashing.
    """
    body = re.sub(r"(?m)^\s*-\s*record_sha256:.*$\n?", "", text)
    return hashlib.sha256(body.rstrip("\n").encode("utf-8")).hexdigest()


def _read_lines(req_dir: Path) -> list[dict]:
    path = _anchor_path(req_dir)
    if not path.is_file():
        return []
    rows: list[dict] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            rows.append(json.loads(raw))
        except json.JSONDecodeError:
            # Treat a corrupt row as a hard chain break; the caller will surface it.
            rows.append({"_corrupt": True, "_raw": raw})
    return rows


def _dedup_key(row: dict) -> tuple[str, str, str]:
    return (row.get("artifact_id", ""), row.get("review_record", ""), row.get("sha256", ""))


def record_anchor(req_dir: Path, artifact: str, artifact_id: str, reviewer: str,
                  review_record: str, sha256: str | None = None,
                  ts: str | None = None) -> dict:
    """Append one anchor row to ``99-review/.hash-anchor.jsonl``.

    Idempotent: if the last row already shares the same ``(artifact_id,
    review_record, sha256)`` triple, no new row is appended. Returns a dict
    describing what happened:

        {"recorded": True, "row": {...}, "skipped_dedup": False}

    If ``sha256`` is None, it falls back to ``""`` — callers are expected to
    compute it from the artifact text via
    :func:`workflow_registry.artifact_content_hash`.
    """
    path = _anchor_path(req_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = _read_lines(req_dir)
    new_row = {
        "ts": ts or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "artifact": artifact,
        "artifact_id": artifact_id,
        "reviewer": reviewer,
        "sha256": sha256 or "",
        "review_record": review_record,
        "prev_anchor_sha256": "",
    }
    # Idempotency: same triple on the last row → no-op.
    if existing:
        last = existing[-1]
        if not last.get("_corrupt") and _dedup_key(last) == _dedup_key(new_row):
            return {"recorded": False, "row": last, "skipped_dedup": True}
    prev_hash = ANCHOR_GENESIS_PREV if not existing else _line_sha256(_canonical_line(existing[-1]))
    new_row["prev_anchor_sha256"] = prev_hash
    line = _canonical_line(new_row)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return {"recorded": True, "row": new_row, "skipped_dedup": False, "line_sha256": _line_sha256(line)}


def verify_anchor_chain(req_dir: Path) -> dict:
    """Re-walk the chain and return ``{ok, count, break_at, issues}``.

    - ``ok`` is True iff every line has a valid ``prev_anchor_sha256`` equal
      to the SHA-256 of the previous line.
    - ``break_at`` is the (0-based) index of the first line whose link is
      broken; ``None`` if the chain is intact.
    - ``issues`` is a list of human-readable strings describing problems.
    """
    rows = _read_lines(req_dir)
    if not rows:
        return {"ok": True, "count": 0, "break_at": None, "issues": [], "missing": True}
    expected_prev = ANCHOR_GENESIS_PREV
    issues: list[str] = []
    break_at: int | None = None
    for idx, row in enumerate(rows):
        if row.get("_corrupt"):
            issues.append(f"record {idx}: corrupt JSON line")
            break_at = break_at if break_at is not None else idx
            expected_prev = ""  # chain beyond this point is unknowable
            continue
        actual_prev = row.get("prev_anchor_sha256", "")
        if actual_prev != expected_prev:
            msg = f"hash anchor chain broken at record {idx}"
            issues.append(msg)
            if break_at is None:
                break_at = idx
        # Always advance expected_prev to the current line's hash, so a break
        # doesn't cascade falsely into "everything after is broken".
        expected_prev = _line_sha256(_canonical_line(row))
    return {"ok": not issues, "count": len(rows), "break_at": break_at, "issues": issues, "missing": False}


def verify_artifact_anchored(req_dir: Path, artifact: str, expected_sha256: str,
                             expected_reviewer: str) -> dict:
    """Confirm ``artifact`` has at least one matching anchor row.

    Returns ``{ok, anchored, mismatches, missing_anchor}``:

    - ``anchored`` is True if any row matches all of (artifact path,
      expected_sha256, expected_reviewer).
    - ``mismatches`` lists rows whose ``artifact`` path matches but whose
      ``sha256`` or ``reviewer`` differs.
    - ``missing_anchor`` is True if no row references this artifact path.
    """
    rows = [r for r in _read_lines(req_dir) if not r.get("_corrupt")]
    anchored = False
    mismatches: list[dict] = []
    referenced = False
    for row in rows:
        if row.get("artifact") != artifact:
            continue
        referenced = True
        sha_match = row.get("sha256") == expected_sha256
        reviewer_match = row.get("reviewer") == expected_reviewer
        if sha_match and reviewer_match:
            anchored = True
        else:
            mismatches.append({
                "row_index": rows.index(row),
                "sha256_match": sha_match,
                "reviewer_match": reviewer_match,
                "row_sha256": row.get("sha256"),
                "row_reviewer": row.get("reviewer"),
            })
    return {
        "ok": anchored,
        "anchored": anchored,
        "missing_anchor": not referenced,
        "mismatches": mismatches,
    }


__all__ = [
    "ANCHOR_FILENAME",
    "ANCHOR_GENESIS_PREV",
    "RECORD_SHA256_PLACEHOLDER",
    "record_anchor",
    "record_body_sha256",
    "verify_anchor_chain",
    "verify_artifact_anchored",
]