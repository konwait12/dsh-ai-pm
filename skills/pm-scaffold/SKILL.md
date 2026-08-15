---
name: pm-scaffold
description: PRD-only product manager AI scaffold. Convert raw requirements (BRDs, meeting notes, emails, PPTs) into structured, human-confirmed Chinese PRDs through a 3-stage registry-driven pipeline.
version: 0.4.0
author: PM Scaffold
tags: [pm, prd, requirements, product-management, spec-driven]
---

# PM Scaffold · 产品 AI 脚手架

Convert raw requirement sources into a single, human-confirmed, traceable Chinese `prd.md` through a 3-stage, 5-work-item pipeline (project-background-goal → user-journey-and-stories → product-ux → function-description → prd-assembly) with cryptographic confirmation invariants.

## Quick Start

```bash
# 1. Initialize a new requirement
python3 src/scripts/pipeline.py init REQ-005-my-feature

# 2. Add your source materials to requirements/REQ-005-my-feature/00-input/

# 3. Check status
python3 src/scripts/pipeline.py requirements/REQ-005-my-feature status

# 4. Work through each stage (AI follows SKILL.md for each Work Item)
#    Stage 1: project-background-goal → user-journey-and-stories
#    Stage 2: product-ux → function-description
#    Stage 3: prd-assembly

# 5. Run validators before human review
python3 src/scripts/pipeline.py requirements/REQ-005-my-feature gate --work-item project-background-goal
bash run_tests_mac.sh
```

## What It Does

- **5 Work Items** across 3 stages: business requirements → product requirements → PRD output
- **9 sub-skills**: UX (page-design, interaction-rules) and function (feature-list, functional-flow, business-rules, validation-rules, state-machine, exception-handling, acceptance-criteria)
- **5 support capabilities**: competitive-research（竞品调研）、feasibility-analysis（可行性分析）、requirement-restate（需求重举能力）、tracking-plan（埋点计划）、issue-record（问题清单）
- **17-lens thinking framework** shared across all skills
- **Non-bypassable human gates**: only `pipeline.py review --decision approve` with a real human reviewer can confirm artifacts
- **SHA-256 binding**: confirmed artifacts are cryptographically bound to their reviewer
- **Full traceability**: G→ST→FEA→FUN→AC/BR forward and reverse traceability
- **85+ regression tests** with fixture-based validation

## Agent Entry Point

New AI agents: read `AGENTS.md` first for startup order, hard rules, and quick-start workflow.

**First contact with a new HUMAN user**: before explaining anything, open the cockpit for them (`open src/toolkit/visualization/scaffold-flow.html`) and point them to the 「📖 新手教程 · 从这里开始」 button in the left sidebar — that single self-contained HTML is the entire onboarding (flow diagram, 19-skill manual, command reference, file architecture, and the 10-chapter human+agent collaboration tutorial). There is no external ecosystem; this file IS the front door.

## Key Files

| File | Purpose |
|---|---|
| `AGENTS.md` | AI agent runtime entry (startup order, hard rules) |
| `README.md` | Human-facing project overview |
| `src/framework/workflow-registry.json` | Single source of truth for all stages, skills, artifacts |
| `src/framework/thinking-core.md` | 17 shared thinking lenses |
| `src/framework/constitution.md` | 8 hard constitutional rules |
| `src/shared/audit/review-taxonomy.md` | 7-label PRD review classification |

## Validation

```bash
bash run_tests_mac.sh                              # Full regression (85+ tests)
python3 src/scripts/consistency_check.py       # Cross-document drift check
python3 src/scripts/property_check.py <fd.md>  # Rule completeness properties
```

## Requirements

- Python 3.10+
- Git (for version control of artifacts)
- lark-cli (optional, for Feishu document integration)
