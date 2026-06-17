# AIGOL First Real Provider Dispatch Execution Plan V1

Status: operational execution plan.

Purpose: define the exact operator plan for the first real governed OpenAI dispatch.

This artifact is planning only.

It does not invoke OpenAI.

It does not disclose credentials.

It does not create authorization.

It does not mutate runtime, governance, ERR, replay, or provider code.

## Context

Current blocker verdict:

```text
NO_PROVIDER_IMPLEMENTATION_BLOCKERS_REMAIN
```

Allowed dispatch scope:

```text
provider = openai
provider_resource_type = COGNITION_PROVIDER
dispatch_attempt_limit = 1
cognition_only = true
retry = false
fallback = false
provider_routing = false
worker_invocation = false
```

## 1. Exact Runtime Entrypoint

Use only:

```text
aigol.runtime.first_live_provider_operator_entrypoint.run_first_live_provider_operator_entrypoint
```

The live transport must be:

```text
aigol.runtime.live_openai_executor.create_governed_live_openai_executor
```

Required invocation flags:

```text
confirm_dispatch = true
live_transport_enabled = true
```

## 2. Exact Authorization Artifact Required

The operator entrypoint loads the final dispatch authorization artifact from:

```text
{dispatch_authorization_replay_dir}/003_first_live_provider_dispatch_authorization.json
```

Required artifact type:

```text
FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1
```

The artifact must satisfy:

```text
authorization_status = DISPATCH_AUTHORIZED
provider_id = openai
provider_resource_type = COGNITION_PROVIDER
dispatch_count = 1
dispatch_attempt_limit = 1
cognition_only = true
cognition_only_response_required = true
live_dispatch_attempted = false
live_dispatch_performed = false
expires_at >= dispatch created_at
```

Required activation package replay directory:

```text
{activation_package_replay_dir}
```

The dispatch authorization must line up with the activation package hashes for approval, credential availability, audit template, recertification template, and rollback evidence.

## 3. Exact Environment Variables Required

Required:

```text
AIGOL_OPENAI_API_KEY
```

Rules:

```text
credential value must be present only in the governed process environment
credential value must not be committed
credential value must not be printed
credential value must not be written to replay
Authorization header must not be written to replay
credential hash must not be written to replay
```

Optional only if the operator environment requires it:

```text
PYTHONPATH
```

When running from the repository root, no additional Python path should be required.

## 4. Exact Operator Confirmation Step

Before execution, operator must confirm:

```text
I authorize exactly one governed OpenAI cognition-only dispatch attempt through AIGOL_FIRST_LIVE_PROVIDER_OPERATOR_ENTRYPOINT_V1.
```

Runtime parameter:

```text
confirm_dispatch = true
```

If this value is not true, the operator entrypoint must fail closed before dispatch.

## 5. Exact Execution Command

Run from repository root.

Replace the replay directory values with the already prepared activation and dispatch authorization replay directories.

Do not echo `AIGOL_OPENAI_API_KEY`.

```bash
python -c '
from datetime import datetime, timezone

from aigol.runtime.first_live_provider_operator_entrypoint import (
    run_first_live_provider_operator_entrypoint,
)
from aigol.runtime.live_openai_executor import create_governed_live_openai_executor

created_at = datetime.now(timezone.utc).isoformat()

result = run_first_live_provider_operator_entrypoint(
    operator_request_id="FIRST-REAL-OPENAI-DISPATCH-000001",
    operator_id="human.operator",
    human_request="Perform the first governed OpenAI cognition-only dispatch validation.",
    created_at=created_at,
    activation_package_replay_dir="runtime/first_live_provider/activation",
    dispatch_authorization_replay_dir="runtime/first_live_provider/dispatch_authorization",
    execution_replay_dir="runtime/first_live_provider/execution",
    operator_replay_dir="runtime/first_live_provider/operator_entrypoint",
    transport=create_governed_live_openai_executor(),
    confirm_dispatch=True,
    live_transport_enabled=True,
)

print(result["final_status"])
print(result["execution_replay_reference"])
print(result["operator_replay_reference"])
'
```

