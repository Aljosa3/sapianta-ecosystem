# AIGOL First Live Provider Activation Package Instantiation V1

Status: implemented pre-dispatch activation package instantiation.

Purpose: create the first concrete activation package instance for a single governed OpenAI invocation attempt.

This milestone creates replay-visible package artifacts.

It does not invoke OpenAI.

It does not disclose credentials.

It does not perform live dispatch.

It does not modify ERR or OCS.

## Context

Inputs:

```text
HIRR_CERTIFIED = YES
ERR_ROLE = UNIVERSAL_RESOURCE_REGISTRY
PROVIDER_ARCHITECTURE_COMPLETE = YES
PROVIDER_GOVERNANCE_COMPLETE = YES
PROVIDER_RUNTIME_COMPLETE = YES
AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_PACKAGE_V1 = COMPLETE
AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_GAP_AUDIT_V1
```

Gap audit verdict:

```text
ACTIVATION_PACKAGE_SPECIFICATION_COMPLETE = YES
ACTIVATION_PACKAGE_INSTANTIATED = NO
```

## Architecture Summary

Implemented path:

```text
activation package request
-> approval artifact instance
-> activation authorization artifact instance
-> credential policy artifact
-> credential availability evidence
-> ERR openai metadata selection
-> canonical provider contract view
-> dispatch attempt prepared artifact
-> post-dispatch audit template
-> post-dispatch recertification template
-> rollback evidence
-> replay reconstruction
```

The dispatch attempt is armed but not executed:

```text
dispatch_status = ARMED_NOT_DISPATCHED
live_dispatch_attempted = false
live_dispatch_performed = false
```

## Runtime Changes

Added:

- `aigol/runtime/first_live_provider_activation_package_instantiation.py`

The runtime provides:

- `instantiate_first_live_provider_activation_package`;
- `create_first_live_provider_approval`;
- `create_first_live_provider_activation_authorization`;
- `create_first_live_provider_credential_availability`;
- `create_first_live_provider_dispatch_attempt`;
- `create_first_live_provider_post_dispatch_audit_template`;
- `create_first_live_provider_post_dispatch_recertification_template`;
- `create_first_live_provider_rollback_evidence`;
- `reconstruct_first_live_provider_activation_package`.

## Replay Evidence

Successful package instantiation writes:

```text
000_first_live_provider_approval.json
001_first_live_provider_activation_authorization.json
002_first_live_provider_credential_policy.json
003_first_live_provider_credential_availability.json
004_first_live_provider_dispatch_attempt_prepared.json
005_first_live_provider_post_dispatch_audit_template.json
006_first_live_provider_post_dispatch_recertification_template.json
007_first_live_provider_rollback_evidence.json
```

Nested ERR selection evidence remains in:

```text
err_openai_selection/
```

Fail-closed package instantiation writes:

```text
000_first_live_provider_activation_package_failed_closed.json
```

Replay reconstruction verifies:

- replay ordering;
- wrapper hashes;
- artifact hashes;
- approval-to-authorization lineage;
- authorization-to-credential lineage;
- credential-to-dispatch lineage;
- dispatch-to-audit lineage;
- audit-to-recertification lineage;
- recertification-to-rollback lineage;
- no live dispatch;
- no credential secret replay;
- no provider invocation;
- no worker invocation;
- no governance mutation;
- no replay mutation.

## Artifact Instances

Implemented artifact types:

| Artifact | Purpose |
| --- | --- |
| `FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1` | One-time human approval instance for the first live OpenAI activation package. |
| `FIRST_LIVE_PROVIDER_ACTIVATION_AUTHORIZATION_ARTIFACT_V1` | One-attempt activation authorization linked to approval. |
| `LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1` | Existing secret-free credential policy artifact. |
| `FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1` | Secret-free credential availability evidence. |
| `FIRST_LIVE_PROVIDER_DISPATCH_ATTEMPT_ARTIFACT_V1` | Pre-dispatch attempt evidence, armed but not dispatched. |
| `FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1` | Post-dispatch audit packet template. |
| `FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1` | Post-dispatch recertification packet template. |
| `FIRST_LIVE_PROVIDER_ROLLBACK_EVIDENCE_ARTIFACT_V1` | Rollback evidence predeclaration. |

## Boundary Preservation

Preserved:

- no OpenAI invocation;
- no live dispatch;
- no credential disclosure;
- no credential secret replay;
- no authorization header replay;
- ERR remains passive;
- OCS architecture is unchanged;
- no provider routing;
- no provider ranking;
- no provider fallback;
- no worker invocation;
- no governance mutation;
- no replay mutation.

Runtime invariant:

```text
activation_package_instantiated = true
live_dispatch_attempted = false
live_dispatch_performed = false
credential_secret_replayed = false
provider_invoked = false
worker_invoked = false
governance_modified = false
replay_modified = false
```

## Tests Added

Added:

- `tests/test_first_live_provider_activation_package_instantiation_v1.py`

Coverage:

- complete package instantiation without live dispatch;
- ordered replay evidence;
- secret-free replay artifacts;
- replay lineage reconstruction;
- credential unavailable fail-closed;
- malformed package id fail-closed;
- replay tampering detection;
- static check that the module has no network or secret dispatch implementation.

## Validation Results

Focused validation:

```text
python -m pytest tests/test_first_live_provider_activation_package_instantiation_v1.py
8 passed
```

Broader regression validation:

```text
python -m pytest tests/test_first_live_provider_activation_package_instantiation_v1.py tests/test_live_provider_http_transport_v1.py tests/test_live_provider_runtime_boundary_v1.py tests/test_live_provider_invocation_prerequisites_v1.py tests/test_first_real_provider_runtime_v1.py tests/test_real_provider_registration_v1.py tests/test_external_resource_registry_runtime_v0.py tests/test_llm_cognition_provider_runtime_v1.py tests/test_cognition_artifact_runtime_v1.py
93 passed
```

## Remaining Gaps

Remaining activation gaps:

- no live OpenAI dispatch has occurred;
- post-dispatch audit remains a template until dispatch occurs;
- post-dispatch recertification remains a template until dispatch occurs;
- rollback evidence is predeclared and not yet executed after a live attempt;
- a separate explicit live-dispatch milestone is still required.

## Final Recommendation

The activation package is now instantiated as replay-visible pre-dispatch evidence.

Proceed only to a separately approved one-attempt live dispatch milestone.

Final position:

```text
ACTIVATION_PACKAGE_INSTANTIATED = YES
LIVE_OPENAI_INVOCATION_PERFORMED = NO
CREDENTIAL_DISCLOSED = NO
LIVE_DISPATCH_ALLOWED_NOW = NO
NEXT_STEP = FIRST_LIVE_OPENAI_ONE_ATTEMPT_DISPATCH
```
