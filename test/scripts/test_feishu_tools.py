#!/usr/bin/env python3

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "src/scripts"
sys.path.insert(0, str(SCRIPTS))

import feishu_fetch
import prd_publish


class FeishuToolTest(unittest.TestCase):
    def test_feishu_fetch_help_exposes_domain_and_register_options(self) -> None:
        result = __import__('subprocess').run(
            [sys.executable, str(SCRIPTS / 'feishu_fetch.py'), '--help'],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8", errors="replace",
        )
        for option in ('--feishu-domain', '--register-dir'):
            self.assertIn(option, result.stdout)

    def test_feishu_fetch_register_uses_output_parent_and_custom_domain(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / 'materials' / 'SRC.md'
            with mock.patch.object(
                feishu_fetch,
                'run_lark_fetch',
                return_value={
                    'ok': True,
                    'data': {'document': {'content': '<p>body</p>'}},
                },
            ):
                with mock.patch.object(sys, 'argv', [
                    str(SCRIPTS / 'feishu_fetch.py'), '<doc-token>',
                    '--output', str(output), '--register',
                    '--feishu-domain', 'example.feishu.cn',
                ]):
                    self.assertEqual(feishu_fetch.main(), 0)

            register = output.parent / 'source-register.md'
            text = register.read_text(encoding='utf-8')
            self.assertIn('https://example.feishu.cn/docx/<doc-token>', text)
            self.assertIn('`SRC.md`', text)

    def test_feishu_fetch_register_uses_requirements_ancestor_for_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / 'requirements' / 'REQ-001-rsvp' / '00-input' / 'SRC.md'
            with mock.patch.object(
                feishu_fetch,
                'run_lark_fetch',
                return_value={
                    'ok': True,
                    'data': {'document': {'content': 'body'}},
                },
            ):
                with mock.patch.object(sys, 'argv', [
                    str(SCRIPTS / 'feishu_fetch.py'), '<doc-token>',
                    '--output', str(output), '--register',
                ]):
                    self.assertEqual(feishu_fetch.main(), 0)

            register = output.parent / 'source-register.md'
            text = register.read_text(encoding='utf-8')
            self.assertIn('`REQ-001-rsvp/00-input/SRC.md`', text)

    def test_feishu_fetch_register_dir_requires_register(self) -> None:
        with mock.patch.object(sys, 'argv', [
            str(SCRIPTS / 'feishu_fetch.py'), '<doc-token>', '--output', '<output-path>',
            '--register-dir', '<register-dir>',
        ]):
            with self.assertRaises(SystemExit) as raised:
                feishu_fetch.main()
        self.assertEqual(raised.exception.code, 2)

    def test_feishu_fetch_register_dir_overrides_default_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / 'materials' / 'SRC.md'
            register_dir = root / 'registers'
            with mock.patch.object(
                feishu_fetch,
                'run_lark_fetch',
                return_value={
                    'ok': True,
                    'data': {'document': {'content': 'body'}},
                },
            ):
                with mock.patch.object(sys, 'argv', [
                    str(SCRIPTS / 'feishu_fetch.py'), '<doc-token>',
                    '--output', str(output), '--register', '--register-dir', str(register_dir),
                ]):
                    self.assertEqual(feishu_fetch.main(), 0)

            self.assertTrue((register_dir / 'source-register.md').is_file())
            self.assertFalse((output.parent / 'source-register.md').exists())

    def test_frontmatter_parser_keeps_available_fields_when_other_keys_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / 'artifact.md'
            artifact.write_text(
                '---\nartifact_id: PRD-001\nversion: v0.2\n'
                'metadata:\n  owner: "PM"\n---\nbody\n',
                encoding='utf-8',
            )
            fm = prd_publish.read_frontmatter(artifact)
            self.assertEqual(fm['artifact_id'], 'PRD-001')
            self.assertEqual(fm['version'], 'v0.2')
            # 复用 workflow_registry 权威实现：缩进嵌套键会被扁平化解析为顶层字段
            self.assertEqual(fm.get('owner'), 'PM')
            self.assertIsNone(fm.get('missing_key'))

    def test_prd_publish_help_exposes_new_options(self) -> None:
        result = __import__('subprocess').run(
            [sys.executable, str(SCRIPTS / 'prd_publish.py'), '--help'],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8", errors="replace",
        )
        for option in (
            '--feishu-domain', '--log-path', '--title-template',
            '--no-title-template', '--dry-run',
        ):
            self.assertIn(option, result.stdout)

    def test_prd_publish_dry_run_prints_title_and_path_without_lark_call(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / 'requirements' / 'REQ-001-rsvp' / '003-prd-output' / 'prd.md'
            artifact.parent.mkdir(parents=True)
            artifact.write_text(
                '---\nartifact_id: PRD-001\nversion: v0.1\n'
                'metadata:\n  owner: "PM"\n---\nbody\n',
                encoding='utf-8',
            )
            stdout = io.StringIO()
            with mock.patch.object(prd_publish, 'run_lark', return_value={'ok': False}) as run_lark:
                with contextlib.redirect_stdout(stdout):
                    with mock.patch.object(sys, 'argv', [
                        str(SCRIPTS / 'prd_publish.py'), str(artifact), '--dry-run',
                    ]):
                        self.assertEqual(prd_publish.main(), 0)
            run_lark.assert_not_called()
            self.assertIn('title:', stdout.getvalue())
            self.assertIn(str(artifact), stdout.getvalue())
            self.assertIn('[PM Scaffold] REQ-001-rsvp PRD-001 v0.1', stdout.getvalue())
            self.assertNotIn('feishu_doc_id', artifact.read_text(encoding='utf-8'))

    def test_prd_publish_no_title_template_keeps_title_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / 'standalone' / 'prd.md'
            artifact.parent.mkdir(parents=True)
            artifact.write_text('---\nversion: v0.1\n---\nbody\n', encoding='utf-8')
            stdout = io.StringIO()
            with mock.patch.object(prd_publish, 'run_lark') as run_lark:
                with contextlib.redirect_stdout(stdout):
                    with mock.patch.object(sys, 'argv', [
                        str(SCRIPTS / 'prd_publish.py'), str(artifact),
                        '--title', 'Raw Title', '--no-title-template', '--dry-run',
                    ]):
                        self.assertEqual(prd_publish.main(), 0)
            run_lark.assert_not_called()
            self.assertIn('title: Raw Title', stdout.getvalue())
            self.assertNotIn('[PM Scaffold]', stdout.getvalue())

    def test_prd_publish_case_falls_back_to_parent_outside_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / 'standalone' / 'release' / 'prd.md'
            artifact.parent.mkdir(parents=True)
            artifact.write_text('---\nartifact_id: PRD-001\nversion: v0.1\n---\nbody\n', encoding='utf-8')
            stdout = io.StringIO()
            with mock.patch.object(prd_publish, 'run_lark') as run_lark:
                with contextlib.redirect_stdout(stdout):
                    with mock.patch.object(sys, 'argv', [
                        str(SCRIPTS / 'prd_publish.py'), str(artifact), '--dry-run',
                    ]):
                        self.assertEqual(prd_publish.main(), 0)
            run_lark.assert_not_called()
            self.assertIn('[PM Scaffold] release PRD-001 v0.1', stdout.getvalue())

    def test_prd_publish_uses_custom_domain_log_path_and_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / 'requirements' / 'REQ-001-rsvp' / '003-prd-output' / 'prd.md'
            artifact.parent.mkdir(parents=True)
            artifact.write_text('---\nartifact_id: PRD-001\nversion: v0.1\n---\nbody\n', encoding='utf-8')
            log_path = root / 'publish-log.md'
            stdout = io.StringIO()
            result = {'ok': True, 'data': {'document': {'document_id': 'doc-001'}}}
            with mock.patch.object(prd_publish, 'run_lark', return_value=result) as run_lark:
                with contextlib.redirect_stdout(stdout):
                    with mock.patch.object(sys, 'argv', [
                        str(SCRIPTS / 'prd_publish.py'), str(artifact),
                        '--feishu-domain', 'example.feishu.cn', '--log-path', str(log_path),
                        '--title-template', '{path}',
                    ]):
                        self.assertEqual(prd_publish.main(), 0)
            run_lark.assert_called_once()
            self.assertIn('example.feishu.cn', stdout.getvalue())
            self.assertEqual(
                str(artifact.resolve()),
                run_lark.call_args.args[0][run_lark.call_args.args[0].index('--title') + 1],
            )
            self.assertIn(str(artifact), log_path.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
