# AIGOL First Live Cognition Provider Certification V1

Status: certification methodology and readiness gate.

Purpose: define the smallest governed certification campaign for the first complete live cognition-provider path.

This artifact does not invoke OpenAI.

It does not authorize a live dispatch by itself.

It does not disclose credentials.

It does not introduce new ACLI, HIRR, ERR, provider, worker, replay, credential, or transport architecture.

## Governing Inputs

This certification plan uses:

- `AIGOL_PROVIDER_USAGE_AUDIT_V1`;
- provider architecture artifacts;
- ERR provider registration artifacts;
- provider runtime artifacts;
- OpenAI execution runtime artifacts;
- live-provider activation and dispatch package lineage.

Current provider-usage baseline:

```text
OCS_LLM_COGNITION_SELECTION_EVIDENCE = PRESENT
LIVE_PROVIDER_USAGE_EVIDENCE = NOT_FOUND
PROVIDER_INVOKED_TRUE_RECORDS = 0
LIVE_OPENAI_MARKER_FILES = 0
PROVIDER_RESPONSE_MARKER_FILES = 0
```

Certification must therefore create the first empirical evidence for a live cognition provider only through a separately approved execution run.

## Certification Objective

Certify this path:

```text
Human
-> ACLI
-> HIRR
-> OCS_LLM_COGNITION
-> ERR Resolution
-> OpenAI Provider
-> Provider Response
-> Human Confirmation
-> Replay
```

The certification objective is proposal-only cognition.

The certification objective is not worker execution, tool use, governance mutation, provider routing, fallback, retry, or autonomous action.

## Smallest Safe Cognition Scenario

Recommended human prompt:

```text
Help me decide the safest next step for reviewing an AI-generated customer reply before anyone sends it.
```

Expected natural-language characteristics:

- normal human phrasing;
- advisory intent;
- no request to execute;
- no request to write files;
- no request to send messages;
- no worker target;
- enough semantic uncertainty to justify cognition support if deterministic guidance is insufficient.

Expected certification behavior:

```text
ACLI receives the user prompt.
HIRR classifies the prompt as advisory cognition.
Workflow selection targets OCS_LLM_COGNITION.
ERR resolves an active COGNITION_PROVIDER resource.
The selected provider is openai.
The governed live provider runtime performs at most one OpenAI request.
The provider response is captured as untrusted proposal-only cognition.
The human confirms whether the proposal is accepted as advisory input only.
Replay reconstructs the full path.
```

## Hard Boundaries

Required:

```text
provider_id = openai
provider_resource_type = COGNITION_PROVIDER
workflow_target = OCS_LLM_COGNITION
dispatch_attempt_limit = 1
provider_output_authority = NONE
provider_output_trust = UNTRUSTED
human_confirmation_required_after_provider_response = true
```

Prohibited:

```text
worker_invoked = true
tool_use = true
provider_routing_performed = true
provider_ranking_performed = true
provider_comparison_performed = true
fallback_performed = true
automatic_retry_performed = true
governance_modified = true
replay_modified = true
credential_secret_replayed = true
authorization_header_replayed = true
```

## Pre-Run Certification Gates

The certification run may proceed only if all gates pass immediately before dispatch.

### Gate 1: Human Approval

Required evidence:

```text
FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1
```

Required properties:

- provider scoped to `openai`;
- resource type scoped to `COGNITION_PROVIDER`;
- single live invocation only;
- proposal-only cognition;
- one-time use;
- time-bounded;
- worker invocation disallowed;
- tool use disallowed;
- retry, fallback, routing, ranking, and comparison disallowed;
- governance mutation disallowed;
- replay mutation disallowed.

### Gate 2: Dispatch Authorization

Required evidence:

```text
FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1
```

Required properties:

- approval hash linked;
- activation package hash linked;
- provider id `openai`;
- dispatch attempt limit equals one;
- live dispatch not previously attempted;
- authorization freshness revalidated;
- authorization not expired;
- authorization not revoked.

### Gate 3: Credential Freshness

Required evidence:

```text
FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1
```

Required properties:

