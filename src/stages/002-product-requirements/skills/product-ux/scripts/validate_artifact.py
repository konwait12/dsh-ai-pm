#!/usr/bin/env python3
"""Validate the structure of a product-ux Markdown artifact."""

from __future__ import annotations

import argparse, json, re, sys
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
    "artifact_id", "version", "status", "owner",
    "business_fact_owner", "goal_decision_owner", "reviewer",
    "created_at", "updated_at", "confirmed_at", "upstream_artifact_id",
}

REQUIRED_HEADINGS = [
    "预检输入充分度判定", "范围引用", "页面设计", "交互规则",
    "事实与决定", "假设、AI 推断、未知与冲突", "待确认问题",
    "来源追溯", "下游输入摘要", "Constitution Compliance", "版本变更摘要",
]

PENDING = ("待确认",)
VALID_STATUSES = {"draft", "needs_user_input", "conditional_review", "ready_for_human_review", "confirmed", "superseded", "legacy_unverified", "simulated"}


def _norm(h: str) -> str:
    # Strip leading numbering and trailing parenthetical suffixes like （Scope 层）.
    h = re.sub(r"^\d+\.\s*", "", h).strip()
    h = re.sub(r"\s*（[^）]*）\s*$", "", h).strip()
    return h


def parse_frontmatter(text: str) -> dict[str, str]:
    text = re.sub(r"^<!--.*?-->\s*", "", text, flags=re.DOTALL)
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    result: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        result[k.strip()] = v.strip().strip('"\'')
    return result


def validate(path: Path) -> dict[str, object]:
    errors, warnings = [], []
    if not path.is_file():
        return {"ok": False, "errors": [f"File not found: {path}"], "warnings": []}

    text = path.read_text(encoding="utf-8")
    meta = parse_frontmatter(text)
    status = meta.get("status")

    missing = sorted(REQUIRED_FRONTMATTER - meta.keys())
    if missing:
        errors.append(f"Missing frontmatter fields: {', '.join(missing)}")

    if status and status not in VALID_STATUSES:
        errors.append(f"Invalid status '{status}'")

    headings = [_norm(m.group(1)) for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)]
    missing_h = [h for h in REQUIRED_HEADINGS if _norm(h) not in headings]
    if missing_h:
        errors.append(f"Missing required headings: {', '.join(missing_h)}")

    if re.search(r"\b(?:BR|VL|AC)-\d+\b", text):
        errors.append("Business rules (BR/VL/AC) belong to function-description, not product-ux. IX interaction rules are OK here.")

    if status == "confirmed":
        unresolved = [k for k in ("business_fact_owner", "goal_decision_owner", "reviewer", "confirmed_at")
                      if meta.get(k, "") in {"", *PENDING}]
        if unresolved:
            errors.append("Confirmed artifact has unresolved confirmation fields: " + ", ".join(unresolved))

    if status in {"ready_for_human_review", "confirmed"}:
        upstream = meta.get("upstream_artifact_id", "")
        if not upstream or upstream in PENDING:
            errors.append("Missing upstream_artifact_id; product-ux requires confirmed user-journey-and-stories")

    if any(p in text for p in PENDING) and status == "confirmed":
        body = re.sub(r"^##\s+\d+\.\s*[^\n]*$", "", text, flags=re.MULTILINE)
        if any(p in body for p in PENDING):
            warnings.append("Confirmed artifact still contains 待确认 markers in body content")

    # Semantic red flags
    if status == "ready_for_human_review":
        # Flag 1: page skeleton coverage — every confirmed page should have a skeleton row.
        page_section = re.search(r"^##\s+\d+\.\s*页面设计\s*$(.*?)(?=^##\s+|\Z)", text, re.MULTILINE | re.DOTALL)
        if page_section:
            page_rows = re.findall(r"^\|", page_section.group(1), re.MULTILINE)
            if len(page_rows) <= 1:
                warnings.append("Semantic: status is ready_for_human_review but §页面设计 has no page/step skeleton rows")

        # Flag 2: interaction rule density (completeness guard).
        # A UX artifact with pages but no IX rules is incomplete.
        ix_count = len(re.findall(r"IX-\d+", text))
        if ix_count < 3:
            warnings.append(
                f"Semantic: only {ix_count} interaction rules (IX-*) found; "
                f"UX is under-specified — likely not covering upstream interaction rules"
            )

    # Clarifications check
    cl = re.search(r"^##\s+Clarifications\s*$(.*?)(?=^##\s+|\Z)", text, re.MULTILINE | re.DOTALL)
    if cl:
        rows = [l for l in cl.group(1).splitlines() if l.lstrip().startswith("|") and "---" not in l and "session_id" not in l and "待补充" not in l]
        if len(rows) > 5:
            warnings.append(f"Clarifications: {len(rows)} sessions exceeds 5-session cap")
        if status == "ready_for_human_review":
            unfilled = [i for i, l in enumerate(rows, 1) if "待补充" in l or "TBD" in l]
            if unfilled:
                warnings.append(f"Clarifications: session rows {unfilled} unfilled at ready_for_human_review")

    issues = [
        make_issue(
            severity="CRITICAL",
            check_id=_px_error_check_id(e),
            family="product_ux",
            location=str(path),
            message=e,
        )
        for e in errors
    ]
    issues.extend(
        make_issue(
            severity="MEDIUM",
            check_id=_px_warning_check_id(w),
            family="product_ux",
            location=str(path),
            message=w,
            blocking=False,
        )
        for w in warnings
    )
    return {"ok": not errors, "errors": errors, "warnings": warnings, "issues": issues}


_PX_ERROR_RULES = [
    ("Missing frontmatter fields:", "px.missing_frontmatter"),
    ("Invalid status", "px.invalid_status"),
    ("Missing required headings:", "px.missing_headings"),
    ("Business rules (BR/VL/AC) belong to function-description", "px.br_vl_ac_not_allowed"),
    ("Confirmed artifact has unresolved confirmation fields:", "px.unresolved_confirmation"),
    ("Missing upstream_artifact_id;", "px.missing_upstream"),
]

_PX_WARNING_RULES = [
    ("Confirmed artifact still contains 待确认 markers in body content", "px.pending_markers_in_confirmed"),
    ("no page/step skeleton rows", "px.no_page_skeleton"),
    ("interaction rules (IX-*) found", "px.ix_under_specified"),
    ("exceeds 5-session cap", "px.clarifications_over_cap"),
    ("session rows", "px.clarifications_unfilled"),
]


def _px_error_check_id(msg: str) -> str:
    for needle, check_id in _PX_ERROR_RULES:
        if needle in msg:
            return check_id
    return "px.structural"


def _px_warning_check_id(msg: str) -> str:
    for needle, check_id in _PX_WARNING_RULES:
        if needle in msg:
            return check_id
    return "px.semantic"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("artifact", type=Path)
    p.add_argument("--json", action="store_true", dest="j")
    a = p.parse_args()
    r = validate(a.artifact)
    if a.j:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print("PASS" if r["ok"] else "FAIL")
        for e in r["errors"]:
            print(f"ERROR: {e}")
        for w in r["warnings"]:
            print(f"WARNING: {w}")
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
