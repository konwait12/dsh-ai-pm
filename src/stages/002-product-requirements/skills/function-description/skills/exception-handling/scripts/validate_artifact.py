#!/usr/bin/env python3
"""Sub-skill validator template.

Each sub-skill produces a section of the parent artifact. This validator checks
that the section exists in the parent artifact and that the expected ID prefix
is present. Copy to <sub-skill>/scripts/validate_artifact.py and set:
  SECTION_NAME, ID_PATTERN, and the parent artifact glob.

Run: python3 validate_artifact.py <parent-artifact.md> [--json]
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

# ── Per-sub-skill configuration (edit these) ──────────────
SECTION_NAME = "异常与失败处理"          # e.g. "交互规则"（子 Skill 输出父产物章节）
ID_PATTERN = r"\bEX-\d+\b"        # e.g. r"\bIX-\d+\b"
# ─────────────────────────────────────────────────────────

SKILL_ID = "exception_handling"   # issue family（统一错误格式分组）
CHECK_PREFIX = "ex"               # issue check_id 语义化前缀


def _norm(h: str) -> str:
    return re.sub(r"^\d+\.\s*", "", h).strip()


def _make_issues(errors: list[str], warnings: list[str], path: Path) -> list[dict]:
    """双轨制: errors/warnings 保持字符串列表, issues 为 make_issue 标准 dict."""
    issues: list[dict] = []
    for e in errors:
        if e.startswith("File not found"):
            cid, sev, exp, act, fix = (
                f"{CHECK_PREFIX}.file_not_found", "CRITICAL",
                "产物文件必须存在且可读", f"文件不存在: {e}",
                "确认产物路径正确, 或先创建对应的 artifact 文件",
            )
        elif e.startswith("Missing required section"):
            cid, sev, exp, act, fix = (
                f"{CHECK_PREFIX}.missing_section", "CRITICAL",
                f"父产物必须包含 '{SECTION_NAME}' 章节（## 标题）",
                f"未找到章节: {e}",
                f"在父产物中添加 '## {SECTION_NAME}' 章节并填充本子 skill 输出",
            )
        elif "identifiers found in section" in e:
            cid, sev, exp, act, fix = (
                f"{CHECK_PREFIX}.missing_ids", "HIGH",
                f"'{SECTION_NAME}' 章节内必须包含至少一个 {ID_PATTERN} 标识符",
                f"未找到任何 {ID_PATTERN} 标识符",
                f"为章节内条目补充形如 {ID_PATTERN} 的稳定标识符",
            )
        else:
            cid, sev, exp, act, fix = f"{CHECK_PREFIX}.error", "CRITICAL", None, None, None
        issues.append(make_issue(
            severity=sev, check_id=cid, family=SKILL_ID,
            location=str(path), message=e,
            expected=exp, actual=act, repair_hint=fix,
        ))
    for w in warnings:
        if w.startswith("No knowledge-state tags"):
            cid, exp, act, fix = (
                f"{CHECK_PREFIX}.missing_ks_tags",
                "可追溯内容应带有知识状态标签 (FACT/DECISION/AI_INFERENCE/UNKNOWN)",
                "全文未发现任何知识状态标签",
                "在事实/决定/推断内容旁标注 FACT / DECISION / AI_INFERENCE / UNKNOWN",
            )
        else:
            cid, exp, act, fix = f"{CHECK_PREFIX}.warning", None, None, None
        issues.append(make_issue(
            severity="MEDIUM", check_id=cid, family=SKILL_ID,
            location=str(path), message=w,
            expected=exp, actual=act, repair_hint=fix, blocking=False,
        ))
    return issues


def validate(path: Path) -> dict:
    errors, warnings = [], []
    if not path.is_file():
        return {"ok": False, "errors": [f"File not found: {path}"], "warnings": [],
                "issues": _make_issues([f"File not found: {path}"], [], path)}

    text = path.read_text(encoding="utf-8")

    # Section must exist
    headings = [_norm(m.group(1)) for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)]
    if _norm(SECTION_NAME) not in headings:
        errors.append(f"Missing required section: {SECTION_NAME}")
        return {"ok": False, "errors": errors, "warnings": warnings,
                "issues": _make_issues(errors, warnings, path)}

    # ID prefix must be present
    ids = re.findall(ID_PATTERN, text)
    if not ids:
        errors.append(f"No {ID_PATTERN} identifiers found in section {SECTION_NAME}")

    # Knowledge state tags present for traceable content
    if not any(tag in text for tag in ("FACT", "DECISION", "AI_INFERENCE", "UNKNOWN")):
        warnings.append("No knowledge-state tags (FACT/DECISION/AI_INFERENCE/UNKNOWN) found")

    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "issues": _make_issues(errors, warnings, path)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("artifact", type=Path, nargs="?", default=None,
                   help="Parent artifact path.")
    p.add_argument("--json", action="store_true", dest="j")
    args = p.parse_args()
    if args.artifact is None:
        print("Usage: python3 validate_artifact.py <artifact.md> [--json]", file=sys.stderr)
        sys.exit(2)
    r = validate(args.artifact)
    if args.j:
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
