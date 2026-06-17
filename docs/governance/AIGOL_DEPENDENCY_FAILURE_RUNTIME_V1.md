# AIGOL Dependency Failure Runtime V1

Status: runtime architecture definition.

Purpose: define the smallest universal runtime pattern for dependency failures across AiGOL capabilities.

This artifact does not implement runtime code.

It does not redesign ERR.

It does not redesign ACLI.

It does not redesign provider architecture.

It does not authorize silent degradation, fallback, retry, provider routing, worker substitution, governance mutation, or replay mutation.

## Context

During `AIGOL_FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_V1`, AiGOL correctly failed closed because:

```text
AIGOL_OPENAI_API_KEY
```

was not present in the governed process environment.

The certification demonstrated:

```text
provider_selected = openai
provider_invoked = false
provider_response_received = false
replay_reconstructed = true
worker_invoked = false
failure_reason = first live provider operator entrypoint failed closed: credential unavailable
```

The behavior was architecturally correct, but the failure information was primarily useful to developers and reviewers.

AiGOL needs a standardized dependency-failure runtime so operators and normal users can understand:

- what stopped;
- why it stopped;
- what dependency is missing or unavailable;
- who can fix it;
- how to verify remediation;
- what to retry after remediation.

## Goal

Define a universal dependency-failure runtime for:

- cognition providers;
- worker providers;
- API integrations;
- databases;
- files;
- authentication systems;
- external services;
- future dependency classes.

The runtime must transform low-level fail-closed dependency evidence into replay-safe, user-readable, and operator-actionable failure records.

## Non-Goals

This runtime does not:

- perform dependency provisioning;
- store secrets;
- retrieve credentials directly;
- invoke providers;
- invoke workers;
- retry automatically;
- fall back automatically;
- guess missing context;
- silently degrade output quality;
- replace capability-specific approval or authorization;
- expand ERR;
- create a new orchestration layer.

## Core Principle

When a required dependency is unavailable, AiGOL must:

```text
FAIL_CLOSED
EXPLAIN_DEPENDENCY
EXPLAIN_IMPACT
EXPLAIN_REMEDIATION
PROVIDE_LOCATION_IF_KNOWN
PROVIDE_VERIFICATION_GUIDANCE
PROVIDE_RETRY_GUIDANCE
RECORD_REPLAY_EVIDENCE
```

AiGOL must not:

```text
SILENTLY_CONTINUE
SILENTLY_DEGRADE
GUESS
HIDE_CAUSE
INVOKE_UNAUTHORIZED_SUBSTITUTE
MUTATE_REPLAY
MUTATE_GOVERNANCE
```

## Runtime Position

The dependency failure runtime sits after a capability-specific boundary detects failure and before the failure is communicated or certified.

Generic position:

```text
capability request
-> dependency resolution or dependency check
-> dependency failure detected
-> fail closed
-> dependency failure runtime normalization
-> user-facing failure structure
-> operator-facing failure structure
-> replay evidence
-> retry guidance
```

Provider example:

```text
Human
-> ACLI
-> HIRR
-> OCS_LLM_COGNITION
-> ERR selects openai
-> operator credential check fails
-> dependency failure runtime records MISSING_CREDENTIAL
-> provider invocation stopped
-> user and operator receive bounded explanation
-> replay reconstructs stopped path
```

Worker example:

```text
Human
-> ACLI
-> workflow selection
-> ERR worker lookup
-> worker dependency missing or unavailable
-> dependency failure runtime records MISSING_WORKER or DEPENDENCY_UNAVAILABLE
-> worker invocation stopped
-> replay reconstructs stopped path
```

## Runtime Responsibilities

The dependency failure runtime must:

1. accept a dependency failure report from a capability-specific boundary;
2. classify the failure using a bounded taxonomy;
3. preserve fail-closed status;
4. identify the affected capability;
5. identify the missing or unavailable dependency;
6. identify the dependency location when safe and available;
7. explain why the dependency is required;
8. explain what could not execute;
9. explain whether quality would be reduced if execution continued;
10. state that execution was stopped;
11. provide remediation owner guidance;
12. provide verification guidance;
13. provide retry guidance;
14. produce replay-safe evidence;
15. redact secrets and sensitive values;
16. preserve governance, replay, ERR, ACLI, provider, worker, and authority boundaries.

The runtime must not:

- perform the remediation;
- assume remediation succeeded;
- re-run the failed action automatically;
- infer missing secrets;
- expose credential values;
- convert failure communication into execution approval.

## Dependency Taxonomy

Dependency classifications:

