"""
Validate the stable structure of an issue-record Markdown artifact
(cross-stage shared issue list under shared/clarify/skills/issue-record/).

The artifact is always Chinese because the deliverable is consumed by
business stakeholders. Section headings match REQUIRED_HEADINGS exactly.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── 统一错误格式引导（借鉴点四: make_issue 契约）───────────
def _bootstrap_scripts() -> None:
    import sys as _sys
    p = Path(__file__).resolve().parent
    while p.parent != p:
        cand = p / "src" / "scripts"
        if (cand / "validation_errors.py").is_file():
            if str(cand) not in _sys.path:
                _sys.path.insert(0, str(cand))
            return
        p = p.parent

_bootstrap_scripts()
from validation_errors import make_issue
# ─────────────────────────────────────────────────────────

SKILL_ID = "issue_record"         # issue family（统一错误格式分组）
CHECK_PREFIX = "ir"               # issue check_id 语义化前缀


REQUIRED_FRONTMATTER = {
    "artifact_id",
    "version",
    "status",
    "owner",
    "goal_decision_owner",
    "business_sponsor",
    "reviewer",
    "created_at",
    "updated_at",
    "confirmed_at",
}

REQUIRED_HEADINGS = [
    "项目元数据",
    "总览",
    "Blocker（BLK）",
    "Risk（RSK）",
    "Decision-in-waiting（DEC）",
    "Information gap（INF）",
    "Clarification（CLS）",
    "Out-of-band（OUT）",
    "Closed Issues",
    "来源追溯",
    "待确认问题",
    "Constitution Compliance",
    "版本变更摘要",
]

PENDING_PLACEHOLDERS = ("待确认",)

VALID_STATUSES = {
    "draft",
    "needs_user_input",
    "conditional_review",
    "ready_for_human_review",
    "confirmed",
    "superseded",
}

VALID_CATEGORIES = {"BLK", "RSK", "DEC", "INF", "CLS", "OUT"}
VALID_STATES = {"open", "in_progress", "blocked", "accepted", "resolved", "escalated"}


def _normalize_heading(heading: str) -> str:
    return re.sub(r"\s*（[^）]*）\s*$", "", re.sub(r"^\d+\.\s*", "", heading).strip()).strip()


def parse_frontmatter(text: str) -> dict[str, str]:
    # Allow leading content (H1, blockquote, comments) before the YAML block.
    text = re.sub(r"^<!--.*?-->\s*", "", text, flags=re.DOTALL)
    match = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.MULTILINE | re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def _extract_section(text: str, heading_pattern: str) -> str:
    match = re.search(heading_pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def _collect_issues(body: str, id_prefix: str) -> list[dict[str, str]]:
    """Parse data rows from a section table.

    Returns one dict per non-header row that contains the expected ID prefix.
    """
    rows: list[dict[str, str]] = []
    for line in body.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        if id_prefix not in line:
            continue
        if set(line.strip()) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        rows.append({"raw": line, "cells": cells})
    return rows


def _make_issues(errors: list[str], warnings: list[str], path: Path) -> list[dict]:
    """双轨制: errors/warnings 保持字符串列表, issues 为 make_issue 标准 dict."""
    issues: list[dict] = []
    for e in errors:
        if e.startswith("File not found"):
            cid, sev, exp, act, fix = (
                f"{CHECK_PREFIX}.file_not_found", "CRITICAL",
                "产物文件必须存在且可读", f"文件不存在: {e}",
                "确认产物路径正确, 或先创建对应的 issue-record 文件",
            )
        elif e.startswith("Missing frontmatter fields"):
            cid, sev, exp, act, fix = (
                f"{CHECK_PREFIX}.missing_frontmatter", "CRITICAL",
                "frontmatter 必须包含全部必填字段", f"缺失字段: {e}",
                "按模板补齐 frontmatter 中缺失的字段",
            )
        elif e.startswith("Invalid status"):
            cid, sev, exp, act, fix = (
                f"{CHECK_PREFIX}.status_invalid", "CRITICAL",
                "frontmatter status 必须在合法状态集合内", f"非法状态: {e}",
                "修正 frontmatter 的 status 字段为合法取值",
            )
        elif e.startswith("Missing required headings"):
            cid, sev, exp, act, fix = (
                f"{CHECK_PREFIX}.missing_headings", "CRITICAL",
                "产物必须包含全部必填章节（## 标题）", f"缺失章节: {e}",
                "按模板补齐缺失的章节标题",
            )
        elif e.startswith("No SRC-*"):
            cid, sev, exp, act, fix = (
                f"{CHECK_PREFIX}.missing_src", "CRITICAL",
                "产物必须包含至少一个 SRC-* 来源追溯标识符", f"未找到: {e}",
                "在来源追溯章节补充 SRC-* 标识符",
            )
        elif e.startswith("Confirmed artifact has unresolved confirmation fields"):
            cid, sev, exp, act, fix = (
                f"{CHECK_PREFIX}.confirmed_unresolved", "CRITICAL",
                "confirmed 状态的产物不得存在未确认字段", f"未确认字段: {e}",
                "补齐 goal_decision_owner / business_sponsor / reviewer / confirmed_at",
            )
        else:
            cid, sev, exp, act, fix = f"{CHECK_PREFIX}.error", "CRITICAL", None, None, None
        issues.append(make_issue(
            severity=sev, check_id=cid, family=SKILL_ID,
            location=str(path), message=e,
            expected=exp, actual=act, repair_hint=fix,
        ))
    for w in warnings:
        if "has pending owner" in w:
            cid, exp, act, fix = (
                f"{CHECK_PREFIX}.pending_owner",
                "issue 的 owner 不应为待确认占位符",
                f"owner 为待确认: {w}",
                "为 issue 指定具体负责人, 或将状态调整为 needs_user_input",
            )
        elif "missing target_close date" in w:
            cid, exp, act, fix = (
                f"{CHECK_PREFIX}.missing_target_close",
                "BLK / DEC issue 应填写 target_close 日期",
                f"缺少 target_close: {w}",
                "为 issue 补充 target_close 日期",
            )
        elif "section is empty or fully placeholder" in w:
            cid, exp, act, fix = (
                f"{CHECK_PREFIX}.section_empty_at_review",
                "ready_for_human_review 状态下 BLK/DEC/RSK 章节应为空或有实质内容",
                f"章节为空或全占位符: {w}",
                "确认该分类确实无内容, 或补充实质 issue 条目",
            )
        else:
            cid, exp, act, fix = f"{CHECK_PREFIX}.warning", None, None, None
        issues.append(make_issue(
            severity="MEDIUM", check_id=cid, family=SKILL_ID,
            location=str(path), message=w,
            expected=exp, actual=act, repair_hint=fix, blocking=False,
        ))
    return issues


def validate(path: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_file():
        return {"ok": False, "errors": [f"File not found: {path}"], "warnings": [],
                "issues": _make_issues([f"File not found: {path}"], [], path)}

    text = path.read_text(encoding="utf-8")
    metadata = parse_frontmatter(text)

    missing_metadata = sorted(REQUIRED_FRONTMATTER - metadata.keys())
    if missing_metadata:
        errors.append(f"Missing frontmatter fields: {', '.join(missing_metadata)}")

    status = metadata.get("status")
    if status and status not in VALID_STATUSES:
        errors.append(
            f"Invalid status '{status}'. Valid: {', '.join(sorted(VALID_STATUSES))}"
        )

    artifact_headings = [
        _normalize_heading(match.group(1))
        for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)
    ]

    missing_headings = [
        h for h in REQUIRED_HEADINGS
        if _normalize_heading(h) not in artifact_headings
    ]
    if missing_headings:
        errors.append(f"Missing required headings: {', '.join(missing_headings)}")

    if "SRC-" not in text:
        errors.append("No SRC-* source traceability identifier found")

    # Section-level issue audits
    section_specs = [
        (r"^##\s+\d+\.\s*Blocker.*?$(.*?)(?=^##\s+|\Z)", "BLK", "ISS-0"),
        (r"^##\s+\d+\.\s*Risk.*?$(.*?)(?=^##\s+|\Z)", "RSK", "ISS-1"),
        (r"^##\s+\d+\.\s*Decision-in-waiting.*?$(.*?)(?=^##\s+|\Z)", "DEC", "ISS-2"),
        (r"^##\s+\d+\.\s*Information gap.*?$(.*?)(?=^##\s+|\Z)", "INF", "ISS-3"),
        (r"^##\s+\d+\.\s*Clarification.*?$(.*?)(?=^##\s+|\Z)", "CLS", "ISS-4"),
        (r"^##\s+\d+\.\s*Out-of-band.*?$(.*?)(?=^##\s+|\Z)", "OUT", "ISS-5"),
    ]
    for pattern, label, id_prefix in section_specs:
        body = _extract_section(text, pattern)
        issues = _collect_issues(body, id_prefix)
        for issue in issues:
            cells = issue["cells"]
            if len(cells) >= 5:
                owner = cells[4]
                if any(p in owner for p in PENDING_PLACEHOLDERS):
                    warnings.append(
                        f"Advisory: {label} issue {cells[0]} has pending owner '{owner}'"
                    )
            if label in {"BLK", "DEC"}:
                if len(cells) >= 8:
                    target = cells[7]
                    if any(p in target for p in PENDING_PLACEHOLDERS):
                        warnings.append(
                            f"Advisory: {label} issue {cells[0]} missing target_close date"
                        )

    if status == "ready_for_human_review":
        for pattern, label, id_prefix in section_specs:
            if label not in {"BLK", "DEC", "RSK"}:
                continue
            body = _extract_section(text, pattern)
            issues = _collect_issues(body, id_prefix)
            concrete = [
                i for i in issues
                if not any(p in i["raw"] for p in PENDING_PLACEHOLDERS)
            ]
            if not concrete:
                warnings.append(
                    f"Advisory: {label} section is empty or fully placeholder at "
                    f"ready_for_human_review. Confirm that this category is genuinely empty."
                )

    if status == "confirmed":
        unresolved = [
            k for k in ("goal_decision_owner", "business_sponsor", "reviewer", "confirmed_at")
            if metadata.get(k, "") in {"", *PENDING_PLACEHOLDERS}
        ]
        if unresolved:
            errors.append(
                "Confirmed artifact has unresolved confirmation fields: "
                + ", ".join(unresolved)
            )

    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "issues": _make_issues(errors, warnings, path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    result = validate(args.artifact)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if result["ok"] else "FAIL")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