Expected completed status:

```text
OPERATOR_DISPATCH_COMPLETED
```

Expected fail-closed status:

```text
FAILED_CLOSED
```

## 6. Expected Replay Evidence Artifacts

### Operator Entrypoint Replay

Directory:

```text
{operator_replay_dir}
```

Expected files:

```text
000_first_live_provider_operator_dispatch_request.json
001_first_live_provider_operator_dispatch_result.json
```

### Execution Runtime Replay

Directory:

```text
{execution_replay_dir}
```

Expected files:

```text
000_first_live_provider_execution_approval_revalidation.json
001_first_live_provider_execution_credential_revalidation.json
002_first_live_provider_live_transport_execution_evidence.json
003_first_live_provider_llm_cognition_artifact.json
004_first_live_provider_post_dispatch_audit_packet.json
005_first_live_provider_post_dispatch_recertification_packet.json
006_first_live_provider_rollback_execution.json
007_first_live_provider_dispatch_execution_packet.json
```

### Live Provider Boundary Replay

Directory:

```text
{execution_replay_dir}/live_provider_boundary
```

Success files:

```text
000_live_provider_credential_retrieval_attempt.json
001_live_provider_credential_use_boundary.json
002_live_provider_request_envelope.json
003_live_provider_response_envelope.json
004_live_provider_runtime_boundary_audit.json
```

Fail-closed files:

```text
000_live_provider_credential_retrieval_attempt.json
001_live_provider_request_envelope.json
002_live_provider_error_envelope.json
003_live_provider_runtime_boundary_audit.json
```

### ERR Selection Replay

Directory:

```text
{execution_replay_dir}/live_provider_boundary/err_openai_selection
```

Expected files:

```text
000_err_resource_selection_evidence_recorded.json
001_err_resource_selection_returned.json
```

## 7. Expected Success Path

Success path:

```text
operator confirmation
-> dispatch authorization loaded
-> authorization freshness validated
-> AIGOL_OPENAI_API_KEY presence validated
-> operator dispatch request replay recorded
-> execution runtime invoked
-> approval revalidation replay recorded
-> credential revalidation replay recorded
-> ERR selects openai
-> live credential retrieval evidence recorded without secret
-> live request envelope recorded without Authorization header
-> governed live OpenAI executor performs exactly one HTTPS request
-> live response envelope recorded without secret
-> canonical provider output produced
-> LLM_COGNITION_ARTIFACT_V1 produced
-> post-dispatch audit packet produced
-> post-dispatch recertification packet produced
-> rollback artifact records rollback not required
-> dispatch execution packet produced
-> operator dispatch result recorded
```

Expected success invariants:

```text
live_provider_call_performed = true
provider_invoked = true
worker_invoked = false
credential_secret_replayed = false
authorization_header_replayed = false
automatic_retry_performed = false
fallback_performed = false
provider_routing_performed = false
governance_modified = false
replay_modified = false
```

## 8. Expected Fail-Closed Path

Fail-closed path may occur before or after request preparation.

Expected fail-closed causes:

```text
missing operator confirmation
missing dispatch authorization replay
invalid dispatch authorization hash
expired dispatch authorization
authorization already attempted
authorization already performed
missing AIGOL_OPENAI_API_KEY
unsupported credential reference
unmarked live transport
timeout
rate limit
transport unavailable
malformed response
authority-bearing provider output
replay artifact already exists
```

Expected fail-closed invariants:

```text
no retry
no fallback
no provider routing
no worker invocation
no governance mutation
no replay mutation
no credential replay
no Authorization header replay
rollback evidence produced where execution runtime is reached
```

## 9. Post-Dispatch Audit Procedure

After execution, inspect:

```text
{execution_replay_dir}/004_first_live_provider_post_dispatch_audit_packet.json
{execution_replay_dir}/007_first_live_provider_dispatch_execution_packet.json
{execution_replay_dir}/live_provider_boundary/004_live_provider_runtime_boundary_audit.json
```

Audit checks:

