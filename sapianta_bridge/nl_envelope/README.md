# Natural Language To Envelope v1

This package defines the first canonical semantic governance ingress layer for AiGOL.

Natural language is governance input. It is not execution authority.

## Flow

```text
Natural Language
-> Intent Extraction
-> Governance Classification
-> Admissibility Evaluation
-> Authority Scope Mapping
-> Workspace Scope Mapping
-> ExecutionEnvelope Proposal
```

## Prompt vs Authority

Prompts cannot directly execute, invoke providers, define authority, define workspace access, bypass governance, bypass envelopes, bypass transport, or bypass runtime validation.

The invariant is:

```text
Natural Language != Execution Authority
```

## Intent Classification

Supported deterministic intent types:

- `GOVERNED_REFINEMENT`
- `CREATIVE_GENERATION`
- `GOVERNED_EXECUTION_PROPOSAL`
- `GOVERNANCE_INSPECTION`
- `UNKNOWN`

Unknown or ambiguous intent fails closed.

## Admissibility

Admissibility outputs are:

- `ADMISSIBLE`
- `REVIEW_REQUIRED`
- `REJECTED`

Requests with implicit execution authority, governance bypass, or ambiguous scope are rejected.

## Authority And Workspace Mapping

Authority and workspace are mapped by deterministic least-privilege rules. Undefined authority and implicit workspace expansion are forbidden.

## Envelope Proposal

Generated envelopes are proposals only. They remain non-authoritative and must pass downstream envelope, transport, runtime, and governance validation before any bounded execution.

## Non-Goals

This package does not add autonomous reasoning, planning, execution, orchestration, routing, retries, fallback, provider APIs, transport execution, hidden reasoning chains, or self-modifying governance.
