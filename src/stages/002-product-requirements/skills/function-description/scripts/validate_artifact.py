#!/usr/bin/env python3
"""Validate the structure of a function-description Markdown artifact."""

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
    "预检输入充分度判定", "功能清单", "功能流程", "业务规则",
    "校验规则与字段定义", "状态变化", "异常与失败处理", "验收依据",
    "事实与决定", "假设、AI 推断、未知与冲突", "待确认问题",
    "来源追溯", "下游输入摘要", "Constitution Compliance", "版本变更摘要",
]

PENDING = ("待确认",)
VALID_STATUSES = {"draft", "needs_user_input", "conditional_review", "ready_for_human_review", "confirmed", "superseded", "legacy_unverified", "simulated"}


def _norm(h: str) -> str:
    # Strip leading numbering and trailing parenthetical suffixes like （按需）.
    h = re.sub(r"^\d+\.\s*", "", h).strip()
    h = re.sub(r"\s*（[^）]*）\s*$", "", h).strip()
    return h


def _section_text(text: str, name: str) -> str | None:
    """Return the block under the `## N. name` heading (up to the next ## heading)."""
    headings = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    for i, m in enumerate(headings):
        if _norm(m.group(1)) == _norm(name):
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            return text[m.start():end]
    return None


def _count_p0_functions(text: str) -> int:
    """Count unique P0 functions from the 功能清单 table's priority column.

    Table shape: `| FEA-XXX | 功能名 | 描述 | 所属故事 | 优先级 | 知识状态 |`
    (priority = 5th column, P0/P1/P2). Counting here avoids the old bug where
    `FUN-(\\d+)[^\\n]*P0` also matched 验收依据 (AC) rows that carry
    `FUN-XXX ... P0` on the same line, inflating the P0 function count.
    """
    section = _section_text(text, "功能清单")
    if section is None:
        return 0
    p0_ids: set[str] = set()
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        m = re.match(r"(?:FEA|FUN)-\d+", cells[0])
        if m and cells[4] == "P0":
            p0_ids.add(m.group(0))
    return len(p0_ids)


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

    if "FEA-" not in text:
        errors.append("No FEA-* feature identifier found; at least one feature (功能清单) is required")

    if "FUN-" not in text:
        errors.append("No FUN-* function identifier found; at least one function is required")

    if "BR-" not in text:
        errors.append("No BR-* business rule identifier found; at least one business rule is required")

    if status == "confirmed":
        unresolved = [k for k in ("business_fact_owner", "goal_decision_owner", "reviewer", "confirmed_at")
                      if meta.get(k, "") in {"", *PENDING}]
        if unresolved:
            errors.append("Confirmed artifact has unresolved confirmation fields: " + ", ".join(unresolved))

    if status in {"ready_for_human_review", "confirmed"}:
        upstream = meta.get("upstream_artifact_id", "")
        if not upstream or upstream in PENDING:
            errors.append("Missing upstream_artifact_id; function-description requires confirmed product-ux")

    if any(p in text for p in PENDING) and status == "confirmed":
        body = re.sub(r"^##\s+\d+\.\s*[^\n]*$", "", text, flags=re.MULTILINE)
        if any(p in body for p in PENDING):
            warnings.append("Confirmed artifact still contains 待确认 markers in body")

    # Semantic red flags
    if status == "ready_for_human_review":
        # Flag 1: fun_count vs br_count
        # Count UNIQUE ids, not raw occurrences: a function referenced in the
        # 功能清单/流程/BR/VL/AC tables appears many times, so `len(re.findall)`
        # over-counts and produces misleading "41 functions" style warnings.
        fun_count = len(set(re.findall(r"FUN-\d+", text)))
        br_count = len(set(re.findall(r"BR-\d+", text)))
        ac_count = len(set(re.findall(r"AC-\d+", text)))
        vl_count = len(set(re.findall(r"VL-\d+", text)))
        if fun_count >= 1 and br_count == 0:
            warnings.append(f"Semantic: {fun_count} functions defined but no business rules (BR-*); functions are underspecified")
        if fun_count >= 1 and ac_count == 0:
            warnings.append(f"Semantic: {fun_count} functions defined but no acceptance criteria (AC-*); functions are unverifiable")

        # Flag 1b: rule density per function (completeness guard).
        # Each detailed P0 function must carry enough rules to be implementable —
        # a thin spec (e.g. 1 BR) that merely names a function without covering
        # upstream business rules fails this check. Threshold: ≥ 3 rules per FUN.
        rule_total = br_count + vl_count + ac_count
        if fun_count >= 1 and rule_total / fun_count < 3:
            warnings.append(
                f"Semantic: {fun_count} functions with only {rule_total} rules "
                f"({br_count} BR + {vl_count} VL + {ac_count} AC, avg {rule_total/fun_count:.1f}/FUN); "
                f"functions are under-specified — likely not fully covering upstream business rules"
            )

        # Flag 2: P0 features must have exception handling
        # P0 count comes from the 功能清单 table's priority column (NOT from AC
        # rows where `FUN-XXX ... P0` also appears on the same line); exception
        # coverage = number of EX-XXX rows (NOT the 异常与失败处理 section-title count).
        p0_count = _count_p0_functions(text)
        exc_count = len(set(re.findall(r"EX-\d+", text)))
        if p0_count >= 2 and exc_count < p0_count:
            warnings.append(f"Semantic: {p0_count} P0 functions but only {exc_count} exception handling sections; verify completeness")

        # Flag 3: 功能/UX 分离——交互规则 IX 归 product-ux/interaction-rules，不应出现在 function-description。
        ix_count = len(re.findall(r"IX-\d+", text))
        if ix_count > 0:
            warnings.append(f"Semantic: {ix_count} interaction rules (IX-*) found; IX belongs to product-ux/interaction-rules, not function-description")

        # Flag 4 (D4.4): AC-XXX must use Given/When/Then format
        # 检测两种写法：1) 表格行 `| AC-XXX | ... |`；2) 段落内 `**AC-XXX**`
        ac_in_text = re.findall(r"\*\*AC-\d+\*\*", text)
        if ac_in_text:
            for ac_match in re.findall(r"\*\*AC-(\d+)\*\*[：:]\s*([^\n]+)", text):
                ac_text = ac_match[1].lower()
                if re.search(r"given.*when.*then|前提.*当.*那么|条件.*动作.*结果", ac_text, re.IGNORECASE | re.DOTALL):
                    pass
                else:
                    errors.append(f"Semantic (D4.4): AC-{ac_match[0]} lacks Given/When/Then format; ISO 29148 requires 二值可测 AC")
                    break  # 一次性报一个，避免堆叠

    # Clarifications
    cl = re.search(r"^##\s+Clarifications\s*$(.*?)(?=^##\s+|\Z)", text, re.MULTILINE | re.DOTALL)
    if cl:
        rows = [l for l in cl.group(1).splitlines() if l.lstrip().startswith("|") and "---" not in l and "session_id" not in l and "待补充" not in l]
        if len(rows) > 5:
            warnings.append(f"Clarifications: {len(rows)} sessions exceeds 5-session cap")
        if status == "ready_for_human_review":
            unfilled = [i for i, l in enumerate(rows, 1) if "待补充" in l or "TBD" in l]
            if unfilled:
                warnings.append(f"Clarifications: session rows {unfilled} unfilled")

    issues = [
        make_issue(
            severity="CRITICAL",
            check_id=_fd_error_check_id(e),
            family="function_description",
            location=str(path),
            message=e,
        )
        for e in errors
    ]
    issues.extend(
        make_issue(
            severity="MEDIUM",
            check_id=_fd_warning_check_id(w),
            family="function_description",
            location=str(path),
            message=w,
            blocking=False,
        )
        for w in warnings
    )
    return {"ok": not errors, "errors": errors, "warnings": warnings, "issues": issues}


