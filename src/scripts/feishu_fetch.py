#!/usr/bin/env python3
"""feishu_fetch.py — 飞书 CLI 材料提取脚本（项目内置，以飞书为主链路）

从飞书文档提取原始需求材料到 requirements/REQ-XXX/00-input/：
  1. 调用 lark-cli docs +fetch 读取文档（markdown 格式）
  2. 清洗：HTML 表格 → Markdown 表格（处理 colspan/rowspan、h8 等 wiki 标签）、
     callout → 引用块、synced_reference/grid/whiteboard/img → 移除并警告、
     cite/a → 链接文本
  3. 脱敏：账号/密码模式替换为 <REDACTED>，长 token 打码
  4. 输出材料文件 + 可选 --register 自动登记 source-register.md

用法:
  python3 src/scripts/feishu_fetch.py <doc-token|url> --output <path.md> [--register] [--register-dir <dir>] [--src-id SRC-001] [--src-title "标题"] [--feishu-domain <domain>]

示例:
  python3 src/scripts/feishu_fetch.py <doc-token> \
    --output requirements/REQ-NNN-<topic>/00-input/SRC-001-<topic>-brd.md \
    --register --src-id SRC-001 --src-title "<src-title>"

依赖: lark-cli 已安装并认证（lark-cli auth status 见 README/04 资源库）。
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# ── 脱敏模式库 ─────────────────────────────────────────────
SECRET_PATTERNS = [
    # 账号/密码类（中英文冒号）
    (re.compile(r'((?:密码|账号|口令|password|Password|account)\s*[:：]\s*)(\S+)'), r'\1<REDACTED>'),
    # 疑似长 token / 密钥（30+ 位字母数字混合）
    (re.compile(r'\b([A-Za-z0-9_-]{30,})\b'), '<REDACTED>'),
    # URL 中内嵌凭据（https://user:pass@host）
    (re.compile(r'(https?://)([^/@\s]+):([^/@\s]+)@'), r'\1<REDACTED>:<REDACTED>@'),
]

KNOWN_EMPTY_BLOCKS = ('whiteboard', 'grid', 'synced_reference', 'img')
DEFAULT_FEISHU_DOMAIN = 'ccegroup.feishu.cn'


def run_lark_fetch(token: str) -> dict:
    """调用 lark-cli 读取文档，返回解析后的 JSON。"""
    cmd = ['lark-cli', 'docs', '+fetch', '--doc', token,
           '--doc-format', 'markdown', '--scope', 'full']
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f'lark-cli 失败: {proc.stderr[:500]}')
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'lark-cli 输出非 JSON: {exc}\n{proc.stdout[:300]}') from exc


def cell_text(cell: str) -> str:
    """单元格：<br> 转空格、去标签、HTML 反转义。

    标签匹配限定为真正的 HTML 标签（<字母 / </字母 / <!），避免表格文本
    中的 "<" 字符（如交互规则「用户点击"<"返回」）被误认为标签起始而
    吞掉后续内容（OBS-002 根因）。"""
    t = re.sub(r'<br\s*/?>', ' ', cell)
    t = re.sub(r'<[/!]?[a-zA-Z][^>]*>', '', t)
    return html.unescape(t).strip()


def table_to_md(tbl: str) -> str:
    """HTML <table> → Markdown 表格。

    colspan 的单元格输出为空占位（信息已由原单元格覆盖），rowspan 同理；
    表头取首个 <tr>；无行时返回空串（调用方跳过）。
    """
    rows = re.findall(r'<tr>(.*?)</tr>', tbl, re.DOTALL)
    md_rows: list[str] = []
    for r in rows:
        cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r, re.DOTALL)
        md_rows.append('| ' + ' | '.join(cell_text(c) for c in cells) + ' |')
    if not md_rows:
        return ''
    header = md_rows[0]
    sep = '|' + '---|' * (header.count('|') - 1)
    return header + '\n' + sep + '\n' + '\n'.join(md_rows[1:])


def sanitize(raw: str) -> tuple[str, list[str]]:
    """清洗 + 脱敏。返回 (文本, 警告列表)。"""
    warnings: list[str] = []

    # 1. 表格转换（先于通用标签清理，保留结构）
    raw = re.sub(r'<table>.*?</table>', lambda m: table_to_md(m.group(0)), raw,
                 flags=re.DOTALL)

    # 2. wiki 特有块：callout → 引用；其余已知空块移除并警告
    raw = re.sub(r'<callout[^>]*>(.*?)</callout>',
                 lambda m: '> 💡 ' + cell_text(m.group(1)), raw, flags=re.DOTALL)
    for kind in KNOWN_EMPTY_BLOCKS:
        before = raw
        raw = re.sub(rf'<{kind}[^>]*>.*?</{kind}>', '', raw, flags=re.DOTALL)
        raw = re.sub(rf'<{kind}[^>]*/>', '', raw)
        if len(raw) < len(before):
            warnings.append(f'移除 {kind} 块（无法转文本）')

    # 3. cite / 链接
    raw = re.sub(r'<cite[^>]*title="([^"]*)"[^>]*>.*?</cite>', r'[\1]', raw, flags=re.DOTALL)
    raw = re.sub(r'<cite[^>]*>.*?</cite>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', raw, flags=re.DOTALL)

    # 4. 剩余标签与空白（限定真标签，避免文本内 "<" 字符误删）
    raw = re.sub(r'<[/!]?[a-zA-Z][^>]*>', '', raw)
    raw = html.unescape(raw)
    raw = re.sub(r'\n{3,}', '\n\n', raw)
    raw = re.sub(r'[ \t]+\n', '\n', raw)

    # 5. 脱敏
    for pattern, repl in SECRET_PATTERNS:
        raw, n = pattern.subn(repl, raw)
        if n > 0:
            warnings.append(f'脱敏替换 {n} 处（{pattern.pattern[:40]}…）')
    return raw, warnings


def build_header(src_id: str, title: str, token: str) -> str:
    return (f'# {title}（{src_id}）\n\n'
            f'> 来源：飞书文档（doc-id: {token}），经 lark-cli 提取。\n'
            f'> 提取日期：{date.today().isoformat()}，由 `src/scripts/feishu_fetch.py` 生成；'
            f'账号密码等敏感信息已脱敏为 <REDACTED>。\n'
            f'> 测试线说明：本材料为真实 BRD 提取整理，用于脚手架全流程跑测。\n\n---\n\n')


def update_source_register(register_path: Path, src_id: str, title: str, token: str,
                           out_rel: str, feishu_domain: str = DEFAULT_FEISHU_DOMAIN) -> None:
    """在 source-register.md 的表格追加一行（存在表头则复用，否则新建）。"""
    line = (f'| {src_id} | 飞书文档（BRD） | `{out_rel}`'
            f'（原文：https://{feishu_domain}/docx/{token}） | {title} | '
            f'{date.today().isoformat()} | 全流程 |\n')
    if register_path.is_file():
        text = register_path.read_text(encoding='utf-8')
        if '|---' in text and src_id not in text:
            # 追加到表尾：从后往前找最后一个「以 | 开头」的行插到它后面——
            # 是数据行则为真正的表尾；若只有表头+分隔行（无数据行），则插到分隔行后。
            lines = text.splitlines()
            insert_idx = None
            for idx in range(len(lines) - 1, -1, -1):
                if lines[idx].lstrip().startswith('|'):
                    insert_idx = idx + 1
                    break
            if insert_idx is not None:
                lines.insert(insert_idx, line.rstrip('\n'))
                register_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        else:
            register_path.write_text(text + line, encoding='utf-8')
    else:
        register_path.write_text(
            '# 来源登记 (Source Register)\n\n'
            '> 登记所有原始需求材料。格式: SRC-NNN → 材料位置 / URL / 飞书链接\n\n'
            '| 来源 ID | 类型 | 位置 | 摘要 | 登记日期 | 权威范围 |\n'
            '|---|---|---|---|---|---|\n' + line, encoding='utf-8')


def find_requirements_parent(path: Path) -> Path | None:
    """返回路径上方第一个名为 requirements 的目录；没有则返回 None。"""
    return next((parent for parent in path.parents if parent.name == 'requirements'), None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('token', help='飞书文档 token 或 URL（/docx/ 与 /wiki/ 均可）')
    parser.add_argument('--output', required=True, help='输出材料文件路径')
    parser.add_argument('--register', action='store_true', help='同步更新 source-register.md')
    parser.add_argument('--register-dir', type=Path, default=None,
                        help='登记目录（默认从 --output 向上查找 requirements）')
    parser.add_argument('--src-id', default='SRC-001', help='来源 ID（默认 SRC-001）')
    parser.add_argument('--src-title', default='飞书需求文档', help='材料标题')
    parser.add_argument('--feishu-domain', default=DEFAULT_FEISHU_DOMAIN,
                        help=f'飞书域名（默认 {DEFAULT_FEISHU_DOMAIN}）')
    args = parser.parse_args()
    if not args.register and args.register_dir is not None:
        parser.error('--register-dir requires --register')

    token = args.token.rsplit('/', 1)[-1]
    result = run_lark_fetch(token)
    if not result.get('ok'):
        print(f"提取失败: {result.get('error', '未知错误')}", file=sys.stderr)
        return 1
    content = result['data']['document']['content']

    text, warnings = sanitize(content)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_header(args.src_id, args.src_title, token) + text, encoding='utf-8')

    print(f'✅ 已写入 {out}（{len(text)} 字符）')
    for w in warnings:
        print(f'  ⚠ {w}')

    if args.register:
        requirements_parent = find_requirements_parent(out)
        if args.register_dir is not None:
            register = args.register_dir / 'source-register.md'
        else:
            register = out.parent / 'source-register.md'
        relative_root = requirements_parent or args.register_dir or out.parent

        try:
            out_rel = out.relative_to(relative_root)
        except ValueError:
            out_rel = Path(out.name)
        register.parent.mkdir(parents=True, exist_ok=True)
        update_source_register(register, args.src_id, args.src_title, token,
                               str(out_rel), args.feishu_domain)
        print(f'✅ source-register 已更新：{register}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
