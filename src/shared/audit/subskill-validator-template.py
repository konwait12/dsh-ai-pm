#!/usr/bin/env python3
"""Sub-skill validator template.

Each sub-skill produces a section of the parent artifact. This validator checks
that the section exists in the parent artifact and that the expected ID prefix
is present. Copy to <sub-skill>/scripts/validate_artifact.py and set:
  SECTION_NAME, ID_PATTERN, and the parent artifact glob.

Run: python3 validate_artifact.py <parent-artifact.md> [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── Per-sub-skill configuration (edit these) ──────────────
SECTION_NAME = "待修改"          # e.g. "交互规则"
ID_PATTERN = r"待修改"            # e.g. r"\bIX-\d+\b"
# ─────────────────────────────────────────────────────────


def _norm(h: str) -> str:
    return re.sub(r"^\d+\.\s*", "", h).strip()


def validate(path: Path) -> dict:
    errors, warnings = [], []
    if not path.is_file():
        return {"ok": False, "errors": [f"File not found: {path}"], "warnings": []}

    text = path.read_text(encoding="utf-8")

    # Section must exist
    headings = [_norm(m.group(1)) for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)]
    if _norm(SECTION_NAME) not in headings:
        errors.append(f"Missing required section: {SECTION_NAME}")
        return {"ok": False, "errors": errors, "warnings": warnings}

    # ID prefix must be present
    ids = re.findall(ID_PATTERN, text)
    if not ids:
        errors.append(f"No {ID_PATTERN} identifiers found in section {SECTION_NAME}")

    # Knowledge state tags present for traceable content
    if not any(tag in text for tag in ("FACT", "DECISION", "AI_INFERENCE", "UNKNOWN")):
        warnings.append("No knowledge-state tags (FACT/DECISION/AI_INFERENCE/UNKNOWN) found")

    return {"ok": not errors, "errors": errors, "warnings": warnings}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("artifact", type=Path, nargs="?", default=None,
                   help="Parent artifact path.")
    p.add_argument("--json", action="store_true", dest="j")
    args = p.parse_args()
    if args.artifact is None:
        print("Usage: python3 validate_artifact.py <artifact.md> [--json]", file=sys.stderr)
        sys.exit(2)
    r = validate(args.artifact)
    if args.j:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print("PASS" if r["ok"] else "FAIL")
        for e in r["errors"]:
            print(f"ERROR: {e}")
        for w in r["warnings"]:
            print(f"WARNING: {w}")
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
