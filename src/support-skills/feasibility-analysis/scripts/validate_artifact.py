#!/usr/bin/env python3
"""Validate a feasibility-analysis output (feasibility report or solution comparison)."""

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


FEASIBILITY_HEADINGS = ["市场空间", "技术可行性", "投入产出", "风险评估", "结论"]
COMPARISON_HEADINGS = ["候选方案", "方案对比矩阵", "AI 推荐", "人工决策"]
PENDING = ("待确认",)
SOURCE_SECTIONS = ["投入产出", "风险评估", "候选方案", "方案对比矩阵", "AI 推荐"]
SRC_ID_RE = re.compile(r"SRC-\d+")
KNOWLEDGE_STATE_RE = re.compile(r"\b(?:FACT|DECISION|AI_INFERENCE|UNKNOWN)\b")


def _norm(h: str) -> str:
    h = re.sub(r"^\d+\.\s*", "", h).strip()
    h = re.sub(r"^[一二三四五六七八九十]+、\s*", "", h).strip()
    return h


def validate(path: Path) -> dict:
    errors, warnings = [], []
    if not path.is_file():
        return {"ok": False, "errors": [f"File not found: {path}"], "warnings": []}
    text = path.read_text(encoding="utf-8")
    headings = [_norm(m.group(1)) for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)]
    targets = FEASIBILITY_HEADINGS if "可行性" in text else COMPARISON_HEADINGS
    for h in targets:
        if _norm(h) not in headings:
            errors.append(f"Missing required heading: {h}")
    if not re.search(r"做|不做|有条件做|推荐方案", text):
        warnings.append("No clear recommendation found; assessment should conclude with 做/不做/有条件做")
    if any(p in text for p in PENDING):
        warnings.append("Assessment still has 待确认 placeholders")
    # Source Fidelity (SKILL.md Audit): cost/risk/solution content must cite
    # an SRC-ID or carry an explicit knowledge-state label.
    if any(h in headings for h in SOURCE_SECTIONS) \
            and not SRC_ID_RE.search(text) and not KNOWLEDGE_STATE_RE.search(text):
        warnings.append(
            "No SRC-ID or knowledge-state label (FACT/DECISION/AI_INFERENCE/UNKNOWN) "
            "found: cost/risk figures must be traceable (Source Fidelity)"
        )
    issues = [
        make_issue(
            severity="CRITICAL",
            check_id=_fa_error_check_id(e),
            family="feasibility_analysis",
            location=str(path),
            message=e,
        )
        for e in errors
    ]
    issues.extend(
        make_issue(
            severity="MEDIUM",
            check_id=_fa_warning_check_id(w),
            family="feasibility_analysis",
            location=str(path),
            message=w,
            blocking=False,
        )
        for w in warnings
    )
    return {"ok": not errors, "errors": errors, "warnings": warnings, "issues": issues}


_FA_ERROR_RULES = [
    ("Missing required heading:", "fa.missing_heading"),
]

_FA_WARNING_RULES = [
    ("No clear recommendation found", "fa.no_clear_recommendation"),
    ("Assessment still has 待确认 placeholders", "fa.pending_placeholders"),
    ("No SRC-ID or knowledge-state label", "fa.missing_src_fidelity"),
]


def _fa_error_check_id(msg: str) -> str:
    for needle, check_id in _FA_ERROR_RULES:
        if needle in msg:
            return check_id
    return "fa.structural"


def _fa_warning_check_id(msg: str) -> str:
    for needle, check_id in _FA_WARNING_RULES:
        if needle in msg:
            return check_id
    return "fa.semantic"


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
