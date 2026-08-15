#!/usr/bin/env python3
"""Regression tests for the B13 / P0 external hash anchor (hash_anchor.py).

Each fixture here is a *self-contained* temp dir that pretends to be a
requirement under ``99-review/``. The scenarios cover:

  1. test_record_and_verify_basic — record one anchor, verify it.
  2. test_chain_break_detected — tamper with a middle row, verify the chain
     walk flags the break at the right index.
  3. test_missing_anchor_detected — delete the anchor file entirely, verify
     branch_validator reports "missing" without false positives (legacy
     requirements must keep passing until they record at least one anchor).
  4. test_artifact_drift_detected — record an anchor for one sha256, then
     rewrite the artifact (and the ReviewRecord) with a different content
     but leave the anchor alone. Verify the anchor mismatch is detected.
  5. test_record_sha256_sync_tamper_detected — change the artifact AND update
     the recorded artifact_content_sha256 in lockstep (so the closed-loop hash
     check passes); verify the record_sha256 self-fingerprint still catches it.
  6. test_record_sha256_backward_compat — legacy ReviewRecords without the
     record_created_at / record_sha256 fields must stay green (non-blocking
     HIGH notice, never CRITICAL).

These tests guard the B13 fix; they must stay green while the existing 77
regression cases also pass (a project-wide re-run is the only acceptance
gate). All tests are unittest-based so ``bash run_tests_mac.sh`` picks them
up automatically via the ``test_*.py`` glob.
"""

from __future__ import annotations

import importlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "src/scripts"
sys.path.insert(0, str(SCRIPTS))

import branch_validator  # noqa: E402
import hash_anchor  # noqa: E402
from workflow_registry import artifact_content_hash  # noqa: E402


