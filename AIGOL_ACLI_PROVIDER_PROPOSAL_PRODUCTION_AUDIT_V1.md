# AIGOL_ACLI_PROVIDER_PROPOSAL_PRODUCTION_AUDIT_V1

## Objective

Determine why ACLI reaches repaired clarification continuity and post-entry continuation, but fails closed before execution summary with:

```text
OpenAI provider request prompt is required
```

This is an audit artifact only. No ACLI, governance, PPP, execution summary, authorization, or worker lifecycle runtime behavior was changed.

## Evidence Source

Real ACLI dogfood replay:

```text
/tmp/aigol_acli_execution_summary_dogfood/ACLI-EXECUTION-SUMMARY-DOGFOOD-2
```

Canonical chain:

```text
CHAIN-E28AD94F43AA5DF6
```

Observed CLI path:

```text
Human Prompt
-> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> POST_ENTRY_CONTINUATION_GATE / CLARIFICATION_REQUIRED
-> WAITING_FOR_OPERATOR
-> continue ppp
-> POST_ENTRY_CONTINUATION_GATE / CONTINUATION_ALLOWED
-> POST_CONTEXT_CONTINUATION
-> conversation PPP routing
-> provider proposal production
-> FAILED_CLOSED: OpenAI provider request prompt is required
```

## Post-Entry Continuation Gate

Turn 1:

```text
artifact_type: POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1
gate_status: CLARIFICATION_REQUIRED
continuation_allowed: false
execution_capable: true
continuation_runtime: context_assembled_to_ppp_routing_continuation
```

Turn 2:

```text
artifact_type: POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1
gate_status: CONTINUATION_ALLOWED
continuation_allowed: true
execution_summary_required: true
human_confirmation_required: true
authorization_required: true
explicit_ppp_continuation_requested: true
lifecycle_replay_reference: /tmp/aigol_acli_execution_summary_dogfood/ACLI-EXECUTION-SUMMARY-DOGFOOD-2/TURN-000001/native_development_context_integration
```

Conclusion:

```text
Post-entry gate behavior is not the blocker.
```

## PPP Invocation Path

`continue_context_assembled_to_ppp_routing(...)` calls:

```text
run_conversation_ppp_routing_integration(...)
```

The PPP path reaches:

```text
conversation native development context integration
domain worker resolution
provider necessity classification
seed proposal contract validation
provider request handoff
provider proposal production
```

Source boundary:

```text
aigol/runtime/conversation_ppp_routing_integration.py:142
```

At that point PPP calls:

```text
produce_provider_development_proposal(...)
```

## Provider Proposal Production Path

`produce_provider_development_proposal(...)` performs:

```text
validate handoff
validate context
validate domain/worker resolution
validate provider policy
validate cross references
build PROVIDER_REQUEST_PACKET_V1
persist provider_request_packet_prepared
call run_provider_attachment(...)
```

Source boundary:

```text
aigol/runtime/provider_proposal_production_runtime.py:105
aigol/runtime/provider_proposal_production_runtime.py:116
```

The provider request packet was successfully created and persisted:

```text
TURN-000002/post_context_continuation/conversation_ppp_routing/provider_proposal_production/000_provider_request_packet_prepared.json
```

Recorded fields include:

```text
artifact_type: PROVIDER_REQUEST_PACKET_V1
provider_id: openai
canonical_chain_id: CHAIN-E28AD94F43AA5DF6
domain_reference: AIGOL
worker_reference: CLAUDE_EXTERNAL
milestone_reference: WORKER_FOUNDATION
output_targets:
- AIGOL_GENERIC_DEVELOPMENT_TASK_V1
- WORKER_FOUNDATION
request_instructions:
- Return one DEVELOPMENT_PROPOSAL_ARTIFACT_V1-compatible proposal payload.
- Proposal must remain proposal-only.
- Do not authorize, dispatch, execute, mutate governance, mutate replay, create workers, or create domains.
```

The packet does not include:

```text
prompt
human_prompt
request
```

## Provider Request Prompt Requirement

The runtime that expects a provider request prompt is the real OpenAI provider adapter:

```text
aigol/provider/providers/openai_provider.py:70
```

It calls:

```text
prompt = _extract_prompt(request)
```

`_extract_prompt(...)` accepts only:

```text
request as a string
request["prompt"]
request["human_prompt"]
request["request"]
```

If none are present, it raises:

```text
OpenAI provider request prompt is required
```

Source boundary:

```text
aigol/provider/providers/openai_provider.py:72
aigol/provider/providers/openai_provider.py:184
```

## Exact Missing Runtime Dependency

The missing runtime dependency is:

```text
a deterministic, replay-visible provider request prompt projection for PROVIDER_REQUEST_PACKET_V1 before dispatch to the OpenAIProviderAdapter
```

Current producer:

```text
aigol/runtime/provider_proposal_production_runtime.py:_provider_request_packet(...)
```

creates a governance packet, not an adapter-ready prompt-bearing request.

