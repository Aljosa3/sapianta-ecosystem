# Resolution Strategy Foundation Review V1

Status: foundation review.

Final classification:

```text
RESOLUTION_STRATEGY_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Scope

This review defines a replay-safe, provider-neutral resolution strategy architecture for AiGOL.

It does not implement runtime, routing, workers, providers, execution, or governance mutation.

## Context

AiGOL now has:

- certified conversational runtime;
- provider-assisted responses;
- replay evidence;
- proposal lifecycle foundation.

The current runtime can answer questions, but it does not yet explicitly model which source of truth should be used for a given prompt.

## 1. What Is A Resolution Strategy?

A Resolution Strategy is AiGOL's replay-visible decision about which evidence source category should be used to answer, classify, explain, or escalate a human prompt.

It is not the answer itself.

It is not provider selection by itself.

It is not routing authority by itself.

It is a governance-bounded source-of-truth selection record that explains why AiGOL used a given source category or failed closed.

## 2. Source Categories

The minimal source categories are:

| Category | Meaning |
| --- | --- |
| `SELF_RESOLUTION` | AiGOL answers from deterministic local runtime knowledge or bounded known responses |
| `CONSTITUTIONAL_MEMORY` | AiGOL answers from citation-backed Constitutional Memory evidence |
| `GOVERNANCE` | AiGOL answers from governance artifacts, invariants, ADRs, or certification records |
| `REPLAY` | AiGOL answers from replay-visible operation evidence |
| `PROVIDER` | AiGOL requests semantic assistance after bounded local resolution is insufficient |
| `WORKER` | AiGOL relies on future authorized worker result evidence |
| `COMBINED` | AiGOL uses multiple categories with explicit source precedence and replay-visible composition |

## 3. Selection Method

AiGOL should select the narrowest sufficient source category first.

The foundation order is:

```text
1. REPLAY
2. GOVERNANCE
3. CONSTITUTIONAL_MEMORY
4. SELF_RESOLUTION
5. PROVIDER
6. WORKER
7. COMBINED
```

This order is not a claim that replay is always semantically best. It is a safety ordering: use directly available evidence before requesting external semantic assistance or future execution.

Selection must consider:

- prompt intent;
- required freshness;
- available replay evidence;
- available governance evidence;
- Constitutional Memory citation availability;
- deterministic self-resolution confidence;
- provider necessity;
- worker-result necessity;
- proposal lifecycle eligibility;
- fail-closed conditions.

## 4. Provider Assistance Requirements

Provider assistance may be required for:

- semantic interpretation not covered by deterministic rules;
- unsupported language or phrasing;
- open-ended conversational synthesis;
- provider-assisted classification after deterministic classification fails;
- response drafting where AiGOL has evidence but needs bounded natural-language synthesis.

Provider assistance must remain optional and substitutable. Provider output is proposal evidence only.

## 5. Strategies That Must Never Require Provider Assistance

The following must never require provider assistance:

- replay reconstruction;
- replay integrity verification;
- governance authority determination;
- constitutional invariant enforcement;
- approval or rejection decisions;
- worker authorization validation;
- provider boundary validation;
- fail-closed termination;
- secret handling;
- governance artifact truth determination.

Provider may explain these only when AiGOL permits provider-assisted conversation. Provider may not decide them.

## 6. Replay Visibility

Strategy selection must be replay-visible as a distinct evidence artifact.

A future strategy selection record should include:

```text
strategy_id
source_prompt_id
source_conversation_id optional
selected_strategy
candidate_strategies
selection_reason
evidence_refs
provider_required
provider_used
worker_required
proposal_lifecycle_required
fail_closed_reason optional
created_by = AIGOL
artifact_hash
```

Replay must show:

- which strategies were considered;
- which strategy was selected;
- why provider was or was not required;
- why worker was or was not required;
- which evidence was used;
- whether selection failed closed.

## 7. Constitutional Preservation

Resolution strategy selection preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

| Role | Strategy meaning |
| --- | --- |
| LLM proposes | Provider may suggest interpretation or response content |
| AiGOL governs | AiGOL selects strategy, validates sources, and accepts or rejects output |
| Worker executes | Worker result may become evidence only after authorized execution |
| Replay records | Replay records strategy selection and source evidence |

## 8. Proposal Lifecycle Integration

Resolution Strategy integrates with Proposal Lifecycle by deciding whether a prompt should remain a conversation response or become a proposal candidate.

Strategy outcomes:

| Strategy result | Proposal lifecycle effect |
| --- | --- |
| Evidence answer available | No proposal required |
| Provider synthesis only | No proposal required unless future action is proposed |
| Action candidate detected | Create proposal candidate through AiGOL only |
| Worker result needed | Require proposal lifecycle and future governed execution path |
| Ambiguous action request | Fail closed or create inspection-only proposal candidate |

Provider output may contribute proposal evidence, but AiGOL alone may create proposal lifecycle state.

## Foundation Result

The resolution strategy foundation is ready as an architectural review artifact.

It remains ready with gaps because no runtime selector, routing integration, schema enforcement, replay record implementation, or tests are introduced by this review.

```text
RESOLUTION_STRATEGY_FOUNDATION_STATUS = READY_WITH_GAPS
```
