#!/usr/bin/env python3
"""Validate the structure of a prd-assembly Markdown artifact (final PRD)."""

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

SKILL_ID = "prd_assembly"     # issue family（统一错误格式分组）
CHECK_PREFIX = "prd"          # issue check_id 语义化前缀

REQUIRED_FRONTMATTER = {
    "artifact_id", "version", "status", "owner",
    "business_fact_owner", "goal_decision_owner", "reviewer",
    "created_at", "updated_at", "confirmed_at",
}

REQUIRED_HEADINGS = [
    "项目背景与目标", "业务角色、用户旅程与用户故事",
    "UX：页面设计与交互规则", "分功能描述", "按需章节",
    "事实与决定", "验收依据", "需求追溯矩阵", "自审记录",
]

PENDING = ("待确认",)
VALID_STATUSES = {"draft", "needs_user_input", "conditional_review", "ready_for_human_review", "confirmed", "superseded", "legacy_unverified", "simulated"}


def _norm(h: str) -> str:
    return re.sub(r"\s*（[^）]*）\s*$", "", re.sub(r"^\d+\.\s*", "", h).strip()).strip()


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

    if "RTM" not in text and "需求追溯矩阵" not in text:
        errors.append("No RTM (Requirements Traceability Matrix) found")

    if status == "confirmed":
        unresolved = [k for k in ("business_fact_owner", "goal_decision_owner", "reviewer", "confirmed_at")
                      if meta.get(k, "") in {"", *PENDING}]
        if unresolved:
            errors.append("Confirmed artifact has unresolved confirmation fields: " + ", ".join(unresolved))

    if any(p in text for p in PENDING) and status == "confirmed":
        body = re.sub(r"^##\s+\d+\.\s*[^\n]*$", "", text, flags=re.MULTILINE)
        if any(p in body for p in PENDING):
            warnings.append("Confirmed PRD still contains 待确认 markers in body")

    # Semantic red flags specific to PRD assembly
    if status == "ready_for_human_review":
        # Note: 上游产物清单 / 不一致报告 已移出 PRD 正文（由机器在 gate 产出、进 99-review）。

        # Flag 1b (D5.2): PRD 必须引用 4 个上游产物（BG/JS/UX/FD），从 frontmatter upstream_artifact_ids 校验。
        # 上游产物 frontmatter 的 artifact_id 为单连字符格式（如 BG-001 / JS-001 / UX-001 / FD-001），
        # 因此这里匹配单连字符 ID；兼容历史遗留的双连字符格式（如 BG-001-1）以免误报。
        upstream_ids = re.findall(r"(BG|JS|UX|FD)-\d+(?:-\d+)?", meta.get("upstream_artifact_ids", ""))
        missing_prefixes = {"BG", "JS", "UX", "FD"} - set(upstream_ids)
        if missing_prefixes:
            errors.append(f"PRD DoD D5.2 failed: missing upstream artifact IDs for {sorted(missing_prefixes)} (need BG + JS + UX + FD all confirmed)")

        # Flag 3: traceability matrices should have content + six columns G→ST→FEA→FUN→AC→BR
        rtm_section = re.search(r"^##\s+\d+\.\s*需求追溯矩阵\s*$(.*?)(?=^##\s+|\Z)", text, re.MULTILINE | re.DOTALL)
        if rtm_section:
            rtm_rows = [l for l in rtm_section.group(1).splitlines() if l.lstrip().startswith("|") and "---" not in l and "目标" not in l]
            rtm_data = [r for r in rtm_rows if "待确认" not in r]
            if len(rtm_data) == 0:
                warnings.append("Semantic: RTM has no data rows; traceability matrix should be populated")
            # Flag 3b (G_CROSS): RTM should have 6 columns G→ST→FEA→FUN→AC→BR
            header_match = re.search(r"^\|\s*([^|]+\|){5,}\s*[^|]+\|\s*$", rtm_section.group(1), re.MULTILINE)
            if header_match:
                col_count = header_match.group(0).count("|") - 1
                if col_count < 6:
                    warnings.append(f"Semantic (G_CROSS): RTM header has {col_count} columns, expected ≥6 for G→ST→FEA→FUN→AC→BR chain")
            # Flag 3c: each data row should not have ⏸/空 placeholders in P0
            incomplete_p0 = 0
            for row in rtm_data:
                cells = [c.strip() for c in row.split("|") if c.strip()]
                if len(cells) >= 6:
                    empty_cells = sum(1 for c in cells if c in {"", "⏸", "-"})
                    if empty_cells >= 3:
                        incomplete_p0 += 1
            if incomplete_p0 > 0:
                warnings.append(f"Semantic: {incomplete_p0} RTM rows have ≥3 empty/⏸ cells; P0 chain must be complete per G_CROSS")

        # Flag 4: check for new content not in upstream
        new_content_markers = ["新增需求", "补充功能", "额外建议"]
        if any(m in text for m in new_content_markers):
            warnings.append("Semantic: PRD contains '新增需求/补充功能/额外建议' markers; PRD assembly should only aggregate, not introduce new requirements")

    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "issues": _make_issues(errors, warnings, path)}


_PRD_ERROR_RULES = [
    ("Missing frontmatter fields:", "prd.missing_frontmatter"),
    ("Invalid status", "prd.invalid_status"),
    ("Missing required headings:", "prd.missing_headings"),
    ("No RTM", "prd.missing_rtm"),
    ("Confirmed artifact has unresolved confirmation fields:", "prd.unresolved_confirmation"),
    ("PRD DoD D5.2 failed:", "prd.d52_missing_upstream"),
]

_PRD_WARNING_RULES = [
    ("Confirmed PRD still contains 待确认 markers", "prd.pending_markers_in_confirmed"),
    ("RTM has no data rows", "prd.rtm_no_data"),
    ("RTM header has", "prd.rtm_column_count"),
    ("RTM rows have", "prd.rtm_incomplete_p0"),
    ("PRD contains", "prd.new_content_markers"),
]


def _check_id(msg: str, rules: list[tuple[str, str]], fallback: str) -> str:
    for needle, check_id in rules:
        if needle in msg:
            return check_id
    return fallback


def _make_issues(errors: list[str], warnings: list[str], path: Path) -> list[dict]:
    """双轨制：errors/warnings 保持字符串列表，issues 为 make_issue 统一 dict。"""
    issues: list[dict] = []
    for e in errors:
        issues.append(make_issue(
            severity="CRITICAL",
            check_id=_check_id(e, _PRD_ERROR_RULES, "prd.structural"),
            family=SKILL_ID,
            location=str(path),
            message=e,
        ))
    for w in warnings:
        issues.append(make_issue(
            severity="MEDIUM",
            check_id=_check_id(w, _PRD_WARNING_RULES, "prd.semantic"),
            family=SKILL_ID,
            location=str(path),
            message=w,
            blocking=False,
        ))
    return issues


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
