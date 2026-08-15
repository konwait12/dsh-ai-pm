#!/usr/bin/env python3
"""Regression tests for OBS-004 / OBS-005 in property_check.py.

OBS-004: exception coverage must judge exception semantics from the BR 规则内容
column (col 2), not the 类型 column (col 3) — a BR whose 类型 says 异常 but whose
content has no exception keyword must NOT be flagged, while content containing
失败/异常/拒绝 must be (recovery check applies, with both BR→EX and EX→BR links).

OBS-005: rule IDs may carry an optional single-letter suffix (BR-006A); density /
pairing checks must count them instead of silently skipping.

Discovered by run_tests_mac.sh via `find test -name 'test_*.py'`.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "src/scripts"
sys.path.insert(0, str(SCRIPTS))

import property_check


def _fd(br_rows: str, ex_rows: str = "") -> str:
    """Assemble a minimal function-description snippet with BR / EX tables."""
    parts = [
        "# function-description 测试",
        "## 3. 业务规则（business-rules 子 skill 产出）",
        "| BR ID | 规则内容 | 类型 | 触发条件 | 预期行为 | 所属功能 | 来源 |",
        "|---|---|---|---|---|---|---|",
        br_rows.strip("\n"),
    ]
    if ex_rows.strip():
        parts += [
            "## 6. 异常与失败处理（exception-handling 子 skill 产出）",
            "| EX ID | 异常场景 | 触发条件 | 系统行为 | 用户操作 | 恢复方式 | 所属功能 |",
            "|---|---|---|---|---|---|---|",
            ex_rows.strip("\n"),
        ]
    return "\n".join(parts)


class ExceptionCoverageTest(unittest.TestCase):
    def _high(self, text: str) -> list[str]:
        return [i["message"] for i in property_check.check_exception_coverage(text)
                if i["severity"] in ("HIGH", "CRITICAL")]

    def test_type_column_alone_is_not_an_exception(self) -> None:
        # OBS-004: 类型列=异常, but 规则内容 has no exception semantics → no flag.
        text = _fd("| BR-012 | 海报保存正常流程 | 异常 | 用户点保存 | 生成海报并下载 | FUN-004 | SRC-001 |\n"
                   "| BR-013 | 评论内容展示 | 展示 | 进入详情页 | 展示评论列表 | FUN-008 | SRC-001 |")
        self.assertEqual(self._high(text), [])

    def test_content_failure_without_recovery_is_flagged(self) -> None:
        # OBS-004: 规则内容 contains 失败 and no recovery anywhere → HIGH.
        text = _fd("| BR-012 | 海报保存失败处理 | 规则 | 保存海报失败 | 网络繁忙→保存失败提示 | FUN-004 | SRC-001 |\n"
                   "| BR-013 | 评论内容展示 | 展示 | 进入详情页 | 展示评论列表 | FUN-008 | SRC-001 |",
                   "| EX-001 | 订阅通知失败 | 网络繁忙 | 订阅失败提示 | 重新订阅 | 再次点击订阅 | FUN-005 |")
        high = self._high(text)
        self.assertEqual(len(high), 1)
        self.assertIn("BR-012", high[0])

    def test_recovery_via_ex_cited_in_br_row(self) -> None:
        # OBS-004: BR row 预期行为 cites EX-001 which has a recovery (REQ-007 BR-012 case).
        text = _fd("| BR-012 | 海报保存失败处理 | 规则 | 保存海报失败 | 网络繁忙→保存失败提示（异常详情见 EX-001） | FUN-004 | SRC-001 |\n"
                   "| BR-013 | 评论内容展示 | 展示 | 进入详情页 | 展示评论列表 | FUN-008 | SRC-001 |",
                   "| EX-001 | 海报保存失败 | 网络繁忙 | 保存失败提示 | 重试 | 重新保存 | FUN-004 |")
        self.assertEqual(self._high(text), [])

    def test_recovery_via_ex_row_citing_br(self) -> None:
        # OBS-004: EX row 触发条件 cites the BR id and has a recovery (REQ-005 pattern).
        text = _fd("| BR-009 | 当日已有预约校验 | 校验 | 提交预约 | 已存在则失败并弹窗 | FUN-004 | SRC-001 |\n"
                   "| BR-013 | 评论内容展示 | 展示 | 进入详情页 | 展示评论列表 | FUN-008 | SRC-001 |",
                   "| EX-001 | 当日已有预约 | 提交时当日已有预约（BR-009） | 弹窗提示 | 重新选择其他日期 | 停留创建预约页 | FUN-004 |")
        self.assertEqual(self._high(text), [])

    def test_content_no_keyword_not_flagged_even_with_recovery_absent(self) -> None:
        # OBS-004: content without exception keywords never triggers the check.
        text = _fd("| BR-007 | 不同服务类型可配置不同店铺列表与场次 | 规则 | 配置服务 | 按类型展示 | FUN-001 | SRC-001 |")
        self.assertEqual(self._high(text), [])


class RuleDensitySuffixTest(unittest.TestCase):
    def test_id_fun_pairs_extracts_suffixed_br(self) -> None:
        # OBS-005: BR-006A must be extracted and mapped to its FUN.
        text = _fd("| BR-006A | 播放控制 | 交互 | 视频播放 | 支持播放/暂停/全屏 | FUN-003 | SRC-001 |\n"
                   "| BR-007 | 分享方式 | 规则 | 用户分享 | 分享卡片 | FUN-004 | SRC-001 |")
        pairs = property_check._id_fun_pairs(
            property_check.section_by_keyword(text, "业务规则"), "BR", 4)
        self.assertIn(("BR-006A", "FUN-003"), pairs)

    def test_suffixed_br_counts_towards_density(self) -> None:
        # OBS-005: BR-006A + VL-001 + AC-001 = 3 rules → no HIGH under-specified.
        text = "\n".join([
            _fd("| BR-006A | 播放控制 | 交互 | 视频播放 | 支持播放/暂停/全屏 | FUN-001 | SRC-001 |"),
            "## 4. 校验规则与字段定义（validation-rules 子 skill 产出）",
            "| VL ID | 校验内容 | 校验规则 | 错误提示 | 所属功能 | 来源 |",
            "|---|---|---|---|---|---|",
            "| VL-001 | 播放权限 | 校验播放权限 | 无权限提示 | FUN-001 | SRC-001 |",
            "## 7. 验收依据（acceptance-criteria 子 skill 产出）",
            "| AC ID | 验收标准（Given/When/Then） | 覆盖率目标 | 优先级 | 所属功能 | 功能优先级 |",
            "|---|---|---|---|---|---|",
            "| AC-001 | Given 用户播放视频, when 点击播放, then 正常播放 | 100% | G1 | FUN-001 | P0 |",
        ])
        issues = property_check.check_rule_density(text)
        high = [i for i in issues if i["severity"] in ("HIGH", "CRITICAL")]
        self.assertEqual(high, [])
        messages = [i["message"] for i in issues]
        self.assertTrue(any("BR=1" in m for m in messages))

    def test_plain_numeric_ids_still_counted(self) -> None:
        # OBS-005: regression guard — plain BR-007 still extracted.
        text = _fd("| BR-007 | 分享方式 | 规则 | 用户分享 | 分享卡片 | FUN-004 | SRC-001 |")
        pairs = property_check._id_fun_pairs(
            property_check.section_by_keyword(text, "业务规则"), "BR", 4)
        self.assertIn(("BR-007", "FUN-004"), pairs)


class MinimumThresholdTest(unittest.TestCase):
    """B11: empty / section-less artifacts must not silent-pass the gate."""

    def _critical(self, text: str) -> list[str]:
        return [i["message"] for i in property_check.check_minimum_threshold(text)
                if i["severity"] in ("HIGH", "CRITICAL")]

    def test_empty_text_is_rejected(self) -> None:
        # B11: an empty artifact must be flagged as an error, not pass silently.
        self.assertNotEqual(self._critical(""), [])

    def test_whitespace_only_is_rejected(self) -> None:
        self.assertNotEqual(self._critical("\n\n   \n"), [])

    def test_plain_text_without_heading_is_rejected(self) -> None:
        # B11: no `## `/`# ` section → error even if frontmatter is present.
        text = "---\nartifact_id: FD-001\nstatus: draft\n---\n\n只有正文没有章节标题\n"
        self.assertNotEqual(self._critical(text), [])

    def test_heading_without_frontmatter_is_rejected(self) -> None:
        # B11: heading present but frontmatter missing artifact_id/status → error.
        text = "# 功能描述\n\n## 1. 功能清单\n"
        critical = self._critical(text)
        self.assertNotEqual(critical, [])
        self.assertTrue(any("artifact_id" in m for m in critical))
        self.assertTrue(any("status" in m for m in critical))

    def test_complete_artifact_passes(self) -> None:
        # B11: heading + required frontmatter → no error.
        text = "---\nartifact_id: FD-001\nstatus: draft\n---\n\n# 功能描述\n\n## 1. 功能清单\n"
        self.assertEqual(self._critical(text), [])


if __name__ == "__main__":
    unittest.main()
