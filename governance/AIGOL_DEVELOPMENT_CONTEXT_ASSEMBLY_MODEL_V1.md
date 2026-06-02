# AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_MODEL_V1

## Status

Review-only context assembly model.

## Canonical Artifact

Canonical artifact type:

```text
DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1
```

## Input Model

Required input object:

```text
development_task_intake
```

Required intake fields:

- `intake_id`;
- `intake_status`;
- `requested_milestone_id`;
- `requested_domain`;
- `requested_worker_family`;
- `requested_output_scope`;
- `explicit_constraints`;
- `task_kind`;
- `safe_for_native_development`;
- `codex_assisted_handoff_required`;
- `artifact_hash`.

Context assembly may only proceed when:

```text
intake_status = NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED
safe_for_native_development = true
```

## Artifact Categories

The context bundle must classify references into ordered categories:

1. core governance context;
2. native development context;
3. cognition context;
4. domain foundation context;
5. domain decision model context;
6. policy and acceptance context;
7. fixture and test scenario context;
8. worker taxonomy context;
9. known gap context;
10. certification context.

## Trading Context Requirements

For Trading worker foundation tasks, required references include:

- `AIGOL_CORE_FREEZE_CERTIFICATION`;
- `AIGOL_CLI_PRIMARY_INTERFACE_CERTIFICATION`;
- `AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_AND_SESSION_RESUME_CERTIFICATION`;
- `COGNITION_RUNTIME_CERTIFICATION`;
- `COGNITION_RUNTIME_COVERAGE_CERTIFICATION`;
- `TRADING_DOMAIN_CERTIFICATION`;
- `TRADING_DOMAIN_DECISION_VALIDATION_CERTIFICATION`;
- `TRADING_DECISION_VALIDATION_ACCEPTANCE_CERTIFICATION`;
- `TRADING_DECISION_POLICY_CONSTRAINT_CERTIFICATION`;
- `TRADING_DECISION_VALIDATION_TEST_FIXTURES_CERTIFICATION`;
- Trading Domain Foundation model documents;
- Trading worker model documents;
- Trading fixture coverage documents.

## Output Model

The artifact must include:

- `artifact_type`;
- `context_assembly_id`;
- `context_assembly_version`;
- `development_task_intake_reference`;
- `development_task_intake_hash`;
- `requested_milestone_id`;
- `requested_domain`;
- `requested_worker_family`;
- `task_kind`;
- `context_status`;
- `artifact_references`;
- `required_context_categories`;
- `missing_context`;
- `ambiguous_context`;
- `known_constraints`;
- `known_assumptions`;
- `known_gaps`;
- `provider_necessity_classification`;
- `provider_context_allowed`;
- `proposal_generation_allowed`;
- `authority`;
- `execution_requested`;
- `worker_invoked`;
- `replay_visible`;
- `created_at`;
- `artifact_hash`.

## Context Status Values

Allowed statuses:

```text
CONTEXT_ASSEMBLED
FAILED_CLOSED_MISSING_CONTEXT
FAILED_CLOSED_AMBIGUOUS_CONTEXT
FAILED_CLOSED_INVALID_INTAKE
FAILED_CLOSED_AUTHORITY_RISK
```

## Provider Necessity Values

Allowed provider necessity classifications:

```text
PROVIDER_NOT_REQUIRED
PROVIDER_OPTIONAL
PROVIDER_REQUIRED_FOR_PROPOSAL
PROVIDER_PROHIBITED
```

For native development context assembly, provider use is not required to assemble context. Provider may be required later for proposal drafting.

## Deterministic Ordering

Artifact references must be ordered by:

1. context category;
2. artifact id;
3. artifact path;
4. artifact hash.

No runtime may use file modification time, provider text, or conversational order as an authoritative ordering source.

## Known Assumptions

Context assembly may record assumptions only when they are explicit and non-authoritative.

Examples:

- target milestone is foundation-only because milestone id contains `_FOUNDATION_`;
- target domain is Trading because milestone id begins with `TRADING_`;
- target worker family is Market Evidence Normalization because milestone id contains `MARKET_EVIDENCE_NORMALIZATION_WORKER`.

Assumptions must not replace missing required context.

## Known Gaps

Known gaps must be preserved, including:

- missing domain/worker registry until implemented;
- missing provider necessity runtime until implemented;
- missing development proposal contract until implemented;
- missing conversation-to-implementation handoff until implemented.

