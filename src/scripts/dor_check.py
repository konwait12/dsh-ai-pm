#!/usr/bin/env python3
"""Check work-item readiness and completion without approving artifacts.

Adds knowledge-state coverage enforcement (v2): for any artifact whose
status is `ready_for_human_review` or `confirmed`, the body must include
all six knowledge states — FACT / DECISION / ASSUMPTION / AI_INFERENCE /
UNKNOWN / CONFLICT — and ASSUMPTION share must be ≤ 30%. See
`src/framework/thinking-core.md` §1.5/§1.6 and `contracts.md` for the
authoritative definitions of the six states.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from workflow_registry import artifact_status, find_artifact, resolve_work_item, skill_path, work_items


# ---- Knowledge state coverage check (v2) -----------------------------------

KNOWLEDGE_STATES = ("FACT", "DECISION", "ASSUMPTION", "AI_INFERENCE", "UNKNOWN", "CONFLICT")
# Match a knowledge state appearing as a table cell (e.g. "| FACT |") or as
# a labelled prefix (e.g. "AI_INFERENCE: ...").  The cell match wins for
# artifacts that use the canonical evidence table form.
KS_CELL_RE = re.compile(r"\|\s*(" + "|".join(KNOWLEDGE_STATES) + r")\s*\|")
# 行首 / 空白 / 中文标点之后的标注都算，如「现状 FACT：人工回执」「。DECISION：走线上」
# 「**FACT**：」加粗形式兼容；要求冒号紧跟标签，避免把正文里碰巧出现的单词误计。
KS_PREFIX_RE = re.compile(r"(?:^|[\s。；;，,、！？!?])\*?\*?(" + "|".join(KNOWLEDGE_STATES) + r")\*?\*?[:：]", re.MULTILINE)
KS_MAX_ASSUMPTION_RATIO = 0.30  # hard ceiling: 假设不能超过总条目的 30%


def knowledge_state_coverage(artifact_text: str) -> dict:
    """Return coverage stats for the six knowledge states in `artifact_text`.

    The artifact must surface every state at least once; otherwise it is
    not ready for human review.  The function deliberately does not judge
    *content* quality, only that the labels are present and balanced.
    """
    matches: list[str] = []
    for pattern in (KS_CELL_RE, KS_PREFIX_RE):
        matches.extend(pattern.findall(artifact_text))
    counts = {state: 0 for state in KNOWLEDGE_STATES}
    for state in matches:
        counts[state] += 1
    total = sum(counts.values())
    covered_states = [state for state, n in counts.items() if n > 0]
    missing_states = [state for state, n in counts.items() if n == 0]
    assumption_ratio = (counts["ASSUMPTION"] / total) if total else 0.0
    return {
        "counts": counts,
        "total": total,
        "covered_states": covered_states,
        "missing_states": missing_states,
        "assumption_ratio": round(assumption_ratio, 3),
    }


def knowledge_state_check(artifact_text: str, status: str) -> dict:
    """Hard gate, calibrated by status:

    - `ready_for_human_review`: artifact must surface ALL six knowledge states
      (FACT / DECISION / ASSUMPTION / AI_INFERENCE / UNKNOWN / CONFLICT) and
      keep ASSUMPTION share ≤ 30%. Rationale: the human reviewer needs to see
      what is known, what is inferred, what is missing, and what is in
      conflict before signing off.
    - `confirmed`: the six-state coverage check is *informational* only.
      After human review, AI_INFERENCE / ASSUMPTION / CONFLICT entries are
      expected to be promoted to FACT / DECISION or formally closed, so the
      artifact may legitimately no longer carry raw ASSUMPTION / CONFLICT
      labels. The function still records counts so reviewers can audit the
      promotion discipline.
    - Other statuses: skipped.
    """
    if status not in {"ready_for_human_review", "confirmed"}:
        return {"name": "knowledge_state_coverage", "pass": True, "skipped": True,
                "detail": f"status={status} (gate not enforced)"}
    cov = knowledge_state_coverage(artifact_text)
    detail_parts = [f"covered={len(cov['covered_states'])}/6", f"total={cov['total']}",
                    f"assumption_ratio={cov['assumption_ratio']}"]
    if status == "confirmed":
        # Informational only — record coverage but never fail a confirmed artifact.
        return {"name": "knowledge_state_coverage", "pass": True, "informational": True, **cov,
                "detail": "confirmed: informational only (promotions expected) | " + " ".join(detail_parts)}
    # ready_for_human_review: full hard gate
    if cov["missing_states"]:
        return {"name": "knowledge_state_coverage", "pass": False,
                "missing_states": cov["missing_states"],
                "detail": "missing=" + ",".join(cov["missing_states"]) + " | " + " ".join(detail_parts)}
    if cov["assumption_ratio"] > KS_MAX_ASSUMPTION_RATIO:
        return {"name": "knowledge_state_coverage", "pass": False,
                "assumption_ratio": cov["assumption_ratio"],
                "detail": f"ASSUMPTION share {cov['assumption_ratio']} > 0.30 | " + " ".join(detail_parts)}
    return {"name": "knowledge_state_coverage", "pass": True, **cov,
            "detail": "all six states covered, ASSUMPTION ≤ 30% | " + " ".join(detail_parts)}


def stage_closeup_check(req_dir: Path, item: dict, artifact_text: str, status: str) -> dict:
    """B3 每阶段强制收口（旧循环语义）——仅送审 ready_for_human_review 时强制：

    1. 99-review/support/issue-record.md 必须存在且阶段收口表含本 work item 行
       （空清单也是审计证据）
    2. 产物正文每个「待确认」标记必须带引用（Q-/ISS-/DEC-/SRC-，同一行）
    """
    if status != "ready_for_human_review":
        return {"name": "stage_closeup", "pass": True, "skipped": True,
                "detail": f"status={status}（送审才强制）"}
    issues: list[str] = []
    ir = req_dir / "99-review" / "support" / "issue-record.md"
    if not ir.is_file():
        issues.append("99-review/support/issue-record.md 不存在（B3 每阶段强制收口，空清单也是审计证据）")
    else:
        ir_text = ir.read_text(encoding="utf-8")
        if item["id"] not in ir_text:
            issues.append(f"issue-record 阶段收口表缺 {item['id']} 收口行")
    # 待确认引用检查（跳过 frontmatter 与标题行）
    body = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", artifact_text, flags=re.DOTALL)
    unreferenced = []
    for line in body.splitlines():
        if "待确认" not in line:
            continue
        if line.lstrip().startswith("#"):
            continue
        if re.search(r"(Q-\d+|ISS-\d+|DEC-\d+|SRC-\d+)", line):
            continue
        unreferenced.append(line.strip()[:60])
    if unreferenced:
        issues.append(f"{len(unreferenced)} 处「待确认」无 Q-/ISS-/DEC-/SRC- 引用，示例：{unreferenced[0]}")
    return {"name": "stage_closeup", "pass": not issues,
            "detail": " | ".join(issues) if issues else "收口行 + 待确认引用齐全"}


def run_validator(item: dict, artifact: Path) -> tuple[bool, str]:
    validator = skill_path(item) / "scripts/validate_artifact.py"
    if not validator.exists():
        return False, f"validator missing: {validator}"
    result = subprocess.run(
        [sys.executable, str(validator), str(artifact), "--json"],
        capture_output=True, text=True, check=False,
        encoding="utf-8", errors="replace",
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False, result.stderr.strip() or "validator returned invalid JSON"
    return bool(payload.get("ok")), f"errors={len(payload.get('errors', []))}, warnings={len(payload.get('warnings', []))}"


def check_item(req_dir: Path, item: dict) -> dict:
    predecessor_states = {p: artifact_status(req_dir, resolve_work_item(p)) for p in item["predecessors"]}
    dor_ok = all(state == "confirmed" for state in predecessor_states.values())
    artifact = find_artifact(req_dir, item)
    checks = []
    # Entry material DoR: project-background-goal must have registered sources
    # (machine version of the SKILL.md Preflight "no source → STOP" rule).
    if item["id"] == "project-background-goal":
        input_dir = req_dir / "00-input"
        src_files = sorted(input_dir.glob("SRC-*.md")) if input_dir.is_dir() else []
        material_ok = len(src_files) >= 1
        checks.append({"name": "entry_material", "pass": material_ok,
                       "detail": f"00-input SRC materials: {len(src_files)} (need >= 1)"})
        dor_ok = dor_ok and material_ok
    if artifact:
        valid, detail = run_validator(item, artifact)
        checks.append({"name": "artifact_validator", "pass": valid, "detail": detail})
        text = artifact.read_text(encoding="utf-8")
        has_audit = "Constitution Compliance" in text or "自审" in text or "Audit" in text
        checks.append({"name": "audit_evidence", "pass": has_audit})
        # v2: knowledge state coverage hard gate (only fires for review-ready statuses)
        checks.append(knowledge_state_check(text, artifact_status(req_dir, item)))
        # B3: per-stage forced closeout (issue-record exists + 待确认 references)
        checks.append(stage_closeup_check(req_dir, item, text, artifact_status(req_dir, item)))
    else:
        checks.append({"name": "artifact_exists", "pass": False})
    dod_ok = bool(artifact) and all(check["pass"] for check in checks)
    return {
        "work_item": item["id"],
        "stage": item["stage"],
        "artifact": str(artifact.relative_to(req_dir)) if artifact else "not_found",
        "status": artifact_status(req_dir, item),
        "predecessors": predecessor_states,
        "dor_pass": dor_ok,
        "dod_pass": dod_ok,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("req_dir", type=Path)
    parser.add_argument("--work-item", choices=[item["id"] for item in work_items()])
    parser.add_argument("--wave", type=int, choices=range(1, 6), help="Deprecated compatibility alias")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.req_dir.is_dir():
        print(f"ERROR: {args.req_dir} is not a directory", file=sys.stderr)
        return 1
    if args.wave:
        print("DEPRECATED: --wave will be removed after the v3 compatibility baseline.", file=sys.stderr)
    selected = [resolve_work_item(args.work_item, args.wave)] if (args.work_item or args.wave) else work_items()
    results = [check_item(args.req_dir, item) for item in selected]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result['work_item']}: DoR={result['dor_pass']} DoD={result['dod_pass']} status={result['status']}")
            for check in result["checks"]:
                print(f"  {'PASS' if check['pass'] else 'FAIL'} {check['name']} {check.get('detail', '')}")
    return 0 if all(r["dor_pass"] and r["dod_pass"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
