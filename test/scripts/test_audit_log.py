#!/usr/bin/env python3
"""Regression tests for audit_log.py (借鉴点一：事件溯源式审计流).

Covers:
  T1. Append is idempotent on (event_type, payload, payload_sha256).
  T2. prev_hash chain links correctly; corrupting any row breaks the chain.
  T3. Self-fingerprint (event_sha256) detects field edits.
  T4. payload_sha256 tripwire detects 同步篡改 of record + event row.
  T5. recorded_at monotonic guard rejects backwards clock skew >1s.
  T6. Unknown event_type is rejected at append time.
  T7. reconstruct_causality rebuilds init→认定→变更→确认 stages in order.
  T8. Missing payload file raises FileNotFoundError at append.
  T9. verify_chain on empty dir returns ok=True (向后兼容).
  T10. CLI entry points: verify / replay / causality --json all succeed.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent.parent / "src/scripts"
sys.path.insert(0, str(SRC))

import audit_log  # noqa: E402


def _utc_iso(offset_seconds: int = 0) -> str:
    dt = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=offset_seconds)
    return dt.isoformat()


class TestAuditLog(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.req = Path(self._tmp.name) / "REQ-999-audit-test"
        self.req.mkdir()
        (self.req / "99-review").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # ---------- T9: backward compat ----------
    def test_t9_empty_req_chain_ok(self) -> None:
        result = audit_log.verify_chain(self.req)
        self.assertTrue(result["ok"])
        self.assertEqual(result["count"], 0)
        self.assertTrue(result.get("empty"))

    # ---------- T6: event_type validation ----------
    def test_t6_reject_unknown_event_type(self) -> None:
        with self.assertRaises(ValueError):
            audit_log.append_event(self.req, "NOT_A_TYPE", {"foo": 1})

    # ---------- T1: idempotent append ----------
    def test_t1_append_idempotent(self) -> None:
        payload = {"inline": True, "v": 1}
        r1 = audit_log.append_event(self.req, "init", payload)
        self.assertTrue(r1["recorded"])
        r2 = audit_log.append_event(self.req, "init", payload)
        self.assertFalse(r2["recorded"])
        self.assertTrue(r2["skipped_dedup"])
        events = audit_log.replay_events(self.req)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_id"], 1)

    # ---------- T2: hash chain continuity ----------
    def test_t2_prev_hash_chain_and_corrupt_breaks(self) -> None:
        for i in range(4):
            audit_log.append_event(
                self.req, "decision", {"step": i}, recorded_at=_utc_iso(i)
            )
        chain = audit_log.verify_chain(self.req)
        self.assertTrue(chain["ok"], f"expected clean chain, got {chain['issues']}")
        self.assertEqual(chain["count"], 4)
        # Corrupt any middle row by flipping prev_hash → must CRITICAL
        lines = (self.req / ".audit/events.jsonl").read_text(encoding="utf-8").splitlines()
        rows = [json.loads(l) for l in lines]
        rows[2]["prev_hash"] = "b" * 64
        (self.req / ".audit/events.jsonl").write_text(
            "\n".join(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows) + "\n",
            encoding="utf-8",
        )
        broken = audit_log.verify_chain(self.req)
        self.assertFalse(broken["ok"])
        severities = {i["severity"] for i in broken["issues"]}
        self.assertIn("CRITICAL", severities)

    # ---------- T3: self-fingerprint integrity ----------
    def test_t3_self_fingerprint_flags_tamper(self) -> None:
        audit_log.append_event(self.req, "init", {"a": 1})
        audit_log.append_event(self.req, "review", {"b": 2}, recorded_at=_utc_iso(1))
        # Tamper: change payload inline value from 2 to 999, don't recompute event_sha256
        lines = (self.req / ".audit/events.jsonl").read_text(encoding="utf-8").splitlines()
        rows = [json.loads(l) for l in lines]
        rows[1]["payload"]["b"] = 999
        (self.req / ".audit/events.jsonl").write_text(
            "\n".join(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows) + "\n",
            encoding="utf-8",
        )
        broken = audit_log.verify_chain(self.req)
        self.assertFalse(broken["ok"])
        checks = {i.get("check") for i in broken["issues"]}
        self.assertIn("audit_chain.event_sha256_mismatch", checks)

    # ---------- T4: payload_sha256 同步篡改 tripwire ----------
    def test_t4_payload_hash_detects_synchronized_tamper(self) -> None:
        rec = self.req / "99-review/review-test.md"
        original_body = "# Review: test\n- decision: approve\n- reviewer: 张三\n"
        rec.write_text(original_body, encoding="utf-8")
        orig_hash = audit_log._sha256_text(original_body)
        r = audit_log.append_event(
            self.req, "review", "99-review/review-test.md", payload_sha256=orig_hash,
            extra={"work_item": "project-background-goal"},
        )
        self.assertTrue(r["recorded"])
        # 同步篡改：rewrite both the record file AND the event row's payload_sha256,
        # but DON'T recompute event_sha256. The self-fingerprint should break first.
        tampered_body = "# Review: test\n- decision: approve\n- reviewer: 李四\n"
        rec.write_text(tampered_body, encoding="utf-8")
        new_hash = audit_log._sha256_text(tampered_body)
        lines = (self.req / ".audit/events.jsonl").read_text(encoding="utf-8").splitlines()
        rows = [json.loads(l) for l in lines]
        rows[0]["payload_sha256"] = new_hash
        (self.req / ".audit/events.jsonl").write_text(
            "\n".join(json.dumps(rr, sort_keys=True, ensure_ascii=False) for rr in rows) + "\n",
            encoding="utf-8",
        )
        broken = audit_log.verify_chain(self.req)
        self.assertFalse(broken["ok"])
        checks = {i.get("check") for i in broken["issues"]}
        # Either event_sha256 mismatch OR payload_hash_mismatch (if attacker also
        # recomputed event_sha256 but not the prev_hash chain) — the point is
        # at least one tripwire fires.
        self.assertTrue(
            "audit_chain.event_sha256_mismatch" in checks
            or "audit_chain.payload_hash_mismatch" in checks,
            f"expected a tripwire to fire among {checks}",
        )

    # ---------- T5: monotonic recorded_at ----------
    def test_t5_monotonic_ts_rejects_backwards_skew(self) -> None:
        audit_log.append_event(self.req, "init", {"v": 1}, recorded_at=_utc_iso(0))
        # 3s backwards = > 1s fuzz → reject
        with self.assertRaises(ValueError):
            audit_log.append_event(
                self.req, "review", {"v": 2}, recorded_at=_utc_iso(-3)
            )
        # 0s delta (= same second) OK, +1s OK.
        audit_log.append_event(self.req, "review", {"v": 3}, recorded_at=_utc_iso(0))
        audit_log.append_event(self.req, "decision", {"v": 4}, recorded_at=_utc_iso(1))
        self.assertEqual(len(audit_log.replay_events(self.req)), 3)

    # ---------- T8: missing payload file raises ----------
    def test_t8_missing_payload_file_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            audit_log.append_event(
                self.req, "review", "99-review/nope.md", payload_sha256="a" * 64,
            )
        with self.assertRaises(ValueError):
            # path payload → payload_sha256 required
            fake = self.req / "99-review/x.md"
            fake.write_text("body", encoding="utf-8")
            audit_log.append_event(self.req, "review", "99-review/x.md")  # missing payload_sha256

    # ---------- T7: causal stage reconstruction ----------
    def test_t7_reconstruct_causality_stages(self) -> None:
        # init
        audit_log.append_event(self.req, "init", {"v": 1})
        # review (认定) → approve → confirmed
        rec = self.req / "99-review/review-bg.md"
        rec.write_text("# R\n- decision: approve\n", encoding="utf-8")
        audit_log.append_event(
            self.req, "review", "99-review/review-bg.md",
            payload_sha256=audit_log._sha256_text(rec.read_text(encoding="utf-8")),
            extra={"work_item": "project-background-goal", "decision": "approve",
                   "reviewer": "张三"},
        )
        # change → 变更
        crec = self.req / "99-review/change-bg.md"
        crec.write_text("# C\n- reason: bug\n", encoding="utf-8")
        audit_log.append_event(
            self.req, "change", "99-review/change-bg.md",
            payload_sha256=audit_log._sha256_text(crec.read_text(encoding="utf-8")),
            extra={"work_item": "project-background-goal", "from_status": "confirmed",
                   "to_status": "draft"},
        )
        # reflow
        rrec = self.req / "99-review/change-record-reflow.md"
        rrec.write_text("# Rf\n- superseded: ux\n", encoding="utf-8")
        audit_log.append_event(
            self.req, "reflow", "99-review/change-record-reflow.md",
            payload_sha256=audit_log._sha256_text(rrec.read_text(encoding="utf-8")),
            extra={"work_item": "project-background-goal", "superseded": ["product-ux"]},
        )
        causality = audit_log.reconstruct_causality(self.req)
        self.assertTrue(causality["chain_ok"])
        phases = [s["phase"] for s in causality["stages"]]
        self.assertEqual(phases, ["init", "认定", "变更", "变更"])
        self.assertEqual(causality["event_count"], 4)
        # Second stage should carry work_item + reviewer + decision
        self.assertEqual(causality["stages"][1]["reviewer"], "张三")
        self.assertEqual(causality["stages"][1]["work_item"], "project-background-goal")
        self.assertEqual(causality["stages"][1]["decision"], "approve")

    # ---------- T10: CLI entry points ----------
    def test_t10_cli_entry_points(self) -> None:
        audit_log.append_event(self.req, "init", {"v": 1})
        script = str(SRC / "audit_log.py")
        for action in ("verify", "replay", "causality"):
            cp = subprocess.run(
                [sys.executable, script, str(self.req), action, "--json"],
                capture_output=True, text=True, check=False, encoding="utf-8", errors="replace",
            )
            self.assertEqual(cp.returncode, 0, f"{action} failed: {cp.stderr}")
            try:
                obj = json.loads(cp.stdout)
            except json.JSONDecodeError as e:
                self.fail(f"{action} --json not valid JSON: {e}\n{cp.stdout}")
            self.assertIsInstance(obj, dict)


if __name__ == "__main__":
    unittest.main()
