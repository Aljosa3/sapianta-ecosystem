# ChatGPT Ingress Bridge v1

This package defines the canonical ChatGPT ingress bridge for AiGOL semantic governance.

ChatGPT is an interaction surface only. It is not governance, execution authority, provider routing, or runtime.

## Flow

```text
ChatGPT Interaction
-> NL Request
-> Intent Classification
-> Admissibility Evaluation
-> Authority Mapping
-> Workspace Mapping
-> ExecutionEnvelope Proposal
-> Replay-safe Ingress Evidence
```

## Invariants

```text
CHATGPT != GOVERNANCE
NATURAL_LANGUAGE != EXECUTION
INGRESS != EXECUTION AUTHORITY
PROPOSAL != EXECUTION
REPLAY MUST REMAIN DETERMINISTIC
```

## Session And Request

Ingress sessions include deterministic session identity, request identity, timestamp, replay binding, and immutable semantic lineage. No mutable memory is introduced.

Ingress requests preserve original natural language, normalized text for deterministic matching, semantic metadata, and governance classification references. Hidden prompt rewriting is forbidden.

## Validation

Ingress validation checks session integrity, request integrity, binding integrity, admissibility, authority scope, workspace scope, proposal identity, and replay safety.

## Non-Goals

This package does not execute, route, retry, schedule, call providers, invoke adapters, mutate memory, run background agents, use network calls, use shell execution, or approve anything autonomously.
