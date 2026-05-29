# Overengineering Risks V1

Status: risks to avoid before first useful AiGOL.

## Risk 1: Capability Expansion Before Usability

Adding write, shell, network, API, or additional read-only capability surfaces before the current flow is usable risks expanding the architecture without improving first usefulness.

Recommendation:

Do not add new capabilities until operator invocation, result readability, replay summary, and pressure validation are complete.

## Risk 2: Orchestration Runtime

Orchestration is attractive but not required for first useful AiGOL.

Risk:

- hidden continuation
- recursive coordination
- authority ambiguity
- replay complexity

Recommendation:

Keep orchestration out of scope.

## Risk 3: Persistent Memory

Memory expansion is not required for first useful read-only operation.

Risk:

- hidden state
- identity drift
- replay ambiguity
- implicit authority continuity

Recommendation:

Use replay evidence, not memory, as the source of continuity.

## Risk 4: Semantic Routing

Automatic prompt-to-capability selection may look useful, but semantic routing can become hidden autonomy.

Recommendation:

If needed, use deterministic rule mapping only after first useful operator flow exists.

## Risk 5: Governance Artifact Proliferation

The governance substrate has many artifacts. More governance documents can reduce clarity if they repeat existing constraints.

Recommendation:

Prefer consolidation, indexes, and operator-facing summaries over new conceptual layers.

## Risk 6: General Agent Framing

AiGOL should not be framed as an agent runtime or autonomous assistant.

Recommendation:

Keep product language focused on governed execution, replay evidence, authorization, and bounded read-only results.

## Risk 7: Premature Refactoring

Replay helper duplication exists, but refactoring too early may obscure fail-closed behavior.

Recommendation:

Refactor only when the duplicated patterns become a practical maintenance problem and tests are strong enough to preserve behavior.