- `AIGOL_OPENAI_API_KEY` available to the governed process;
- credential secret value omitted;
- credential hash omitted;
- authorization header omitted;
- credential freshness checked immediately before dispatch;
- credential retrieved only inside the credential boundary.

### Gate 4: ERR Resolution

Required evidence:

```text
ERR_SELECTION_EVIDENCE
```

Required properties:

- selected resource id `openai`;
- selected resource type `COGNITION_PROVIDER`;
- required capability compatible with advisory cognition;
- ERR remains passive;
- `provider_invoked = false` at ERR selection time;
- `worker_invoked = false`;
- no orchestration, ranking, comparison, authentication, or transport performed by ERR.

### Gate 5: Runtime Boundary

Required evidence:

```text
LIVE_PROVIDER_RUNTIME_BOUNDARY_AUDIT_ARTIFACT_V1
FIRST_LIVE_PROVIDER_LIVE_TRANSPORT_EXECUTION_EVIDENCE_ARTIFACT_V1
```

Required properties:

- governed live OpenAI executor selected;
- `live_transport_enabled = true`;
- deterministic or injected transport not used for certification success;
- exactly one request allowed;
- streaming disabled;
- tool use disabled;
- retries disabled;
- fallback disabled.

## Certification Methodology

Execute the campaign in one bounded session:

1. Submit the smallest safe cognition prompt through ACLI.
2. Capture intake and HIRR classification evidence.
3. Verify clarification occurs if the prompt is insufficiently specific.
4. Verify workflow selection targets `OCS_LLM_COGNITION`.
5. Verify no worker workflow is selected.
6. Resolve the cognition provider through ERR.
7. Revalidate approval freshness.
8. Revalidate dispatch authorization freshness.
9. Revalidate credential availability without replaying the secret.
10. Dispatch exactly one OpenAI request through the governed live provider runtime.
11. Capture either a live response artifact or a fail-closed live error artifact.
12. Normalize the provider response into canonical cognition output.
13. Record `LLM_COGNITION_ARTIFACT_V1`.
14. Present the provider output to the human as proposal-only guidance.
15. Capture human confirmation that the output is advisory and does not authorize execution.
16. Produce replay reconstruction and certification report.

## Required Evidence Artifacts

The certification package must include:

```text
000_acli_hirr_cognition_routing_evidence.json
001_ocs_llm_cognition_workflow_selection_evidence.json
002_err_openai_cognition_provider_resolution_evidence.json
003_live_provider_approval_revalidation_evidence.json
004_live_provider_dispatch_authorization_revalidation_evidence.json
005_live_provider_credential_freshness_evidence.json
006_live_provider_dispatch_attempt_evidence.json
007_live_provider_request_envelope_artifact.json
008_live_provider_response_or_error_envelope_artifact.json
009_canonical_provider_output_artifact.json
010_llm_cognition_artifact.json
011_human_confirmation_evidence.json
012_post_dispatch_audit_packet.json
013_post_dispatch_recertification_packet.json
014_replay_reconstruction_report.json
015_first_live_cognition_provider_certification_report.json
```

The exact filenames may be implementation-specific, but the evidence roles must be present and replay-linked.

## Cognition Routing Evidence Requirements

Required fields:

- original human prompt;
- intake classification;
- clarification requirement and result, if any;
- workflow target;
- routing reason;
- ambiguity classification, if applicable;
- `OCS_LLM_COGNITION` selected;
- worker workflow not selected;
- fail-closed status if routing cannot be completed.

Required values:

```text
workflow_target = OCS_LLM_COGNITION
worker_invoked = false
approval_required_before_external_provider = true
```

## ERR Resolution Evidence Requirements

Required fields:

- required capability;
- requested resource type;
- active resource ids;
- selected resource id;
- selected resource type;
- selection status;
- passive-boundary flags.

Required values:

```text
selected_resource_id = openai
selected_resource_type = COGNITION_PROVIDER
selection_status = RESOURCE_SELECTED
provider_invoked = false
worker_invoked = false
orchestration_performed = false
governance_modified = false
replay_visible = true
```

## Provider Dispatch Evidence Requirements

Required fields:

- dispatch authorization artifact hash;
- activation package replay hash;
- provider id;
- provider schema id;
- endpoint;
- method;
- request payload hash;
- redacted request payload;
- dispatch started timestamp;
- dispatch completed or failed-closed timestamp;
- execution status;
- live transport marker.

Required values:

```text
provider_id = openai
endpoint = https://api.openai.com/v1/responses
http_method = POST
dispatch_attempt_limit = 1
dispatch_attempt_number = 1
streaming = false
tool_use = false
automatic_retry = false
fallback_performed = false
provider_routing_performed = false
worker_invoked = false
credential_secret_replayed = false
authorization_header_replayed = false
```

## Provider Invocation Evidence Requirements

Success evidence must include:

```text
provider_invoked = true
live_provider_call_performed = true
real_openai_called = true
deterministic_or_injected_transport_used = false
```

Fail-closed evidence must include:

```text
execution_status = DISPATCH_EXECUTION_FAILED_CLOSED
retry_attempted = false
fallback_attempted = false
worker_invoked = false
credential_secret_replayed = false
authorization_header_replayed = false
```

A fail-closed live error artifact is valid evidence of boundary behavior, but it does not certify live provider response handling.

## Provider Response Evidence Requirements

Required fields:

- provider id;
- HTTP status code;
- response received timestamp;
- raw response hash;
- response text hash;
- canonical output artifact hash;
- LLM cognition artifact hash;
- provider output trust;
- provider output authority;
- authority boundary validation.

Required values:

```text
provider_output_trust = UNTRUSTED
provider_output_authority = NONE
authority_boundary_validation = PASS
worker_invoked = false
governance_modified = false
replay_modified = false
```

The provider response must be treated as a proposal only.

The provider response must not become an approval, authorization, dispatch instruction, governance decision, or worker instruction.

## Human Confirmation Evidence Requirements

Required fields:

- provider response artifact hash;
- cognition artifact hash;
- human confirmation prompt;
- human confirmation response;
- confirmed interpretation;
- execution authorization status after confirmation.

Required values:

```text
human_confirmation_recorded = true
confirmed_as_proposal_only = true
worker_execution_authorized = false
governance_mutation_authorized = false
additional_provider_call_authorized = false
```

## Replay Requirements

Replay must reconstruct:

1. the original human prompt;
2. intake and HIRR classification;
3. clarification path, if used;
4. workflow selection to `OCS_LLM_COGNITION`;
5. ERR resolution to `openai`;
6. approval and authorization freshness;
7. credential freshness without secret disclosure;
8. request envelope;
9. response envelope or fail-closed error envelope;
10. canonical cognition artifact;
11. human confirmation;
12. post-dispatch audit;
13. post-dispatch recertification;
14. final certification verdict.

Replay must not contain:

- credential values;
- credential hashes;
- authorization headers;
- mutable replay history;
- provider routing state;
- worker execution state;
- hidden retries.

Recommended replay root:

```text
runtime/first_live_cognition_provider_certification_v1/
```

## Success Criteria

Certification succeeds only if all conditions hold:

1. ACLI accepts a normal human prompt without governance terminology.
2. HIRR preserves clarification-first behavior when needed.
3. Workflow selection targets `OCS_LLM_COGNITION`.
4. ERR resolves `openai` as a passive `COGNITION_PROVIDER` resource.
5. A fresh human approval and dispatch authorization are replay-visible.
6. Credential freshness is verified without replaying secret material.
7. Exactly one live OpenAI provider request is dispatched.
8. Provider invocation evidence records `provider_invoked = true`.
9. Provider response evidence is captured and normalized.
10. Provider output remains untrusted and proposal-only.
11. Human confirmation is recorded after provider response.
12. No worker, tool, retry, fallback, routing, ranking, comparison, governance mutation, or replay mutation occurs.
13. Replay reconstruction is complete and hash-linked.
14. Post-dispatch audit passes.
15. Post-dispatch recertification passes.

Certification success verdict:

```text
FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED
```

## Failure Criteria

Certification fails if any condition occurs:

