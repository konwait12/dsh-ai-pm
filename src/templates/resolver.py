#!/usr/bin/env python3
"""Template resolver with priority stack (project > preset > extension > core).

Usage:
  python3 resolver.py <template-name> <req-dir> [--preset <name>]
  python3 resolver.py background-goal.md requirements/REQ-NNN-topic
  python3 resolver.py prd.md requirements/REQ-NNN-topic --preset <name>

Priority (highest first):
  1. Project-level overrides:  requirements/REQ-NNN/.templates/<name>
  2. Active preset:            src/templates/presets/<preset>/<name>
  3. Extensions (future):      src/templates/extensions/<ext>/<name>
  4. Core (default):           src/templates/**/<name>

Output: resolved template path (prints absolute path to stdout).
Exit 0 = found, 1 = not found.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
TEMPLATES = PROJECT / "src/templates"
PRESETS_DIR = TEMPLATES / "presets"
EXTENSIONS_DIR = TEMPLATES / "extensions"

# Map registry artifact_file to template paths
TEMPLATE_MAP = {
    "background-goal.md": "stage-1-business/background-goal.md",
    "journey-and-stories.md": "stage-1-business/journey-and-stories.md",
    "product-ux.md": "stage-2-product/product-ux.md",
    "function-description.md": "stage-2-product/function-description.md",
    "prd.md": "stage-3-prd/prd.md",
}


def find_template(name: str, req_dir: Path | None = None, preset: str | None = None) -> Path | None:
    """Resolve template path using priority stack."""

    # 1. Project-level override
    if req_dir:
        project_template = req_dir / ".templates" / name
        if project_template.exists():
            return project_template

    # 2. Active preset
    if preset:
        preset_template = PRESETS_DIR / preset / name
        if preset_template.exists():
            return preset_template

    # 3. Extensions (future — scan for matching name)
    if EXTENSIONS_DIR.exists():
        for ext_dir in sorted(EXTENSIONS_DIR.iterdir()):
            if ext_dir.is_dir():
                ext_template = ext_dir / name
                if ext_template.exists():
                    return ext_template

    # 4. Core — use template map or recursive search
    if name in TEMPLATE_MAP:
        core_path = TEMPLATES / TEMPLATE_MAP[name]
        if core_path.exists():
            return core_path

    # Fallback: recursive search in templates
    for candidate in TEMPLATES.rglob(name):
        # Skip presets and extensions (already checked)
        if "presets" not in str(candidate) and "extensions" not in str(candidate):
            return candidate

    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 resolver.py <template-name> [<req-dir>] [--preset <name>]", file=sys.stderr)
        sys.exit(2)

    name = sys.argv[1]
    req_dir = None
    preset = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--preset":
            preset = args[i + 1]
            i += 2
        elif not args[i].startswith("--"):
            req_dir = Path(args[i])
            i += 1
        else:
            i += 1

    result = find_template(name, req_dir, preset)
    if result:
        print(str(result))
        sys.exit(0)
    else:
        print(f"Template not found: {name}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