_FD_ERROR_RULES = [
    ("Missing frontmatter fields:", "fd.missing_frontmatter"),
    ("Invalid status", "fd.invalid_status"),
    ("Missing required headings:", "fd.missing_headings"),
    ("No FEA-* feature identifier found", "fd.missing_features"),
    ("No FUN-* function identifier found", "fd.missing_functions"),
    ("No BR-* business rule identifier found", "fd.missing_business_rules"),
    ("Confirmed artifact has unresolved confirmation fields:", "fd.unresolved_confirmation"),
    ("Missing upstream_artifact_id;", "fd.missing_upstream"),
    ("Semantic (D4.4): AC-", "fd.d44_no_gwt"),
]

_FD_WARNING_RULES = [
    ("Confirmed artifact still contains 待确认 markers in body", "fd.pending_markers_in_confirmed"),
    ("no business rules (BR-*)", "fd.functions_without_business_rules"),
    ("no acceptance criteria (AC-*)", "fd.functions_without_acceptance_criteria"),
    ("functions with only", "fd.low_rule_density"),
    ("P0 functions but only", "fd.p0_missing_exception_handling"),
    ("interaction rules (IX-*) found", "fd.ix_belongs_to_ux"),
    ("exceeds 5-session cap", "fd.clarifications_over_cap"),
    ("session rows", "fd.clarifications_unfilled"),
]


def _fd_error_check_id(msg: str) -> str:
    for needle, check_id in _FD_ERROR_RULES:
        if needle in msg:
            return check_id
    return "fd.structural"


def _fd_warning_check_id(msg: str) -> str:
    for needle, check_id in _FD_WARNING_RULES:
        if needle in msg:
            return check_id
    return "fd.semantic"


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
