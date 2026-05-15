# ADR_GOVERNED_TERMINAL_RUNTIME_ATTACHMENT_V1

## Decision

Introduce a deterministic governed terminal runtime attachment layer above `LIVE_GOVERNED_RUNTIME_SERVING_LAYER_V1`.

## Rationale

The governed runtime stack already preserves interaction, transport, execution, live runtime, and serving continuity. The terminal surface remained detached. This milestone adds an explicit replay-visible attachment identity plus bounded `stdin` and `stdout` continuity identifiers so terminal-facing interaction can be governed without fabricating state.

## Boundary

The attachment is not orchestration, not a websocket service, not autonomous continuation, and not unrestricted shell access. It does not execute arbitrary commands, trust provider hidden memory, or mutate prior runtime history.

## Consequence

Terminal continuity can now be validated as part of the governed no-copy/paste chain while preserving deterministic replay, fail-closed validation, and explicit runtime lineage.