class HashAnchorTest(unittest.TestCase):
    def _make_req(self) -> Path:
        """Build a minimal req layout: 99-review/ + a single review record."""
        temp = Path(tempfile.mkdtemp())
        req = temp / "REQ-TEST"
        review_dir = req / "99-review"
        review_dir.mkdir(parents=True)
        self._write_record(req, "deadbeef")
        # Keep a reference so tests can clean up.
        self._tempdir = temp
        return req

    def _write_record(self, req: Path, artifact_hash: str) -> Path:
        """Write a ReviewRecord whose record_sha256 is consistent with its body.

        Mirrors the writer in pipeline.py: record_sha256 covers the whole body
        except the record_sha256 line itself.
        """
        record = req / "99-review" / "review-bg-2026-08-14.md"
        lines = [
            "# Review: 项目背景与目标",
            "",
            "- work_item: project-background-goal",
            "- artifact: 001-business-requirements/01-background-goal/background-goal.md",
            "- artifact_version: v0.1",
            f"- artifact_content_sha256: {artifact_hash}",
            "- decision: approve",
            "- reviewer: Ayan",
            "- reviewer_id: u-ayan",
            "- reviewer_role: business_owner",
            "- reviewed_at: 2026-08-14T10:00:00+00:00",
            "- record_created_at: 2026-08-14T10:00:00+00:00",
            f"- record_sha256: {hash_anchor.RECORD_SHA256_PLACEHOLDER}",
            "- comments: 无",
            "",
        ]
        text = "\n".join(lines)
        text = text.replace(
            hash_anchor.RECORD_SHA256_PLACEHOLDER,
            hash_anchor.record_body_sha256(text),
        )
        record.write_text(text, encoding="utf-8")
        return record

    def tearDown(self) -> None:
        shutil.rmtree(self._tempdir, ignore_errors=True)

    # ----- scenario 1: happy path -----------------------------------------

    def test_record_and_verify_basic(self) -> None:
        req = self._make_req()
        result = hash_anchor.record_anchor(
            req,
            artifact="001-business-requirements/01-background-goal/background-goal.md",
            artifact_id="BG-001",
            reviewer="Ayan",
            review_record="99-review/review-bg-2026-08-14.md",
            sha256="a" * 64,
            ts="2026-08-14T10:00:00+00:00",
        )
        self.assertTrue(result["recorded"])
        self.assertFalse(result["skipped_dedup"])
        chain = hash_anchor.verify_anchor_chain(req)
        self.assertTrue(chain["ok"], chain["issues"])
        self.assertEqual(chain["count"], 1)
        self.assertIsNone(chain["break_at"])
        self.assertFalse(chain["missing"])

        anchored = hash_anchor.verify_artifact_anchored(
            req,
            artifact="001-business-requirements/01-background-goal/background-goal.md",
            expected_sha256="a" * 64,
            expected_reviewer="Ayan",
        )
        self.assertTrue(anchored["anchored"])
        self.assertFalse(anchored["missing_anchor"])

        # Idempotency: a second call with the same triple must NOT append.
        again = hash_anchor.record_anchor(
            req,
            artifact="001-business-requirements/01-background-goal/background-goal.md",
            artifact_id="BG-001",
            reviewer="Ayan",
            review_record="99-review/review-bg-2026-08-14.md",
            sha256="a" * 64,
            ts="2026-08-14T10:00:00+00:00",
        )
        self.assertFalse(again["recorded"])
        self.assertTrue(again["skipped_dedup"])
        self.assertEqual(hash_anchor.verify_anchor_chain(req)["count"], 1)

    # ----- scenario 2: tamper in the middle of the chain ------------------

    def test_chain_break_detected(self) -> None:
        req = self._make_req()
        for i, sha in enumerate(["1" * 64, "2" * 64, "3" * 64]):
            hash_anchor.record_anchor(
                req,
                artifact=f"001-business-requirements/01-background-goal/artifact-{i}.md",
                artifact_id=f"BG-{i:03d}",
                reviewer="Ayan",
                review_record=f"99-review/review-bg-{i}.md",
                sha256=sha,
                ts=f"2026-08-14T10:0{i}:00+00:00",
            )
        # Chain is intact so far.
        ok_chain = hash_anchor.verify_anchor_chain(req)
        self.assertTrue(ok_chain["ok"], ok_chain["issues"])
        self.assertEqual(ok_chain["count"], 3)

        # Tamper with the middle row: rewrite the file with the row's sha256
        # field changed but keep the line structure intact. The walker will
        # see the new line's hash and notice the next row's prev_anchor_sha256
        # no longer matches.
        path = hash_anchor._anchor_path(req)
        lines = path.read_text(encoding="utf-8").splitlines()
        tampered_row = json.loads(lines[1])
        tampered_row["sha256"] = "f" * 64
        lines[1] = json.dumps(tampered_row, sort_keys=True, ensure_ascii=False)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        broken = hash_anchor.verify_anchor_chain(req)
        self.assertFalse(broken["ok"])
        self.assertEqual(broken["count"], 3)
        # The break is at row 3 (index 2): row 2's sha256 changed, so row 2's
        # line hash changed, so row 3's prev_anchor_sha256 no longer matches
        # the new hash of row 2.
        self.assertEqual(broken["break_at"], 2)
        self.assertTrue(any("broken at record 2" in issue for issue in broken["issues"]))

        # branch_validator must surface this as CRITICAL. The validator only checks
        # anchors when it sees a confirmed artifact, so plant one (and its
        # ReviewRecord) referencing an existing artifact path used above.
        import hashlib as _hashlib
        body_hash = _hashlib.sha256(b"# body").hexdigest()
        artifact = req / "001-business-requirements/01-background-goal" / "artifact-0.md"
        artifact.parent.mkdir(parents=True)
        artifact.write_text(
            "---\nartifact_id: BG-000\nstatus: confirmed\nreviewer: Ayan\n---\n# body\n",
            encoding="utf-8",
        )
        # Anchor the confirmed artifact with a hash that matches its current body
        # so the anchor check reaches the chain-broken step.
        hash_anchor.record_anchor(
            req,
            artifact="001-business-requirements/01-background-goal/artifact-0.md",
            artifact_id="BG-000",
            reviewer="Ayan",
            review_record="99-review/review-bg-2026-08-14.md",
            sha256=body_hash,
            ts="2026-08-14T10:00:01+00:00",
        )
        # Update the ReviewRecord to match.
        (req / "99-review" / "review-bg-2026-08-14.md").write_text(
            "\n".join([
                "# Review: 项目背景与目标",
                "",
                "- work_item: project-background-goal",
                "- artifact: 001-business-requirements/01-background-goal/artifact-0.md",
                "- artifact_version: v0.1",
                f"- artifact_content_sha256: {body_hash}",
                "- decision: approve",
                "- reviewer: Ayan",
                "- reviewed_at: 2026-08-14T10:00:01+00:00",
                "",
            ]),
            encoding="utf-8",
        )
        validator_result = branch_validator.validate_records(req)
        chain_issues = [i for i in validator_result["issues"]
                        if "hash anchor chain broken" in i["message"]]
        self.assertGreaterEqual(len(chain_issues), 1, validator_result["issues"])
        self.assertTrue(all(i["severity"] == "CRITICAL" for i in chain_issues))

    # ----- scenario 3: anchor file missing entirely -----------------------

    def test_missing_anchor_detected(self) -> None:
        req = self._make_req()
        # No anchor file exists yet: verify_anchor_chain must report missing=True
        # and NOT raise; verify_artifact_anchored must report missing_anchor=True.
        chain = hash_anchor.verify_anchor_chain(req)
        self.assertTrue(chain["ok"])
        self.assertTrue(chain["missing"])
        self.assertEqual(chain["count"], 0)

        anchored = hash_anchor.verify_artifact_anchored(
            req,
            artifact="001-business-requirements/01-background-goal/background-goal.md",
            expected_sha256="a" * 64,
            expected_reviewer="Ayan",
        )
        self.assertFalse(anchored["anchored"])
        self.assertTrue(anchored["missing_anchor"])

        # branch_validator on a req with NO confirmed artifact and NO anchor
        # must remain PASS (backward-compat: only confirmed artifacts are
        # checked against the anchor).
        validator_result = branch_validator.validate_records(req)
        blocking = [i for i in validator_result["issues"]
                    if i["severity"] in {"CRITICAL", "HIGH"}]
        self.assertEqual(blocking, [])

    # ----- scenario 4: artifact drifts but anchor is untouched ------------

    def test_artifact_drift_detected(self) -> None:
        req = self._make_req()
        original_sha = "1" * 64
        hash_anchor.record_anchor(
            req,
            artifact="001-business-requirements/01-background-goal/background-goal.md",
            artifact_id="BG-001",
            reviewer="Ayan",
            review_record="99-review/review-bg-2026-08-14.md",
            sha256=original_sha,
            ts="2026-08-14T10:00:00+00:00",
        )

        # Drift: the artifact's content changes (and so does the ReviewRecord's
        # recorded hash — but the attacker forgets to rewrite the anchor).
        new_sha = "9" * 64
        record = req / "99-review" / "review-bg-2026-08-14.md"
        record.write_text(
            record.read_text(encoding="utf-8").replace(
                "artifact_content_sha256: deadbeef",
                f"artifact_content_sha256: {new_sha}",
            ),
            encoding="utf-8",
        )

        # Anchor chain is still valid (anchor itself untouched).
        chain = hash_anchor.verify_anchor_chain(req)
        self.assertTrue(chain["ok"], chain["issues"])

        # But the artifact's current sha no longer matches any anchor row.
        anchored = hash_anchor.verify_artifact_anchored(
            req,
            artifact="001-business-requirements/01-background-goal/background-goal.md",
            expected_sha256=new_sha,
            expected_reviewer="Ayan",
        )
        self.assertFalse(anchored["anchored"])
        self.assertFalse(anchored["missing_anchor"])
        self.assertEqual(len(anchored["mismatches"]), 1)
        self.assertFalse(anchored["mismatches"][0]["sha256_match"])

        # And branch_validator surfaces the drift as CRITICAL.
        # First, register a confirmed artifact so the check actually fires.
        artifact = req / "001-business-requirements/01-background-goal/background-goal.md"
        artifact.parent.mkdir(parents=True)
        artifact.write_text(
            "---\nartifact_id: BG-001\nstatus: confirmed\nreviewer: Ayan\n---\n# body\n",
            encoding="utf-8",
        )
        result = branch_validator.validate_records(req)
        mismatch = [i for i in result["issues"] if "anchor sha256 mismatch" in i["message"]]
        self.assertEqual(len(mismatch), 1)
        self.assertEqual(mismatch[0]["severity"], "CRITICAL")

        # Drift the reviewer instead: anchor stays valid; mismatch is reviewer-side.
        artifact.write_text(
            "---\nartifact_id: BG-001\nstatus: confirmed\nreviewer: Mallory\n---\n# body\n",
            encoding="utf-8",
        )
        result2 = branch_validator.validate_records(req)
        reviewer_mismatch = [i for i in result2["issues"]
                             if "anchor reviewer mismatch" in i["message"]]
        self.assertEqual(len(reviewer_mismatch), 1)
        self.assertEqual(reviewer_mismatch[0]["severity"], "CRITICAL")

    # ----- scenario 5: artifact + ReviewRecord hash 同步篡改 ---------------

    def test_record_sha256_sync_tamper_detected(self) -> None:
        """B13: editing artifact AND the recorded hash in lockstep is caught.

        The closed-loop check (artifact current hash vs artifact_content_sha256
        in the record) passes because the attacker updates BOTH the artifact and
        the recorded hash. The record_sha256 self-fingerprint is the layer that
        catches it: editing artifact_content_sha256 changes the record body, so
        the declared record_sha256 no longer matches.
        """
        req = self._make_req()
        artifact = req / "001-business-requirements/01-background-goal/background-goal.md"
        artifact.parent.mkdir(parents=True)
        original = "---\nartifact_id: BG-001\nstatus: confirmed\nreviewer: Ayan\n---\n# body\n"
        artifact.write_text(original, encoding="utf-8")
        original_hash = artifact_content_hash(original)

        # Rewrite the ReviewRecord so its artifact_content_sha256 and
        # record_sha256 are both consistent with the artifact's real hash.
        record = self._write_record(req, original_hash)

        # Sanity: before tampering, the validator must PASS.
        before = branch_validator.validate_records(req)
        self.assertTrue(before["ok"], before["issues"])

        # Sync tamper: change the artifact content AND update the recorded hash
        # to match, but leave record_sha256 untouched.
        tampered = original + "\n## 新增段落（被篡改）\n"
        artifact.write_text(tampered, encoding="utf-8")
        tampered_hash = artifact_content_hash(tampered)
        record.write_text(
            record.read_text(encoding="utf-8").replace(
                f"artifact_content_sha256: {original_hash}",
                f"artifact_content_sha256: {tampered_hash}",
            ),
            encoding="utf-8",
        )

        after = branch_validator.validate_records(req)
        # The closed-loop check now passes (artifact hash == recorded hash), so
        # the ONLY thing that can catch the tamper is the record_sha256
        # self-fingerprint.
        closed_loop = [i for i in after["issues"]
                       if "differs from its ReviewRecord hash" in i["message"]]
        self.assertEqual(closed_loop, [])
        fingerprint = [i for i in after["issues"]
                       if "differs from its record_sha256" in i["message"]]
        self.assertEqual(len(fingerprint), 1)
        self.assertEqual(fingerprint[0]["severity"], "CRITICAL")
        self.assertFalse(after["ok"])

    # ----- scenario 6: legacy records without the new fields stay green -----

    def test_record_sha256_backward_compat(self) -> None:
        """Legacy ReviewRecords without the immutable-anchor fields must not FAIL.

        Missing record_created_at / record_sha256 is a non-blocking HIGH notice
        (blocking=False); only a present-but-mismatched record_sha256 is
        CRITICAL, so already-confirmed cases never FAIL for lacking the fields.
        """
        req = self._make_req()
        # Strip the new fields to simulate a legacy record.
        record = req / "99-review" / "review-bg-2026-08-14.md"
        record.write_text(
            re.sub(
                r"(?m)^\s*-\s*(record_created_at|record_sha256):.*$\n?",
                "",
                record.read_text(encoding="utf-8"),
            ),
            encoding="utf-8",
        )
        result = branch_validator.validate_records(req)
        self.assertTrue(result["ok"], result["issues"])
        notice = [i for i in result["issues"] if "missing immutable anchor" in i["message"]]
        self.assertEqual(len(notice), 1)
        self.assertEqual(notice[0]["severity"], "HIGH")
        self.assertFalse(notice[0].get("blocking", True))
        self.assertTrue(all(i["severity"] != "CRITICAL" for i in result["issues"]))


if __name__ == "__main__":
    unittest.main()