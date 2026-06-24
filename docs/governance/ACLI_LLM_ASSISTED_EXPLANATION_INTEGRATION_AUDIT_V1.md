# ACLI LLM Assisted Explanation Integration Audit V1

Status: COMPLETE

Verdict: ACLI_LLM_ASSISTED_EXPLANATION_INTEGRATION_AUDIT_COMPLETE

## 1. Objective

This audit determines whether `ACLI_LLM_ASSISTED_EXPLANATION_PROTOTYPE_V1` is currently integrated into any live ACLI conversational path.

Reviewed surfaces:

- `aigol/cli/aigol_cli.py`;
- deterministic human-friendly explanation runtime;
- `aigol/runtime/acli_llm_assisted_explanation_runtime.py`;
- governed development proposal flow;
- approval flow;
- replay reconstruction flow.

## 2. Executive Finding

`ACLI_LLM_ASSISTED_EXPLANATION_PROTOTYPE_V1` exists as a tested runtime module, but it is not currently wired into the live ACLI conversational path.

Current live ACLI behavior:

```text
Human prompt
-> ACLI conversational routing
-> governed development proposal
-> deterministic human-friendly explanation
-> approval request
-> replay record for deterministic explanation
```

Current live ACLI behavior does not include:

```text
authoritative explanation state
-> LLM-assisted explanation request
-> explanation provider invocation
-> LLM-assisted explanation replay record
-> LLM-assisted operator rendering
```

## 3. Runtime Reachability

### 3.1 Module Reachability

The prototype runtime exists:

```text
aigol/runtime/acli_llm_assisted_explanation_runtime.py
```

It defines:

```text
create_acli_llm_assisted_explanation()
authoritative_state_from_acli_proposal_capture()
reconstruct_acli_llm_assisted_explanation_replay()
render_acli_llm_assisted_explanation()
```

The module is importable and covered by:

```text
tests/test_acli_llm_assisted_explanation_runtime_v1.py
```

### 3.2 Live Conversational Reachability

The prototype runtime is not imported by the live ACLI conversational entrypoint.

`aigol/cli/aigol_cli.py` imports only the deterministic explanation runtime:

```text
from aigol.runtime.acli_human_friendly_explanation_runtime import (
    create_acli_human_friendly_explanation,
    render_acli_human_friendly_explanation,
)
```

No import exists in the live CLI path for:

```text
create_acli_llm_assisted_explanation
authoritative_state_from_acli_proposal_capture
render_acli_llm_assisted_explanation
```

Therefore the prototype runtime is reachable to tests and direct Python callers, but not reachable from the operator-facing ACLI conversation loop.

## 4. Invocation Review

Repository-wide Python caller search found live definitions and tests, but no production caller:

```text
aigol/runtime/acli_llm_assisted_explanation_runtime.py
tests/test_acli_llm_assisted_explanation_runtime_v1.py
```

No governed development proposal path, approval path, replay reconstruction path, or CLI output path invokes:

```text
create_acli_llm_assisted_explanation()
```

Current answer:

```text
Is the runtime invoked anywhere in live ACLI? No.
```

## 5. Governed Development Proposal Flow

The live governed development proposal path is:

```text
aigol/cli/aigol_cli.py
-> propose_acli_governed_development_execution()
-> create_acli_human_friendly_explanation()
-> render_acli_human_friendly_explanation()
-> render_acli_governed_development_bridge_summary()
```

The governing code path creates the deterministic explanation after an approval-required proposal:

```text
if bridge_capture.get("bridge_status") == ACLI_GOVERNED_DEVELOPMENT_APPROVAL_REQUIRED:
    pending_governed_development_bridge = bridge_capture
    human_friendly_explanation_capture = create_acli_human_friendly_explanation(...)
    output_writer(render_acli_human_friendly_explanation(human_friendly_explanation_capture))
    output_writer(render_acli_governed_development_bridge_summary(bridge_capture))
```

No LLM-assisted explanation runtime is invoked before or after deterministic explanation rendering.

## 6. Approval Flow

The approval flow consumes pending governed development proposal state and executes only after valid approval handling.

The LLM-assisted explanation runtime has no approval authority and is not currently attached to approval handling.

Current approval flow does not:

- generate provider-assisted approval explanations;
- record provider explanation artifacts;
- render provider-assisted approval guidance;
- use provider output to authorize or reject execution.

This preserves the existing approval boundary, but it also means the prototype is not part of live approval UX.

## 7. Replay Reconstruction Flow

The deterministic human-friendly explanation replay flow is live.

The deterministic runtime persists:

```text
000_acli_human_friendly_explanation_recorded.json
```

and reconstructs it through:

```text
reconstruct_acli_human_friendly_explanation_replay()
```

The LLM-assisted runtime can persist:

```text
000_acli_llm_assisted_explanation_recorded.json
```

and reconstruct it through:

```text
reconstruct_acli_llm_assisted_explanation_replay()
```

However, because the live CLI never invokes the assisted runtime, live ACLI replay currently contains deterministic explanation evidence only.

## 8. Provider Review

The prototype runtime supports two provider interfaces:

```text
callable provider(request_artifact) -> dict
provider.generate_explanation(request_artifact) -> dict
```

The provider response must preserve:

- artifact identifiers;
- target paths;
- approval state;
- replay references.

Malformed, unavailable, or unsupported providers fall back to deterministic explanation text.

Current live ACLI provider answer:

```text
Which providers can be used by live ACLI? None are configured or wired.
```

