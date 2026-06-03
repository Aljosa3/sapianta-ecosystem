# AIGOL_HUMAN_CLARIFICATION_AND_APPROVAL_POLICY_V1

## Status

Constitutional policy certification.

## Final Classification

```text
AIGOL_HUMAN_CLARIFICATION_AND_APPROVAL_POLICY_STATUS = CERTIFIED
```

## Purpose

This policy defines how AiGOL governs human clarification and human approval interactions for provider-assisted native development.

It governs:

```text
Human
AiGOL
Provider
AiGOL
Human
```

The policy does not implement runtime behavior.

## Authority Model

Human remains:

```text
FINAL AUTHORITY
```

AiGOL remains:

```text
GOVERNANCE ONLY
```

Provider remains:

```text
PROPOSAL ONLY
```

## Clarification Triggers

Human clarification is required when:

- prompt intent is ambiguous;
- domain selection is ambiguous;
- worker family selection is ambiguous;
- milestone type is ambiguous;
- output scope is ambiguous;
- context remains incomplete;
- provider confidence is insufficient;
- proposed target could represent multiple artifact classes;
- provider retry would require unstated assumptions;
- AiGOL cannot resume workflow deterministically.

Example:

```text
create a workstation
```

This must not be resolved automatically when `workstation` could mean:

- domain;
- worker;
- artifact;
- infrastructure component.

## Approval Triggers

Human approval is required when:

- domain is high risk;
- corrected proposal is valid but materially changes scope;
- proposal impacts governance boundaries;
- proposal references execution-sensitive future work;
- proposal references trading, healthcare, legal, critical infrastructure, or public services;
- proposal could affect user-visible authority boundaries;
- proposal requires final authorization before implementation handoff resumes.

High-risk domains include:

- trading;
- healthcare;
- legal;
- critical infrastructure;
- public services.

## Ambiguity Categories

Ambiguity categories:

- `INTENT_AMBIGUITY`;
- `DOMAIN_AMBIGUITY`;
- `WORKER_AMBIGUITY`;
- `MILESTONE_AMBIGUITY`;
- `OUTPUT_SCOPE_AMBIGUITY`;
- `CONTEXT_INCOMPLETENESS`;
- `PROVIDER_CONFIDENCE_INSUFFICIENT`;
- `AUTHORITY_BOUNDARY_AMBIGUITY`;
- `RESUME_PATH_AMBIGUITY`.

## Confidence Policy

Provider confidence is insufficient when:

- provider returns multiple conflicting interpretations;
- provider cannot identify one target milestone;
- provider confidence is missing;
- provider confidence is below the configured policy threshold;
- provider confidence conflicts with deterministic registry resolution;
- provider confidence depends on unstated context.

Default policy threshold:

```text
provider_confidence_threshold = HIGH
```

Numerical thresholds remain a future policy extension.

## Clarification Lifecycle

Clarification lifecycle:

1. AiGOL detects ambiguity or incomplete context.
2. AiGOL creates `HUMAN_CLARIFICATION_REQUIRED_ARTIFACT_V1`.
3. AiGOL presents a bounded clarification prompt to the human.
4. Human provides clarification.
5. AiGOL records `HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1`.
6. AiGOL validates the response against the original ambiguity category.
7. AiGOL updates workflow resume instructions.
8. AiGOL resumes from the earliest deterministic safe stage.

## Approval Lifecycle

Approval lifecycle:

1. AiGOL detects approval requirement.
2. AiGOL creates `HUMAN_APPROVAL_REQUIRED_ARTIFACT_V1`.
3. AiGOL presents proposal, hashes, context, risk category, and approval reason.
4. Human approves, rejects, or requests clarification.
5. AiGOL records `HUMAN_APPROVAL_DECISION_ARTIFACT_V1`.
6. If approved, workflow may resume from the governed continuation point.
7. If rejected, workflow fails closed or returns to repair depending on policy.
8. If clarification is requested, workflow enters clarification lifecycle.

## Replay Requirements

Replay must preserve:

- clarification request id;
- clarification reason;
- ambiguity category;
- human response reference;
- human response hash;
- approval request id;
- approval reason;
- approval decision;
- approval decision hash;
- canonical chain id;
- resume stage;
- resume input references;
- provider request hashes;
- proposal hashes;
- context hashes.

## Resume Behavior

After clarification, AiGOL may resume only from:

- task intake;
- context assembly;
- domain and worker resolution;
- provider proposal production;
- provider proposal repair and retry;
- implementation handoff.

Resume must fail closed when:

- clarification does not resolve ambiguity;
- clarification changes milestone id without explicit human confirmation;
- approval is missing for a high-risk domain;
- approval decision hash mismatches;
- resume target cannot be reconstructed;
- replay continuity fails.

## Non-Goals

This policy does not:

- invoke providers;
- implement clarification runtime;
- implement approval runtime;
- authorize implementation;
- dispatch workers;
- execute;
- mutate governance;
- mutate replay outside future append-only evidence.

## Certification Judgment

Clarification and approval behavior is constitutionally defined.

The remaining implementation gap is conversation CLI routing into provider proposal production, repair/retry, clarification, and approval surfaces.