Current consumer:

```text
aigol/provider/providers/openai_provider.py:OpenAIProviderAdapter.generate_proposal(...)
```

requires either a string request or a dict containing `prompt`, `human_prompt`, or `request`.

Therefore the failure is a request-shape mismatch:

```text
PROVIDER_REQUEST_PACKET_V1 != OpenAIProviderAdapter prompt contract
```

## Context Availability

Context exists to generate a bounded provider prompt.

Available upstream evidence includes:

```text
native_development_task_intake:
- human_prompt_hash
- human_prompt_reference
- requested_domain
- requested_worker_family
- requested_milestone_id
- requested_output_scope
- explicit_constraints

development_context_assembly:
- context_hash
- requested_domain
- requested_worker_family
- requested_output_scope
- known_assumptions
- known_constraints
- known_gaps
- artifact_references

provider_request_packet:
- output_targets
- request_instructions
- assumptions
- known_gaps
- handoff/context/resolution/policy hashes
```

The original human prompt is not embedded in `PROVIDER_REQUEST_PACKET_V1`; it is represented by hash and replay lineage. A repair can still build a deterministic prompt from replay-visible structured fields, or explicitly add a hash-bound prompt projection artifact derived from upstream replay.

## Should ACLI Generate It Automatically?

Yes, but only inside the existing provider proposal production boundary, not as a conversational shortcut and not as a governance redesign.

The prompt should be:

- deterministic;
- replay-visible;
- hash-bound to `PROVIDER_REQUEST_PACKET_V1`;
- proposal-only;
- non-authoritative;
- constrained by existing request instructions;
- provider-adapter compatible;
- explicit that provider output cannot authorize, dispatch, execute, mutate governance, mutate replay, create workers, or create domains.

The repair should not make ACLI select providers, bypass approval, bypass execution summary, or create worker lifecycle artifacts.

## Replay Lineage

Replay lineage remains intact.

Evidence:

```text
Turn 1 native context replay exists.
Turn 1 post-entry gate references native context replay.
Turn 2 post-entry gate references Turn 1 native context replay.
Turn 2 post-context continuation preserves canonical_chain_id: CHAIN-E28AD94F43AA5DF6.
Provider proposal production persisted a failed request packet and failed provider attachment replay.
```

Chain inspection:

```text
conversation: True
execution_lifecycle_artifacts: 0
worker_evidence_artifacts: 0
replay_evidence_artifacts: 15
execution_requests_created: False
workers_dispatched: False
workers_invoked: False
```

## Test Coverage Gap

The provider proposal production unit tests use a fake provider adapter that accepts any request object.

That means the tests validate governance packet production and proposal validation, but do not catch the real OpenAI adapter request-shape requirement.

The failing dogfood path is therefore an integration gap between:

```text
PROVIDER_REQUEST_PACKET_V1 producer
and
OpenAIProviderAdapter prompt extractor
```

## Minimal Repair

Smallest governance-preserving repair:

```text
Add a deterministic provider prompt projection step inside provider proposal production, before run_provider_attachment(...), producing an adapter-ready request that includes a prompt or request string while preserving the original PROVIDER_REQUEST_PACKET_V1 as source lineage.
```

The projected request should include:

```text
prompt: <deterministic proposal-only prompt derived from provider request packet and context>
original_provider_request_packet: <the existing PROVIDER_REQUEST_PACKET_V1 or reference/hash>
provider_request_packet_hash: <artifact_hash>
proposal_only: true
provider_authority: false
execution_requested: false
dispatch_requested: false
worker_created: false
domain_created: false
governance_modified: false
replay_modified: false
```

Recommended tests:

```text
1. Provider proposal production with OpenAIProviderAdapter-compatible fake client succeeds when prompt projection exists.
2. Prompt projection is replay-visible and hash-bound to PROVIDER_REQUEST_PACKET_V1.
3. Prompt projection preserves all no-authority flags.
4. Existing fake-provider proposal production tests continue to pass.
```

## Final Fields

```text
PPP_REACHED = YES
PROVIDER_PROPOSAL_PRODUCTION_REACHED = YES
PROVIDER_REQUEST_PROMPT_REQUIRED = YES
PROVIDER_REQUEST_PROMPT_AVAILABLE = NO
FIRST_FAIL_CLOSED_STAGE = OPENAI_PROVIDER_ADAPTER_PROMPT_EXTRACTION
ROOT_CAUSE = Provider proposal production creates PROVIDER_REQUEST_PACKET_V1 and passes it directly to OpenAIProviderAdapter, but the packet lacks the prompt/human_prompt/request string required by the OpenAI adapter.
MINIMAL_REPAIR = Add deterministic replay-visible provider prompt projection from PROVIDER_REQUEST_PACKET_V1 before run_provider_attachment, preserving the packet as lineage and keeping proposal-only/no-authority semantics.
EXECUTION_SUMMARY_PATH_BLOCKER_IDENTIFIED = YES
```
