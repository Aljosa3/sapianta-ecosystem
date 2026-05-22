# SEMANTIC_CONTRACT_SYNTHESIS_V1

Status: implemented as bounded deterministic semantic contract synthesis.

## Semantic Contract Model

The semantic contract is a structured governance input created before task packaging.

Canonical fields:

- `human_request`
- `semantic_intent`
- `requested_operation`
- `allowed_scope`
- `expected_artifacts`
- `expected_tests`
- `forbidden_operations`
- `completion_requirements`
- `ambiguities`
- `authority_boundary`
- `semantic_source`
- `contract_version`
- `contract_id`
- `artifact_hash`
- `provenance`

The contract is deterministic, hashable, replay-visible, and inspectable.

## Authority Semantics

The semantic contract carries:

`SEMANTIC_ONLY_NON_EXECUTION_AUTHORITY`

This means:

- it is not approval;
- it is not dispatch;
- it is not execution authorization;
- it is not provider routing;
- it is not orchestration;
- it is not autonomous continuation.

## Semantic Synthesis Boundaries

Current synthesis is local and deterministic. It does not invoke live ChatGPT or an OpenAI API.

The semantic contract represents bounded semantic structure:

- inferred intent;
- requested operation;
- allowed scope;
- expected artifacts;
- expected tests;
- forbidden operations;
- completion requirements;
- ambiguity markers.

It does not perform semantic correctness review.

## Governance Mediation Role

The semantic contract becomes input to AiGOL governance mediation.

AiGOL remains the execution gate. The bridge packages the semantic contract into the governed task package only after transport validation and contract validation.

Codex receives:

- governed semantic contract;
- bounded execution scope;
- explicit constraints;
- expected outputs;
- forbidden operations;
- completion requirements.

Codex does not receive a vague proposal-id-only prompt as the primary semantic payload.

## Replayability Model

The semantic contract includes:

- deterministic `contract_id`;
- deterministic `artifact_hash`;
- `contract_version`;
- semantic source provenance;
- authority boundary;
- replayable provenance label.

The artifact hash excludes the `artifact_hash` field itself.

## Observability Integration

The Browser Companion observatory now includes a Semantic Contract card with:

- `STRUCTURED_SEMANTIC_CONTRACT`;
- `NON_EXECUTION_AUTHORITY`;
- `GOVERNANCE_MEDIATED`;
- `REPLAYABLE_SEMANTIC_CONTRACT`;
- semantic provenance;
- authority boundary;
- ambiguity visibility;
- expandable semantic contract JSON.

## Semantic Cognition vs Execution Authority

Semantic cognition may structure possible meaning.

AiGOL governs whether that structured meaning is admissible for task packaging and bounded execution.

Codex executes only the governed task package.

The semantic contract does not bypass governance mediation and does not authorize execution by itself.

## Explicit Non-Goals

This milestone does not add:

- live ChatGPT invocation;
- semantic auto-execution;
- semantic correctness AI review;
- orchestration;
- autonomous loops;
- hidden continuation;
- multi-agent runtime;
- background execution.
