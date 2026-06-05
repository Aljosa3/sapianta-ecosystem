# AIGOL_ROADMAP_POST_AUDIT_V1

## Status

Post-audit roadmap.

## Completed Capabilities

Completed means `CERTIFIED` in `governance/AIGOL_CAPABILITY_MATRIX_V1.json`.

Major certified capability groups:

- constitutional governance conformance;
- capability governance matrix;
- replay evidence schema and replay reconstruction;
- approval and authorization governance;
- runtime policy engine;
- operational governance evidence index;
- conversation runtime and continuity;
- intent classification;
- prompt-to-conversation integration;
- OCS cognition, semantic resolution, context assembly, clarification, memory, and chain inspection;
- native development task intake and session resume;
- provider registry, identity, OpenAI adapter, live invocation, normalization, proposal runtime, repair/retry, and raw response capture;
- worker runtime, assignment, authorization, dispatch, invocation, and result capture;
- execution request runtime;
- minimal governed execution runtime;
- dispatch and ready-for-dispatch boundaries;
- result runtime and governed return interpretation;
- governed live execution transport;
- operational runtime CLI and inspection;
- post-execution replay review and operation ledger;
- implementation manifest runtime;
- implementation plan to execution request conversion;
- generated content validation and acceptance;
- first implementation-generation epoch;
- governed implementation dry run;
- trading decision validation runtime and fixtures;
- healthcare, marketing, and server-management domain seed runtimes;
- resource selection runtime.

## Partially Completed Capabilities

Partial capability groups:

- native development end-to-end readiness;
- provider ecosystem completeness;
- production deployment automation;
- native implementation generation as an operator-ready product flow;
- trading market evidence normalization worker foundation;
- generic domain factory and executable domain bundle;
- production-grade multi-domain commercial runtime portfolio;
- provider substitutability;
- worker ecosystem readiness;
- local node architecture.

## Missing Capabilities

Missing capability groups:

- autonomous code mutation without human authority, intentionally not started and constitutionally forbidden;
- marketplace discovery, packaging, and commercial listing;
- enterprise tenant, organization, and billing governance;
- external partner onboarding and certification workflow.

## Recommended Execution Order

### 1. Native Development Replay-Safe Handoff Hardening

Milestone:

```text
AIGOL_NATIVE_DEVELOPMENT_REPLAY_SAFE_HANDOFF_HARDENING_V1
```

Rationale:

This closes the most visible gap between certified cognition and useful operator-facing development work.

Required outputs:

- deterministic resumed session state;
- development task packet;
- target artifact list;
- context hash;
- provider necessity classification;
- proposal validation artifact;
- operator-facing handoff artifact;
- failure certification path.

Validation:

```bash
pytest tests/test_native_development_task_intake_and_session_resume_v1.py
pytest tests/test_development_context_assembly_runtime_v1.py
pytest tests/test_domain_and_worker_resolution_registry_v1.py
pytest tests/test_provider_necessity_policy_runtime_v1.py
pytest tests/test_development_proposal_contract_runtime_v1.py
pytest tests/test_conversation_to_implementation_handoff_runtime_v1.py
git diff --check
```

### 2. Operator-Ready Implementation Generation Runtime

Rationale:

Build on the handoff milestone to make implementation generation repeatable without granting hidden autonomy.

Required outputs:

- implementation authority contract enforcement;
- generated target artifact manifest;
- deterministic validation result;
- human approval checkpoint;
- replay-safe generated content evidence;
- implementation certification record.

Validation:

```bash
pytest tests/test_implementation_manifest_runtime_v1.py
pytest tests/test_generated_content_validation_runtime_v1.py
pytest tests/test_generated_content_acceptance_runtime_v1.py
pytest tests/test_first_end_to_end_implementation_generation_epoch_v1.py
git diff --check
```

### 3. Trading Domain Worker Hardening

Rationale:

Trading is the strongest current domain seed and the most natural Product 1 demonstration target.

Required outputs:

- trading market evidence normalization runtime coverage;
- fixture coverage;
- policy constraint replay;
- worker invocation evidence;
- result validation evidence.

Validation:

```bash
pytest tests/test_first_readonly_domain_experiment_v1.py
pytest tests/test_first_real_domain_worker_v1.py
pytest tests/test_worker_invocation_runtime_v1.py
pytest tests/test_worker_result_validation_runtime_v1.py
git diff --check
```

### 4. Generic Domain Factory And Bundle Registry

Rationale:

Convert domain-specific success into repeatable governed domain onboarding.

Required outputs:

- domain factory contract hardening;
- executable bundle registry;
- domain compatibility validation;
- cross-domain fixture evidence;
- portfolio readiness review.

Validation:

```bash
pytest tests/test_generic_domain_factory_runtime_v1.py
pytest tests/test_domain_bundle_registry_runtime_v1.py
pytest tests/test_executable_domain_bundle_runtime_v1.py
pytest tests/test_multi_artifact_domain_bundle_runtime_v1.py
git diff --check
```

### 5. Provider And Worker Ecosystem Certification

Rationale:

AiGOL has certified provider and worker cores, but commercial ecosystem maturity needs onboarding, substitutability, and lifecycle certification.

Required outputs:

- provider capability metadata schema;
- worker capability metadata schema;
- substitutability evidence;
- domain compatibility evidence;
- partner rejection and repair evidence;
- ecosystem certification gate.

Validation:

```bash
pytest tests/test_provider_registry.py
pytest tests/test_provider_contracts.py
pytest tests/test_provider_transport_connector.py
pytest tests/test_worker_runtime_v1.py
pytest tests/test_worker_assignment_runtime_v1.py
git diff --check
```

### 6. Marketplace And Enterprise Commercial Governance

Rationale:

Only start marketplace work after provider, worker, and domain metadata are hardened. Marketplace work must remain governance-first and avoid uncontrolled execution semantics.

Required outputs:

- marketplace discovery model;
- listing package schema;
- tenant and organization policy model;
- entitlement and billing event model;
- partner certification workflow;
- replay and redaction policy for commercial events.

Validation:

```bash
pytest tests/test_capability_registry.py
pytest tests/test_unified_resource_selection_runtime_v1.py
pytest tests/test_runtime_policy_engine_v1.py
git diff --check
```

## Recommended Next Milestone

```text
AIGOL_NATIVE_DEVELOPMENT_REPLAY_SAFE_HANDOFF_HARDENING_V1
```

Success criteria:

- Native development requests no longer depend on ambiguous conversation interpretation.
- Resumed sessions preserve append-only replay.
- Target artifacts and validation scope are deterministic.
- Provider use is classified before invocation.
- Provider proposals remain non-authoritative.
- Operator handoff is explicit and replay-visible.
- Failure remains certified rather than hidden.

