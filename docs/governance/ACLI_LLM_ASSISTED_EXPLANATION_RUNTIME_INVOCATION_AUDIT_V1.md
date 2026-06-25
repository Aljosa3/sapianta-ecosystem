# ACLI LLM Assisted Explanation Runtime Invocation Audit V1

Status: COMPLETE

Verdict: ACLI_LLM_ASSISTED_EXPLANATION_RUNTIME_INVOCATION_COMPLETE

## 1. Objective

This audit determines whether the integrated LLM-assisted explanation runtime is actually invoked during a live governed development proposal.

Reviewed runtime surfaces:

- `aigol/cli/aigol_cli.py`;
- `aigol/runtime/acli_human_friendly_explanation_runtime.py`;
- `aigol/runtime/acli_llm_assisted_explanation_runtime.py`.

The audit traces:

- runtime call path;
- provider invocation;
- rendered operator output;
- replay evidence.

## 2. Executive Finding

The LLM-assisted explanation runtime is integrated into the live governed development proposal path, but it is optional and disabled by default.

Current behavior:

| Scenario | Assisted Runtime Called | Provider Invoked | Provider Explanation Rendered | Replay Evidence |
| --- | --- | --- | --- | --- |
| default live ACLI proposal | No | No | No | deterministic explanation only |
| `--enable-llm-assisted-explanation` with no provider | Yes | No | No | assisted fallback replay |
| injected explanation provider | Yes | Yes | Yes | assisted provider replay |

Therefore:

```text
Integrated: yes
Default operator invocation: no
Provider invocation by default: no
Provider rendering by default: no
```

This is expected for the current integration because provider-assisted explanation is an optional augmentation layer, not the authoritative explanation path.

## 3. Live Call Path

The governed development proposal path in `aigol_cli.py` is:

```text
run_interactive_conversation()
-> propose_acli_governed_development_execution()
-> create_acli_human_friendly_explanation()
-> render_acli_human_friendly_explanation()
-> optional LLM-assisted explanation gate
-> render_acli_governed_development_bridge_summary()
```

The assisted explanation gate is:

```text
llm_assisted_explanation_enabled = (
    args.enable_llm_assisted_explanation
    or llm_explanation_provider is not None
)
```

When the gate is true, ACLI calls:

```text
authoritative_state_from_acli_proposal_capture()
create_acli_llm_assisted_explanation()
```

When the provider response is accepted, ACLI renders:

```text
PROVIDER-ASSISTED EXPLANATION
<provider explanation text>
```

## 4. Deterministic Explanation Path

The deterministic explanation runtime remains the default live path.

It creates replay evidence under:

```text
TURN-000001/human_friendly_explanation/
000_acli_human_friendly_explanation_recorded.json
```

It remains:

- non-authoritative;
- replay-visible;
- approval-neutral;
- execution-neutral;
- always available for governed development proposal explanation.

The deterministic explanation text is also passed into the assisted runtime as the fallback explanation when assisted explanation is enabled.

## 5. Assisted Runtime Invocation Conditions

The assisted runtime is called only when one of these conditions is true:

```text
--enable-llm-assisted-explanation
```

or:

```text
run_interactive_conversation(..., llm_explanation_provider=<provider>)
```

If neither condition is true, the live governed development proposal path does not call:

```text
create_acli_llm_assisted_explanation()
```

No assisted replay artifact is created in the default path.

## 6. Provider Invocation Conditions

Inside `acli_llm_assisted_explanation_runtime.py`, provider invocation occurs only when a provider object is supplied.

Supported provider forms:

```text
callable provider(request_artifact) -> dict
provider.generate_explanation(request_artifact) -> dict
```

If the assisted runtime is enabled but no provider is supplied, `_invoke_provider()` returns:

```text
EXPLANATION_PROVIDER_NOT_CONFIGURED
```

and the runtime records:

```text
DETERMINISTIC_FALLBACK_USED
provider_invoked: false
provider_explanation_used: false
deterministic_fallback_used: true
```

This is a configuration outcome, not a missing runtime call.

## 7. Provider Rendering Conditions

Provider explanation is rendered only when:

```text
provider_explanation_used: true
```

If the provider is missing, unavailable, malformed, or violates fidelity checks, ACLI records fallback replay and does not render the provider-assisted section.

The operator-visible proof of provider rendering is:

```text
PROVIDER-ASSISTED EXPLANATION
```

followed by the provider explanation text.

If the assisted runtime falls back to deterministic explanation, this provider section is intentionally not rendered because the deterministic explanation has already been shown.

## 8. Replay Evidence Model

When assisted explanation is invoked, replay evidence is written under:

```text
TURN-000001/llm_assisted_explanation/
000_acli_llm_assisted_explanation_recorded.json
```

The replay artifact must contain:

- authoritative state;
- authoritative state hash;
- deterministic explanation;
- deterministic explanation hash;
- explanation request artifact;
- explanation response artifact;
- provider id;
- provider invocation status;
- provider explanation status;
- fallback reason when applicable;
- rendered explanation hash;
- advisory-only authority flags.

Replay reconstruction is performed by:

```text
reconstruct_acli_llm_assisted_explanation_replay()
```

The reconstruction verifies artifact hashes, rendered explanation hash, and provider response fidelity against authoritative state.

## 9. Validation Trace

### 9.1 Default Live ACLI Proposal

Prompt:

```text
Create governance artifact ACLI_INVOCATION_AUDIT_TEST_V1 documenting LLM assisted explanation invocation.
```

Observed:

