# PROVIDER_ATTACHMENT_CONTINUATION_AUDIT_V1

Status: COMPLETE

Target verdict:

```text
PROVIDER_ATTACHMENT_CONTINUATION_AUDIT_COMPLETE
```

## 1. Audit Purpose

This audit reviews the provider pipeline reached after successful replay-restored lifecycle continuation and PPP continuation handoff.

The audit is implementation-only. It does not redesign Platform Core architecture, governance, replay, approval, translation, lifecycle, PPP, routing, provider authority, or workflow semantics.

Observed hardening state:

```text
Human Prompt
-> Human Intent Resolution
-> Native Development Context Assembly
-> Replay Recording
-> Replay Restoration
-> Lifecycle Continuation
-> PPP Handoff
-> Provider Proposal Production
-> FAILED_CLOSED

Reason:
OpenAI provider unavailable
```

Previous audits established that HIRR, conversational routing, replay restoration, lifecycle continuation, and PPP restored-context handoff are correct. This audit starts immediately after successful PPP continuation reaches provider proposal production.

## 2. Complete Execution Trace

Current execution path after PPP continuation:

```text
continue_context_assembled_to_ppp_routing(...)
-> run_conversation_ppp_routing_integration(...)
-> resolve_domain_worker_milestone(...)
-> classify_provider_necessity(...)
-> validate_development_proposal_contract(...)
-> create_conversation_to_implementation_handoff(...)
-> produce_provider_development_proposal(...)
-> run_provider_attachment(...)
-> OpenAIProviderAdapter.generate_proposal(...)
-> OpenAIProviderAdapter._call_openai(...)
-> OpenAIHTTPClient.__call__(...)
-> FAILED_CLOSED: OpenAI provider unavailable
```

Relevant code locations:

- `aigol/cli/aigol_cli.py:724-729`: post-context continuation provider registry and adapter are constructed.
- `aigol/cli/aigol_cli.py:3523-3539`: restored native context continuation invokes PPP with `provider_id=OPENAI_PROVIDER_ID`.
- `aigol/runtime/conversation_ppp_routing_integration.py:104-125`: provider necessity is classified and must be `PROVIDER_REQUIRED`.
- `aigol/runtime/conversation_ppp_routing_integration.py:126-148`: seed proposal and implementation handoff are created.
- `aigol/runtime/conversation_ppp_routing_integration.py:149-160`: provider proposal production is invoked.
- `aigol/runtime/provider_proposal_production_runtime.py:79-140`: provider request packet, prompt projection, and provider attachment are created.
- `aigol/provider/provider_runtime.py:51-113`: provider attachment runtime performs lookup, readiness checks, adapter validation, request validation, and adapter call.
- `aigol/provider/providers/openai_provider.py:66-103`: OpenAI adapter creates request payload and calls OpenAI.
- `aigol/provider/providers/openai_provider.py:105-118`: adapter maps client/transport exceptions to `OpenAI provider unavailable`.
- `aigol/provider/providers/openai_provider.py:136-158`: HTTP client maps URL, timeout, and decode failures to `OpenAI provider unavailable`.

## 3. Provider Pipeline Sequence

The provider pipeline sequence is deterministic:

```text
Provider Request Packet
-> Provider Request Prompt Projection
-> Provider Attachment
-> Provider Adapter Invocation
-> Provider Proposal Production Result
-> PPP Route Result
-> Post-Context Continuation Result
```

The reproduced Golden Scenario #001 reached the provider proposal production stage and created provider-stage replay evidence under:

```text
TURN-000002/post_context_continuation/conversation_ppp_routing/provider_proposal_production
```

## 4. Provider Request Lifecycle

### 4.1 Provider Request Artifact

A provider request artifact is created.

Replay files observed in reproduction:

```text
provider_proposal_production/000_provider_request_packet_prepared.json
provider_proposal_production/000_provider_request_prompt_projection.json
```

Provider request packet:

```text
artifact_type: PROVIDER_REQUEST_PACKET_V1
production_id: <session>:TURN-000002:PPP-PROVIDER-PROPOSAL-PRODUCTION
provider_id: openai
canonical_chain_id: <preserved chain id>
context_reference: <session>:TURN-000001:DEVELOPMENT_CONTEXT_ASSEMBLY
handoff_reference: <session>:TURN-000002:PPP-PROVIDER-REQUEST-HANDOFF
provider_request_hash: sha256:...
```