| Classification | Detection | Impact | Remediation Expectation |
| --- | --- | --- | --- |
| `MISSING_CREDENTIAL` | Required credential reference is absent, empty, revoked, or not retrievable | Stop external provider, API, database, authentication, or service call | Operator or secret authority provisions the credential in the approved location |
| `MISSING_PROVIDER` | Required provider metadata cannot be resolved or selected | Stop cognition or provider-backed capability | Operator or maintainer registers or activates a provider through approved governance |
| `MISSING_WORKER` | Required worker metadata cannot be resolved or worker is unavailable | Stop execution workflow requiring that worker | Operator or maintainer registers, activates, or restores the worker |
| `MISSING_CONFIGURATION` | Required config key, file, endpoint, model id, policy reference, or runtime flag is absent | Stop capability requiring configuration | Operator updates approved configuration source |
| `UNREACHABLE_SERVICE` | Network, transport, DNS, timeout, service down, rate limit, or service endpoint failure | Stop external dependency call or record fail-closed external error | Operator checks service health, network, endpoint, quota, or provider status |
| `AUTHORIZATION_FAILURE` | Approval, authorization, token scope, permission, policy, or access check fails | Stop protected action or external call | Human approver, operator, or administrator grants fresh approved authorization |
| `DEPENDENCY_UNAVAILABLE` | Dependency exists but is disabled, inactive, locked, busy, unhealthy, or currently unusable | Stop capability relying on that dependency | Operator restores availability or selects approved remediation path |
| `UNKNOWN_DEPENDENCY_FAILURE` | Dependency failure is detected but cannot be safely classified | Stop capability and escalate to operator review | Operator investigates logs and replay evidence; no automatic retry |

All classifications must fail closed unless a separate governance artifact explicitly authorizes a narrower safe continuation mode.

## Classification Details

### MISSING_CREDENTIAL

Detection examples:

- `AIGOL_OPENAI_API_KEY` absent;
- credential reference empty;
- credential policy points to unsupported reference;
- credential retrieval fails;
- credential revoked or rotated out of current approval scope.

Required impact explanation:

- external invocation cannot proceed;
- output quality cannot be silently reduced by using a weaker or fake provider;
- execution stopped before external dispatch.

Required remediation:

- provision credential in approved location;
- keep credential out of replay and repository;
- revalidate credential presence without printing its value.

### MISSING_PROVIDER

Detection examples:

- ERR has no active `COGNITION_PROVIDER` for required capability;
- provider id requested by authorization is not registered;
- provider is inactive.

Required impact explanation:

- cognition-provider path cannot execute;
- AiGOL cannot substitute another provider without explicit governance.

Required remediation:

- register or activate provider metadata through governed provider registration;
- verify ERR selection evidence.

### MISSING_WORKER

Detection examples:

- ERR has no active `EXECUTION_WORKER` for required capability;
- worker contract is missing;
- worker runtime is unavailable.

Required impact explanation:

- worker-backed execution cannot occur;
- AiGOL must not use another worker unless workflow governance approves it.

Required remediation:

- register, restore, or certify the worker;
- verify worker selection and authorization evidence.

### MISSING_CONFIGURATION

Detection examples:

- missing model id;
- missing endpoint;
- missing database DSN reference;
- missing file path policy;
- required runtime flag not enabled;
- missing provider schema reference.

Required impact explanation:

- configured capability cannot execute reliably;
- continuing would require guessing or using defaults not authorized by governance.

Required remediation:

- fix approved configuration source;
- verify configuration is visible to the governed process.

### UNREACHABLE_SERVICE

Detection examples:

- timeout;
- DNS failure;
- connection failure;
- HTTP transport failure;
- provider rate limit;
- database unavailable;
- API endpoint unavailable.

Required impact explanation:

- external dependency could not be reached;
- execution stopped or failed closed after a bounded attempt;
- no silent retry, fallback, or quality degradation occurred.

Required remediation:

- verify network/service health;
- verify endpoint and quota;
- retry only through a new approved attempt if the action is governed.

### AUTHORIZATION_FAILURE

Detection examples:

- missing approval;
- expired authorization;
- revoked authorization;
- insufficient scope;
- confirmation missing;
- permission denied.

Required impact explanation:

- protected action or external dependency use is not authorized;
- execution stopped before the protected boundary.

Required remediation:

- obtain fresh human approval or administrator permission;
- re-run the governed authorization workflow.

### DEPENDENCY_UNAVAILABLE

Detection examples:

- dependency registered but inactive;
- worker disabled;
- database locked;
- file not accessible;
- service unhealthy;
- provider in maintenance state.

Required impact explanation:

- dependency exists but cannot currently support the requested capability;
- AiGOL stopped rather than pretending execution succeeded.

Required remediation:

- restore dependency health or activate it through approved controls;
- verify availability state.

### UNKNOWN_DEPENDENCY_FAILURE

Detection examples:

- boundary reports failure without safe classification;
- unexpected dependency exception;
- incomplete failure evidence.

Required impact explanation:

