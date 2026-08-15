"""
Validate the stable structure of a requirement-restate Markdown artifact.

The artifact is the "shared understanding" checkpoint, NOT a PRD deliverable.
Its outputs feed into issue-record (CONFLICT → ISS, UNKNOWN → Q).

Section headings match REQUIRED_HEADINGS exactly.
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
    "stakeholder",
    "stakeholder_delegate",
    "reviewer",
    "created_at",
    "updated_at",
    "confirmed_at",
}

REQUIRED_HEADINGS = [
    "项目元数据",
    "来源清单",
    "重述需求清单",
    "冲突清单",
    "未知清单",
    "stakeholder 自查反馈位",
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


def _normalize_heading(heading: str) -> str:
    return re.sub(r"\s*（[^）]*）\s*$", "", re.sub(r"^\d+\.\s*", "", heading).strip()).strip()


def parse_frontmatter(text: str) -> dict[str, str]:
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


def _collect_rows(body: str, id_prefix: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in body.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        if id_prefix not in line:
            continue
        if set(line.strip()) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    return rows


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
        h for h in REQUIRED_HEADINGS
        if _normalize_heading(h) not in artifact_headings
    ]
    if missing_headings:
        errors.append(f"Missing required headings: {', '.join(missing_headings)}")

    if "SRC-" not in text:
        errors.append("No SRC-* source traceability identifier found")

    # RR-NNN rows must have non-placeholder restated + original_phrase
    body = _extract_section(
        text, r"^##\s+\d+\.\s*重述需求清单.*?$(.*?)(?=^##\s+|\Z)"
    )
    rr_rows = _collect_rows(body, "RR-")
    if status == "ready_for_human_review" and not rr_rows:
        warnings.append(
            "Advisory: 重述需求清单 is empty at ready_for_human_review. "
            "Confirm the ask is genuinely empty."
        )
    for cells in rr_rows:
        # columns: ID | restated | original_phrase | source | ks | stakeholder | confidence | solution_leak
        if len(cells) >= 3:
            if any(p in cells[1] for p in PENDING_PLACEHOLDERS) or any(
                p in cells[2] for p in PENDING_PLACEHOLDERS
            ):
                warnings.append(
                    f"Advisory: {cells[0]} has placeholder restated or original_phrase"
                )

    # Conflict list rows must have at least 2 source references
    body = _extract_section(text, r"^##\s+\d+\.\s*冲突清单.*?$(.*?)(?=^##\s+|\Z)")
    for cells in _collect_rows(body, "CON-"):
        if len(cells) >= 4:
            if any(p in cells[1] for p in PENDING_PLACEHOLDERS):
                warnings.append(
                    f"Advisory: {cells[0]} conflict description still placeholder"
                )

    # Optional SCN-XXX divergence-mode candidate table check（模式二 发散收敛）.
    # Runs only when SCN- rows are present; an RR-only artifact is unaffected.
    scn_body = _extract_section(
        text, r"^##\s+\d+\.\s*发散收敛候选清单.*?$(.*?)(?=^##\s+|\Z)"
    )
    scn_rows = _collect_rows(scn_body, "SCN-") or _collect_rows(text, "SCN-")
    for cells in scn_rows:
        # columns: ID | 发散维度 | Candidate | Evidence | Impact | 知识状态
        if len(cells) >= 5:
            scn_placeholders = ("待确认", "待填写", "待补充", "TBD")
            if any(p in cells[3] for p in scn_placeholders) or any(
                p in cells[4] for p in scn_placeholders
            ):
                warnings.append(
                    f"Advisory: {cells[0]} divergence candidate has placeholder "
                    f"Evidence or Impact"
                )

    if status == "confirmed":
        unresolved = [
            k for k in ("stakeholder", "reviewer", "confirmed_at")
            if metadata.get(k, "") in {"", *PENDING_PLACEHOLDERS}
        ]
        if unresolved:
            errors.append(
                "Confirmed artifact has unresolved confirmation fields: "
                + ", ".join(unresolved)
            )

    issues = [
        make_issue(
            severity="CRITICAL",
            check_id=_rr_error_check_id(e),
            family="requirement_restate",
            location=str(path),
            message=e,
        )
        for e in errors
    ]
    issues.extend(
        make_issue(
            severity="MEDIUM",
            check_id=_rr_warning_check_id(w),
            family="requirement_restate",
            location=str(path),
            message=w,
            blocking=False,
        )
        for w in warnings
    )
    return {"ok": not errors, "errors": errors, "warnings": warnings, "issues": issues}


_RR_ERROR_RULES = [
    ("Missing frontmatter fields:", "rr.missing_frontmatter"),
    ("Invalid status", "rr.invalid_status"),
    ("Missing required headings:", "rr.missing_headings"),
    ("No SRC-* source traceability identifier found", "rr.missing_src_traceability"),
    ("Confirmed artifact has unresolved confirmation fields:", "rr.unresolved_confirmation"),
]

_RR_WARNING_RULES = [
    ("重述需求清单 is empty at ready_for_human_review", "rr.empty_restate_list_at_review"),
    ("has placeholder restated or original_phrase", "rr.placeholder_restated"),
    ("conflict description still placeholder", "rr.placeholder_conflict"),
    ("divergence candidate has placeholder Evidence or Impact", "rr.placeholder_divergence_candidate"),
]


def _rr_error_check_id(msg: str) -> str:
    for needle, check_id in _RR_ERROR_RULES:
        if needle in msg:
            return check_id
    return "rr.structural"


def _rr_warning_check_id(msg: str) -> str:
    for needle, check_id in _RR_WARNING_RULES:
        if needle in msg:
            return check_id
    return "rr.semantic"


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
