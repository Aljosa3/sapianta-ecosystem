# AIGOL_DOMAIN_EXECUTION_BINDING_V1

## Status

Runtime implementation certification.

```text
AIGOL_DOMAIN_EXECUTION_BINDING_STATUS = CERTIFIED
```

## Purpose

Allow governed domains to dispatch certified execution requests through existing AiGOL provider, authorization, and worker runtimes.

This milestone binds an `ACTIVE` governed domain to a real bounded execution path:

```text
Domain
-> Execution Request
-> Provider
-> Worker
-> Result
-> Replay
-> Domain Evidence
```

## Runtime Scope

Runtime file:

```text
aigol/runtime/domain_execution_binding_runtime.py
```

Certified supporting runtimes:

- `aigol/provider/provider_runtime.py`;
- `aigol/authorization/authorization_runtime.py`;
- `aigol/workers/filesystem_worker.py`;
- `aigol/runtime/domain_runtime.py`.

Test file:

```text
tests/test_domain_execution_binding_runtime_v1.py
```

## Domain Execution Contract

The runtime creates:

- `DOMAIN_EXECUTION_CONTRACT_ARTIFACT_V1`;
- `DOMAIN_PROVIDER_BINDING_ARTIFACT_V1`;
- `DOMAIN_WORKER_BINDING_ARTIFACT_V1`;
- `DOMAIN_EXECUTION_EVIDENCE_ARTIFACT_V1`.

The contract binds:

- active domain artifact hash;
- domain replay identity;
- provider identity;
- worker identity;
- authorized worker scope;
- requested file output;
- replay visibility.

## Provider Binding

The provider binding uses the existing provider attachment runtime.

Provider output remains proposal-only. The provider does not authorize execution, dispatch workers, mutate governance, or carry authority.

## Worker Binding

The worker binding uses the existing governed filesystem worker runtime.

The certified worker operation creates one bounded evidence file inside the supplied workspace after governed authorization.

## Execution Authorization

Execution authorization is created through the existing governed worker authorization runtime.

The provider proposal cannot authorize execution. The worker cannot self-authorize. Authorization evidence is replay-visible before worker request creation.

## Replay Events

Certified domain replay events:

- `DOMAIN_EXECUTION_REQUESTED`;
- `DOMAIN_EXECUTION_AUTHORIZED`;
- `DOMAIN_EXECUTION_DISPATCHED`;
- `DOMAIN_EXECUTION_COMPLETED`;
- `DOMAIN_EXECUTION_REJECTED`.

Success replay records:

```text
DOMAIN_EXECUTION_REQUESTED
-> DOMAIN_EXECUTION_AUTHORIZED
-> DOMAIN_EXECUTION_DISPATCHED
-> DOMAIN_EXECUTION_COMPLETED
```

Fail-closed replay records:

```text
DOMAIN_EXECUTION_REJECTED
```

or:

```text
DOMAIN_EXECUTION_REQUESTED
-> DOMAIN_EXECUTION_REJECTED
```

depending on whether the failure occurred before or after contract creation.

## Fail-Closed Behavior

The runtime rejects:

- missing or inactive domains;
- unavailable or unknown providers;
- provider proposal failures;
- invalid worker targets;
- invalid worker file paths;
- authorization failures;
- worker execution failures;
- replay hash corruption;
- replay lineage breaks.

## Certified Execution

The certified execution path creates one bounded workspace file:

```text
domain_execution_evidence.txt
```

with deterministic content:

```text
AIGOL_DOMAIN_EXECUTION_BINDING_V1 certified domain execution evidence
```

This is a real governed worker execution through the existing AiGOL stack. It is not external API execution, broker execution, autonomous continuation, or governance mutation.

## Authority Boundaries

The binding preserves:

- provider authority absent;
- worker self-authorization absent;
- human/governance authorization required before worker request creation;
- replay visibility;
- append-only replay persistence;
- fail-closed behavior.

## Certification Evidence

Certified tests cover:

- successful domain execution binding;
- required replay event persistence;
- inactive-domain rejection;
- unknown-provider rejection before worker execution;
- invalid worker file path rejection;
- replay tamper detection;
- integration with existing provider, authorization, and worker runtimes.

Validation result:

```text
python -m pytest tests/test_domain_execution_binding_runtime_v1.py tests/test_domain_runtime_v1.py tests/test_first_end_to_end_governed_operation_v1.py
26 passed
```

## Success Criteria

A governed domain can perform a real certified execution through the existing AiGOL stack.

Final status:

```text
AIGOL_DOMAIN_EXECUTION_BINDING_STATUS = CERTIFIED
```
