# Intake And Routing

Every requirement starts by registering input and assessing whether required upstream business context already exists. The normal entry is `project-background-goal`.

Advanced material may reduce drafting work, but a downstream work item cannot start until every predecessor in `workflow-registry.json` has a valid confirmed baseline. Missing upstream context is backfilled; it is never silently skipped.

Assess input maturity as L0 vague input, L1 business need, L2 business solution, L3 product solution, or L4 detailed specification. Present the assessment for human confirmation. L0 triggers requirement-restate 发散模式（brainstorming 能力已并入）; L1-L4 still enter at the earliest unconfirmed predecessor. Use `src/templates/others/entry-assessment.md` when a persistent routing record is needed.
