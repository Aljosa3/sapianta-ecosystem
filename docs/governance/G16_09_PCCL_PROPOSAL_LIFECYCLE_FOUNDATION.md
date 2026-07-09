# G16-09 - PCCL Proposal Lifecycle Foundation

Status: CERTIFIED

Date: 2026-07-09

Milestone: G16-09

Scope: Deterministic PCCL Proposal Lifecycle Foundation. This milestone implements state-only lifecycle tracking for cognition proposals. It does not implement proposal generation, provider invocation, provider selection, governance execution, replay execution, worker execution, cognitive loop control, prompt generation, runtime execution, or AiCLI behavior.

## Objective

Implement the smallest missing deterministic PCCL capability after G16-08:

```text
PCCL Proposal Lifecycle
-> validated PCCL Session reference
-> validated PCCL Reference Binding
-> deterministic proposal state transitions
-> hash-chained lifecycle events
-> external references only
```

The lifecycle tracks proposal state. It does not produce proposal content, invoke providers, evaluate governance, approve execution, mutate replay, dispatch workers, or generate prompts.

## Knowledge Reuse Audit

G16-09 reused the completed Generation 16 PCCL foundation and existing Platform Core capabilities.

Reviewed governance evidence:

- `docs/governance/G16_01_PCCL_FOUNDATION.md`
- `docs/governance/G16_02_PCCL_SESSION_RUNTIME.md`
- `docs/governance/G16_03_CANONICAL_CONTEXT_ENVELOPE.md`
- `docs/governance/G16_04_CANONICAL_POLICY_ENVELOPE.md`
- `docs/governance/G16_05_PCCL_PROVIDER_INTEGRATION_AUDIT.md`
- `docs/governance/G16_06_PCCL_CAPABILITY_RESOLUTION_AUDIT.md`
- `docs/governance/G16_07_PCCL_ARCHITECTURE_CONSOLIDATION_REVIEW.md`
- `docs/governance/G16_08_PCCL_REFERENCE_BINDING.md`
- `docs/governance/G15_COGNITION_02_AUTONOMOUS_GOVERNED_COGNITIVE_LOOP_READINESS_AUDIT.md`

Reviewed implementation surfaces:

- `aigol/runtime/platform_core_cognition_layer.py`
- `aigol/runtime/platform_capability_certification_registry.py`
- `aigol/runtime/provider_proposal_production_runtime.py`
- `aigol/runtime/provider_proposal_repair_and_retry_runtime.py`
- `aigol/provider/provider_proposal_envelope.py`
- `aigol/runtime/replay_certification_runtime.py`
- `aigol/runtime/human_interface_runtime_entry_service.py`

Reused Platform Core capabilities:

- PCCL Session Runtime.
- Canonical Context Envelope.
- Canonical Policy Envelope.
- PCCL Reference Binding.
- Platform Capability Certification Registry.
- deterministic hashing through `replay_hash`.
- fail-closed validation through `FailClosedRuntimeError`.
- existing provider proposal and governance evidence as external references only.

No provider runtime, provider selection, proposal generation, governance execution, replay execution, worker execution, cognitive loop, prompt generation, or runtime execution was introduced.

## Architecture Review

G16-07 established that PCCL owns deterministic cognition session artifacts and proposal lifecycle orchestration while reusing existing certified Platform Core services.

G16-09 implements only that ownership boundary.

PCCL owns:

- proposal lifecycle artifact identity;
- proposal lifecycle status;
- deterministic lifecycle transition rules;
- hash-chained proposal lifecycle events;
- references to PCCL Session and PCCL Reference Binding;
- external lifecycle references such as context, policy, provider request, provider completion, review, approval, completion, escalation, and cancellation references.

PCCL does not own:

- proposal content generation;
- provider selection;
- provider invocation;
- provider result validation;
- governance execution;
- authorization;
- replay execution;
- replay certification;
- worker execution;
- cognitive loop control;
- prompt generation.

No Generation 14 ownership boundary changed.

## Existing Capability Discovery

Existing provider and governance services already own proposal production, proposal repair, provider output validation, governance summaries, runtime entry, replay certification, and worker execution.

No existing artifact provided a PCCL-specific proposal lifecycle state machine tied to PCCL Session and PCCL Reference Binding artifacts while explicitly preserving:

- no proposal generation;
- no provider invocation;
- no provider selection;
- no governance execution;
- no replay execution;
- no worker execution;
- no cognitive loop;
- no prompt generation.

Therefore G16-09 extends `aigol.runtime.platform_core_cognition_layer` with a state-only lifecycle artifact instead of modifying provider, governance, runtime, replay, or worker services.

## Proposal Lifecycle Specification

Implemented artifact:

- `PCCL_PROPOSAL_LIFECYCLE_ARTIFACT_V1`

Implemented version:

- `G16_09_PCCL_PROPOSAL_LIFECYCLE_FOUNDATION_V1`

Implemented operations:

- `create_pccl_proposal_lifecycle(...)`
- `validate_pccl_proposal_lifecycle(...)`
- `mark_pccl_proposal_context_ready(...)`
- `mark_pccl_proposal_policy_ready(...)`
- `mark_pccl_proposal_provider_pending(...)`
- `mark_pccl_proposal_provider_completed(...)`
- `mark_pccl_proposal_review_pending(...)`
- `mark_pccl_proposal_approval_pending(...)`
- `mark_pccl_proposal_completed(...)`
- `mark_pccl_proposal_escalated(...)`
- `cancel_pccl_proposal(...)`
- service methods on `PlatformCoreCognitionLayer`

