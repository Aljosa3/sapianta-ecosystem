# AGOL Layer Separation Model v1

## Purpose

This evidence artifact establishes the first canonical layered authority model for AGOL.

The model separates:

- interaction intelligence;
- governance authority;
- execution authority;
- validation authority;
- reflection authority.

AGOL acts as a governance/control plane, not execution intelligence.

## Stabilization Baseline

Canonical replay-safe substrate baseline:

```text
STABILIZATION_CERTIFICATION_EPOCH_V1
```

This model depends on the stabilization epoch and does not redefine or mutate it.

## Canonical Layers

### INTERACTION_LAYER

Receives user intent, creates structured proposals, explains outcomes, summarizes replay evidence, and provides strategic reasoning.

It may communicate, interpret, and propose. It cannot execute, mutate the filesystem directly, override governance, certify, or silently run tasks.

Authority: `NONE_OVER_EXECUTION`

### GOVERNANCE_LAYER

Classifies intent, evaluates admissibility, classifies risk, creates execution envelopes, determines escalation, requires approval, and creates replay identity.

It may allow, block, escalate, and constrain execution. It cannot execute, mutate code directly, orchestrate secretly, or bypass approval.

Authority: `CONTROLS_EXECUTION_ADMISSIBILITY`

### EXECUTION_LAYER

Executes only inside a provided bounded envelope, generates artifacts, and returns normalized results.

It may perform bounded execution, patch generation, test generation, and artifact creation. It cannot modify governance, override approval, mutate policy, generate tasks autonomously, or mutate replay history.

Authority: `ONLY_INSIDE_PROVIDED_ENVELOPE`

### VALIDATION_LAYER

Performs Guardian validation, test execution, policy validation, certification, and replay-safe verification.

It may certify, reject, produce evidence, and verify determinism. It cannot plan execution, repair silently, mutate silently, or override approval.

Authority: `DETERMINES_ARTIFACT_VALIDITY`

### REFLECTION_LAYER

Interprets evidence, summarizes capability deltas, summarizes governance risk, and proposes future directions.

It may reason advisory-only, explain, and propose next steps. It cannot execute, enqueue tasks, orchestrate secretly, mutate governance, or escalate autonomously.

Authority: `ADVISORY_ONLY`

## Permanent Invariant

```text
INTERACTION_LAYER != EXECUTION_LAYER
```

No provider, interface, or future executor milestone may collapse this boundary without a new governance milestone.

## Provider Independence

Execution providers are replaceable bounded workers:

- Codex
- Claude Code
- Gemini
- local executor
- deterministic symbolic executor

Provider identity must not affect governance semantics. Replay evidence format must remain stable across providers.

## Replay-Safe Evidence Shape

```json
{
  "interaction_layer": {
    "proposal_created": true,
    "execution_authority": false
  },
  "governance_layer": {
    "decision": "ALLOW",
    "risk_class": "LOW",
    "controls_execution_admissibility": true
  },
  "execution_layer": {
    "provider": "codex",
    "bounded_execution": true,
    "provider_authoritative": false
  },
  "validation_layer": {
    "certification": "CERTIFIED",
    "determines_artifact_validity": true
  },
  "reflection_layer": {
    "advisory_generated": true,
    "allowed_to_execute_automatically": false
  }
}
```

## Explicit Non-Goals

This model does not implement provider abstraction, executor routing, execution envelopes, orchestration, token optimization, runtime optimization, adaptive planning, recursive autonomy, or hidden authority escalation.
