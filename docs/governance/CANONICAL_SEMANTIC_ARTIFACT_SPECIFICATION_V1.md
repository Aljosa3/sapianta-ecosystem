# Canonical Semantic Artifact Specification V1

Status: Generation 2 specification.

Scope: canonical semantic artifact consumed by Platform Core Generation 2 consumers.

This artifact does not implement runtime code, modify tests, change Platform Core Generation 1, alter governance, alter replay, change routing, change HIRR, change PPP, change approval, or remove compatibility layers.

## 1. Purpose

Platform Core Generation 1 is certified with limitations.

Generation 2 adopts the objective that Universal Bidirectional Translation Runtime becomes the exclusive semantic authority.

To satisfy that objective, every Platform Core consumer must consume the same canonical semantic artifact rather than independently deriving semantic meaning from human language.

This specification defines that artifact.

Target flow:

```text
Human
-> Universal Bidirectional Translation Runtime
-> Canonical Semantic Artifact
-> Platform Core consumers
-> Replay
-> Human-friendly explanation
```

## 2. Relationship To Existing UBTR Artifacts

The Canonical Semantic Artifact is not a replacement for the Universal Translation Artifact Schema.

It is the Generation 2 consumer-facing semantic contract derived from and linked to Universal Translation Artifacts.

Required source artifacts:

- Human -> Governance Universal Translation Artifact.
- Governance -> Human Universal Translation Artifact when a human-readable projection is present.

The Canonical Semantic Artifact must preserve:

- source translation ids;
- translation artifact hashes;
- replay references;
- source payload hashes;
- authority-denial flags;
- deterministic confidence and ambiguity evidence.

## 3. Authority Boundary

The Canonical Semantic Artifact is semantic evidence only.

It never:

- approves;
- rejects;
- authorizes;
- executes;
- invokes workers;
- invokes providers as authority;
- mutates governance;
- mutates replay;
- selects authoritative workflow by itself;
- bypasses fail-closed behavior.

Consumers may use the artifact as input to governed decision logic. Governance remains authoritative for admissibility, routing decisions, approval requirements, execution gates, worker authorization, and replay persistence.

## 4. Artifact Type

Canonical artifact type:

```text
CANONICAL_SEMANTIC_ARTIFACT_V1
```

Required final verdict for this specification:

```text
CANONICAL_SEMANTIC_ARTIFACT_SPECIFICATION_READY
```

## 5. Top-Level Artifact Shape

The artifact must be JSON serializable and deterministic-hash bound.

Required top-level fields:

```text
artifact_type
schema_version
semantic_identity
conversation_identity
workflow_identity
replay_identity
translation_lineage
semantic_payload
confidence
ambiguity
clarification_state
approval_state
execution_intent
provider_projection
worker_projection
human_readable_projection
technical_projection
governance_requirements
authority_flags
forward_compatibility
backward_compatibility
created_at
artifact_hash
```

Optional top-level fields:

```text
extension_fields
migration_metadata
compatibility_fallback
consumer_annotations
```

Optional fields must not grant authority.

## 6. Field Specification

### 6.1 `artifact_type`

Status: mandatory.

Producer: UBTR canonical semantic artifact builder.

Consumers: all Platform Core semantic consumers.

Replay requirements:

- recorded exactly;
- included in artifact hash;
- must equal `CANONICAL_SEMANTIC_ARTIFACT_V1`.

Governance requirements:

- malformed or unexpected artifact type fails closed.

### 6.2 `schema_version`

Status: mandatory.

Producer: UBTR canonical semantic artifact builder.

Consumers: all consumers and replay reconstruction.

Replay requirements:

- recorded exactly;
- included in artifact hash.

Governance requirements:

- unsupported major version fails closed;
- supported minor versions may be accepted under compatibility rules.

### 6.3 `semantic_identity`

Status: mandatory.

Producer: UBTR.

Consumers:

- ACLI;
- HIRR;
- workflow routing;
- PPP;
- hardening;
- replay;
- replay-derived learning.

Required subfields:

```text
semantic_id
semantic_hash
source_language
normalized_language
intent_family
requested_actions
domain_candidate
entity_set_hash
semantic_equivalence_group
```

Replay requirements:

- `semantic_hash` must be deterministic;
- replay must link `semantic_id` to source translation artifact hashes.

