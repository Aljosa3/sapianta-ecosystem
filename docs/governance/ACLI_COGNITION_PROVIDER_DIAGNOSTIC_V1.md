# ACLI_COGNITION_PROVIDER_DIAGNOSTIC_V1

## 1. Purpose

This diagnostic determines why recent ACLI real-world sessions showed:

- `providers: NONE`;
- `No provider invoked.`;
- `HUMAN_INTENT_CLARIFICATION_INTAKE`;
- `unknown-human-intent`;
- routing confidence `LOW`;
- repeated clarification;
- no cognition provider invocation.

This is a diagnostic artifact only.

No runtime behavior, routing behavior, governance behavior, approval boundary, replay behavior, provider behavior, worker behavior, or test expectation was modified.

## 2. Current Provider Inventory

Diagnostic command inspected the live ACLI conversation provider registry by constructing `_conversation_openai_provider_registry()`.

Observed provider metadata:

```json
[
  {
    "provider_id": "openai",
    "provider_type": "LLM",
    "provider_version": "openai-responses-v1",
    "provider_status": "AVAILABLE",
    "capability": "proposal_generation",
    "execution_capable": false,
    "dispatch_capable": false,
    "authority": false
  }
]
```

Provider inventory conclusion:

- at least one cognition-capable provider metadata entry is registered;
- the provider is marked `AVAILABLE`;
- the provider is non-authoritative;
- the provider is not execution-capable;
- the provider is not dispatch-capable.

## 3. Activation State

The live ACLI conversation adapter is constructed by:

- `aigol/cli/aigol_cli.py::_conversation_openai_provider_adapter`;
- `aigol/cli/aigol_cli.py::_conversation_openai_provider_registry`.

Observed adapter state:

```json
{
  "adapter_provider_id": "openai",
  "adapter_provider_version": "openai-responses-v1",
  "adapter_model": "gpt-5.1",
  "adapter_endpoint": "https://api.openai.com/v1/responses",
  "api_key_env": "OPENAI_API_KEY",
  "api_key_env_present": true
}
```

Activation conclusion:

- metadata registration exists;
- credential environment appears present in this diagnostic environment;
- provider invocation eligibility still depends on routing reaching a provider-invoking branch;
- the observed sessions did not reach provider credential or transport invocation.

## 4. Actual Diagnostic Session

Diagnostic prompts:

```text
Rad bi ustvaril kratek governance artefakt...
Želim samo pripraviti governance dokument. Ne želim izvajanja workerjev ali zapisovanja datotek.
Ne odobrim. Želim ostati samo pri pogovoru...
```

Observed turn summary:

| Turn | Workflow | Status | Provider Invoked | Reason |
| --- | --- | --- | --- | --- |
| 1 | `HUMAN_INTENT_CLARIFICATION_INTAKE` | `CLARIFICATION_REQUIRED` | `false` | `unknown-human-intent`, low confidence |
| 2 | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `WORKFLOW_SELECTED` | `false` | clarification continuity preserved original target |
| 3 | `HUMAN_INTENT_CLARIFICATION_INTAKE` | `CLARIFICATION_REQUIRED` | `false` | rejection/conversation-only prompt not matched to OCS |

Diagnostic output included:

```text
workflow: HUMAN_INTENT_CLARIFICATION_INTAKE
confidence: LOW
matched:
- unknown-human-intent
reason:
Ask deterministic clarification questions for normal human intent before provider fallback.
```

Second-turn continuity selected:

```text
workflow_id: CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
provider_invoked: false
real_llm_provider_used_by_ocs: false
workflow_target_refinement_status: TARGET_PRESERVED_LOW_CONFIDENCE
```

## 5. Runtime Decision Path

The observed path is:

```text
Human Prompt
↓
run_interactive_conversation
↓
route_conversational_cli_intent
↓
conversational_cli_runtime._classify_workflow
↓
HUMAN_INTENT_CLARIFICATION_INTAKE
↓
clarification lifecycle state persisted
↓
operator clarification
↓
continue_human_intent_clarification_to_workflow
↓
_refined_workflow_target
↓
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
↓
provider_invoked = false
```

The path that would invoke OCS provider cognition is separate:

```text
Human Prompt
↓
route_conversational_cli_intent
↓
workflow_id == OCS_LLM_COGNITION
↓
_run_conversational_ocs_llm_cognition
↓
_conversation_openai_provider_registry
↓
_conversation_openai_provider_adapter
↓
provider proposal generation
```

The observed prompts did not enter this path.

## 6. Routing Decisions That Prevent Provider Invocation

Provider invocation is prevented when any of the following occurs:

1. Deterministic workflow selection resolves to a non-provider workflow.
2. HIRR selects `HUMAN_INTENT_CLARIFICATION_INTAKE`.
3. Unknown-domain clarification selects `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`.
4. Clarification continuity preserves the original target with `TARGET_PRESERVED_LOW_CONFIDENCE`.
5. Clarification continuity selects `OCS_LLM_COGNITION`, but ACLI marks `post_clarification_ocs_execution_deferred = true`.
6. Provider-assisted default conversation is not selected.
7. Provider metadata is unavailable.
8. Provider credential or transport fails closed.

The observed sessions were blocked by conditions 2, 3, and 4.

## 7. HIRR Analysis

`HUMAN_INTENT_CLARIFICATION_INTAKE` is deterministic and non-provider by design.

Evidence:

- interactive tests assert `providers: NONE` for normal human intent clarification;
- the turn summary reports `Workflow Name: HUMAN_INTENT_CLARIFICATION_INTAKE`;
- workflow state is `WAITING_FOR_OPERATOR`;
- current lifecycle stage is `CLARIFICATION`;
- required input is `operator clarification`.

HIRR clarification does not invoke a provider directly.

