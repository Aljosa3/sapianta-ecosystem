# G15-AICLI-04 Runtime Routing Verification

## Status

Audit completed. No implementation change required.

## Knowledge Reuse Audit

Inspected and reused existing certified evidence and implementation surfaces:

- `aigol/cli/aicli.py`
  - `/approve` in interactive mode delegates to `run_human_interface_runtime_entry`.
  - submit mode approval from G15-AICLI-03 delegates through the same canonical entry.
- `aigol/runtime/human_interface_runtime_entry_service.py`
  - owns the shared Human Interface runtime entry boundary.
  - prepares Platform Core project context.
  - injects admissible runtime prompts into `run_interactive_conversation`.
  - computes `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND` only when the latest governed conversation turn reaches worker invocation and replay certification.
- `aigol/cli/aigol_cli.py`
  - owns `run_interactive_conversation`.
  - performs conversational routing, native development context integration, post-entry continuation, provider continuation, worker lifecycle continuation, turn completion, and status rendering.
- `aigol/runtime/conversational_cli_runtime.py`
  - owns `conversational_cli_routing` replay artifacts and workflow selection.
- `docs/governance/G14_35_DETERMINISTIC_ROUTING_PRECEDENCE_RESTORATION_V1.md`
  - certifies generic implementation prompts as `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`.
  - records `REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND` with provider unavailable as known real-interface evidence.
- Existing regression tests:
  - `tests/test_g14_35_deterministic_routing_precedence_restoration_v1.py`
  - `tests/test_conversational_cli_runtime_v1.py`
  - `tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py`

No duplicate runtime router, approval router, provider router, or governance logic was added.

## Runtime Routing Analysis

Verified submit approval flow:

```text
./aicli submit
-> stdin request capture
-> Platform Core project context
-> Platform Core approval summary
-> /approve
-> run_human_interface_runtime_entry
-> run_interactive_conversation(auto_continue=True)
-> conversational_cli_routing
-> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> post_entry_continuation_gate
-> context_assembled_to_ppp_routing_continuation
-> provider availability fail-closed
-> canonical runtime entry partial binding
-> Reference UHI partial binding
```

Observed local trace:

```text
session_id: G15-AICLI-04-TRACE
runtime_status: REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND
canonical_runtime_entry_status: CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND
runtime_command: aigol conversation
runtime_turn_count: 1
runtime_failed_turns: 1
runtime_exit_reason: EXIT_COMMAND
governance_authorization_reached: False
provider_invocation_reached: False
worker_execution_reached: False
replay_certification_reached: False
failure_reason: OpenAI provider unavailable
```

Replay evidence showed:

```text
conversational_cli_routing/002_conversational_routing_returned.json
workflow_id: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
routing_status: WORKFLOW_SELECTED
provider_invoked: false
worker_invoked: false
```

Post-entry continuation evidence showed:

```text
post_entry_continuation_gate_status: CONTINUATION_ALLOWED
continuation_runtime: context_assembled_to_ppp_routing_continuation
authorization_required: true
human_confirmation_required: true
```

Post-context continuation evidence showed:

```text
continuation_status: FAILED_CLOSED
ppp_route_status: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
operational_failure_classification: PROVIDER_AVAILABILITY
provider_resilience_status: PROVIDER_UNAVAILABLE_FAIL_CLOSED
retry_performed: false
provider_invoked: false
worker_invoked: false
```

## Architectural Verification

AiCLI correctly delegates after approval.

Evidence:

- AiCLI calls `run_human_interface_runtime_entry`.
- Runtime entry sets `human_interface_runtime_entry_orchestrates: False`.
- Runtime entry sets `platform_core_runtime_delegated: True`.
- Runtime entry invokes `run_interactive_conversation` with `auto_continue=True`.
- Runtime status is computed from the latest governed conversation turn, not from AiCLI.

The component responsible for selecting the next runtime stage is the certified conversational runtime path:

```text
run_interactive_conversation
-> route_conversational_cli_intent
-> authoritative_workflow_id
-> selected workflow branch
```

AiCLI does not select:

- workflow;
- provider;
- governance stage;
- worker stage;
- replay certification path.

## Root Cause Analysis

The observed partial runtime state is not caused by AiCLI.

The runtime did not merely stop at `conversational_cli_routing` in the verified trace. It selected the native development workflow, entered native context integration, allowed post-entry continuation, and then failed closed in provider-dependent continuation because the OpenAI provider was unavailable.

The routing decision itself is consistent with certified current behavior for generic implementation prompts. G14.35 explicitly certifies:

```text
Implement governance validation utility.
-> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
```

The current executable tests also preserve a distinction:

- natural development prompts such as `Add replay validation` route to `GOVERNED_DEVELOPMENT_WORKFLOW`;
- generic implementation prompts such as `Implement governance validation utility.` route to `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`.

The routing replay did record a non-authoritative semantic comparison divergence where CSA indicated `GOVERNED_DEVELOPMENT_WORKFLOW` while the certified compatibility route selected `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`. The current certified routing source remains the compatibility fallback for this class of generic implementation prompt. That is visible evidence for a possible future routing migration milestone, but it is not a proven AiCLI defect and should not be corrected inside the Human Interface.

## Implementation Summary

No implementation change was made for G15-AICLI-04.

Reason:

- AiCLI delegated correctly.
- Canonical runtime entry delegated correctly.
- Runtime entered `aigol conversation`.
- Certified routing selected an expected current workflow for the prompt class.
- The first terminal failure was provider availability inside post-context continuation.
- Moving routing into AiCLI would violate Generation 14 ownership boundaries.

## Validation Summary

Real submit-equivalent validation was run through `run_reference_uhi_submit_session` using:

```text
initial request: Implement deterministic governance report exporter.
approval input: /approve
runtime runner: default run_interactive_conversation
runtime root: /tmp/g15-aicli-04-trace
```

Validation commands:

```bash
python -m py_compile aigol/cli/aicli.py
python -m pytest -q
git diff --check
```

The trace produced deterministic evidence for:

- Platform Core project context;
- runtime entry delegation;
- conversational routing;
- native development context integration;
- post-entry continuation gate;
- provider availability fail-closed;
- partial binding status mapping.

## Files Modified

- `docs/governance/G15_AICLI_04_RUNTIME_ROUTING_VERIFICATION.md`

No production code was modified.

## Boundary Confirmation

Platform Core and certified runtime components remain responsible for:

- conversation semantics;
- clarification;
- approval semantics;
- runtime selection;
- governance;
- provider continuation;
- worker continuation;
- replay.

AiCLI remains responsible only for:

- stdin capture;
- stdout rendering;
- session lifecycle;
- forwarding human replies;
- forwarding approval into the canonical runtime entry.

## Verdict

Current behavior is architecturally explained and does not prove an AiCLI routing defect.

`REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND` is the expected reported status when the canonical runtime entry enters the governed conversation runtime but the latest turn does not reach worker invocation and replay certification.

For the verified prompt class, the first failing component is provider availability inside post-context continuation:

```text
context_assembled_to_ppp_routing_continuation
-> PROVIDER_UNAVAILABLE_FAIL_CLOSED
```

Smallest correction required now:

```text
None.
```

Future work, if desired, should be a Platform Core runtime-routing migration milestone that certifies whether CSA-primary `GOVERNED_DEVELOPMENT_WORKFLOW` should replace compatibility fallback routing for generic implementation prompts. That work must not be implemented in AiCLI.