Governance requirements:

- semantic identity may identify meaning but does not select workflow, approve execution, or authorize mutation.

### 6.4 `workflow_identity`

Status: mandatory.

Producer: UBTR for candidate fields; workflow governance for selected fields.

Consumers:

- ACLI;
- workflow routing;
- HIRR;
- PPP;
- approval;
- replay;
- hardening.

Required subfields:

```text
workflow_candidate
workflow_candidate_confidence
workflow_candidate_source
selected_workflow
workflow_selection_status
workflow_selection_reference
workflow_selection_hash
```

Replay requirements:

- candidate and selected workflow must be distinguishable;
- workflow selection reference must point to governed routing evidence when selected.

Governance requirements:

- UBTR may produce `workflow_candidate`;
- only governed routing may produce authoritative `selected_workflow`;
- mismatch between candidate and selection must be replay-visible.

### 6.5 `conversation_identity`

Status: mandatory.

Producer: ACLI/session runtime with UBTR reference.

Consumers:

- ACLI;
- HIRR;
- resume runtime;
- lifecycle runtime;
- replay;
- hardening.

Required subfields:

```text
session_id
conversation_id
turn_id
turn_index
operator_id
created_at
parent_turn_reference
continuation_of_turn
```

Replay requirements:

- every semantic artifact must be traceable to a conversation turn;
- continuation turns must preserve parent reference.

Governance requirements:

- conversation identity does not grant authority;
- missing conversation identity fails closed for interactive ACLI flows.

### 6.6 `replay_identity`

Status: mandatory.

Producer: replay runtime / ACLI runtime.

Consumers:

- all replay-aware consumers;
- hardening;
- certification evidence;
- replay-derived learning.

Required subfields:

```text
replay_chain_id
replay_reference
source_replay_reference
translation_replay_reference
workflow_replay_reference
approval_replay_reference
execution_replay_reference
semantic_artifact_hash
source_artifact_hashes
```

Replay requirements:

- replay chain id must be stable;
- source artifact hashes must be deterministic;
- reconstruction must verify hashes.

Governance requirements:

- replay identity is evidence identity only;
- replay identity must not be writable by providers or workers.

### 6.7 `translation_lineage`

Status: mandatory.

Producer: UBTR.

Consumers:

- ACLI;
- HIRR;
- routing;
- explanation runtime;
- replay;
- hardening;
- replay-derived learning.

Required subfields:

```text
human_to_governance_translation_id
human_to_governance_artifact_hash
human_to_governance_replay_reference
governance_to_human_translation_id
governance_to_human_artifact_hash
governance_to_human_replay_reference
translation_runtime_versions
deterministic_fallback_status
provider_translation_candidates
selected_translation_source
```

Replay requirements:

- every source translation artifact must be hash-verifiable;
- provider translation candidates must be replay-visible when present.

Governance requirements:

- provider candidates remain non-authoritative;
- selected translation source does not authorize execution.

### 6.8 `semantic_payload`

Status: mandatory.

Producer: UBTR.

Consumers:

- ACLI;
- HIRR;
- routing;
- OCS;
- PPP;
- approval;
- hardening;
- replay-derived learning.

Required subfields:

```text
normalized_text
intent_family
requested_actions
domain_candidate
subjects
entities
artifact_identifiers
target_paths
constraints
non_goals
operator_preferences
language_metadata
```

Replay requirements:

- normalized text and entity sets must be deterministic;
- target paths and artifact identifiers must be preserved exactly when extracted.

Governance requirements:

- semantic payload is candidate meaning only;
- consumers must validate against governance and workflow policy before action.

### 6.9 `confidence`

Status: mandatory.

Producer: UBTR.

Consumers:

- ACLI;
- HIRR;
- routing;
- provider escalation;
- hardening;
- replay.

Required subfields:

```text
overall_confidence
intent_confidence
domain_confidence
workflow_candidate_confidence
entity_confidence
language_confidence
confidence_basis
threshold_policy
```

Allowed confidence values:

```text
HIGH
MEDIUM
LOW
INSUFFICIENT
```

Replay requirements:

- confidence values and basis must be replay-visible;
- threshold policy version must be recorded.

Governance requirements:

- low or insufficient confidence may trigger clarification or fail-closed behavior;
- confidence alone never authorizes execution.

### 6.10 `ambiguity`

