#!/usr/bin/env python3
"""Compatibility entry point for shared review, change, and reflow records."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from workflow_registry import (
    artifact_content_hash,
    find_artifact,
    read_frontmatter,
    work_items,
)

import audit_log
import hash_anchor
import projection_cache
from validation_errors import make_issue

FAMILY = "branch_validator"


def _reviewed_at(record: Path) -> str:
    """Return the reviewed_at timestamp of a review record ('' if missing)."""
    m = re.search(r"(?m)^\s*-\s*reviewed_at:\s*(.+)$", record.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else ""


def _legacy_latest_review_for_artifact(req_dir: Path, artifact_rel: str) -> Path | None:
    """Legacy glob+sort fallback (B7-pitfall-prone, kept only for pre-projection cases).

    Deprecated in favour of :func:`projection_cache.latest_review_for`; use this
    only when projection is unavailable and the caller requires a path.
    """
    review_records = list(req_dir.glob("99-review/review-*.md"))
    matching = [r for r in review_records if artifact_rel in r.read_text(encoding="utf-8")]
    if not matching:
        return None
    matching.sort(key=lambda r: _reviewed_at(r))
    return matching[-1]


def validate_records(req_dir: Path) -> dict:
    issues: list[dict] = []
    artifacts = {}
    review_records = list(req_dir.glob("99-review/review-*.md"))
    # 借鉴点二：投影缓存（物化视图）。一次性构建 projection，所有 work_item 对"最
    # 新评审记录"的判定都来自同一个 source of truth，不再各自 glob+sort 导致漂移。
    try:
        projection_cache.build_projection(req_dir, write=True)
        projection_avail = True
    except Exception:
        # 构建失败不致命：回退 legacy 模式并追加一个 HIGH 级 notice，让回归保持绿
        # 色；同时投影问题在日志中可见。
        projection_avail = False
        issues.append(make_issue(
            severity="HIGH", check_id="projection.build_failed", family=FAMILY,
            location=".audit/projection.json",
            message="projection_cache.build_projection raised; falling back to legacy glob-sort",
            expected="projection_cache.build_projection 应成功构建 .audit/projection.json",
            actual="build_projection 抛出异常（详见 stderr）",
            repair_hint="检查 .audit/events.jsonl 是否损坏、workflow-registry 是否正确；可运行 "
                        "python3 src/scripts/projection_cache.py <req_dir> build 手动重建并查看报错",
            source_ref="contracts.md §ProjectionCache",
            blocking=False,
        ))
    for item in work_items():
        artifact = find_artifact(req_dir, item)
        if artifact:
            fm = read_frontmatter(artifact)
            artifact_id = fm.get("artifact_id")
            if artifact_id:
                artifacts[artifact_id] = artifact
            if fm.get("status") == "confirmed":
                reviewer = fm.get("reviewer", "")
                normalized = reviewer.lower()
                if (not reviewer or reviewer in {"待确认", "待评审", "AI"}
                        or "simulat" in normalized or "模拟" in reviewer):
                    issues.append(make_issue(
                        severity="CRITICAL", check_id="confirmed.no_valid_reviewer", family=FAMILY,
                        location=str(artifact.relative_to(req_dir)),
                        field_path="frontmatter.reviewer",
                        message="confirmed artifact has no valid human reviewer",
                        expected="confirmed 产物的 frontmatter.reviewer 必须是真实具名人工评审人（非 AI/待确认/模拟）",
                        actual=f"reviewer='{reviewer}'",
                        repair_hint=f"在 {artifact.relative_to(req_dir)} 的 frontmatter 填写真实评审人姓名",
                        source_ref="constitution §6 人工闸门不可绕过 / contracts.md §Artifact States",
                    ))
                expected = str(artifact.relative_to(req_dir))
                # --- 判定最新评审记录：优先投影缓存，回退 legacy glob-sort ---
                newest_record_path: Path | None = None
                if projection_avail:
                    bucket = projection_cache.latest_review_for(req_dir, item["id"])
                    proj_record_rel = bucket.get("latest_review_record") if isinstance(bucket, dict) else None
                    if proj_record_rel:
                        candidate = req_dir / proj_record_rel
                        if candidate.is_file():
                            newest_record_path = candidate
                        else:
                            issues.append(make_issue(
                                severity="HIGH", check_id="projection.stale_record_path", family=FAMILY,
                                location=".audit/projection.json",
                                field_path=f"work_items.{item['id']}.latest_review_record",
                                message=f"projection points to missing ReviewRecord {proj_record_rel}; fallback to glob-sort",
                                expected="投影指向的 latest_review_record 必须存在于磁盘",
                                actual=f"{candidate} 不存在",
                                repair_hint="删除或重建 .audit/projection.json（append_event 会自动重建）",
                                source_ref="contracts.md §ProjectionCache",
                                blocking=False,
                            ))
                if newest_record_path is None:
                    # Legacy fallback (B7-prone path): only hit for requirements
                    # created before audit_log/projection_cache were adopted.
                    newest_record_path = _legacy_latest_review_for_artifact(req_dir, expected)
                if newest_record_path is None:
                    issues.append(make_issue(
                        severity="CRITICAL", check_id="confirmed.no_review_record", family=FAMILY,
                        location=expected, field_path="99-review",
                        message="confirmed artifact has no matching ReviewRecord",
                        expected=f"confirmed 产物 {expected} 必须存在匹配的 99-review/review-*.md 记录",
                        actual="未找到任何引用该产物路径的评审记录",
                        repair_hint=f"为该产物补做人工评审并写入 99-review/review-*.md（含 artifact_content_sha256）",
                        source_ref="contracts.md §ReviewRecord / constitution §6",
                    ))
                else:
                    # 现在 newest_record_path 是确定的，不需要再排序
                    current_hash = artifact_content_hash(artifact.read_text(encoding="utf-8"))
                    newest_text = newest_record_path.read_text(encoding="utf-8")
                    recorded_hash = re.search(r"artifact_content_sha256:\s*([0-9a-f]{64})", newest_text)
                    if recorded_hash and recorded_hash.group(1) != current_hash:
                        issues.append(make_issue(
                            severity="CRITICAL", check_id="confirmed.hash_differs", family=FAMILY,
                            location=expected, field_path="frontmatter.artifact_content_sha256",
                            message="confirmed artifact content differs from its ReviewRecord hash",
                            expected=f"当前产物内容 hash 必须等于最新评审记录声明的 artifact_content_sha256（{recorded_hash.group(1)[:12]}…）",
                            actual=f"当前 hash={current_hash[:12]}…",
                            repair_hint=f"产物在评审后被修改：回退到评审时版本，或重新走 review 流程更新评审记录与 hash",
                            source_ref="contracts.md §ReviewRecord 绑定内容 hash",
                        ))
                    # B13 fix: external anchor check. The chain hash on its own
                    # is closed-loop (artifact + ReviewRecord can be swapped in
                    # lockstep). The .hash-anchor.jsonl file under 99-review
                    # provides an external append-only anchor; if BOTH the
                    # artifact and the ReviewRecord were rewritten together
                    # AND the anchor was rewritten too, the anchor's internal
                    # hash chain breaks (or the row goes missing entirely).
                    anchor_chain = hash_anchor.verify_anchor_chain(req_dir)
                    if not anchor_chain["ok"]:
                        for chain_issue in anchor_chain["issues"]:
                            issues.append(make_issue(
                                severity="CRITICAL", check_id="anchor.chain_broken", family=FAMILY,
                                location=expected, field_path="99-review/.hash-anchor.jsonl",
                                message=chain_issue,
                                expected="外部锚点链 .hash-anchor.jsonl 必须完整（hash 链连续）",
                                actual=chain_issue,
                                repair_hint="锚点链被篡改：核对 99-review/.hash-anchor.jsonl 各行 prev_hash 与 hash；被改动的行需人工复核",
                                source_ref="hash_anchor.py §B13 外部锚点",
                            ))
                        continue
                    if anchor_chain["missing"]:
                        # Backward-compat: legacy requirements never recorded
                        # anchors — skip the per-artifact check rather than
                        # regress all 8 existing cases.
                        continue
                    anchor_check = hash_anchor.verify_artifact_anchored(
                        req_dir, expected, current_hash, reviewer,
                    )
                    if anchor_check["missing_anchor"]:
                        issues.append(make_issue(
                            severity="CRITICAL", check_id="anchor.missing", family=FAMILY,
                            location=expected, field_path="99-review/.hash-anchor.jsonl",
                            message="confirmed artifact not anchored to .hash-anchor.jsonl",
                            expected="每个 confirmed 产物都必须在 99-review/.hash-anchor.jsonl 有锚点行（sha256+reviewer 绑定）",
                            actual=f"{expected} 无对应锚点行",
                            repair_hint="运行 pipeline.py review（approve）重新记录锚点，或用 hash_anchor.record_anchor 补锚",
                            source_ref="hash_anchor.py §B13 外部锚点",
                        ))
                    else:
                        # report every mismatched row's individual problems
                        for mismatch in anchor_check["mismatches"]:
                            if not mismatch["sha256_match"]:
                                issues.append(make_issue(
                                    severity="CRITICAL", check_id="anchor.sha256_mismatch", family=FAMILY,
                                    location=expected, field_path="99-review/.hash-anchor.jsonl",
                                    message="anchor sha256 mismatch",
                                    expected="锚点行声明的 sha256 必须等于当前产物 hash",
                                    actual=f"锚点 sha256={mismatch.get('sha256','')[:12]}… 与当前 hash={current_hash[:12]}… 不一致",
                                    repair_hint="产物在锚定后被修改：回退内容或重新评审更新锚点",
                                    source_ref="hash_anchor.py §B13 外部锚点",
                                ))
                            if not mismatch["reviewer_match"]:
                                issues.append(make_issue(
                                    severity="CRITICAL", check_id="anchor.reviewer_mismatch", family=FAMILY,
                                    location=expected, field_path="99-review/.hash-anchor.jsonl",
                                    message="anchor reviewer mismatch with ReviewRecord",
                                    expected="锚点行的 reviewer 必须与评审记录/产物 frontmatter 的 reviewer 一致",
                                    actual="reviewer 不一致（锚点记录与评审记录分属不同评审人）",
                                    repair_hint="核对锚点行 reviewer 与 ReviewRecord reviewer；若有异议按变更管理流程处理",
                                    source_ref="hash_anchor.py §B13 外部锚点",
                                ))

    for record in review_records:
        text = record.read_text(encoding="utf-8")
        for required in ["work_item:", "decision:", "reviewer:", "reviewed_at:"]:
            if required not in text:
                issues.append(make_issue(
                    severity="HIGH", check_id=f"review_record.missing_{required[:-1]}", family=FAMILY,
                    location=str(record.relative_to(req_dir)),
                    field_path=f"99-review.{record.name}.{required}",
                    message=f"review record missing {required}",
                    expected=f"评审记录必须包含字段 {required}",
                    actual=f"{record.name} 中未找到 '{required}'",
                    repair_hint=f"在 {record.relative_to(req_dir)} 中补充 {required} 字段",
                    source_ref="contracts.md §ReviewRecord 字段契约",
                    blocking=False,
                ))
        # B13 fix: immutable self-fingerprint of the ReviewRecord. record_sha256
        # covers the whole record body except the record_sha256 line itself, so
        # editing any field (e.g. artifact_content_sha256 to match a rewritten
        # artifact) breaks the fingerprint even when the artifact + record hash
        # pair is kept internally consistent.
        has_created = bool(re.search(r"(?m)^\s*-\s*record_created_at:", text))
        has_sha = bool(re.search(r"(?m)^\s*-\s*record_sha256:", text))
        if not has_created or not has_sha:
            # Backward-compat: legacy ReviewRecords predate the immutable-anchor
            # fields. Missing fields are a non-blocking HIGH notice (blocking=False),
            # so already-confirmed cases never FAIL merely for lacking the new
            # fields; only a present-but-mismatched record_sha256 is CRITICAL.
            missing = [name for name, present in (("record_created_at", has_created), ("record_sha256", has_sha)) if not present]
            issues.append(make_issue(
                severity="HIGH", check_id="review_record.missing_immutable_anchor", family=FAMILY,
                location=str(record.relative_to(req_dir)),
                field_path=f"99-review.{record.name}.{'/'.join(missing)}",
                message=f"review record missing immutable anchor ({' / '.join(missing)})",
                expected=f"评审记录应包含 record_created_at 与 record_sha256（B13 自指纹）",
                actual=f"缺少字段：{' / '.join(missing)}",
                repair_hint=f"为 {record.relative_to(req_dir)} 补写 record_created_at 与 record_sha256（由 hash_anchor.record_body_sha256 生成）",
                source_ref="contracts.md §ReviewRecord record_sha256 自指纹 / hash_anchor.py §B13",
                blocking=False,
            ))
        if has_sha:
            declared = re.search(r"(?m)^\s*-\s*record_sha256:\s*(\S+)\s*$", text)
            computed = hash_anchor.record_body_sha256(text)
            if not declared or declared.group(1) != computed:
                issues.append(make_issue(
                    severity="CRITICAL", check_id="review_record.self_fingerprint_mismatch", family=FAMILY,
                    location=str(record.relative_to(req_dir)),
                    field_path=f"99-review.{record.name}.record_sha256",
                    message="review record content differs from its record_sha256",
                    expected="record_sha256 自指纹必须匹配记录正文（B13 防同步篡改）",
                    actual=f"声明={declared.group(1)[:12] if declared else '缺失'}… computed={computed[:12]}…",
                    repair_hint=f"记录被修改过：回退 {record.relative_to(req_dir)} 到原始内容，或重新评审生成新记录",
                    source_ref="contracts.md §ReviewRecord record_sha256 自指纹",
                ))

    for record in list(req_dir.glob("**/*change*.md")) + list(req_dir.glob("**/*reflow*.md")):
        text = record.read_text(encoding="utf-8")
        if not re.search(r"downstream|下游|影响", text, re.IGNORECASE):
            issues.append(make_issue(
                severity="HIGH", check_id="change_record.missing_downstream_impact", family=FAMILY,
                location=str(record.relative_to(req_dir)),
                field_path=f"99-review.{record.name}",
                message="change/reflow record missing downstream impact",
                expected="变更/回流记录必须声明下游影响（downstream/下游/影响 关键字）",
                actual=f"{record.relative_to(req_dir)} 中未出现 downstream/下游/影响",
                repair_hint="在变更记录中补充受影响的下游产物说明（如『下游 FD 需重新校验』）",
                source_ref="workflow.md §Reflow / 变更管理机制 §3.3",
                blocking=False,
            ))

    # 事件溯源审计链校验（借鉴点一）。
    # 空链（尚无 .audit/events.jsonl）= PASS（向后兼容老案例）；
    # 一旦有任何事件写入，则链完整性、payload hash、自指纹均必须成立。
    chain = audit_log.verify_chain(req_dir)
    if not chain.get("empty"):
        for ci in chain.get("issues", []):
            # Map audit_log severity/fields into the standard issue shape
            severity = ci.get("severity", "HIGH")
            check_tag = ci.get("check", "audit_chain")
            ev_idx = ci.get("event_index")
            location_suffix = f" (event #{ev_idx})" if ev_idx is not None else ""
            issues.append(make_issue(
                severity=severity, check_id=check_tag, family=FAMILY,
                location=".audit/events.jsonl",
                field_path=f"events.jsonl[{ev_idx}]" if ev_idx is not None else "events.jsonl",
                message=ci.get("message", "audit chain issue") + location_suffix,
                expected="事件日志必须保持 hash 链连续、event_sha256 自指纹一致、payload 未篡改、时间戳单调",
                actual=ci.get("message", "audit chain issue"),
                repair_hint="事件日志被篡改或损坏：恢复 .audit/events.jsonl 到受信任版本；任何人工修改都必须重建投影与后续事件",
                source_ref="constitution §7 事件溯源不可篡改 / contracts.md §AuditEvent",
            ))

    blocking = [issue for issue in issues
                if issue["severity"] in {"CRITICAL", "HIGH"} and issue.get("blocking", True)]
    return {"ok": not blocking, "issues": issues, "audit_chain": chain}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("req_dir", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--branch", help="Deprecated and ignored")
    args = parser.parse_args()
    if not args.req_dir.is_dir():
        print(f"ERROR: {args.req_dir} is not a directory", file=sys.stderr)
        return 1
    result = validate_records(args.req_dir)
    if args.as_json:
        from validation_errors import aggregate_by_check_id
        result = dict(result)
        result["aggregate_by_check_id"] = aggregate_by_check_id([result["issues"]])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        from validation_errors import format_issue
        print(f"Shared record validation: {'PASS' if result['ok'] else 'FAIL'}")
        for issue in result["issues"]:
            print(f"  [{issue['severity']}] {format_issue(issue)}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
