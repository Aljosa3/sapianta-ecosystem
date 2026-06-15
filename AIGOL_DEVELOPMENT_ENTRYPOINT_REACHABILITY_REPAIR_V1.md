# AIGOL_DEVELOPMENT_ENTRYPOINT_REACHABILITY_REPAIR_V1

## Objective

Repair ACLI development routing so certified development entrypoints are reachable from conversational ACLI prompts.

This repair changes routing reachability only. It does not redesign governance, replay, PPP, authorization, worker lifecycle, or provider behavior.

## Repair Summary

ACLI now registers and selects the nine certified development entrypoints that were unreachable in `AIGOL_DEVELOPMENT_ENTRYPOINT_DISCOVERY_AUDIT_V1`.

The repaired entrypoints are selection-visible and replay-visible. They do not invoke providers, workers, authorization, execution, governance mutation, or replay mutation at route-selection time.

## Repaired Entrypoint Matrix

| Certified entrypoint | Conversational example | ACLI route after repair |
|---|---|---|
| `AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION` | `Define the AI Decision Validator domain foundation for Product 1.` | `AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION` |
| `AI_DECISION_VALIDATOR_CAPABILITY_MODEL` | `Define the decision model for Product 1 AI Decision Validator.` | `AI_DECISION_VALIDATOR_CAPABILITY_MODEL` |
| `AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE` | `Define the capability lifecycle for Product 1 AI Decision Validator.` | `AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE` |
| `DOMAIN_LIFECYCLE_GOVERNANCE_RUNTIME` | `Create a domain activation candidate for Product 1 AI Decision Validator.` | `DOMAIN_LIFECYCLE_GOVERNANCE_RUNTIME` |
| `CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME` | `Create a capability activation candidate for Product 1 AI Decision Validator.` | `CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME` |
| `PROPOSAL_RUNTIME` | `Create a governed proposal artifact for Product 1 decision validation.` | `PROPOSAL_RUNTIME` |
| `IMPROVEMENT_PROPOSAL_RUNTIME` | `Create an improvement proposal for Product 1 replay evidence requirements.` | `IMPROVEMENT_PROPOSAL_RUNTIME` |
| `FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH` | `Run the first real implementation generation epoch for Product 1 evidence requirements.` | `FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH` |
| `IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME` | `Convert the implementation plan to an execution request for Product 1 decision model work.` | `IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME` |

## Live CLI Evidence

Command:

```bash
python -m aigol.cli.aigol_cli conversational route --prompt "Define the decision model for Product 1 AI Decision Validator." --runtime-root /tmp/aigol-entrypoint-route-check
```

Observed:

```text
routing_status: WORKFLOW_SELECTED
workflow_id: AI_DECISION_VALIDATOR_CAPABILITY_MODEL
existing_runtime: AI_DECISION_VALIDATOR_CAPABILITY_MODEL_V1.md
coverage: 35/35
provider_invoked: False
worker_invoked: False
execution_requested: False
fail_closed: False
```

## Boundary Preservation

The repair preserves:

- provider invocation boundary;
- worker invocation boundary;
- authorization boundary;
- PPP behavior;
- governance mutation boundary;
- replay mutation boundary;
- fail-closed behavior for generic governed execution intents without certified mapping.

Historical fallback routing remains available for unknown non-certified prompts. The repair prevents the identified certified development prompts from falling into that fallback.

## Validation

```bash
python -m pytest tests/test_conversational_cli_runtime_v1.py
```

Result:

```text
93 passed
```

## Final Fields

```text
UNREACHABLE_ENTRYPOINTS_BEFORE = 9
UNREACHABLE_ENTRYPOINTS_AFTER = 0
PRODUCT_1_ENTRYPOINT_REACHABLE = YES
PLACEHOLDER_ENTRYPOINTS_RETIRED = NO
ROUTING_COVERAGE_PERCENT = 100
ACLI_DEVELOPMENT_ROUTING_OPERATIONAL = YES
```