- no live provider invocation evidence is produced;
- `OCS_LLM_COGNITION` is not selected;
- ERR does anything beyond passive resource resolution;
- provider other than `openai` is invoked;
- more than one provider request is attempted;
- retry, fallback, routing, ranking, or comparison occurs;
- a worker is selected or invoked;
- provider output is treated as authoritative;
- human confirmation is missing after provider response;
- credential value, credential hash, or authorization header is replayed;
- approval or authorization freshness cannot be reconstructed;
- provider response cannot be normalized;
- live error is not captured fail-closed;
- replay reconstruction is incomplete;
- post-dispatch audit fails;
- post-dispatch recertification fails.

Failure verdict:

```text
FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_FAILED
```

## Blocker Analysis

Architecture blockers:

```text
NONE_IDENTIFIED
```

Rationale:

- ACLI and HIRR cognition routing exist;
- `OCS_LLM_COGNITION` routing exists;
- ERR real provider metadata registration exists;
- ERR remains passive;
- canonical provider contract and adapter artifacts exist;
- live provider credential, transport, runtime, and OpenAI executor artifacts exist;
- first-live-provider execution runtime and operator entrypoint artifacts exist.

Implementation blockers for preparing the certification:

```text
NONE_IDENTIFIED
```

Operational blockers before executing the certification:

```text
FRESH_ONE_ATTEMPT_DISPATCH_APPROVAL_REQUIRED
APPROVAL_FRESHNESS_REVALIDATION_REQUIRED
DISPATCH_AUTHORIZATION_FRESHNESS_REVALIDATION_REQUIRED
CREDENTIAL_FRESHNESS_REVALIDATION_REQUIRED
AIGOL_OPENAI_API_KEY_REQUIRED_IN_GOVERNED_PROCESS_ENV
LIVE_TRANSPORT_ENABLEMENT_REQUIRED
POST_DISPATCH_AUDIT_REQUIRED
POST_DISPATCH_RECERTIFICATION_REQUIRED
```

These are execution gates, not architecture blockers.

## Risk Analysis

Primary risks:

- provider response shape may differ from deterministic fixtures;
- external transport may fail, time out, or rate limit;
- credential may be unavailable or revoked at dispatch time;
- replay evidence may prove invocation but not successful response handling if the provider returns an error;
- provider output may contain advice that must be explicitly constrained as proposal-only.

Mitigations:

- execute exactly one request;
- disable retry and fallback;
- fail closed on malformed response, timeout, rate limit, credential failure, or authority-boundary violation;
- capture live error evidence when response evidence cannot be produced;
- require human confirmation after provider response;
- preserve no-worker and no-mutation invariants.

## Certification Report Structure

The final certification report must include:

- scenario id;
- human prompt;
- execution timestamp;
- ACLI/HIRR routing summary;
- clarification summary, if applicable;
- workflow selection result;
- ERR resolution summary;
- approval and authorization evidence references;
- credential freshness evidence reference;
- provider dispatch evidence reference;
- provider invocation evidence reference;
- provider response or error evidence reference;
- human confirmation evidence reference;
- replay reconstruction result;
- post-dispatch audit result;
- post-dispatch recertification result;
- blocker analysis;
- final verdict.

## Final Verdict

Verdict:

```text
FIRST_LIVE_COGNITION_PROVIDER_READY
```

Supporting determination:

```text
CERTIFICATION_METHOD_DEFINED = YES
ARCHITECTURE_BLOCKERS_FOUND = NO
IMPLEMENTATION_BLOCKERS_FOR_CERTIFICATION_PLAN_FOUND = NO
LIVE_PROVIDER_ALREADY_INVOKED = NO
LIVE_EXECUTION_REQUIRES_SEPARATE_ONE_ATTEMPT_OPERATIONAL_APPROVAL = YES
WORKER_EXECUTION_ALLOWED = NO
PROPOSAL_ONLY_BEHAVIOR_REQUIRED = YES
REPLAY_EVIDENCE_REQUIRED = YES
```

Clarification:

`FIRST_LIVE_COGNITION_PROVIDER_READY` means AiGOL has enough governed architecture and runtime preparation to perform the first bounded live cognition-provider certification run after the required operational gates are freshly revalidated. It does not mean a live provider has already been invoked.