This preserves:

- human authority;
- deterministic routing;
- replay-visible clarification;
- fail-closed behavior;
- provider non-authority.

## 8. Workflow Selection Analysis

The observed first prompt did not match:

- English governance artifact creation rules;
- English native development rules;
- OCS cognition rules;
- domain proposal rules requiring English domain terms.

It therefore entered low-confidence clarification.

The second prompt:

```text
Želim samo pripraviti governance dokument. Ne želim izvajanja workerjev ali zapisovanja datotek.
```

did not contain deterministic refinement signals recognized by `_refined_workflow_target`.

Specifically:

- it did not match advisory signals such as `advisory`, `guidance`, `plan only`, `analyze`, `recommend`, `no implementation`, or Slovenian phrases currently listed for advisory routing;
- it did not match unresolved ambiguity signals such as `help me decide`, `safest interpretation`, or their supported variants;
- it did not match bounded proof-file signals;
- it did not match governed workflow signals strongly enough to refine the target differently.

The result was:

```text
TARGET_PRESERVED_LOW_CONFIDENCE
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
provider_invoked: false
```

## 9. Provider Invocation Decision Analysis

Provider invocation requires a selected provider-invoking workflow.

Current provider-invoking conversational paths include:

- `OCS_LLM_COGNITION`;
- `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`;
- provider-assisted intent classification in dedicated runtimes;
- provider proposal production in PPP-oriented runtimes.

The observed path selected neither `OCS_LLM_COGNITION` nor `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`.

Even when human-intent clarification continuity refines to `OCS_LLM_COGNITION`, ACLI currently records:

```python
post_clarification_ocs_execution_deferred = True
post_clarification_ocs_replay_reference = None
post_clarification_ocs_llm_cognition = {}
provider_invoked = False
provider_ids = []
real_llm_provider_used_by_ocs = False
live_provider_response_received = False
```

Therefore clarification responses can select an OCS workflow target, but they do not currently execute provider cognition in that same clarification-continuity turn.

## 10. Multilingual Considerations

The routing pipeline has limited multilingual support.

Observed support:

- provider onboarding includes Slovenian normalization for terms such as `dodaj`, `uporabljati`, and provider names;
- some clarification refinement signals include Slovenian phrases such as `samo predlog`, `nič ne spreminjaj`, `pomagaj mi izbrati`, and related advisory phrases.

Observed gap:

- Slovenian governance-document phrasing such as `pripraviti governance dokument`;
- Slovenian worker/file negation such as `ne želim izvajanja workerjev ali zapisovanja datotek`;
- Slovenian conversation-only rejection such as `želim ostati samo pri pogovoru`;
- mixed Slovenian/English governance artifact language.

These phrases do not currently promote the request to proposal-only cognition.

## 11. Decision Tree For Provider Invocation

Provider may be invoked only if all required conditions pass:

```text
1. Human prompt enters ACLI.
2. Lifecycle continuation commands are checked first.
3. Pending approval/continuation state is checked.
4. Conversational routing classifies prompt.
5. Selected workflow must be provider-invoking:
   - OCS_LLM_COGNITION, or
   - DEFAULT_PROVIDER_ASSISTED_CONVERSATION, or
   - an explicit provider-assisted runtime path.
6. Provider registry must contain matching provider metadata.
7. Provider status must be AVAILABLE.
8. Provider metadata must remain non-authoritative:
   - authority = false;
   - execution_capable = false;
   - dispatch_capable = false.
9. Provider adapter must have credential/transport availability.
10. Provider invocation must produce replay-visible proposal/cognition evidence.
11. Provider output remains non-authoritative.
12. Human approval remains required before execution or mutation.
```

Any earlier deterministic clarification, unknown-domain clarification, unsupported workflow, or fail-closed result prevents provider invocation.

## 12. Root Cause

The root cause is routing and clarification signal coverage, not provider registration.

Specifically:

- provider metadata is registered and available;
- credential environment appears present;
- the observed prompts never reached the provider-invoking OCS branch;
- `HUMAN_INTENT_CLARIFICATION_INTAKE` is intentionally non-provider;
- clarification continuity can select `OCS_LLM_COGNITION`, but currently defers actual OCS execution after clarification;
- the Slovenian governance-document clarification did not match existing deterministic advisory/proposal-only cognition signals.

## 13. Behavior Classification

Observed behavior is:

- expected for the current deterministic clarification design;
- routing-related for the user’s desired proposal-only cognition behavior;
- not configuration-related in the observed diagnostic environment;
- not an architectural defect;
- not a provider registration defect;
- not a replay defect;
- not a worker or approval defect.

## 14. Recommendation

Do not change provider behavior.

Do not change governance boundaries.

Do not invoke providers from `HUMAN_INTENT_CLARIFICATION_INTAKE` by default.

Recommended future repair, if desired:

1. Add deterministic multilingual clarification refinement signals for Slovenian governance-document and conversation-only proposal language.
2. Decide whether post-clarification `OCS_LLM_COGNITION` should execute immediately or remain deferred behind an explicit confirmation boundary.
3. Add regression coverage for:
   - `Rad bi ustvaril kratek governance artefakt...`;
   - `Želim samo pripraviti governance dokument. Ne želim izvajanja workerjev ali zapisovanja datotek.`;
   - `Ne odobrim. Želim ostati samo pri pogovoru...`.

Any such repair should be handled as a separate scoped routing implementation, not as a provider implementation.

## 15. Final Verdict

`ROUTING_GAP_CONFIRMED`

Supporting evidence:

- cognition provider metadata is registered and available;
- provider credential environment is present;
- observed ACLI turns remain in clarification workflows;
- clarification workflows intentionally set `provider_invoked = false`;
- multilingual governance-document clarification text is not currently recognized as proposal-only cognition input.

