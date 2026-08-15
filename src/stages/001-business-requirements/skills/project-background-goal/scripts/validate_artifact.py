#!/usr/bin/env python3
"""Validate the stable structure of a project-background-goal Markdown artifact.

The artifact itself (and therefore its section headings) is always Chinese
because the deliverable is a Chinese report consumed by business stakeholders.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


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


REQUIRED_FRONTMATTER = {
    "artifact_id",
    "version",
    "status",
    "owner",
    "business_fact_owner",
    "goal_decision_owner",
    "reviewer",
    "created_at",
    "updated_at",
    "confirmed_at",
}

# Chinese-only section headings. The artifact is a Chinese report; the
# validator matches exactly these strings.
REQUIRED_HEADINGS = [
    "预检输入充分度判定",
    "需求来源与触发",
    "项目与需求背景",
    "当前现状与已有做法",
    "核心问题与证据",
    "目标、未来期望与成功判断",
    "用户角色与利益相关者",
    "时间、约束与依赖",
    "初步边界与非目标",
    "事实与决定",
    "假设、AI 推断、未知与冲突",
    "待确认问题",
    "来源追溯",
    "下游输入摘要",
    "Constitution Compliance",
    "版本变更摘要",
]

# The Chinese phrase 待确认 is the canonical placeholder.
PENDING_PLACEHOLDERS = ("待确认",)

VALID_STATUSES = {
    "draft",
    "needs_user_input",
    "conditional_review",
    "ready_for_human_review",
    "confirmed",
    "superseded", "legacy_unverified",
    "simulated", "legacy_unverified",
}


def _normalize_heading(heading: str) -> str:
    """Strip leading numbering like '1. ' and trailing （…） suffixes."""
    return re.sub(r"\s*（[^）]*）\s*$", "", re.sub(r"^\d+\.\s*", "", heading).strip()).strip()


def parse_frontmatter(text: str) -> dict[str, str]:
    # Allow optional leading HTML comment block(s) before the YAML frontmatter
    # (the template and example artifacts ship with a comment header).
    text = re.sub(r"^<!--.*?-->\s*", "", text, flags=re.DOTALL)
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def validate(path: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_file():
        return {"ok": False, "errors": [f"File not found: {path}"], "warnings": []}

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
        heading for heading in REQUIRED_HEADINGS
        if _normalize_heading(heading) not in artifact_headings
    ]
    if missing_headings:
        errors.append(f"Missing required headings: {', '.join(missing_headings)}")

    if "SRC-" not in text:
        errors.append("No SRC-* source traceability identifier found")

    if status == "confirmed":
        unresolved_owners = [
            key
            for key in ("business_fact_owner", "goal_decision_owner", "reviewer", "confirmed_at")
            if metadata.get(key, "") in {"", *PENDING_PLACEHOLDERS}
        ]
        if unresolved_owners:
            errors.append(
                "Confirmed artifact has unresolved confirmation fields: "
                + ", ".join(unresolved_owners)
            )

    if any(p in text for p in PENDING_PLACEHOLDERS) and status == "confirmed":
        # Strip mandatory template headings (e.g. "## 11. 待确认问题") before
        # scanning, otherwise the required section title itself always triggers
        # this warning. Only body content counts as a pending marker.
        body_without_headings = re.sub(
            r"^##\s+\d+\.\s*[^\n]*$", "", text, flags=re.MULTILINE
        )
        if any(p in body_without_headings for p in PENDING_PLACEHOLDERS):
            warnings.append(
                "Confirmed artifact still contains 待确认 markers in body content; "
                "verify these are accepted non-blocking items"
            )

    if len(text.strip()) < 800:
        warnings.append(
            "Artifact is unusually short; verify that source coverage is sufficient"
        )

    sem_errors, sem_warnings = check_semantic_red_flags(text, metadata)
    errors.extend(sem_errors)
    warnings.extend(sem_warnings)

    issues = [
        make_issue(
            severity="CRITICAL",
            check_id=_bg_error_check_id(e),
            family="project_background_goal",
            location=str(path),
            message=e,
        )
        for e in errors
    ]
    for w in warnings:
        severity = "MEDIUM"
        if "ready_for_human_review" in w and ("空" in w or "empty" in w.lower()):
            severity = "HIGH"
        elif "待确认" in w and "UNKNOWN" in w:
            severity = "HIGH"
        issues.append(make_issue(
            severity=severity,
            check_id=_bg_warning_check_id(w),
            family="project_background_goal",
            location=str(path),
            message=w,
            blocking=False,
        ))
    return {"ok": not errors, "errors": errors, "warnings": warnings, "issues": issues}


_BG_ERROR_RULES = [
    ("Missing frontmatter fields:", "bg.missing_frontmatter"),
    ("Invalid status", "bg.invalid_status"),
    ("Missing required headings:", "bg.missing_headings"),
    ("No SRC-* source traceability identifier found", "bg.missing_src_traceability"),
    ("Confirmed artifact has unresolved confirmation fields:", "bg.unresolved_confirmation"),
    ("目标、未来期望与成功判断 section is empty", "bg.empty_goal_at_review"),
]

_BG_WARNING_RULES = [
    ("Confirmed artifact still contains 待确认 markers in body content", "bg.pending_markers_in_confirmed"),
    ("Artifact is unusually short", "bg.artifact_too_short"),
    ("implementation vocabulary", "bg.solution_as_fact"),
    ("markers found but status is", "bg.status_mismatch_pending_markers"),
    ("exceeds the 5-session cap", "bg.clarifications_over_cap"),
    ("session row(s)", "bg.clarifications_unfilled"),
    ("no numeric fit criterion", "bg.no_numeric_fit_criterion"),
]


def _bg_error_check_id(msg: str) -> str:
    for needle, check_id in _BG_ERROR_RULES:
        if needle in msg:
            return check_id
    return "bg.structural"


def _bg_warning_check_id(msg: str) -> str:
    for needle, check_id in _BG_WARNING_RULES:
        if needle in msg:
            return check_id
    return "bg.semantic"


def check_semantic_red_flags(text: str, metadata: dict[str, str]) -> tuple[list[str], list[str]]:
    """Semantic checks that catch common AI mistakes the structural validator misses.

    Blocking errors (must fix): goal-less baseline shipped for review.
    Soft warnings (document in audit notes): everything else.
    """
    errors: list[str] = []
    warnings: list[str] = []
    status = metadata.get("status")

    # Flag 1: ready_for_human_review status but the goal section is empty.
    goal_match = re.search(
        r"^##\s+\d+\.\s*目标、未来期望与成功判断\s*$(.*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if goal_match and status == "ready_for_human_review":
        goal_section = goal_match.group(1).strip()
        cleaned = re.sub(r"待确认|UNKNOWN|TBD", "", goal_section).strip()
        if len(cleaned) < 20:
            errors.append(
                "Semantic: status is ready_for_human_review but 目标、未来期望与成功判断 section is empty; "
                "AI cannot ship a goal-less baseline"
            )

    # Flag 2: implementation vocabulary with FACT entries but too few SRC citations.
    fact_count = len(re.findall(r"\bFACT\b|FCT-\d+", text))
    implementation_words = ["按钮", "表单", "接口", "字段", "数据库", "API"]
    src_count = len(re.findall(r"SRC-\d+", text))
    if fact_count >= 1 and src_count < 2 and any(word in text for word in implementation_words):
        warnings.append(
            "Semantic: implementation vocabulary (按钮/表单/接口/字段/数据库/API) appears with "
            "FACT entries but fewer than 2 SRC citations; "
            "possible 'treating solution as fact' anti-pattern"
        )

    # Flag 3: many 待确认 markers but status does not reflect it.
    nc_count = len(re.findall(r"待确认|UNKNOWN", text))
    if nc_count >= 3 and status not in {"needs_user_input", "draft"}:
        warnings.append(
            f"Semantic: {nc_count} 待确认 / UNKNOWN markers found but status is "
            f"'{status}'; should be 'needs_user_input' or 'draft'"
        )

    # Flag 4: Clarifications Session consistency.
    # If the artifact declares ## Clarifications, check that:
    #   (a) every non-empty Session row has accepted_answer filled in
    #       before reaching ready_for_human_review,
    #   (b) the row count does not exceed 5 (per SKILL.md cap).
    check_clarifications(text, status, warnings)

    # Flag 5: ready_for_human_review but the goal section has no quantifiable
    # fit criterion (no digits / percent / currency / time units).
    # Per ISO/IEC/IEEE 29148 Verifiable + Volere Fit Criterion, a goal without
    # a measure is not complete. This is a soft warning, not an error, because
    # some legitimate goals cannot be quantified — human confirms at review.
    if status == "ready_for_human_review" and goal_match:
        goal_text = goal_match.group(1)
        has_number = re.search(
            r"[0-9０-９]|%|％|¥|元|万|天|日|周|月|季|年|pp", goal_text
        )
        if not has_number:
            warnings.append(
                "Semantic: status is ready_for_human_review but 目标、未来期望与成功判断 section "
                "has no numeric fit criterion (Volere Fit Criterion / ISO-IEEE 29148 Verifiable); "
                "confirm with the goal decision owner that this is intentional"
            )

    return errors, warnings


def check_clarifications(text: str, status: str | None, warnings: list[str]) -> None:
    clarifications_match = re.search(
        r"^##\s+Clarifications\s*$(.*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if clarifications_match:
        body = clarifications_match.group(1)
        # Count actual data rows (skip the markdown separator row "---" and
        # the placeholder row "待补充").
        session_rows = [
            line for line in body.splitlines()
            if line.lstrip().startswith("|")
            and "---" not in line
            and "session_id" not in line
            and "待补充" not in line
        ]
        if len(session_rows) > 5:
            warnings.append(
                f"Clarifications: {len(session_rows)} sessions found, exceeds the 5-session cap "
                f"(see SKILL.md § Clarify Is Its Own Loop); switch to needs_user_input"
            )
        if status == "ready_for_human_review":
            unfilled = [
                line_no for line_no, line in enumerate(session_rows, start=1)
                if "待补充" in line or "TBD" in line
            ]
            if unfilled:
                warnings.append(
                    f"Clarifications: status is ready_for_human_review but session row(s) "
                    f"{unfilled} still contain 待确认 / TBD; fill accepted_answer first"
                )


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
