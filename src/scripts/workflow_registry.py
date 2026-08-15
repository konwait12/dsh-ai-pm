#!/usr/bin/env python3
"""Load and resolve the stage, work-item, and artifact registry."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = PROJECT / "src/framework/workflow-registry.json"


def artifact_content_hash(text: str) -> str:
    """Single canonical SHA-256 of an artifact's content.

    Review-metadata fields (status / reviewer / reviewed_at / confirmed_at)
    are stripped before hashing so post-confirmation edits to those fields do
    not break `branch_validator` cross-checks against a recorded ReviewRecord.
    Both `pipeline.py` and `branch_validator.py` import this function — keep
    the algorithm here as the single source of truth.
    """
    canonical = re.sub(
        r"(?m)^(status|reviewer|reviewed_at|confirmed_at):.*$",
        r"\1: <review-metadata>",
        text,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_registry() -> dict:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if registry.get("schema_version") not in (3, 4, 5, 6):
        raise ValueError("Unsupported workflow registry schema")
    return registry


def work_items() -> list[dict]:
    return sorted(load_registry()["work_items"], key=lambda item: item["order"])


def branch_capabilities() -> list[dict]:
    """Return conditional/branch skills (support + newly-registered branch skills)."""
    return list(load_registry().get("support_capabilities", []))


def resolve_branch_capability(branch_id: str) -> dict:
    for cap in branch_capabilities():
        if cap["id"] == branch_id:
            return cap
    raise KeyError(f"Unknown branch capability: {branch_id}")


def resolve_work_item(work_item: str | None = None, wave: int | None = None) -> dict:
    items = work_items()
    if wave is not None:
        for item in items:
            if item["legacy_wave"] == wave:
                return item
        raise KeyError(f"Unknown legacy wave: {wave}")
    if work_item:
        for item in items:
            if item["id"] == work_item:
                return item
        raise KeyError(f"Unknown work item: {work_item}")
    raise ValueError("work_item or wave is required")


def artifact_dirs(req_dir: Path, item: dict) -> list[Path]:
    return [req_dir / item["artifact_dir"], req_dir / item["legacy_artifact_dir"]]


def find_artifact(req_dir: Path, item: dict) -> Path | None:
    for directory in artifact_dirs(req_dir, item):
        if not directory.exists():
            continue
        preferred = directory / item["artifact_file"]
        if preferred.exists():
            return preferred
        for path in sorted(directory.glob("*.md")):
            if path.name != "README.md" and not re.search(r"v0\.\d+", path.name):
                return path
    return None


def read_frontmatter(path: Path) -> dict[str, str]:
    text = re.sub(r"^<!--.*?-->\s*", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    match = re.match(r"---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip("'\"")
    return result


def artifact_status(req_dir: Path, item: dict) -> str:
    artifact = find_artifact(req_dir, item)
    return read_frontmatter(artifact).get("status", "unknown") if artifact else "not_created"


def skill_path(item: dict) -> Path:
    return PROJECT / item["skill_path"]