```text
workflow: GOVERNED_DEVELOPMENT_WORKFLOW
response_status: APPROVAL_REQUIRED
has_llm_keys: False
contains_provider_section: False
replay_dirs:
- human_friendly_explanation
```

Conclusion:

```text
Assisted runtime not called.
Provider not invoked.
No assisted replay evidence created.
```

Reason:

```text
Feature flag disabled and no provider injected.
```

### 9.2 Assisted Runtime Enabled With No Provider

Invocation mode:

```text
--enable-llm-assisted-explanation
```

Observed:

```text
workflow: GOVERNED_DEVELOPMENT_WORKFLOW
status: DETERMINISTIC_FALLBACK_USED
provider_invoked: False
provider_used: False
fallback_used: True
contains_provider_section: False
replay_status: DETERMINISTIC_FALLBACK_USED
replay_provider_used: False
replay_dirs:
- human_friendly_explanation
- llm_assisted_explanation
```

Conclusion:

```text
Assisted runtime called.
Provider not invoked.
Fallback replay recorded.
Provider explanation not rendered.
```

Reason:

```text
No provider contract or provider object was supplied.
```

### 9.3 Assisted Runtime With Injected Provider

Invocation mode:

```text
run_interactive_conversation(..., llm_explanation_provider=provider)
```

Observed:

```text
workflow: GOVERNED_DEVELOPMENT_WORKFLOW
status: PROVIDER_EXPLANATION_USED
provider_invoked: True
provider_used: True
contains_provider_section: True
contains_provider_text: True
replay_status: PROVIDER_EXPLANATION_USED
replay_provider_used: True
artifact_ids:
- ACLI_INVOCATION_AUDIT_TEST_V1
```

Conclusion:

```text
Assisted runtime called.
Provider invoked.
Provider response accepted.
Provider explanation rendered.
Replay reconstruction verified invocation.
```

## 10. Answers

### 10.1 Is The Runtime Called?

Default live ACLI:

```text
No.
```

Opt-in assisted mode:

```text
Yes.
```

Injected provider mode:

```text
Yes.
```

### 10.2 If Called, Does Provider Invocation Occur?

With no provider:

```text
No. The runtime records deterministic fallback.
```

With an injected provider:

```text
Yes. The runtime invokes the provider and validates response fidelity.
```

### 10.3 If Provider Invocation Does Not Occur, Why?

For the default path:

```text
Feature flag disabled.
No provider injected.
Assisted runtime gate not entered.
```

For the enabled fallback path:

```text
Assisted runtime entered.
No provider object configured.
Provider invocation skipped with EXPLANATION_PROVIDER_NOT_CONFIGURED.
```

This is not caused by:

- missing runtime call in opt-in mode;
- provider disabled by governance;
- missing provider response contract in the runtime.

The actual cause is configuration: no provider is supplied to the optional explanation layer.

### 10.4 If Provider Invocation Occurs, Why Is No Provider Explanation Rendered?

When provider invocation succeeds and response fidelity passes, provider explanation is rendered.

If provider invocation occurs but no provider explanation is rendered, expected causes are:

- provider raised an exception;
- provider returned malformed output;
- provider failed artifact identifier preservation;
- provider failed target path preservation;
- provider failed approval state preservation;
- provider failed replay reference preservation;
- provider attempted to claim authority.

In those cases, the runtime records deterministic fallback and intentionally suppresses duplicate provider rendering.

### 10.5 What Replay Evidence Proves Invocation?

Invocation is proven by:

```text
TURN-000001/llm_assisted_explanation/
000_acli_llm_assisted_explanation_recorded.json
```

and turn-summary fields:

```text
llm_assisted_explanation_replay_reference
llm_assisted_explanation_artifact_type
llm_assisted_explanation_status
llm_assisted_explanation_provider_id
llm_assisted_explanation_provider_invoked
llm_assisted_explanation_provider_used
llm_assisted_explanation_deterministic_fallback_used
llm_assisted_explanation_advisory_only
llm_assisted_explanation_authority_granted
llm_assisted_explanation_rendered_hash
```

Provider rendering is proven by operator output containing:

```text
PROVIDER-ASSISTED EXPLANATION
```

and replay reconstruction returning:

```text
provider_explanation_used: true
```

## 11. Authority Boundary Verification

The assisted explanation runtime does not alter:

- workflow selection;
- approval state;
- proposal hash;
- replay evidence;
- execution decisions;
- mutation behavior;
- validation behavior.

Its replay artifact records:

```text
advisory_only: true
visibility_only: true
authority_granted: false
provider_authority: false
approval_authority: false
execution_authority: false
worker_authority: false
approval_granted: false
execution_authorized: false
mutation_performed: false
worker_invoked: false
validation_executed: false
```

ACLI remains authoritative for workflow state.

Human approval remains authoritative for execution authorization.

## 12. Final Determination

The integrated LLM-assisted explanation runtime is live but optional.

Default operator runs still use deterministic explanation only.

To prove assisted runtime invocation, enable the feature flag or inject/configure a provider and inspect:

```text
llm_assisted_explanation_replay_reference
000_acli_llm_assisted_explanation_recorded.json
```

To prove provider explanation rendering, inspect operator output for:

```text
PROVIDER-ASSISTED EXPLANATION
```

and replay reconstruction for:

```text
PROVIDER_EXPLANATION_USED
```

## 13. Final Verdict

```text
ACLI_LLM_ASSISTED_EXPLANATION_RUNTIME_INVOCATION_COMPLETE
```
