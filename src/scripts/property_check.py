#!/usr/bin/env python3
"""Property-based completeness checker for function-description artifacts.

Goes beyond structural validation to check logical completeness:
1. State machine exhaustiveness: every state × known event → target state defined
2. Exception path coverage: every BR with an exception branch has a recovery path
3. VL↔AC pairing: every validation rule has a corresponding acceptance criterion
4. Rule density: each FUN has sufficient BR+VL+AC coverage

Usage: python3 property_check.py <function-description.md> [--json]
Exit 0 = complete, 1 = gaps found.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
from validation_errors import make_issue

FAMILY = "property_check"


def _norm(text: str) -> str:
    """Normalize text for comparison: lowercase, strip brackets/parens content."""
    t = text.lower().strip()
    t = re.sub(r'[（(][^)）]*[)）]', '', t)
    t = re.sub(r'[〔【][^】〕]*[】〕]', '', t)
    return re.sub(r'\s+', '', t)


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Parse YAML frontmatter (``---\\n...\\n---``) into a flat dict.

    Mirrors ``workflow_registry.read_frontmatter`` so the minimum-threshold
    check agrees with the rest of the scaffold on what counts as a required
    frontmatter field.
    """
    match = re.match(r"---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip("'\"")
    return result


def check_minimum_threshold(text: str, artifact_path: str = "<artifact>") -> list[dict]:
    """B11: minimum threshold — an artifact must not silent-pass the gate."""
    issues = []
    if not re.search(r"(?m)^#{1,2}\s+\S+", text):
        issues.append(make_issue(
            severity="CRITICAL",
            check_id="minimum_threshold.no_headings",
            family=FAMILY,
            location=artifact_path,
            field_path="sections.headings",
            message="产物缺少章节标题",
            expected="至少有一个 `## ` 或 `# ` 章节（空文件/无章节产物不得通过闸门）",
            actual="全文 0 个 # 或 ## 标题",
            repair_hint="在产物开头添加章节标题，例如 ## 1. 业务背景 / ## 功能清单 FEA-001；若使用模板请按模板的章节结构填写内容",
            source_ref="constitution §4 知识状态必须标注 + B11 silent-pass gate",
        ))
    fm = _parse_frontmatter(text)
    for field in ("artifact_id", "status"):
        if not fm.get(field):
            issues.append(make_issue(
                severity="CRITICAL",
                check_id=f"minimum_threshold.missing_frontmatter_{field}",
                family=FAMILY,
                location=artifact_path,
                field_path=f"frontmatter.{field}",
                message=f"frontmatter 缺少必备字段 {field}",
                expected=f"产物 YAML frontmatter 必须含 `{field}: <value>`（与 templates/_frontmatter-schema.md 一致）",
                actual=f"frontmatter 中未找到字段 {field}（或值为空）",
                repair_hint=f"在文件最上方 YAML frontmatter（---...--- 区块）中添加一行: `{field}: {'<如-FD-001>' if field=='artifact_id' else 'draft'}`",
                source_ref="contracts.md §Artifact States + _frontmatter-schema.md",
            ))
    if not issues:
        issues.append(make_issue(
            severity="INFO",
            check_id="minimum_threshold.pass",
            family=FAMILY,
            location=artifact_path,
            message="Minimum threshold OK: ≥1 heading section + required frontmatter (artifact_id/status)",
            blocking=False,
        ))
    return issues


def _rule_id_re(prefix: str) -> str:
    """Regex fragment matching a rule/feature ID, with an optional letter suffix.

    Accepts `PREFIX-123` and `PREFIX-123A` (single uppercase letter). OBS-005:
    older checks only matched pure digits (`BR-\\d+`), so suffixed IDs such as
    BR-006A were silently skipped by the rule-density / pairing / exception
    checks and under-counted the rules per FUN.
    """
    return rf"\b{prefix}-\d+[A-Z]?\b"


def parse_sections(text: str) -> dict[str, str]:
    """Extract sections by ## heading."""
    sections = {}
    current = "preamble"
    current_content = []
    for line in text.split("\n"):
        m = re.match(r'^##\s+(.+)', line)
        if m:
            sections[current] = "\n".join(current_content)
            current = _norm(m.group(1))
            current_content = []
        else:
            current_content.append(line)
    sections[current] = "\n".join(current_content)
    return sections


def section_by_keyword(text: str, *keywords: str) -> str:
    """Return the concatenated content of sections whose heading contains any keyword.

    `parse_sections` keys keep their leading numbering (e.g. "5.状态变化"), so we
    match by keyword rather than exact name.
    """
    return "\n".join(
        val for key, val in parse_sections(text).items()
        if any(kw in key for kw in keywords)
    )


def check_state_machine(text: str, artifact_path: str = "<artifact>") -> list[dict]:
    """Check state transition completeness (parses the 状态变化 section only)."""
    issues = []
    section = section_by_keyword(text, "状态变化")
    state_rows = re.findall(
        r'\|\s*[^|]+\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|',
        section,
    )
    if not state_rows:
        issues.append(make_issue(
            severity="MEDIUM",
            check_id="state_machine.missing_table",
            family=FAMILY,
            location=artifact_path,
            field_path="sections.状态变化.table",
            message="No state transition table found in 状态变化 section",
            expected="若产物定义状态机（状态变化章节非空），必须包含 STATE × 触发事件 → 目标状态 的6列表格",
            actual="状态变化章节未匹配到任何4列以上的状态行（可能标题命名不一致或使用了纯列表）",
            repair_hint="按子模板 state-machine-output.md 的 6 列格式填写：| STATE | 状态名称 | 触发事件 | 目标状态 | 条件 | 所属 FUN |",
            source_ref="state-machine skill output-contract §状态迁移矩阵",
            blocking=False,
        ))
        return issues

    states = set()
    events = set()
    transitions = set()

    for row in state_rows:
        current = _norm(row[0])   # 状态名称
        event = _norm(row[1])     # 触发事件
        target = _norm(row[2])    # 目标状态
        if current and event and target:
            # Skip header rows
            if any(h in current for h in ['状态名称', '当前状态', 'state']):
                continue
            states.add(current)
            events.add(event)
            transitions.add((current, event))

    terminal_keywords = ['完成', '结束', '关闭', '归档', 'done', 'complete', 'closed']
    for state in states:
        if any(kw in state for kw in terminal_keywords):
            continue
        outgoing = [(s, e) for (s, e) in transitions if s == state]
        if not outgoing:
            issues.append(make_issue(
                severity="HIGH",
                check_id="state_machine.no_outgoing",
                family=FAMILY,
                location=artifact_path,
                field_path=f"sections.状态变化.states.{state}",
                message=f"State '{state}' has no outgoing transitions (non-terminal state)",
                expected=f"非终态 '{state}' 必须至少定义 1 条 触发事件→目标状态 的迁移行",
                actual=f"'{state}' 当前状态变化表格中 outgoing 迁移数 = 0",
                repair_hint=f"在 状态变化 表格为 '{state}' 增加至少一个触发事件（如「用户提交」「审批通过」「系统处理完成」「超时 N 分钟」等），并指定目标状态",
                source_ref="thinking-core.md §透镜7 穷尽性 / state-machine subskill output-contract",
            ))

    for event in events:
        incoming = [(s, e) for (s, e) in transitions if e == event]
        if not incoming:
            issues.append(make_issue(
                severity="MEDIUM",
                check_id="state_machine.event_no_incoming",
                family=FAMILY,
                location=artifact_path,
                field_path=f"sections.状态变化.events.{event}",
                message=f"Event '{event}' triggers no transitions",
                expected=f"每个在表中出现过的触发事件 '{event}' 必须至少从 1 个源状态触发迁移",
                actual=f"事件 '{event}' 在全表匹配到 0 条 incoming 迁移（可能只是目标状态的注释？）",
                repair_hint=f"若 '{event}' 是真实触发条件，请为它在表格中补充至少一行源状态；若是拼写错误或注释，请删除或修正事件名称",
                source_ref="state-machine 子技能 SKILL.md §完整性检查",
                blocking=False,
            ))

    if not issues:
        issues.append(make_issue(
            severity="INFO",
            check_id="state_machine.pass",
            family=FAMILY,
            location=artifact_path,
            message=f"State machine: {len(states)} states, {len(events)} events, {len(transitions)} transitions — appears complete",
            blocking=False,
        ))

    return issues


def check_exception_coverage(text: str, artifact_path: str = "<artifact>") -> list[dict]:
    """Check every BR exception branch has a recovery path."""
    issues = []
    exception_keywords = ['失败', '异常', '超时', '过期', '无法', '拒绝', '禁止', '冲突']
    br_rows = re.findall(
        r'\|\s*(' + _rule_id_re("BR") + r')\s*\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|',
        section_by_keyword(text, "业务规则"),
    )
    exception_brs = []
    for br_id, content, rule_type, trigger, behavior in br_rows:
        content = content.strip()
        if any(kw in content for kw in exception_keywords):
            exception_brs.append({
                "id": br_id,
                "content": content,
                "row": " | ".join(c.strip() for c in (content, rule_type, trigger, behavior)),
            })

    recovery_keywords = ['恢复', '重试', '重授权', '重新', '联系']
    ex_with_recovery: list[tuple[str, str]] = []
    for line in section_by_keyword(text, "异常").split("\n"):
        m = re.match(r'^\|\s*(EX-\d+[A-Z]?|BR-\d+[A-Z]?)\s*\|(.+)$', line.strip())
        if m and any(kw in m.group(2) for kw in recovery_keywords):
            ex_with_recovery.append((m.group(1), m.group(2)))

    for br in exception_brs:
        br_id = br["id"]
        has_recovery = (
            any(br_id in row_text for _, row_text in ex_with_recovery)
            or any(ex_id in br["row"] for ex_id, _ in ex_with_recovery)
            or any(kw in br["row"] for kw in recovery_keywords)
        )
        if not has_recovery:
            issues.append(make_issue(
                severity="HIGH",
                check_id="exception_coverage.missing_recovery",
                family=FAMILY,
                location=artifact_path,
                field_path=f"tables.业务规则.rows.{br_id}",
                message=f"BR {br_id} 规则内容含异常语义，但异常处理章节未找到 recovery path",
                expected=f"每条包含异常/失败/拒绝/超时语义的业务规则（{br_id}）必须在 异常与失败处理 章节定义对应的恢复路径（重试/回滚/联系支持/转人工 等）",
                actual=f"{br_id} 的规则内容：'{br['content'][:60]}'；未在 异常章节匹配到含 恢复/重试/重新/联系 等关键字的恢复方案；规则类型列='{br['row'].split(' | ')[1][:20]}'",
                repair_hint=f"（1）在 异常与失败处理 表格中为 {br_id} 新增 EX-xxx 行，写明恢复方式（重试 N 次？转人工？提示用户并返回草稿？）；（2）或在业务规则表格本 {br_id} 行的「预期行为」列直接声明恢复动作",
                source_ref="exception-handling subskill output-contract / thinking-core.md §透镜8 异常路径",
            ))

    if not issues:
        issues.append(make_issue(
            severity="INFO",
            check_id="exception_coverage.pass",
            family=FAMILY,
            location=artifact_path,
            message=f"Exception coverage: {len(exception_brs)} exception BRs, all have recovery paths",
            blocking=False,
        ))

    return issues


def check_vl_ac_pairing(text: str, artifact_path: str = "<artifact>") -> list[dict]:
    """Check every VL's owning FUN has a corresponding AC (VL↔AC via 所属 FUN)."""
    issues = []
    vl_section = section_by_keyword(text, "校验规则")
    ac_section = section_by_keyword(text, "验收依据")
    vl_ids = set(re.findall(_rule_id_re("VL"), vl_section))
    ac_ids = set(re.findall(_rule_id_re("AC"), ac_section))

    vl_funs = set(re.findall(r'\|\s*VL-\d+[A-Z]?\s*\|(?:[^|\n]*\|){3}\s*([^|\n]+?)\s*\|', vl_section))
    ac_funs = set(re.findall(r'\|\s*AC-\d+[A-Z]?\s*\|(?:[^|\n]*\|){3}\s*([^|\n]+?)\s*\|', ac_section))
    uncovered = {f for f in vl_funs - ac_funs if f and f != "—"}
    for fun in sorted(uncovered):
        issues.append(make_issue(
            severity="MEDIUM",
            check_id="vl_ac_pairing.uncovered_fun",
            family=FAMILY,
            location=artifact_path,
            field_path=f"tables.校验规则.FUNs.{fun}",
            message=f"FUN {fun} has validation rules (VL) but no acceptance criteria (AC)",
            expected=f"每个在 校验规则 表格中出现过的所属 FUN={fun}，必须在 验收依据 表格中有至少一行 验收标准 AC-xxx 覆盖（可验证阈值）",
            actual=f"所属 FUN '{fun}' 匹配到 VL 规则（共 {len(vl_ids)} 个 VL），但 AC 表格的所属 FUN 集合缺少 '{fun}'（当前 AC 共 {len(ac_ids)} 条）",
            repair_hint=f"在 验收依据 章节添加 AC-xxx 行，其所属 FUN 列填 '{fun}'，量化阈值列写出该功能的可验证指标（如『成功率≥99.9%』『P95 响应<200ms』『字段 XXX 必过后台校验』）",
            source_ref="acceptance-criteria subskill SKILL.md §EAR 语法",
            blocking=False,
        ))

    if not issues:
        issues.append(make_issue(
            severity="INFO",
            check_id="vl_ac_pairing.pass",
            family=FAMILY,
            location=artifact_path,
            message=f"VL↔AC pairing: {len(vl_ids)} VLs, {len(ac_ids)} ACs — all VL FUNs covered by ACs",
            blocking=False,
        ))

    return issues


def _id_fun_pairs(section: str, id_prefix: str, gap: int) -> list[tuple[str, str]]:
    """Extract (ID, FUN) pairs from a table section's 所属 FUN column.

    `gap` is the number of cells between the ID cell and the 所属 FUN cell:
      BR: | BR-X | 规则描述 | 类型 | 触发条件 | 约束/逻辑 | FUN-X | 来源 |  → gap=4
      VL: | VL-X | 校验内容 | 校验规则 | 错误提示 | FUN-X | 来源 |        → gap=3
      AC: | AC-X | 验收标准 | 量化阈值 | 来源目标 G | FUN-X | 优先级 |    → gap=3
    `[^|\n]` keeps each match on a single table row (same fix as B1), so a
    non-ID cell can never anchor across newlines.
    """
    pairs: list[tuple[str, str]] = []
    pattern = re.compile(
        r"\|\s*(" + _rule_id_re(id_prefix) + r")\s*\|(?:[^|\n]*\|){"
        + str(gap) + r"}\s*([^|\n]+?)\s*\|"
    )
    for m in pattern.finditer(section):
        fun = re.search(r"\bFUN-\d+[A-Z]?\b", m.group(2))
        if fun:
            pairs.append((m.group(1), fun.group(0)))
    return pairs


def _table_rule_density(text: str, artifact_path: str) -> list[dict]:
    """Table-based rule density for 功能清单表格 layouts (no `### FUN-XXX`)."""
    issues = []
    br_pairs = _id_fun_pairs(section_by_keyword(text, "业务规则"), "BR", 4)
    vl_pairs = _id_fun_pairs(section_by_keyword(text, "校验规则"), "VL", 3)
    ac_pairs = _id_fun_pairs(section_by_keyword(text, "验收依据"), "AC", 3)

    funs = sorted({fun for _, fun in br_pairs + vl_pairs + ac_pairs})
    if not funs:
        issues.append(make_issue(
            severity="MEDIUM",
            check_id="rule_density.no_fun_refs",
            family=FAMILY,
            location=artifact_path,
            field_path="tables.功能清单",
            message="未检测到功能子标题（### FUN-XXX）或表格中的 FUN 引用，规则密度校验跳过",
            expected="function-description 产物应至少定义 FUN-XXX 并在业务规则/校验规则/验收依据表格的 所属 FUN 列引用它",
            actual="业务规则/校验规则/验收依据 三张表全部未匹配到 FUN-XXX 引用",
            repair_hint="（1）在功能清单中为每个功能定义 FUN-xxx 编号；（2）在业务规则/校验规则/验收依据表格的 所属 FUN 列填入对应 FUN-xxx（不可留空）",
            source_ref="function-description skill §FUN/BR/VL/AC 编号规范",
            blocking=False,
        ))
        return issues

    for fun in funs:
        br_count = sum(1 for _, f in br_pairs if f == fun)
        vl_count = sum(1 for _, f in vl_pairs if f == fun)
        ac_count = sum(1 for _, f in ac_pairs if f == fun)
        total = br_count + vl_count + ac_count

        if total < 3:
            issues.append(make_issue(
                severity="HIGH",
                check_id="rule_density.underspecified",
                family=FAMILY,
                location=artifact_path,
                field_path=f"tables.rules.FUNs.{fun}",
                message=f"{fun} has only {total} rules (BR={br_count}, VL={vl_count}, AC={ac_count}) — under-specified (minimum 3)",
                expected=f"每个 FUN 至少需要 3 条 BR+VL+AC 规则合计（推荐 6 条以上，覆盖 规则/校验/验收三个维度）",
                actual=f"{fun} 当前只有 {total} 条：BR={br_count}, VL={vl_count}, AC={ac_count}",
                repair_hint=f"为 {fun} 补充规则：至少 1 条业务规则(BR) + 1 条校验规则(VL) + 1 条验收标准(AC)，合计 ≥ 3；推荐达到 6 条以通过 MEDIUM 提示",
                source_ref="thinking-core.md §透镜4 功能描述密度 / property_check §B5",
            ))
        elif total < 6:
            issues.append(make_issue(
                severity="MEDIUM",
                check_id="rule_density.consider_more",
                family=FAMILY,
                location=artifact_path,
                field_path=f"tables.rules.FUNs.{fun}",
                message=f"{fun} has {total} rules (BR={br_count}, VL={vl_count}, AC={ac_count}) — consider adding more coverage",
                expected=f"建议每个 FUN 的 BR+VL+AC 合计达到 6 条以上，确保业务规则、前后端校验、验收阈值三维度都覆盖充分",
                actual=f"{fun} 当前 {total} 条（BR={br_count}, VL={vl_count}, AC={ac_count}），低于 6 条建议阈值",
                repair_hint=f"检查 {fun} 是否遗漏以下维度：异常分支 BR、边界条件 VL、非功能指标 AC（性能/安全/可用性阈值）；各加 1 条即可达标",
                source_ref="thinking-core.md §透镜5 异常穷尽 / §透镜9 非功能约束",
                blocking=False,
            ))

    if not any(i["severity"] in {"HIGH", "MEDIUM"} for i in issues):
        issues.append(make_issue(
            severity="INFO",
            check_id="rule_density.pass_table",
            family=FAMILY,
            location=artifact_path,
            message=f"All {len(funs)} FUNs have sufficient rule density (table layout)",
            blocking=False,
        ))

    return issues


def check_rule_density(text: str, artifact_path: str = "<artifact>") -> list[dict]:
    """Check each FUN has sufficient rule coverage."""
    issues = []
    fun_blocks = re.split(r'###\s+(FUN-\d+[A-Z]?)', text)
    if len(fun_blocks) < 3:
        return _table_rule_density(text, artifact_path)

    for i in range(1, len(fun_blocks), 2):
        fun_id = fun_blocks[i]
        block = fun_blocks[i + 1] if i + 1 < len(fun_blocks) else ""
        br_count = len(re.findall(_rule_id_re("BR"), block))
        vl_count = len(re.findall(_rule_id_re("VL"), block))
        ac_count = len(re.findall(_rule_id_re("AC"), block))
        total = br_count + vl_count + ac_count

        if total < 3:
            issues.append(make_issue(
                severity="HIGH",
                check_id="rule_density.underspecified",
                family=FAMILY,
                location=artifact_path,
                field_path=f"sections.heading_blocks.{fun_id}",
                message=f"{fun_id} has only {total} rules (BR={br_count}, VL={vl_count}, AC={ac_count}) — under-specified (minimum 3)",
                expected=f"每个 ### FUN-xxx 子块至少需要 3 条 BR+VL+AC 规则合计",
                actual=f"{fun_id} 当前 {total} 条：BR={br_count}, VL={vl_count}, AC={ac_count}",
                repair_hint=f"在 ### {fun_id} 下方小节补充至少 3 条：1条业务规则(BR) + 1条校验(VL) + 1条验收(AC)",
                source_ref="thinking-core.md §透镜4 / property_check §B5",
            ))
        elif total < 6:
            issues.append(make_issue(
                severity="MEDIUM",
                check_id="rule_density.consider_more",
                family=FAMILY,
                location=artifact_path,
                field_path=f"sections.heading_blocks.{fun_id}",
                message=f"{fun_id} has {total} rules (BR={br_count}, VL={vl_count}, AC={ac_count}) — consider adding more coverage",
                expected=f"建议每个 FUN 子块 ≥6 条 BR+VL+AC 合计",
                actual=f"{fun_id} 当前 {total} 条（BR={br_count}, VL={vl_count}, AC={ac_count}）",
                repair_hint=f"为 {fun_id} 增加异常业务 BR、边界校验 VL、以及非功能 AC（性能/安全/可用性）各至少 1 条",
                source_ref="thinking-core.md §透镜5 / §透镜9",
                blocking=False,
            ))

    if not any(i["severity"] in {"HIGH", "MEDIUM"} for i in issues):
        issues.append(make_issue(
            severity="INFO",
            check_id="rule_density.pass_heading",
            family=FAMILY,
            location=artifact_path,
            message="All FUN blocks have sufficient rule density",
            blocking=False,
        ))

    return issues


def main():
    parser = argparse.ArgumentParser(description="Property-based completeness checker for function-description artifacts")
    parser.add_argument("artifact", type=Path, help="Path to function-description.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.artifact.exists():
        print(f"File not found: {args.artifact}", file=sys.stderr)
        sys.exit(2)

    text = args.artifact.read_text(encoding="utf-8")
    art_path = str(args.artifact)

    all_issues = []
    all_issues.extend(check_minimum_threshold(text, art_path))
    all_issues.extend(check_state_machine(text, art_path))
    all_issues.extend(check_exception_coverage(text, art_path))
    all_issues.extend(check_vl_ac_pairing(text, art_path))
    all_issues.extend(check_rule_density(text, art_path))

    errors = [i for i in all_issues if i.get("severity") in ("HIGH", "CRITICAL") and i.get("blocking", True)]
    warnings = [i for i in all_issues if i.get("severity") == "MEDIUM" or (i.get("severity") in ("HIGH","CRITICAL") and not i.get("blocking", True))]
    info = [i for i in all_issues if i.get("severity") == "INFO"]

    if args.json:
        from validation_errors import aggregate_by_check_id
        print(json.dumps({
            "ok": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "info": [i["message"] for i in info],
            "aggregate_by_check_id": aggregate_by_check_id([errors + warnings]),
            "total_issues_scanned": len(all_issues),
        }, ensure_ascii=False, indent=2))
    else:
        from validation_errors import format_issue
        for e in errors:
            print(f"ERROR {format_issue(e)}")
        for w in warnings:
            print(f"WARN  {format_issue(w)}")
        for i in info:
            print(f"INFO  [{i.get('check_id')}] {i['message']}")
        if not errors:
            print("✅ Property checks passed (standardized format: [check_id] location.field_path: expect vs actual (修复))")

    sys.exit(0 if len(errors) == 0 else 1)


if __name__ == "__main__":
    main()
