#!/usr/bin/env python3
"""prd_publish.py — 飞书 PRD 发布脚本（项目内置，以飞书为主闭环）

把生成好的 PRD 产物（或任意交付文档）发布为飞书文档，返回 doc-id，
并登记到产物 frontmatter（feishu_doc_id）与 99-review/飞书发布日志。

闭环：飞书取材料（feishu_fetch.py）→ 本地生成产物 → 飞书发布（本脚本）。

用法:
  python3 src/scripts/prd_publish.py <prd.md 路径> [--title 标题] [--note 备注] [--feishu-domain <domain>] [--log-path <path>] [--title-template <template>] [--no-title-template] [--dry-run]

示例:
  python3 src/scripts/prd_publish.py requirements/REQ-NNN-<topic>/003-prd-output/prd.md
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from workflow_registry import read_frontmatter

DEFAULT_FEISHU_DOMAIN = 'ccegroup.feishu.cn'
DEFAULT_TITLE_TEMPLATE = '[PM Scaffold] {case} {artifact_id} v{version}'
LOG_PATH = Path('99-review/飞书发布日志.md')


def run_lark(args: list[str], input_text: str | None = None) -> dict:
    proc = subprocess.run(['lark-cli', *args], input=input_text,
                          capture_output=True, text=True, timeout=120,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f'lark-cli 失败: {proc.stderr[:500]}')
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'lark-cli 输出非 JSON: {exc}\n{proc.stdout[:300]}') from exc


def upsert_frontmatter_field(path: Path, key: str, value: str) -> None:
    text = path.read_text(encoding='utf-8')
    m = re.match(r'(\A---\s*\n)(.*?)(\n---\s*\n)', text, re.DOTALL)
    if not m:
        return
    body = m.group(2)
    if re.search(rf'^{key}:', body, re.MULTILINE):
        body = re.sub(rf'^{key}:.*$', f'{key}: {value}', body, flags=re.MULTILINE)
    else:
        body = body + f'\n{key}: {value}'
    path.write_text(m.group(1) + body + m.group(3), encoding='utf-8')


def append_log(entry: dict, log_path: Path = LOG_PATH) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = (f"| {entry['time']} | {entry['case']} | {entry['artifact']} | "
            f"{entry['title']} | {entry['doc_id']} | {entry.get('note', '—')} |\n")
    if log_path.is_file():
        text = log_path.read_text(encoding='utf-8')
        if '|---' in text:
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
                log_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        else:
            log_path.write_text(text + line, encoding='utf-8')
    else:
        log_path.write_text(
            '# 飞书发布日志\n\n> 记录通过 prd_publish.py 发布到飞书的文档。\n\n'
            '| 时间 | 案例 | 产物 | 标题 | 飞书 doc-id | 备注 |\n'
            '|---|---|---|---|---|---|\n' + line, encoding='utf-8')


def find_requirements_parent(path: Path) -> Path | None:
    """返回路径上方第一个名为 requirements 的目录；没有则返回 None。"""
    return next((parent for parent in path.parents if parent.name == 'requirements'), None)


def infer_case(artifact: Path) -> str:
    """从 requirements/<case>/... 推导案例名，否则使用产物父目录名。"""
    requirements_parent = find_requirements_parent(artifact)
    if requirements_parent is not None:
        relative = artifact.relative_to(requirements_parent)
        if len(relative.parts) > 1:
            return relative.parts[0]
    return artifact.parent.name


def render_title(template: str, case: str, artifact_id: str, version: str,
                 artifact_path: Path) -> str:
    values = {
        'case': case,
        'artifact_id': artifact_id,
        'version': version,
        'path': str(artifact_path),
    }
    return template.format_map(values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('artifact', type=Path, help='要发布的 Markdown 产物路径')
    parser.add_argument('--title', default=None, help='飞书文档标题（默认使用标题模板）')
    parser.add_argument('--note', default='', help='备注（追加到日志）')
    parser.add_argument('--feishu-domain', default=DEFAULT_FEISHU_DOMAIN,
                        help=f'飞书域名（默认 {DEFAULT_FEISHU_DOMAIN}）')
    parser.add_argument('--log-path', type=Path, default=LOG_PATH,
                        help=f'发布日志路径（默认 {LOG_PATH}）')
    parser.add_argument('--title-template', default=DEFAULT_TITLE_TEMPLATE,
                        help=('标题模板（占位符: {case} {artifact_id} {version} {path}；'
                              f'默认 {DEFAULT_TITLE_TEMPLATE}）'))
    parser.add_argument('--no-title-template', action='store_true',
                        help='使用 --title 原样作为标题')
    parser.add_argument('--dry-run', action='store_true',
                        help='只打印将要发布的标题和路径，不调用 lark-cli')
    args = parser.parse_args()

    artifact = args.artifact.resolve()
    if not artifact.is_file():
        print(f'文件不存在: {artifact}', file=sys.stderr)
        return 1

    fm = read_frontmatter(artifact)
    case = infer_case(artifact)
    ver = fm.get('version', '?').lstrip('v')
    artifact_id = fm.get('artifact_id', 'PRD')
    if args.no_title_template:
        title = args.title or ''
    else:
        title = args.title or render_title(
            args.title_template, case, artifact_id, ver, artifact)

    if args.dry_run:
        print(f'[DRY-RUN] title: {title}')
        print(f'[DRY-RUN] path: {artifact}')
        return 0

    # 读取内容并发布（markdown 格式，经 stdin 传入避免 --content 多行被当 flag）
    content = artifact.read_text(encoding='utf-8')
    result = run_lark(['docs', '+create', '--title', title, '--doc-format', 'markdown'], content)
    if not result.get('ok'):
        print(f"发布失败: {result.get('error', '未知错误')}", file=sys.stderr)
        return 1

    doc = result.get('data', {}).get('document', {})
    doc_id = doc.get('document_id') or doc.get('doc_id') or '?'
    url = f'https://{args.feishu_domain}/docx/{doc_id}'

    # 登记：frontmatter feishu_doc_id + 发布日志
    upsert_frontmatter_field(artifact, 'feishu_doc_id', doc_id)
    append_log({
        'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'case': case,
        'artifact': artifact.name,
        'title': title,
        'doc_id': doc_id,
        'note': args.note,
    }, args.log_path)
    print(f'✅ 已发布到飞书: {url}')
    print(f'   doc-id: {doc_id}（已写入产物 frontmatter feishu_doc_id + 发布日志）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
