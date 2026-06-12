# AIGOL_ACLI_REQUESTED_DOMAIN_FAIL_CLOSED_ROOT_CAUSE_CERTIFICATION_V1

Status: investigation-only certification evidence.

Scope: ACLI fail-closed behavior for development-oriented prompts that route to
`NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` and fail inside
`NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY` before proposal generation.

No runtime behavior was modified by this investigation.

## Root Cause

`requested_domain` is populated only by
`aigol/runtime/native_development_task_intake_runtime.py::_detect_domain`.

That detector scans the prompt and milestone id for the hard-coded
`SUPPORTED_DOMAINS` tuple:

- `TRADING`
- `MARKETING`
- `GOVERNANCE`
- `COGNITION`
- `AIGOL`

If none of those literal tokens appears, intake still accepts the native
development task and records `requested_domain = null`.

`aigol/runtime/development_context_assembly_runtime.py::_validate_intake`
then requires `requested_domain` to be a non-empty string and fail-closes with:

`requested_domain is required`

This occurs before context artifact resolution, provider proposal generation,
worker invocation, or execution.

## Lifecycle Trace

1. `aigol/cli/aigol_cli.py::run_interactive_conversation`
   reads the operator prompt.

2. Conversational routing selects
   `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` when the prompt has a milestone-like
   token (`aigol_` or `v1`) and a development marker such as `implement`,
   `create`, `foundation`, `runtime`, `worker`, or `domain`.

3. `run_interactive_conversation` dispatches that workflow to
   `run_conversation_native_development_context_integration`.

4. `run_conversation_native_development_context_integration` calls
   `run_native_development_task_intake`.

5. `run_native_development_task_intake` calls `_analyze_prompt`, extracts a
   single milestone id, determines task kind, and sets:

   `requested_domain = _detect_domain(prompt, milestone_id)`

6. `_detect_domain` returns `None` when the prompt and milestone id do not
   contain one of the hard-coded supported domain tokens.

7. `run_conversation_native_development_context_integration` passes the accepted
   intake artifact into `assemble_development_context`.

8. `assemble_development_context` calls `_validate_intake`.

9. `_validate_intake` calls `_require_string(intake.get("requested_domain"),
   "requested_domain")`.

10. `_require_string` raises `FailClosedRuntimeError("requested_domain is
    required")`.

11. The integration returns `FAILED_CLOSED`, with provider, worker, dispatch,
    invocation, proposal, and execution flags all false.

## Domain Registry Finding

A domain and worker resolution registry exists in:

`aigol/runtime/domain_and_worker_resolution_registry.py`

The default registry includes:

- `TRADING`
- `MARKETING`
- `HEALTHCARE`
- `PUBLIC_SERVICES`
- `SERVER_MANAGEMENT`

That registry is not called by the native development context integration path.

The development context assembly runtime instead uses a local
`DOMAIN_CONTEXT_FILES` map containing only:

- `TRADING`

Therefore there are two related fail-closed modes:

1. No supported token detected by intake:
   `requested_domain = null` and context assembly fails with
   `requested_domain is required`.

2. A supported intake token is detected but no context bundle exists in
   `DOMAIN_CONTEXT_FILES`, for example `AIGOL`:
   context assembly fails with
   `development context assembly failed closed: unsupported domain context`.

## Minimal Reproduction

Prompt:

```text
Implement PROVIDER_CAPABILITY_CATALOG_V1. Create runtime foundation only. No dispatch. No execution.
```

Observed replay-safe direct harness result:

```json
{
  "intake_status": "NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED",
  "requested_milestone_id": "PROVIDER_CAPABILITY_CATALOG_V1",
  "requested_domain": null,
  "integration_status": "FAILED_CLOSED",
  "context_status": "FAILED_CLOSED_INVALID_INTAKE",
  "failure_reason": "requested_domain is required",
  "proposal_generated": false,
  "provider_invoked": false,
  "worker_invoked": false
}
```

Control prompt:

```text
Implement TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1. Foundation only. No broker integration. No exchange integration. No order placement. No live trading. No dispatch. No execution.
```

Observed replay-safe direct harness result:

```json
{
  "intake_status": "NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED",
  "requested_milestone_id": "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1",
  "requested_domain": "TRADING",
  "integration_status": "CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED",
  "context_status": "CONTEXT_ASSEMBLED",
  "failure_reason": null
}
```

Neighboring fail-closed mode:

```json
{
  "requested_milestone_id": "AIGOL_ACLI_PRODUCTION_PILOT_V1",
  "requested_domain": "AIGOL",
  "integration_status": "FAILED_CLOSED",
  "context_status": "FAILED_CLOSED_INVALID_INTAKE",
  "failure_reason": "development context assembly failed closed: unsupported domain context"
}
```

## Expected Prompt Format

The currently successful format is domain-prefixed and worker/foundation shaped:

```text
Implement TRADING_<WORKER_FAMILY>_WORKER_FOUNDATION_V1. Foundation only. No dispatch. No execution.
```

The practical domain must currently be `TRADING` for context assembly to
succeed, because only `TRADING` has a registered `DOMAIN_CONTEXT_FILES` context
bundle in the development context assembly runtime.

## Failing Component

Primary failing component:

`aigol/runtime/development_context_assembly_runtime.py::_validate_intake`

Immediate failing condition:

`requested_domain` is `None` on the accepted intake artifact.

Upstream source of the missing value:

`aigol/runtime/native_development_task_intake_runtime.py::_detect_domain`

Systemic gap:

Native development context assembly requires a domain context, but the
conversation/intake path does not have a canonical way to populate
`requested_domain` for repository-development or ACLI milestones that are not
domain-prefixed.

## Recommended Fix

Do not weaken fail-closed behavior.

Recommended shortest governed fix:

1. Define an explicit domain resolution contract for native repository
   development prompts before context assembly.

2. Either:
   - require an explicit operator field such as `requested_domain = TRADING` or
     `requested_domain = REPOSITORY_DEVELOPMENT`, or
   - add a certified repository-development domain such as
     `REPOSITORY_DEVELOPMENT`/`AIGOL` with corresponding context files.

3. Route intake through the existing domain and worker resolution registry or
   align the intake domain detector with that registry.

4. Extend `development_context_assembly_runtime.DOMAIN_CONTEXT_FILES` only after
   the target domain has certified context artifacts.

5. Add regression tests for:
   - missing domain fails closed with clear remediation guidance;
   - explicit supported domain succeeds;
   - registered but unsupported context domain fails closed with
     `unsupported domain context`;
   - ACLI/repository-development prompt can assemble context once a certified
     repository-development context bundle exists.

## Certification Outputs

ROOT_CAUSE_CONFIRMED = YES

REQUESTED_DOMAIN_SOURCE_IDENTIFIED = YES

DOMAIN_REGISTRY_IDENTIFIED = YES

MINIMAL_REPRODUCTION_CONFIRMED = YES

FIX_RECOMMENDATION_AVAILABLE = YES
