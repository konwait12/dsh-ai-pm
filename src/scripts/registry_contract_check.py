#!/usr/bin/env python3
"""Registry contract hardening (Harness借鉴点三：注册表契约硬化).

Checks:
  1. **Schema validation** (without external deps): hand-written walker that
     ensures ``workflow-registry.json`` matches the expected shape — stages/
     work_items/internal_capabilities/artifact_types/support_capabilities
     all present; required fields per row; correct types; no unknown fields;
     ``predecessors`` / ``depends_on`` / ``parent_work_item`` IDs refer to
     existing entries.
  2. **Template ↔ Validator closure**: For every skill (work_item /
     internal_capability / support_capability) that ships a template file
     under ``assets/*.md`` or ``templates/*.md``, the corresponding
     ``scripts/validate_artifact.py`` MUST reference every frontmatter
     *required field* declared by the template. Missing reference = drift.
     This catches the OBS class of bugs where someone adds a new field to
     the artifact template but forgets to update the validator.

Exit 0 = clean contract, 1 = problems. This is intentionally run as the
FIRST check in run_tests_mac.sh (before consistency_check, before fixture
tests) so registry-level defects are surfaced earliest.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

from validation_errors import make_issue

PROJECT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = PROJECT / "src/framework/workflow-registry.json"
FAMILY = "registry_contract"
LOCATION = str(REGISTRY_PATH.relative_to(PROJECT))

# ------- Schema definition (no jsonschema dep: a lightweight spec) -------
# Each T_* describes (required_fields, optional_fields, types). Unknown fields
# are an error so typos like "artifact_fiLe" don't silently degrade.
# Cross-reference rules (predecessors → known work_item ids, etc.) are checked
# separately after shape validation.

T_STAGE = {
    "req": {"id": str, "name": str, "path": str, "work_items": list},
    "opt": {},  # all fields required for stages
}
T_WORK_ITEM = {
    "req": {
        "id": str, "name": str, "order": int, "stage": str,
        "skill_path": str, "artifact_dir": str, "artifact_file": str,
        "artifact_prefix": str, "required_outputs": list,
        "predecessors": list, "reviewer_roles": list,
    },
    "opt": {
        "legacy_wave": int, "legacy_artifact_dir": str, "human_gate": bool,
    },
}
T_INTERNAL_CAP = {
    "req": {"id": str, "parent_work_item": str, "order": int, "skill_path": str},
    "opt": {"output_section": str},
}
T_ARTIFACT_TYPE = {
    "req": {"id": str, "name": str, "producer": str, "artifact_file": str, "depends_on": list},
    "opt": {"prd_destination": str},
}
T_SUPPORT_CAP = {
    "req": {"id": str, "skill_path": str, "trigger": str,
           "applicable_stages": list, "output_location": str},
    "opt": {"resume_work_item": (str, type(None)), "responsible_role": str,
            "output_kind": str, "name": str},
}
T_TOP = {
    "req": {
        "schema_version": int, "stages": list, "work_items": list,
        "internal_capabilities": list, "artifact_types": list,
        "support_capabilities": list,
    },
    "opt": {"issue_policy": dict, "dependency_policy": dict},
}


def _type_ok(value: Any, expected: Any) -> bool:
    """Return True iff value matches expected type (supports tuple-union)."""
    if isinstance(expected, tuple):
        return any(_type_ok(value, e) for e in expected)
    if expected is list:
        return isinstance(value, list)
    if expected is dict:
        return isinstance(value, dict)
    if expected is int:
        # bool is subclass of int in Python → reject booleans for int fields
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, expected)


def _shape_issue(context: str, label: str, kind: str, *, detail: str) -> dict[str, Any]:
    """Build a standardized issue for a schema-shape defect.

    kind ∈ {missing_required, wrong_type, unknown_field, not_object, cross_ref}.
    """
    return make_issue(
        severity="CRITICAL" if kind != "unknown_field" else "HIGH",
        check_id=f"registry.schema.{kind}",
        family=FAMILY,
        location=LOCATION,
        field_path=context,
        message=f"{context}: {detail}",
        expected=(
            f"{context} 必须符合 {label} 契约：必填字段齐全、类型正确、无未知字段，"
            f"且跨引用（stage/predecessors/depends_on/parent_work_item）指向已注册 ID"
        ),
        actual=detail,
        repair_hint=(
            f"打开 src/framework/workflow-registry.json 修正 {context}（{label}）："
            + {
                "missing_required": "补齐缺失的必填字段",
                "wrong_type": "把字段值改为契约要求的类型",
                "unknown_field": "删除拼写错误的字段或修正字段名",
                "not_object": "把该节点改为对象结构",
                "cross_ref": "引用已存在的 stage/work_item/artifact_type 的 id",
            }.get(kind, "按契约修正该节点")
            + "；修改后运行 python3 src/scripts/registry_contract_check.py 验证"
        ),
        source_ref="contracts.md §RegistryContract / registry_contract_check §schema",
    )


def _validate_shape(data: Any, spec: dict[str, dict], label: str,
                    issues: list[dict[str, Any]], context: str = "$") -> None:
    """Shape-check one object against its req/opt spec. Appends issues."""
    if not isinstance(data, dict):
        issues.append(_shape_issue(context, label, "not_object",
                                   detail=f"expected object for {label}, got {type(data).__name__}"))
        return
    req, opt = spec["req"], spec["opt"]
    for key, exp in req.items():
        if key not in data:
            issues.append(_shape_issue(
                context + f".{key}", label, "missing_required",
                detail=f"required field missing for {label}",
            ))
            continue
        if not _type_ok(data[key], exp):
            issues.append(_shape_issue(
                context + f".{key}", label, "wrong_type",
                detail=f"wrong type for {label}: expected {exp!r}, got {type(data[key]).__name__}",
            ))
    for key, exp in opt.items():
        if key in data and not _type_ok(data[key], exp):
            issues.append(_shape_issue(
                context + f".{key}", label, "wrong_type",
                detail=f"wrong type for {label} (optional): expected {exp!r}, got {type(data[key]).__name__}",
            ))
    allowed = set(req.keys()) | set(opt.keys())
    for key in data.keys():
        if key not in allowed:
            issues.append(_shape_issue(
                context + f".{key}", label, "unknown_field",
                detail=f"unknown field '{key}' for {label} (allowed: {sorted(allowed)})",
            ))


def _parse_frontmatter_fields(template_text: str) -> set[str]:
    """Return every frontmatter key in the template's YAML header.

    Example template:
        ---
        artifact_id: BG-001
        status: draft
        foo: true
        ---
    returns {"artifact_id", "status", "foo"}.
    """
    m = re.match(r"---\s*\n(.*?)\n---", template_text, re.DOTALL)
    if not m:
        return set()
    fields: set[str] = set()
    for line in m.group(1).splitlines():
        line = line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if ":" not in line:
            continue
        key = line.split(":", 1)[0].strip()
        if key:
            fields.add(key)
    return fields


def _string_literals_in_py(py_text: str) -> set[str]:
    """Extract every string literal token from Python source (via AST).

    This is what enables the "template field must be referenced by validator"
    check: if a template declares frontmatter field "artifact_id", we expect
    to see the literal string "artifact_id" somewhere in the validator source
    (e.g. inside ``fm.get("artifact_id")`` or a regex pattern / error message
    / issue dict key). Missing literal → drift → contract fail.
    """
    try:
        tree = ast.parse(py_text)
    except SyntaxError:
        return set()
    literals: set[str] = set()
    legacy_str = getattr(ast, "Str", None)  # removed in Py3.12; keep for old runtimes
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value)
        elif legacy_str is not None and isinstance(node, legacy_str):
            literals.add(node.s)
    return literals


def locate_skill_dirs(registry: dict) -> list[tuple[str, Path]]:
    """Return list of (skill_id, skill_abs_dir) for every registered skill."""
    out: list[tuple[str, Path]] = []
    for item in registry.get("work_items", []):
        out.append((item["id"], PROJECT / item["skill_path"]))
    for cap in registry.get("internal_capabilities", []):
        out.append((cap["id"], PROJECT / cap["skill_path"]))
    for cap in registry.get("support_capabilities", []):
        out.append((cap["id"], PROJECT / cap["skill_path"]))
    return out


def validate_schema(registry: dict) -> list[dict[str, Any]]:
    """Shape + cross-reference validation of workflow-registry.json.

    Returns a list of standardized ValidatorIssue dicts (see
    validation_errors.make_issue). Raises nothing; shape defects are surfaced
    as CRITICAL/HIGH issues.
    """
    issues: list[dict[str, Any]] = []
    _validate_shape(registry, T_TOP, "top-level", issues)
    if issues:
        return issues
    for idx, s in enumerate(registry["stages"]):
        _validate_shape(s, T_STAGE, "stage", issues, context=f"$.stages[{idx}]")
    known_stages = {s["id"] for s in registry["stages"]}
    for idx, wi in enumerate(registry["work_items"]):
        _validate_shape(wi, T_WORK_ITEM, "work_item", issues, context=f"$.work_items[{idx}]")
    known_wis = {wi["id"] for wi in registry["work_items"]}
    # Cross-ref: work_item.stage ∈ known_stages; work_item.predecessors ⊆ known_wis
    for wi in registry["work_items"]:
        if wi.get("stage") not in known_stages:
            issues.append(_shape_issue(
                f"$.work_items.{wi['id']}.stage", "work_item", "cross_ref",
                detail=f"stage '{wi.get('stage')}' not registered in $.stages",
            ))
        for pred in wi.get("predecessors", []):
            if pred not in known_wis:
                issues.append(_shape_issue(
                    f"$.work_items.{wi['id']}.predecessors.{pred}", "work_item", "cross_ref",
                    detail=f"predecessor '{pred}' not a known work_item id",
                ))
        at_ids = {a["id"] for a in registry.get("artifact_types", [])}
        for r in wi.get("required_outputs", []):
            if r not in at_ids:
                issues.append(_shape_issue(
                    f"$.work_items.{wi['id']}.required_outputs.{r}", "work_item", "cross_ref",
                    detail=f"required_output '{r}' has no matching artifact_type",
                ))
    for idx, cap in enumerate(registry["internal_capabilities"]):
        _validate_shape(cap, T_INTERNAL_CAP, "internal_capability", issues,
                        context=f"$.internal_capabilities[{idx}]")
        parent = cap.get("parent_work_item")
        if parent and parent not in known_wis:
            issues.append(_shape_issue(
                f"$.internal_capabilities.{cap['id']}.parent_work_item", "internal_capability", "cross_ref",
                detail=f"parent_work_item '{parent}' unknown",
            ))
    for idx, at in enumerate(registry["artifact_types"]):
        _validate_shape(at, T_ARTIFACT_TYPE, "artifact_type", issues,
                        context=f"$.artifact_types[{idx}]")
        prod = at.get("producer")
        if prod and prod not in known_wis:
            issues.append(_shape_issue(
                f"$.artifact_types.{at['id']}.producer", "artifact_type", "cross_ref",
                detail=f"producer '{prod}' not a known work_item id",
            ))
        at_ids = {a["id"] for a in registry.get("artifact_types", [])}
        for dep in at.get("depends_on", []):
            if dep not in at_ids:
                issues.append(_shape_issue(
                    f"$.artifact_types.{at['id']}.depends_on.{dep}", "artifact_type", "cross_ref",
                    detail=f"depends_on '{dep}' unknown",
                ))
    for idx, sc in enumerate(registry["support_capabilities"]):
        _validate_shape(sc, T_SUPPORT_CAP, "support_capability", issues,
                        context=f"$.support_capabilities[{idx}]")
        for stage in sc.get("applicable_stages", []):
            if stage not in known_stages:
                issues.append(_shape_issue(
                    f"$.support_capabilities.{sc['id']}.applicable_stages.{stage}", "support_capability", "cross_ref",
                    detail=f"applicable_stages entry '{stage}' not a registered stage",
                ))
        resume = sc.get("resume_work_item")
        if resume and resume not in known_wis:
            issues.append(_shape_issue(
                f"$.support_capabilities.{sc['id']}.resume_work_item", "support_capability", "cross_ref",
                detail=f"resume_work_item '{resume}' not a known work_item id",
            ))
    # Stage.work_items reference check (双向一致)
    for s in registry["stages"]:
        for wi_id in s.get("work_items", []):
            if wi_id not in known_wis:
                issues.append(_shape_issue(
                    f"$.stages.{s['id']}.work_items.{wi_id}", "stage", "cross_ref",
                    detail=f"listed work_item '{wi_id}' not registered under $.work_items",
                ))
    return issues


def validate_template_validator_closure(registry: dict) -> list[dict[str, Any]]:
    """Check every template's frontmatter fields are referenced by its validator.

    For each registered skill:
      * Find all template files under ``<skill>/assets/*.md`` and
        ``<skill>/templates/*.md``.
      * If ANY template files exist AND ``<skill>/scripts/validate_artifact.py``
        exists → cross-check frontmatter fields vs validator string literals.
      * Missing validator while templates exist → ERROR (contract broken).
      * Template field never appears as a literal in validator source → ERROR
        (template/validator drift: field is no longer checked).

    Returns a list of standardized ValidatorIssue dicts.
    """
    issues: list[dict[str, Any]] = []
    for skill_id, skill_dir in locate_skill_dirs(registry):
        if not skill_dir.is_dir():
            # Path-existence is consistency_check's job; skip here to avoid
            # double-reporting the same underlying issue.
            continue
        template_paths: list[Path] = []
        for glb in ("assets/*.md", "templates/*.md"):
            template_paths.extend(sorted(skill_dir.glob(glb)))
        if not template_paths:
            continue  # skill doesn't ship templates (e.g. competitive-research)
        validator = skill_dir / "scripts/validate_artifact.py"
        if not validator.is_file():
            issues.append(make_issue(
                severity="CRITICAL",
                check_id="registry.closure.missing_validator",
                family=FAMILY,
                location=str(validator.relative_to(PROJECT)) if validator.exists() else skill_id,
                field_path=f"skills.{skill_id}.scripts.validate_artifact.py",
                message=f"{skill_id}: skill ships {len(template_paths)} template file(s) under assets/templates but has no scripts/validate_artifact.py",
                expected=f"每个带模板的 skill（{skill_id}）必须在 scripts/ 下有 validate_artifact.py 校验器",
                actual=f"{skill_id} 有 {len(template_paths)} 个模板但缺少校验器文件",
                repair_hint=f"为 {skill_id} 创建 scripts/validate_artifact.py（可参考子 skill validator template），"
                            f"并在其中校验模板 frontmatter 的每个必填字段",
                source_ref="contracts.md §RegistryContract template↔validator closure",
            ))
            continue
        validator_source = validator.read_text(encoding="utf-8")
        literals = _string_literals_in_py(validator_source)
        # Also: fall back to substring scan for regex-built patterns like
        # re.search(r"^artifact_id:", ...) where AST would see the raw string
        # only as the pattern "artifact_id:" — split any non-identifier characters
        # and collect identifier tokens, so "artifact_id:" yields "artifact_id".
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", validator_source):
            literals.add(token)
        for tp in template_paths:
            try:
                text = tp.read_text(encoding="utf-8")
            except OSError:
                issues.append(make_issue(
                    severity="CRITICAL",
                    check_id="registry.closure.unreadable_template",
                    family=FAMILY,
                    location=str(tp.relative_to(PROJECT)),
                    field_path=f"skills.{skill_id}.templates.{tp.name}",
                    message=f"{skill_id}: cannot read template {tp.relative_to(PROJECT)}",
                    expected="模板文件必须可读",
                    actual=f"读取 {tp} 时发生 OSError",
                    repair_hint="检查模板文件权限与路径；若文件已删除，同步从 registry 移除对应 skill 的模板引用",
                    source_ref="contracts.md §RegistryContract",
                ))
                continue
            fields = _parse_frontmatter_fields(text)
            if not fields:
                # Template without a frontmatter section is a process doc (not an
                # artifact skeleton). Not a contract failure (there's nothing to
                # validate structurally), but log an INFO-level notice in verbose.
                continue
            for fld in sorted(fields):
                # The validator should reference every template frontmatter
                # field. Whitelist: "待确认" placeholder values are data, not
                # structural, so a template field whose *value* is 待确认 still
                # requires the validator to check for its existence.
                if fld in literals:
                    continue
                issues.append(make_issue(
                    severity="HIGH",
                    check_id="registry.closure.e3_drift",
                    family=FAMILY,
                    location=str(tp.relative_to(PROJECT)),
                    field_path=f"skills.{skill_id}.templates.{tp.name}.frontmatter.{fld}",
                    message=f"[E3_drift] {skill_id}: template '{tp.relative_to(PROJECT)}' declares "
                            f"frontmatter field '{fld}' but scripts/validate_artifact.py never references it",
                    expected=f"模板声明的 frontmatter 字段 '{fld}' 必须在 scripts/validate_artifact.py 中至少出现一次"
                             f"（fm.get(\"{fld}\") / 正则 / 错误信息均可）",
                    actual=f"校验器源码（AST 字符串字面量 + 标识符扫描）未发现 '{fld}' 的任何引用",
                    repair_hint=f"二选一：① 若 '{fld}' 是必须校验的字段，在 validate_artifact.py 中显式读取并校验它；"
                                f"② 若 '{fld}' 已废弃，从模板 frontmatter 中删除该字段",
                    source_ref="contracts.md §RegistryContract template↔validator closure / E3_drift",
                ))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        from validation_errors import make_issue
        msg = f"cannot read {REGISTRY_PATH}: {e}"
        issue = make_issue(
            severity="CRITICAL", check_id="registry.read_error", family=FAMILY,
            location=LOCATION, message=msg,
            expected="workflow-registry.json 必须可解析为合法 JSON",
            actual=msg,
            repair_hint="检查文件是否存在、是否为合法 JSON；必要时重新生成注册表",
            source_ref="contracts.md §RegistryContract",
        )
        if args.as_json:
            print(json.dumps({"ok": False, "errors": [issue]}, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {msg}", file=sys.stderr)
        return 1

    schema_issues = validate_schema(registry)
    closure_issues = validate_template_validator_closure(registry)
    all_issues = schema_issues + closure_issues
    ok = not all_issues

    if args.as_json:
        from validation_errors import aggregate_by_check_id
        drift = [i for i in all_issues if i.get("check_id") == "registry.closure.e3_drift"]
        other_closure = [i for i in all_issues
                         if i.get("check_id", "").startswith("registry.closure") and i.get("check_id") != "registry.closure.e3_drift"]
        print(json.dumps({
            "ok": ok,
            "errors": all_issues,
            "schema_errors": [i for i in schema_issues],
            "template_validator_drift": drift,
            "other_closure_errors": other_closure,
            "total": len(all_issues),
            "aggregate_by_check_id": aggregate_by_check_id([all_issues]),
        }, ensure_ascii=False, indent=2))
    else:
        from validation_errors import format_issue
        if ok:
            print("PASS registry contract: schema clean + template↔validator closure OK")
        else:
            print(f"FAIL registry contract: {len(all_issues)} issue(s)")
            for i in all_issues:
                print(f"  - {format_issue(i)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
