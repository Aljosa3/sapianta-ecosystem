# COGNITION_RUNTIME_COVERAGE_FINDINGS_V1

## Status

Review-only coverage findings.

## Finding 1: Representative Prompt Classes Were Covered

The coverage sweep exercised all requested prompt classes.

Coverage by class:

```text
case_count = 16
representative_prompt_class_coverage = 100%
```

## Finding 2: Response Success Is Strong But Not Complete

Successful governed conversation responses:

```text
12 / 16 = 75%
```

Fail-closed outcomes:

```text
4 / 16 = 25%
```

The fail-closed outcomes are healthy boundary behavior, but the coverage status remains `READY_WITH_GAPS` because not every expected class produces a useful operator answer.

## Finding 3: Provider Assistance Is Common

Provider assistance was used in 10 of 16 cases.

This is safe but shows that deterministic self-resolution and context assembly remain incomplete for several common operator prompts.

## Finding 4: Deterministic Self-Resolution Works For Core AiGOL Explanation

`What is AiGOL?` resolved without provider assistance.

This confirms that self-resolution exists and can produce governed conversation output when the prompt matches known internal knowledge.

## Finding 5: Source Routing Is Useful But Not Final

Source routing selected meaningful evidence-bound sources for replay, governance, constitutional memory, and self-resolution prompts.

However, several prompts route to `PROVIDER` where a future integrated context assembly or domain selector should probably route to:

- dashboard;
- replay reconstruction;
- governance memory;
- domain registry;
- explicit fail-closed unsafe handling.

## Finding 6: Constitutional Memory Path Exists But Is Not Integrated Into Conversation

The constitutional memory consultation prompt was correctly selected by source routing, but prompt-to-conversation failed closed because the prompt was not a conversation intent.

This is safe, but it shows that source routing and conversation response paths are not yet unified into one operator-friendly cognition answer path.

## Finding 7: Unsafe Execution Requests Fail Closed

The unsafe execution request failed closed and did not create execution requests or invoke workers.

This preserves the constitutional boundary.

## Finding 8: Replay Evidence Exists But Top-Level Visibility Is Inconsistent

Temporary replay artifacts were created for the coverage cases.

The top-level prompt-to-conversation result does not consistently expose a simple `replay_visible` flag for successful responses, even though replay references and artifacts exist.

## Finding 9: Domain Prompts Need Domain Selection

Domain-related and trading-domain prompts were handled with provider assistance, but the system lacks a canonical domain registry to identify `TRADING` as a domain target.

## Finding 10: Coverage Is Ready With Gaps

The cognition runtime is operationally broad and boundary-safe.

It is not yet coverage-certified because current-state, domain-selection, context-assembly, and provider-necessity gaps remain.

## Final Finding

```text
COGNITION_RUNTIME_COVERAGE_STATUS = READY_WITH_GAPS
```
