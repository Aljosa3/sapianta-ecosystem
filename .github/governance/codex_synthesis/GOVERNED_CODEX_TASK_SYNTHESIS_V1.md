# GOVERNED_CODEX_TASK_SYNTHESIS_V1

This milestone introduces the first governance-first AI-to-AI task formation
layer above `operational-governed-interaction-runtime-v1`.

## Scope

- supported task classes:
  - `GOVERNANCE_ARTIFACT_TASK`
  - `VALIDATION_TASK`
  - `TEST_GENERATION_TASK`
  - `FINALIZE_TASK`
- deterministic bounded prompt previews
- explicit approval required before any downstream handoff
- replay-visible synthesis evidence

## Boundary

Codex remains a downstream bounded execution surface. AiGOL remains the
governance authority. This layer does not execute Codex, invoke tools, chain
tasks, plan recursively, or widen authority.
