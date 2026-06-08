# AIGOL_CLARIFICATION_LIFECYCLE_RESOLUTION_RUNTIME_V1

## Status

Clarification lifecycle resolution runtime implemented and regression-tested.

No provider was invoked. No worker was invoked. No authorization was created. No execution was started. No domain was created. No repair or retry behavior was implemented.

## Purpose

Investigate and fix the clarification continuity failure:

```text
FAILED_CLOSED: multiple active clarifications
```

The observed operator flow was:

```text
Create a new governed domain called PilotDomain.
-> clarification requested
-> operator answered
-> FAILED_CLOSED: multiple active clarifications
```

## Lifecycle Audit

Clarification creation:

```text
unknown_domain_clarification_runtime
```

creates:

- `UNKNOWN_DOMAIN_ARTIFACT_V1`
- `CLARIFICATION_REQUEST_ARTIFACT_V1`

Clarification storage:

```text
TURN-*/unknown_domain_clarification/
```

Clarification identifiers:

- `clarification_request_artifact.clarification_id`
- `clarification_request_artifact.artifact_hash`
- `unknown_domain_artifact.unknown_domain_id`
- `unknown_domain_artifact.artifact_hash`

Continuity response handling:

```text
clarification_continuity_runtime
```

creates:

- `CLARIFICATION_REPLY_BINDING_ARTIFACT_V1`
- `CLARIFICATION_RESPONSE_ARTIFACT_V1`
- `CLARIFICATION_RESOLUTION_ARTIFACT_V1`
- `CLARIFICATION_WORKFLOW_RESUME_ARTIFACT_V1`

## Root Cause

Active clarification discovery previously classified every unresolved clarification request as active.

If a session contained more than one open clarification replay record, active discovery produced multiple active candidates and failed closed. Older clarification requests were only excluded after a resolution artifact existed. They were not lifecycle-classified as superseded when a newer open clarification existed.

## Implemented Runtime

Added:

```text
aigol/runtime/clarification_lifecycle_resolution_runtime.py
```

The runtime reconstructs clarification lifecycle state from session replay and classifies clarification requests as:

- `ACTIVE`
- `OPEN`
- `RESPONDED`
- `RESOLVED`
- `SUPERSEDED`

Only the latest unresolved clarification may be `ACTIVE`. Older unresolved clarifications are lifecycle-classified as `SUPERSEDED` and are not considered active.

## Continuity Integration

Updated:

```text
aigol/runtime/clarification_continuity_runtime.py
```

Continuity now uses the lifecycle resolver to discover the single active clarification. Resolved clarifications are excluded from active discovery. Superseded clarifications are excluded from active discovery.

## State Transition

The supported operator reply transition is:

```text
OPEN
-> RESPONDED
-> RESOLVED
-> WORKFLOW_RESUME_READY
```

For `PilotDomain`, the successful state is:

```text
clarification requested
operator reply bound
clarification response recorded
clarification resolution recorded
workflow continuation ready
```

## Guarantees

This milestone guarantees:

- at most one `ACTIVE` clarification per session;
- resolved clarifications are not considered active;
- superseded clarifications are not considered active;
- clarification response transitions through reply binding, response, resolution, and resume-ready artifacts;
- fail-closed behavior remains preserved for missing state, chain mismatch, replay mismatch, and workflow mismatch;
- provider invocation remains false;
- worker invocation remains false;
- execution remains false;
- domain creation remains false.

## Regression Coverage

Updated:

```text
tests/test_clarification_continuity_runtime_v1.py
```

Verified:

- interactive clarification reply resolves and resumes without provider fallback;
- lifecycle resolution allows only the latest open clarification to be active;
- older unresolved clarifications become `SUPERSEDED`;
- resolved clarifications are not active;
- missing clarification state fails closed;
- chain mismatch fails closed;
- replay mismatch fails closed;
- workflow mismatch fails closed.

## Validation

Executed:

```text
python -m pytest tests/test_clarification_continuity_runtime_v1.py tests/test_conversational_cli_runtime_v1.py tests/test_unknown_domain_and_clarification_ux_v1.py
```

Result:

```text
40 passed
```

## Final Outputs

```text
MULTIPLE_ACTIVE_CLARIFICATIONS_FIXED = TRUE
AT_MOST_ONE_ACTIVE_CLARIFICATION_PER_SESSION = TRUE
OPEN_TO_RESPONDED_TO_RESOLVED = TRUE
RESOLVED_CLARIFICATIONS_EXCLUDED_FROM_ACTIVE = TRUE
FAIL_CLOSED_PRESERVED = TRUE
PROVIDER_INVOCATION_PREVENTED = TRUE
WORKER_INVOCATION_PREVENTED = TRUE
DOMAIN_CREATION_PREVENTED = TRUE
READY_FOR_HUMAN_CLARIFICATION_ACCEPTANCE = TRUE
```
