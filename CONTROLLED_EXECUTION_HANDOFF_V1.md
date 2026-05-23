# CONTROLLED_EXECUTION_HANDOFF_V1

Status: implemented as the first real governed execution continuity loop.

## Purpose

`CONTROLLED_EXECUTION_HANDOFF_V1` connects the governed continuity chain to one real bounded execution path.

The only allowed path is:

```text
sidepanel
-> service_worker
-> Native Messaging
-> Python runtime bridge
-> bounded Codex CLI provider
```

## Non-Goals

This milestone does not add orchestration, retries, autonomous continuation, multi-provider routing, background execution, automatic recursion, hidden execution paths, adaptive runtime behavior, provider abstraction redesign, or dynamic governance mutation.

## Bounded Execution Model

Execution is allowed only after `CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1` reaches `READY_FOR_CONTROLLED_EXECUTION_HANDOFF`.

Execution remains:

- single execution only;
- single provider only;
- single path only;
- fail-closed;
- replay-visible;
- governance-mediated.

## Fail-Closed Guarantees

Execution blocks if the continuity preview is missing, replay identity is invalid, provenance is missing, source hashes are invalid, execution is already performed, Native Messaging is already called, provider execution is already invoked, or autonomous continuation is requested.

## Replay-Visible Execution Evidence

The artifact records:

- replay identity;
- dispatch authorization hash;
- continuity preview hash;
- execution path used;
- Native Messaging call status;
- service worker call status;
- provider invocation status;
- bounded Codex provider used;
- execution result summary;
- execution result hash;
- execution governance hash.

## Execution Governance Hash

`execution_governance_hash` is deterministic. It includes:

- replay identity;
- dispatch authorization hash;
- continuity preview hash;
- execution path used;
- execution status;
- execution result hash;
- authority boundary flags.

## Single Path

No alternate execution path is introduced. The handoff uses the existing Native Messaging host and Python bridge path only.

## Single Provider

No provider routing is introduced. The only provider is the existing bounded Codex CLI provider.

## Autonomous Continuation Blocked

The artifact always records:

```text
autonomous_continuation_performed: false
```

No retry, chain execution, recursive execution, or background continuation behavior is added.