Status: mandatory.

Producer: UBTR.

Consumers:

- HIRR;
- ACLI;
- routing;
- provider escalation;
- hardening.

Required subfields:

```text
ambiguity_status
ambiguity_reasons
unsafe_ambiguity
material_ambiguity
missing_required_fields
conflicting_interpretations
clarification_required
clarification_questions
```

Replay requirements:

- ambiguity reasons must be deterministic and replay-visible.

Governance requirements:

- unsafe ambiguity must fail closed;
- material ambiguity must route to clarification unless a certified policy permits provider-assisted explanation.

### 6.11 `clarification_state`

Status: mandatory.

Producer: UBTR and HIRR-compatible clarification runtime.

Consumers:

- HIRR;
- ACLI;
- resume runtime;
- replay;
- hardening.

Required subfields:

```text
clarification_required
clarification_status
clarification_questions
clarification_answers
clarification_turn_references
ambiguity_reduced
target_preserved
next_required_operator_action
```

Replay requirements:

- every clarification question and response must be turn-linked;
- target preservation must be replay-visible.

Governance requirements:

- clarification may refine semantic meaning but does not approve or execute.

### 6.12 `approval_state`

Status: mandatory.

Producer: proposal/approval runtime, with UBTR semantic references.

Consumers:

- ACLI;
- approval runtime;
- resume runtime;
- workflow execution bridge;
- replay;
- hardening.

Required subfields:

```text
approval_required
approval_status
approval_reason
proposal_identifier
proposal_hash
approval_reference
approval_command
approval_actor
approval_timestamp
modification_requested
rejection_reason
```

Replay requirements:

- proposal hash binding must be recorded;
- approval and rejection events must be replay-visible;
- absent approval must be explicit.

Governance requirements:

- semantic artifact may state whether approval appears required;
- only approval runtime records authoritative approval status;
- execution without valid approval fails closed.

### 6.13 `execution_intent`

Status: mandatory.

Producer: UBTR for candidate intent; governance/workflow runtime for authorized execution state.

Consumers:

- ACLI;
- routing;
- approval;
- PPP;
- worker runtime;
- replay;
- hardening.

Required subfields:

```text
execution_requested
execution_type_candidate
execution_scope_candidate
side_effects_possible
repository_mutation_possible
execution_authorized
authorization_reference
authorization_hash
fail_closed_required
```

Replay requirements:

- requested and authorized execution must be separate fields;
- authorization reference must be hash-verifiable when present.

Governance requirements:

- UBTR can identify execution intent;
- UBTR cannot authorize execution;
- side-effect-bearing execution requires governed approval and authorization.

### 6.14 `provider_projection`

Status: mandatory.

Producer: UBTR and provider policy runtime.

Consumers:

- OCS;
- provider routing;
- explanation runtime;
- replay;
- hardening.

Required subfields:

```text
provider_relevance
provider_invocation_allowed
provider_invoked
provider_role
provider_selection_policy
provider_candidates
provider_response_references
provider_authority
provider_failure_reason
```

Replay requirements:

- provider selection and invocation must be replay-visible;
- provider failures must be recorded when applicable.

Governance requirements:

- provider authority must always be false;
- provider output is proposal-only or explanation-only unless a separate governed worker path applies.

### 6.15 `worker_projection`

Status: mandatory.

Producer: UBTR for worker relevance; worker/governance runtimes for actual worker state.

Consumers:

- PPP;
- worker selection;
- worker dispatch;
- approval runtime;
- replay;
- hardening.

Required subfields:

```text
worker_relevance
worker_required
worker_candidate_family
worker_invocation_allowed
worker_invoked
worker_authorization_reference
worker_result_reference
worker_authority
```

Replay requirements:

- worker relevance and worker invocation must be separate;
- worker authorization and result references must be hash-verifiable when present.

Governance requirements:

- worker authority must always be false as semantic authority;
- workers execute only through governed, authorized worker runtime.

### 6.16 `human_readable_projection`

Status: mandatory.

Producer: Governance -> Human UBTR translation and explanation runtime.

Consumers:

- ACLI operator view;
- human-friendly explanation runtime;
- LLM-assisted explanation runtime;
- replay review;
- hardening.

Required subfields:

```text
what_i_understood
what_will_happen
what_will_not_happen
what_requires_approval
what_to_type_next
replay_visibility
operator_warnings
plain_language_summary
```

Replay requirements:

- human-readable projection must be replay-visible;
- optional LLM-assisted wording must include deterministic fallback evidence.

Governance requirements:

- human-readable projection is explanatory only;
- explanation cannot alter workflow state.

### 6.17 `technical_projection`

Status: mandatory.

Producer: UBTR plus consuming runtime annotations.

Consumers:

- diagnostics;
- replay;
- hardening;
- certification;
- developers.

Required subfields:

```text
runtime_versions
semantic_rule_ids
translation_rule_ids
decision_source
compatibility_fallback_used
compatibility_fallback_reason
consumer_expectations
validation_status
diagnostic_details
```

Replay requirements:

- diagnostic details must not contain secrets;
- compatibility fallback must be visible when used.

Governance requirements:

- technical projection supports audit only;
- technical projection cannot grant authority.

### 6.18 `governance_requirements`

Status: mandatory.

Producer: UBTR and governance policy runtime.

Consumers:

- ACLI;
- routing;
- approval;
- PPP;
- worker runtime;
- replay.

Required subfields:

```text
approval_required
authorization_required
validation_required
replay_required
human_review_required
fail_closed_conditions
policy_references
```

Replay requirements:

- policy references must be stable identifiers.

Governance requirements:

- governance requirements constrain consumers;
- missing required governance requirement fails closed.

### 6.19 `authority_flags`

Status: mandatory.

Producer: UBTR.

Consumers: all.

Required flags:

```text
semantic_authority
governance_authority
approval_authority
execution_authority
mutation_authority
provider_authority
worker_authority
replay_mutation_authority
```

Required values:

```text
semantic_authority: true
all other authority flags: false
```

Replay requirements:

- included in artifact hash;
- reconstructed and validated.

Governance requirements:

- any non-semantic authority flag set to true fails closed;
- `semantic_authority` means translation ownership only, not governance authority.

### 6.20 `forward_compatibility`

Status: mandatory.

Producer: UBTR.

Consumers:

- all consumers;
- replay;
- migration tooling.

Required subfields:

```text
schema_major_version
schema_minor_version
required_consumer_capabilities
optional_consumer_capabilities
extension_policy
unknown_field_policy
```

Replay requirements:

- compatibility policy version must be recorded.

Governance requirements:

- unsupported major version fails closed;
- unknown mandatory fields fail closed;
- unknown optional fields may be ignored only if artifact hash remains valid.

### 6.21 `backward_compatibility`

Status: mandatory.

Producer: UBTR migration/integration layer.

Consumers:

- replay;
- hardening;
- ACLI;
- migration tooling.

Required subfields:

```text
source_generation
legacy_translation_reference
legacy_local_marker_reference
compatibility_mode
fallback_allowed
fallback_reason
legacy_replay_readable
```

Replay requirements:

- legacy references must remain readable;
- compatibility fallback must be explicit.

Governance requirements:

- backward compatibility may preserve behavior but cannot bypass current governance.

## 7. Producer And Consumer Matrix

| Field Group | Producer | Primary Consumers |
| --- | --- | --- |
| semantic identity | UBTR | ACLI, HIRR, routing, hardening, replay |
| workflow identity | UBTR candidate, governed routing selected | ACLI, routing, PPP, approval, replay |
| conversation identity | ACLI/session runtime | HIRR, resume, replay, hardening |
| replay identity | replay runtime / ACLI | all replay-aware consumers |
| translation lineage | UBTR | all semantic consumers |
| confidence | UBTR | HIRR, routing, escalation, hardening |
| ambiguity | UBTR | HIRR, ACLI, routing |
| clarification state | UBTR and HIRR-compatible runtime | HIRR, ACLI, resume |
| approval state | approval runtime | ACLI, execution bridge, replay |
| execution intent | UBTR candidate, governance authorized state | routing, PPP, approval, worker |
| provider projection | UBTR and provider policy | OCS, provider routing, explanation |
| worker projection | UBTR candidate, worker runtimes actual state | PPP, worker runtimes, replay |
| human-readable projection | Governance -> Human UBTR / explanation runtime | ACLI, operator, replay |
| technical projection | UBTR and consumers | diagnostics, replay, certification |

## 8. Replay Requirements

Replay must preserve:

