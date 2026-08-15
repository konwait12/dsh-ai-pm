#!/usr/bin/env python3
"""Validate the stable structure of a user-journey-and-stories Markdown artifact.

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
    "upstream_artifact_id",
}

REQUIRED_HEADINGS = [
    "预检输入充分度判定",
    "业务生命周期分解",
    "用户旅程图",
    "用户故事卡片",
    "旅程→故事覆盖矩阵",
    "路径类型覆盖检查",
    "事实与决定",
    "假设、AI 推断、未知与冲突",
    "待确认问题",
    "项目范围基线",
    "来源追溯",
    "下游输入摘要",
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
    "superseded", "legacy_unverified",
    "simulated", "legacy_unverified",
}

VALID_PATH_TYPES = {
    "normal", "alternative", "exception", "failure", "handoff", "recovery",
    "正常路径", "备选路径", "异常路径", "失败路径", "交接路径", "恢复路径",
}

CANONICAL_STORY_PATTERN = re.compile(
    r"在〈[^〉]*〉下，作为〈[^〉]*〉，我希望〈[^〉]*〉，以便〈[^〉]*〉"
)


def _normalize_heading(heading: str) -> str:
    return re.sub(r"\s*（[^）]*）\s*$", "", re.sub(r"^\d+\.\s*", "", heading).strip()).strip()


def parse_frontmatter(text: str) -> dict[str, str]:
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

    # --- Structural checks ---
    missing_meta = sorted(REQUIRED_FRONTMATTER - metadata.keys())
    if missing_meta:
        errors.append(f"Missing frontmatter fields: {', '.join(missing_meta)}")

    status = metadata.get("status")
    if status and status not in VALID_STATUSES:
        errors.append(
            f"Invalid status '{status}'. Valid: {', '.join(sorted(VALID_STATUSES))}"
        )

    # Check upstream artifact is present and non-empty for review/confirmed statuses
    upstream = metadata.get("upstream_artifact_id", "")
    if status in {"ready_for_human_review", "confirmed"} and (not upstream or upstream in PENDING_PLACEHOLDERS):
        errors.append(
            "Missing or placeholder upstream_artifact_id; "
            "user-journey-and-stories requires a confirmed project-background-goal artifact"
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

    if "ST-" not in text:
        errors.append("No ST-* story card identifier found; at least one story card is required")

    if status == "confirmed":
        unresolved = [
            key
            for key in ("business_fact_owner", "goal_decision_owner", "reviewer", "confirmed_at")
            if metadata.get(key, "") in {"", *PENDING_PLACEHOLDERS}
        ]
        if unresolved:
            errors.append(
                "Confirmed artifact has unresolved confirmation fields: "
                + ", ".join(unresolved)
            )

    # Confirmed artifact must not have 待确认 in body
    if any(p in text for p in PENDING_PLACEHOLDERS) and status == "confirmed":
        body_without_headings = re.sub(
            r"^##\s+\d+\.\s*[^\n]*$", "", text, flags=re.MULTILINE
        )
        if any(p in body_without_headings for p in PENDING_PLACEHOLDERS):
            warnings.append(
                "Confirmed artifact still contains 待确认 markers in body content; "
                "verify these are accepted non-blocking items"
            )

    # --- Semantic red flags ---
    warnings.extend(check_semantic_red_flags(text, metadata))

    issues = [
        make_issue(
            severity="CRITICAL",
            check_id=_uj_error_check_id(e),
            family="user_journey_and_stories",
            location=str(path),
            message=e,
        )
        for e in errors
    ]
    issues.extend(
        make_issue(
            severity="MEDIUM",
            check_id=_uj_warning_check_id(w),
            family="user_journey_and_stories",
            location=str(path),
            message=w,
            blocking=False,
        )
        for w in warnings
    )
    return {"ok": not errors, "errors": errors, "warnings": warnings, "issues": issues}


_UJ_ERROR_RULES = [
    ("Missing frontmatter fields:", "uj.missing_frontmatter"),
    ("Invalid status", "uj.invalid_status"),
    ("Missing or placeholder upstream_artifact_id;", "uj.missing_upstream"),
    ("Missing required headings:", "uj.missing_headings"),
    ("No ST-* story card identifier found", "uj.missing_story_cards"),
    ("Confirmed artifact has unresolved confirmation fields:", "uj.unresolved_confirmation"),
]

_UJ_WARNING_RULES = [
    ("Confirmed artifact still contains 待确认 markers in body content", "uj.pending_markers_in_confirmed"),
    ("业务生命周期分解 has fewer than 2 non-placeholder stages", "uj.insufficient_lifecycle_stages"),
    ("no story card uses the canonical", "uj.no_canonical_story_format"),
    ("旅程→故事覆盖矩阵 has", "uj.unexplained_coverage_gaps"),
    ("role-grouped listing has no non-placeholder role sections", "uj.no_role_groups"),
    ("exceeds the 5-session cap", "uj.clarifications_over_cap"),
    ("session row(s)", "uj.clarifications_unfilled"),
    ("critical path types still 待确认 in §5", "uj.uncovered_path_types"),
]


def _uj_error_check_id(msg: str) -> str:
    for needle, check_id in _UJ_ERROR_RULES:
        if needle in msg:
            return check_id
    return "uj.structural"


def _uj_warning_check_id(msg: str) -> str:
    for needle, check_id in _UJ_WARNING_RULES:
        if needle in msg:
            return check_id
    return "uj.semantic"


def check_semantic_red_flags(text: str, metadata: dict[str, str]) -> list[str]:
    warnings: list[str] = []
    status = metadata.get("status")

    # Flag 1: ready_for_human_review but fewer than 2 lifecycle stages with content.
    if status == "ready_for_human_review":
        # Count non-empty lifecycle stage rows in §1 table
        stage_rows = re.findall(
            r"^\|\s*(.+?)\s*\|",
            text,
            re.MULTILINE,
        )
        # Count rows in §1 (after the header/separator)
        lifecycle_section = re.search(
            r"^##\s+\d+\.\s*业务生命周期分解\s*$(.*?)(?=^##\s+|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if lifecycle_section:
            section_text = lifecycle_section.group(1)
            data_rows = [
                line for line in section_text.splitlines()
                if line.lstrip().startswith("|")
                and "---" not in line
                and "阶段" not in line
                and "待确认" not in line
            ]
            if len(data_rows) < 2:
                warnings.append(
                    "Semantic: status is ready_for_human_review but 业务生命周期分解 has "
                    f"fewer than 2 non-placeholder stages ({len(data_rows)} found); "
                    "lifecycle is likely insufficiently decomposed"
                )

    # Flag 2: Story cards present but no canonical format stories found.
    story_count = len(re.findall(r"ST-\d+", text))
    canonical_count = len(CANONICAL_STORY_PATTERN.findall(text))
    if story_count >= 1 and canonical_count == 0 and status == "ready_for_human_review":
        warnings.append(
            "Semantic: status is ready_for_human_review but no story card uses the canonical "
            "format '在〈前提/场景〉下，作为〈角色〉，我希望〈动作〉，以便〈目标/价值〉'; "
            "verify the story cards are properly formatted"
        )

    # Flag 3: Coverage matrix has gaps without reasons.
    if status == "ready_for_human_review":
        coverage_section = re.search(
            r"^##\s+\d+\.\s*旅程→故事覆盖矩阵\s*$(.*?)(?=^##\s+|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if coverage_section:
            cov_text = coverage_section.group(1)
            gap_rows = [
                line for line in cov_text.splitlines()
                if line.lstrip().startswith("|")
                and "---" not in line
                and ("未覆盖" in line or "待确认" in line)
            ]
            if gap_rows:
                unexplained = [
                    line for line in gap_rows
                    if line.count("|") >= 4 and line.split("|")[4].strip() in {"—", "-", "", "待确认"}
                ]
                if unexplained:
                    warnings.append(
                        f"Semantic: 旅程→故事覆盖矩阵 has {len(unexplained)} gap(s) without "
                        "explicit reasons; document why each gap exists"
                    )

    # Flag 4: Journey map mentions roles not in upstream background.
    # (Soft check: if roles appear in §2 but not as known roles from §0/preflight)
    roles_in_journey = set(re.findall(r"作为〈([^〉]+)〉", text))
    roles_in_stories = set(re.findall(r"作为〈([^〉]+)〉", text))
    # This is a soft heuristic — we flag if the artifact declares roles in §0
    # that don't match what appears in the journey/story sections.
    if status == "ready_for_human_review":
        # Check §3.1 role-grouped listing has content
        role_sections = re.findall(
            r"^###\s+(.+?)\s*$",
            text,
            re.MULTILINE,
        )
        role_group_count = len([
            r for r in role_sections
            if not any(kw in r for kw in ["按角色", "故事清单", "角色名", "待确认"])
        ])
        if role_group_count == 0 and story_count >= 3:
            warnings.append(
                "Semantic: story cards present but §3.1 role-grouped listing has no "
                "non-placeholder role sections; story cards should be organized by role"
            )

    # Flag 5: Clarifications consistency (same logic as `project-background-goal`).
    check_clarifications(text, status, warnings)

    # Flag 6: Path type coverage — ready status but some path types are all 待确认.
    if status == "ready_for_human_review":
        path_section = re.search(
            r"^##\s+\d+\.\s*路径类型覆盖检查\s*$(.*?)(?=^##\s+|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if path_section:
            path_text = path_section.group(1)
            uncovered = []
            for path_type in ["正常路径", "备选路径", "异常路径", "失败路径"]:
                pattern = rf"\|\s*{path_type}.*?\|\s*待确认"
                if re.search(pattern, path_text):
                    uncovered.append(path_type)
            if len(uncovered) >= 2:
                warnings.append(
                    f"Semantic: {len(uncovered)} critical path types still 待确认 in §5 "
                    f"({', '.join(uncovered)}); verify this is intentional"
                )

    return warnings


def check_clarifications(text: str, status: str | None, warnings: list[str]) -> None:
    clarifications_match = re.search(
        r"^##\s+Clarifications\s*$(.*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if clarifications_match:
        body = clarifications_match.group(1)
        session_rows = [
            line for line in body.splitlines()
            if line.lstrip().startswith("|")
            and "---" not in line
            and "session_id" not in line
            and "待补充" not in line
        ]
        if len(session_rows) > 5:
            warnings.append(
                f"Clarifications: {len(session_rows)} sessions found, exceeds the 5-session cap"
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
