#!/usr/bin/env python3
"""Cross-document consistency check: workflow-registry.json ↔ Skill files.

Checks:
1. Registry paths (stages / work_items / internal_capabilities / support_capabilities)
   all resolve to existing directories or files on disk.
2. Every registered work item has a SKILL.md, a scripts/validate_artifact.py, and a
   references/thinking-framework.md that references src/framework/thinking-core.md.
3. Artifact types: every artifact_type.producer maps to a known work item; every
   artifact_type.depends_on entry maps to a known artifact_type id.
4. Reviewer roles: every work item's reviewer_roles is non-empty and each role is
   a known role token (business_owner / product_owner / tech_owner / designer / qa).
5. requirements/ content: REQ-* dirs must be structurally valid; surfaces when no
   real (non-simulated) requirement product exists yet.
6. (E1) Template ↔ validator contract: `_frontmatter-schema.md`'s
   `upstream_artifact_ids` example must match the regex the prd-assembly validator
   actually accepts `(BG|JS|UX|FD)-\\d+(?:-\\d+)?`, so the template and the validator
   cannot silently drift apart again (single- vs double-hyphen convention).

Exit code 0 = consistent, 1 = inconsistencies found (non-interactive must fail).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from validation_errors import make_issue

PROJECT = Path(__file__).resolve().parent.parent.parent
REGISTRY = PROJECT / "src/framework/workflow-registry.json"
THINKING_CORE = PROJECT / "src/framework/thinking-core.md"
FAMILY = "consistency"
LOCATION = str(REGISTRY.relative_to(PROJECT))

KNOWN_ROLES = {"business_owner", "product_owner", "tech_owner", "designer", "qa", "tester", "legal", "ops"}


def _add(issues: list[dict[str, Any]], severity: str, check_id: str, message: str, *,
         field_path: str | None = None, expected: str | None = None,
         actual: str | None = None, repair_hint: str | None = None,
         source_ref: str | None = None, blocking: bool | None = None,
         location: str | None = None) -> None:
    """Append a standardized ValidatorIssue (family=consistency)."""
    issues.append(make_issue(
        severity=severity, check_id=check_id, family=FAMILY,
        location=location or LOCATION, field_path=field_path, message=message,
        expected=expected, actual=actual, repair_hint=repair_hint,
        source_ref=source_ref, blocking=blocking,
    ))


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def check_paths(registry: dict, issues: list[dict[str, Any]]) -> None:
    for stage in registry.get("stages", []):
        p = PROJECT / stage["path"]
        if not p.is_dir():
            _add(issues, "CRITICAL", "consistency.paths.stage_missing",
                 f"Registry stage path missing: {stage['id']} -> {stage['path']}",
                 field_path=f"$.stages.{stage['id']}.path",
                 expected=f"stage '{stage['id']}' 的 path 必须在磁盘上存在",
                 actual=f"{p} 目录不存在",
                 repair_hint=f"创建目录 {stage['path']}，或修正 workflow-registry.json 中 stage '{stage['id']}' 的 path",
                 source_ref="consistency_check §paths")
    for item in registry.get("work_items", []):
        p = PROJECT / item["skill_path"]
        if not p.is_dir():
            _add(issues, "CRITICAL", "consistency.paths.work_item_skill_missing",
                 f"Registry work-item skill path missing: {item['id']} -> {item['skill_path']}",
                 field_path=f"$.work_items.{item['id']}.skill_path",
                 expected=f"work_item '{item['id']}' 的 skill_path 必须在磁盘上存在",
                 actual=f"{p} 目录不存在",
                 repair_hint=f"创建目录 {item['skill_path']}，或修正 registry 中 '{item['id']}' 的 skill_path",
                 source_ref="consistency_check §paths")
    for cap in registry.get("internal_capabilities", []):
        p = PROJECT / cap["skill_path"]
        if not p.is_dir():
            _add(issues, "CRITICAL", "consistency.paths.internal_cap_missing",
                 f"Registry internal-capability path missing: {cap['id']} -> {cap['skill_path']}",
                 field_path=f"$.internal_capabilities.{cap['id']}.skill_path",
                 expected=f"internal_capability '{cap['id']}' 的 skill_path 必须在磁盘上存在",
                 actual=f"{p} 目录不存在",
                 repair_hint=f"创建目录 {cap['skill_path']}，或修正 registry 中 '{cap['id']}' 的 skill_path",
                 source_ref="consistency_check §paths")
    for cap in registry.get("support_capabilities", []):
        p = PROJECT / cap["skill_path"]
        if not p.is_dir():
            _add(issues, "CRITICAL", "consistency.paths.support_cap_missing",
                 f"Registry support-capability path missing: {cap['id']} -> {cap['skill_path']}",
                 field_path=f"$.support_capabilities.{cap['id']}.skill_path",
                 expected=f"support_capability '{cap['id']}' 的 skill_path 必须在磁盘上存在",
                 actual=f"{p} 目录不存在",
                 repair_hint=f"创建目录 {cap['skill_path']}，或修正 registry 中 '{cap['id']}' 的 skill_path",
                 source_ref="consistency_check §paths")


def check_skill_contracts(registry: dict, issues: list[dict[str, Any]]) -> None:
    item_ids = {item["id"] for item in registry.get("work_items", [])}
    for item in registry.get("work_items", []):
        base = PROJECT / item["skill_path"]
        if not (base / "SKILL.md").is_file():
            _add(issues, "CRITICAL", "consistency.skill.missing_skill_md",
                 f"{item['id']}: missing SKILL.md",
                 field_path=f"skills.{item['id']}.SKILL.md",
                 expected=f"work_item '{item['id']}' 必须在 skill 目录下提供 SKILL.md",
                 actual=f"{base / 'SKILL.md'} 不存在",
                 repair_hint=f"为 {item['id']} 创建 SKILL.md（遵循其他 skill 的 SKILL.md 结构）",
                 source_ref="workflow.md §Work-Item Skills")
        if not (base / "scripts/validate_artifact.py").is_file():
            _add(issues, "CRITICAL", "consistency.skill.missing_validator",
                 f"{item['id']}: missing scripts/validate_artifact.py",
                 field_path=f"skills.{item['id']}.scripts.validate_artifact.py",
                 expected=f"work_item '{item['id']}' 必须在 scripts/ 下提供 validate_artifact.py",
                 actual=f"{base / 'scripts/validate_artifact.py'} 不存在",
                 repair_hint=f"为 {item['id']} 创建 scripts/validate_artifact.py",
                 source_ref="contracts.md §RegistryContract template↔validator closure")
        tf = base / "references/thinking-framework.md"
        if not tf.is_file():
            _add(issues, "CRITICAL", "consistency.skill.missing_thinking_framework",
                 f"{item['id']}: missing references/thinking-framework.md",
                 field_path=f"skills.{item['id']}.references.thinking-framework.md",
                 expected=f"work_item '{item['id']}' 必须提供 references/thinking-framework.md",
                 actual=f"{tf} 不存在",
                 repair_hint=f"为 {item['id']} 创建 references/thinking-framework.md 并引用 src/framework/thinking-core.md",
                 source_ref="consistency_check §skill_contracts")
        else:
            text = tf.read_text(encoding="utf-8")
            if "thinking-core.md" not in text:
                _add(issues, "MEDIUM", "consistency.skill.thinking_core_not_referenced",
                     f"{item['id']}: references/thinking-framework.md does not reference src/framework/thinking-core.md",
                     field_path=f"skills.{item['id']}.references.thinking-framework.md",
                     expected="thinking-framework.md 必须引用 src/framework/thinking-core.md",
                     actual="文本中未找到 'thinking-core.md'",
                     repair_hint=f"在 {item['id']} 的 thinking-framework.md 中引用 thinking-core.md（链接或文字均可）",
                     source_ref="workflow.md §Think")
    # sub-skills: their thinking-framework must also reference thinking-core
    for cap in registry.get("internal_capabilities", []):
        tf = PROJECT / cap["skill_path"] / "references/thinking-framework.md"
        if tf.is_file():
            text = tf.read_text(encoding="utf-8")
            if "thinking-core.md" not in text:
                _add(issues, "MEDIUM", "consistency.subskill.thinking_core_not_referenced",
                     f"{cap['id']}: sub-skill thinking-framework.md does not reference thinking-core.md",
                     field_path=f"subskills.{cap['id']}.references.thinking-framework.md",
                     expected="子 skill 的 thinking-framework.md 必须引用 thinking-core.md",
                     actual="文本中未找到 'thinking-core.md'",
                     repair_hint=f"在 {cap['id']} 的 thinking-framework.md 中引用 thinking-core.md",
                     source_ref="workflow.md §Think")
        else:
            _add(issues, "CRITICAL", "consistency.subskill.missing_thinking_framework",
                 f"{cap['id']}: sub-skill missing references/thinking-framework.md",
                 field_path=f"subskills.{cap['id']}.references.thinking-framework.md",
                 expected=f"子 skill '{cap['id']}' 必须提供 references/thinking-framework.md",
                 actual=f"{tf} 不存在",
                 repair_hint=f"为 {cap['id']} 创建 references/thinking-framework.md",
                 source_ref="consistency_check §skill_contracts")
    # support/branch skills: enforce SKILL.md + validate_artifact.py + references/thinking-framework.md
    for cap in registry.get("support_capabilities", []):
        base = PROJECT / cap["skill_path"]
        if not base.is_dir():
            _add(issues, "CRITICAL", "consistency.support.skill_dir_missing",
                 f"support/{cap['id']}: skill_path directory missing → {cap['skill_path']}",
                 field_path=f"$.support_capabilities.{cap['id']}.skill_path",
                 expected=f"support_capability '{cap['id']}' 的 skill_path 目录必须存在",
                 actual=f"{base} 不存在",
                 repair_hint=f"创建目录 {cap['skill_path']}，或修正 registry",
                 source_ref="consistency_check §skill_contracts")
            continue
        if not (base / "SKILL.md").is_file():
            _add(issues, "CRITICAL", "consistency.support.missing_skill_md",
                 f"support/{cap['id']}: missing SKILL.md under {cap['skill_path']}",
                 field_path=f"support.{cap['id']}.SKILL.md",
                 expected=f"support skill '{cap['id']}' 必须提供 SKILL.md",
                 actual=f"{base / 'SKILL.md'} 不存在",
                 repair_hint=f"为 {cap['id']} 创建 SKILL.md",
                 source_ref="consistency_check §skill_contracts")
        if not (base / "scripts/validate_artifact.py").is_file():
            _add(issues, "CRITICAL", "consistency.support.missing_validator",
                 f"support/{cap['id']}: missing scripts/validate_artifact.py under {cap['skill_path']}",
                 field_path=f"support.{cap['id']}.scripts.validate_artifact.py",
                 expected=f"support skill '{cap['id']}' 必须提供 scripts/validate_artifact.py",
                 actual=f"{base / 'scripts/validate_artifact.py'} 不存在",
                 repair_hint=f"为 {cap['id']} 创建 scripts/validate_artifact.py",
                 source_ref="consistency_check §skill_contracts")
        tf = base / "references/thinking-framework.md"
        if tf.is_file():
            text = tf.read_text(encoding="utf-8")
            if "thinking-core.md" not in text:
                _add(issues, "MEDIUM", "consistency.support.thinking_core_not_referenced",
                     f"support/{cap['id']}: references/thinking-framework.md does not reference src/framework/thinking-core.md",
                     field_path=f"support.{cap['id']}.references.thinking-framework.md",
                     expected="thinking-framework.md 必须引用 thinking-core.md",
                     actual="文本中未找到 'thinking-core.md'",
                     repair_hint=f"在 {cap['id']} 的 thinking-framework.md 中引用 thinking-core.md",
                     source_ref="workflow.md §Think")
        else:
            _add(issues, "MEDIUM", "consistency.support.missing_thinking_framework",
                 f"support/{cap['id']}: missing references/thinking-framework.md",
                 field_path=f"support.{cap['id']}.references.thinking-framework.md",
                 expected=f"support skill '{cap['id']}' 建议提供 references/thinking-framework.md",
                 actual=f"{tf} 不存在",
                 repair_hint=f"为 {cap['id']} 创建 references/thinking-framework.md",
                 source_ref="consistency_check §skill_contracts",
                 blocking=False)
    # reviewer roles
    for item in registry.get("work_items", []):
        roles = item.get("reviewer_roles", [])
        if not roles:
            _add(issues, "CRITICAL", "consistency.reviewer_roles.empty",
                 f"{item['id']}: empty reviewer_roles",
                 field_path=f"$.work_items.{item['id']}.reviewer_roles",
                 expected=f"work_item '{item['id']}' 必须声明非空 reviewer_roles",
                 actual="reviewer_roles 为空列表",
                 repair_hint=f"为 {item['id']} 添加至少一个已知角色（{sorted(KNOWN_ROLES)}）",
                 source_ref="workflow.md §Human Gate")
        for role in roles:
            if role not in KNOWN_ROLES:
                _add(issues, "MEDIUM", "consistency.reviewer_roles.unknown_role",
                     f"{item['id']}: reviewer role '{role}' not in known set {sorted(KNOWN_ROLES)}",
                     field_path=f"$.work_items.{item['id']}.reviewer_roles.{role}",
                     expected=f"角色必须在已知集合 {sorted(KNOWN_ROLES)} 中",
                     actual=f"角色 '{role}' 不在已知集合中",
                     repair_hint=f"使用已知角色之一：{sorted(KNOWN_ROLES)}；若确为新角色，先更新 KNOWN_ROLES",
                     source_ref="consistency_check §reviewer_roles",
                     blocking=False)


def check_artifact_types(registry: dict, issues: list[dict[str, Any]]) -> None:
    item_ids = {item["id"] for item in registry.get("work_items", [])}
    artifact_ids = {a["id"] for a in registry.get("artifact_types", [])}
    for a in registry.get("artifact_types", []):
        if a["producer"] not in item_ids:
            _add(issues, "CRITICAL", "consistency.artifact_types.unknown_producer",
                 f"Artifact type '{a['id']}': producer '{a['producer']}' is not a known work item",
                 field_path=f"$.artifact_types.{a['id']}.producer",
                 expected=f"artifact_type '{a['id']}' 的 producer 必须是已注册的 work_item id",
                 actual=f"producer '{a['producer']}' 不在 work_items 中",
                 repair_hint=f"把 producer 改为已注册的 work_item id（{sorted(item_ids)}），或在 registry 注册该 work_item",
                 source_ref="consistency_check §artifact_types")
        for dep in a.get("depends_on", []):
            if dep not in artifact_ids:
                _add(issues, "CRITICAL", "consistency.artifact_types.unknown_depends_on",
                     f"Artifact type '{a['id']}': depends_on '{dep}' is not a known artifact type",
                     field_path=f"$.artifact_types.{a['id']}.depends_on.{dep}",
                     expected=f"depends_on 条目必须是已注册的 artifact_type id",
                     actual=f"depends_on '{dep}' 不在 artifact_types 中",
                     repair_hint=f"把 depends_on 改为已注册的 artifact_type id（{sorted(artifact_ids)}）",
                     source_ref="consistency_check §artifact_types")


def check_requirements_content(issues: list[dict[str, Any]]) -> None:
    """Close the 'empty requirements/' blind spot.

    `requirements/` is gitignored (each user creates their own), so a fresh
    clone legitimately has none.  But if REQ-* dirs exist, their structure
    must be valid, and we surface how many non-simulated PRDs actually exist
    so the repo cannot silently claim 'validated' without evidence.
    """
    req_root = PROJECT / "requirements"
    if not req_root.is_dir():
        _add(issues, "MEDIUM", "consistency.requirements.no_dir",
             "requirements/ 不存在 — 尚无真实端到端需求产物（待首个真实需求验证）",
             field_path="requirements/",
             expected="requirements/ 目录存在（可被 .gitignore，但本地应有真实需求目录）",
             actual="requirements/ 不存在",
             repair_hint="创建一个真实需求目录（如 requirements/REQ-NNN-xxx/，含 README.md 与 00-input/）",
             source_ref="consistency_check §requirements_content",
             blocking=False)
        return
    req_dirs = [d for d in req_root.iterdir() if d.is_dir() and d.name.startswith("REQ-")]
    if not req_dirs:
        _add(issues, "MEDIUM", "consistency.requirements.empty",
             "requirements/ 为空 — 尚无真实端到端需求产物（待首个真实需求验证）",
             field_path="requirements/",
             expected="requirements/ 下至少有一个 REQ-* 目录",
             actual="requirements/ 存在但没有任何 REQ-* 目录",
             repair_hint="创建 requirements/REQ-NNN-xxx/ 骨架（README.md + 00-input/）",
             source_ref="consistency_check §requirements_content",
             blocking=False)
        return
    real_prds = 0
    for d in req_dirs:
        if not (d / "README.md").is_file():
            _add(issues, "MEDIUM", "consistency.requirements.missing_readme",
                 f"{d.name}: 缺 README.md（骨架不完整）",
                 field_path=f"requirements.{d.name}.README.md",
                 expected=f"REQ 目录 '{d.name}' 必须有 README.md",
                 actual="README.md 不存在",
                 repair_hint=f"创建 {d.name}/README.md",
                 source_ref="consistency_check §requirements_content",
                 blocking=False)
        if not (d / "00-input").is_dir():
            _add(issues, "MEDIUM", "consistency.requirements.missing_input",
                 f"{d.name}: 缺 00-input/（骨架不完整）",
                 field_path=f"requirements.{d.name}.00-input",
                 expected=f"REQ 目录 '{d.name}' 必须有 00-input/",
                 actual="00-input/ 目录不存在",
                 repair_hint=f"创建 {d.name}/00-input/ 并放入 SRC-*.md 源材料",
                 source_ref="consistency_check §requirements_content",
                 blocking=False)
        prd = d / "003-prd-output" / "prd.md"
        if prd.is_file():
            text = prd.read_text(encoding="utf-8")
            if not re.search(r"(?m)^status:\s*simulated", text):
                real_prds += 1
    if real_prds == 0:
        _add(issues, "MEDIUM", "consistency.requirements.no_real_prd",
             "requirements/ 存在 REQ-* 目录但无非 simulated prd.md — 尚无真实人工确认产物",
             field_path="requirements/",
             expected="至少一个 REQ 目录有非 simulated 的 003-prd-output/prd.md",
             actual=f"{len(req_dirs)} 个 REQ 目录中没有任何非 simulated prd.md",
             repair_hint="完成一个真实需求的端到端确认流程，产出 003-prd-output/prd.md（status≠simulated）",
             source_ref="consistency_check §requirements_content",
             blocking=False)


def check_reference_integrity(registry: dict, issues: list[dict[str, Any]]) -> None:
    """Every references/*.md under a skill must be cited somewhere (SKILL.md / thinking-framework.md / other references)."""
    import re as _re
    for item in registry.get("work_items", []):
        base = PROJECT / item["skill_path"]
        ref_dir = base / "references"
        if not ref_dir.is_dir():
            continue
        # collect all text that could cite references
        citation_sources: list[str] = []
        for f in [base / "SKILL.md", ref_dir / "thinking-framework.md"]:
            if f.is_file():
                citation_sources.append(f.read_text(encoding="utf-8"))
        # also sub-skill references dirs
        sub_dir = base / "skills"
        if sub_dir.is_dir():
            for sub in sorted(sub_dir.iterdir()):
                sref = sub / "references/thinking-framework.md"
                if sref.is_file():
                    citation_sources.append(sref.read_text(encoding="utf-8"))
        blob = "\n".join(citation_sources)
        for ref_file in sorted(ref_dir.glob("*.md")):
            if ref_file.name in {"thinking-framework.md", "output-contract.md", "audit-checklist.md"}:
                continue  # core files, always loaded by convention
            if ref_file.stem not in blob and ref_file.name not in blob:
                _add(issues, "MEDIUM", "consistency.references.uncited",
                     f"{item['id']}: references/{ref_file.name} not cited in SKILL.md / thinking-framework.md",
                     field_path=f"skills.{item['id']}.references.{ref_file.name}",
                     expected=f"references/{ref_file.name} 必须在 SKILL.md 或 thinking-framework.md 中被引用",
                     actual="SKILL.md / thinking-framework.md / 子 skill thinking-framework 中均未出现该文件名或 stem",
                     repair_hint=f"在 {item['id']} 的 SKILL.md 或 thinking-framework.md 中引用 references/{ref_file.name}；若文件已废弃则删除",
                     source_ref="consistency_check §reference_integrity",
                     blocking=False)
    # support skills
    for cap in registry.get("support_capabilities", []):
        base = PROJECT / cap["skill_path"]
        ref_dir = base / "references"
        if not ref_dir.is_dir():
            continue
        blob = ""
        for f in [base / "SKILL.md", ref_dir / "thinking-framework.md"]:
            if f.is_file():
                blob += f.read_text(encoding="utf-8")
        for ref_file in sorted(ref_dir.glob("*.md")):
            if ref_file.name in {"thinking-framework.md"}:
                continue
            if ref_file.stem not in blob and ref_file.name not in blob:
                _add(issues, "MEDIUM", "consistency.references.uncited_support",
                     f"{cap['id']}: references/{ref_file.name} not cited in SKILL.md / thinking-framework.md",
                     field_path=f"support.{cap['id']}.references.{ref_file.name}",
                     expected=f"references/{ref_file.name} 必须在 SKILL.md 或 thinking-framework.md 中被引用",
                     actual="SKILL.md / thinking-framework.md 中均未出现该文件名或 stem",
                     repair_hint=f"在 {cap['id']} 的 SKILL.md 或 thinking-framework.md 中引用 references/{ref_file.name}",
                     source_ref="consistency_check §reference_integrity",
                     blocking=False)


def check_upstream_artifact_ids_contract(issues: list[dict[str, Any]]) -> None:
    """E1: `_frontmatter-schema.md` 的 upstream_artifact_ids 示例必须与 prd-assembly
    校验器实际接受的正则 (BG|JS|UX|FD)-\\d+(?:-\\d+)? 一致。

    背景：模板示例曾写单连字符（BG-XXX），而校验器曾要求双连字符，导致 gate 失败；
    现校验器已兼容单连字符。此检查作为自动化护栏，防止模板与校验器约定再次漂移。
    """
    schema = PROJECT / "src/templates/_frontmatter-schema.md"
    validator = PROJECT / "src/stages/003-prd-output/skills/prd-assembly/scripts/validate_artifact.py"
    if not schema.is_file():
        _add(issues, "CRITICAL", "consistency.e1.schema_missing",
             "E1: _frontmatter-schema.md 缺失",
             field_path="src/templates/_frontmatter-schema.md",
             expected="_frontmatter-schema.md 模板契约文件必须存在",
             actual="文件缺失",
             repair_hint="创建 src/templates/_frontmatter-schema.md（含 upstream_artifact_ids 示例）",
             source_ref="consistency_check §E1")
        return
    if not validator.is_file():
        _add(issues, "CRITICAL", "consistency.e1.validator_missing",
             "E1: prd-assembly validate_artifact.py 缺失",
             field_path="src/stages/003-prd-output/skills/prd-assembly/scripts/validate_artifact.py",
             expected="prd-assembly 校验器必须存在",
             actual="文件缺失",
             repair_hint="创建 prd-assembly 的 validate_artifact.py",
             source_ref="consistency_check §E1")
        return

    text = schema.read_text(encoding="utf-8")
    m = re.search(r'upstream_artifact_ids:\s*\[([^\]]*)\]', text)
    if not m:
        _add(issues, "MEDIUM", "consistency.e1.no_example",
             "E1: _frontmatter-schema.md 中未找到 upstream_artifact_ids 示例",
             field_path="src/templates/_frontmatter-schema.md",
             expected="模板中应声明 upstream_artifact_ids 示例",
             actual="未匹配到 upstream_artifact_ids: [...]",
             repair_hint="在 _frontmatter-schema.md 中补充 upstream_artifact_ids 示例",
             source_ref="consistency_check §E1",
             blocking=False)
        return
    example_ids = re.findall(r'"([^"]+)"', m.group(1))
    if not example_ids:
        _add(issues, "MEDIUM", "consistency.e1.empty_example",
             "E1: _frontmatter-schema.md 中 upstream_artifact_ids 示例为空",
             field_path="src/templates/_frontmatter-schema.md",
             expected="upstream_artifact_ids 至少有一个带引号的示例",
             actual="示例为空",
             repair_hint="在 upstream_artifact_ids 中填入带引号的示例 ID",
             source_ref="consistency_check §E1",
             blocking=False)
        return

    vtext = validator.read_text(encoding="utf-8")
    vm = re.search(r"\(BG\|JS\|UX\|FD\)-\\d\+\(\?:-\\d\+\)\?", vtext)
    if not vm:
        _add(issues, "MEDIUM", "consistency.e1.regex_missing",
             "E1: validate_artifact.py 中未找到 upstream_artifact_ids 正则 (BG|JS|UX|FD)-\\d+(?:-\\d+)?",
             field_path="src/stages/003-prd-output/skills/prd-assembly/scripts/validate_artifact.py",
             expected="校验器源码应包含正则 (BG|JS|UX|FD)-\\d+(?:-\\d+)?",
             actual="未匹配到该正则模式",
             repair_hint="确认 prd-assembly 校验器使用的 upstream 正则与此处期望一致",
             source_ref="consistency_check §E1",
             blocking=False)
        return
    pattern = re.compile(vm.group(0))

    for aid in example_ids:
        # 模板示例常用占位符 XXX 表示数字段，替换为 123 后再与校验器正则比对
        probe = re.sub(r"X+", "123", aid)
        if not pattern.fullmatch(probe):
            _add(issues, "CRITICAL", "consistency.e1.drift",
                 f"E1: _frontmatter-schema.md 示例 '{aid}' 与 prd-assembly 校验器正则 "
                 f"'{vm.group(0)}' 不一致（模板与校验器约定漂移）",
                 field_path=f"src/templates/_frontmatter-schema.md.upstream_artifact_ids.{aid}",
                 expected=f"模板示例 '{aid}' 必须能匹配校验器正则 {vm.group(0)}",
                 actual=f"'{probe}' 不满足 fullmatch",
                 repair_hint="统一模板示例与校验器正则的连字符约定（单连字符 BG-XXX 或双连字符），保证二者一致",
                 source_ref="consistency_check §E1 / OBS 教训")


def main() -> int:
    issues: list[dict[str, Any]] = []

    if not REGISTRY.is_file():
        print(f"ERROR: registry missing: {REGISTRY}")
        return 1
    if not THINKING_CORE.is_file():
        _add(issues, "MEDIUM", "consistency.thinking_core_missing",
             "src/framework/thinking-core.md missing (referenced by all thinking-frameworks)",
             field_path="src/framework/thinking-core.md",
             expected="thinking-core.md 必须存在（所有 thinking-framework 引用它）",
             actual="文件缺失",
             repair_hint="恢复 src/framework/thinking-core.md",
             source_ref="workflow.md §Think",
             blocking=False)

    registry = load_registry()
    check_paths(registry, issues)
    check_skill_contracts(registry, issues)
    check_artifact_types(registry, issues)
    check_reference_integrity(registry, issues)
    check_requirements_content(issues)
    check_upstream_artifact_ids_contract(issues)

    from validation_errors import aggregate_by_check_id, format_issue
    errors = [i for i in issues if i.get("severity") in ("CRITICAL", "HIGH") and i.get("blocking", True)]
    warnings = [i for i in issues if i not in errors]

    print("== consistency_check ==")
    for w in warnings:
        print(f"  WARN: {format_issue(w)}")
    for e in errors:
        print(f"  ERROR: {format_issue(e)}")
    print(f"Result: {len(errors)} errors, {len(warnings)} warnings")
    print("Aggregate: " + json.dumps(aggregate_by_check_id([issues]), ensure_ascii=False))
    if errors:
        return 1
    if warnings:
        print("Consistent with warnings (reviewable).")
        return 0
    print("Consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
