# Governance Policy Engine v1

This package provides deterministic, replay-safe policy classification before any bounded autonomy or execution authorization model exists.

Policy classifies advisory proposals, approval candidates, and governance requests. It produces policy evidence only. It does not approve, reject as a human decision, enqueue tasks, invoke Codex, trigger transport, or mutate replay, reflection, approval, or transport artifacts.

## Architecture

- `policy_engine.py`: builds and writes policy evaluations.
- `policy_rules.py`: detects forbidden capabilities conservatively.
- `admissibility.py`: assigns `ALLOWED`, `RESTRICTED`, `ESCALATE`, or `BLOCKED`.
- `escalation.py`: assigns escalation classes.
- `policy_evidence.py`: writes immutable evaluation evidence.
- `policy_reader.py`: reads policy history.
- `policy_cli.py`: classification-only CLI.

## Admissibility Model

- `ALLOWED`: advisory-only, human approval required, no execution authority requested.
- `RESTRICTED`: runtime, transport, protocol, or reflection boundary touched without direct execution request.
- `ESCALATE`: governance, approval, policy, enforcement, or authority boundary touched.
- `BLOCKED`: forbidden capability requested.

## Forbidden Capabilities

Policy blocks automatic execution, execution authority, automatic approval/rejection, Codex invocation, transport invocation, task generation, recursive execution, self-approval, self-modifying governance, policy/protocol bypass, auto-merge, and auto-push.

## Replay-Safe Evidence

Policy evaluations are written append-only under `sapianta_bridge/runtime/policy/evaluations/`. Evaluations preserve source lineage, matched rules, blocked capabilities, violations, timestamps, and classification results.

## Fail-Closed Behavior

Malformed input, missing lineage, unknown input types, unknown states, or unresolved uncertainty never become optimistic `ALLOWED` decisions. Policy either blocks or escalates.

## No Execution Authority

Every policy evaluation sets:

```json
{
  "allowed_to_execute_automatically": false,
  "execution_authority_granted": false
}
```

Policy precedes bounded autonomy because governance admissibility must exist before execution authorization can be considered.
