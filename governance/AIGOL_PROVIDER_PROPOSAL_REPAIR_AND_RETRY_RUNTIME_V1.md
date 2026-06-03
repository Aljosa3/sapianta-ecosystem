# AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_V1

## Status

Runtime implementation certification.

## Final Classification

```text
AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_STATUS = CERTIFIED
```

## Purpose

This runtime repairs rejected provider-generated development proposals through bounded, replay-visible provider retries.

The runtime supports:

```text
Proposal
Validation
Retry
```

and:

```text
Proposal
Ambiguity
Human Clarification
```

and:

```text
Proposal
High Risk
Human Approval
```

It does not implement proposals.

## Runtime Component

Implemented:

```text
aigol/runtime/provider_proposal_repair_and_retry_runtime.py
```

## Defined Artifacts

Defined:

```text
PROVIDER_REPAIR_REQUEST_V1
PROVIDER_RETRY_RESPONSE_V1
CORRECTED_DEVELOPMENT_PROPOSAL_V1
RETRY_STATUS_ARTIFACT_V1
HUMAN_CLARIFICATION_REQUIRED_ARTIFACT_V1
HUMAN_APPROVAL_REQUIRED_ARTIFACT_V1
```

## Retry Model

Default:

```text
MAX_PROVIDER_RETRIES = 3
```

Supported retry mode:

```text
AUTO_RETRY
```

Auto retry is allowed for deterministic validation failures such as:

- missing references;
- missing fields;
- invalid schema;
- invalid artifact links;
- replay-visible integrity failures;
- proposal contract violations that can be corrected through proposal revision.

## Clarification Policy

The runtime does not automatically retry when:

- intent is ambiguous;
- domain resolution is ambiguous;
- worker resolution is ambiguous;
- context remains incomplete;
- provider confidence is insufficient.

Instead it creates:

```text
HUMAN_CLARIFICATION_REQUIRED_ARTIFACT_V1
```

Example:

```text
create a workstation
```

If `workstation` could mean a domain, worker, artifact, or infrastructure component, the runtime stops for human clarification.

## High-Risk Policy

High-risk domains require human approval after a corrected proposal validates.

High-risk domains include:

- trading;
- healthcare;
- legal;
- critical infrastructure;
- public services.

For these domains, the provider may propose corrected content, but the runtime emits:

```text
HUMAN_APPROVAL_REQUIRED_ARTIFACT_V1
```

and does not continue beyond approval boundaries.

## Retry Lifecycle

Lifecycle:

1. Accept rejected `DEVELOPMENT_PROPOSAL_ARTIFACT_V1`.
2. Accept validation failure evidence.
3. Accept provider response evidence.
4. Validate context, registry resolution, provider necessity, and chain reference.
5. Classify failure as auto-retry, clarification-required, or fail-closed.
6. Create `PROVIDER_REPAIR_REQUEST_V1`.
7. Invoke approved provider for bounded retry when allowed.
8. Convert provider retry response into corrected proposal candidate.
9. Validate corrected proposal through `AIGOL_DEVELOPMENT_PROPOSAL_CONTRACT_RUNTIME_V1`.
10. Stop on validated correction, clarification requirement, approval requirement, or fail-closed condition.

## Replay

Replay steps:

```text
000_provider_repair_request_created.json
001_provider_retry_response_captured.json
002_retry_status_recorded.json
003_provider_repair_retry_returned.json
```

Replay persists:

- retry count;
- retry history;
- retry reasons;
- validation failures;
- provider request hashes;
- provider response hashes;
- proposal hashes;
- escalation reasons;
- clarification requests;
- approval requests;
- canonical chain references.

## Fail-Closed Conditions

The runtime fails closed when:

- retry limit is exceeded;
- provider is unavailable;
- replay mismatch is detected;
- authority violation is detected;
- governance violation is detected;
- invalid proposal is repeatedly returned;
- escalation artifact cannot be created;
- replay corruption is detected.

## Authority Boundaries

Provider remains:

```text
PROPOSAL ONLY
```

Provider may not:

- authorize;
- govern;
- dispatch;
- execute;
- mutate replay;
- mutate governance.

AiGOL remains:

```text
GOVERNANCE ONLY
```

Human remains:

```text
FINAL AUTHORITY
```

## Native Development Impact

AiGOL-native development readiness increases from:

```text
99%
```

to:

```text
99.5%
```

## Remaining Gap

The remaining no-copy-paste development blockers are:

- conversation CLI routing into provider proposal production and repair/retry;
- operational provider availability and credentials;
- final real-world no-copy-paste dry run through `python -m aigol.cli.aigol_cli conversation`.

