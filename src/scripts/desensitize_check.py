#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
desensitize_check.py — 测试 fixtures 脱敏自动化检查（E3）

扫描 test/ 目录下所有 .md / .json fixture，检测疑似未脱敏的敏感数据：
  - 手机号（完整 11 位，未掩码）
  - 身份证号（18 位 / 15 位）
  - 真实邮箱（非 example.* 域、非掩码）
  - 疑似真实人名（姓名上下文中的完整中文名 / 西文全名）

已掩码 / 泛化形式视为通过，不告警，避免误报：
  - 手机号掩码：138xxxx、138****5678（含非数字占位，不会被手机号正则命中）
  - 邮箱掩码：xxx@example.com（example.* 域或全 x 本地部分）
  - 人名泛化：业务方代表A/B、产品经理A、陈工/郑总/周工（姓氏+职称）等

用法：
  python3 src/scripts/desensitize_check.py            # 扫描默认 test/ 目录
  python3 src/scripts/desensitize_check.py <dir>      # 扫描指定目录

退出码：0 = 无严重告警；1 = 存在严重告警；2 = 目录不存在。
"""

import os
import re
import sys

# ---- 敏感模式 ----

# 完整 11 位手机号（未掩码）。掩码形式（138xxxx / 138****5678）因含非数字不会命中。
PHONE_RE = re.compile(r"\b1[3-9]\d{9}\b")

# 身份证号：18 位（17 位数字 + 校验位）或 15 位（旧版）
ID18_RE = re.compile(r"\b\d{17}[\dXx]\b")
ID15_RE = re.compile(r"\b\d{15}\b")

# 邮箱
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

# 占位/示例域名（视为已脱敏）
PLACEHOLDER_DOMAINS = {
    "example.com", "example.org", "example.net", "example.edu",
    "test.com", "test.org", "test.net", "acme.com", "foo.com",
    "bar.com", "domain.com", "yourdomain.com", "localhost",
    "example", "invalid", "email.com",
}

# 姓名字段：上下文标记 + 冒号 + 值（仅扫描该值，避免散文误报）
NAME_FIELD_RE = re.compile(
    r"(?:姓名|联系人|负责人|签字|签名|客户姓名|候选人姓名|提出方|决策人|"
    r"审批人|经办人|干系人|stakeholder|reviewer|owner|name)\s*[:：]\s*([^\n|]*)"
)

# 常见中文姓氏（用于人名启发式）
SURNAMES = (
    "王李张刘陈杨黄赵周吴徐孙马朱胡郭何林罗郑梁谢宋唐许韩冯邓曹彭曾肖田董袁潘蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤"
)

# 职称/称谓后缀：姓氏+职称（陈工/郑总/周工）视为泛化，不告警
TITLE_SUFFIXES = set(
    "工总经理总监老师先生女士老板主任部长处长科长主管董助师姐哥长官员经理总"
)

# 西文名占位首词：首词为这些词视为占位符，不告警
PLACEHOLDER_FIRST_WORDS = {
    "test", "real", "sample", "dummy", "foo", "bar", "example", "mock",
    "fake", "placeholder", "anonymous", "unknown", "tbd", "na", "none",
    "empty", "admin", "user", "guest", "customer", "client", "vendor",
    "partner", "staff", "manager", "owner", "reviewer", "pm", "vp",
    "ceo", "cto", "cfo", "coo", "hr", "it", "talent", "office",
}

# 中文人名：姓氏 + 1~2 个汉字，前面必须是边界（非汉字），末字不能是职称后缀
CHINESE_NAME_RE = re.compile(
    r"(?<![\u4e00-\u9fa5])([%s])([\u4e00-\u9fa5]{1,2})" % SURNAMES
)

# 西文全名：两个首字母大写的单词
WESTERN_NAME_RE = re.compile(r"\b[A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20}\b")


def is_masked_email(email: str) -> bool:
    """判断邮箱是否已脱敏（example.* 域 或 掩码本地部分）。"""
    local, _, domain = email.partition("@")
    domain = domain.lower().rstrip(".")
    if domain in PLACEHOLDER_DOMAINS:
        return True
    # 本地部分全为 x / *（掩码）
    if local and all(ch in "xX*" for ch in local):
        return True
    # 本地部分含掩码占位（如 ab***@...）
    if "*" in local or local.endswith("xxx") or local.endswith("XXX"):
        return True
    return False


def scan_text(path: str, rel: str) -> list:
    """扫描单个文件，返回告警列表 [(行号, 类型, 片段)]。"""
    warnings = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, OSError) as e:
        print(f"[skip] {rel}: 无法读取（{e}）")
        return warnings

    for lineno, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        # 手机号
        for m in PHONE_RE.finditer(line):
            warnings.append((lineno, "手机号", m.group(0)))
        # 身份证
        for m in ID18_RE.finditer(line):
            warnings.append((lineno, "身份证", m.group(0)))
        for m in ID15_RE.finditer(line):
            warnings.append((lineno, "身份证", m.group(0)))
        # 邮箱
        for m in EMAIL_RE.finditer(line):
            if not is_masked_email(m.group(0)):
                warnings.append((lineno, "邮箱", m.group(0)))
        # 人名（仅姓名字段值，避免散文误报）
        for m in NAME_FIELD_RE.finditer(line):
            value = m.group(1)
            for cm in CHINESE_NAME_RE.finditer(value):
                name = cm.group(0)
                # 末字是职称后缀 → 泛化，跳过
                if name[-1] in TITLE_SUFFIXES:
                    continue
                warnings.append((lineno, "疑似人名", name))
            for wm in WESTERN_NAME_RE.finditer(value):
                words = wm.group(0).split()
                if words[0].lower() in PLACEHOLDER_FIRST_WORDS:
                    continue
                warnings.append((lineno, "疑似人名", wm.group(0)))
    return warnings


def main() -> int:
    # 项目根 = src/scripts/ 上溯三级
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "test")
    target = os.path.abspath(target)

    if not os.path.isdir(target):
        print(f"错误：目录不存在 {target}")
        return 2

    total = 0
    files = 0
    for dirpath, _dirs, filenames in os.walk(target):
        for fn in sorted(filenames):
            if not fn.endswith((".md", ".json")):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            files += 1
            for lineno, kind, snippet in scan_text(full, rel):
                print(f"{rel}:{lineno}: {kind}: {snippet}")
                total += 1

    print("-" * 60)
    print(f"扫描完成：{files} 个 .md/.json 文件，命中 {total} 处敏感模式。")
    if total == 0:
        print("结果：通过（未发现疑似未脱敏的真实数据）。")
        return 0
    print("结果：发现疑似未脱敏数据，请人工复核。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