The runtime can accept provider objects if called directly, but `aigol_cli.py` does not currently expose a provider selector, provider registry lookup, provider configuration, or provider invocation point for assisted explanations.

## 9. Deterministic Explanation Status

Deterministic explanation remains the live default and the only live explanation path.

Current deterministic explanation properties:

- replay-visible;
- non-authoritative;
- provider-free;
- rendered before approval;
- attached to the turn summary;
- reconstructable from replay.

The LLM-assisted explanation prototype also preserves non-authority when called directly, but that property is not exercised in live ACLI conversation because the runtime is not invoked.

## 10. Operator-Visible Invocation Proof

Operator-visible evidence that LLM-assisted explanation had been invoked would include at least one of:

- an output section explicitly identifying provider-assisted explanation status;
- `PROVIDER_EXPLANATION_USED`;
- `DETERMINISTIC_FALLBACK_USED` from the assisted runtime;
- a provider identifier;
- a replay reference under an `llm_assisted_explanation` directory;
- turn-summary fields beginning with `llm_assisted_explanation_*`;
- replay artifact type `ACLI_LLM_ASSISTED_EXPLANATION_ARTIFACT_V1`.

Live validation produced:

```text
workflow: GOVERNED_DEVELOPMENT_WORKFLOW
response_status: APPROVAL_REQUIRED
human_friendly_ref: .../TURN-000001/human_friendly_explanation
has_llm_assisted_key: False
replay_dirs: ['.../TURN-000001/human_friendly_explanation']
```

The only explanation replay directory created by the live turn was:

```text
human_friendly_explanation
```

No `llm_assisted_explanation` replay directory or turn-summary field was produced.

## 11. Workflow Coverage

Current live workflow invocation status:

| Workflow / Path | Deterministic Explanation | LLM-Assisted Explanation |
| --- | --- | --- |
| `GOVERNED_DEVELOPMENT_WORKFLOW` proposal | Invoked | Not invoked |
| governed development approval | Not a separate explanation invocation | Not invoked |
| governed development execution | Not a separate explanation invocation | Not invoked |
| replay reconstruction | Deterministic explanation replay supported | Prototype reconstruction exists, but no live artifact is produced |
| non-governed conversational workflows | Not generally invoked | Not invoked |

No currently reviewed workflow invokes `ACLI_LLM_ASSISTED_EXPLANATION_PROTOTYPE_V1`.

## 12. Missing Wiring

The missing integration points are:

1. CLI import wiring for the assisted runtime.

2. Construction of authoritative explanation state from the governed development proposal capture:

```text
authoritative_state_from_acli_proposal_capture(...)
```

3. Invocation policy deciding whether provider assistance is enabled.

4. Provider resolution, such as an injected provider, configured provider, or provider registry adapter.

5. Assisted explanation replay directory allocation, for example:

```text
TURN-000001/llm_assisted_explanation/
```

6. Operator rendering policy deciding whether to show deterministic text, provider text, or deterministic fallback metadata.

7. Turn-summary attachment fields for replay and audit visibility.

8. Replay reconstruction integration for live ACLI transcripts.

These are wiring gaps, not governance authority gaps. The prototype runtime already preserves non-authority and fail-closed validation when called directly.

## 13. Authority Analysis

The current absence of live LLM-assisted wiring preserves:

- ACLI authority over workflow state;
- human approval authority;
- deterministic routing;
- worker protections;
- replay authority.

If integrated later, the provider-assisted explanation runtime must remain advisory only.

The existing prototype already encodes:

```text
advisory_only: True
visibility_only: True
authority_granted: False
provider_authority: False
approval_authority: False
execution_authority: False
worker_authority: False
approval_granted: False
execution_authorized: False
mutation_performed: False
```

Therefore the missing live integration should be added, if desired, as an operator-visibility extension after deterministic state is already established.

## 14. Answers

1. Is the runtime reachable?

```text
Reachable to direct Python callers and tests.
Not reachable from live ACLI conversational execution.
```

2. Is it invoked anywhere?

```text
Invoked by tests.
Not invoked by live ACLI workflows.
```

3. Which workflows invoke it?

```text
No live workflow currently invokes it.
```

4. Which providers can be used?

```text
The runtime can accept a callable provider or an object with generate_explanation().
No provider is currently configured or selected by live ACLI.
```

5. Is deterministic explanation still always used?

```text
Yes, for governed development proposal explanation in the live ACLI path.
```

6. What operator-visible output would prove invocation?

```text
LLM-assisted explanation status, provider id, assisted replay reference,
llm_assisted_explanation turn-summary fields, or an
ACLI_LLM_ASSISTED_EXPLANATION_ARTIFACT_V1 replay artifact.
```

## 15. Recommendation

Do not treat `ACLI_LLM_ASSISTED_EXPLANATION_PROTOTYPE_V1` as live operator-facing functionality yet.

Recommended next implementation step, if provider-assisted explanations are desired:

```text
wire optional assisted explanation after deterministic explanation creation
and before proposal summary rendering
```

The integration should:

- keep deterministic explanation as the default;
- invoke the provider only when explicitly enabled;
- persist both authoritative state and provider response;
- render assisted text as advisory;
- fall back to deterministic explanation on provider failure;
- preserve approval and execution boundaries.

## 16. Final Verdict

```text
ACLI_LLM_ASSISTED_EXPLANATION_INTEGRATION_AUDIT_COMPLETE
```

`ACLI_LLM_ASSISTED_EXPLANATION_PROTOTYPE_V1` is implemented and testable, but it is not currently integrated into any live ACLI conversational path. The live governed development proposal path still uses deterministic human-friendly explanation only.
