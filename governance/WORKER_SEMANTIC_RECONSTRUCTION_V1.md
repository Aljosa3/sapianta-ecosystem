# Worker Semantic Reconstruction V1

Status: reconstructed Worker semantics.

## What Is A Worker?

A Worker is an execution-only participant that performs a bounded authorized capability and returns replay-visible evidence.

Worker is not:

- an LLM
- a proposer
- a governance authority
- an authorization authority
- a replay authority
- an orchestration system
- an autonomous agent
- a memory system

## Worker Identity

Worker identity is already modeled as deterministic, replay-visible, invocation-scoped identity.

Defined identity fields include:

- worker id
- worker type
- worker instance identity
- worker version
- capability binding id
- invocation id
- authorized request id
- created timestamp

Worker identity does not grant authority.

## Worker Authority

Worker has bounded execution participation only after AiGOL authorization.

Worker is explicitly prohibited from:

- self-authorizing
- authorizing execution
- governing
- mutating replay
- mutating governance
- expanding capability scope
- invoking unsupported capabilities
- creating hidden continuation
- persisting hidden state

## Worker And AiGOL

AiGOL governs Worker execution by:

- validating proposal and execution requests
- authorizing or rejecting execution
- preserving replay lineage
- enforcing capability boundaries
- producing governed return evidence

Worker executes only after this governance path completes.

## Worker And LLM

LLM proposes.

Worker executes.

AiGOL separates them.

Worker never receives raw LLM authority. Worker receives only a governed execution request that is already validated, authorized, bounded, and replay-linked.

## Worker And Replay

Worker activity must become replay-visible and append-only.

Worker logs cannot replace replay evidence.

Replay corruption, missing worker evidence, or ambiguous ordering must fail closed.

## Worker And Capabilities

Worker binds to a specific authorized capability.

Current first-worker constraint is read-only:

- `READ_ONLY_RUNTIME_INSPECTION`
- `FILESYSTEM_READ_ONLY_INSPECTION`

Capability binding narrows authority. It does not expand authority.