Implemented lifecycle states:

- `CREATED`
- `CONTEXT_READY`
- `POLICY_READY`
- `PROVIDER_PENDING`
- `PROVIDER_COMPLETED`
- `REVIEW_PENDING`
- `APPROVAL_PENDING`
- `COMPLETED`
- `ESCALATED`
- `CANCELLED`

Terminal states:

- `COMPLETED`
- `ESCALATED`
- `CANCELLED`

Lifecycle invariants:

- PCCL Session artifacts are validated before lifecycle creation.
- PCCL Reference Binding artifacts are validated before lifecycle creation.
- The binding must belong to the same PCCL Session.
- Every transition appends a hash-chained event.
- Every event records from-status, to-status, transition reference, timestamp, and payload.
- Invalid transitions fail closed.
- Terminal lifecycles cannot transition.
- Proposal payloads are not embedded.
- Proposals are not generated.
- Providers are not selected or invoked.
- Governance is not executed or invoked.
- Replay is not executed or modified.
- Workers are not invoked.
- Prompt text is not generated.

## Implementation Summary

Updated:

- `aigol/runtime/platform_core_cognition_layer.py`
  - Added `PCCL_PROPOSAL_LIFECYCLE_VERSION`.
  - Added `PCCL_PROPOSAL_LIFECYCLE_ARTIFACT_V1`.
  - Added deterministic proposal lifecycle statuses and allowed transitions.
  - Added proposal lifecycle creation, transition, and validation functions.
  - Added service methods on `PlatformCoreCognitionLayer`.
  - Added fail-closed validation for lifecycle artifacts and lifecycle events.

- `aigol/runtime/platform_capability_certification_registry.py`
  - Registered `PCCL_PROPOSAL_LIFECYCLE` as a certified metadata-only Platform Core capability.

Added:

- `tests/test_g16_09_pccl_proposal_lifecycle.py`
- `docs/governance/G16_09_PCCL_PROPOSAL_LIFECYCLE_FOUNDATION.md`

## Integration Summary

The proposal lifecycle integrates by reference only.

Integration flow:

```text
PCCL Session
-> PCCL Reference Binding
-> PCCL Proposal Lifecycle
-> external provider/governance/replay/approval/completion references
```

The lifecycle can record references to provider request and completion evidence, review evidence, approval evidence, and completion evidence. It does not produce or validate those artifacts.

Behavior remains with existing owners:

- Provider Platform owns provider proposal production and provider invocation.
- Governance owns governance execution and approval semantics.
- Runtime owns runtime entry and continuation.
- Replay owns replay execution, reconstruction, and certification.
- Worker Platform owns worker execution.
- Human Authority owns approval where required.

## Architectural Health Assessment

Duplication assessment:

- No duplicate proposal generator introduced.
- No duplicate Provider Runtime introduced.
- No duplicate Provider Selection introduced.
- No duplicate Governance path introduced.
- No duplicate Replay execution introduced.
- No duplicate Worker Execution introduced.
- No prompt builder introduced.
- No cognitive loop introduced.

Ownership assessment:

- PCCL owns proposal lifecycle state only.
- Existing Platform Core services retain behavioral authority.
- Proposal lifecycle references are not authorization.
- Provider completion references are not provider invocation.
- Approval references are not approval execution.
- Completion references are not runtime completion certification.

Risk assessment:

- Future milestones must not treat `PROVIDER_PENDING` as provider invocation.
- Future milestones must not treat `PROVIDER_COMPLETED` as provider output validation.
- Future milestones must not treat `APPROVAL_PENDING` as approval granted.
- Future milestones must not use lifecycle completion as replay certification.

Current health verdict:

```text
ARCHITECTURALLY_HEALTHY_STATE_ONLY_PROPOSAL_LIFECYCLE
```

## Validation Summary

Validation performed:

- `python -m py_compile aigol/runtime/platform_core_cognition_layer.py aigol/runtime/platform_capability_certification_registry.py tests/test_g16_09_pccl_proposal_lifecycle.py`
- `python -m pytest tests/test_g16_09_pccl_proposal_lifecycle.py tests/test_g16_08_pccl_reference_binding.py tests/test_g16_04_canonical_policy_envelope.py tests/test_g16_03_canonical_context_envelope.py tests/test_g16_02_pccl_session_runtime.py -q`
- `git diff --check`

Observed result:

- Focused py_compile passed.
- Focused regression passed: `36 passed`.
- `git diff --check` passed.

## Boundary Confirmation

G16-09 did not modify AiCLI.

G16-09 did not generate proposals.

G16-09 did not invoke Cognition Providers.

G16-09 did not select providers.

G16-09 did not execute governance.

G16-09 did not execute replay.

G16-09 did not invoke workers.

G16-09 did not implement a cognitive loop.

G16-09 did not generate prompts.

G16-09 did not change Generation 14 ownership boundaries.

## Certification Verdict

CERTIFIED

G16-09 gives Platform Core a deterministic PCCL Proposal Lifecycle Foundation.

PCCL continues to own only cognition orchestration artifacts while reusing existing certified Platform Core services.