Prompt projection:

```text
artifact_type: PROVIDER_REQUEST_PROMPT_PROJECTION_V1
provider_id: openai
adapter_request_shape: OPENAI_PROVIDER_PROMPT_REQUEST
proposal_only: true
provider_authority: false
execution_requested: false
dispatch_requested: false
worker_created: false
domain_created: false
governance_modified: false
replay_modified: false
```

Request contents are a bounded proposal-only prompt beginning with:

```text
Produce one DEVELOPMENT_PROPOSAL_ARTIFACT_V1-compatible JSON object.
The proposal must remain proposal-only and non-authoritative.
```

The request includes task reference, domain, worker family, milestone, output targets, constraints, assumptions, and known gaps. It explicitly prohibits authorization, execution, dispatch, worker creation, domain creation, governance mutation, and replay mutation.

Conclusion:

```text
PROVIDER_REQUEST_CREATED
```

## 5. Provider Selection Review

There is no independent provider-selection runtime in this continuation path.

The selected provider is determined by the CLI continuation call:

```python
provider_id=OPENAI_PROVIDER_ID
registry=_post_context_continuation_provider_registry()
adapter=_post_context_continuation_provider_adapter()
```

Code locations:

- `aigol/cli/aigol_cli.py:724-729`
- `aigol/cli/aigol_cli.py:3527-3532`

The registry contains OpenAI because `_conversation_openai_provider_registry()` registers:

```python
openai_provider_metadata()
```

Provider considered:

```text
openai
```

Why OpenAI became selected:

```text
The post-context continuation path passes OPENAI_PROVIDER_ID directly.
```

This is deterministic and not a provider-selection defect. It is a fixed-provider continuation policy, not a multi-provider selection process.

Conclusion:

```text
PROVIDER_SELECTION_FIXED_BY_CONTINUATION_PATH
```

## 6. Provider Attachment Review

Provider attachment is attempted by:

```text
aigol/provider/provider_runtime.py
run_provider_attachment(...)
```

Inputs:

```text
provider_id: openai
request: PROVIDER_REQUEST_PROMPT_PROJECTION_V1
proposal_id: <production_id>:PROVIDER-ENVELOPE
timestamp: created_at
registry: ProviderRegistry containing openai
adapter: OpenAIProviderAdapter
replay_dir: provider_proposal_production/provider_attachment
```

Attachment runtime steps:

1. Lookup provider metadata.
2. Run provider readiness checks when adapter supports readiness.
3. Validate provider status.
4. Validate adapter identity and version.
5. Validate request serialization and forbidden fields.
6. Call `adapter.generate_proposal(...)`.
7. Persist success or fail-closed replay.

Observed attachment result:

```text
event_type: FAILED_CLOSED
provider_id: openai
provider_invoked: false
failure_reason: OpenAI provider unavailable
failure_diagnostics:
  failure_stage: openai_http_request
  exception_type: URLError
  transport_failure_category: URL_ERROR
  http_status: null
```

Replay files:

```text
provider_proposal_production/provider_attachment/000_provider_proposal_created.json
provider_proposal_production/provider_attachment/001_provider_proposal_returned.json
```

Conclusion:

```text
PROVIDER_ATTACHMENT_ATTEMPTED_AND_FAILED_CLOSED
```

## 7. Provider Invocation Review

Provider invocation was attempted at the adapter transport boundary.

Execution path:

```text
run_provider_attachment(...)
-> adapter.generate_proposal(...)
-> OpenAIProviderAdapter._call_openai(...)
-> OpenAIHTTPClient.__call__(...)
```

The replay marks:

```text
provider_invoked: false
provider_invocation_status: PROVIDER_NOT_INVOKED
```

This means no successful provider proposal envelope was captured. It does not mean the adapter never attempted transport. The provider attachment failure diagnostics show:

```text
failure_stage: openai_http_request
exception_type: URLError
transport_failure_category: URL_ERROR
```

Therefore:

```text
Transport invocation was attempted.
Governed provider proposal invocation did not complete.
No provider proposal envelope was accepted.
```

## 8. Exact Fail-Closed Source

The operator-facing reason:

```text
OpenAI provider unavailable
```

is produced by:

```text
aigol/provider/providers/openai_provider.py
OpenAIProviderAdapter._call_openai(...)
```

Deterministic condition:

```python
except Exception as exc:
    raise FailClosedRuntimeError("OpenAI provider unavailable") from exc
```

For the default HTTP client, equivalent mapping also exists in:

```text
aigol/provider/providers/openai_provider.py
OpenAIHTTPClient.__call__(...)
```

where:

```python
except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
    raise FailClosedRuntimeError("OpenAI provider unavailable") from exc
```

The provider attachment runtime records sanitized diagnostics from the exception chain:

```text
failure_stage: openai_http_request
exception_type: URLError
transport_failure_category: URL_ERROR
http_status: null
```

Conclusion:

```text
FAILED_CLOSED_ORIGIN = OpenAI adapter transport failure mapping
```

## 9. Failure Classification

Classification for the reproduced Golden Scenario #001:

```text
D) provider invocation failed
```

More specifically:

```text
OpenAI provider transport failed with URLError.
```

Not supported by observed evidence:

- provider selection defect;
- PPP continuation defect;
- provider attachment contract defect;
- governance defect;
- replay defect;
- approval defect.

Possible environmental causes include network restriction, DNS/connection failure, endpoint unavailability, or equivalent transport failure. The replay evidence classifies it as `URL_ERROR`, not as a deterministic routing or governance failure.

## 10. Replay Evidence Review

Replay records:

| Evidence | Status | Replay Location |
| --- | --- | --- |
| Provider Request Packet | PRESENT | `provider_proposal_production/000_provider_request_packet_prepared.json` |
| Provider Prompt Projection | PRESENT | `provider_proposal_production/000_provider_request_prompt_projection.json` |
| Provider Attachment | PRESENT | `provider_proposal_production/provider_attachment/` |
| Provider Invocation Attempt Diagnostics | PRESENT | provider attachment `failure_diagnostics` |
| Provider Proposal Production Result | PRESENT | `provider_proposal_production/002_development_proposal_artifact_produced.json` |
| Provider Proposal Production Return | PRESENT | `provider_proposal_production/003_provider_proposal_production_returned.json` |
| Provider Selection Event | NOT SEPARATE | Selection is fixed by CLI continuation path and provider id input. |

Provider-stage replay evidence is sufficient to reconstruct:

- provider request creation;
- OpenAI as fixed selected provider;
- attachment attempt;
- transport-stage failure;
- fail-closed result;
- non-authority flags;
- absence of worker execution.

Replay limitation:

```text
There is no standalone provider-selection replay artifact in this path.
```

This is not necessarily a defect because this path does not perform multi-provider selection. However, hardening diagnostics should explicitly state that the provider was fixed by continuation policy rather than selected by a separate provider-selection runtime.

## 11. Governance Impact

Governance behavior is correct.

Verified:

- fail-closed behavior is preserved;
- no provider output was accepted;
- no worker was invoked;
- no execution was requested;
- no dispatch was requested;
- no approval model was changed;
- no governance mutation occurred;
- no replay mutation occurred outside append-only evidence;
- OpenAI remained non-authoritative.

Conclusion:

```text
NO_GOVERNANCE_DEFECT
```

## 12. Replay Impact

Replay remains authoritative.

The provider-stage failure is replay-visible and reconstructable. The important replay evidence is nested below the provider proposal production stage, not only in the top-level ACLI failure message.

Recommended hardening interpretation:

```text
Top-level failure message is a summary.
Provider attachment replay is the source of truth for failure stage and diagnostic category.
```

## 13. Provider State Verification

The runtime can distinguish several provider states:

| Provider State | Current Support | Evidence |
| --- | --- | --- |
| provider missing | SUPPORTED | `ProviderRegistry.lookup_provider(...)` raises `provider is unknown`. |
| provider disabled/unavailable by metadata | SUPPORTED | `provider_status != AVAILABLE` raises `provider is unavailable`. |
| missing API key | SUPPORTED for OpenAI readiness adapters | readiness diagnostic `MISSING_API_KEY`, surfaced as `OPENAI_API_KEY is required`. |
| provider configuration invalid | SUPPORTED | readiness diagnostic `PROVIDER_CONFIGURATION_INVALID`. |
| model configuration invalid | SUPPORTED | readiness diagnostic `MODEL_CONFIGURATION_INVALID`. |
| transport unavailable | SUPPORTED | readiness diagnostic `TRANSPORT_UNAVAILABLE` when client is not callable. |
| transport failure during request | SUPPORTED | failure diagnostics include `URL_ERROR`, `TIMEOUT`, `HTTP_ERROR`, or `JSON_DECODE`. |
| provider authorization failure | PARTIAL | HTTP status can distinguish `HTTP_ERROR`, but operator message does not specialize authorization failures. |

