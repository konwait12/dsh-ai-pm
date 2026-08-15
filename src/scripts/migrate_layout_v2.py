#!/usr/bin/env python3
"""Migrate REQ-DIR folders from the flat Wave layout to the v2 stage layout.

Note on the v1 -> v2 simulated marking
--------------------------------------
Artifacts produced under the v1 (flat Wave) layout were generated before the
v2 review/validation pipeline was in place. They therefore MUST be marked as
``simulation: true`` / ``status: simulated`` when migrated so that downstream
validators and orchestrators do not mistake them for artifacts that have
already cleared the v2 review process.

The marking is opt-in: it only runs when ``--apply --confirm --mark-simulated``
are all passed. By default the migration does NOT simulate, so callers that
intend to re-validate the migrated artifacts end-to-end (or that already have
real review records) keep their status untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

MAPPINGS = {
    "00_input": "00-input",
    "01_background-goal": "001-business-requirements/01-background-goal",
    "02_journey-stories": "001-business-requirements/02-user-journey-stories",
    "03_ux": "002-product-requirements/01-product-ux",
    "04_function": "002-product-requirements/02-function-description",
    "05_prd": "003-prd-output",
    "99_review": "99-review",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_manifest(req_dir: Path) -> dict[str, str]:
    return {
        str(path.relative_to(req_dir)): digest(path)
        for path in sorted(req_dir.rglob("*")) if path.is_file()
    }


def plan_migration(req_dir: Path) -> dict:
    moves = []
    conflicts = []
    for old, new in MAPPINGS.items():
        source, target = req_dir / old, req_dir / new
        if not source.exists():
            continue
        if target.exists():
            conflicts.append({"source": old, "target": new, "reason": "target exists"})
        else:
            moves.append({"source": old, "target": new})
    return {"requirement": req_dir.name, "moves": moves, "conflicts": conflicts}


def rewrite_paths(req_dir: Path) -> int:
    changed = 0
    replacements = sorted(MAPPINGS.items(), key=lambda pair: len(pair[0]), reverse=True)
    for path in req_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements:
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def mark_simulated(req_dir: Path) -> int:
    """Rewrite ``status: confirmed`` -> ``status: simulated`` and inject
    ``simulation: true`` next to ``artifact_id:`` for every markdown file
    under ``req_dir``.

    The rewrite logic is identical to the original v2 migration; the only
    behavioural change is that this now applies to *every* REQ directory
    (no hard-coded REQ-002 prefix). Whether the marking actually runs is
    controlled by the ``mark_simulated`` flag passed to
    :func:`apply_migration`.
    """
    changed = 0
    for path in req_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        updated = text.replace("status: confirmed", "status: simulated")
        updated = updated.replace("status = confirmed", "status = simulated")
        if "artifact_id:" in updated and "simulation: true" not in updated:
            updated = updated.replace("artifact_id:", "simulation: true\nartifact_id:", 1)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def apply_migration(req_dir: Path, plan: dict, mark_simulated: bool = False) -> dict:
    if plan["conflicts"]:
        raise RuntimeError(f"migration conflicts: {plan['conflicts']}")
    before = file_manifest(req_dir)
    for move in plan["moves"]:
        source, target = req_dir / move["source"], req_dir / move["target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
    rewritten = rewrite_paths(req_dir)
    # The ``mark_simulated`` parameter shadows the module-level
    # ``mark_simulated`` function inside this scope. Capture the parameter as
    # ``mark_simulated_arg`` and reach the rewrite function through the
    # module globals to avoid the shadowing entirely.
    mark_simulated_arg = mark_simulated
    rewrite_fn = globals()["mark_simulated"]
    simulated = rewrite_fn(req_dir) if mark_simulated_arg else 0
    after = file_manifest(req_dir)
    review_dir = req_dir / "99-review"
    review_dir.mkdir(parents=True, exist_ok=True)
    result = {
        **plan,
        "applied_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "rewritten_markdown_files": rewritten,
        "simulated_files": simulated,
        "mark_simulated_applied": bool(mark_simulated_arg),
        "before_hashes": before,
        "after_hashes": after,
    }
    (review_dir / "layout-migration-v2.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="One-shot migration tool: flat Wave layout -> v2 stage layout. "
                    "Only needed for requirements created before the v2 layout.",
    )
    parser.add_argument("req_dirs", nargs="+", type=Path)
    parser.add_argument("--apply", action="store_true", help="Actually move/rewrite requirement files")
    parser.add_argument("--confirm", action="store_true",
                        help="Required with --apply: acknowledge that files will be moved and rewritten")
    parser.add_argument("--mark-simulated", action="store_true", default=False,
                        help="Mark migrated artifacts as simulated. Only effective together with "
                             "--apply --confirm; without it the migration never simulates.")
    args = parser.parse_args()
    if args.apply and not args.confirm:
        print("ERROR: --apply moves directories and rewrites .md content in place.", file=sys.stderr)
        print("       This is a one-shot migration tool; run without --apply for a dry-run,", file=sys.stderr)
        print("       or re-run with --apply --confirm to proceed.", file=sys.stderr)
        return 2
    results = []
    for req_dir in args.req_dirs:
        if not req_dir.is_dir():
            print(f"ERROR: {req_dir} is not a directory", file=sys.stderr)
            return 1
        plan = plan_migration(req_dir)
        if args.apply:
            plan = apply_migration(req_dir, plan, mark_simulated=args.mark_simulated)
        results.append(plan)
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", "results": results}, ensure_ascii=False, indent=2))
    return 1 if any(result["conflicts"] for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
