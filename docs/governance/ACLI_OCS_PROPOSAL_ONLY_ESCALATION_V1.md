# ACLI_OCS_PROPOSAL_ONLY_ESCALATION_V1

## 1. Purpose

This artifact records the first minimal implementation of `ACLI_TO_OCS_ESCALATION_POLICY_V1`.

The implemented subset allows ACLI to escalate deterministic proposal-only requests into OCS cognition while preserving all execution and governance boundaries.

Implemented flow:

Human
-> ACLI
-> HIRR / deterministic routing
-> OCS proposal-only cognition
-> Replay

PPP, workers, approval authorization, and repository mutation remain unavailable unless a separate certified execution path explicitly requires them.

## 2. Implemented Policy Subset

The implemented subset recognizes proposal-only cognition prompts for:

- governance document preparation;
- explanation requests;
- summary requests;
- comparison requests;
- brainstorming requests;
- implementation proposal requests;
- explicit no-worker / no-file-write governance artifact requests;
- equivalent supported Slovenian proposal-only wording.

Examples now deterministically route to `OCS_LLM_COGNITION`:

- `Create governance document explaining ACLI approval behavior for an operator.`
- `Explain ACLI approval, replay, validation, and execution behavior for a non-technical operator.`
- `Compare provider options for proposal-only cognition.`
- `Želim samo pripraviti governance dokument. Ne želim izvajanja workerjev ali zapisovanja datotek.`

Standard operator governance artifact creation prompts remain routed to the complete governed development lifecycle unless they explicitly ask for proposal-only/no-execution handling.

## 3. Safety Boundaries

The implementation preserves:

- deterministic routing;
- fail-closed behavior;
- provider isolation;
- replay determinism;
- approval boundaries;
- worker lifecycle boundaries;
- repository mutation protections;
- multilingual handling for the implemented Slovenian proposal-only forms.

The implementation does not change:

- execution authorization;
- worker lifecycle;
- approval model;
- governance evidence semantics;
- PPP semantics;
- Human Intent Resolution semantics.

## 4. Replay Evidence

Conversational routing replay now records proposal-only OCS escalation metadata:

- `ocs_escalation_reason`;
- `ocs_escalation_confidence`;
- `ocs_provider_selection`;
- `proposal_only_classification`.

The actual provider invocation remains recorded by the OCS cognition replay path. Routing replay remains non-executing and records `provider_invoked: false`, `worker_invoked: false`, and `execution_requested: false`.

## 5. Validation

Focused regression coverage was added for:

- proposal-only prompt routing;
- replay-visible escalation metadata;
- multilingual proposal-only governance document handling;
- OCS provider invocation through the live conversational path using a hermetic fake provider;
- confirmation that PPP, workers, execution authorization, and worker adapters are not reached.

Validation commands:

```bash
python -m pytest tests/test_conversational_cli_runtime_v1.py::test_proposal_only_prompts_route_to_ocs_with_replay_visible_escalation_metadata tests/test_acli_certified_continuation_orchestration_v1.py::test_proposal_only_governance_document_prompt_invokes_ocs_without_execution -q
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_acli_certified_continuation_orchestration_v1.py -q
git diff --check
python -m pytest -q
```

Observed result:

```text
5 passed
155 passed
git diff --check passed
5388 passed, 4 skipped
```

## 6. Remaining Escalation Stages

Not implemented in this subset:

- multi-clarification escalation thresholds;
- provider tier escalation;
- adaptive confidence estimation;
- cognition escalation after clarification continuity;
- execution-producing escalation.

These remain governed by `ACLI_TO_OCS_ESCALATION_POLICY_V1` and require separate implementation work.

## 7. Final Verdict

ACLI_OCS_PROPOSAL_ONLY_ESCALATION_READY