```text
final status is completed or failed closed
dispatch attempt number is 1
dispatch attempt limit is 1
provider is openai
provider resource type is COGNITION_PROVIDER
credential_secret_replayed is false
authorization_header_replayed is false
worker_invoked is false
fallback_performed is false
automatic_retry_performed is false
governance_modified is false
replay_modified is false
ERR evidence selected openai
LLM_COGNITION_ARTIFACT_V1 is present on success
error envelope is present on fail-closed provider boundary failure
```

Any failed audit check requires rollback review and no second dispatch without a new authorization chain.

## 10. Post-Dispatch Recertification Procedure

After audit, inspect:

```text
{execution_replay_dir}/005_first_live_provider_post_dispatch_recertification_packet.json
{execution_replay_dir}/006_first_live_provider_rollback_execution.json
```

Recertification checks:

```text
post-dispatch audit packet hash is referenced
recertification final status matches execution outcome
rollback is ROLLBACK_NOT_REQUIRED on success
rollback is ROLLBACK_EXECUTED on failure
dispatch authorization is not reused
any later live attempt requires a new activation and dispatch authorization package
```

## Operator Checklist

Before execution:

```text
[ ] Confirm activation package replay directory exists.
[ ] Confirm dispatch authorization replay directory exists.
[ ] Confirm 003_first_live_provider_dispatch_authorization.json exists.
[ ] Confirm authorization is fresh and one-attempt only.
[ ] Confirm AIGOL_OPENAI_API_KEY is present in the governed process environment.
[ ] Confirm the credential value is not printed or recorded.
[ ] Confirm operator_replay_dir does not already contain replay artifacts.
[ ] Confirm execution_replay_dir does not already contain replay artifacts.
[ ] Confirm live_transport_enabled will be true.
[ ] Confirm transport is create_governed_live_openai_executor().
[ ] Confirm confirm_dispatch will be true.
```

After execution:

```text
[ ] Record final_status.
[ ] Record execution_replay_reference.
[ ] Record operator_replay_reference.
[ ] Inspect post-dispatch audit packet.
[ ] Inspect recertification packet.
[ ] Inspect rollback artifact.
[ ] Verify no secret or Authorization header appears in replay.
[ ] Do not perform a second dispatch without a new authorization chain.
```

## Rollback Checklist

If final status is fail-closed:

```text
[ ] Stop immediately.
[ ] Do not retry.
[ ] Do not fallback.
[ ] Do not route to another provider.
[ ] Do not invoke workers.
[ ] Inspect 006_first_live_provider_rollback_execution.json.
[ ] Inspect live provider boundary error envelope if present.
[ ] Record failure reason from operator dispatch result.
[ ] Preserve replay evidence immutably.
[ ] Revoke, rotate, or remove credential according to operator policy if exposure is suspected.
[ ] Require a new activation and dispatch authorization package before any later attempt.
```

## Expected Evidence Inventory

Required evidence on any completed operator run:

```text
operator dispatch request artifact
operator dispatch result artifact
execution approval revalidation artifact
execution credential revalidation artifact
live transport execution evidence artifact
LLM_COGNITION_ARTIFACT_V1 or failed cognition artifact
post-dispatch audit packet
post-dispatch recertification packet
rollback execution artifact
dispatch execution packet
ERR resource selection evidence
live provider boundary audit
live response envelope or live error envelope
```

Forbidden evidence:

```text
OpenAI API key value
Authorization header
credential hash
second dispatch attempt
retry evidence
fallback evidence
worker invocation evidence
provider routing evidence
governance mutation evidence
replay mutation evidence
```

## Final Recommendation

Proceed with the first real governed OpenAI dispatch only if every pre-execution checklist item is satisfied.

Use exactly:

```text
AIGOL_FIRST_LIVE_PROVIDER_OPERATOR_ENTRYPOINT_V1
```

with:

```text
create_governed_live_openai_executor()
confirm_dispatch = true
live_transport_enabled = true
```

Treat any failure as final for that authorization chain. No retry, fallback, second attempt, worker invocation, or provider rerouting is permitted.
