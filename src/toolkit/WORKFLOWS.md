# Toolkit Workflows

Toolkit capabilities support a work item; they do not determine workflow order.

## Requirement Intake

Register sources → inspect material types → route to the earliest unconfirmed predecessor in `workflow-registry.json` → use document/image/browser tooling only as needed.

## Visual Communication

Start from the authoritative text/table model → choose Mermaid, editable canvas, HTML prototype or export format according to the review need → keep the same stable IDs → verify rendering → link the visual from the artifact.

Journey and P0 UX flow contracts require a visual flow representation. Other work items use diagrams only when they improve communication.

## Review And Reflow

Run the Skill validator → shared record validator → human review. A requested change produces a ModificationRecord and reruns Audit. A confirmed upstream change produces a SelectiveReflowRecord and invalidates affected downstream baselines.

## Publish

Only a human-confirmed PRD with passing traceability may be exported to Feishu, PDF or HTML. Publishing never changes content or confirmation state.