- source human prompt hash;
- source governance state hash;
- Canonical Semantic Artifact hash;
- source Universal Translation Artifact hashes;
- producer runtime version;
- consumer runtime ids;
- selected workflow reference;
- approval reference;
- execution reference;
- provider/worker references when applicable;
- compatibility fallback status;
- fail-closed reason when applicable.

Replay reconstruction must verify:

- artifact hash;
- translation lineage hashes;
- authority flags;
- schema version compatibility;
- replay reference integrity;
- no provider or worker mutation of semantic artifact.

## 9. Governance Requirements

Consumers must enforce:

- malformed artifact fails closed;
- unsupported major version fails closed;
- missing mandatory field fails closed;
- true non-semantic authority flag fails closed;
- execution intent without approval/authorization fails closed;
- provider projection cannot grant authority;
- worker projection cannot invoke workers by itself;
- human-readable projection cannot modify state.

Governance may select workflow using the artifact, but workflow selection remains a governed decision.

## 10. Forward Compatibility

Forward compatibility rules:

1. Minor versions may add optional fields.

2. Optional fields must live under declared extension locations or explicitly versioned groups.

3. Unknown optional fields may be ignored by consumers if:

   - artifact hash validates;
   - required fields are present;
   - authority flags are valid;
   - consumer capability requirements are satisfied.

4. Unknown mandatory fields fail closed unless the consumer declares support.

5. New authority flags default to false and must fail closed if true and unsupported.

6. New provider, worker, or explanation projections must remain non-authoritative.

## 11. Backward Compatibility

Backward compatibility rules:

1. Generation 1 Universal Translation Artifacts remain valid source artifacts.

2. Generation 1 replay remains readable.

3. Local marker compatibility references may be preserved as historical evidence.

4. Compatibility fallback must be explicit.

5. Historical replay must not be reinterpreted as if it used Generation 2 exclusive authority.

6. Migration tools may wrap Generation 1 evidence in a Generation 2 compatibility envelope, but must mark `source_generation: PLATFORM_CORE_GENERATION1`.

7. Backward compatibility cannot bypass current governance checks.

## 12. Versioning Strategy

Version format:

```text
CANONICAL_SEMANTIC_ARTIFACT_V<major>.<minor>
```

Governance artifact name:

```text
CANONICAL_SEMANTIC_ARTIFACT_SPECIFICATION_V1
```

Runtime artifact type for V1:

```text
CANONICAL_SEMANTIC_ARTIFACT_V1
```

Rules:

- major version changes may alter required fields or semantics;
- minor version changes may add optional fields;
- patch-level implementation changes must not change schema semantics;
- consumers must declare supported major and minor ranges;
- unsupported major versions fail closed;
- schema changes require governance artifact update and regression certification.

## 13. Consumer Requirements

Every Generation 2 consumer must:

1. Validate the artifact schema.

2. Validate artifact hash.

3. Validate authority flags.

4. Validate supported version.

5. Consume semantic fields instead of raw prompt markers.

6. Record decision source in replay.

7. Preserve compatibility fallback only when explicitly allowed.

8. Fail closed on malformed or insufficient artifacts.

9. Avoid modifying the artifact in place.

10. Emit consumer-specific derived artifacts rather than mutating canonical semantic evidence.

## 14. Non-Goals

This specification does not:

- implement runtime code;
- modify Platform Core Generation 1;
- remove compatibility layers now;
- redesign governance;
- redesign replay;
- redesign HIRR;
- redesign PPP;
- redesign approval;
- grant UBTR execution authority;
- grant providers authority;
- grant workers authority;
- make explanations authoritative;
- certify exclusive UBTR migration as complete.

## 15. Acceptance Criteria

This specification is ready when it defines:

- semantic identity;
- workflow identity;
- conversation identity;
- replay identity;
- translation lineage;
- confidence representation;
- ambiguity representation;
- clarification state;
- approval state;
- execution intent;
- provider projection;
- worker projection;
- human-readable projection;
- technical projection;
- mandatory and optional field status;
- producers and consumers;
- replay requirements;
- governance requirements;
- forward compatibility;
- backward compatibility;
- versioning strategy.

This artifact satisfies those criteria.

## Final Verdict

CANONICAL_SEMANTIC_ARTIFACT_SPECIFICATION_READY
