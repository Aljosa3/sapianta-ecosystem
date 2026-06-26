# ACLI_OCS_PROPOSAL_ONLY_TRACE_V1

## 1. Purpose

This artifact diagnoses why the implemented `ACLI_OCS_PROPOSAL_ONLY_ESCALATION_V1` behavior was not observed during a real ACLI session.

Prompt traced:

```text
Rad bi ustvaril kratek governance artefakt, ki povzame današnji namen testiranja ACLI v realni uporabi.
```

No runtime behavior, tests, routing rules, governance semantics, replay semantics, or provider logic were changed by this audit.

## 2. Observed Runtime Result

Local deterministic routing trace for the exact prompt produced:

```text
workflow_id: HUMAN_INTENT_CLARIFICATION_INTAKE
routing_status: CLARIFICATION_REQUIRED
intent_family: AMBIGUOUS_INTENT
matched_terms: unknown-human-intent
proposal_only_classification: false
ocs_escalation_reason: null
provider_invoked: false
worker_invoked: false
execution_requested: false
```

The reported real ACLI session later showed:

```text
Proposal-Only Cognition Routing: NO
providers: NONE
Selected Workflow: CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

These are compatible observations. The initial prompt does not satisfy proposal-only OCS escalation; after clarification/refinement, the system may preserve the target as domain clarification rather than OCS cognition.

## 3. Complete Decision Trace

Normalized prompt:

```text
rad bi ustvaril kratek governance artefakt, ki povzame današnji namen testiranja acli v realni uporabi
```

ASCII-normalized Slovenian prompt:

```text
rad bi ustvaril kratek governance artefakt, ki povzame danasnji namen testiranja acli v realni uporabi
```

Routing sequence:

1. Domain approval / worker / governed termination entry checks: no match.
2. Provider onboarding domain check: no match.
3. Early Human Intent Resolution with `include_unknown=False`: no match.
4. Freeform OCS clarification prompts: no match.
5. Trading / marketing domain prompts: no match.
6. Proposal-only OCS escalation helper: reached, returned no escalation.
7. Proposal runtime and improvement proposal runtime checks: no match.
8. Governance artifact creation prompt check: no match.
9. Governed repository mutation and governed development checks: no match.
10. Native development and Product 1 checks: no match.
11. Broad OCS cognition check: no match.
12. Plain domain proposal / plain OCS / native development checks: no match.
13. Human execution intent detection: no execution intent.
14. Final Human Intent Resolution with `include_unknown=True`: matched `AMBIGUOUS_INTENT`.
15. Selected workflow: `HUMAN_INTENT_CLARIFICATION_INTAKE`.

## 4. Proposal-Only Escalation Conditions

The relevant helper is `_proposal_only_ocs_escalation(normalized)` in `aigol/runtime/conversational_cli_runtime.py`.

Evaluated values for the exact prompt:

| Condition | Value |
| --- | --- |
| Helper reached | YES |
| `has_no_execution_marker` | `false` |
| `execution_marker_without_no_execution` | `false` |
| `governance_document_marker` | `false` |
| `contains_governance_artifact_term` | `true` |
| `explicit_governance_artifact_with_no_execution` | `false` |
| `implementation_proposal_marker` | `false` |
| `proposal_action_marker` | `false` |
| `governed_subject_marker` | `true` |
| Helper result | `None` |

The prompt contains governed subject evidence:

```text
governance
ACLI
```

The prompt also contains a governance artifact term:

```text
governance artefakt
```

But it does not contain any currently recognized proposal-only/no-execution marker, and the summary verb `povzame` is not currently included in the proposal-action marker list.

## 5. First Blocking Condition

The first blocking condition is inside the governance-document branch:

```text
governance_document_marker == false
explicit_governance_artifact_with_no_execution == false
```

Why:

- `governance_document_marker` only recognizes English governance document phrases and two Slovenian `governance dokument` phrases.
- The prompt uses `governance artefakt`, not `governance dokument`.
- `explicit_governance_artifact_with_no_execution` requires both `governance artefakt` and an explicit no-execution marker such as `brez izvajanja`, `brez zapisovanja datotek`, or equivalent.
- The prompt does not include a no-worker / no-file-write statement.

The second relevant blocking condition is in the explanation/analysis branch:

```text
proposal_action_marker == false
```

Why:

- The prompt uses `povzame`.
- The current proposal-action markers include `povzemi`, but not `povzame`.

## 6. Root Cause

Root cause:

```text
Slovenian proposal-only vocabulary coverage is incomplete.
```

More specifically:

- The implemented multilingual handling covers `pripraviti governance dokument` and explicit no-execution governance artifact wording.
- It does not cover `ustvaril kratek governance artefakt`.
- It does not cover the Slovenian summary verb form `povzame`.
- It requires explicit no-execution wording before treating a governance artifact phrase as proposal-only OCS cognition.

This is a language matching gap, not a provider registration issue, not a provider activation issue, not a replay issue, and not a worker/approval gate issue.

## 7. Was The New Code Path Reached?

Yes.

The `_proposal_only_ocs_escalation` helper was reached before governance artifact creation, governed development, broad OCS cognition, plain domain proposal, and final human-intent clarification fallback.

It returned no escalation because its deterministic markers did not match the exact Slovenian phrasing.

## 8. Gate Classification

| Gate | Classification |
| --- | --- |
| Routing | Reached and evaluated |
| Workflow selection | Selected clarification after proposal-only escalation returned no match |
| Clarification refinement | May explain the reported `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` after follow-up, but is not the first blocker |
| Confidence threshold | Not reached because no proposal-only classification was produced |
| Language matching | Blocking gate |
| Provider eligibility | Not reached |
| Provider invocation | Not reached |
| Worker lifecycle | Not reached |

## 9. Replay Impact

Because proposal-only escalation did not match, routing replay records no OCS escalation metadata:

```text
ocs_escalation_reason: null
ocs_escalation_confidence: null
ocs_provider_selection: null
proposal_only_classification: false
```

Replay behavior is deterministic and correct for the current implemented rules.

## 10. Recommended Minimal Fix

If this prompt should be treated as proposal-only cognition, the minimal Feature-Freeze-compatible repair is a vocabulary coverage update only:

1. Add Slovenian summary verb forms to proposal-action markers:

```text
povzame
povzeti
```

2. Add a narrowly scoped Slovenian governance artifact proposal-only phrase, preferably constrained by summary wording:

```text
kratek governance artefakt
governance artefakt ... povzame
```

3. Preserve the current safety rule that generic governance artifact creation remains governed-development unless:

- the prompt is clearly summary/explanation/proposal-only cognition, or
- the prompt explicitly states no workers / no file writes / no execution.

This repair would not change governance, approval, replay, worker lifecycle, provider model, or execution authorization. It would only broaden deterministic language coverage for proposal-only OCS escalation.

## 11. Validation

Diagnostics performed:

```bash
python - <<'PY'
from pathlib import Path
from aigol.runtime.conversational_cli_runtime import route_conversational_cli_intent

prompt = "Rad bi ustvaril kratek governance artefakt, ki povzame današnji namen testiranja ACLI v realni uporabi."
capture = route_conversational_cli_intent(
    routing_id="TRACE-ACLI-OCS-PROPOSAL-ONLY",
    prompt_id="TRACE-PROMPT",
    human_prompt=prompt,
    canonical_chain_id="TRACE-CHAIN",
    created_at="2026-06-26T00:00:00Z",
    replay_dir=Path("/tmp/acli-ocs-proposal-only-trace"),
)
print(capture["workflow_id"])
print(capture["routing_decision_artifact"])
PY
```

Observed:

```text
HUMAN_INTENT_CLARIFICATION_INTAKE
proposal_only_classification: false
```

`git diff --check` must pass after this audit artifact is added.

## 12. Final Verdict

ACLI_OCS_PROPOSAL_ONLY_TRACE_COMPLETE
