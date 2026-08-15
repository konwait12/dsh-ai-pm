#!/usr/bin/env python3
"""snapshot_cases.py — 案例产物快照对比（借鉴 deepseek-harness 快照测试理念）

把每个案例的产物规模（ST/FEA/FUN/BR/AC/EX/EV/IX/SRC/状态）录制为基线快照，
`--check` 时与当前扫描对比，输出差异。用途：
  1. 案例跑测后机器化「结果比对」（新增/膨胀/收缩/状态漂移一目了然）
  2. 回归时发现「产物意外变化」（对应 DSH 快照测试的定位：
     "green unit tests, broken product" 类问题只有快照能抓）

用法:
  python3 src/scripts/snapshot_cases.py --record   # 录制/更新基线
  python3 src/scripts/snapshot_cases.py --check    # 对比基线（exit 1 有差异）
  python3 src/scripts/snapshot_cases.py            # 仅打印当前统计

基线位置: 99-review/产物快照.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path('99-review/产物快照.json')


def status_of(p: Path) -> str:
    if not p.is_file():
        return '-'
    m = re.search(r'^status:\s*(\S+)', p.read_text(encoding='utf-8'), re.MULTILINE)
    return m.group(1) if m else '?'


def ids_of(p: Path, pattern: str) -> int:
    if not p.is_file():
        return 0
    return len(set(re.findall(pattern, p.read_text(encoding='utf-8'))))


def scan_case(d: Path) -> dict:
    journey = d / '001-business-requirements/02-user-journey-stories/journey-and-stories.md'
    bg = d / '001-business-requirements/01-background-goal/background-goal.md'
    ux = d / '002-product-requirements/01-product-ux/product-ux.md'
    fd = d / '002-product-requirements/02-function-description/function-description.md'
    prd = d / '003-prd-output/prd.md'
    tp = d / '99-review/support/tracking-plan.md'
    return {
        'statuses': {
            'BG': status_of(bg), 'JS': status_of(journey), 'UX': status_of(ux),
            'FD': status_of(fd), 'PRD': status_of(prd),
        },
        'counts': {
            'ST': ids_of(journey, r'\bST-\d+\b'),
            'FEA': ids_of(fd, r'\bFEA-\d+\b'),
            'FUN': ids_of(fd, r'\bFUN-\d+\b'),
            'BR': ids_of(fd, r'\bBR-\d+\b'),
            'AC': ids_of(fd, r'\bAC-\d+\b'),
            'EX': ids_of(fd, r'\bEX-\d+\b'),
            'EV': ids_of(tp, r'\bEV-\d+\b'),
            'IX': ids_of(ux, r'\bIX-\d+\b'),
            'SRC': len(list((d / '00-input').glob('SRC-*'))) if (d / '00-input').is_dir() else 0,
        },
    }


def scan_all() -> dict[str, dict]:
    result = {}
    for d in sorted(Path('requirements').glob('REQ-*')):
        if d.is_dir():
            result[d.name] = scan_case(d)
    return result


def render(current: dict) -> str:
    lines = []
    for case in sorted(current):
        c = current[case]
        sts = '/'.join(c['statuses'][k][:6] for k in ('BG', 'JS', 'UX', 'FD', 'PRD'))
        cnt = c['counts']
        lines.append(
            f"{case:<24}{sts:<32}"
            f"ST={cnt['ST']:>3} FEA={cnt['FEA']:>3} FUN={cnt['FUN']:>3} "
            f"BR={cnt['BR']:>3} AC={cnt['AC']:>3} EX={cnt['EX']:>3} "
            f"EV={cnt['EV']:>3} IX={cnt['IX']:>3} SRC={cnt['SRC']:>2}")
    return '\n'.join(lines)


def diff(base: dict, current: dict) -> list[str]:
    out = []
    for case in sorted(set(base) | set(current)):
        if case not in base:
            out.append(f'➕ 新案例 {case}')
            continue
        if case not in current:
            out.append(f'➖ 案例消失 {case}')
            continue
        b, c = base[case], current[case]
        if b['statuses'] != c['statuses']:
            for k in b['statuses']:
                if b['statuses'][k] != c['statuses'][k]:
                    out.append(f'🔁 {case} {k} 状态: {b["statuses"][k]} → {c["statuses"][k]}')
        for k in sorted(set(b['counts']) | set(c['counts'])):
            bv, cv = b['counts'].get(k, 0), c['counts'].get(k, 0)
            if bv != cv:
                delta = cv - bv
                out.append(f'{"📈" if delta > 0 else "📉"} {case} {k}: {bv} → {cv} ({delta:+d})')
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--record', action='store_true', help='录制/更新基线快照')
    parser.add_argument('--check', action='store_true', help='与基线对比（有差异时 exit 1）')
    args = parser.parse_args()

    current = scan_all()
    if args.record:
        BASE.parent.mkdir(parents=True, exist_ok=True)
        BASE.write_text(json.dumps(current, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'✅ 基线已录制: {BASE}（{len(current)} 案例）')
        print(render(current))
        return 0

    if args.check:
        if not BASE.is_file():
            print(f'⚠ 基线不存在，请先 --record: {BASE}', file=sys.stderr)
            return 2
        base = json.loads(BASE.read_text(encoding='utf-8'))
        diffs = diff(base, current)
        if diffs:
            print('❌ 快照差异：')
            for line in diffs:
                print('  ' + line)
            return 1
        print('✅ 快照一致（无差异）')
        return 0

    print(render(current))
    return 0


if __name__ == '__main__':
    sys.exit(main())
