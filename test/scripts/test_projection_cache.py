#!/usr/bin/env python3
"""Unit tests for projection_cache.py (Harness 借鉴点二·投影缓存)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent.parent / "src/scripts"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import audit_log
import projection_cache


class ProjectionCacheTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.req = Path(self._tmp.name) / "REQ-TEST"
        self.req.mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_build_on_empty_dir_is_clean(self) -> None:
        proj = projection_cache.build_projection(self.req, write=False)
        self.assertEqual(proj["session_id"], "REQ-TEST")
        self.assertEqual(proj["event_count_snapshot"], 0)
        self.assertTrue(proj["audit_chain_ok"])
        # every registry work item has a bucket
        from workflow_registry import work_items
        for item in work_items():
            self.assertIn(item["id"], proj["work_items"])
        self.assertEqual(proj["derived_from_events"], [])

    def test_write_and_read_roundtrip(self) -> None:
        proj = projection_cache.build_projection(self.req, write=True)
        loaded = projection_cache.read_projection(self.req, auto_rebuild=False)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["event_count_snapshot"], proj["event_count_snapshot"])
        self.assertTrue((self.req / ".audit" / "projection.json").is_file())

    def test_auto_rebuild_after_event_append(self) -> None:
        # Harness 借鉴点二闭环：append_event 成功后会自动重建投影缓存，
        # 因此 append 后投影不再 stale，且 event_count_snapshot 立即反映新事件。
        projection_cache.build_projection(self.req, write=True)
        self.assertFalse(projection_cache.is_stale(self.req))
        audit_log.append_event(
            self.req, event_type="init",
            payload={"skeleton": True}, extra={"requirement_name": "T"},
        )
        # 自动重建已发生：不 stale，且快照计数=1
        self.assertFalse(projection_cache.is_stale(self.req))
        proj = projection_cache.read_projection(self.req, auto_rebuild=False)
        self.assertEqual(proj["event_count_snapshot"], 1)
        # 手动删除 projection.json → 变为 stale；read_projection(auto_rebuild=True) 恢复
        (self.req / ".audit" / "projection.json").unlink()
        self.assertTrue(projection_cache.is_stale(self.req))
        proj = projection_cache.read_projection(self.req, auto_rebuild=True)
        self.assertEqual(proj["event_count_snapshot"], 1)

    def test_latest_review_for_with_review_event(self) -> None:
        # simulate a review event referencing a fake record
        record = self.req / "99-review" / "review-fake-2026-08-14.md"
        record.parent.mkdir(parents=True)
        body = ("# Review\n- work_item: project-background-goal\n"
                "- decision: approve\n- reviewer: Real\n"
                "- artifact: 001-business-requirements/01-background-goal/background-goal.md\n"
                "- artifact_content_sha256: " + "a" * 64 + "\n"
                "- reviewed_at: 2026-08-14T00:00:00+00:00\n")
        record.write_text(body, encoding="utf-8")
        audit_log.append_event(
            self.req, event_type="review",
            payload=str(record.relative_to(self.req)),
            payload_sha256=audit_log._sha256_text(body),
            extra={"work_item": "project-background-goal", "decision": "approve"},
        )
        bucket = projection_cache.latest_review_for(self.req, "project-background-goal")
        self.assertIsNotNone(bucket)
        self.assertEqual(
            bucket["latest_review_record"],
            str(Path("99-review") / "review-fake-2026-08-14.md"),
        )
        self.assertEqual(bucket["latest_review_decision"], "approve")

    def test_legacy_fallback_flag(self) -> None:
        # No events, no records → not legacy-confirmed (status not confirmed)
        bucket = projection_cache.latest_review_for(self.req, "project-background-goal")
        self.assertIsNotNone(bucket)
        self.assertIsNone(bucket.get("latest_review_record"))


if __name__ == "__main__":
    unittest.main()
