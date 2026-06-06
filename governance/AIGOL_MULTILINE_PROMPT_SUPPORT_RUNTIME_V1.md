# AIGOL_MULTILINE_PROMPT_SUPPORT_RUNTIME_V1

## Status

Certified runtime milestone.

Classification:

```text
CERTIFIED_MULTILINE_PROMPT_SUPPORT_RUNTIME
```

## Objective

Implement first-class multi-line prompt support for:

```text
aigol conversation
```

This milestone directly remediates:

```text
F-1 - Multi-line prompts are fragmented into separate turns
```

from `AIGOL_CONVERSATIONAL_CLI_OPERATIONAL_VALIDATION_V1`.

## Findings

The previous interactive loop read exactly one line per turn through:

```text
input_reader("AiGOL > ")
```

As a result, pasted multi-line operator requests were fragmented into
independent prompts, independent turn ids, independent source-router decisions,
and independent completion artifacts.

The new runtime introduces deterministic prompt assembly before turn routing.
The sentinel:

```text
.
```

on its own line terminates multi-line input. The terminator is not included in
the assembled prompt.

Replay now records:

- `MULTILINE_PROMPT_CAPTURED`;
- `TURN_STARTED`;
- line count;
- character count;
- assembled prompt hash;
- single-turn guarantee;
- no fragment turns;
- no partial routing.

## Assumptions

The runtime preserves current single-line behavior. A normal prompt such as:

```text
AiGOL > hello
```

still produces exactly one turn.

Multi-line assembly is activated only when continuation input is already
available from the input source. This preserves the existing single-line REPL
contract while allowing pasted blocks and test adapters to provide buffered
continuation lines.

The milestone does not change OCS cognition, provider execution, conversation
routing, or the existing replay schemas. It adds a bounded prompt-capture
artifact under each turn.

## Alternatives

1. Always require `.` after every prompt.

   Rejected because it would break the existing single-line UX and make normal
   interactive usage slower.

2. Add a new explicit command such as `:multiline`.

   Rejected for this milestone because the operator should be able to paste a
   complete prompt without learning a separate command prefix.

3. Add `--prompt-file`.

   Useful as a future batch mode, but it does not solve pasted interactive
   prompt fragmentation.

4. Accept multi-line input until EOF.

   Rejected because EOF is a session boundary in the REPL and does not provide
   a deterministic per-turn prompt boundary.

## Risks

Buffered-input detection depends on the input source. The test runtime exposes
buffered continuation explicitly, and the real CLI uses nonblocking stdin
readiness. If a terminal does not expose pasted continuation lines as readable
after the first line, the operator can still enter the sentinel flow line by
line once continuation is available.

The milestone does not repair unrelated routing fragility, provider
availability, provider projection, elapsed-time measurement, or fallback
coverage findings. Those remain separate milestones.

## Recommendation

Certify this milestone as a narrow runtime remediation for F-1.

The implementation should remain scoped to prompt assembly and replay-visible
input evidence. Unified intent routing, real-time progress measurement, provider
projection, and fallback hardening should remain separate governed work so this
change does not blur constitutional or runtime boundaries.

## Runtime Behavior

Single-line:

```text
AiGOL > hello
```

Result:

```text
turn_count: 1
line_count: 1
input_mode: SINGLE_LINE
```

Multi-line:

```text
AiGOL > I want to create the first real commercial Sapianta product.
... Use the current AiGOL architecture and repository state.
... Produce:
... 1. Findings
... 2. Assumptions
... 3. Alternatives
... 4. Risks
... 5. Recommendation
... Explain your reasoning.
... .
```

Result:

```text
turn_count: 1
line_count: many
input_mode: MULTILINE_SENTINEL
fragment_turns_created: false
partial_routing_allowed: false
```

## Replay Evidence

Each turn records prompt assembly evidence under:

```text
<runtime_root>/<session_id>/<turn_id>/multiline_prompt_capture/
```

Replay file:

```text
000_multiline_prompt_captured.json
```

The replay proves:

```text
many lines -> one assembled prompt -> one turn -> one routing decision
```

## Banner

The real interactive CLI startup banner includes:

```text
Multi-line mode enabled.
Finish prompt with a single '.' on its own line.
```

## Boundary Preservation

This milestone does not:

- invoke providers;
- change provider behavior;
- change OCS cognition;
- change conversation routing;
- dispatch workers;
- request execution;
- create approval authority;
- mutate governance;
- mutate existing replay.

It creates only prompt-capture evidence and uses the assembled prompt as the
single `human_prompt` passed into the existing routing cascade.
