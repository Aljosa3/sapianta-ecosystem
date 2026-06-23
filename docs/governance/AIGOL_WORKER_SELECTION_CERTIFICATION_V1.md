# AIGOL_WORKER_SELECTION_CERTIFICATION_V1

Status: prepared and executable.

Purpose: certify governed worker selection across deterministic and LLM worker candidates.

This certification uses:

```text
LLM_WORKER_EXECUTION_CERTIFIED
WORKER_SELECTION_GOVERNANCE_DEFINED
ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED
MULTI_PROVIDER_OPERATIONALLY_READY
PRODUCT1_END_TO_END_CERTIFIED
```

It does not invoke production workers.

It does not invoke live providers.

It does not authorize execution from selection alone.

It does not grant authority to workers or LLMs.

## Goal

Certify that AiGOL can prove the selected worker was the most appropriate governed choice while preserving governance authority and deterministic-first selection.

## Runtime

Run:

```bash
python -m aigol.runtime.worker_selection_certification_v1
```

Artifacts are written under:

```text
runtime/worker_selection_certification_v1/CERT-XXXXXX/
```

Required outputs:

```text
coverage_report/000_worker_selection_coverage_report.json
evidence_package/000_worker_selection_evidence_package.json
replay_package/000_worker_selection_replay_package.json
certification_report/000_worker_selection_certification_report.json
scenarios/WSG-*/
```

## Scenario Coverage

The certification covers:

```text
WSG-001 deterministic worker available
WSG-002 deterministic worker unavailable
WSG-003 deterministic worker preferred over LLM worker
WSG-004 multiple LLM workers available
WSG-005 worker failover
WSG-006 worker validation failure
WSG-007 capability mismatch
```

Each scenario records:

```text
worker capability declarations
candidate set
suitability scores
selection decision
selection rationale
failover decision
selection validation
authority boundary
```

## Certification Assertions

Required assertions:

```text
deterministic_worker_available_certified
deterministic_worker_unavailable_certified
deterministic_worker_preferred_over_llm_certified
multiple_llm_workers_available_certified
worker_failover_certified
worker_validation_failure_certified
capability_mismatch_certified
all_scenarios_certified
selection_rationale_recorded
suitability_score_recorded
replay_records_selection_process
governance_authority_preserved
deterministic_first_policy_enforced
reviewer_can_audit_selection
secret_free_evidence
```

## Auditability Requirements

The certification must prove a reviewer can determine:

```text
which capability was required
which workers were candidates
which worker was selected
why the selected worker was selected
why alternatives were rejected
whether deterministic-first policy was applied
whether LLM worker use was justified
whether failover was bounded
whether validation failure failed closed
whether governance authority was preserved
```

## Pass Criteria

The certification verdict is:

```text
WORKER_SELECTION_CERTIFIED
```

only if:

```text
all seven scenarios certify
worker selection rationale is replay-visible
suitability scores are replay-visible
selection process replay reconstructs
governance authority is preserved
deterministic-first policy is enforced
reviewer can audit selection and alternative rejection
evidence remains secret-free
```

Otherwise the verdict is:

```text
WORKER_SELECTION_GAPS_FOUND
```

## Final Verdict

Runtime-determined:

```text
WORKER_SELECTION_CERTIFIED
```

or:

```text
WORKER_SELECTION_GAPS_FOUND
```
