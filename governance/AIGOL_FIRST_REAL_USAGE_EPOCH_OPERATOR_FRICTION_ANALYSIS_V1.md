# AIGOL_FIRST_REAL_USAGE_EPOCH_OPERATOR_FRICTION_ANALYSIS_V1

## Status

Operator friction analysis.

## Friction 1: Workspace Preflight Failure Is Underspecified

Observed:

```text
FAILED_CLOSED: generic domain factory failed closed: required directory missing
```

Impact:

The operator cannot tell whether `governance/`, `aigol/runtime/`, `tests/`, or
another directory is missing.

Needed improvement:

Show the exact missing path and the expected workspace shape before attempting
bundle generation.

## Friction 2: Successful Domain Creation Prints Too Much Lifecycle Detail

Observed:

Domain creation prints every stage from handoff through execution preparation,
authorization, worker request, assignment, dispatch, invocation, capture,
validation, bundle creation, replay review, and termination.

Impact:

The operator has to scan a wall of lifecycle detail to answer simple questions:

- Did it work?
- What was created?
- Where is the replay?
- What did not happen?

Needed improvement:

Default to a compact operator summary with an optional verbose flag for full
lineage.

## Friction 3: Authority Language Is Confusing

Observed terms:

- `Execution Authorization`;
- `Worker Dispatch`;
- `Worker Invocation`;
- `WORKER_INVOKED`;
- `Execution Status: EXECUTION_READY`;
- `Execution has not started.`

Impact:

The output mixes reassuring no-execution statements with status names that
sound like real execution occurred. This is especially confusing after
approval.

Needed improvement:

Separate operator terms from internal lifecycle terms. Make the default summary
say:

```text
Real implementation: NOT PERFORMED
Filesystem mutation: only authorized bundle artifacts, when applicable
Worker execution: simulated/governed placeholder lifecycle
```

## Friction 4: Aggregate Replay Inspection Fails For Multi-Session Roots

Observed:

```text
failure_reason: unified replay reconstruction failed closed: multiple chain ownership
```

Impact:

An operator naturally points `show-latest-chain` at the runtime root. The
command fails once multiple sessions exist.

Needed improvement:

`show-latest-chain` should either:

- select the latest chain deterministically across sessions; or
- list candidate sessions/turns and tell the operator which exact root or chain
  command to use.

## Friction 5: `show-chain` Still Requires Exact Turn Root

Observed:

`show-chain <chain_id>` failed from aggregate root but succeeded from exact
turn root.

Impact:

The operator must know filesystem internals even after providing a chain id.

Needed improvement:

Resolve chain id to turn root from the aggregate replay root, or provide a
chain discovery command.

## Friction 6: Unknown Domain And Multi-Domain Failures Are Not Human-Readable

Observed:

```text
conversation provider clarification fallback failed closed: prompt is not clarification-eligible
```

Impact:

This does not tell the operator whether the domain is unknown, the prompt is
multi-target, or a provider fallback policy blocked clarification.

Needed improvement:

Render domain-resolution and multi-domain ambiguity directly:

```text
I found multiple requested domains: HEALTHCARE, TRADING.
Please choose one domain per operation.
```

or:

```text
FINANCE is not registered. Registered domains are MARKETING,
SERVER_MANAGEMENT, TRADING, HEALTHCARE.
```

## Friction 7: Request Modification Has No Continuation Prompt

Observed:

Request modification records `CLARIFICATION_REQUIRED`, then stops.

Impact:

The operator does not know whether to type a new prompt, reference the prior
request, or use a specific modification format.

Needed improvement:

Show a next-step line:

```text
Describe the requested modification in the next message.
```

## Friction 8: OCS Is Not Visible As OCS In CLI Conversation

Observed:

Conversation flows do not expose a clear OCS chain summary. `cognition`
commands expose primitive registry and unknown-state envelopes unless supplied
with artifact files.

Impact:

The certified OCS is hard to experience as an operator.

Needed improvement:

Expose existing OCS evidence through a compact inspection command or conversation
summary section.