Limitation:

```text
The operator-facing message collapses several transport/runtime failures into "OpenAI provider unavailable".
Replay diagnostics are more specific than the user-visible output.
```

## 14. UX Impact

Current operator-facing message:

```text
FAILED_CLOSED:
OpenAI provider unavailable
```

This is accurate but incomplete for hardening and non-technical operation.

It does not explain:

- provider request was created;
- OpenAI was the fixed provider for this continuation path;
- provider attachment was attempted;
- the failure occurred at HTTP transport;
- no provider proposal was accepted;
- no worker executed;
- replay contains diagnostic details.

Recommended fail-closed diagnostic:

```text
Provider stage failed closed.

What succeeded:
- PPP continuation reached provider proposal production.
- A proposal-only provider request was created.
- OpenAI was the configured provider for this continuation path.

Where it failed:
- Provider: OpenAI
- Stage: HTTP request
- Diagnostic: URL_ERROR

What did not happen:
- No provider proposal was accepted.
- No worker executed.
- No repository mutation occurred.
- No execution was authorized.

Replay:
<provider_proposal_production_replay_reference>
```

This is a UX/diagnostic improvement only. It does not change governance behavior.

## 15. Root Cause

Root cause:

```text
OpenAI provider transport was unavailable during provider proposal production.
```

Immediate source:

```text
OpenAIProviderAdapter._call_openai(...)
```

Observed diagnostic:

```text
failure_stage: openai_http_request
exception_type: URLError
transport_failure_category: URL_ERROR
```

This is expected fail-closed behavior when a provider transport cannot complete.

## 16. Implementation Complexity

If a repair is pursued, the complexity is:

```text
LOW
```

Reason:

- provider failure detection already exists;
- replay diagnostics already exist;
- governance behavior is correct;
- the main gap is operator-facing diagnostic propagation from nested provider attachment replay to ACLI output and hardening summaries.

No architecture change is required.

## 17. Minimal Repair Recommendation

No provider-pipeline repair is required for correctness.

Optional Feature-Freeze-compliant improvements:

1. Propagate provider attachment failure diagnostics into the top-level post-context continuation summary.

2. Add hardening evidence fields for:

```text
provider_stage
provider_id
provider_failure_category
provider_failure_exception_type
provider_http_status
```

3. Improve operator message as described in the UX section.

4. Preserve replay as the source of truth and do not introduce autonomous retry, provider switching, or provider selection changes.

## 18. Regression Requirements

If diagnostic propagation is implemented later, add regression tests for:

1. Provider request packet is created before provider failure.

2. Provider prompt projection is replay-visible.

3. OpenAI transport failure records:

```text
failure_stage: openai_http_request
transport_failure_category: URL_ERROR
```

4. Missing API key records:

```text
readiness_stage: api_key_presence
failure_category: MISSING_API_KEY
```

5. Provider metadata unavailable records:

```text
provider is unavailable
```

6. Provider unknown records:

```text
provider is unknown
```

7. Operator output includes provider stage diagnostics but does not expose credentials, request body secrets, raw response bodies, or stack traces.

8. No worker invocation occurs on provider failure.

9. Replay reconstruction validates provider attachment failure evidence.

## 19. Final Assessment

The provider pipeline behaved correctly.

Confirmed:

```text
Provider request was created.
Provider prompt projection was created.
OpenAI was selected deterministically by the continuation path.
Provider attachment was attempted.
OpenAI transport invocation was attempted.
Provider proposal production failed closed.
Replay captured provider diagnostics.
Governance remained unchanged.
No unauthorized execution occurred.
```

Final verdict:

```text
PROVIDER_ATTACHMENT_CONTINUATION_AUDIT_COMPLETE
```