- AiGOL cannot safely determine the dependency state;
- execution stopped because continuing would require guessing.

Required remediation:

- operator reviews replay and runtime logs;
- maintainer improves classification if recurring;
- no automatic retry.

## Evidence Model

Artifact type:

```text
DEPENDENCY_FAILURE_RUNTIME_ARTIFACT_V1
```

Required fields:

- `artifact_type`;
- `runtime_version`;
- `failure_id`;
- `created_at`;
- `detected_by_runtime`;
- `source_artifact_hash`;
- `source_replay_reference`;
- `capability_id`;
- `capability_type`;
- `workflow_target`;
- `dependency_classification`;
- `dependency_id`;
- `dependency_type`;
- `dependency_required_for`;
- `dependency_location_type`;
- `dependency_location_reference`;
- `location_safe_to_display`;
- `failure_reason_code`;
- `failure_reason_summary`;
- `execution_stopped`;
- `provider_selected`;
- `provider_invoked`;
- `worker_selected`;
- `worker_invoked`;
- `external_call_attempted`;
- `quality_degradation_prevented`;
- `silent_degradation_performed`;
- `fallback_performed`;
- `automatic_retry_performed`;
- `governance_modified`;
- `replay_modified`;
- `secret_value_replayed`;
- `secret_hash_replayed`;
- `authorization_header_replayed`;
- `user_message`;
- `operator_message`;
- `remediation_owner`;
- `remediation_action`;
- `verification_guidance`;
- `retry_guidance`;
- `replay_visible`;
- `artifact_hash`.

Required invariant values:

```text
execution_stopped = true
silent_degradation_performed = false
governance_modified = false
replay_modified = false
secret_value_replayed = false
authorization_header_replayed = false
replay_visible = true
```

## Replay Model

Replay must reconstruct:

1. original capability request;
2. workflow or runtime target;
3. dependency selected or requested;
4. dependency check performed;
5. failure classification;
6. fail-closed decision;
7. user-facing failure message;
8. operator-facing failure message;
9. remediation and verification guidance;
10. retry guidance;
11. no-secret/no-replay-mutation invariants.

Replay must not contain:

- secret values;
- secret hashes;
- authorization headers;
- raw tokens;
- unredacted service responses containing sensitive material;
- mutable dependency state claims not backed by evidence.

Recommended replay placement:

```text
runtime/<campaign_or_session>/dependency_failures/<failure_id>/
```

Required replay packet:

```text
000_dependency_failure_source_reference.json
001_dependency_failure_runtime_artifact.json
002_dependency_failure_user_message.json
003_dependency_failure_operator_message.json
004_dependency_failure_replay_reconstruction.json
```

## Failure Communication Model

The runtime must produce two communication structures.

### User-Facing Failure Structure

Purpose: explain the stopped capability in normal language without exposing secrets or internal architecture unnecessarily.

Required fields:

- `summary`;
- `what_happened`;
- `what_cannot_continue`;
- `why_stopped`;
- `safe_next_step`;
- `operator_needed`;

Example:

```text
I could not complete the provider-backed advice step because the required OpenAI credential is not available to the governed runtime. I stopped before contacting the provider, so no external request was sent. An operator needs to provision the credential, then the request can be retried through a new governed attempt.
```

User-facing communication must not include:

- credential values;
- stack traces;
- internal secret references unless safe and necessary;
- misleading claims that the task succeeded;
- fallback advice pretending to be provider-backed.

### Operator-Facing Failure Structure

Purpose: provide actionable remediation for the person responsible for the dependency.

Required fields:

- `classification`;
- `missing_or_failed_dependency`;
- `dependency_location`;
- `required_capability`;
- `affected_runtime`;
- `failure_gate`;
- `stopped_before`;
- `expected_owner`;
- `remediation_steps`;
- `verification_command_or_check`;
- `retry_instruction`;
- `evidence_references`;

Example:

```text
classification = MISSING_CREDENTIAL
missing_or_failed_dependency = AIGOL_OPENAI_API_KEY
dependency_location = governed process environment
affected_runtime = AIGOL_FIRST_LIVE_PROVIDER_OPERATOR_ENTRYPOINT_V1
failure_gate = credential availability before live dispatch
stopped_before = OpenAI provider invocation
expected_owner = human operator or organization secret authority
verification = confirm AIGOL_OPENAI_API_KEY_PRESENT = true without printing the value
retry = re-run the governed one-attempt certification after fresh authorization
```

## Governance Implications

Dependency failure normalization is governance-preserving only if:

- fail-closed behavior is preserved;
- dependency messages do not authorize execution;
- remediation guidance does not bypass approval;
- retry guidance requires fresh approval when the failed capability is governed;
- replay evidence remains immutable;
- secret values remain outside replay;
- ERR remains passive;
- provider and worker runtimes retain their own boundaries;
- normal users are not asked to fix operator-only dependencies unless they are the operator.

The runtime must distinguish:

```text
DEPENDENCY_FAILURE_EXPLANATION != EXECUTION_APPROVAL
REMEDIATION_GUIDANCE != AUTHORIZATION
RETRY_GUIDANCE != AUTOMATIC_RETRY
```

## Generic Dependency Classification Model

A generic dependency classification model should exist.

Rationale:

- the same failure pattern appears across providers, workers, files, databases, APIs, and auth systems;
- operators need consistent remediation language;
- users need consistent stop/impact language;
- replay needs stable evidence fields independent of dependency type;
- future dependency classes can extend classification without redesigning ERR or ACLI.

Minimum model:

```text
dependency_classification
dependency_type
dependency_id
dependency_location_type
dependency_location_reference
capability_type
capability_id
failure_gate
execution_stopped
remediation_owner
verification_guidance
retry_guidance
```

Allowed dependency types:

- `COGNITION_PROVIDER`;
- `EXECUTION_WORKER`;
- `API_INTEGRATION`;
- `DATABASE`;
- `FILE_RESOURCE`;
- `AUTHENTICATION_SYSTEM`;
- `EXTERNAL_SERVICE`;
- `CONFIGURATION`;
- `UNKNOWN_DEPENDENCY`.

Allowed location types:

- `ENVIRONMENT_VARIABLE`;
- `CONFIGURATION_FILE`;
- `ERR_PROVIDER_REGISTRATION`;
- `ERR_WORKER_REGISTRATION`;
- `CREDENTIAL_SOURCE`;
- `SERVICE_ENDPOINT`;
- `DATABASE_CONNECTION_REFERENCE`;
- `FILE_PATH`;
- `AUTHORIZATION_ARTIFACT`;
- `UNKNOWN_LOCATION`.

## Certification Requirements

Focused certification must prove:

1. missing credential becomes `MISSING_CREDENTIAL`;
2. missing provider becomes `MISSING_PROVIDER`;
3. missing worker becomes `MISSING_WORKER`;
4. missing configuration becomes `MISSING_CONFIGURATION`;
5. unreachable service becomes `UNREACHABLE_SERVICE`;
6. authorization failure becomes `AUTHORIZATION_FAILURE`;
7. inactive or unhealthy dependency becomes `DEPENDENCY_UNAVAILABLE`;
8. unknown dependency failure becomes `UNKNOWN_DEPENDENCY_FAILURE`;
9. all classifications fail closed;
10. no classification silently degrades;
11. user-facing message is safe and understandable;
12. operator-facing message contains location, owner, verification, and retry guidance;
13. replay reconstructs the failure;
14. secrets are not replayed;
15. authorization headers are not replayed;
16. governance and replay are not mutated;
17. ERR remains passive;
18. provider and worker boundaries remain intact.

Minimum initial certification scenario:

```text
MISSING_CREDENTIAL
dependency_id = AIGOL_OPENAI_API_KEY
capability_type = COGNITION_PROVIDER
provider_selected = openai
provider_invoked = false
execution_stopped = true
```

## Success Criteria

The dependency failure runtime is acceptable if:

- it produces standardized evidence for dependency failures;
- it produces both user-facing and operator-facing failure structures;
- it preserves fail-closed behavior;
- it preserves no-secret replay;
- it does not add fallback or retry behavior;
- it does not redesign ERR, ACLI, provider runtime, or worker runtime;
- it can represent the failed first live cognition-provider certification cleanly;
- it can extend to future dependency classes through taxonomy entries rather than architecture redesign.

## Failure Criteria

The runtime definition fails if:

- it permits silent continuation;
- it permits silent quality degradation;
- it hides the dependency cause;
- it stores secrets or headers in replay;
- it authorizes retry automatically;
- it uses ERR as a credential or execution system;
- it asks normal users to perform operator-only remediation without context;
- it cannot represent provider, worker, file, database, API, auth, and service dependencies through the same evidence shape.

## Final Verdict

Verdict:

```text
DEPENDENCY_FAILURE_RUNTIME_DEFINED
```

Supporting determinations:

```text
UNIVERSAL_RUNTIME_SCOPE_DEFINED = YES
DEPENDENCY_TAXONOMY_DEFINED = YES
EVIDENCE_MODEL_DEFINED = YES
REPLAY_MODEL_DEFINED = YES
USER_FAILURE_STRUCTURE_DEFINED = YES
OPERATOR_FAILURE_STRUCTURE_DEFINED = YES
CERTIFICATION_REQUIREMENTS_DEFINED = YES
ERR_REDESIGN_REQUIRED = NO
ACLI_REDESIGN_REQUIRED = NO
PROVIDER_ARCHITECTURE_REDESIGN_REQUIRED = NO
```
